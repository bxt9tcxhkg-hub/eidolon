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
    active = next((item for item in workspaces if item.get('product_state') == 'active_project'), None)
    focus = target or active
    needs_confirm = bool(from_state and to_state and requires_confirmation(from_state, to_state))
    session = (operate_snapshot or {}).get('session') or {}
    metadata = (focus or {}).get('metadata') or {}
    label = (focus or {}).get('topic_label') or context_model.get('current_focus_label')
    why = metadata.get('why') or (
        'Erst mit deiner Bestätigung wird daraus ein dauerhaftes Projekt.'
        if needs_confirm else
        'Das Thema kann als Kandidat gemerkt werden, ohne still ein Projekt anzulegen.'
        if proposed == 'structure_topic_into_candidate' else
        ''
    )
    board_items = ((((focus or {}).get('state_data') or {}).get('module_data') or {}).get('board') or {}).get('items') or []
    formation_proposed = proposed in {'promote_candidate_to_project', 'structure_topic_into_candidate'}
    can_seed_board = current_state == 'active_project' and bool(active) and not board_items and not formation_proposed
    return {
        'current_state': current_state,
        'from_state': from_state,
        'to_state': to_state or ('active_project' if can_seed_board else None),
        'proposed_transition': proposed if formation_proposed else ('seed_board_from_vorhaben' if can_seed_board else None),
        'requires_confirmation': needs_confirm or can_seed_board,
        'creates_durable_project': bool(from_state and to_state and creates_durable_project(from_state, to_state)),
        'workspace_id': (focus or {}).get('workspace_id'),
        'label': label,
        'summary': metadata.get('project_description') or (focus or {}).get('overview') or '',
        'why': why,
        'visible': bool((formation_proposed and focus) or can_seed_board),
        'action_enabled': bool((focus and formation_proposed) or can_seed_board),
        'action_label': (
            'Ins Board übernehmen' if can_seed_board else
            'Ja, übernehmen' if needs_confirm else
            ('Als Kandidat merken' if proposed == 'structure_topic_into_candidate' else None)
        ),
        'decline_label': 'Nein, nur im Chat' if needs_confirm else None,
        'decline_to_state': 'chat_topic' if needs_confirm and from_state == 'project_candidate' else None,
        'seed_board': bool(needs_confirm or can_seed_board),
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
