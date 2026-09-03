from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

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


def map_workspace_state_to_product_state(runtime_state: str | None, topic: dict[str, Any] | None = None) -> str:
    state = str(runtime_state or 'suggested')
    if state == 'active':
        return 'active_project'
    topic = topic or {}
    action = float(topic.get('action_relevance', 0) or 0)
    recurrence = float(topic.get('recurrence_score', 0) or 0)
    if action >= 0.45 or recurrence >= 0.3:
        return 'project_candidate'
    return 'chat_topic'


def build_workspace_semantic_frame(workspace: dict[str, Any], state_data: dict[str, Any]) -> dict[str, Any]:
    metadata = workspace.get('metadata') or {}
    product_state = map_workspace_state_to_product_state(workspace.get('state'), metadata)
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
