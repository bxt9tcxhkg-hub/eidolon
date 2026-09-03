from __future__ import annotations

import sqlite3
from pathlib import Path

from eidolon.core.config import state_path


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                display_name TEXT DEFAULT '',
                email TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_login_at TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                ip_address TEXT DEFAULT '',
                user_agent TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                key_hash TEXT NOT NULL,
                key_prefix TEXT NOT NULL,
                name TEXT DEFAULT '',
                scopes TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                expires_at TEXT DEFAULT '',
                last_used_at TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)


def auth_db_path(project_root: Path) -> Path:
    return state_path('auth', 'auth.db', project_root=project_root)
