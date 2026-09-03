from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.core.evidence import EvidenceStore
from eidolon.operate.bridge import sync_operate_with_workspace_payload  # type: ignore[import-not-found]
from eidolon.operate.service import OperateService  # type: ignore[import-not-found]


def _temp_service(tmp_path):
    evidence_db = tmp_path / 'evidence.db'
    legacy_store = EvidenceStore(evidence_db)
    return OperateService(project_root=tmp_path, db_path=tmp_path / 'operate.db', evidence_store=legacy_store), legacy_store


def test_operate_service_start_objective_creates_session_run_and_transition(tmp_path):
    service, _ = _temp_service(tmp_path)

    started = service.start_objective(
        user_request='fix deployment timeout',
        title='Fix deployment timeout',
        normalized_goal='Diagnose and resolve deployment timeout',
        scope_summary='diagnosis, fix, verification',
        decomposition_mode='multi_stream',
    )

    assert started['session'].title == 'Fix deployment timeout'
    assert started['objective'].normalized_goal == 'Diagnose and resolve deployment timeout'
    assert started['run'].state == 'understanding'
    assert started['run'].current_phase == 'understand'

    events = service.list_transition_events(started['run'].id)
    assert len(events) == 1
    assert events[0].transition_type == 'state_change'
    assert events[0].to_state == 'understanding'


def test_operate_service_can_spawn_subagent_and_mirror_evidence(tmp_path):
    service, legacy_store = _temp_service(tmp_path)
    started = service.start_objective(
        user_request='verify regression suite',
        title='Verify regression suite',
        normalized_goal='Run regression verification',
        scope_summary='verification',
        decomposition_mode='multi_stream',
    )
    run = started['run']

    subagent = service.spawn_subagent_run(
        run_id=run.id,
        display_name='Verification',
        function_type='verifier',
        mission='Run regression verification',
        state_reason='Verification worker created',
    )
    evidence = service.emit_evidence(
        owner_type='subagent',
        owner_id=subagent.id,
        kind='test_result',
        title='Regression suite',
        summary='18 passed',
        metadata_json={'passed': 18},
    )

    subagents = service.list_subagent_runs(run.id)
    assert len(subagents) == 1
    assert subagents[0].state == 'queued'

    evidence_items = service.list_evidence_items(run.id)
    assert len(evidence_items) == 1
    assert evidence_items[0].id == evidence.id

    legacy_observations = legacy_store.get_actions(limit=5)
    assert legacy_observations == []
    observations = legacy_store._connect().execute('SELECT kind, description, detail FROM observations').fetchall()
    assert len(observations) == 1
    assert observations[0]['kind'] == 'test_result'
    assert observations[0]['description'] == 'Regression suite'
    assert '18 passed' in observations[0]['detail']


def test_operate_service_request_and_resolve_approval_updates_run_state(tmp_path):
    service, _ = _temp_service(tmp_path)
    started = service.start_objective(
        user_request='deploy release',
        title='Deploy release',
        normalized_goal='Deploy release to production',
        scope_summary='deploy',
    )
    run = started['run']

    gate = service.request_approval(
        run_id=run.id,
        title='Deploy to production',
        summary='Would change external system state',
        action_type='deploy',
    )
    after_request = service.get_run(run.id)
    assert gate.status == 'pending'
    assert after_request.state == 'waiting'
    assert after_request.approval_required is True

    resolved = service.resolve_approval(gate.id, decision='approved', resolved_by='user')
    after_resolve = service.get_run(run.id)
    assert resolved.status == 'approved'
    assert after_resolve.state == 'planning'
    assert after_resolve.approval_required is False


