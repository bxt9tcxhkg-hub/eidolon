from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from eidolon.mesh.peer_models import merge_metadata, row_to_peer


def upsert_peer(store, *, peer_id: str, peer_name: str | None = None, pairing_status: str | None = None, connection_status: str | None = None, last_seen: str | None = None, paired_at: str | None = None, host: str | None = None, http_port: int | None = None, quic_port: int | None = None, via: str | None = None, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    if not peer_id:
        raise ValueError('peer_id required')
    seen = last_seen or datetime.now(timezone.utc).isoformat()
    with store._lock:
        with store._connect() as conn:
            existing = conn.execute('SELECT metadata_json FROM peers WHERE peer_id = ?', (peer_id,)).fetchone()
            merged_meta = merge_metadata(existing, metadata or {})
            conn.execute(
                'INSERT INTO peers (peer_id, peer_name, pairing_status, connection_status, last_seen, paired_at, host, http_port, quic_port, via, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(peer_id) DO UPDATE SET peer_name=COALESCE(excluded.peer_name, peers.peer_name), pairing_status=COALESCE(excluded.pairing_status, peers.pairing_status), connection_status=COALESCE(excluded.connection_status, peers.connection_status), last_seen=COALESCE(excluded.last_seen, peers.last_seen), paired_at=COALESCE(excluded.paired_at, peers.paired_at), host=COALESCE(excluded.host, peers.host), http_port=COALESCE(excluded.http_port, peers.http_port), quic_port=COALESCE(excluded.quic_port, peers.quic_port), via=COALESCE(excluded.via, peers.via), metadata_json=excluded.metadata_json',
                (peer_id, peer_name, pairing_status, connection_status, seen, paired_at, host, http_port, quic_port, via, json.dumps(merged_meta, ensure_ascii=False)),
            )
            conn.commit()
    return store.get_peer(peer_id) or {'peer_id': peer_id}


def list_peers(store) -> list[dict[str, Any]]:
    with store._connect() as conn:
        rows = conn.execute('SELECT peer_id, peer_name, pairing_status, connection_status, last_seen, paired_at, host, http_port, quic_port, via, metadata_json FROM peers ORDER BY COALESCE(last_seen, paired_at, peer_id) DESC').fetchall()
    return [row_to_peer(row) for row in rows]


def get_peer(store, peer_id: str) -> dict[str, Any] | None:
    with store._connect() as conn:
        row = conn.execute('SELECT peer_id, peer_name, pairing_status, connection_status, last_seen, paired_at, host, http_port, quic_port, via, metadata_json FROM peers WHERE peer_id = ?', (peer_id,)).fetchone()
    return row_to_peer(row) if row else None
