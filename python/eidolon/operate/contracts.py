from __future__ import annotations

from eidolon.domain.mission.contracts import AgentRunPhase, AgentRunState
from eidolon.operate.contract_records import AgentRunRecord, ApprovalGateRecord, BlockingIssueRecord, EvidenceItemRecord, NextActionRecord, ObjectiveRecord, SubAgentRunRecord, TransitionEventRecord, WorkSessionRecord
from eidolon.operate.contract_transitions import RUN_TRANSITIONS, SUBAGENT_TRANSITIONS, is_valid_run_transition, is_valid_subagent_transition
from eidolon.operate.contract_types import ApprovalActionType, BlockingCategory, BlockingOwnerType, EvidenceKind, EvidenceOwnerType, NextActionKind, ResultStatus, SubAgentFunctionType, SubAgentRunState, TransitionActorType, TransitionType
