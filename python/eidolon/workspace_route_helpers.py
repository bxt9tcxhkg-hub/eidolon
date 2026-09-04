from __future__ import annotations

from fastapi import HTTPException


def require_workspace(workspace_ui_service, workspace_id: str):
    workspace = workspace_ui_service().get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail='Nicht gefunden')
    return workspace


def kernel_payload(workspace_ui_service, result):
    truth = workspace_ui_service().get_work_truth()
    return {**result, 'data': {'result': result, **truth}}


def execution_payload(workspace_ui_service, result):
    truth = workspace_ui_service().get_work_truth()
    return {**result, 'data': {'workspace_execution': result, 'operate': result.get('operate') or truth.get('operate'), 'work_kernel': truth.get('work_kernel'), 'formation': truth.get('formation'), 'generic_slots': truth.get('generic_slots')}}
