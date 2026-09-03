from __future__ import annotations

from fastapi import FastAPI

from eidolon.routes.api_response import api_v1_ok


def register_operate_session_routes(app: FastAPI, *, runtime, get_operate_service, workspace_ui_service) -> None:
    @app.get('/api/v1/session/current')
    async def api_v1_current_session():
        runtime.ensure_operate_bootstrap_from_workspace()
        service = get_operate_service()
        session = service.get_current_session()
        return api_v1_ok({'session': session.to_dict() if session else None})

    @app.post('/api/v1/session/sync-from-workspaces')
    async def api_v1_sync_from_workspaces():
        service = get_operate_service()
        from eidolon.operate.bridge import sync_operate_with_workspace_payload
        from eidolon.operate.bridge_snapshot import build_operate_snapshot
        synced = sync_operate_with_workspace_payload(service, workspace_ui_service.get_runtime_payload())
        if synced is None:
            return api_v1_ok({'session': None, 'objective': None, 'run': None, 'subagents': []})
        return api_v1_ok(build_operate_snapshot(service, synced['run'].id))
