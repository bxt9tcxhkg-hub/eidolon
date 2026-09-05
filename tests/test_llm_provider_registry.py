from pathlib import Path
import asyncio
import json
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))

import eidolon.core.llm_fallback as llm_fallback
from eidolon.core.llm_backend import LLMBackend
from eidolon.core.llm_config_store import load_llm_config, save_llm_config, save_openai_api_key
from eidolon.core.llm_openai_compat import USER_AGENT, openai_compat_headers
from eidolon.core.llm_provider_catalog import build_fallback_chain, normalize_llm_settings
from eidolon.core.llm_secrets import contains_secret, mask_secret
from eidolon.core.runtime_problems import healing_visible_problems
import agent_server


SECRET = 'sk-secret-test-key-1234567890'


def test_catalog_oauth_is_only_on_codex_provider():
    client = TestClient(agent_server.app)
    catalog = client.get('/llm/providers').json()
    by_id = {item['id']: item for item in catalog['providers']}
    assert by_id['openai']['oauth_supported'] is False
    assert by_id['openai']['auth_methods'] == ['api_key']
    assert by_id['openai_oauth']['oauth_supported'] is True
    assert by_id['openai_oauth']['auth_methods'] == ['chatgpt_login']
    assert by_id['ollama']['oauth_supported'] is False
    assert {item['id'] for item in catalog['presets']} >= {'groq', 'openrouter', 'mistral', 'gemini', 'local', 'openai', 'custom'}


def test_settings_accept_openai_compat_fields_and_normalize_auth():
    client = TestClient(agent_server.app)
    original = agent_server.settings_store.get_area('llm')
    try:
        response = client.post('/settings/llm', json={
            'provider': 'openai',
            'preset': 'groq',
            'base_url': 'https://api.groq.com/openai/v1',
            'model': 'llama-3.1-8b-instant',
            'auth_method': 'chatgpt_login',
            'fallback_chain': ['openai', 'ollama'],
        })
        assert response.status_code == 200
        payload = response.json()
        assert payload['ok'] is True
        stored = agent_server.settings_store.get_area('llm')
        assert stored['provider'] == 'openai'
        assert stored['preset'] == 'groq'
        assert stored['base_url'] == 'https://api.groq.com/openai/v1'
        assert stored['auth_method'] == 'api_key'
        assert stored['fallback_chain'] == ['openai', 'ollama']
        assert agent_server.llm_backend.status()['provider'] == 'openai'
        assert agent_server.llm_backend.status()['auth_method'] == 'api_key'
        assert agent_server.llm_backend.status()['connection']['oauth_supported'] is False
    finally:
        agent_server.settings_store.set_area('llm', original)
        agent_server.llm_backend.configure(**{key: original[key] for key in original if key in {
            'provider', 'model', 'ollama_url', 'base_url', 'preset', 'auth_method', 'fallback_chain', 'temperature', 'max_tokens'
        }})


def test_settings_reject_invalid_base_url():
    client = TestClient(agent_server.app)
    original = agent_server.settings_store.get_area('llm')
    try:
        response = client.post('/settings/llm', json={'base_url': 'not-a-url'})
        assert response.status_code == 200
        payload = response.json()
        assert payload['ok'] is False
        assert 'base_url' in payload['error']
        assert agent_server.settings_store.get_area('llm')['base_url'] == original.get('base_url', '')
    finally:
        agent_server.settings_store.set_area('llm', original)


def test_connection_and_settings_never_return_api_key():
    client = TestClient(agent_server.app)
    previous = None
    try:
        stored = client.post('/llm/openai/api-key', json={'api_key': SECRET})
        assert stored.status_code == 200
        stored_payload = stored.json()
        assert stored_payload['ok'] is True
        assert stored_payload['key_present'] is True
        assert stored_payload['key_masked'] == mask_secret(SECRET)
        assert SECRET not in json.dumps(stored_payload)

        connection = client.get('/llm/connection')
        settings = client.get('/settings')
        models = client.get('/llm/models')
        providers = client.get('/llm/providers')
        for response in (connection, settings, models, providers, stored):
            blob = response.text
            assert SECRET not in blob
            assert contains_secret(blob, SECRET) is False
        connection_payload = connection.json()
        assert connection_payload['key_present'] is True
        assert connection_payload['key_masked']
        assert 'api_key' not in connection_payload
        assert connection_payload['connection']['auth_method'] in {'api_key', 'none', 'chatgpt_login'}
    finally:
        client.post('/llm/openai/api-key', json={'api_key': ''})
        save_openai_api_key(previous or '')


