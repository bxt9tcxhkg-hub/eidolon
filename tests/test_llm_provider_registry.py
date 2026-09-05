from pathlib import Path
import asyncio
import json
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))

import eidolon.core.llm_fallback as llm_fallback
from eidolon.core.llm_backend import LLMBackend
from eidolon.core.llm_config_store import load_llm_config, save_llm_config, save_openai_api_key
from eidolon.core.llm_provider_catalog import build_fallback_chain, normalize_llm_settings
from eidolon.core.llm_secrets import contains_secret, mask_secret
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
        seen['auth'] = request.headers.get('Authorization')
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
        assert seen['payload']['model'] == 'llama-3.1-8b-instant'
    finally:
        save_openai_api_key('')
        save_llm_config(original_cfg)


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
