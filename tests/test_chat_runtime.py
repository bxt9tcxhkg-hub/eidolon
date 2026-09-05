from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.chat_error_support import prune_synthetic_chat_sessions, scrub_chat_sessions


def test_chat_endpoint_returns_real_model_response():
    interaction_log = Path(__file__).resolve().parents[1] / 'data' / 'user' / 'interaction_log.jsonl'
    original = interaction_log.read_text(encoding='utf-8') if interaction_log.exists() else None
    original_status = agent_server.llm_backend.status()
    agent_server.llm_backend.configure(
        provider='ollama',
        model='llama3.1:8b',
        ollama_url='http://127.0.0.1:11434',
        fallback_chain=['ollama'],
    )
    client = TestClient(agent_server.app)
    try:
        response = client.post('/chat', json={'message': 'Antworte nur mit dem Wort OK.', 'source': 'test-chat-runtime'})

        assert response.status_code == 200
        payload = response.json()
        assert payload['ok'] is True
        assert isinstance(payload.get('response'), str)
        assert payload['response'].strip()
        assert 'Eidolon hat deine Nachricht erhalten' not in payload['response']
        assert 'noch nicht angebunden' not in payload.get('error', '')
        session_id = payload.get('session_id')
    finally:
        if 'session_id' in locals() and session_id:
            agent_server.chat_session_store.delete_session(session_id)
        agent_server.llm_backend.configure(
            provider=original_status['provider'],
            model=original_status['model'],
            ollama_url=original_status['ollama_url'],
        )
        if original is None:
            if interaction_log.exists():
                interaction_log.unlink()
        else:
            interaction_log.write_text(original, encoding='utf-8')


def test_chat_endpoint_answers_model_question_with_runtime_truth_without_evasion():
    original_status = agent_server.llm_backend.status()
    agent_server.llm_backend.configure(
        provider='openai_oauth',
        model='gpt-5.5',
        ollama_url='http://localhost:11434',
    )
    client = TestClient(agent_server.app)
    try:
        response = client.post('/chat', json={'message': 'welches modell bist du', 'source': 'test-model-truth'})
        assert response.status_code == 200
        payload = response.json()
        assert payload['ok'] is True
        assert 'gpt-5.5' in payload['response']
        assert 'openai_oauth' in payload['response']
        assert 'Wie kann ich helfen' not in payload['response']
        assert 'Wie kann ich dir im Kontext dieses Systems konkret helfen' not in payload['response']
        session_id = payload.get('session_id')
    finally:
        if 'session_id' in locals() and session_id:
            agent_server.chat_session_store.delete_session(session_id)
        agent_server.llm_backend.configure(
            provider=original_status['provider'],
            model=original_status['model'],
            ollama_url=original_status['ollama_url'],
        )


def test_social_chat_prompt_is_not_forced_into_continue_existing_work(monkeypatch):
    client = TestClient(agent_server.app)
    captured = {}
    payload = {
        'context_model': {
            'current_context_state': 'active_project',
            'current_phase': 'execute',
            'next_transition': 'continue_execution',
            'next_step': 'Aktiven Projektschritt sichtbar fortführen und verifizieren.',
            'chat_topic_count': 0,
        },
        'topics': [],
        'proactive_assistance': {'suggestions': []},
        'workspaces': [{
            'workspace_id': 'project_chat_mode',
            'topic_label': 'Operate Workspace Bridge',
            'workspace_type': 'project_workspace',
            'state': 'active',
            'product_state': 'active_project',
            'state_data': {'next_actions': ['Arbeitskontext später fortsetzen']},
        }],
    }

    async def fake_complete(system: str, user: str) -> str:
        captured['system'] = system
        captured['user'] = user
        return 'Verstanden. Ich arbeite als Eidolon: hilfreich, präzise und ehrlich.'

    monkeypatch.setattr(agent_server.workspace_ui_service, 'get_runtime_payload', lambda: payload)
    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)

    response = client.post('/chat', json={'message': 'lass uns ein bisschen plaudern', 'source': 'test-social-chat'})
    assert response.status_code == 200
    body = response.json()
    assert body['ok'] is True
    assert body['runtime_context']['user_intent']['classification'] == 'casual_chat'
    assert body['runtime_context']['user_intent']['is_work_oriented'] is False
    assert 'normaler Gesprächspartner' in captured['system']
    assert 'nicht primär ein allgemeiner Chat-Assistent' not in captured['system']
    assert 'normal' in body['response'].lower()
    assert 'operativ' in body['response'].lower() or 'normal' in body['response'].lower()
    assert 'Konkreter nächster Schritt:' not in body['response']
    session_id = body['session_id']
    client.delete(f'/chat/sessions/{session_id}')


