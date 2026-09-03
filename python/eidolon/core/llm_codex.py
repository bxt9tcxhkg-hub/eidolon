from __future__ import annotations

import json
import subprocess
from pathlib import Path

from eidolon.core.llm_provider_status import codex_available, codex_login_status


def complete_openai_oauth(backend, *, system: str, user: str) -> str:
    if not codex_available():
        raise RuntimeError('Codex-CLI nicht gefunden. Installiere OpenAI Codex.')
    login = codex_login_status()
    if not login['logged_in']:
        raise RuntimeError('Codex ist nicht eingeloggt. Führe `codex login` aus.')
    prompt = f'{system.strip()}\n\nNutzeranfrage:\n{user.strip()}\n'
    model = backend.model or 'gpt-5.5'
    try:
        result = subprocess.run([
            'codex', 'exec', '--json', '-m', model, '-C', str(Path.home()), '--skip-git-repo-check', '--dangerously-bypass-approvals-and-sandbox', prompt,
        ], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=180, cwd=str(Path.home()), shell=True)
    except subprocess.TimeoutExpired:
        raise RuntimeError('Codex-Request nach 180s abgebrochen.')
    except FileNotFoundError:
        raise RuntimeError('Codex-CLI nicht gefunden.')
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        if 'usage limit' in stderr.lower() or 'rate limit' in stderr.lower():
            raise RuntimeError('OpenAI Usage-Limit erreicht. Upgrade zu Pro oder warte auf Reset.')
        raise RuntimeError(f'Codex-Fehler (exit {result.returncode}): {stderr[:500]}')
    for line in result.stdout.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get('type') == 'item.completed':
            item = event.get('item', {})
            if item.get('type') == 'agent_message' and item.get('text', '').strip():
                return item['text'].strip()
    raise RuntimeError('Codex hat keine Antwort geliefert.')
