from __future__ import annotations

from pathlib import Path

from eidolon.mesh.peer_mutations import mark_peer_offline, mark_peer_reachable, prune_offline_peers, refresh_statuses
from eidolon.mesh.peer_queries import get_peer, list_peers, upsert_peer
from eidolon.mesh.peer_store_support import connect, default_db_path, default_lock, init_schema


class PeerStateStore:
    def __init__(self, db_path: str | Path = default_db_path()):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = default_lock()
        init_schema(self.db_path)

    def _connect(self):
        return connect(self.db_path)

    def upsert_peer(self, **kwargs):
        return upsert_peer(self, **kwargs)

    def get_peer(self, peer_id: str):
        return get_peer(self, peer_id)

    def list_peers(self):
        return list_peers(self)

    def refresh_statuses(self):
        return refresh_statuses(self)

    def mark_peer_reachable(self, peer_id: str, *, via: str | None = None, metadata: dict | None = None):
        return mark_peer_reachable(self, peer_id, via=via, metadata=metadata)

    def prune_offline_peers(self, older_than_seconds: int = 1800 * 24):
        return prune_offline_peers(self, older_than_seconds=older_than_seconds)

    def mark_peer_offline(self, peer_id: str, reason: str | None = None):
        return mark_peer_offline(self, peer_id, reason=reason)


_default_store: PeerStateStore | None = None


def get_peer_state_store() -> PeerStateStore:
    global _default_store
    if _default_store is None:
        _default_store = PeerStateStore()
    return _default_store
