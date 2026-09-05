from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from eidolon.core.llm_config_store import load_openai_api_key
from eidolon.core.llm_provider_catalog import resolve_base_url
from eidolon.core.llm_secrets import redact_secrets

# Cloudflare (Groq and similar fronts) returns 403 error code 1010 for urllib's
# default User-Agent. Identify as this product, not a browser spoof.
USER_AGENT = 'Eidolon/1.0 (+https://github.com/bxt9tcxhkg-hub/eidolon)'


def openai_compat_headers(api_key: str) -> dict[str, str]:
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'User-Agent': USER_AGENT,
    }


def complete_openai_compat(backend, *, system: str, user: str) -> str:
    api_key = load_openai_api_key()
    if not api_key:
        raise RuntimeError('API-Schlüssel fehlt. Hinterlege einen Key für den OpenAI-kompatiblen Anbieter.')
    base_url = resolve_base_url(getattr(backend, 'provider', 'openai'), getattr(backend, 'base_url', ''), getattr(backend, 'preset', 'custom'))
    if not base_url:
        raise RuntimeError('Basis-URL fehlt. Setze eine OpenAI-kompatible base_url oder ein Preset.')
    payload: dict[str, Any] = {
        'model': getattr(backend, 'model', '') or 'gpt-4o-mini',
        'messages': [
            {'role': 'system', 'content': system.strip()},
            {'role': 'user', 'content': user.strip()},
        ],
        'temperature': float(getattr(backend, 'temperature', 0.4) or 0.4),
        'max_tokens': int(getattr(backend, 'max_tokens', 4096) or 4096),
    }
    request = urllib.request.Request(
        base_url.rstrip('/') + '/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers=openai_compat_headers(api_key),
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            body = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        detail = redact_secrets(exc.read().decode('utf-8', errors='replace'), api_key)
        raise RuntimeError(f'OpenAI-kompatibler HTTP-Fehler {exc.code}: {detail[:400]}') from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f'OpenAI-kompatibler Endpunkt nicht erreichbar: {exc.reason}') from exc
    text = _extract_message_text(body)
    if not text:
        raise RuntimeError('OpenAI-kompatibler Endpunkt lieferte keine Antwort.')
    return text


def _extract_message_text(body: dict[str, Any]) -> str:
    choices = body.get('choices') or []
    if not choices:
        return ''
    message = choices[0].get('message') or {}
    content = message.get('content')
    if isinstance(content, list):
        parts = [str(part.get('text') or '') for part in content if isinstance(part, dict)]
        return ''.join(parts).strip()
    if isinstance(content, str) and content.strip():
        return content.strip()
    return str(choices[0].get('text') or '').strip()