def test_operate_api_routes_expose_run_truth(tmp_path, monkeypatch):
    service, _ = _temp_service(tmp_path)
    started = service.start_objective(
        user_request='fix deployment timeout',
        title='Fix deployment timeout',
        normalized_goal='Diagnose and resolve deployment timeout',
        scope_summary='diagnosis, fix, verification',
        decomposition_mode='multi_stream',
    )
    run = started['run']
    service.spawn_subagent_run(
        run_id=run.id,
        display_name='Research',
        function_type='research',
        mission='Inspect deployment logs',
        state_reason='Research worker created',
    )
    gate = service.request_approval(
        run_id=run.id,
        title='Deploy to production',
        summary='Would change external system state',
        action_type='deploy',
    )

    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    client = TestClient(agent_server.app)

    session_payload = client.get('/api/v1/session/current').json()
    run_payload = client.get('/api/v1/runs/current').json()
    subagents_payload = client.get(f'/api/v1/runs/{run.id}/subagents').json()
    approvals_payload = client.get(f'/api/v1/runs/{run.id}/approvals').json()
    next_action_payload = client.get(f'/api/v1/runs/{run.id}/next-action').json()

    assert session_payload['ok'] is True
    assert session_payload['data']['session']['current_run_id'] == run.id
    assert run_payload['data']['run']['id'] == run.id
    assert run_payload['data']['run']['state'] == 'waiting'
    assert run_payload['data']['run']['phase_preservation']['workflow_phases'][0] == 'chat_entry'
    assert run_payload['data']['run']['phase_preservation']['phase_status']['context_classification']['preserved'] is True
    assert len(subagents_payload['data']['subagents']) == 1
    assert approvals_payload['data']['approvals'][0]['id'] == gate.id
    assert next_action_payload['data']['next_action']['kind'] == 'approval_request'