def test_openai_compat_complete_uses_base_url_key_and_model(monkeypatch):
    seen = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({'choices': [{'message': {'content': 'GROQ_OK'}}]}).encode('utf-8')

    def fake_urlopen(request, timeout=90):
        seen['url'] = request.full_url
        seen['auth'] = request.get_header('Authorization')
        seen['user_agent'] = request.get_header('User-agent')
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
        text = asyncio.run(backend.complete('Du bist Eidolon.', 'Sag OK'))
        assert text == 'GROQ_OK'
        assert seen['url'] == 'https://api.groq.com/openai/v1/chat/completions'
        assert seen['auth'] == f'Bearer {SECRET}'
        assert seen['user_agent'] == USER_AGENT
        assert seen['payload']['model'] == 'llama-3.1-8b-instant'
    finally:
        save_openai_api_key('')
        save_llm_config(original_cfg)


def test_openai_compat_headers_include_product_user_agent():
    headers = openai_compat_headers(SECRET)
    assert headers['User-Agent'] == USER_AGENT
    assert headers['User-Agent'].startswith('Eidolon/')
    assert 'github.com/bxt9tcxhkg-hub/eidolon' in headers['User-Agent']
    assert headers['Authorization'] == f'Bearer {SECRET}'
    assert headers['Content-Type'] == 'application/json'


def test_fallback_chain_uses_secondary_when_primary_fails(monkeypatch):
    calls = []

    def boom(backend, *, system, user):
        calls.append('openai')
        raise RuntimeError(f'primary down bearer {SECRET}')

    def ok(backend, *, system, user):
        calls.append('ollama')
        return 'from-ollama'

    monkeypatch.setattr(llm_fallback, 'complete_openai_compat', boom)
    monkeypatch.setattr(llm_fallback, 'complete_ollama', ok)
    original_cfg = load_llm_config()
    backend = LLMBackend()
    try:
        backend.configure(provider='openai', model='llama-3.1-8b-instant', fallback_chain=['openai', 'ollama'])
        text, meta = llm_fallback.complete_with_fallback(backend, system='sys', user='hi')
        assert text == 'from-ollama'
        assert calls == ['openai', 'ollama']
        assert meta['used_provider'] == 'ollama'
        assert meta['fallback_used'] is True
        assert build_fallback_chain('openai', ['openai', 'ollama']) == ['openai', 'ollama']
    finally:
        save_llm_config(original_cfg)


def test_fallback_errors_do_not_leak_secrets(monkeypatch):
    def boom(backend, *, system, user):
        raise RuntimeError(f'Authorization: Bearer {SECRET}')

    monkeypatch.setattr(llm_fallback, 'complete_openai_compat', boom)
    monkeypatch.setattr(llm_fallback, 'complete_ollama', boom)
    original_cfg = load_llm_config()
    backend = LLMBackend()
    try:
        backend.configure(provider='openai', fallback_chain=['openai', 'ollama'])
        llm_fallback.complete_with_fallback(backend, system='sys', user='hi')
    except RuntimeError as exc:
        assert SECRET not in str(exc)
        assert 'Bearer ***' in str(exc) or '***' in str(exc)
    else:
        raise AssertionError('expected fallback failure')
    finally:
        save_llm_config(original_cfg)


def test_normalize_rejects_fake_oauth_on_key_provider():
    normalized, changed = normalize_llm_settings({
        'provider': 'openai',
        'auth_method': 'chatgpt_login',
        'preset': 'groq',
        'base_url': '',
    })
    assert normalized['auth_method'] == 'api_key'
    assert 'auth_method' in changed
    assert normalized['base_url'] == 'https://api.groq.com/openai/v1'


def test_settings_apply_requires_explicit_user_request_and_never_returns_secrets():
    client = TestClient(agent_server.app)
    original = agent_server.settings_store.get_area('llm')
    try:
        denied = client.post('/settings/apply', json={
            'user_requested': False,
            'area': 'llm',
            'values': {'fallback_chain': ['openai', 'ollama']},
        }).json()
        assert denied['ok'] is False
        assert denied['applied'] is False
        assert 'ausdrücklichen Wunsch' in denied['error']

        secret_try = client.post('/settings/apply', json={
            'user_requested': True,
            'area': 'llm',
            'values': {'api_key': SECRET, 'fallback_chain': ['openai', 'ollama']},
        }).json()
        assert SECRET not in json.dumps(secret_try)

        applied = client.post('/settings/apply', json={
            'user_requested': True,
            'area': 'llm',
            'values': {'fallback_chain': ['openai', 'ollama'], 'provider': 'openai'},
            'reason': 'Testauftrag',
        }).json()
        assert applied['ok'] is True
        assert applied['applied'] is True
        assert applied['settings']['fallback_chain'] == ['openai', 'ollama']
        assert 'api_key' not in applied.get('settings', {})
        assert SECRET not in json.dumps(applied)
        assert agent_server.llm_backend.status()['fallback_chain'] == ['openai', 'ollama']
    finally:
        agent_server.settings_store.set_area('llm', original)
        agent_server.llm_backend.configure(**{key: original[key] for key in original if key in {
            'provider', 'model', 'ollama_url', 'base_url', 'preset', 'auth_method', 'fallback_chain', 'temperature', 'max_tokens'
        }})