def test_who_are_you_prompt_is_not_hijacked_into_model_truth_reply(monkeypatch):
    client = TestClient(agent_server.app)

    async def fake_complete(system: str, user: str) -> str:
        return 'Wir können uns auch einfach normal unterhalten.'

    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)
    response = client.post('/chat', json={'message': 'wer bist du', 'source': 'test-who-are-you'})
    assert response.status_code == 200
    body = response.json()
    assert body['ok'] is True
    assert body['runtime_context']['user_intent']['classification'] == 'casual_chat'
    assert 'gpt-5.5 über den Provider openai_oauth' not in body['response']
    assert 'normal' in body['response'].lower()
    assert 'über den Provider' not in body['response']
    session_id = body['session_id']
    client.delete(f'/chat/sessions/{session_id}')


def test_social_chat_generic_help_is_replaced_with_non_work_fallback(monkeypatch):
    client = TestClient(agent_server.app)
    payload = {
        'context_model': {
            'current_context_state': 'active_project',
            'current_phase': 'execute',
            'next_transition': 'continue_execution',
            'next_step': 'Aktiven Projektschritt sichtbar fortführen und verifizieren.',
            'chat_topic_count': 0,
        },
        'topics': [],
        'proactive_assistance': {'suggestions': []},
        'workspaces': [{
            'workspace_id': 'project_chat_mode',
            'topic_label': 'Operate Workspace Bridge',
            'workspace_type': 'project_workspace',
            'state': 'active',
            'product_state': 'active_project',
            'state_data': {'next_actions': ['Arbeitskontext später fortsetzen']},
        }],
    }

    async def fake_complete(system: str, user: str) -> str:
        return 'Verstanden. Wie kann ich helfen?'

    monkeypatch.setattr(agent_server.workspace_ui_service, 'get_runtime_payload', lambda: payload)
    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)
    response = client.post('/chat', json={'message': 'lass uns ein bisschen plaudern', 'source': 'test-social-generic-help'})
    assert response.status_code == 200
    body = response.json()
    assert body['ok'] is True
    assert body['runtime_context']['user_intent']['classification'] == 'casual_chat'
    assert 'Wie kann ich helfen' not in body['response']
    assert 'operativ' in body['response'].lower() or 'normal' in body['response'].lower()
    assert body['response_quality']['used_fallback'] is True
    session_id = body['session_id']
    client.delete(f'/chat/sessions/{session_id}')


