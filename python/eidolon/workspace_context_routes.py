from __future__ import annotations

from fastapi import FastAPI, HTTPException

from eidolon.workspace_route_helpers import execution_payload, kernel_payload, require_workspace


def register_workspace_context_routes(app: FastAPI, *, workspace_ui_service, workspace_service) -> None:
    @app.get('/workspaces')
    async def workspaces_overview():
        return workspace_ui_service().get_overview()

    @app.get('/workspaces/context')
    async def workspaces_context():
        return workspace_ui_service().get_overview().get('context_model', {})

    @app.get('/workspaces/{workspace_id}')
    async def workspaces_get(workspace_id: str):
        return {'workspace': require_workspace(workspace_ui_service, workspace_id)}

    @app.get('/workspaces/{workspace_id}/orchestration')
    async def workspaces_orchestration(workspace_id: str):
        workspace = require_workspace(workspace_ui_service, workspace_id)
        return {'ok': True, 'workspace_id': workspace_id, 'orchestration': ((workspace.get('state_data') or {}).get('orchestration') or {})}

    @app.get('/assist/proactive')
    async def assist_proactive():
        payload = workspace_ui_service().get_runtime_payload()
        proactive = payload.get('proactive_assistance', {})
        return {'ok': True, **proactive} if isinstance(proactive, dict) else {'ok': True, 'suggestions': [], 'policy': {}}

    @app.get('/workspaces/tasks')
    async def workspaces_tasks(domain: str | None = None, status: str | None = None):
        return {'tasks': workspace_service().list_tasks(domain=domain, status=status)}

    @app.get('/workspaces/tasks/{task_id}')
    async def workspaces_get_task(task_id: str):
        return workspace_service().get_task(task_id)

    @app.get('/workspaces/tasks/{task_id}/allowed-transitions')
    async def workspaces_allowed_transitions(task_id: str):
        return {'transitions': workspace_service().allowed_transitions(task_id)}

    @app.get('/workspaces/tasks/{task_id}/dependencies')
    async def workspaces_dependency_status(task_id: str):
        return workspace_service().get_dependency_status(task_id)

    @app.get('/workspaces/next-best-action')
    async def workspaces_next_best_action(domain: str = 'project'):
        return workspace_service().next_best_action(domain)

    @app.get('/workspaces/stats/{domain}')
    async def workspaces_stats(domain: str):
        return workspace_service().get_stats(domain)
