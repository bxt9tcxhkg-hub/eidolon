from pathlib import Path
import json
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
import eidolon.core.llm_fallback as llm_fallback
from eidolon.chat_stream import parse_sse_events
from eidolon.chat_turn_status import PHASE_ANTWORTET, PHASE_DENKT, reset_chat_turn_status, snapshot_chat_turn
from eidolon.core.llm_backend import LLMBackend
from eidolon.core.llm_config_store import load_llm_config, save_llm_config, save_openai_api_key
from eidolon.core.llm_fallback import iter_stream_or_complete, provider_can_stream
from eidolon.core.llm_openai_compat import parse_openai_sse_delta, stream_openai_compat


ROOT = Path(__file__).resolve().parents[1]
CHAT_UI = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
CHAT_ROUTES = ROOT / 'python' / 'eidolon' / 'chat_message_routes.py'
SECRET = 'sk-secret-test-key-1234567890'


def _new_session(client: TestClient, source: str) -> str:
    created = client.post('/chat/sessions', json={'source': source})
    assert created.status_code == 200
    return created.json()['session']['session_id']


def _cleanup(client: TestClient, session_id: str) -> None:
    client.delete(f'/chat/sessions/{session_id}')
    reset_chat_turn_status()


def _event_types(events):
    return [event.get('type') for event in events]


def test_openai_sse_delta_parser_is_honest():
    assert parse_openai_sse_delta('') == ''
    assert parse_openai_sse_delta('event: message') == ''
    assert parse_openai_sse_delta('data: [DONE]') is None
    assert parse_openai_sse_delta('data: {"choices":[{"delta":{"role":"assistant"}}]}') == ''
    assert parse_openai_sse_delta('data: {"choices":[{"delta":{"content":"Hal"}}]}') == 'Hal'
    assert parse_openai_sse_delta('data: not-json') == ''


def test_openai_compat_stream_sends_stream_true_and_yields_provider_deltas(monkeypatch):
    seen = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def __iter__(self):
            return iter([
                b'data: {"choices":[{"delta":{"content":"Hal"}}]}\n',
                b'data: {"choices":[{"delta":{"content":"lo"}}]}\n',
                b'data: [DONE]\n',
            ])

    def fake_urlopen(request, timeout=90):
        seen['url'] = request.full_url
        seen['payload'] = json.loads(request.data.decode('utf-8'))
        return FakeResponse()

    monkeypatch.setattr('eidolon.core.llm_openai_compat.urllib.request.urlopen', fake_urlopen)
    original_cfg = load_llm_config()
    save_openai_api_key(SECRET)
    backend = LLMBackend()
    try:
        backend.configure(
            provider='openai',
            preset='groq',
            base_url='https://api.groq.com/openai/v1',
            model='llama-3.1-8b-instant',
            fallback_chain=['openai'],
        )
        chunks = list(stream_openai_compat(backend, system='sys', user='hi'))
        assert chunks == ['Hal', 'lo']
        assert seen['url'] == 'https://api.groq.com/openai/v1/chat/completions'
        assert seen['payload']['stream'] is True
        assert seen['payload']['model'] == 'llama-3.1-8b-instant'
        assert 'stream' not in json.dumps(seen['payload']['messages'])
    finally:
        save_openai_api_key('')
        save_llm_config(original_cfg)


def test_iter_stream_or_complete_falls_back_without_inventing_deltas(monkeypatch):
    def boom(backend, *, system, user):
        raise RuntimeError('stream down')

    def ok(backend, *, system, user):
        return 'volle Antwort'

    monkeypatch.setattr(llm_fallback, 'stream_openai_compat', boom)
    monkeypatch.setattr(llm_fallback, 'complete_openai_compat', boom)
    monkeypatch.setattr(llm_fallback, 'complete_ollama', ok)
    original_cfg = load_llm_config()
    backend = LLMBackend()
    try:
        backend.configure(provider='openai', fallback_chain=['openai', 'ollama'])
        items = list(iter_stream_or_complete(backend, system='sys', user='hi'))
        assert [item['kind'] for item in items] == ['complete']
        assert items[0]['text'] == 'volle Antwort'
        assert items[0]['streamed'] is False
        assert items[0]['used_provider'] == 'ollama'
        assert provider_can_stream('openai') is True
        assert provider_can_stream('ollama') is False
        assert provider_can_stream('openai_oauth') is False
    finally:
        save_llm_config(original_cfg)


def test_chat_stream_emits_real_deltas_and_marks_antwortet(monkeypatch):
    reset_chat_turn_status()
    client = TestClient(agent_server.app)
    session_id = _new_session(client, 'test-chat-stream-deltas')
    seen = []

    def fake_iter_reply(system, user, *, prefer_stream=False):
        assert prefer_stream is True
        seen.append(snapshot_chat_turn(session_id)['phase'])
        yield {'kind': 'delta', 'text': 'Hal'}
        seen.append(snapshot_chat_turn(session_id)['phase'])
        yield {'kind': 'delta', 'text': 'lo'}
        yield {'kind': 'meta', 'streamed': True, 'used_provider': 'openai'}

    monkeypatch.setattr(agent_server.llm_backend, 'iter_reply', fake_iter_reply)
    try:
        response = client.post('/chat', json={
            'message': 'lass uns ein bisschen plaudern',
            'source': 'test-chat-stream-deltas',
            'session_id': session_id,
            'stream': True,
        })
        assert response.status_code == 200
        assert 'text/event-stream' in response.headers['content-type']
        events = parse_sse_events(response.text)
        types = _event_types(events)
        assert types[0] == 'start'
        assert 'delta' in types
        assert types[-1] == 'done'
        deltas = [event['text'] for event in events if event.get('type') == 'delta']
        assert deltas == ['Hal', 'lo']
        done = events[-1]
        assert done['ok'] is True
        assert done['streamed'] is True
        assert done['response'] == 'Hallo'
        assert done['session_id'] == session_id
        assert seen[0] == PHASE_DENKT
        after = client.get('/chat/turn-status', params={'session_id': session_id}).json()
        assert after['phase'] == PHASE_ANTWORTET
        assert after['reason'] == 'finalize_reply'
        stored = client.get(f'/chat/sessions/{session_id}').json()['session']
        assert stored['messages'][-1]['content'] == 'Hallo'
    finally:
        _cleanup(client, session_id)


