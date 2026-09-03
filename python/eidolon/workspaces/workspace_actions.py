from __future__ import annotations

from typing import Any

from eidolon.workspaces.workspace_action_evidence import record_workspace_evidence
from eidolon.workspaces.workspace_action_mutations import apply_project_workspace_action
from eidolon.workspaces.workspace_action_support import clean_selection_payload, require_project
from eidolon.workspaces.workspace_support import project_summary


def execute_workspace_action(*, project_service, project_to_workspace_record, operate_service, workspace_id: str, module_id: str, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    project = require_project(project_service, workspace_id)
    elements = list(project.elements or [])
    before_summary = project_summary(project)
    result: dict[str, Any] = {'workspace_id': workspace_id, 'module_id': module_id, 'action': action, 'project_id': project.id, 'before_summary': before_summary}
    changed, result = apply_project_workspace_action(project_service, project, module_id, action, payload, result, elements)
    refreshed = project_service.get_project(project.id)
    workspace = project_to_workspace_record(refreshed) if refreshed else None
    after_summary = project_summary(refreshed) if refreshed else None
    clean_payload, selection_reason, selection_score, selection_source = clean_selection_payload(payload)
    evidence_info, operate = record_workspace_evidence(operate_service=operate_service, workspace=workspace, workspace_id=workspace_id, module_id=module_id, action=action, clean_payload=clean_payload, changed=changed, before_summary=before_summary, after_summary=after_summary, element_id=result.get('element_id'), selection_reason=selection_reason, selection_score=selection_score)
    result.update({'ok': bool(changed), 'workspace': workspace, 'after_summary': after_summary, 'changed': bool(changed), 'selection_reason': selection_reason, 'selection_score': selection_score, 'selection_source': selection_source, 'evidence': {**evidence_info, 'selection_reason': selection_reason, 'selection_score': selection_score}, 'change_summary': {'before_total': before_summary.get('total'), 'after_total': (after_summary or {}).get('total'), 'before_ready': before_summary.get('ready'), 'after_ready': (after_summary or {}).get('ready'), 'before_dependencies': before_summary.get('dependencies'), 'after_dependencies': (after_summary or {}).get('dependencies')}, 'operate': operate})
    return result
