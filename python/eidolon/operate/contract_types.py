from __future__ import annotations

from typing import Literal

from eidolon.domain.mission.contracts import AgentRunPhase, AgentRunState

SubAgentFunctionType = Literal['research', 'builder', 'verifier', 'monitor', 'reconciler', 'planner', 'operator', 'resolver', 'executor']
SubAgentRunState = Literal['queued', 'running', 'waiting', 'blocked', 'completed', 'failed', 'cancelled']
ResultStatus = Literal['success', 'warning', 'failure']
NextActionKind = Literal['next_step', 'approval_request', 'blocking_condition', 'none']
EvidenceOwnerType = Literal['run', 'subagent', 'objective']
EvidenceKind = Literal['file_change', 'test_result', 'command_output', 'web_source', 'api_result', 'log_excerpt', 'diff', 'artifact', 'verification_report', 'workspace_context', 'workspace_mutation']
BlockingOwnerType = Literal['run', 'subagent']
BlockingCategory = Literal['approval', 'credential', 'dependency', 'runtime_error', 'external_system', 'validation']
ApprovalActionType = Literal['deploy', 'publish', 'delete', 'external_write', 'permission', 'other']
TransitionActorType = Literal['run', 'subagent']
TransitionType = Literal['state_change', 'spawned', 'interrupted', 'approved', 'rejected', 'blocked', 'resumed', 'completed', 'failed', 'cancelled']


SPECIALIST_FAMILIES: tuple[str, ...] = (
    'planner',
    'research',
    'builder',
    'verifier',
    'resolver',
    'operator',
    'monitor',
    'reconciler',
)


def is_specialist_family(function_type: str | None) -> bool:
    return function_type in SPECIALIST_FAMILIES


def is_generic_execution_record(function_type: str | None) -> bool:
    return function_type == 'executor'