def test_chat_stream_nonstreamable_path_is_one_done_without_deltas(monkeypatch):
    reset_chat_turn_status()
    client = TestClient(agent_server.app)
    session_id = _new_session(client, 'test-chat-stream-fallback')

    def fake_iter_reply(system, user, *, prefer_stream=False):
        yield {'kind': 'complete', 'text': 'Ganze Antwort auf einmal', 'streamed': False, 'used_provider': 'ollama'}

    monkeypatch.setattr(agent_server.llm_backend, 'iter_reply', fake_iter_reply)
    try:
        response = client.post('/chat', json={
            'message': 'lass uns ein bisschen plaudern',
            'source': 'test-chat-stream-fallback',
            'session_id': session_id,
            'stream': True,
        })
        assert response.status_code == 200
        assert 'text/event-stream' in response.headers['content-type']
        events = parse_sse_events(response.text)
        assert [event.get('type') for event in events if event.get('type') == 'delta'] == []
        done = events[-1]
        assert done['type'] == 'done'
        assert done['streamed'] is False
        assert done['response'] == 'Ganze Antwort auf einmal'
        after = client.get('/chat/turn-status', params={'session_id': session_id}).json()
        assert after['phase'] == PHASE_ANTWORTET
        assert after['reason'] == 'finalize_reply'
    finally:
        _cleanup(client, session_id)


def test_chat_stream_truth_and_skill_do_not_fake_tokens():
    reset_chat_turn_status()
    client = TestClient(agent_server.app)
    original_status = agent_server.llm_backend.status()
    agent_server.llm_backend.configure(provider='openai_oauth', model='gpt-5.5', ollama_url='http://localhost:11434')
    truth_id = _new_session(client, 'test-chat-stream-truth')
    skill_id = _new_session(client, 'test-chat-stream-skill')
    try:
        truth = client.post('/chat', json={
            'message': 'welches modell bist du',
            'source': 'test-chat-stream-truth',
            'session_id': truth_id,
            'stream': True,
        })
        truth_events = parse_sse_events(truth.text)
        assert [event.get('type') for event in truth_events if event.get('type') == 'delta'] == []
        truth_done = truth_events[-1]
        assert truth_done['streamed'] is False
        assert 'gpt-5.5' in truth_done['response']

        skill = client.post('/chat', json={
            'message': 'fass meinen kalender zusammen',
            'source': 'test-chat-stream-skill',
            'session_id': skill_id,
            'stream': True,
        })
        skill_events = parse_sse_events(skill.text)
        assert [event.get('type') for event in skill_events if event.get('type') == 'delta'] == []
        skill_done = skill_events[-1]
        assert skill_done['streamed'] is False
        assert skill_done['skill']['executed'] is False
        assert 'nicht als Runtime verdrahtet' in skill_done['response']
    finally:
        _cleanup(client, truth_id)
        _cleanup(client, skill_id)
        agent_server.llm_backend.configure(
            provider=original_status['provider'],
            model=original_status['model'],
            ollama_url=original_status['ollama_url'],
        )


def test_chat_json_fallback_stays_available(monkeypatch):
    reset_chat_turn_status()
    client = TestClient(agent_server.app)
    session_id = _new_session(client, 'test-chat-json-fallback')

    async def fake_complete(system: str, user: str) -> str:
        return 'JSON bleibt der Nicht-Stream-Pfad.'

    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)
    try:
        response = client.post('/chat', json={
            'message': 'lass uns ein bisschen plaudern',
            'source': 'test-chat-json-fallback',
            'session_id': session_id,
        })
        assert response.status_code == 200
        assert 'text/event-stream' not in (response.headers.get('content-type') or '')
        body = response.json()
        assert body['ok'] is True
        assert body['response'] == 'JSON bleibt der Nicht-Stream-Pfad.'
    finally:
        _cleanup(client, session_id)


def test_chat_ui_consumes_sse_without_fake_typewriter():
    js = CHAT_UI.read_text(encoding='utf-8')
    routes = CHAT_ROUTES.read_text(encoding='utf-8')
    assert "stream: true" in js
    assert "'Accept': 'text/event-stream'" in js
    assert 'async function consumeChatStream' in js
    assert "event.type === 'delta'" in js
    assert 'function updateStreamingAssistant' in js
    assert 'function applyFinishedChatReply' in js
    assert 'llm_sse_response' in routes
    assert 'want_stream' in routes
    send = js.split('async function sendChat')[1].split('function renderChatTurn')[0]
    consume = js.split('async function consumeChatStream')[1].split('async function sendChat')[0]
    for blob in (send, consume):
        assert 'typewriter' not in blob.lower()
        assert 'charAt(' not in blob
        assert 'setInterval(' not in blob
        lowered = blob.lower()
        assert 'fake stream' not in lowered
        assert 'for (let i = 0; i <' not in blob
