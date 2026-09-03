from __future__ import annotations

import json


def load_sessions(path) -> list[dict]:
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            sessions = data.get('sessions', [])
            if isinstance(sessions, list):
                return [s for s in sessions if isinstance(s, dict) and s.get('session_id')]
        except Exception:
            pass
    return []


def save_sessions(path, sessions: list[dict]) -> None:
    path.write_text(json.dumps({'sessions': sessions}, indent=2, ensure_ascii=False), encoding='utf-8')


def find_session(sessions: list[dict], session_id: str):
    return next((s for s in sessions if s.get('session_id') == session_id), None)
