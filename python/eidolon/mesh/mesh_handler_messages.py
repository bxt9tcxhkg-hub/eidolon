from __future__ import annotations

import time
from typing import Any

from eidolon.mesh.mesh_handler_support import message_id, message_string


def send_message(handler, peer_id: str, message_type: str, payload: dict[str, Any], priority: str = 'normal') -> dict[str, Any]:
    start = time.time()
    msg_id = message_id(peer_id, start)
    result = handler.inbox.append(to=peer_id, message=message_string(payload), from_id='eidolon-agent', message_type=message_type, metadata={'type': message_type, 'priority': priority})
    try:
        handler.peer_store.upsert_peer(peer_id=peer_id, pairing_status='accepted' if message_type == 'pairing_accept' else None, connection_status='reachable', via='mesh_send', metadata={'last_message_type': message_type, 'priority': priority})
    except Exception:
        pass
    latency_ms = (time.time() - start) * 1000
    handler._latency_samples.append(latency_ms)
    handler._message_count += 1
    handler._peer_ids.add(peer_id)
    return {'ok': True, 'msg_id': msg_id, 'status': result.get('status', 'stored'), 'latency_ms': round(latency_ms, 2), 'peer_id': peer_id}


def receive_message(handler, device_id: str, message_type: str = 'chat') -> dict[str, Any]:
    msgs = handler.inbox.get_recent_messages(device_id, limit=50)
    if not msgs:
        return {'ok': True, 'messages': [], 'count': 0}
    return {'ok': True, 'messages': msgs, 'count': len(msgs)}
