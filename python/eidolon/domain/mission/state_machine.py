from __future__ import annotations

from .contracts import AgentRunPhase, AgentRunState

_PHASE_BY_STATE: dict[str, AgentRunPhase] = {
    'understanding': 'understand',
    'planning': 'plan',
    'spawning_work': 'execute',
    'acting': 'execute',
    'waiting': 'plan',
    'blocked': 'plan',
    'verifying': 'verify',
    'completed': 'finalize',
    'failed': 'finalize',
    'cancelled': 'finalize',
}

_PRODUCT_PHASE_BY_STATE: dict[str, str] = {
    'understanding': 'understand_and_structure',
    'planning': 'understand_and_structure',
    'spawning_work': 'execution',
    'acting': 'execution',
    'waiting': 'understand_and_structure',
    'blocked': 'understand_and_structure',
    'verifying': 'verification_and_return',
    'completed': 'verification_and_return',
    'failed': 'verification_and_return',
    'cancelled': 'verification_and_return',
}

_NEXT_BY_STATE: dict[str, AgentRunPhase | None] = {
    'understanding': 'plan',
    'planning': 'execute',
    'spawning_work': 'execute',
    'acting': 'verify',
    'waiting': 'execute',
    'blocked': None,
    'verifying': 'finalize',
    'completed': None,
    'failed': None,
    'cancelled': None,
}

_ADVANCE: dict[str, tuple[AgentRunState, str | None]] = {
    'understanding': ('planning', None),
    'planning': ('spawning_work', None),
    'spawning_work': ('acting', None),
    'acting': ('verifying', None),
    'waiting': ('planning', None),
    'blocked': ('planning', None),
    'verifying': ('completed', 'success'),
}


def normalize_phase_for_state(state: str | None, current_phase: str | None = None) -> AgentRunPhase:
    if current_phase in {'understand', 'plan', 'execute', 'verify', 'finalize'}:
        if state in {'blocked', 'waiting'}:
            return current_phase  # keep current planning/execute context when paused
    return _PHASE_BY_STATE.get(str(state), 'understand')


def product_phase_for_state(state: str | None) -> str:
    return _PRODUCT_PHASE_BY_STATE.get(str(state), 'understand_and_structure')


def normalize_next_transition(state: str | None, next_transition: str | None = None) -> AgentRunPhase | None:
    if next_transition in {'plan', 'execute', 'verify', 'finalize'}:
        return next_transition  # explicit contract wins
    return _NEXT_BY_STATE.get(str(state))


def advance_run_state(state: str, reason: str | None = None) -> dict[str, str | None]:
    if state not in _ADVANCE:
        raise ValueError(f'Cannot advance terminal or unknown run state: {state}')
    new_state, result_status = _ADVANCE[state]
    return {
        'new_state': new_state,
        'state_reason': reason or f'Advanced from {state} to {new_state}',
        'current_phase': normalize_phase_for_state(new_state),
        'next_transition': normalize_next_transition(new_state),
        'result_status': result_status,
    }
