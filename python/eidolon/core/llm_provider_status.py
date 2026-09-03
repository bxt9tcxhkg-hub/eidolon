from __future__ import annotations

import json
import subprocess
import urllib.request
from pathlib import Path
from typing import Any

from eidolon.core.llm_config_store import OLLAMA_MODELS, OPENAI_MODELS


def get_ollama_models(url: str) -> list[str]:
    try:
        req = urllib.request.Request(url.rstrip('/') + '/api/tags', headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            models = [model['name'] for model in data.get('models', [])]
            return models if models else OLLAMA_MODELS
    except Exception:
        return OLLAMA_MODELS


def get_openai_models() -> list[str]:
    return OPENAI_MODELS


def codex_available() -> bool:
    import shutil
    for cmd in ['codex', 'codex.cmd']:
        if shutil.which(cmd):
            return True
    try:
        result = subprocess.run(['codex', '--version'], capture_output=True, text=True, timeout=10, shell=True)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def codex_login_status() -> dict[str, Any]:
    try:
        result = subprocess.run(['codex', 'login', 'status'], capture_output=True, text=True, timeout=15, shell=True)
        output = (result.stdout + result.stderr).lower()
        if 'logged in' in output or 'chatgpt' in output:
            return {'logged_in': True, 'mode': 'chatgpt'}
        return {'logged_in': False, 'mode': 'none'}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {'logged_in': False, 'mode': 'none'}


def openai_connection_status() -> dict[str, Any]:
    if codex_available():
        login = codex_login_status()
        if login['logged_in']:
            return {'configured': True, 'source': 'codex_login', 'oauth_supported': True, 'auth_method': 'chatgpt_login', 'detail': 'OpenAI wird über deinen ChatGPT-Login via Codex-CLI verbunden.'}
        return {'configured': False, 'source': 'codex_available', 'oauth_supported': True, 'auth_method': 'chatgpt_login', 'detail': 'Codex-CLI gefunden, aber nicht eingeloggt. Führe `codex login` aus.'}
    return {'configured': False, 'source': 'missing', 'oauth_supported': False, 'auth_method': 'none', 'detail': 'Codex-CLI nicht gefunden. Installiere OpenAI Codex.'}
