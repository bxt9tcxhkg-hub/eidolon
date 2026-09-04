from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.workspaces.generic_slots import build_generic_slots
from eidolon.workspaces.project_formation import FormationError, apply_transition, map_workspace_state_to_product_state, propose_product_state
from eidolon.workspaces.project_service import ProjectService
from eidolon.workspaces.registry import WorkspaceRegistry
from eidolon.workspaces.work_truth import describe_formation
from eidolon.workspaces.workspace_ui_service import WorkspaceUIService


def test_formation_heuristic_never_silently_creates_active_project():
    assert map_workspace_state_to_product_state('active', {'action_relevance': 1.0, 'recurrence_score': 1.0}) == 'project_candidate'
    assert propose_product_state('suggested', {'action_relevance': 0.5}) == 'project_candidate'
    assert propose_product_state('suggested', {'action_relevance': 0.1, 'recurrence_score': 0.1}) == 'chat_topic'
    assert propose_product_state('active', {'formation_confirmed': True}) == 'active_project'
    assert propose_product_state('active', {'formation_source': 'user_created_project'}) == 'active_project'


def test_candidate_to_active_requires_visible_confirmation():
    blocked = apply_transition('chat_topic', 'project_candidate', confirmed=False, reason='recurring_help')
    assert blocked['ok'] is True
    assert blocked['to_state'] == 'project_candidate'
    assert blocked['creates_durable_project'] is False
    try:
        apply_transition('project_candidate', 'active_project', confirmed=False)
        raise AssertionError('silent promotion must fail')
    except FormationError as exc:
        assert 'Bestätigung' in str(exc)
    promoted = apply_transition('project_candidate', 'active_project', confirmed=True, reason='user_ok')
    assert promoted['creates_durable_project'] is True
    assert promoted['formation_source'] == 'user_confirmed_promotion'


def test_user_created_project_is_confirmed_active_project(tmp_path):
    service = ProjectService(tmp_path)
    project = service.create_project('Explizites Projekt', 'Nutzer hat Anlegen gedrückt', 'general')
    assert project.metadata['formation_confirmed'] is True
    assert project.metadata['product_state'] == 'active_project'
    ui = WorkspaceUIService(tmp_path)
    workspace = ui._project_to_workspace(project)
    assert workspace['product_state'] == 'active_project'


def test_formation_api_promotes_topic_candidate_only_when_confirmed(tmp_path, monkeypatch):
    registry = WorkspaceRegistry(tmp_path)
    registry._save({
        'workspaces': [{
            'workspace_id': 'ws_candidate_demo',
            'topic_label': 'Eidolon Kernvertrag',
            'workspace_type': 'project_workspace',
            'state': 'suggested',
            'product_state': 'project_candidate',
            'metadata': {'formation_confirmed': False},
        }],
        'feature_flags': {'workspace_adaptive_modules': True},
    })
    ui = WorkspaceUIService(tmp_path)
    ui._registry = registry
    ui._project_service = ProjectService(tmp_path)
    from eidolon.operate.service import OperateService
    ui._operate_service = OperateService(tmp_path)
    monkeypatch.setattr(agent_server, 'workspace_ui_service', ui, raising=False)
    monkeypatch.setattr(agent_server, 'project_service', ui._project_service, raising=False)
    client = TestClient(agent_server.app)

    denied = client.post('/workspaces/formation', json={
        'workspace_id': 'ws_candidate_demo',
        'to_state': 'active_project',
        'confirmed': False,
    })
    assert denied.status_code == 400
    assert 'Bestätigung' in denied.json()['detail']

    accepted = client.post('/workspaces/formation', json={
        'workspace_id': 'ws_candidate_demo',
        'to_state': 'active_project',
        'confirmed': True,
        'reason': 'user_confirmed_promotion',
    })
    assert accepted.status_code == 200
    payload = accepted.json()
    assert payload['ok'] is True
    assert payload['to_state'] == 'active_project'
    assert payload['project']['title'] == 'Eidolon Kernvertrag'
    assert payload['project']['metadata']['formation_source'] == 'user_confirmed_promotion'
    assert payload['operate'] is not None
    assert payload['work_kernel']['formation']['current_state'] in {'active_project', 'project_candidate'}
    persisted = ui._project_service.get_project(payload['project']['id'])
    assert persisted is not None
    assert persisted.metadata['formation_confirmed'] is True


