from __future__ import annotations

from eidolon.domain.mission.state_machine import normalize_next_transition, normalize_phase_for_state
from eidolon.operate.contracts import is_valid_run_transition, is_valid_subagent_transition
from eidolon.operate.service_support_common import now_iso


def set_run_state(service, run_id: str, new_state: str, state_reason: str, current_phase: str | None = None, next_transition: str | None = None, result_status: str | None = None):
    run = service.store.get_run(run_id)
    if run is None:
        raise KeyError(run_id)
    if not is_valid_run_transition(run.state, new_state):
        raise ValueError(f'Invalid run transition: {run.state} -> {new_state}')
    from eidolon.domain.mission.state_machine import product_phase_for_state
    updated = service.store.update_agent_run(
        run_id,
        state=new_state,
        state_reason=state_reason,
        current_phase=normalize_phase_for_state(new_state, current_phase or run.current_phase),
        next_transition=normalize_next_transition(new_state, next_transition),
        result_status=result_status,
        ended_at=now_iso() if new_state in {'completed', 'failed', 'cancelled'} else run.ended_at,
        product_phase=product_phase_for_state(new_state),
        completion_summary=state_reason if new_state in {'completed', 'failed', 'cancelled'} else run.completion_summary,
    )
    service.store.append_transition_event(
        actor_type='run', actor_id=run_id, transition_type='state_change', from_state=run.state, to_state=new_state, summary=state_reason, evidence_ids=[]
    )
    return updated


def set_subagent_state(service, subagent_id: str, new_state: str, state_reason: str, result_status: str | None = None):
    current = service.store.get_subagent_run(subagent_id)
    if current is None:
        raise KeyError(subagent_id)
    if not is_valid_subagent_transition(current.state, new_state):
        raise ValueError(f'Invalid subagent transition: {current.state} -> {new_state}')
    updated = service.store.update_subagent_run(
        subagent_id,
        state=new_state,
        state_reason=state_reason,
        result_status=result_status,
        started_at=current.started_at or (now_iso() if new_state == 'running' else None),
        ended_at=now_iso() if new_state in {'completed', 'failed', 'cancelled'} else current.ended_at,
    )
    service.store.append_transition_event(
        actor_type='subagent', actor_id=subagent_id, transition_type='state_change', from_state=current.state, to_state=new_state, summary=state_reason, evidence_ids=[]
    )
    return updated
