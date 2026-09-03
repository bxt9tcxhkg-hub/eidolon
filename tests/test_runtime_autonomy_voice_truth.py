from pathlib import Path
import os
import sys
import socket
import json
import asyncio

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.mesh.transport.quic_server import EidolonQuicClient, EidolonQuicServer
from eidolon.voice_runtime import VoiceRuntimeService
from eidolon.workspaces.orchestrator import WorkspaceOrchestrator


ROOT = Path(__file__).resolve().parents[1]


def test_runtime_process_endpoint_exposes_live_server_identity():
    client = TestClient(agent_server.app)
    response = client.get('/runtime/process')
    assert response.status_code == 200
    payload = response.json()
    assert payload['ok'] is True
    assert payload['server_pid'] == os.getpid()
    assert payload['lifecycle']['status'] == 'running'
    assert payload['lifecycle']['started_at']



def test_autonomy_status_prefers_active_workspace_action_over_goal_action(monkeypatch):
    client = TestClient(agent_server.app)

    monkeypatch.setattr(agent_server.autonomy_engine, 'next_best_action', lambda: {
        'action': 'complete_step',
        'goal_id': 'goal-1',
        'goal_title': 'Unrelated Goal',
        'step_id': 'step-1',
        'step_title': 'Do unrelated thing',
        'reason': 'goal engine still has an open step',
    })
    monkeypatch.setattr(agent_server.workspace_ui_service, 'get_runtime_payload', lambda: {
        'context_model': {'current_phase': 'execute'},
        'workspaces': [{
            'workspace_id': 'project_live',
            'topic_label': 'Workspace Truth Test',
            'workspace_type': 'project_workspace',
            'state': 'active',
            'metadata': {'project_id': 'project-live', 'project_status': 'active'},
            'state_data': {
                'orchestration': {
                    'next_best_action': {
                        'module_id': 'board',
                        'action': 'set_status',
                        'label': 'Blocker auflösen',
                        'payload': {'index': 0, 'status': 'ready', 'clear_blocker': True},
                        'reason': 'workspace has a blocked item',
                    }
                }
            },
        }],
    })

    response = client.get('/autonomy/status')
    assert response.status_code == 200
    payload = response.json()
    assert payload['effective_next_action']['source'] == 'workspace_orchestration'
    assert payload['effective_next_action']['label'] == 'Blocker auflösen'
    assert payload['goal_next_action']['action'] == 'complete_step'



def test_workspace_orchestrator_avoids_creating_duplicate_generic_followup_cards(tmp_path):
    workspace = {
        'workspace_id': 'ws_duplicate_generic',
        'topic_label': 'Projekt',
        'workspace_type': 'project_workspace',
        'layout_template': 'hybrid',
        'metadata': {'needs': {'planning': 0.95, 'execution': 0.2}},
        'state_data': {
            'module_data': {
                'next_actions': {'items': []},
                'board': {
                    'items': [
                        {'id': 'a', 'label': 'Nächsten konkreten Schritt ergänzen', 'status': 'planned', 'dependency_ids': []},
                        {'id': 'b', 'label': 'Schon in Arbeit', 'status': 'in_progress', 'dependency_ids': []},
                    ]
                },
                'graph': {'edges': [{'from': 'a', 'to': 'b', 'type': 'depends_on'}]},
            }
        },
    }
    result = WorkspaceOrchestrator(tmp_path).evaluate(workspace)
    action = result['next_best_action']
    assert not (action['module_id'] == 'board' and action['action'] == 'add_card' and action['payload'].get('label') == 'Nächsten konkreten Schritt ergänzen')



def test_evidence_summary_exposes_recent_actions_and_blocked_reasons():
    client = TestClient(agent_server.app)
    response = client.get('/evidence/summary')
    assert response.status_code == 200
    payload = response.json()
    assert 'recent_actions' in payload
    assert 'blocked_reasons' in payload



def test_voice_status_is_honest_about_tts_and_stt_state():
    client = TestClient(agent_server.app)
    response = client.get('/voice/status')
    assert response.status_code == 200
    payload = response.json()
    assert payload['ok'] is True
    assert 'tts' in payload and 'stt' in payload
    assert payload['tts']['available'] in {True, False}
    assert payload['stt']['available'] in {True, False}
    if payload['stt']['available'] is False:
        assert payload['stt']['reason']


def test_voice_runtime_transcribe_uses_faster_whisper_when_available(tmp_path, monkeypatch):
    audio = tmp_path / 'sample.wav'
    audio.write_bytes(b'RIFFfakeWAVEdata')
    service = VoiceRuntimeService(ROOT)
    monkeypatch.setattr(service, '_stt_backend_status', lambda: {
        'available': True,
        'provider': 'faster_whisper',
        'mode': 'local_file_transcription',
        'model': 'tiny',
    })
    monkeypatch.setattr(service, '_transcribe_with_faster_whisper', lambda source: 'Hallo aus Whisper')
    result = service.transcribe(str(audio))
    assert result['ok'] is True
    assert result['text'] == 'Hallo aus Whisper'
    assert result['stt']['provider'] == 'faster_whisper'


def test_voice_runtime_status_prefers_real_local_stt_backend_when_present():
    service = VoiceRuntimeService(ROOT)
    status = service.status()
    assert status['ok'] is True
    assert status['stt']['provider'] in {'faster_whisper', 'speech_recognition', 'none'}
    if status['stt']['provider'] == 'faster_whisper':
        assert status['stt']['available'] is True
        assert status['stt']['model'] == 'tiny'


def test_python_quic_server_and_client_exchange_message_with_certificate_verification(tmp_path):
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()

    async def run_flow():
        server = EidolonQuicServer(device_id='server-test', device_name='Server Test', host='127.0.0.1', port=port, cert_dir=tmp_path)
        messages = []

        async def on_message(data: bytes):
            messages.append(data)

        server.on_message = on_message
        client = EidolonQuicClient(cert_dir=tmp_path)
        await server.start()
        try:
            connected = await client.connect('127.0.0.1', port)
            assert connected is True
            response = await client.send_message({'type': 'ping', 'text': 'hello quic'})
            assert response is not None
            payload = json.loads(response.decode('utf-8'))
            assert payload['from'] == 'server-test'
            assert payload['echo']['text'] == 'hello quic'
            assert len(messages) == 1
        finally:
            await client.close()
            await server.stop()

    asyncio.run(run_flow())
