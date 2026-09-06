from pathlib import Path
import json
import platform
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.chat_turn_status import PHASE_ANTWORTET, PHASE_ARBEITET, PHASE_DENKT, reset_chat_turn_status, snapshot_chat_turn
from eidolon.core.config import state_path
from eidolon.runtime_builtin_skills import BUILTIN_SKILLS
from eidolon.skills.chat_skill_turn import match_chat_skill
from eidolon.skills.live_skills import execute_live_skill


ROOT = Path(__file__).resolve().parents[1]
CHAT_UI = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
SKILLS_UI = ROOT / 'python' / 'eidolon' / 'web' / 'skills-backups-ui.js'


def _new_session(client: TestClient, source: str) -> str:
    created = client.post('/chat/sessions', json={'source': source})
    assert created.status_code == 200
    return created.json()['session']['session_id']


def _cleanup(client: TestClient, session_id: str) -> None:
    client.delete(f'/chat/sessions/{session_id}')
    reset_chat_turn_status()


def test_matcher_is_conservative_and_does_not_steal_casual_chat():
    assert match_chat_skill('lass uns ein bisschen plaudern') is None
    assert match_chat_skill('info über das projekt') is None
    assert match_chat_skill('was ist das ziel') is None
    assert match_chat_skill('welches modell bist du') is None
    assert match_chat_skill(
        'Familienwochenende: Anreise mit Laden, Unterkunft mit eigenem Bad, Dauer klären und Packen vorbereiten.'
    ) is None
    assert match_chat_skill(
        'Familienwochenende mit Tesla, 2 Nächte, Unterkunft mit eigenem Bad, CF.'
    ) is None
    live = match_chat_skill('zeig systeminfo')
    assert live is not None and live.name == 'system_info' and live.wired is True
    note = match_chat_skill('Notiz: Milch kaufen')
    assert note is not None and note.name == 'note' and note.payload.get('action') == 'add'
    unwired = match_chat_skill('fass meinen kalender zusammen')
    assert unwired is not None and unwired.name == 'calendar' and unwired.wired is False


def test_chat_system_info_skill_returns_real_host_data():
    reset_chat_turn_status()
    client = TestClient(agent_server.app)
    session_id = _new_session(client, 'test-skill-system-info')
    seen = []

    real_execute = execute_live_skill

    def probe(name, payload=None):
        seen.append(snapshot_chat_turn(session_id)['phase'])
        return real_execute(name, payload)

    import eidolon.skills.chat_skill_turn as turn
    original = turn.execute_live_skill
    turn.execute_live_skill = probe
    try:
        response = client.post('/chat', json={
            'message': 'zeig systeminfo',
            'source': 'test-skill-system-info',
            'session_id': session_id,
        })
        assert response.status_code == 200
        body = response.json()
        assert body['ok'] is True
        assert body['skill']['name'] == 'system_info'
        assert body['skill']['wired'] is True
        assert body['skill']['executed'] is True
        assert platform.system() in body['response']
        assert platform.node() in body['response']
        assert 'System-Info (echt vom Host)' in body['response']
        assert seen == [PHASE_ARBEITET]
        after = client.get('/chat/turn-status', params={'session_id': session_id}).json()
        assert after['phase'] == PHASE_ANTWORTET
        assert after['reason'] == 'skill_reply'
    finally:
        turn.execute_live_skill = original
        _cleanup(client, session_id)


def test_chat_note_skill_persists_real_note():
    reset_chat_turn_status()
    token = 'vertrag-notiz-skill-turn-4791'
    client = TestClient(agent_server.app)
    session_id = _new_session(client, 'test-skill-note')
    try:
        response = client.post('/chat', json={
            'message': f'Notiz: {token}',
            'source': 'test-skill-note',
            'session_id': session_id,
        })
        assert response.status_code == 200
        body = response.json()
        assert body['ok'] is True
        assert body['skill']['name'] == 'note'
        assert body['skill']['executed'] is True
        assert token in body['response']
        assert 'gespeichert' in body['response'].casefold()
        notes_path = state_path('persistence', 'notes.json')
        stored = json.loads(notes_path.read_text(encoding='utf-8'))
        assert any(isinstance(item, dict) and token in str(item.get('note') or '') for item in stored)
    finally:
        _cleanup(client, session_id)