def test_chat_applies_fallback_chain_only_on_explicit_request():
    client = TestClient(agent_server.app)
    original = agent_server.settings_store.get_area('llm')
    try:
        question = client.post('/chat', json={'message': 'Was wäre eine gute Ersatzkette?', 'source': 'test-settings-question'})
        assert question.status_code == 200
        assert agent_server.settings_store.get_area('llm')['fallback_chain'] == original['fallback_chain']
        assert question.json().get('settings_apply') is None

        applied = client.post('/chat', json={'message': 'Setze die Ersatzkette auf openai, dann ollama.', 'source': 'test-settings-apply'})
        assert applied.status_code == 200
        body = applied.json()
        assert body['settings_apply']['applied'] is True
        assert body['settings_apply']['updated'] == ['fallback_chain']
        assert 'openai' in body['response'] and 'ollama' in body['response']
        assert agent_server.settings_store.get_area('llm')['preset'] == original['preset']
        assert SECRET not in body['response']
        assert agent_server.settings_store.get_area('llm')['fallback_chain'] == ['openai', 'ollama']
        client.delete(f"/chat/sessions/{body['session_id']}")
        if question.json().get('session_id'):
            client.delete(f"/chat/sessions/{question.json()['session_id']}")
    finally:
        agent_server.settings_store.set_area('llm', original)
        agent_server.llm_backend.configure(**{key: original[key] for key in original if key in {
            'provider', 'model', 'ollama_url', 'base_url', 'preset', 'auth_method', 'fallback_chain', 'temperature', 'max_tokens'
        }})


def test_chat_rejects_secret_and_invalid_fallback_from_intent():
    client = TestClient(agent_server.app)
    original = agent_server.settings_store.get_area('llm')
    try:
        secret = client.post('/chat', json={'message': 'Setze den API-Key auf sk-secret-test-key-1234567890', 'source': 'test-settings-secret'}).json()
        assert secret['settings_apply']['applied'] is False
        assert 'Schlüssel' in secret['response']
        assert SECRET not in secret['response']

        invalid = client.post('/chat', json={'message': 'Setze die Ersatzkette auf foo, dann bar', 'source': 'test-settings-invalid'}).json()
        assert invalid['settings_apply']['applied'] is False
        assert 'leer oder ungültig' in invalid['response']
        assert agent_server.settings_store.get_area('llm')['fallback_chain'] == original['fallback_chain']
        client.delete(f"/chat/sessions/{secret['session_id']}")
        client.delete(f"/chat/sessions/{invalid['session_id']}")
    finally:
        agent_server.settings_store.set_area('llm', original)


def test_connection_and_chat_truth_surface_visible_problems():
    client = TestClient(agent_server.app)
    status = client.get('/llm/connection').json()
    assert 'problems' in status
    assert isinstance(status['problems'], list)
    health = client.get('/health').json()
    reply = client.post('/chat', json={'message': 'Welche Fehler sind erkannt?', 'source': 'test-runtime-problems'}).json()
    assert reply['ok'] is True
    assert 'Aktiver Anbieter' in reply['response'] or 'keine erkannten' in reply['response'] or 'Erkannte Probleme' in reply['response']
    assert SECRET not in reply['response']
    runtime_problems = (reply.get('runtime_context') or {}).get('runtime_problems') or []
    assert isinstance(runtime_problems, list)
    for item in health.get('problems') or []:
        assert item in runtime_problems
        assert item in reply['response']
    if reply.get('session_id'):
        client.delete(f"/chat/sessions/{reply['session_id']}")


