from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from eidolon.workspaces.project_formation import map_workspace_state_to_product_state, propose_product_state

CORE_LOCKED_AREAS = [
    'core-nav',
    'core-topbar',
    'core-status',
    'core-chat',
    'core-dashboard',
    'core-settings',
]

PRODUCT_CONTEXT_STATES = ['chat_topic', 'project_candidate', 'active_project']
CONTEXT_SHIFT_STATES = ['same_project', 'possible_project_shift', 'confirmed_project_shift']


def build_workspace_semantic_frame(workspace: dict[str, Any], state_data: dict[str, Any]) -> dict[str, Any]:
    metadata = workspace.get('metadata') or {}
    stored = workspace.get('product_state') or metadata.get('product_state') or metadata.get('stored_product_state')
    product_state = stored if stored in PRODUCT_CONTEXT_STATES else propose_product_state(workspace.get('state'), metadata, stored_product_state=stored)
    orchestration = (state_data or {}).get('orchestration') or {}
    next_best = orchestration.get('next_best_action') or {}
    details = ((state_data or {}).get('module_data') or {}).get('details') or {}
    selected = details.get('selected_item') or {}
    owner = selected.get('owner') or 'eidolon'
    object_state = selected.get('status') or state_data.get('status') or workspace.get('state') or 'prepared'
    next_actions = (state_data or {}).get('next_actions') or []
    primary_goal = next_best.get('label') or (next_actions[0] if next_actions else f"{workspace.get('topic_label', 'Kontext')} konkretisieren")
    interaction_type = 'conversation' if product_state == 'chat_topic' else 'workspace'
    permission_state = 'approval_required' if product_state == 'project_candidate' else 'within_guardrails'
    return {
        'active_context': product_state,
        'primary_goal': primary_goal,
        'object_state': object_state,
        'owner': owner,
        'interaction_type': interaction_type,
        'change_state': 'derived',
        'permission_state': permission_state,
        'next_recommended_action': next_best,
        'return_anchor': 'chat',
    }


@dataclass
class WorkspaceModuleContract:
    workspace_id: str
    topic_label: str
    workspace_type: str
    layout_template: str
    modules: list[str]
    render_slot: str = 'adaptive-workspace-host'
    feature_flag: str = 'workspace_adaptive_modules'
    safe_mode: str = 'sandboxed'
    mutable_core_areas: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


__all__ = [
    'CORE_LOCKED_AREAS',
    'PRODUCT_CONTEXT_STATES',
    'CONTEXT_SHIFT_STATES',
    'map_workspace_state_to_product_state',
    'propose_product_state',
    'build_workspace_semantic_frame',
    'WorkspaceModuleContract',
]
