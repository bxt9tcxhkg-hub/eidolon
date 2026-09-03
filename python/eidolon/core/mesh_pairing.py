from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from eidolon.core.config import state_path
from eidolon.core.mesh_models import PairingRequest


class MeshPairing:
    def __init__(self, project_root: Path):
        self._root = project_root
        self._requests: dict[str, PairingRequest] = {}
        self._paired: dict[str, dict] = {}
        self._load()

    def _load(self):
        path = state_path('mesh', 'pairings.json', project_root=self._root)
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            self._paired = data.get('paired', {})
        except Exception:
            self._paired = {}

    def _save(self):
        path = state_path('mesh', 'pairings.json', project_root=self._root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'paired': self._paired}, indent=2), encoding='utf-8')

    def create_pairing_request(self, name: str, address: str, port: int, public_key: str) -> tuple[str, str]:
        import secrets
        code = secrets.token_hex(4).upper()
        peer_id = hashlib.sha256(code.encode()).hexdigest()[:16]
        request = PairingRequest(code=code, peer_id=peer_id, name=name, address=address, port=port, public_key=public_key, created_at=time.time(), expires_at=time.time() + 300)
        self._requests[code] = request
        qr_payload = f'http://{address}:{port}/pairing?code={code}&name={quote(name)}'
        return code, qr_payload

    def get_request(self, code: str) -> PairingRequest | None:
        return self._requests.get(code)

    def accept_pairing(self, code: str) -> dict | None:
        request = self._requests.get(code)
        if not request:
            return None
        if time.time() > request.expires_at:
            del self._requests[code]
            return None
        request.status = 'accepted'
        self._paired[request.peer_id] = {'name': request.name, 'address': request.address, 'port': request.port, 'public_key': request.public_key, 'paired_at': datetime.now(tz=timezone.utc).isoformat()}
        self._save()
        return self._paired[request.peer_id]

    def reject_pairing(self, code: str) -> bool:
        request = self._requests.get(code)
        if not request:
            return False
        request.status = 'rejected'
        del self._requests[code]
        return True

    def get_paired(self) -> dict[str, dict]:
        return dict(self._paired)

    def unpair(self, peer_id: str) -> bool:
        clean_peer_id = (peer_id or '').strip()
        if not clean_peer_id or clean_peer_id not in self._paired:
            return False
        del self._paired[clean_peer_id]
        self._save()
        return True

    def get_pending(self) -> list[dict]:
        return [
            {'code': request.code, 'peer_id': request.peer_id, 'name': request.name, 'address': request.address, 'port': request.port, 'expires_at': datetime.fromtimestamp(request.expires_at, tz=timezone.utc).isoformat()}
            for request in self._requests.values()
            if request.status == 'pending' and time.time() <= request.expires_at
        ]

    def verify_code(self, code: str) -> bool:
        request = self._requests.get(code)
        return bool(request and time.time() <= request.expires_at)
