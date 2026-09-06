from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.chat_route_support import operate_overview_from_context
from eidolon.core.evidence import EvidenceStore
from eidolon.operate.service import OperateService
from eidolon.web_routes import read_root_html
from eidolon.work_context_contracts import operate_context

ROOT = Path(__file__).resolve().parents[1]
CHAT_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
OPERATE_ACTIONS_JS = ROOT / 'python' / 'eidolon' / 'web' / 'operate-actions-ui.js'
CHAT_THREAD_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'chat' / 'chat-thread.css'


def _html():
    return read_root_html(ROOT)


def _temp_service(tmp_path):
    return OperateService(
        project_root=tmp_path,
        db_path=tmp_path / 'operate.db',
        evidence_store=EvidenceStore(tmp_path / 'evidence.db'),
    )


def test_chat_freigabe_buttons_share_arbeit_write_path():
    chat = CHAT_UI_JS.read_text(encoding='utf-8')
    actions = OPERATE_ACTIONS_JS.read_text(encoding='utf-8')
    html = _html()
    assert 'id="chat-operate-actions"' in html
    assert "operateActionButton('Freigeben', 'resolveOperateApproval'" in chat
    assert "operateActionButton('Ablehnen', 'resolveOperateApproval'" in chat
    assert "operateActionButton('Fortsetzen', 'advanceOperateRun'" in chat
    assert "operateActionButton(nextAction.action_label || 'Fortsetzen', 'resolveOperateBlocker'" in chat
    assert "async function resolveOperateApproval(runId, approvalId, decision)" in actions
    assert "await api('POST', '/api/v1/runs/' + runId + '/approval/' + approvalId" in actions
    assert "await api('POST', '/api/v1/runs/' + runId + '/blockers/' + blockerId + '/resolve'" in actions
    assert "await api('POST', '/api/v1/runs/' + runId + '/advance'" in actions
    assert 'function operateDoorHasWork' in chat
    assert 'renderChatOperateActionsFromContext(runtimeContext)' in chat
    assert 'if (!idle) renderChatOperateActionsFromContext(null)' not in chat
    assert "api('GET', '/api/v1/operate/overview')" not in chat
    assert "url = sessionId" in chat
    assert "'/chat/context?session_id=' + encodeURIComponent(sessionId)" in chat
    assert "'/chat/context'" in chat
    assert 'operate_overview' in chat


def test_idle_chat_has_no_placebo_freigabe_wall():
    html = _html()
    css = CHAT_THREAD_CSS.read_text(encoding='utf-8')
    chat = CHAT_UI_JS.read_text(encoding='utf-8')
    assert 'id="chat-operate-actions" class="chat-operate-actions" hidden' in html
    assert 'Freigeben' not in html.split('id="chat-operate-actions"')[1].split('id="chat-messages"')[0]
    assert 'Braucht deine Entscheidung' not in html
    assert '.chat-is-idle #chat-formation' in css
    assert '.chat-is-idle #chat-operate-actions' not in css
    assert '.chat-operate-actions[hidden]' in css
    assert 'if (!operateDoorHasWork(operate))' in chat
    assert "el.hidden = true" in chat
    assert 'function operateDoorHasWork' in chat


def test_chat_door_shows_kernel_next_action_reasons():
    chat = CHAT_UI_JS.read_text(encoding='utf-8')
    assert 'nextAction.action_reason_disabled' in chat
    assert 'run_state_reason' in chat
    assert 'pending_interrupt_count' in chat
    assert 'interrupt_classification' in chat
    assert 'Unterbrochen' in chat
    assert 'Schreibt nur die Phase weiter — keine Ausführung.' in chat
    assert "nextAction.kind === 'blocking_condition'" in chat
    assert "nextAction.kind === 'next_step' && !approvals.length && !blockers.length" in chat


def test_operate_context_passes_kernel_interrupt_and_reason_fields():
    context = operate_context(
        {'id': 'sess1', 'title': 'Arbeit', 'current_view': 'chat'},
        {'id': 'obj1', 'title': 'Kern'},
        {
            'id': 'run1',
            'state': 'planning',
            'state_reason': 'Interrupt received: refine',
            'canonical_phase': 'plan',
            'pending_interrupt_count': 2,
            'interrupt_classification': 'refine',
            'interruptible': True,
        },
        {
            'kind': 'next_step',
            'title': 'Phase fortschreiben: plan',
            'summary': 'Interrupt received: refine. Keine Ausführung — nur Zustandsmaschine.',
            'action_label': 'Phase fortschreiben',
            'action_enabled': True,
            'action_reason_disabled': None,
        },
        [],
        [],
        [],
    )
    assert context['run_state_reason'] == 'Interrupt received: refine'
    assert context['current_phase'] == 'plan'
    assert context['pending_interrupt_count'] == 2
    assert context['interrupt_classification'] == 'refine'
    assert context['next_action']['action_reason_disabled'] is None
    overview = operate_overview_from_context({'operate_context': context})
    assert overview['source'] == 'chat_context'
    assert overview['run']['id'] == 'run1'
    assert overview['run']['state_reason'] == 'Interrupt received: refine'
    assert overview['run']['pending_interrupt_count'] == 2
    assert overview['next_action']['kind'] == 'next_step'


def test_chat_context_is_shared_operate_snapshot_and_approval_write_path(tmp_path, monkeypatch):
    service = _temp_service(tmp_path)
    started = service.start_objective(
        user_request='deploy release',
        title='Deploy release',
        normalized_goal='Deploy release',
        scope_summary='release',
    )
    run = started['run']
    gate = service.request_approval(
        run_id=run.id,
        title='Produktion freigeben',
        summary='Würde den externen Stand ändern',
        action_type='deploy',
    )
    from eidolon.operate.bridge_snapshot import build_operate_snapshot

    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    monkeypatch.setattr(agent_server, 'sync_operate_with_workspace_payload', lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(
        agent_server,
        'build_operate_snapshot',
        lambda svc, run_id=None: build_operate_snapshot(service, run.id),
        raising=False,
    )
    client = TestClient(agent_server.app)
    created = client.post('/chat/sessions', json={'source': 'test-chat-operate-door'})
    assert created.status_code == 200
    session_id = created.json()['session']['session_id']
    try:
        context = client.get('/chat/context', params={'session_id': session_id}).json()
        assert context['ok'] is True
        operate = context['runtime_context']['operate_context']
        overview = context['operate_overview']
        assert overview['source'] == 'chat_context'
        assert operate['run_id'] == run.id
        assert operate['pending_approval_count'] == 1
        assert operate['pending_approvals'][0]['id'] == gate.id
        assert operate['pending_approvals'][0]['title'] == 'Produktion freigeben'
        assert (operate.get('next_action') or {}).get('kind') == 'approval_request'
        assert overview['approvals'][0]['id'] == gate.id
        assert overview['run']['id'] == run.id
        assert 'run_state_reason' in operate

        resolved = client.post(
            f'/api/v1/runs/{run.id}/approval/{gate.id}',
            json={'decision': 'approved', 'resolved_by': 'user'},
        )
        assert resolved.status_code == 200
        body = resolved.json()
        assert body['ok'] is True
        assert body['data']['approval']['status'] == 'approved'
        assert body['data']['execution']['wired'] is False

        after = client.get('/chat/context', params={'session_id': session_id}).json()
        after_operate = after['runtime_context']['operate_context']
        assert after_operate['pending_approval_count'] == 0
        assert after_operate['pending_approvals'] == []
        assert (after['operate_overview'].get('approvals') or []) == []
    finally:
        client.delete(f'/chat/sessions/{session_id}')
