from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal, Optional

from eidolon.domain.mission.contracts import AgentRunPhase, AgentRunState
from eidolon.operate.contract_types import ResultStatus, SubAgentFunctionType, SubAgentRunState


@dataclass
class AgentRunRecord:
    id: str
    session_id: str
    objective_id: str
    state: AgentRunState
    state_reason: str
    current_phase: AgentRunPhase
    next_transition: AgentRunPhase | None
    autonomy_mode: Literal['manual', 'bounded_autonomous', 'autonomous']
    approval_required: bool
    blocking_issue_id: str | None
    interruptible: bool
    pending_interrupt_count: int
    last_interrupt_at: str | None
    result_status: ResultStatus | None
    started_at: str
    updated_at: str
    ended_at: str | None
    product_phase: Optional[str] = None
    phase_provenance: Optional[str] = None
    completion_summary: Optional[str] = None
    current_owner: Literal['eidolon', 'child'] = 'eidolon'
    interrupt_classification: Optional[Literal['refine', 'conflict', 'supersede']] = None
    def to_dict(self) -> dict[str, Any]: return asdict(self)


@dataclass
class SubAgentRunRecord:
    id: str
    parent_run_id: str
    objective_id: str
    display_name: str
    function_type: SubAgentFunctionType
    mission: str
    state: SubAgentRunState
    state_reason: str
    assigned_by: Literal['system', 'user']
    blocking_issue_id: str | None
    evidence_count: int
    output_count: int
    result_status: ResultStatus | None
    started_at: str | None
    updated_at: str
    ended_at: str | None
    def to_dict(self) -> dict[str, Any]: return asdict(self)
