from __future__ import annotations

from datetime import datetime, timezone

from eidolon.mesh.peer_models import OFFLINE_AFTER_SECONDS


def refresh_statuses(store) -> list[dict]:
    peers = store.list_peers()
    for peer in peers:
        status = peer.get('status')
        if status in ('reachable', 'stale', 'offline'):
            store.upsert_peer(peer_id=peer['peer_id'], connection_status=status, last_seen=peer.get('last_seen'), via=peer.get('via'), metadata=peer.get('metadata') or {})
    return store.list_peers()


def mark_peer_reachable(store, peer_id: str, *, via: str | None = None, metadata: dict | None = None):
    peer = store.get_peer(peer_id)
    if not peer:
        return None
    merged = dict(peer.get('metadata') or {})
    if metadata:
        merged.update(metadata)
    return store.upsert_peer(peer_id=peer_id, peer_name=peer.get('peer_name'), pairing_status=peer.get('pairing_status'), connection_status='reachable', paired_at=peer.get('paired_at'), host=peer.get('host'), http_port=peer.get('http_port'), quic_port=peer.get('quic_port'), via=via or peer.get('via'), metadata=merged)


def mark_peer_offline(store, peer_id: str, reason: str | None = None):
    peer = store.get_peer(peer_id)
    if not peer:
        return None
    metadata = dict(peer.get('metadata') or {})
    if reason:
        metadata['offline_reason'] = reason
    return store.upsert_peer(peer_id=peer_id, peer_name=peer.get('peer_name'), pairing_status=peer.get('pairing_status'), connection_status='offline', last_seen=peer.get('last_seen'), paired_at=peer.get('paired_at'), host=peer.get('host'), http_port=peer.get('http_port'), quic_port=peer.get('quic_port'), via=peer.get('via'), metadata=metadata)


def prune_offline_peers(store, older_than_seconds: int = OFFLINE_AFTER_SECONDS * 24) -> int:
    cutoff = datetime.now(timezone.utc).timestamp() - older_than_seconds
    removed = 0
    with store._lock:
        with store._connect() as conn:
            rows = conn.execute('SELECT peer_id, last_seen FROM peers WHERE connection_status = ?', ('offline',)).fetchall()
            for peer_id, last_seen in rows:
                try:
                    seen_dt = datetime.fromisoformat(str(last_seen).replace('Z', '+00:00'))
                    if seen_dt.timestamp() <= cutoff:
                        conn.execute('DELETE FROM peers WHERE peer_id = ?', (peer_id,))
                        removed += 1
                except Exception:
                    continue
            conn.commit()
    return removed
