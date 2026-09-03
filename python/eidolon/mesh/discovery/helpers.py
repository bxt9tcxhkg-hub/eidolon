from __future__ import annotations
from pathlib import Path
import logging
import secrets
import socket

logger = logging.getLogger("eidolon.mesh.discovery")


def _local_ip() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return None


def generate_pairing_code() -> str:
    return f"{secrets.randbelow(1000000):06d}"
