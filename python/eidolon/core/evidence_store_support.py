from __future__ import annotations

import sqlite3
from pathlib import Path

from eidolon.core.config import EVIDENCE_DB


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute('PRAGMA journal_mode=WAL')
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(db_path: Path) -> None:
    with connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                exit_code INTEGER,
                stdout TEXT,
                stderr TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id INTEGER,
                kind TEXT NOT NULL,
                description TEXT NOT NULL,
                detail TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (action_id) REFERENCES actions(id)
            );
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id INTEGER,
                path TEXT NOT NULL,
                sha256 TEXT,
                size_bytes INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (action_id) REFERENCES actions(id)
            );
            CREATE TABLE IF NOT EXISTS verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id INTEGER,
                claim TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('verified', 'inferred', 'unverified', 'blocked')),
                evidence TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (action_id) REFERENCES actions(id)
            );
            CREATE TABLE IF NOT EXISTS blocked_reasons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim TEXT NOT NULL,
                reason TEXT NOT NULL,
                capability TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        conn.commit()


def default_db_path() -> Path:
    return EVIDENCE_DB
