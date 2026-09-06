from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

from eidolon.core.config import PROJECT_ROOT, state_path

_quic_listener_running = False


def set_quic_listener_running(running: bool) -> None:
    global _quic_listener_running
    _quic_listener_running = bool(running)


def module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def cmd_available(name: str) -> bool:
    return shutil.which(name) is not None


def mesh_certificates_present() -> bool:
    mesh_dir = state_path('mesh', project_root=PROJECT_ROOT)
    return (mesh_dir / 'server.crt').exists() and (mesh_dir / 'server.key').exists()


def mesh_quic_available() -> bool:
    return _quic_listener_running


def filesystem_readable() -> bool:
    try:
        return Path(PROJECT_ROOT).exists() and os.access(PROJECT_ROOT, os.R_OK)
    except Exception:
        return False


def filesystem_writable() -> bool:
    try:
        target = state_path('.', project_root=PROJECT_ROOT)
        target.mkdir(parents=True, exist_ok=True)
        return os.access(target, os.W_OK)
    except Exception:
        return False


def evidence_store_available() -> bool:
    try:
        from eidolon.core.evidence import get_evidence_store
        get_evidence_store().get_blocked()
        return True
    except Exception:
        return False


def hud_runtime_available() -> bool:
    hud_module = Path(PROJECT_ROOT) / 'python' / 'eidolon' / 'ui' / 'hud.py'
    return module_available('PyQt6') and hud_module.exists()


def browser_control_available() -> bool:
    try:
        probe = (
            "import asyncio\n"
            "from playwright.async_api import async_playwright\n"
            "async def main():\n"
            "    async with async_playwright() as p:\n"
            "        b = await p.chromium.launch(headless=True)\n"
            "        await b.close()\n"
            "asyncio.run(main())\n"
        )
        result = subprocess.run([sys.executable, '-c', probe], capture_output=True, text=True, timeout=20)
        return result.returncode == 0
    except Exception:
        return False


def image_generation_available() -> bool:
    try:
        from eidolon.image_generation import get_image_generation_service
        return get_image_generation_service().is_available()[0]
    except Exception:
        return False


def chat_skills_runtime_available() -> bool:
    try:
        from eidolon.skills.live_skills import LIVE_SKILL_MODULES, _load_skill_module
        for stem in LIVE_SKILL_MODULES.values():
            mod = _load_skill_module(stem)
            if not callable(getattr(mod, 'run', None)):
                return False
        return True
    except Exception:
        return False


def ollama_available() -> bool:
    host = os.environ.get('OLLAMA_HOST') or os.environ.get('OLLAMA_URL') or 'http://127.0.0.1:11434'
    try:
        req = urllib.request.Request(str(host).rstrip('/') + '/api/tags', headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            status = getattr(resp, 'status', 200)
            if not (200 <= int(status) < 300):
                return False
            json.loads(resp.read().decode('utf-8'))
            return True
    except Exception:
        return False
