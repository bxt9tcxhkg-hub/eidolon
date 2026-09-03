from __future__ import annotations

import json
import sqlite3

from eidolon.core.auth_models import ApiKey, Role, Session, User


def row_to_user(row: sqlite3.Row) -> User:
    return User(user_id=row['user_id'], username=row['username'], password_hash=row['password_hash'], role=Role(row['role']), display_name=row['display_name'], email=row['email'], created_at=row['created_at'], updated_at=row['updated_at'], last_login_at=row['last_login_at'], is_active=bool(row['is_active']), failed_login_attempts=row['failed_login_attempts'], locked_until=row['locked_until'])


def row_to_session(row: sqlite3.Row) -> Session:
    return Session(session_id=row['session_id'], user_id=row['user_id'], created_at=row['created_at'], expires_at=row['expires_at'], last_activity=row['last_activity'], ip_address=row['ip_address'], user_agent=row['user_agent'])


def row_to_api_key(row: sqlite3.Row) -> ApiKey:
    return ApiKey(key_id=row['key_id'], user_id=row['user_id'], key_hash=row['key_hash'], key_prefix=row['key_prefix'], name=row['name'], scopes=json.loads(row['scopes']), created_at=row['created_at'], expires_at=row['expires_at'], last_used_at=row['last_used_at'], is_active=bool(row['is_active']))
