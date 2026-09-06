from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.chat_turn_status import PHASE_ANTWORTET, PHASE_DENKT, reset_chat_turn_status, snapshot_chat_turn
from eidolon.web_routes import read_root_html

ROOT = Path(__file__).resolve().parents[1]


class _RenderedIndexHtml:
    def read_text(self, encoding: str = 'utf-8') -> str:
        return read_root_html(ROOT)


INDEX_HTML = _RenderedIndexHtml()
CHAT_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
THREAD_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'chat' / 'chat-thread.css'
MOBILE_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'app-mobile.css'
CHAT_ROUTES = ROOT / 'python' / 'eidolon' / 'chat_message_routes.py'
SESSION_ROUTES = ROOT / 'python' / 'eidolon' / 'chat_session_routes.py'


def test_chat_transcript_is_flat_rows_not_bubbles():
    css = THREAD_CSS.read_text(encoding='utf-8')
    js = CHAT_UI_JS.read_text(encoding='utf-8')
    html = INDEX_HTML.read_text()
    assert '.chat-turn,' in css or '.chat-turn' in css
    assert 'max-width: none' in css
    assert 'background: transparent' in css
    assert '.chat-messages' in css
    assert 'margin-left: auto' not in css
    assert 'border-bottom-right-radius: 2px' not in css
    assert 'border-bottom-left-radius: 2px' not in css
    turn_css = css.split('.chat-turn,')[1].split('.chat-input-shell')[0]
    assert 'border-radius: 0' in turn_css
    assert 'border-radius: 10px' not in turn_css
    assert 'max-width: 72%' not in turn_css
    assert 'function renderChatTurn' in js
    assert "class=\"chat-turn msg '" in js
    assert 'id="chat-agent-status"' in html
    assert 'id="chat-eidolon-presence"' in html
    assert 'chat-composer-chrome' in html
    assert 'id="chat-eidolon-presence-park"' not in html
    assert 'data-presence-host' not in js
    assert 'function mountChatPresenceMark' not in js
    assert 'overflow-y: auto' in css
    assert 'max-height: min(78vh, 800px)' in (ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'chat' / 'chat-session-rail.css').read_text(encoding='utf-8')
    assert 'denkt…' in js
    assert 'arbeitet…' in js
    assert 'antwortet' in js


def test_chat_status_is_honest_and_german():
    js = CHAT_UI_JS.read_text(encoding='utf-8')
    routes = CHAT_ROUTES.read_text(encoding='utf-8')
    sessions = SESSION_ROUTES.read_text(encoding='utf-8')
    html = INDEX_HTML.read_text()
    assert "setChatAgentStatus('denkt', 'local')" in js
    assert "startChatStatusPoll(currentChatSessionId)" in js
    assert "'/chat/turn-status?session_id='" in js
    assert "setChatAgentStatus('antwortet', 'response')" in js
    assert "setChatAgentStatus('arbeitet'" not in js
    assert 'setEidolonTurnPhase(phase)' in js
    assert "PHASE_DENKT, 'build_runtime_context')" in routes or "PHASE_DENKT, 'llm_complete')" in routes
    assert "PHASE_ANTWORTET" in routes
    assert "PHASE_ARBEITET" not in routes
    assert "@app.get('/chat/turn-status')" in sessions
    assert 'aria-live="polite"' in html
    assert 'thinking…' not in js
    assert 'Typing' not in js


def test_mobile_chat_keeps_flat_transcript_with_tighter_density():
    mobile = MOBILE_CSS.read_text(encoding='utf-8')
    assert '.chat-turn,' in mobile
    assert '.msg {' in mobile
    assert 'font-size: 0.88rem' in mobile
    assert 'border-radius: 10px' not in mobile.split('.chat-turn')[1].split('.mobile-device-banner')[0]


def test_chat_turn_status_endpoint_is_idle_until_a_turn_runs():
    reset_chat_turn_status()
    client = TestClient(agent_server.app)
    created = client.post('/chat/sessions', json={'source': 'test-turn-status'})
    assert created.status_code == 200
    session_id = created.json()['session']['session_id']
    try:
        idle = client.get('/chat/turn-status', params={'session_id': session_id})
        assert idle.status_code == 200
        body = idle.json()
        assert body['ok'] is True
        assert body['phase'] == 'idle'
        assert body['label'] == ''
        assert 'denkt' in body['instrumented']
        assert 'arbeitet' in body['instrumented']
        assert 'antwortet' in body['instrumented']
    finally:
        client.delete(f'/chat/sessions/{session_id}')
        reset_chat_turn_status()


def test_chat_post_marks_real_denkt_then_antwortet(monkeypatch):
    reset_chat_turn_status()
    client = TestClient(agent_server.app)
    created = client.post('/chat/sessions', json={'source': 'test-turn-phases'})
    session_id = created.json()['session']['session_id']
    seen = []

    async def fake_complete(system: str, user: str) -> str:
        seen.append(snapshot_chat_turn(session_id)['phase'])
        return 'Verstanden. Ich bin Eidolon und antworte direkt.'

    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)
    try:
        response = client.post('/chat', json={
            'message': 'lass uns ein bisschen plaudern',
            'source': 'test-turn-phases',
            'session_id': session_id,
        })
        assert response.status_code == 200
        body = response.json()
        assert body['ok'] is True
        assert seen == [PHASE_DENKT]
        after = client.get('/chat/turn-status', params={'session_id': session_id}).json()
        assert after['phase'] == PHASE_ANTWORTET
        assert after['label'] == 'antwortet'
        assert after['reason'] in {'finalize_reply', 'runtime_truth_reply', 'settings_apply_reply'}
    finally:
        client.delete(f'/chat/sessions/{session_id}')
        reset_chat_turn_status()


def test_truth_reply_marks_antwortet_without_faking_tools():
    reset_chat_turn_status()
    client = TestClient(agent_server.app)
    original_status = agent_server.llm_backend.status()
    agent_server.llm_backend.configure(
        provider='openai_oauth',
        model='gpt-5.5',
        ollama_url='http://localhost:11434',
    )
    created = client.post('/chat/sessions', json={'source': 'test-truth-phase'})
    session_id = created.json()['session']['session_id']
    try:
        response = client.post('/chat', json={
            'message': 'welches modell bist du',
            'source': 'test-truth-phase',
            'session_id': session_id,
        })
        assert response.status_code == 200
        assert response.json()['ok'] is True
        after = client.get('/chat/turn-status', params={'session_id': session_id}).json()
        assert after['phase'] == PHASE_ANTWORTET
        assert after['reason'] == 'runtime_truth_reply'
        assert after['label'] == 'antwortet'
    finally:
        client.delete(f'/chat/sessions/{session_id}')
        agent_server.llm_backend.configure(
            provider=original_status['provider'],
            model=original_status['model'],
            ollama_url=original_status['ollama_url'],
        )
        reset_chat_turn_status()