def test_chat_unwired_calendar_skill_is_honest_and_does_not_claim_success():
    reset_chat_turn_status()
    client = TestClient(agent_server.app)
    session_id = _new_session(client, 'test-skill-unwired')
    called = {'llm': False}

    async def fake_complete(system: str, user: str) -> str:
        called['llm'] = True
        return 'sollte nicht laufen'

    original = agent_server.llm_backend.complete
    agent_server.llm_backend.complete = fake_complete
    try:
        response = client.post('/chat', json={
            'message': 'fass meinen kalender zusammen',
            'source': 'test-skill-unwired',
            'session_id': session_id,
        })
        assert response.status_code == 200
        body = response.json()
        assert body['ok'] is True
        assert body['skill']['name'] == 'calendar'
        assert body['skill']['wired'] is False
        assert body['skill']['executed'] is False
        assert 'nicht als Runtime verdrahtet' in body['response']
        assert 'Kalender-Skill' not in body['response']
        assert 'erfinde keine Termine' in body['response']
        assert called['llm'] is False
        after = client.get('/chat/turn-status', params={'session_id': session_id}).json()
        assert after['phase'] == PHASE_ANTWORTET
        assert after['reason'] == 'skill_unwired'
        assert after['reason'] != 'skill_reply'
    finally:
        agent_server.llm_backend.complete = original
        _cleanup(client, session_id)


def test_casual_chat_still_uses_llm_and_does_not_set_arbeitet(monkeypatch):
    reset_chat_turn_status()
    client = TestClient(agent_server.app)
    session_id = _new_session(client, 'test-skill-casual')
    seen = []

    async def fake_complete(system: str, user: str) -> str:
        seen.append(snapshot_chat_turn(session_id)['phase'])
        return 'Verstanden. Ich bin Eidolon und antworte direkt.'

    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)
    try:
        response = client.post('/chat', json={
            'message': 'lass uns ein bisschen plaudern',
            'source': 'test-skill-casual',
            'session_id': session_id,
        })
        assert response.status_code == 200
        body = response.json()
        assert body.get('skill') is None
        assert seen == [PHASE_DENKT]
        after = client.get('/chat/turn-status', params={'session_id': session_id}).json()
        assert after['phase'] == PHASE_ANTWORTET
        assert after['reason'] in {'finalize_reply', 'runtime_truth_reply', 'settings_apply_reply'}
    finally:
        _cleanup(client, session_id)


def test_skills_api_marks_live_vs_catalog():
    client = TestClient(agent_server.app)
    listed = client.get('/skills').json()
    assert listed['ok'] is True
    assert listed['catalog_only'] is False
    assert listed['runtime_wired'] is True
    by_name = {skill['name']: skill for skill in listed['skills']}
    for live in ('note', 'system_info', 'device_status'):
        assert by_name[live]['executable'] is True
        assert by_name[live]['runtime_wired'] is True
    for catalog in ('chat', 'calendar', 'file_organizer', 'mesh_send', 'goal_manager'):
        assert by_name[catalog]['executable'] is False
        assert by_name[catalog]['runtime_wired'] is False
    assert 'nicht verdrahtet' in listed['detail']
    assert 'note' in listed['detail']


def test_unwired_skill_has_no_success_toast_path():
    skills_ui = SKILLS_UI.read_text(encoding='utf-8')
    chat_ui = CHAT_UI.read_text(encoding='utf-8')
    load_fn = skills_ui.split('async function loadSkills')[1].split('// Backups')[0]
    assert 'showNotice' not in load_fn
    assert "showNotice(" not in load_fn
    assert "s.enabled ? 'ok'" not in skills_ui
    assert 'ausführbar im Chat' in skills_ui
    assert 'Katalog · nicht verdrahtet' in skills_ui
    send = chat_ui.split('async function sendChat')[1].split('function renderChatTurn')[0]
    assert "showNotice(" not in send
    assert "'success'" not in send


def test_disabled_live_skill_does_not_execute():
    reset_chat_turn_status()
    client = TestClient(agent_server.app)
    session_id = _new_session(client, 'test-skill-disabled')
    original = next(skill for skill in BUILTIN_SKILLS if skill['name'] == 'note')['enabled']
    try:
        disabled = client.post('/skills/note/disable').json()
        assert disabled['ok'] is True
        assert disabled['enabled'] is False
        assert disabled['runtime_wired'] is True
        response = client.post('/chat', json={
            'message': 'Notiz: sollte nicht geschrieben werden',
            'source': 'test-skill-disabled',
            'session_id': session_id,
        })
        body = response.json()
        assert body['skill']['executed'] is False
        assert body['skill']['disabled'] is True
        assert 'ausgeschaltet' in body['response']
    finally:
        if original:
            client.post('/skills/note/enable')
        else:
            client.post('/skills/note/disable')
        _cleanup(client, session_id)
