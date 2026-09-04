from __future__ import annotations

from typing import Any

from eidolon.workspaces.generic_slots import build_generic_slots
from eidolon.workspaces.project_formation import creates_durable_project, requires_confirmation


def describe_formation(workspace_payload: dict[str, Any] | None, operate_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = workspace_payload or {}
    context_model = payload.get('context_model') or {}
    workspaces = list(payload.get('workspaces') or [])
    current_state = context_model.get('current_context_state') or 'no_live_context'
    proposed = context_model.get('next_transition')
    target = None
    if proposed == 'promote_candidate_to_project':
        target = next((item for item in workspaces if item.get('product_state') == 'project_candidate'), None)
        to_state = 'active_project'
        from_state = 'project_candidate'
    elif proposed == 'structure_topic_into_candidate':
        target = next((item for item in workspaces if item.get('product_state') == 'chat_topic'), None)
        to_state = 'project_candidate'
        from_state = 'chat_topic'
    else:
        to_state = None
        from_state = current_state
    needs_confirm = bool(from_state and to_state and requires_confirmation(from_state, to_state))
    session = (operate_snapshot or {}).get('session') or {}
    return {
        'current_state': current_state,
        'from_state': from_state,
        'to_state': to_state,
        'proposed_transition': proposed,
        'requires_confirmation': needs_confirm,
        'creates_durable_project': bool(from_state and to_state and creates_durable_project(from_state, to_state)),
        'workspace_id': (target or {}).get('workspace_id'),
        'label': (target or {}).get('topic_label') or context_model.get('current_focus_label'),
        'visible': bool(proposed),
        'action_enabled': bool(target and proposed),
        'action_label': 'Als Projekt übernehmen' if needs_confirm else ('Als Kandidat merken' if proposed == 'structure_topic_into_candidate' else None),
        'operate_context_kind': session.get('context_kind'),
        'approval_state': context_model.get('approval_state'),
    }


def work_truth_fields(overview: dict[str, Any], *, project: dict[str, Any] | None = None) -> dict[str, Any]:
    operate = overview.get('operate') or {}
    work_kernel = overview.get('work_kernel') or {}
    formation = work_kernel.get('formation') or describe_formation(overview, operate)
    slots = build_generic_slots(project=project, work_kernel=work_kernel, operate=operate)
    return {
        'operate': operate,
        'work_kernel': work_kernel,
        'formation': formation,
        'generic_slots': slots,
    }
