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


def openai_compat_payload(backend, *, system: str, user: str, stream: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        'model': getattr(backend, 'model', '') or 'gpt-4o-mini',
        'messages': [
            {'role': 'system', 'content': system.strip()},
            {'role': 'user', 'content': user.strip()},
        ],
        'temperature': float(getattr(backend, 'temperature', 0.4) or 0.4),
        'max_tokens': int(getattr(backend, 'max_tokens', 4096) or 4096),
    }
    if stream:
        payload['stream'] = True
    return payload


def _openai_compat_request(backend, *, system: str, user: str, stream: bool = False) -> tuple[urllib.request.Request, str]:
    api_key = load_openai_api_key()
    if not api_key:
        raise RuntimeError('API-Schlüssel fehlt. Hinterlege einen Key für den OpenAI-kompatiblen Anbieter.')
    base_url = resolve_base_url(getattr(backend, 'provider', 'openai'), getattr(backend, 'base_url', ''), getattr(backend, 'preset', 'custom'))
    if not base_url:
        raise RuntimeError('Basis-URL fehlt. Setze eine OpenAI-kompatible base_url oder ein Preset.')
    payload = openai_compat_payload(backend, system=system, user=user, stream=stream)
    request = urllib.request.Request(
        base_url.rstrip('/') + '/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers=openai_compat_headers(api_key),
        method='POST',
    )
    return request, api_key


def _open_openai_compat(request: urllib.request.Request, api_key: str):
    try:
        return urllib.request.urlopen(request, timeout=90)
    except urllib.error.HTTPError as exc:
        detail = redact_secrets(exc.read().decode('utf-8', errors='replace'), api_key)
        raise RuntimeError(f'OpenAI-kompatibler HTTP-Fehler {exc.code}: {detail[:400]}') from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f'OpenAI-kompatibler Endpunkt nicht erreichbar: {exc.reason}') from exc


def complete_openai_compat(backend, *, system: str, user: str) -> str:
    request, api_key = _openai_compat_request(backend, system=system, user=user, stream=False)
    with _open_openai_compat(request, api_key) as response:
        body = json.loads(response.read().decode('utf-8'))
    text = _extract_message_text(body)
    if not text:
        raise RuntimeError('OpenAI-kompatibler Endpunkt lieferte keine Antwort.')
    return text


def stream_openai_compat(backend, *, system: str, user: str):
    """Yield real completion deltas. Does not invent tokens from a finished string."""
    request, api_key = _openai_compat_request(backend, system=system, user=user, stream=True)
    yielded = False
    with _open_openai_compat(request, api_key) as response:
        for raw in response:
            line = raw.decode('utf-8', errors='replace') if isinstance(raw, (bytes, bytearray)) else str(raw)
            delta = parse_openai_sse_delta(line)
            if delta is None:
                break
            if delta:
                yielded = True
                yield delta
    if not yielded:
        raise RuntimeError('OpenAI-kompatibler Endpunkt lieferte keinen Stream.')


def parse_openai_sse_delta(line: str) -> str | None:
    """Return delta text, '' to skip, or None when the stream is done."""
    text = line.strip()
    if not text:
        return ''
    if not text.startswith('data:'):
        return ''
    data = text[5:].strip()
    if data == '[DONE]':
        return None
    try:
        chunk = json.loads(data)
    except json.JSONDecodeError:
        return ''
    if not isinstance(chunk, dict):
        return ''
    return _extract_delta_text(chunk)


def _extract_delta_text(chunk: dict[str, Any]) -> str:
    choices = chunk.get('choices') or []
    if not choices or not isinstance(choices[0], dict):
        return ''
    delta = choices[0].get('delta') or {}
    content = delta.get('content') if isinstance(delta, dict) else None
    if isinstance(content, list):
        return ''.join(str(part.get('text') or '') for part in content if isinstance(part, dict))
    if isinstance(content, str) and content:
        return content
    text = choices[0].get('text')
    return text if isinstance(text, str) else ''


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
