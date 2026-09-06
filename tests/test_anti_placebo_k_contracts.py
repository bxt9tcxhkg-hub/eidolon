from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.core.capability_catalog import build_default_capabilities
from eidolon.core.capability_models import Capability
from eidolon.domain.mission.next_action import derive_next_action
from eidolon.runtime_health_payloads import evidence_health_payload, health_payload, knowledge_graph_health_payload, mesh_metrics_payload
from eidolon.runtime_service_auth import spawn_openai_device_login


ROOT = Path(__file__).resolve().parents[1]
CHAT_UI = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
SETTINGS_UI = ROOT / 'python' / 'eidolon' / 'web' / 'settings-ui.js'
DASHBOARD_UI = ROOT / 'python' / 'eidolon' / 'web' / 'dashboard-ui.js'
SKILLS_UI = ROOT / 'python' / 'eidolon' / 'web' / 'skills-backups-ui.js'
OPERATE_RENDER = ROOT / 'python' / 'eidolon' / 'web' / 'operate-render-ui.js'
OPERATE_ACTIONS = ROOT / 'python' / 'eidolon' / 'web' / 'operate-actions-ui.js'
APP_SHELL = ROOT / 'python' / 'eidolon' / 'web' / 'app-shell.js'


def test_k6_chat_ui_reads_envelope_and_top_level_response():
    js = CHAT_UI.read_text(encoding='utf-8')
    assert 'function chatModelText(r)' in js
    assert 'r.data && r.data.response' in js
    assert 'typeof r?.response === \'string\' && r.response.trim()' not in js or 'chatModelText(r)' in js


def test_k6_self_reflection_api_exposes_response_for_ui():
    client = TestClient(agent_server.app)
    original = agent_server.llm_backend.complete

    async def fake_complete(system, user):
        return 'Echte Reflexion über den aktuellen Stand.'

    agent_server.llm_backend.complete = fake_complete
    try:
        response = client.post('/api/v1/self-reflection/chat', json={'message': 'reflektiere dich'})
        assert response.status_code == 200
        body = response.json()
        assert body.get('ok') is True
        assert body.get('response') == 'Echte Reflexion über den aktuellen Stand.'
        assert (body.get('data') or {}).get('response') == 'Echte Reflexion über den aktuellen Stand.'
    finally:
        agent_server.llm_backend.complete = original


def test_k1_login_ok_only_when_really_logged_in():
    payload = spawn_openai_device_login()
    assert not payload.get('session_id')
    assert not payload.get('user_code')
    if payload.get('logged_in'):
        assert payload['ok'] is True
    else:
        assert payload['ok'] is False


def test_k1_settings_ui_has_no_device_code_placebo():
    js = SETTINGS_UI.read_text(encoding='utf-8')
    assert 'function triggerOpenAILogin' not in js
    assert 'Login erfolgreich' not in js
    assert "showNotice(result.detail || 'OpenAI verbunden', 'success')" not in js
    assert 'ChatGPT-Login läuft nur über die Codex-CLI' in js
    assert "api('GET', '/llm/connection')" in js
    assert "openai.configured === true || openai.logged_in === true" in js


def test_k2_capability_default_is_not_available():
    cap = Capability('probe.default', 'Default-Probe')
    assert cap.check_available() is False
    assert cap.to_dict()['available'] is False


def test_k2_skills_runtime_and_autonomy_loop_are_not_claimed():
    by_id = {item.id: item for item in build_default_capabilities()}
    assert by_id['skills.runtime'].check_available() is True
    detail = by_id['skills.runtime'].detail.lower()
    assert 'note' in detail and 'system_info' in detail
    assert 'openclaw' in detail or 'hermes' in detail
    assert by_id['autonomy.loop'].check_available() is False
    assert 'keine hintergrundschleife' in by_id['autonomy.loop'].detail.lower()


def test_k2_capabilities_endpoint_does_not_default_true():
    import eidolon.core.capabilities as caps_mod
    caps_mod._registry = None
    client = TestClient(agent_server.app)
    payload = client.get('/capabilities').json()
    by_id = {item['id']: item for item in payload['capabilities']}
    assert by_id['skills.runtime']['available'] is True
    assert by_id['autonomy.loop']['available'] is False
    health = client.get('/health').json()
    assert by_id['mesh.quic']['available'] is bool(health['components']['quic_port']['listening'])


def test_k3_skills_page_is_labeled_catalog():
    shell = APP_SHELL.read_text(encoding='utf-8')
    ui = SKILLS_UI.read_text(encoding='utf-8')
    assert 'ausführbar nur im Chat, wo verdrahtet' in shell
    assert 'Katalog · nicht verdrahtet' in ui
    assert 'ausführbar im Chat' in ui
    assert "s.enabled ? 'ok'" not in ui


def test_k3_skills_api_is_honest_about_memory_only():
    client = TestClient(agent_server.app)
    listed = client.get('/skills').json()
    assert listed['ok'] is True
    assert listed['catalog_only'] is False
    assert listed['runtime_wired'] is True
    assert listed['persistence'] == 'memory'
    by_name = {skill['name']: skill for skill in listed['skills']}
    assert by_name['chat']['executable'] is False
    assert by_name['note']['executable'] is True
    assert not all(skill.get('executable') for skill in listed['skills'])
    disabled = client.post('/skills/chat/disable').json()
    assert disabled['ok'] is True
    assert disabled['persisted'] is False
    assert disabled['runtime_wired'] is False
    client.post('/skills/chat/enable')


