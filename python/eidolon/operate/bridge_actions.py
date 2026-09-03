from __future__ import annotations

from typing import Any

from eidolon.operate.bridge_snapshot import build_operate_snapshot
from eidolon.operate.bridge_sync import sync_operate_with_workspace_payload
from eidolon.operate.bridge_workspace import align_run_state_from_summary


def record_workspace_action(service, payload: dict[str, Any] | None, workspace_id: str, module_id: str, action: str, mutation_payload: dict[str, Any] | None, changed: bool, before_summary: dict[str, Any], after_summary: dict[str, Any] | None, element_id: str | None = None, selection_reason: str | None = None) -> dict[str, Any] | None:
    synced = sync_operate_with_workspace_payload(service, payload)
    if synced is None:
        return None
    run = synced['run']
    mission = f'{module_id}.{action} on {workspace_id}'
    subagent = service.spawn_subagent_run(run_id=run.id, display_name='Workspace Action', function_type=f'{module_id}:{action}', mission=mission, state_reason='Workspace action registered in operate kernel', assigned_by='workspace_ui')
    service.set_subagent_state(subagent.id, 'running', 'Workspace mutation is executing')
    service.emit_evidence(owner_type='subagent', owner_id=subagent.id, kind='workspace_mutation', title=mission, summary=str({'element_id': element_id, 'changed': changed, 'selection_reason': selection_reason, 'payload': mutation_payload or {}, 'before': before_summary, 'after': after_summary}), metadata_json={'workspace_id': workspace_id, 'module_id': module_id, 'action': action, 'element_id': element_id, 'changed': changed})
    if changed:
        service.set_subagent_state(subagent.id, 'completed', 'Workspace mutation verified', result_status='success')
    else:
        service.set_subagent_state(subagent.id, 'failed', selection_reason or 'Workspace mutation produced no state change', result_status='failure')
    if after_summary:
        align_run_state_from_summary(service, run.id, after_summary)
    return build_operate_snapshot(service, run.id)
