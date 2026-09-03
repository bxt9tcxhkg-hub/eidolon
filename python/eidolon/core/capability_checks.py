from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

from eidolon.core.config import PROJECT_ROOT, state_path


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
    try:
        from eidolon.mesh.transport.quic_server import EidolonQuicServer  # noqa: F401
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


def ollama_available() -> bool:
    return bool(os.environ.get('OLLAMA_HOST', 'http://localhost:11434'))
