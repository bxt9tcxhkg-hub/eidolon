from __future__ import annotations

import json
import urllib.error
import urllib.request


def complete_ollama(backend, *, system: str, user: str) -> str:
    prompt = f'{system.strip()}\n\nNutzeranfrage:\n{user.strip()}\n'
    payload = {'model': backend.model, 'prompt': prompt, 'stream': False, 'options': {'temperature': 0.4}}
    request = urllib.request.Request(backend.ollama_url.rstrip('/') + '/api/generate', data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            body = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'Ollama HTTP-Fehler {exc.code}: {detail}') from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f'Ollama nicht erreichbar: {exc.reason}') from exc
    text = str(body.get('response') or '').strip()
    if not text:
        raise RuntimeError('Ollama lieferte keine Antwort.')
    return text
