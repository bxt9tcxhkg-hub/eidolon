from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Callable

from fastapi import FastAPI, WebSocket, WebSocketDisconnect


def register_system_status_routes(
    app: FastAPI,
    *,
    server_start: float,
    get_llm_backend: Callable[[], Any],
    get_settings_store: Callable[[], Any],
    get_workspace_ui_service: Callable[[], Any],
    get_voice_runtime_service: Callable[[], Any],
    get_ollama_models: Callable[[str], Any],
    get_openai_models: Callable[[], Any],
    get_openai_login_payload: Callable[[], Callable[[], dict[str, Any]]],
) -> None:
    def llm_backend():
        return get_llm_backend()
    def settings_store():
        return get_settings_store()
    def workspace_ui_service():
        return get_workspace_ui_service()
    def voice_runtime_service():
        return get_voice_runtime_service()

    @app.get('/llm/connection')
    async def llm_connection_status():
        status = llm_backend().status()
        return {'ok': True, **status}

    @app.get('/llm/models')
    async def llm_models():
        return {
            'ok': True,
            'ollama': get_ollama_models(llm_backend().status().get('ollama_url') or settings_store().get_area('llm').get('ollama_url') or 'http://127.0.0.1:11434'),
            'openai': get_openai_models(),
        }

    @app.post('/integrations/openai/auth')
    async def integrations_openai_auth():
        openai = dict(llm_backend().status().get('openai') or {})
        return {'ok': True, 'supported': True, 'provider': 'openai', 'auth_method': 'chatgpt_login', **openai}

    @app.post('/integrations/openai/login')
    async def integrations_openai_login():
        return get_openai_login_payload()()

    @app.get('/integrations/status')
    async def integrations_status():
        llm = llm_backend().status()
        openai = dict(llm.get('openai') or {})
        openai['current_provider'] = llm.get('provider') in ('openai', 'openai_oauth')
        return {'ok': True, 'integrations': {'openai': openai, 'ollama': {'configured': llm.get('provider') == 'ollama', 'url': llm.get('ollama_url')}}}

    @app.get('/runtime/process')
    async def runtime_process():
        return {'ok': True, 'server_pid': os.getpid(), 'lifecycle': {'status': 'running', 'started_at': datetime.fromtimestamp(server_start, timezone.utc).isoformat()}}

    @app.get('/evidence/summary')
    async def evidence_summary():
        payload = workspace_ui_service().get_runtime_payload()
        blocked_reasons = []
        recent_actions = []
        for ws in payload.get('workspaces', []):
            state_data = ws.get('state_data') or {}
            summary = (((state_data.get('module_data') or {}).get('board') or {}).get('summary') or {})
            for item in summary.get('blocked_items', []) or []:
                reason = item.get('blocker_reason') or item.get('reason') or item.get('label')
                if reason:
                    blocked_reasons.append(str(reason))
            for action in state_data.get('next_actions', []) or []:
                recent_actions.append(str(action))
        return {'ok': True, 'recent_actions': recent_actions[:10], 'blocked_reasons': blocked_reasons[:10]}

    @app.get('/voice/status')
    async def voice_status():
        return voice_runtime_service().status()

    @app.websocket('/ws')
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                await websocket.send_json({'type': 'echo', 'data': data})
        except WebSocketDisconnect:
            pass
