from __future__ import annotations

from typing import Any

from eidolon.core.llm_provider_catalog import KIND_OLLAMA, KIND_OPENAI_COMPAT, catalog_payload, provider_spec, resolve_base_url
from eidolon.core.llm_provider_status import openai_connection_status
from eidolon.core.llm_secrets import secret_status


def selected_connection(backend) -> dict[str, Any]:
    spec = provider_spec(getattr(backend, 'provider', 'ollama'))
    if spec['kind'] == KIND_OLLAMA:
        url = getattr(backend, 'ollama_url', '') or ''
        return {
            'status': 'connected' if url else 'missing',
            'auth_method': 'none',
            'oauth_supported': False,
            'configured': bool(url),
            'detail': f'Ollama nutzt {url}.' if url else 'Ollama-URL fehlt.',
        }
    if spec['kind'] == KIND_OPENAI_COMPAT:
        secrets = secret_status()
        configured = bool(secrets['key_present'])
        return {
            'status': 'connected' if configured else 'missing',
            'auth_method': 'api_key',
            'oauth_supported': False,
            'configured': configured,
            'detail': 'API-Schlüssel hinterlegt. OAuth ist für diesen Anbieter nicht verfügbar.' if configured else 'API-Schlüssel fehlt. OAuth ist für diesen Anbieter nicht verfügbar.',
        }
    oauth = openai_connection_status()
    return {
        'status': 'connected' if oauth.get('configured') else 'missing',
        'auth_method': oauth.get('auth_method') or 'chatgpt_login',
        'oauth_supported': bool(oauth.get('oauth_supported')),
        'configured': bool(oauth.get('configured')),
        'detail': oauth.get('detail') or '',
        'source': oauth.get('source'),
    }


def backend_status(backend) -> dict[str, Any]:
    secrets = secret_status()
    connection = selected_connection(backend)
    return {
        'model': getattr(backend, 'model', ''),
        'provider': getattr(backend, 'provider', 'ollama'),
        'ollama_url': getattr(backend, 'ollama_url', ''),
        'base_url': resolve_base_url(getattr(backend, 'provider', 'ollama'), getattr(backend, 'base_url', ''), getattr(backend, 'preset', 'custom')),
        'preset': getattr(backend, 'preset', 'custom'),
        'auth_method': connection['auth_method'],
        'fallback_chain': list(getattr(backend, 'fallback_chain', []) or []),
        'connection': connection,
        'openai': openai_connection_status(),
        'providers': catalog_payload()['providers'],
        'presets': catalog_payload()['presets'],
        'key_present': secrets['key_present'],
        'key_masked': secrets['key_masked'],
        'key_source': secrets['source'],
    }