def test_chat_sessions_persist_and_isolate_multiple_conversations():
    client = TestClient(agent_server.app)
    session_a = client.post('/chat/sessions', json={'title': 'Session A', 'source': 'test'}).json()['session']
    session_b = client.post('/chat/sessions', json={'title': 'Session B', 'source': 'test'}).json()['session']

    first = client.post('/chat', json={'message': 'welches modell bist du', 'source': 'test', 'session_id': session_a['session_id']})
    second = client.post('/chat', json={'message': 'welches modell bist du', 'source': 'test', 'session_id': session_b['session_id']})
    assert first.status_code == 200
    assert second.status_code == 200

    loaded_a = client.get(f"/chat/sessions/{session_a['session_id']}").json()['session']
    loaded_b = client.get(f"/chat/sessions/{session_b['session_id']}").json()['session']
    listed = client.get('/chat/sessions').json()['sessions']

    assert loaded_a['session_id'] != loaded_b['session_id']
    assert len(loaded_a['messages']) == 2
    assert len(loaded_b['messages']) == 2
    assert loaded_a['messages'][0]['content'] == 'welches modell bist du'
    assert 'über den Provider' in loaded_a['messages'][1]['content']
    assert any(item['session_id'] == session_a['session_id'] for item in listed)
    assert any(item['session_id'] == session_b['session_id'] for item in listed)

    deleted_a = client.delete(f"/chat/sessions/{session_a['session_id']}").json()
    deleted_b = client.delete(f"/chat/sessions/{session_b['session_id']}").json()
    assert deleted_a['ok'] is True
    assert deleted_b['ok'] is True


def test_chat_endpoint_sanitizes_internal_backend_auth_errors(monkeypatch):
    client = TestClient(agent_server.app)

    async def fake_complete(system: str, user: str) -> str:
        raise RuntimeError('Codex-Fehler (exit 1): Reading additional input from stdin... ERROR rmcp:transport:worker: worker quit with fatal: Transport channel closed, when AuthRequired(AuthRequiredError { www_authenticate_header: "Bearer error=\"invalid_request\"", error_description="No access token was provided in this request", resource_metadata="https://mcp.supabase" })')

    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)
    response = client.post('/chat', json={'message': 'lass uns ein bisschen plaudern', 'source': 'test-auth-sanitize'})
    assert response.status_code == 200
    body = response.json()
    assert body['ok'] is False
    assert body['error_code'] == 'backend_auth_unavailable'
    assert 'abhängigen Auth- oder MCP-Dienst' in body['error']
    assert 'www_authenticate' not in body['error']
    assert 'No access token was provided' not in body['error']
    session_id = body['session_id']
    try:
        session = client.get(f'/chat/sessions/{session_id}').json()['session']
        assistant = session['messages'][-1]['content']
        assert 'Fehler:' in assistant
        assert 'gültige Anmeldung' in assistant
        assert 'www_authenticate' not in assistant
        assert 'No access token was provided' not in assistant
        assert 'mcp.supabase' not in assistant
    finally:
        client.delete(f'/chat/sessions/{session_id}')


def test_scrub_chat_sessions_redacts_leaked_internal_backend_errors():
    sessions = [{
        'session_id': 's1',
        'messages': [
            {'role': 'user', 'content': 'hi'},
            {'role': 'assistant', 'content': 'Fehler: Codex-Fehler (exit 1): Reading additional input from stdin... AuthRequired www_authenticate_header: Bearer error="invalid_request" error_description="No access token was provided in this request" resource_metadata="https://mcp.supabase"'},
        ],
    }]
    changed = scrub_chat_sessions(sessions)
    assert changed is True
    assistant = sessions[0]['messages'][1]['content']
    assert 'gültige Anmeldung' in assistant
    assert 'www_authenticate' not in assistant
    assert 'No access token was provided' not in assistant
    assert 'mcp.supabase' not in assistant


def test_scrub_chat_sessions_rewrites_social_work_drift_replies():
    sessions = [{
        'session_id': 's2',
        'messages': [
            {'role': 'user', 'content': 'ich will dass du mich kennenlernst'},
            {'role': 'assistant', 'content': 'Verstanden. Was soll ich als Nächstes für dich erledigen?'},
        ],
    }]
    changed = scrub_chat_sessions(sessions)
    assert changed is True
    assistant = sessions[0]['messages'][1]['content']
    assert 'kennenlernen' in assistant
    assert 'erledigen' not in assistant


