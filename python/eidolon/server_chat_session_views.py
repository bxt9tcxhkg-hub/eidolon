from __future__ import annotations

from eidolon.server_chat_session_models import infer_title_from_message, new_session, now_iso
from eidolon.server_chat_session_store import find_session


def list_sessions_payload(sessions: list[dict]) -> list[dict]:
    items = sorted(sessions, key=lambda s: s.get('updated_at') or '', reverse=True)
    result = []
    for session in items:
        messages = session.get('messages') or []
        last_message = messages[-1] if messages else None
        result.append({'session_id': session.get('session_id'), 'title': session.get('title') or 'Neue Unterhaltung', 'source': session.get('source') or 'chat', 'created_at': session.get('created_at'), 'updated_at': session.get('updated_at'), 'message_count': int(session.get('message_count') or len(messages)), 'last_message_preview': (last_message or {}).get('content', '')[:120]})
    return result


def session_payload(session: dict) -> dict:
    return {'session_id': session.get('session_id'), 'title': session.get('title') or 'Neue Unterhaltung', 'source': session.get('source') or 'chat', 'created_at': session.get('created_at'), 'updated_at': session.get('updated_at'), 'message_count': int(session.get('message_count') or len(session.get('messages') or [])), 'messages': list(session.get('messages') or [])}


def append_message_to_session(store, session_id: str, role: str, content: str, source: str | None = None):
    session = find_session(store._sessions, session_id)
    if not session:
        return None
    normalized_role = role if role in {'user', 'assistant'} else 'assistant'
    text = str(content or '').strip()
    entry = {'role': normalized_role, 'content': text, 'created_at': now_iso()}
    messages = list(session.get('messages') or [])
    messages.append(entry)
    session['messages'] = messages[-store._max_messages:]
    session['message_count'] = len(session['messages'])
    session['updated_at'] = entry['created_at']
    if source:
        session['source'] = source
    if normalized_role == 'user' and session.get('title') == 'Neue Unterhaltung':
        session['title'] = infer_title_from_message(text)
    store._save()
    return entry


def ensure_session(store, session_id: str | None, source: str = 'chat', title: str | None = None):
    if session_id:
        existing = find_session(store._sessions, session_id)
        if existing:
            return existing
    created = store.create_session(title=title, source=source)
    return find_session(store._sessions, created['session_id']) or created
