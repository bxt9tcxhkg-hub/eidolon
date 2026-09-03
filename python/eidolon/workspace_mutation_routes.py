from __future__ import annotations

from fastapi import FastAPI, HTTPException

from eidolon.workspace_route_helpers import execution_payload, kernel_payload, require_workspace


def register_workspace_mutation_routes(app: FastAPI, *, workspace_ui_service, workspace_service) -> None:
    @app.post('/workspaces/{workspace_id}/orchestration/execute')
    async def workspaces_orchestration_execute(workspace_id: str, request: dict | None = None):
        workspace = require_workspace(workspace_ui_service, workspace_id)
        request = request or {}
        orchestration = ((workspace.get('state_data') or {}).get('orchestration') or {})
        next_best = orchestration.get('next_best_action') or {}
        module_id = request.get('module_id') or next_best.get('module_id')
        action = request.get('action') or next_best.get('action')
        payload = request.get('payload') if isinstance(request.get('payload'), dict) else next_best.get('payload') or {}
        if not module_id or not action:
            raise HTTPException(status_code=400, detail='Keine ausführbare Workspace-Aktion vorhanden')
        try:
            result = workspace_ui_service().execute_workspace_action(workspace_id, module_id, action, payload)
            return execution_payload(workspace_ui_service, result)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post('/workspaces/{workspace_id}/orchestration/feedback')
    async def workspaces_orchestration_feedback(workspace_id: str, request: dict):
        state = require_workspace(workspace_ui_service, workspace_id)
        runtime = workspace_ui_service()._registry.orchestrator.memory
        if runtime is None:
            return {'ok': False, 'error': 'Learning deaktiviert'}
        data = state.get('state_data') or {}
        runtime.record_outcome(workspace_type=data.get('workspace_type', 'workspace'), module_id=str(request.get('module_id') or 'unknown'), action=str(request.get('action') or 'unknown'), success=bool(request.get('success', True)), metadata={'workspace_id': workspace_id, 'note': str(request.get('note') or '')})
        return {'ok': True, 'data': {'workspace_id': workspace_id, 'operate': workspace_ui_service().get_runtime_payload().get('operate', {}), 'work_kernel': workspace_ui_service().get_unified_work_context(source='workspace')}}

    @app.post('/workspaces/{workspace_id}/activate')
    async def workspaces_activate(workspace_id: str):
        return kernel_payload(workspace_ui_service, workspace_ui_service().activate_workspace(workspace_id))

    @app.post('/workspaces/{workspace_id}/suspend')
    async def workspaces_suspend(workspace_id: str):
        return kernel_payload(workspace_ui_service, workspace_ui_service().suspend_workspace(workspace_id))

    @app.post('/workspaces/feature-flag')
    async def workspaces_feature_flag(request: dict):
        return kernel_payload(workspace_ui_service, workspace_ui_service().set_feature_flag(request.get('enabled', True)))

    @app.post('/workspaces/propose')
    async def workspaces_propose():
        return kernel_payload(workspace_ui_service, workspace_ui_service().refresh())

    @app.post('/workspaces/tasks')
    async def workspaces_create_task(request: dict):
        try:
            return workspace_service().create_task(title=request.get('title', ''), description=request.get('description', ''), domain=request.get('domain', 'project'), priority=int(request.get('priority', 0)), dependencies=request.get('dependencies'), due_at=request.get('due_at', ''), tags=request.get('tags'))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.put('/workspaces/tasks/{task_id}')
    async def workspaces_update_task(task_id: str, request: dict):
        try:
            return workspace_service().update_task(task_id, **request)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.delete('/workspaces/tasks/{task_id}')
    async def workspaces_delete_task(task_id: str):
        return workspace_service().delete_task(task_id)

    @app.post('/workspaces/tasks/{task_id}/transition')
    async def workspaces_transition_task(task_id: str, request: dict):
        return workspace_service().transition_task(task_id, request.get('status', ''))

    @app.post('/workspaces/tasks/{task_id}/dependencies')
    async def workspaces_add_dependency(task_id: str, request: dict):
        return workspace_service().add_dependency(task_id, request.get('depends_on_id', ''))

    @app.delete('/workspaces/tasks/{task_id}/dependencies/{dep_id}')
    async def workspaces_remove_dependency(task_id: str, dep_id: str):
        return workspace_service().remove_dependency(task_id, dep_id)

    @app.post('/workspaces/tasks/{task_id}/blocker')
    async def workspaces_set_blocker(task_id: str, request: dict):
        return workspace_service().set_blocker(task_id, request.get('reason', ''))

    @app.post('/workspaces/tasks/{task_id}/resolve-blocker')
    async def workspaces_resolve_blocker(task_id: str):
        return workspace_service().resolve_blocker(task_id)
