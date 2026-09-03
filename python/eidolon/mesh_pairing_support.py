from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_pairing_page(code: str, name: str) -> str:
    template_path = Path(__file__).with_name('web') / 'pairing-page.html'
    html = template_path.read_text(encoding='utf-8')
    return (
        html.replace('__PAIRING_CODE__', code)
        .replace('__PAIRING_NAME__', name or 'unbekannt')
        .replace('__PAIRING_CODE_JS__', json.dumps(code)[1:-1])
        .replace('__PAIRING_NAME_JS__', json.dumps(name)[1:-1])
    )


def pairing_self_payload(mesh_service, http_port: int) -> dict[str, Any]:
    return {
        'peer_id': mesh_service.peer_id,
        'name': mesh_service.name,
        'address': mesh_service.get_local_ip(),
        'port': http_port,
    }


def pairing_status_payload(mesh_service, http_port: int) -> dict[str, Any]:
    return {
        'ok': True,
        'self': {**pairing_self_payload(mesh_service, http_port), 'public_key': mesh_service.public_key[:32] + '...'},
        'peers': len(mesh_service.scan_peers()),
        'paired': len(mesh_service.get_paired_peers()),
        'pending': len(mesh_service.get_pending_requests()),
    }