def test_k4_next_action_labels_phase_advance_without_execution():
    class _Run:
        current_phase = 'plan'
        next_transition = 'execute'
        state = 'planning'
        state_reason = 'Approval granted'

    action = derive_next_action(_Run(), [], [])
    assert action.kind == 'next_step'
    assert action.action_label == 'Phase fortschreiben'
    assert action.execution_wired is False
    assert 'keine ausführung' in (action.summary or '').lower()


def test_k4_ui_and_api_do_not_imply_external_execution():
    chat = CHAT_UI.read_text(encoding='utf-8')
    render = OPERATE_RENDER.read_text(encoding='utf-8')
    actions = OPERATE_ACTIONS.read_text(encoding='utf-8')
    assert "nextAction.kind === 'approval_request' && !approvals.length" in chat
    assert 'Freigabe erneut anfordern' in chat
    assert 'Phase fortschreiben' in chat
    assert 'Phase fortschreiben' in render
    assert "row('Ausführung'" in render
    assert 'Freigabe notiert' in actions
    assert 'Ausführung (Buchung, Mail, externe Aktion) ist nicht angebunden' in actions


def test_k4_approval_api_reports_execution_not_wired(tmp_path, monkeypatch):
    from eidolon.core.evidence import EvidenceStore
    from eidolon.operate.service import OperateService

    service = OperateService(project_root=tmp_path, db_path=tmp_path / 'operate.db', evidence_store=EvidenceStore(tmp_path / 'evidence.db'))
    started = service.start_objective(
        user_request='deploy release',
        title='Deploy release',
        normalized_goal='Deploy release',
        scope_summary='deploy',
    )
    run = started['run']
    gate = service.request_approval(
        run_id=run.id,
        title='Deploy',
        summary='Would change external system state',
        action_type='deploy',
    )
    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    client = TestClient(agent_server.app)
    resolved = client.post(f'/api/v1/runs/{run.id}/approval/{gate.id}', json={'decision': 'approved', 'resolved_by': 'user'})
    assert resolved.status_code == 200
    body = resolved.json()
    assert body['data']['approval']['status'] == 'approved'
    assert body['data']['execution']['wired'] is False
    assert 'Executor' in body['data']['execution']['detail']


def test_k5_health_does_not_mark_placeholders_available():
    kg = knowledge_graph_health_payload()
    if not kg['available']:
        assert kg.get('stats') in (None, {})
        assert kg.get('detail')
    evidence = evidence_health_payload()
    if evidence['available']:
        assert isinstance(evidence.get('verified'), int)
        assert isinstance(evidence.get('blocked'), int)
    else:
        assert evidence.get('verified') is None
    mesh = mesh_metrics_payload(None, 0)
    assert mesh['available'] is False
    assert mesh['avg_latency'] is None
    assert mesh['metrics_complete'] is False

    client = TestClient(agent_server.app)
    payload = client.get('/health').json()
    comps = payload['components']
    kg_live = comps['knowledge_graph']
    if kg_live['available']:
        assert isinstance((kg_live.get('stats') or {}).get('entities'), int)
    else:
        assert kg_live.get('stats') in (None, {})
    assert comps['skills']['available'] is True
    assert comps['skills'].get('catalog_only') is False
    assert comps['skills'].get('executable_count', 0) >= 3
    assert comps['mesh_metrics']['avg_latency'] is None
    assert comps['mesh_metrics']['metrics_complete'] is False
    if comps['evidence']['available']:
        assert isinstance(comps['evidence']['verified'], int)
    else:
        assert comps['evidence']['verified'] is None


def test_k5_dashboard_renders_problems_and_host_badge():
    js = DASHBOARD_UI.read_text(encoding='utf-8')
    assert "document.getElementById('health-problems')" in js
    assert 'd.problems' in js
    assert "label: 'Host · Grenzen'" in js
    assert 'Nicht angebunden' in js or 'nicht angebunden' in js.lower()


def test_health_payload_builder_stays_honest_without_mesh():
    payload = health_payload(
        server_start=__import__('time').time(),
        goal_stats={'total': 0, 'active_count': 0, 'done_count': 0, 'overall_progress': 0.0, 'by_status': {}},
        backup_stats={'count': 0, 'max_backups': 3, 'total_size_mb': 0},
        healing_state={'running': False, 'total_checks': 0, 'checks_registered': []},
        quic_status={'available': False, 'listening': False, 'status': 'not_wired'},
        caps=[{'id': 'skills.runtime', 'available': False}],
        certs={'complete': False},
        builtin_skills=[{'name': 'chat', 'enabled': True}],
        human_duration=lambda seconds: f'{seconds}s',
        http_port=8080,
        quic_port=4433,
        get_mesh_service=None,
    )
    assert payload['components']['skills']['available'] is True
    assert payload['components']['mesh_metrics']['available'] is False
    assert payload['components']['mesh_metrics']['peer_count'] is None
    assert payload['problems']
