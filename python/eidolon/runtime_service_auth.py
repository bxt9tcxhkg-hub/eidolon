from __future__ import annotations

from typing import Any

import eidolon.core.llm_backend as llm_backend_mod


def spawn_openai_device_login() -> dict[str, Any]:
    if not llm_backend_mod._codex_available():
        return {
            'ok': False,
            'supported': False,
            'provider': 'openai',
            'auth_method': 'chatgpt_login',
            'logged_in': False,
            'configured': False,
            'error': 'Codex-CLI nicht gefunden. Es gibt keinen Gerätecode-Login in dieser Oberfläche.',
        }
    status = llm_backend_mod._codex_login_status()
    if status.get('logged_in'):
        return {
            'ok': True,
            'supported': True,
            'provider': 'openai',
            'auth_method': 'chatgpt_login',
            'status': 'already_logged_in',
            'logged_in': True,
            'configured': True,
        }
    return {
        'ok': False,
        'supported': True,
        'provider': 'openai',
        'auth_method': 'chatgpt_login',
        'status': 'manual_login_required',
        'logged_in': False,
        'configured': False,
        'detail': 'Codex-CLI verfügbar, aber nicht eingeloggt. Es gibt keinen Gerätecode in dieser Oberfläche. Führe im Terminal `codex login` aus.',
        'command': 'codex login',
    }