def test_prune_synthetic_chat_sessions_removes_test_and_verify_entries():
    sessions = [
        {'session_id': 'keep1', 'source': 'chat', 'messages': []},
        {'session_id': 'drop1', 'source': 'verify-normal-chat-live', 'messages': []},
        {'session_id': 'drop2', 'source': 'test-social-chat', 'messages': []},
        {'session_id': 'drop3', 'source': 'pre-restart-check', 'messages': []},
    ]
    changed = prune_synthetic_chat_sessions(sessions)
    assert changed is True
    assert [s['session_id'] for s in sessions] == ['keep1']


def test_chat_open_work_prompt_uses_grounded_fallback_when_model_returns_generic_help(monkeypatch):
    client = TestClient(agent_server.app)
    payload = {
        'context_model': {
            'current_context_state': 'active_project',
            'current_phase': 'execute',
            'next_transition': 'continue_execution',
            'next_step': 'Aktiven Projektschritt sichtbar fortführen und verifizieren.',
            'chat_topic_count': 0,
        },
        'topics': [{'label': 'Chat-Logik'}],
        'proactive_assistance': {'suggestions': []},
        'workspaces': [{
            'workspace_id': 'project_chat_logic',
            'topic_label': 'Chat-Logik härten',
            'workspace_type': 'project_workspace',
            'state': 'active',
            'product_state': 'active_project',
            'state_data': {
                'next_actions': ['Antwortpolitik härten'],
                'module_data': {
                    'board': {
                        'summary': {
                            'blocked': 1,
                            'in_progress': 0,
                            'ready': 2,
                            'done': 0,
                            'total': 3,
                            'blocked_items': [
                                {'label': 'Generische Erstreaktion', 'blocker_reason': 'Chat fällt auf generische Hilfsangebote zurück'}
                            ],
                        }
                    }
                },
            },
            'semantic_frame': {'primary_goal': 'Agentische Erstreaktion stärken'},
        }],
    }

    async def fake_complete(system: str, user: str) -> str:
        return 'Verstanden. Wie kann ich helfen?'

    monkeypatch.setattr(agent_server.workspace_ui_service, 'get_runtime_payload', lambda: payload)
    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)

    response = client.post('/chat', json={'message': 'was können wir zwei anstellen?', 'source': 'test-open-work'})
    assert response.status_code == 200
    body = response.json()
    assert body['ok'] is True
    assert 'Wie kann ich helfen' not in body['response']
    assert 'Sinnvolle Richtungen jetzt:' in body['response']
    assert 'Ich empfehle:' in body['response']
    assert body['response_quality']['used_fallback'] is True
    assert body['response_quality']['generic_assistant_pattern'] is True
    assert body['runtime_context']['workflow_state']['current_context_state'] == 'active_project'
    assert body['runtime_context']['user_intent']['classification'] == 'repair_or_unblock'

    session_id = body['session_id']
    try:
        context_response = client.get('/chat/context', params={'session_id': session_id})
        assert context_response.status_code == 200
        context_body = context_response.json()
        assert context_body['runtime_context']['workflow_state']['current_phase'] == 'execute'
        assert context_body['runtime_context']['project_context']['active_project_title'] == 'Chat-Logik härten'
        assert context_body['runtime_context']['user_intent']['is_open_work_prompt'] is True
    finally:
        client.delete(f'/chat/sessions/{session_id}')