def test_chat_and_project_mutations_share_work_truth_operate(tmp_path, monkeypatch):
    service = ProjectService(tmp_path)
    project = service.create_project('Gemeinsame Wahrheit', 'Chat und Projektfläche', 'general')
    monkeypatch.setattr(agent_server, 'project_service', service, raising=False)
    client = TestClient(agent_server.app)
    created = client.post(f'/projects/{project.id}/elements', json={'title': 'Nächster Schritt', 'status': 'planned'})
    assert created.status_code == 200
    body = created.json()
    assert body['ok'] is True
    assert 'work_kernel' in body
    assert 'generic_slots' in body
    assert any(slot['kind'] == 'next' for slot in body['generic_slots'])
    overview = client.get('/api/v1/operate/overview').json()
    assert overview['ok'] is True
    assert 'work_kernel' in overview['data']
    assert overview['data']['work_kernel']['operate_context'] is not None
    chat_ctx = client.get('/chat/context').json()
    assert 'formation' in chat_ctx['runtime_context']
    assert 'operate_context' in chat_ctx['runtime_context']


def test_generic_slots_are_situation_adaptive_not_domain_packs():
    slots = build_generic_slots(
        project={'title': 'Beliebiges Vorhaben', 'status': 'in_progress', 'description': 'Kein Domänenpaket', 'elements': [{'title': 'Schritt', 'status': 'blocked', 'description': 'Wartet'}], 'inbox': [{'id': 'i1', 'text': 'Rohinput', 'processed': False}]},
        work_kernel={
            'workflow_state': {'current_context_state': 'active_project', 'current_phase': 'execute', 'next_step': 'Blocker lösen'},
            'project_context': {'active_project_title': 'Beliebiges Vorhaben', 'active_goal': 'Liefern'},
            'operate_context': {
                'run_state': 'blocked',
                'objective_title': 'Liefern',
                'pending_approvals': [{'id': 'a1', 'title': 'Freigabe', 'summary': 'Richtung bestätigen', 'status': 'pending'}],
                'open_blockers': [{'id': 'b1', 'title': 'Wartet', 'summary': 'Input fehlt', 'status': 'open'}],
                'next_action': {'kind': 'approval_request', 'title': 'Freigabe', 'summary': 'Richtung bestätigen'},
            },
        },
        operate={'evidence': [{'title': 'Hinweis', 'summary': 'Aus Workspace', 'kind': 'workspace_context'}]},
    )
    kinds = [slot['kind'] for slot in slots]
    assert kinds[:4] == ['context', 'goal', 'status', 'owner']
    assert 'approval' in kinds
    assert 'blocker' in kinds
    assert 'inbox' in kinds
    assert 'evidence' in kinds
    assert 'training' not in kinds
    assert 'instagram' not in kinds


def test_describe_formation_exposes_visible_promotion_contract():
    formation = describe_formation({
        'context_model': {
            'current_context_state': 'project_candidate',
            'next_transition': 'promote_candidate_to_project',
            'current_focus_label': 'Kernvertrag',
            'approval_state': 'project_role_requires_explicit_approval',
        },
        'workspaces': [{'workspace_id': 'ws_1', 'topic_label': 'Kernvertrag', 'product_state': 'project_candidate'}],
    })
    assert formation['requires_confirmation'] is True
    assert formation['creates_durable_project'] is True
    assert formation['action_label'] == 'Als Projekt übernehmen'
    assert formation['workspace_id'] == 'ws_1'
