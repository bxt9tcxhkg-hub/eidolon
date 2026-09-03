from __future__ import annotations

from eidolon.domain.mission.contracts import AgentRunState
from eidolon.operate.contract_types import SubAgentRunState

RUN_TRANSITIONS: dict[str, set[str]] = {
    'understanding': {'planning', 'waiting', 'blocked', 'failed', 'cancelled'},
    'planning': {'spawning_work', 'acting', 'waiting', 'blocked', 'failed', 'cancelled'},
    'spawning_work': {'acting', 'waiting', 'blocked', 'failed', 'cancelled'},
    'acting': {'waiting', 'blocked', 'verifying', 'failed', 'cancelled'},
    'waiting': {'planning', 'acting', 'blocked', 'cancelled', 'failed'},
    'blocked': {'planning', 'acting', 'cancelled', 'failed'},
    'verifying': {'completed', 'failed', 'blocked', 'cancelled'},
    'completed': set(),
    'failed': set(),
    'cancelled': set(),
}
SUBAGENT_TRANSITIONS: dict[str, set[str]] = {
    'queued': {'running', 'waiting', 'blocked', 'cancelled', 'failed'},
    'running': {'waiting', 'blocked', 'completed', 'failed', 'cancelled'},
    'waiting': {'running', 'blocked', 'failed', 'cancelled'},
    'blocked': {'running', 'failed', 'cancelled'},
    'completed': set(),
    'failed': set(),
    'cancelled': set(),
}


def is_valid_run_transition(from_state: AgentRunState | str, to_state: AgentRunState | str) -> bool:
    return str(to_state) in RUN_TRANSITIONS.get(str(from_state), set())


def is_valid_subagent_transition(from_state: SubAgentRunState | str, to_state: SubAgentRunState | str) -> bool:
    return str(to_state) in SUBAGENT_TRANSITIONS.get(str(from_state), set())