def test_chat_prompt_includes_work_leading_contract_and_runtime_context(monkeypatch):
    client = TestClient(agent_server.app)
    captured = {}
    payload = {
        'context_model': {
            'current_context_state': 'project_candidate',
            'current_phase': 'form_project',
            'next_transition': 'promote_candidate_to_project',
            'next_step': 'Projektkandidaten in einen belastbaren Verantwortungsbereich überführen.',
            'chat_topic_count': 1,
        },
        'topics': [{'label': 'Prompt-Contract'}],
        'proactive_assistance': {'suggestions': []},
        'workspaces': [{
            'workspace_id': 'candidate_prompt_contract',
            'topic_label': 'Prompt-Contract',
            'workspace_type': 'project_workspace',
            'state': 'suggested',
            'product_state': 'project_candidate',
            'state_data': {'next_actions': ['Kontextschema festziehen']},
        }],
    }

    async def fake_complete(system: str, user: str) -> str:
        captured['system'] = system
        captured['user'] = user
        return 'Ich verstehe den Fokus und leite die nächste Richtung ab.'

    monkeypatch.setattr(agent_server.workspace_ui_service, 'get_runtime_payload', lambda: payload)
    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)

    response = client.post('/chat', json={'message': 'setz das um', 'source': 'test-prompt-contract'})
    assert response.status_code == 200
    body = response.json()
    assert body['ok'] is True
    assert 'Du bist nicht primär ein allgemeiner Chat-Assistent' in captured['system']
    assert 'RUNTIME_CONTEXT_JSON:' in captured['system']
    assert 'project_candidate' in captured['system']
    assert 'SESSION_VERLAUF:' in captured['user']
    assert 'LETZTE_NACHRICHT:' in captured['user']
    assert 'setz das um' in captured['user']

    session_id = body['session_id']
    client.delete(f'/chat/sessions/{session_id}')


def test_chat_context_includes_operate_snapshot_fields(monkeypatch):
    client = TestClient(agent_server.app)
    payload = {
        'context_model': {
            'current_context_state': 'active_project',
            'current_phase': 'execute',
            'next_transition': 'verify',
            'chat_topic_count': 0,
        },
        'topics': [],
        'proactive_assistance': {'suggestions': []},
        'workspaces': [{
            'workspace_id': 'project_operate_sync',
            'topic_label': 'Operate Sync',
            'workspace_type': 'project_workspace',
            'state': 'active',
            'product_state': 'active_project',
            'state_data': {'next_actions': ['Arbeitskern vereinheitlichen']},
        }],
    }
    monkeypatch.setattr(agent_server.workspace_ui_service, 'get_runtime_payload', lambda: payload)
    monkeypatch.setattr(agent_server, 'build_operate_snapshot', lambda service, run_id=None: {
        'session': {'id': 'sess1', 'title': 'Operate Session', 'current_view': 'operate'},
        'objective': {'id': 'obj1', 'title': 'Arbeitskern', 'normalized_goal': 'Chat und Operate vereinheitlichen'},
        'run': {'id': 'run1', 'state': 'acting', 'current_phase': 'execute', 'next_transition': 'verify', 'approval_required': True, 'pending_interrupt_count': 2},
        'next_action': {'kind': 'approval_request', 'title': 'Freigabe nötig', 'summary': 'Freigabe für strukturelle Änderung einholen'},
        'approvals': [{'id': 'ap1', 'title': 'Freigabe nötig', 'status': 'pending'}],
        'blockers': [{'id': 'bl1', 'title': 'Wartet auf Klärung', 'status': 'open'}],
        'subagents': [{'id': 'sa1'}],
    })

    response = client.get('/chat/context')
    assert response.status_code == 200
    body = response.json()
    runtime = body['runtime_context']
    assert runtime['operate_context']['run_id'] == 'run1'
    assert runtime['operate_context']['objective_title'] == 'Arbeitskern'
    assert runtime['operate_context']['pending_approval_count'] == 1
    assert runtime['operate_context']['pending_approvals'][0]['id'] == 'ap1'
    assert runtime['operate_context']['open_blocker_count'] == 1
    assert runtime['operate_context']['open_blockers'][0]['id'] == 'bl1'
    assert runtime['workflow_state']['operate_run_state'] == 'acting'
    assert runtime['workflow_state']['approval_required'] is True
    assert runtime['workflow_state']['pending_interrupt_count'] == 2
    assert runtime['workflow_state']['next_step'] == 'Freigabe für strukturelle Änderung einholen'
    assert runtime['capabilities']['can_execute_actions'] is True
    assert runtime['capabilities']['can_spawn_specialists'] is True
