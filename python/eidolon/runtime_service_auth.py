from __future__ import annotations

from typing import Any

import eidolon.core.llm_backend as llm_backend_mod


def spawn_openai_device_login() -> dict[str, Any]:
    if not llm_backend_mod._codex_available():
        return {'ok': False, 'supported': False, 'provider': 'openai', 'auth_method': 'chatgpt_login', 'error': 'Codex-CLI nicht gefunden'}
    status = llm_backend_mod._codex_login_status()
    if status.get('logged_in'):
        return {'ok': True, 'supported': True, 'provider': 'openai', 'auth_method': 'chatgpt_login', 'status': 'already_logged_in', 'logged_in': True}
    return {
        'ok': True,
        'supported': True,
        'provider': 'openai',
        'auth_method': 'chatgpt_login',
        'status': 'manual_login_required',
        'logged_in': False,
        'detail': 'Codex-CLI verfügbar, aber nicht eingeloggt. Führe `codex login` aus.',
        'command': 'codex login --device-auth',
    }
