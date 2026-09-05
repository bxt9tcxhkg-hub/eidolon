from __future__ import annotations

import os
import re
from typing import Any

from eidolon.core.llm_config_store import load_openai_api_key, save_openai_api_key


SECRET_PATTERNS = (
    re.compile(r'Bearer\s+\S+', re.IGNORECASE),
    re.compile(r'(api[_-]?key|authorization)\s*[:=]\s*\S+', re.IGNORECASE),
)


def api_key_source() -> str:
    if os.environ.get('OPENAI_API_KEY', '').strip():
        return 'environment'
    key = load_openai_api_key()
    return 'file' if key else 'missing'


def mask_secret(value: str) -> str:
    key = (value or '').strip()
    if not key:
        return ''
    if len(key) <= 8:
        return '••••'
    return f'{key[:4]}…{key[-4:]}'


def secret_status() -> dict[str, Any]:
    key = load_openai_api_key()
    source = api_key_source()
    return {
        'key_present': bool(key),
        'key_masked': mask_secret(key),
        'source': source,
    }


def store_api_key(api_key: str) -> dict[str, Any]:
    save_openai_api_key(api_key)
    status = secret_status()
    return {'ok': True, **status, 'detail': 'API-Schlüssel gespeichert.' if status['key_present'] else 'API-Schlüssel entfernt.'}


def redact_secrets(text: str, *secrets: str) -> str:
    redacted = str(text or '')
    for secret in secrets:
        cleaned = (secret or '').strip()
        if cleaned:
            redacted = redacted.replace(cleaned, '***')
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub('***', redacted)
    return redacted


def contains_secret(payload: Any, *secrets: str) -> bool:
    blob = payload if isinstance(payload, str) else repr(payload)
    for secret in secrets:
        cleaned = (secret or '').strip()
        if cleaned and cleaned in blob:
            return True
    return False
