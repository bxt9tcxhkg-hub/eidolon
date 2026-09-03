from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.core.evidence import EvidenceStore
from eidolon.operate.service import OperateService
from eidolon.workspaces.project_model import ProjectService
from eidolon.workspaces.workspace_ui_service import WorkspaceUIService


def _services(tmp_path):
    project_service = ProjectService(tmp_path)
    workspace_ui_service = WorkspaceUIService(tmp_path)
    workspace_ui_service._project_service = project_service
    operate_service = OperateService(project_root=tmp_path, db_path=tmp_path / 'operate.db', evidence_store=EvidenceStore(tmp_path / 'evidence.db'))
    workspace_ui_service._operate_service = operate_service
    return project_service, workspace_ui_service, operate_service


def test_workspace_execute_creates_real_subagent_lifecycle_and_operate_snapshot(tmp_path, monkeypatch):
    project_service, workspace_ui_service, operate_service = _services(tmp_path)
    project = project_service.create_project('Kernel Migration', 'Close the remaining operate gaps', 'general')
    project_service.add_element(project.id, title='Wire API', status='planned', element_type='task')

    monkeypatch.setattr(agent_server, 'project_service', project_service, raising=False)
    monkeypatch.setattr(agent_server, 'workspace_ui_service', workspace_ui_service, raising=False)
    monkeypatch.setattr(agent_server, 'operate_service', operate_service, raising=False)
    client = TestClient(agent_server.app)

    response = client.post(f'/workspaces/project_{project.id}/orchestration/execute', json={
        'module_id': 'board',
        'action': 'set_status',
        'payload': {'index': 0, 'status': 'in_progress'},
    })
    data = response.json()

    assert response.status_code == 200
    assert data['ok'] is True
    assert data['operate']['run']['state'] in {'planning', 'acting', 'spawning_work'}
    assert len(data['operate']['subagents']) >= 1
    assert any(item['state'] == 'completed' for item in data['operate']['subagents'])
    assert len(data['operate']['history']) >= 1


def test_project_element_endpoint_now_feeds_operate_kernel(tmp_path, monkeypatch):
    project_service, workspace_ui_service, operate_service = _services(tmp_path)
    project = project_service.create_project('Primary Operate Surface', 'Make operate the dominant product mode', 'general')

    monkeypatch.setattr(agent_server, 'project_service', project_service, raising=False)
    monkeypatch.setattr(agent_server, 'workspace_ui_service', workspace_ui_service, raising=False)
    monkeypatch.setattr(agent_server, 'operate_service', operate_service, raising=False)
    client = TestClient(agent_server.app)

    created = client.post(f'/projects/{project.id}/elements', json={'title': 'Move history into operate', 'status': 'planned', 'element_type': 'task'})
    created_json = created.json()

    assert created.status_code == 200
    assert created_json['ok'] is True
    assert created_json['operate']['run']['state'] == 'planning'
    assert any(item['state'] == 'completed' for item in created_json['operate']['subagents'])


def test_operate_history_and_work_graph_endpoints_reflect_kernel_state(tmp_path, monkeypatch):
    _, workspace_ui_service, operate_service = _services(tmp_path)
    started = operate_service.start_objective(user_request='Ship operate kernel', decomposition_mode='multi_stream')
    run = started['run']
    operate_service.spawn_subagent_run(run.id, 'Executor', 'executor', 'Implement API', 'Ready to work')
    operate_service.emit_evidence('run', run.id, 'verification', 'API verified', 'Endpoints answered correctly')

    monkeypatch.setattr(agent_server, 'workspace_ui_service', workspace_ui_service, raising=False)
    monkeypatch.setattr(agent_server, 'operate_service', operate_service, raising=False)
    client = TestClient(agent_server.app)

    history = client.get(f'/api/v1/runs/{run.id}/history').json()
    graph = client.get(f'/api/v1/runs/{run.id}/work-graph').json()

    assert history['ok'] is True
    assert len(history['data']['history']) >= 2
    assert graph['ok'] is True
    assert any(node['kind'] == 'run' for node in graph['data']['nodes'])
    assert any(node['kind'] == 'subagent' for node in graph['data']['nodes'])
    assert any(edge['type'] == 'spawned' for edge in graph['data']['edges'])


def test_operate_blocker_and_approval_actions_are_directly_actionable(tmp_path, monkeypatch):
    _, workspace_ui_service, operate_service = _services(tmp_path)
    started = operate_service.start_objective(user_request='Close blockers')
    run = started['run']
    blocker, _ = operate_service.open_blocking_issue(run.id, 'Need input', 'Waiting for blocker resolution', resolution_hint='Clarify the missing input')
    gate = operate_service.request_approval(run.id, 'Ship it?', 'Need explicit approval before release', 'release')

    monkeypatch.setattr(agent_server, 'workspace_ui_service', workspace_ui_service, raising=False)
    monkeypatch.setattr(agent_server, 'operate_service', operate_service, raising=False)
    client = TestClient(agent_server.app)

    resolved_blocker = client.post(f'/api/v1/runs/{run.id}/blockers/{blocker.id}/resolve', json={'resume_state': 'planning', 'state_reason': 'User clarified the blocker'})
    resolved_approval = client.post(f'/api/v1/runs/{run.id}/approval/{gate.id}', json={'decision': 'approved', 'resolved_by': 'user'})

    assert resolved_blocker.status_code == 200
    assert resolved_blocker.json()['data']['blocking_issue']['status'] == 'resolved'
    assert resolved_approval.status_code == 200
    assert resolved_approval.json()['data']['approval']['status'] == 'approved'
