from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

STALE_AFTER_SECONDS = 300
OFFLINE_AFTER_SECONDS = 1800


def row_to_peer(row: tuple[Any, ...]) -> dict[str, Any]:
    peer_id, peer_name, pairing_status, connection_status, last_seen, paired_at, host, http_port, quic_port, via, metadata_json = row
    try:
        metadata = json.loads(metadata_json or '{}')
    except Exception:
        metadata = {}
    freshness_status = connection_status or 'unknown'
    reachable = freshness_status == 'reachable'
    if last_seen:
        try:
            seen_dt = datetime.fromisoformat(str(last_seen).replace('Z', '+00:00'))
            age = (datetime.now(timezone.utc) - seen_dt).total_seconds()
            if age > OFFLINE_AFTER_SECONDS:
                freshness_status = 'offline'
            elif age > STALE_AFTER_SECONDS and freshness_status == 'reachable':
                freshness_status = 'stale'
            reachable = freshness_status == 'reachable'
        except Exception:
            pass
    return {'peer_id': peer_id, 'peer_name': peer_name or peer_id, 'pairing_status': pairing_status or 'unknown', 'status': freshness_status, 'reachable': reachable, 'last_seen': last_seen, 'paired_at': paired_at, 'host': host, 'http_port': http_port, 'quic_port': quic_port, 'via': via or 'peer_store', 'metadata': metadata}


def merge_metadata(existing_row, metadata: dict[str, Any]) -> dict[str, Any]:
    merged = metadata or {}
    if existing_row:
        try:
            merged = json.loads(existing_row[0] or '{}')
        except Exception:
            merged = {}
        merged.update(metadata or {})
    return merged