def test_chat_does_not_treat_work_phrase_as_settings_apply():
    client = TestClient(agent_server.app)
    original = agent_server.settings_store.get_area('llm')
    original_complete = agent_server.llm_backend.complete
    try:
        captured = {}

        async def fake_complete(system: str, user: str) -> str:
            captured['system'] = system
            captured['user'] = user
            return 'Ich setze die vorhandene Arbeit fort.'

        agent_server.llm_backend.complete = fake_complete
        body = client.post('/chat', json={'message': 'setz das um', 'source': 'test-settings-work-phrase'}).json()
        assert body.get('settings_apply') is None
        assert captured.get('user')
        assert 'setz das um' in captured['user']
        assert agent_server.settings_store.get_area('llm')['fallback_chain'] == original['fallback_chain']
        if body.get('session_id'):
            client.delete(f"/chat/sessions/{body['session_id']}")
    finally:
        agent_server.llm_backend.complete = original_complete
        agent_server.settings_store.set_area('llm', original)


def test_chat_and_operate_apply_general_settings_and_reject_invalid():
    client = TestClient(agent_server.app)
    original_ui = agent_server.settings_store.get_area('ui')
    original_llm = agent_server.settings_store.get_area('llm')
    try:
        groq = client.post('/chat', json={'message': 'Stell den Anbieter auf OpenAI-kompatibel und die Vorlage auf Groq', 'source': 'test-settings-preset'}).json()
        assert groq['settings_apply']['applied'] is True
        assert agent_server.settings_store.get_area('llm')['provider'] == 'openai'
        assert agent_server.settings_store.get_area('llm')['preset'] == 'groq'
        if groq.get('session_id'):
            client.delete(f"/chat/sessions/{groq['session_id']}")

        chat = client.post('/chat', json={'message': 'Ändere das Thema auf light', 'source': 'test-settings-theme'}).json()
        assert chat['settings_apply']['applied'] is True
        assert agent_server.settings_store.get_area('ui')['theme'] == 'light'
        assert 'light' in chat['response']
        assert SECRET not in chat['response']

        invalid = client.post('/settings/apply', json={
            'user_requested': True,
            'area': 'ui',
            'values': {'theme': 'neon'},
        }).json()
        assert invalid['ok'] is False
        assert invalid['applied'] is False
        assert agent_server.settings_store.get_area('ui')['theme'] == 'light'

        empty_chain = client.post('/settings/apply', json={
            'user_requested': True,
            'area': 'llm',
            'values': {'fallback_chain': []},
        }).json()
        assert empty_chain['ok'] is False
        assert 'nicht-leere Liste' in (empty_chain.get('error') or '')
        assert agent_server.settings_store.get_area('llm')['fallback_chain'] == original_llm['fallback_chain']

        operate = client.post('/api/v1/operate/settings/apply', json={
            'user_requested': True,
            'area': 'ui',
            'values': {'theme': 'dark'},
            'reason': 'Test über Operate',
        }).json()
        assert operate['ok'] is True
        assert operate['data']['applied'] is True
        assert operate['data']['settings']['theme'] == 'dark'
        assert 'api_key' not in (operate['data'].get('settings') or {})
        assert SECRET not in json.dumps(operate)
        assert agent_server.settings_store.get_area('ui')['theme'] == 'dark'

        denied = client.post('/api/v1/operate/settings/apply', json={
            'user_requested': False,
            'area': 'ui',
            'values': {'theme': 'light'},
        })
        assert denied.status_code == 400
        assert agent_server.settings_store.get_area('ui')['theme'] == 'dark'
        if chat.get('session_id'):
            client.delete(f"/chat/sessions/{chat['session_id']}")
    finally:
        agent_server.settings_store.set_area('ui', original_ui)
        agent_server.settings_store.set_area('llm', original_llm)


def test_healing_visible_problems_are_honest_not_placebo():
    assert healing_visible_problems(None) == []
    stopped = healing_visible_problems({'running': False, 'blocked': {}, 'error_counts': {}})
    assert stopped == ['SelfHealingService ist verdrahtet, läuft aber aktuell nicht.']
    blocked = healing_visible_problems({
        'running': True,
        'blocked': {'ollama': True},
        'error_counts': {'ollama': 2},
    })
    assert 'Healing-Check blockiert: ollama' in blocked
    assert 'Healing-Fehler ollama: 2' in blocked
    client = TestClient(agent_server.app)
    status = client.get('/healing/status').json()
    assert 'checks_registered' in status
    assert 'SelfHealingService' in (status.get('detail') or '')
    reply = client.post('/chat', json={'message': 'Welche Fehler sind erkannt?', 'source': 'test-healing-visible'}).json()
    assert reply['ok'] is True
    assert SECRET not in reply['response']
    if not status.get('available'):
        assert 'SelfHealingService' in reply['response']
    if reply.get('session_id'):
        client.delete(f"/chat/sessions/{reply['session_id']}")
