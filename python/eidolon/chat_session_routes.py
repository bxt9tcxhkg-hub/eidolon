from __future__ import annotations

from fastapi import FastAPI

from eidolon.chat_route_support import operate_overview_from_context, session_payload
from eidolon.chat_turn_status import snapshot_chat_turn


def register_chat_session_routes(app: FastAPI, *, chat_session_store, latest_session_user_message, chat_runtime_payload) -> None:
    @app.get('/chat/turn-status')
    async def chat_turn_status(session_id: str | None = None):
        return {'ok': True, **snapshot_chat_turn(session_id)}

    @app.get('/chat/context')
    async def chat_context(session_id: str | None = None):
        session = chat_session_store.get_session(session_id) if session_id else None
        source = str((session or {}).get('source') or 'chat')
        message = latest_session_user_message(session)
        session, runtime_context = session_payload(chat_session_store, session_id, source, message, chat_runtime_payload)
        return {
            'ok': True,
            'session_id': (session or {}).get('session_id'),
            'runtime_context': runtime_context,
            'operate_overview': operate_overview_from_context(runtime_context),
        }

    @app.get('/chat/sessions')
    async def list_chat_sessions():
        return {'ok': True, 'sessions': chat_session_store.list_sessions()}

    @app.post('/chat/sessions')
    async def create_chat_session(request: dict | None = None):
        request = request or {}
        session = chat_session_store.create_session(title=request.get('title'), source=str(request.get('source') or 'chat'))
        return {'ok': True, 'session': session}

    @app.get('/chat/sessions/{session_id}')
    async def get_chat_session(session_id: str):
        session = chat_session_store.get_session(session_id)
        return {'ok': True, 'session': session} if session else {'ok': False, 'error': 'Chat-Session nicht gefunden', 'session_id': session_id}

    @app.delete('/chat/sessions/{session_id}')
    async def delete_chat_session(session_id: str):
        deleted = chat_session_store.delete_session(session_id)
        return {'ok': True, 'deleted': True, 'session_id': session_id} if deleted else {'ok': False, 'error': 'Chat-Session nicht gefunden', 'session_id': session_id}
