from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal, Optional


@dataclass
class WorkSessionRecord:
    id: str
    title: str
    status: Literal['active', 'idle', 'archived']
    current_run_id: str | None
    current_objective_id: str | None
    current_view: Literal['operate', 'work_graph', 'history', 'settings']
    source_kind: Literal['chat', 'ui', 'api']
    created_at: str
    updated_at: str
    context_kind: Literal['chat_topic', 'project_candidate', 'active_project'] = 'chat_topic'
    entry_message_id: Optional[str] = None
    linked_workspace_id: Optional[str] = None
    surface_reason: Optional[str] = None
    def to_dict(self) -> dict[str, Any]: return asdict(self)


@dataclass
class ObjectiveRecord:
    id: str
    session_id: str
    title: str
    user_request: str
    normalized_goal: str
    scope_summary: str
    decomposition_mode: Literal['single_stream', 'multi_stream', 'undecided']
    status: Literal['draft', 'active', 'completed', 'failed', 'cancelled']
    created_at: str
    updated_at: str
    candidate_source: Optional[str] = None
    acceptance_state: Literal['pending', 'accepted', 'rejected'] = 'pending'
    goal_confidence: float = 0.0
    clarification_completeness: float = 0.0
    linked_project_id: Optional[str] = None
    def to_dict(self) -> dict[str, Any]: return asdict(self)
