from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.operate.service import OperateService
from eidolon.workspaces.project_service import ProjectService
from eidolon.workspaces.vorhaben_extract import extract_planning_cards, extract_vorhaben, looks_like_vorhaben
from eidolon.workspaces.workspace_ui_service import WorkspaceUIService
from eidolon.web_routes import read_root_html

ROOT = Path(__file__).resolve().parents[1]
FAMILIEN = (
    'Familienwochenende: Anreise mit Laden, Unterkunft mit eigenem Bad, '
    'Dauer klären und Packen vorbereiten.'
)


def _isolated(tmp_path, monkeypatch):
    ui = WorkspaceUIService(tmp_path)
    ui._project_service = ProjectService(tmp_path)
    ui._operate_service = OperateService(tmp_path)
    monkeypatch.setattr(agent_server, 'workspace_ui_service', ui, raising=False)
    monkeypatch.setattr(agent_server, 'project_service', ui._project_service, raising=False)
    monkeypatch.setattr(agent_server, 'operate_service', ui._operate_service, raising=False)
    return ui


def test_vorhaben_extract_is_generic_not_a_travel_pack():
    assert looks_like_vorhaben(FAMILIEN) is True
    assert looks_like_vorhaben('Wie geht es dir heute?') is False
    extracted = extract_vorhaben(FAMILIEN)
    assert extracted is not None
    assert extracted['title'] == 'Familienwochenende'
    titles = [card['title'] for card in extracted['cards']]
    assert any('Anreise' in title and 'Laden' in title for title in titles)
    assert any('Unterkunft' in title and 'Bad' in title for title in titles)
    assert any('Dauer' in title or 'Termin' in title for title in titles)
    assert any('Packen' in title or 'Vorbereitung' in title for title in titles)
    assert extracted['approval']['action_type'] == 'external_write'
    assert extracted['approval']['title'] == 'Buchung vorschlagen'

    software = extract_planning_cards('Login-Flow mit Tests und Fehlerbehandlung bauen', title='Login-Flow')
    software_titles = ' '.join(card['title'] for card in software)
    assert 'Anreise' not in software_titles
    assert 'Unterkunft' not in software_titles
    assert any(card['slot'] == 'goal' for card in software)


def test_chat_surfaces_candidate_when_llm_fails(tmp_path, monkeypatch):
    ui = _isolated(tmp_path, monkeypatch)

    async def boom(*_args, **_kwargs):
        raise RuntimeError('connection refused: ollama down')

    monkeypatch.setattr(agent_server.llm_backend, 'complete', boom)
    client = TestClient(agent_server.app)
    response = client.post('/chat', json={'message': FAMILIEN, 'source': 'chat'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['ok'] is False
    assert payload.get('error_code') == 'backend_failure'
    formation = (payload.get('runtime_context') or {}).get('formation') or {}
    assert formation.get('visible') is True
    assert formation.get('current_state') == 'project_candidate'
    assert formation.get('to_state') == 'active_project'
    assert formation.get('requires_confirmation') is True
    assert formation.get('workspace_id')
    assert 'Familienwochenende' in (formation.get('label') or '')
    assert formation.get('action_label') == 'Ja, übernehmen'
    session_id = payload.get('session_id')
    if session_id:
        agent_server.chat_session_store.delete_session(session_id)
    assert any(item.get('product_state') == 'project_candidate' for item in ui.get_runtime_payload().get('workspaces') or [])


def test_confirm_seeds_board_and_real_approval(tmp_path, monkeypatch):
    ui = _isolated(tmp_path, monkeypatch)

    async def boom(*_args, **_kwargs):
        raise RuntimeError('connection refused: ollama down')

    monkeypatch.setattr(agent_server.llm_backend, 'complete', boom)
    client = TestClient(agent_server.app)
    chat = client.post('/chat', json={'message': FAMILIEN, 'source': 'chat'})
    formation = chat.json()['runtime_context']['formation']
    denied = client.post('/workspaces/formation', json={
        'workspace_id': formation['workspace_id'],
        'to_state': 'active_project',
        'confirmed': False,
    })
    assert denied.status_code == 400

    accepted = client.post('/workspaces/formation', json={
        'workspace_id': formation['workspace_id'],
        'to_state': 'active_project',
        'confirmed': True,
        'seed_board': True,
        'reason': 'user_confirmed_promotion',
    })
    assert accepted.status_code == 200
    body = accepted.json()
    assert body['ok'] is True
    assert body['to_state'] == 'active_project'
    project = body['project']
    assert project['title'] == 'Familienwochenende'
    titles = [item['title'] for item in project['elements']]
    assert titles, 'empty board after confirm is a failure'
    assert any('Anreise' in title for title in titles)
    assert any('Unterkunft' in title for title in titles)
    assert len(project['elements']) >= 3
    assert all(item.get('element_type') == 'task' for item in project['elements'])
    assert not any(item.get('domain') == 'travel' for item in project['elements'])
    approval = body.get('approval')
    assert approval is not None
    assert approval['status'] == 'pending'
    assert approval['action_type'] == 'external_write'
    assert approval['title'] == 'Buchung vorschlagen'

    overview = client.get('/api/v1/operate/overview').json()
    data = overview['data']
    pending = [item for item in (data.get('approvals') or []) if item.get('status') == 'pending']
    assert pending
    assert (data.get('next_action') or {}).get('kind') == 'approval_request'
    run_id = (data.get('run') or {}).get('id')
    assert run_id
    resolved = client.post(f'/api/v1/runs/{run_id}/approval/{pending[0]["id"]}', json={'decision': 'approved', 'resolved_by': 'user'})
    assert resolved.status_code == 200
    assert resolved.json()['data']['approval']['status'] == 'approved'
    session_id = chat.json().get('session_id')
    if session_id:
        agent_server.chat_session_store.delete_session(session_id)


def test_formation_and_approval_door_ui_contracts():
    html = read_root_html(ROOT)
    chat_js = (ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js').read_text(encoding='utf-8')
    operate_js = (ROOT / 'python' / 'eidolon' / 'web' / 'operate-render-ui.js').read_text(encoding='utf-8')
    assert 'id="chat-formation"' in html
    assert 'chat-formation-card' in chat_js
    assert 'Daraus ein Projekt machen?' in chat_js
    assert 'Ja, übernehmen' in chat_js
    assert 'Nein, nur im Chat' in chat_js
    assert 'seed_board' in chat_js
    assert "nextAction.kind === 'next_step' && nextAction.action_enabled && !approvals.length" in chat_js
    assert '>Freigeben</button>' in operate_js
    assert '>Ablehnen</button>' in operate_js
    assert "nextAction.kind === 'next_step' && nextAction.action_enabled && !pending.length" in operate_js
