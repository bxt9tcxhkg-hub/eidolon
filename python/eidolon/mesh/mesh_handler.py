"""
Eidolon Mesh Handler — zentraler Mesh-Kommunikationsmanager

Kombiniert QUIC-Transport, Inbox-Verwaltung und Proto-Edge-Evolution.
Wird vom Agent-Server für alle Geräte-zu-Gerät-Kommunikation verwendet.
"""
from __future__ import annotations

import time
from pathlib import Path

from eidolon.core.config import MESH_DISCOVERY_PORT, QUIC_PORT
from eidolon.mesh.inbox import get_mesh_inbox_store
from eidolon.mesh.mesh_handler_messages import receive_message, send_message
from eidolon.mesh.mesh_handler_runtime import enable_adaptive_compression, enable_message_batching, enable_priority_routing, start, stop
from eidolon.mesh.mesh_handler_support import metric_payload
from eidolon.mesh.peers import get_peer_state_store


class MeshHandler:
    """Zentraler Mesh-Manager: Transport + Inbox + Proto-Edge."""

    def __init__(self, project_root: str = '.') -> None:
        self.project_root = Path(project_root)
        self.inbox = get_mesh_inbox_store()
        self.peer_store = get_peer_state_store()
        self.quic_port = QUIC_PORT
        self.discovery_port = MESH_DISCOVERY_PORT
        self._latency_samples: list[float] = []
        self._peer_ids: set[str] = set()
        self._message_count = 0
        self._started_at = time.time()

    def send_message(self, peer_id: str, message_type: str, payload: dict[str, object], priority: str = 'normal') -> dict[str, object]:
        return send_message(self, peer_id, message_type, payload, priority)

    def receive_message(self, device_id: str, message_type: str = 'chat') -> dict[str, object]:
        return receive_message(self, device_id, message_type)

    def get_metrics(self) -> dict[str, object]:
        return metric_payload(self._latency_samples, self._peer_ids, self._message_count, self._started_at)

    def enable_priority_routing(self) -> bool:
        return enable_priority_routing(self)

    def enable_message_batching(self) -> bool:
        return enable_message_batching(self)

    def enable_adaptive_compression(self) -> bool:
        return enable_adaptive_compression(self)

    def start(self) -> dict[str, object]:
        return start(self)

    def stop(self) -> None:
        stop(self)


_default_handler: MeshHandler | None = None


def get_mesh_handler(project_root: str = '.') -> MeshHandler:
    global _default_handler
    if _default_handler is None:
        _default_handler = MeshHandler(project_root=project_root)
    return _default_handler
