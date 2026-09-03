from __future__ import annotations

from pathlib import Path

from eidolon.core.auth_store_keys import create_api_key, delete_api_key, get_api_key_by_hash, get_api_keys_for_user
from eidolon.core.auth_store_support import auth_db_path, connect, init_db
from eidolon.core.auth_store_users import cleanup_expired_sessions, create_session, create_user, delete_session, delete_user, get_session, get_user, get_user_by_username, list_users, update_session, update_user


class AuthStore:
    def __init__(self, project_root: Path):
        self._db_path = auth_db_path(project_root)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        init_db(self._db_path)

    def _connect(self):
        return connect(self._db_path)

    def create_user(self, user) -> None: create_user(self, user)
    def get_user(self, user_id: str): return get_user(self, user_id)
    def get_user_by_username(self, username: str): return get_user_by_username(self, username)
    def update_user(self, user) -> None: update_user(self, user)
    def delete_user(self, user_id: str) -> None: delete_user(self, user_id)
    def list_users(self): return list_users(self)
    def create_session(self, session) -> None: create_session(self, session)
    def get_session(self, session_id: str): return get_session(self, session_id)
    def update_session(self, session) -> None: update_session(self, session)
    def delete_session(self, session_id: str) -> None: delete_session(self, session_id)
    def cleanup_expired_sessions(self) -> int: return cleanup_expired_sessions(self)
    def create_api_key(self, api_key) -> None: create_api_key(self, api_key)
    def get_api_key_by_hash(self, key_hash: str): return get_api_key_by_hash(self, key_hash)
    def get_api_keys_for_user(self, user_id: str): return get_api_keys_for_user(self, user_id)
    def delete_api_key(self, key_id: str) -> None: delete_api_key(self, key_id)