def test_operate_api_interrupt_appends_transition(tmp_path, monkeypatch):
    service, _ = _temp_service(tmp_path)
    started = service.start_objective(
        user_request='investigate timeout',
        title='Investigate timeout',
        normalized_goal='Investigate timeout',
        scope_summary='investigation',
    )
    run = started['run']
    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    client = TestClient(agent_server.app)

    response = client.post(f'/api/v1/runs/{run.id}/interrupt', json={'type': 'redirect', 'message': 'Focus on API gateway logs'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['ok'] is True
    updated_run = payload['data']['run']
    assert updated_run['pending_interrupt_count'] == 1
    assert updated_run['current_phase'] == 'plan'

    transitions = client.get(f'/api/v1/runs/{run.id}/transitions').json()
    assert any(event['transition_type'] == 'interrupted' for event in transitions['data']['transitions'])


def test_operate_bridge_bootstraps_from_active_workspace_payload(tmp_path):
    service, _ = _temp_service(tmp_path)
    payload = {
        'workspaces': [{
            'workspace_id': 'project_abc123',
            'topic_label': 'API Runtime Cleanup',
            'state': 'active',
            'workspace_type': 'project_workspace',
            'metadata': {
                'project_id': 'abc123',
                'project_status': 'active',
                'project_description': 'Stabilize the runtime and close gaps',
            },
            'state_data': {
                'module_data': {
                    'board': {
                        'summary': {
                            'blocked': 1,
                            'in_progress': 0,
                            'ready': 2,
                            'done': 0,
                            'blocked_items': [{'id': 'e1', 'label': 'Fix API drift', 'blocker_reason': 'Contract mismatch'}],
                        }
                    }
                },
                'next_actions': ['Nächsten Schritt starten: Fix API drift'],
                'overview': 'Projektfläche für API Runtime Cleanup',
            },
        }],
    }

    started = sync_operate_with_workspace_payload(service, payload)

    assert started is not None
    assert started['session'].title == 'API Runtime Cleanup'
    assert started['run'].state == 'blocked'
    subagents = service.list_subagent_runs(started['run'].id)
    assert len(subagents) >= 2
    assert any(item.mission == 'Resolve blocker: Fix API drift' for item in subagents)
    assert any('Fix API drift' in item.mission for item in subagents)
    evidence = service.list_evidence_items(started['run'].id)
    assert len(evidence) >= 1


def test_operate_api_current_session_bootstraps_from_workspace_context(tmp_path, monkeypatch):
    service, _ = _temp_service(tmp_path)
    payload = {
        'workspaces': [{
            'workspace_id': 'project_boot',
            'topic_label': 'Bridge Operate Project',
            'state': 'active',
            'workspace_type': 'project_workspace',
            'metadata': {
                'project_id': 'boot1',
                'project_status': 'active',
                'project_description': 'Bridge active project into operate kernel',
            },
            'state_data': {
                'module_data': {
                    'board': {
                        'summary': {
                            'blocked': 0,
                            'in_progress': 1,
                            'ready': 1,
                            'done': 0,
                            'blocked_items': [],
                        }
                    }
                },
                'next_actions': ['Blocker auflösen', 'Nächsten Schritt starten'],
                'overview': 'Projektfläche für Bridge Operate Project',
            },
        }],
    }
    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    monkeypatch.setattr(agent_server.workspace_ui_service, 'get_runtime_payload', lambda: payload)
    client = TestClient(agent_server.app)

    session_payload = client.get('/api/v1/session/current').json()
    run_payload = client.get('/api/v1/runs/current').json()

    assert session_payload['ok'] is True
    assert session_payload['data']['session']['title'] == 'Bridge Operate Project'
    assert run_payload['data']['run']['state'] == 'acting'
    assert run_payload['data']['objective']['decomposition_mode'] == 'multi_stream'


def test_operate_api_advance_run_walks_real_state_machine(tmp_path, monkeypatch):
    service, _ = _temp_service(tmp_path)
    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    client = TestClient(agent_server.app)

    created = client.post('/api/v1/objectives', json={'user_request': 'Ship the operate kernel'})
    run_id = created.json()['data']['run']['id']

    first = client.post(f'/api/v1/runs/{run_id}/advance', json={'reason': 'Plan established'})
    second = client.post(f'/api/v1/runs/{run_id}/advance', json={'reason': 'Work streams spawned'})
    third = client.post(f'/api/v1/runs/{run_id}/advance', json={'reason': 'Execution started'})
    fourth = client.post(f'/api/v1/runs/{run_id}/advance', json={'reason': 'Verification started'})
    fifth = client.post(f'/api/v1/runs/{run_id}/advance', json={'reason': 'Work verified'})

    assert first.json()['data']['run']['state'] == 'planning'
    assert second.json()['data']['run']['state'] == 'spawning_work'
    assert third.json()['data']['run']['state'] == 'acting'
    assert fourth.json()['data']['run']['state'] == 'verifying'
    assert fifth.json()['data']['run']['state'] == 'completed'
    assert fifth.json()['data']['run']['result_status'] == 'success'


def test_operate_api_sync_endpoint_bootstraps_and_returns_run(tmp_path, monkeypatch):
    service, _ = _temp_service(tmp_path)
    payload = {
        'workspaces': [{
            'workspace_id': 'project_sync',
            'topic_label': 'Sync Operate Workspace',
            'state': 'active',
            'workspace_type': 'project_workspace',
            'metadata': {
                'project_id': 'sync1',
                'project_status': 'active',
                'project_description': 'Synchronize workspace into operate',
            },
            'state_data': {
                'module_data': {
                    'board': {
                        'summary': {
                            'blocked': 1,
                            'in_progress': 0,
                            'ready': 1,
                            'done': 0,
                            'blocked_items': [{'id': 'b1', 'label': 'Close sync gap', 'blocker_reason': 'Operate not linked'}],
                        }
                    }
                },
                'next_actions': ['Nächsten Schritt starten: Close sync gap'],
                'overview': 'Projektfläche für Sync Operate Workspace',
            },
        }],
    }
    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    monkeypatch.setattr(agent_server.workspace_ui_service, 'get_runtime_payload', lambda: payload)
    client = TestClient(agent_server.app)

    response = client.post('/api/v1/session/sync-from-workspaces')
    data = response.json()['data']

    assert response.status_code == 200
    assert data['session']['title'] == 'Sync Operate Workspace'
    assert data['run']['state'] == 'blocked'
    assert len(data['subagents']) >= 2


def test_operate_prefixed_goal_endpoints_return_goal_truth_and_operate_snapshot(tmp_path, monkeypatch):
    service, _ = _temp_service(tmp_path)
    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    client = TestClient(agent_server.app)

    created = client.post('/api/v1/operate/goals', json={'title': 'Collapse legacy autonomy surface', 'description': 'Move goal actions behind operate routes'})
    assert created.status_code == 200
    created_payload = created.json()['data']
    goal_id = created_payload['goal']['id']
    assert created_payload['goal']['title'] == 'Collapse legacy autonomy surface'
    assert 'operate' in created_payload

    goals = client.get('/api/v1/operate/goals').json()['data']
    assert any(goal['id'] == goal_id for goal in goals['goals'])
    assert 'operate' in goals

    transitioned = client.post(f'/api/v1/operate/goals/{goal_id}/transition', json={'status': 'active'}).json()['data']
    assert transitioned['goal']['status'] == 'active'
    assert 'operate' in transitioned

    revalidated = client.post('/api/v1/operate/revalidate', json={}).json()['data']
    assert 'operate' in revalidated

    derived = client.get('/api/v1/operate/derive').json()['data']
    assert 'operate' in derived


def test_legacy_autonomy_routes_are_degraded_to_operate_backed_compatibility(tmp_path, monkeypatch):
    service, _ = _temp_service(tmp_path)
    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    client = TestClient(agent_server.app)

    created = client.post('/autonomy/goals', json={'title': 'Compatibility route'})
    assert created.status_code == 200
    created_payload = created.json()
    assert created_payload['deprecated'] is True
    assert created_payload['canonical_path'] == '/api/v1/operate/goals'
    assert 'operate' in created_payload

    listed = client.get('/autonomy/goals').json()
    assert listed['deprecated'] is True
    assert listed['canonical_path'] == '/api/v1/operate/goals'
    assert 'operate' in listed

    cycle = client.post('/autonomy/cycle', json={}).json()
    assert cycle['deprecated'] is True
    assert cycle['canonical_path'] == '/api/v1/operate/cycle'
    assert 'operate' in cycle


def test_deprecated_autonomy_routes_cannot_become_sole_ui_truth_source(tmp_path, monkeypatch):
    service, _ = _temp_service(tmp_path)
    started = service.start_objective(
        user_request='Ship operate kernel',
        title='Ship operate kernel',
        normalized_goal='Ship operate kernel',
        scope_summary='understand, plan, execute, verify',
        decomposition_mode='multi_stream',
    )
    run = started['run']

    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    client = TestClient(agent_server.app)

    status = client.get('/autonomy/status').json()
    assert status['deprecated'] is True
    assert status['canonical_path'] == '/api/v1/operate/overview'

    cycle = client.post('/autonomy/cycle', json={}).json()
    assert cycle['deprecated'] is True
    assert cycle['canonical_path'] == '/api/v1/operate/cycle'

    derive = client.get('/autonomy/derive').json()
    assert derive['deprecated'] is True
    assert derive['canonical_path'] == '/api/v1/operate/derive'

    enforce = client.post('/autonomy/enforce-invariants', json={}).json()
    assert enforce['deprecated'] is True
    assert enforce['canonical_path'] == '/api/v1/operate/revalidate'

    revalidate = client.post('/autonomy/revalidate', json={}).json()
    assert revalidate['deprecated'] is True
    assert revalidate['canonical_path'] == '/api/v1/operate/revalidate'

    goals = client.get('/autonomy/goals').json()
    assert goals['deprecated'] is True
    assert goals['canonical_path'] == '/api/v1/operate/goals'

    stats = client.get('/autonomy/stats').json()
    assert stats['deprecated'] is True
    assert stats['canonical_path'] == '/api/v1/operate/goals'

    log = client.get('/autonomy/log').json()
    assert log['deprecated'] is True
    assert log['canonical_path'] == '/api/v1/operate/overview'

    overview = client.get('/api/v1/operate/overview').json()
    assert overview['ok'] is True
    assert 'deprecated' not in overview
    assert overview['data']['run']['id'] == run.id


def test_self_reflection_returns_real_codebase_analysis(tmp_path, monkeypatch):
    service, _ = _temp_service(tmp_path)
    started = service.start_objective(
        user_request='Ship operate kernel',
        title='Ship operate kernel',
        normalized_goal='Ship operate kernel',
        scope_summary='understand, plan, execute, verify',
        decomposition_mode='multi_stream',
    )

    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    client = TestClient(agent_server.app)

    response = client.get('/api/v1/self-reflection')
    assert response.status_code == 200
    payload = response.json()

    assert payload['ok'] is True
    assert 'data' in payload
    data = payload['data']

    # Summary
    assert 'summary' in data
    summary = data['summary']
    assert summary['total_files'] > 0
    assert summary['total_loc'] > 0
    assert summary['total_improvements'] >= 0

    # Improvements
    assert 'improvements' in data
    assert isinstance(data['improvements'], list)

    # Runtime issues
    assert 'runtime_issues' in data
    assert isinstance(data['runtime_issues'], list)

    # Code findings
    assert 'code_findings' in data
    assert isinstance(data['code_findings'], list)

    # File metrics
    assert 'file_metrics' in data
    assert isinstance(data['file_metrics'], list)
    assert len(data['file_metrics']) > 0

    # Doc freshness
    assert 'doc_freshness' in data
    assert isinstance(data['doc_freshness'], list)

    # Verify improvement structure
    for improvement in data['improvements']:
        assert 'priority' in improvement
        assert 'category' in improvement
        assert 'target' in improvement
        assert 'issue' in improvement
        assert 'suggestion' in improvement
        assert improvement['priority'] in ('critical', 'high', 'medium', 'low')


def test_operate_overview_is_compact_and_defers_deep_collections_to_lazy_endpoints(tmp_path, monkeypatch):
    service, _ = _temp_service(tmp_path)
    started = service.start_objective(
        user_request='Ship operate kernel',
        title='Ship operate kernel',
        normalized_goal='Ship operate kernel',
        scope_summary='understand, plan, execute, verify',
        decomposition_mode='multi_stream',
    )
    run = started['run']
    subagent = service.spawn_subagent_run(
        run_id=run.id,
        display_name='Verifier',
        function_type='verifier',
        mission='Run focused verification',
        state_reason='Verification worker created',
    )
    service.set_subagent_state(subagent.id, 'running', 'Verification in progress')
    service.emit_evidence(
        owner_type='subagent',
        owner_id=subagent.id,
        kind='test_result',
        title='Focused verification',
        summary='4 checks passed',
        metadata_json={'passed': 4},
    )

    monkeypatch.setattr(agent_server, 'operate_service', service, raising=False)
    client = TestClient(agent_server.app)

    overview = client.get('/api/v1/operate/overview')
    payload = overview.json()['data']

    assert overview.status_code == 200
    assert payload['run']['id'] == run.id
    assert 'history' not in payload
    assert 'transitions' not in payload
    assert 'work_graph' not in payload
    assert payload['deep_links']['history'].endswith(f'/api/v1/runs/{run.id}/history')
    assert payload['deep_links']['work_graph'].endswith(f'/api/v1/runs/{run.id}/work-graph')
    assert payload['counts']['subagents'] >= 1
    assert payload['counts']['evidence'] >= 1
    assert len(payload['subagents']) <= 3
    assert len(payload['evidence']) <= 5
