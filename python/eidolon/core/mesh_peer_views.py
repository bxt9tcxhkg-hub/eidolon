from __future__ import annotations

import time
from typing import Any

from eidolon.core.mesh_support import PeerInfo


def is_self_pairing(service, info: dict[str, Any]) -> bool:
    address = str(info.get('address') or '')
    public_key = str(info.get('public_key') or '')
    name = str(info.get('name') or '')
    return public_key == service._public_key or (address and address == service.get_local_ip() and name == service._name)


def scan_peers(service) -> list[PeerInfo]:
    service._discovery.broadcast_presence(service._http_port, service._peer_id, service._name, service._public_key)
    discovered_map = {peer.peer_id: peer for peer in service._discovery.get_peers()}
    combined: dict[str, PeerInfo] = dict(discovered_map)
    for peer_id, info in service._pairing.get_paired().items():
        if is_self_pairing(service, info):
            continue
        if peer_id in combined:
            combined[peer_id].paired = True
            continue
        combined[peer_id] = PeerInfo(peer_id=peer_id, name=info.get('name') or peer_id, address=info.get('address') or '', port=int(info.get('port') or service._http_port), public_key=info.get('public_key') or '', last_seen=time.time(), status='paired', latency_ms=0.0, paired=True)
    service._local_peers = combined
    return list(combined.values())


def paired_peers(service) -> list[dict]:
    return [{'peer_id': peer_id, **info} for peer_id, info in service._pairing.get_paired().items() if not is_self_pairing(service, info)]
