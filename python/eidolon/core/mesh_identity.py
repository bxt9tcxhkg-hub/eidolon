from __future__ import annotations

import hashlib
import json
import socket
from pathlib import Path

from eidolon.core.config import state_path
from eidolon.core.mesh_support import MeshCrypto


def host_identity(project_root: Path) -> tuple[str, str]:
    name = socket.gethostname()
    peer_id = hashlib.sha256(name.encode()).hexdigest()[:16]
    key_path = state_path('mesh', 'identity.key', project_root=project_root)
    if key_path.exists():
        data = json.loads(key_path.read_text(encoding='utf-8'))
        return peer_id, data.get('public', '')
    private_key, public_key = MeshCrypto.generate_keypair()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(json.dumps({'private': private_key, 'public': public_key}), encoding='utf-8')
    return peer_id, public_key


def local_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:
        return '127.0.0.1'
