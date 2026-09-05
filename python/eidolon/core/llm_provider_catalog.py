from __future__ import annotations

from typing import Any

from eidolon.core.llm_config_store import OLLAMA_MODELS, OPENAI_MODELS


PROVIDER_OLLAMA = 'ollama'
PROVIDER_OPENAI_COMPAT = 'openai'
PROVIDER_OPENAI_OAUTH = 'openai_oauth'
PROVIDER_IDS = (PROVIDER_OLLAMA, PROVIDER_OPENAI_COMPAT, PROVIDER_OPENAI_OAUTH)

AUTH_NONE = 'none'
AUTH_API_KEY = 'api_key'
AUTH_CHATGPT = 'chatgpt_login'
AUTH_METHODS = (AUTH_NONE, AUTH_API_KEY, AUTH_CHATGPT)

KIND_OLLAMA = 'ollama'
KIND_OPENAI_COMPAT = 'openai_compat'
KIND_OPENAI_OAUTH = 'openai_oauth'


def _provider(id: str, label: str, kind: str, auth_method: str, *, oauth_supported: bool, needs_base_url: bool, needs_api_key: bool, default_base_url: str = '') -> dict[str, Any]:
    return {
        'id': id,
        'label': label,
        'kind': kind,
        'auth_methods': [auth_method],
        'oauth_supported': oauth_supported,
        'needs_base_url': needs_base_url,
        'needs_api_key': needs_api_key,
        'default_base_url': default_base_url,
    }


def _preset(id: str, label: str, base_url: str, models: list[str]) -> dict[str, Any]:
    return {'id': id, 'label': label, 'base_url': base_url, 'models': list(models)}


PROVIDER_SPECS: tuple[dict[str, Any], ...] = (
    _provider(PROVIDER_OLLAMA, 'Ollama lokal', KIND_OLLAMA, AUTH_NONE, oauth_supported=False, needs_base_url=False, needs_api_key=False),
    _provider(PROVIDER_OPENAI_COMPAT, 'OpenAI-kompatibel (API-Key)', KIND_OPENAI_COMPAT, AUTH_API_KEY, oauth_supported=False, needs_base_url=True, needs_api_key=True, default_base_url='https://api.openai.com/v1'),
    _provider(PROVIDER_OPENAI_OAUTH, 'OpenAI (ChatGPT-Login)', KIND_OPENAI_OAUTH, AUTH_CHATGPT, oauth_supported=True, needs_base_url=False, needs_api_key=False),
)

PRESET_SPECS: tuple[dict[str, Any], ...] = (
    _preset('custom', 'Benutzerdefiniert', '', []),
    _preset('openai', 'OpenAI', 'https://api.openai.com/v1', OPENAI_MODELS),
    _preset('groq', 'Groq', 'https://api.groq.com/openai/v1', ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768', 'openai/gpt-oss-120b']),
    _preset('openrouter', 'OpenRouter', 'https://openrouter.ai/api/v1', ['openai/gpt-4o-mini', 'anthropic/claude-sonnet-4']),
    _preset('mistral', 'Mistral', 'https://api.mistral.ai/v1', ['mistral-small-latest', 'mistral-large-latest']),
    _preset('gemini', 'Gemini (OpenAI-kompatibel)', 'https://generativelanguage.googleapis.com/v1beta/openai', ['gemini-2.0-flash', 'gemini-1.5-flash']),
    _preset('local', 'Lokales Gateway', 'http://127.0.0.1:8080/v1', []),
)

PRESET_IDS = tuple(item['id'] for item in PRESET_SPECS)


def provider_spec(provider_id: str) -> dict[str, Any]:
    for spec in PROVIDER_SPECS:
        if spec['id'] == provider_id:
            return dict(spec)
    return dict(PROVIDER_SPECS[0])


def preset_spec(preset_id: str) -> dict[str, Any]:
    for spec in PRESET_SPECS:
        if spec['id'] == preset_id:
            return dict(spec)
    return dict(PRESET_SPECS[0])


def catalog_payload() -> dict[str, Any]:
    return {
        'providers': [dict(item) for item in PROVIDER_SPECS],
        'presets': [dict(item) for item in PRESET_SPECS],
    }


def models_for_provider(provider_id: str, preset_id: str = 'custom') -> list[str]:
    if provider_id == PROVIDER_OLLAMA:
        return list(OLLAMA_MODELS)
    if provider_id == PROVIDER_OPENAI_OAUTH:
        return list(OPENAI_MODELS)
    models = preset_spec(preset_id).get('models') or []
    return list(models) if models else list(OPENAI_MODELS)


def resolve_base_url(provider_id: str, base_url: str = '', preset_id: str = 'custom') -> str:
    spec = provider_spec(provider_id)
    if spec['kind'] != KIND_OPENAI_COMPAT:
        return ''
    cleaned = (base_url or '').strip().rstrip('/')
    if cleaned:
        return cleaned
    preset = preset_spec(preset_id)
    return (preset.get('base_url') or spec.get('default_base_url') or '').rstrip('/')


def normalize_llm_settings(values: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    out = dict(values)
    changed: list[str] = []
    spec = provider_spec(str(out.get('provider') or PROVIDER_OLLAMA))
    expected_auth = spec['auth_methods'][0]
    if out.get('auth_method') != expected_auth:
        out['auth_method'] = expected_auth
        changed.append('auth_method')
    if spec['kind'] == KIND_OPENAI_COMPAT:
        resolved = resolve_base_url(spec['id'], str(out.get('base_url') or ''), str(out.get('preset') or 'custom'))
        if resolved and out.get('base_url') != resolved:
            out['base_url'] = resolved
            changed.append('base_url')
    return out, changed


def build_fallback_chain(primary: str, fallback_chain: list[str] | None) -> list[str]:
    chain = [primary] if primary in PROVIDER_IDS else []
    for item in fallback_chain or []:
        if item in PROVIDER_IDS and item not in chain:
            chain.append(item)
    if not chain:
        chain = [PROVIDER_OLLAMA]
    return chain
