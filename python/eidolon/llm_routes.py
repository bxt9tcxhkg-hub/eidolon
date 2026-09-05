from __future__ import annotations

from typing import Any, Callable

from fastapi import FastAPI

from eidolon.core.llm_provider_catalog import catalog_payload, models_for_provider
from eidolon.core.llm_secrets import contains_secret, redact_secrets, store_api_key
from eidolon.core.llm_config_store import load_openai_api_key


def register_llm_routes(
    app: FastAPI,
    *,
    get_llm_backend: Callable[[], Any],
    get_settings_store: Callable[[], Any],
    get_ollama_models: Callable[[str], Any],
    get_openai_models: Callable[[], Any],
    get_openai_login_payload: Callable[[], Callable[[], dict[str, Any]]],
) -> None:
    def llm_backend():
        return get_llm_backend()

    def settings_store():
        return get_settings_store()

    @app.get('/llm/connection')
    async def llm_connection_status():
        status = llm_backend().status()
        return {'ok': True, **_public_status(status)}

    @app.get('/llm/providers')
    async def llm_providers():
        status = llm_backend().status()
        catalog = catalog_payload()
        return {'ok': True, **catalog, 'current_provider': status.get('provider'), 'auth_method': status.get('auth_method')}

    @app.get('/llm/models')
    async def llm_models():
        status = llm_backend().status()
        ollama_url = status.get('ollama_url') or settings_store().get_area('llm').get('ollama_url') or 'http://127.0.0.1:11434'
        openai_models = models_for_provider('openai', status.get('preset') or 'custom') or get_openai_models()
        return {
            'ok': True,
            'ollama': get_ollama_models(ollama_url),
            'openai': openai_models,
            'by_provider': {
                'ollama': get_ollama_models(ollama_url),
                'openai': openai_models,
                'openai_oauth': get_openai_models(),
            },
        }

    @app.post('/llm/openai/api-key')
    @app.post('/llm/api-key')
    async def llm_store_api_key(request: dict):
        result = store_api_key(str(request.get('api_key') or request.get('key') or ''))
        return _public_status(result)

    @app.post('/integrations/openai/auth')
    async def integrations_openai_auth():
        openai = dict(llm_backend().status().get('openai') or {})
        return {'ok': True, 'supported': True, 'provider': 'openai', 'auth_method': 'chatgpt_login', **openai}

    @app.post('/integrations/openai/login')
    async def integrations_openai_login():
        return get_openai_login_payload()()

    @app.get('/integrations/status')
    async def integrations_status():
        llm = llm_backend().status()
        openai = dict(llm.get('openai') or {})
        openai['current_provider'] = llm.get('provider') in ('openai', 'openai_oauth')
        return {
            'ok': True,
            'integrations': {
                'openai': openai,
                'ollama': {'configured': llm.get('provider') == 'ollama', 'url': llm.get('ollama_url')},
                'openai_compat': {
                    'configured': bool(llm.get('key_present')),
                    'current_provider': llm.get('provider') == 'openai',
                    'oauth_supported': False,
                    'auth_method': 'api_key',
                    'base_url': llm.get('base_url') or '',
                },
            },
        }


def _public_status(payload: dict[str, Any]) -> dict[str, Any]:
    secret = load_openai_api_key()
    public = dict(payload)
    for key in ('api_key', 'openai_api_key', 'raw_key', 'secret'):
        public.pop(key, None)
    blob = redact_secrets(repr(public), secret)
    if contains_secret(blob, secret):
        return {'ok': False, 'error': 'Antwort würde ein Geheimnis enthalten und wurde unterdrückt.'}
    return public
