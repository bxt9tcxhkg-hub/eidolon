from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Callable

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from eidolon.llm_routes import register_llm_routes


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
    register_llm_routes(
        app,
        get_llm_backend=get_llm_backend,
        get_settings_store=get_settings_store,
        get_ollama_models=get_ollama_models,
        get_openai_models=get_openai_models,
        get_openai_login_payload=get_openai_login_payload,
    )
    def workspace_ui_service():
        return get_workspace_ui_service()
    def voice_runtime_service():
        return get_voice_runtime_service()

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
