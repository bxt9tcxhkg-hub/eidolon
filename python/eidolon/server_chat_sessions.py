from __future__ import annotations

from pathlib import Path
from typing import Any

from eidolon.chat_error_support import prune_synthetic_chat_sessions, scrub_chat_sessions
from eidolon.core.config import state_path
from eidolon.server_chat_session_models import new_session
from eidolon.server_chat_session_store import find_session, load_sessions, save_sessions
from eidolon.server_chat_session_views import append_message_to_session, ensure_session, list_sessions_payload, session_payload


class ChatSessionStore:
    def __init__(self, project_root: Path, max_messages_per_session: int = 200):
        self._path = state_path('user', 'chat_sessions.json', project_root=project_root)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._max_messages = max(10, int(max_messages_per_session))
        self._sessions: list[dict[str, Any]] = load_sessions(self._path)
        changed = False
        if prune_synthetic_chat_sessions(self._sessions):
            changed = True
        if scrub_chat_sessions(self._sessions):
            changed = True
        if changed:
            self._save()

    def _save(self) -> None:
        save_sessions(self._path, self._sessions)

    def _find_session(self, session_id: str) -> dict[str, Any] | None:
        return find_session(self._sessions, session_id)

    def create_session(self, title: str | None = None, source: str = 'chat') -> dict[str, Any]:
        session = new_session(title=title, source=source)
        self._sessions.insert(0, session)
        self._save()
        return self.get_session(session['session_id'])

    def list_sessions(self) -> list[dict[str, Any]]:
        return list_sessions_payload(self._sessions)

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        session = self._find_session(session_id)
        return session_payload(session) if session else None

    def ensure_session(self, session_id: str | None, source: str = 'chat', title: str | None = None) -> dict[str, Any]:
        return ensure_session(self, session_id, source=source, title=title)

    def append_message(self, session_id: str, role: str, content: str, source: str | None = None) -> dict[str, Any] | None:
        return append_message_to_session(self, session_id, role, content, source)

    def delete_session(self, session_id: str) -> bool:
        session = self._find_session(session_id)
        if not session:
            return False
        self._sessions.remove(session)
        self._save()
        return True
