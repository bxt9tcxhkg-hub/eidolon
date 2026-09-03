from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from eidolon.core.config import MESH_PEERS_DB


def connect(db_path: Path):
    return sqlite3.connect(db_path)


def init_schema(db_path: Path) -> None:
    sql = (
        'CREATE TABLE IF NOT EXISTS peers ('
        'peer_id TEXT PRIMARY KEY, '
        'peer_name TEXT, '
        'pairing_status TEXT, '
        'connection_status TEXT, '
        'last_seen TEXT, '
        'paired_at TEXT, '
        'host TEXT, '
        'http_port INTEGER, '
        'quic_port INTEGER, '
        'via TEXT, '
        'metadata_json TEXT NOT NULL)'
    )
    with connect(db_path) as conn:
        conn.execute(sql)
        conn.commit()


def default_db_path() -> Path:
    return Path(MESH_PEERS_DB)


def default_lock() -> threading.Lock:
    return threading.Lock()
