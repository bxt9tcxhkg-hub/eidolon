from __future__ import annotations

from fastapi import HTTPException


def require_workspace(workspace_ui_service, workspace_id: str):
    workspace = workspace_ui_service().get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail='Nicht gefunden')
    return workspace


def kernel_payload(workspace_ui_service, result):
    return {**result, 'data': {'result': result, 'operate': workspace_ui_service().get_runtime_payload().get('operate', {}), 'work_kernel': workspace_ui_service().get_unified_work_context(source='workspace')}}


def execution_payload(workspace_ui_service, result):
    return {**result, 'data': {'workspace_execution': result, 'operate': result.get('operate'), 'work_kernel': workspace_ui_service().get_unified_work_context(source='workspace')}}
