from __future__ import annotations

from eidolon.core.mesh_rendering import register_browser_device_pairing
from eidolon.core.mesh_peer_views import is_self_pairing


def create_pairing(service, target_name: str = '', target_address: str = '', target_port: int = 0) -> dict:
    code, qr_payload = service._pairing.create_pairing_request(name=service._name, address=service.get_local_ip(), port=service._http_port, public_key=service._public_key)
    return {'code': code, 'qr_payload': qr_payload, 'target_name': target_name, 'target_address': target_address, 'target_port': target_port, 'expires_in': 300}


def accept_pairing(service, code: str) -> dict:
    request = service._pairing.get_request(code)
    if not request:
        return {'ok': False, 'error': 'Code ungültig oder abgelaufen'}
    candidate = {'name': request.name, 'address': request.address, 'port': request.port, 'public_key': request.public_key}
    if is_self_pairing(service, candidate):
        return {'ok': False, 'error': 'Dieses Gerät kann sich nicht mit sich selbst koppeln'}
    result = service._pairing.accept_pairing(code)
    return {'ok': True, 'peer': result} if result else {'ok': False, 'error': 'Code ungültig oder abgelaufen'}


def accept_browser_pairing(service, code: str, *, device_name: str, peer_id: str, public_key: str, address: str, user_agent: str = '') -> dict:
    candidate = {'name': (device_name or '').strip()[:80] or 'Gekoppeltes Gerät', 'address': address, 'port': 0, 'public_key': (public_key or '').strip()}
    clean_peer_id = (peer_id or '').strip()
    if clean_peer_id == service._peer_id or is_self_pairing(service, candidate):
        return {'ok': False, 'error': 'Dieses Gerät kann sich nicht mit sich selbst koppeln'}
    return register_browser_device_pairing(service._pairing, code, device_name=device_name, peer_id=peer_id, public_key=public_key, address=address, user_agent=user_agent)


def unpair_peer(service, peer_id: str) -> dict:
    clean_peer_id = (peer_id or '').strip()
    if not clean_peer_id:
        return {'ok': False, 'error': 'Peer-ID fehlt'}
    paired = service._pairing.get_paired()
    if clean_peer_id not in paired or is_self_pairing(service, paired.get(clean_peer_id, {})):
        return {'ok': False, 'error': 'Gekoppeltes Gerät nicht gefunden'}
    removed = service._pairing.unpair(clean_peer_id)
    if not removed:
        return {'ok': False, 'error': 'Kopplung konnte nicht aufgehoben werden'}
    service._local_peers.pop(clean_peer_id, None)
    return {'ok': True, 'peer_id': clean_peer_id}
