from __future__ import annotations

from typing import Any

from eidolon.domain.mission.next_action import derive_next_action
from eidolon.domain.mission.state_machine import advance_run_state
from eidolon.operate.contracts import NextActionRecord, is_valid_run_transition
from eidolon.operate.service_support_common import now_iso
from eidolon.operate.service_support_state import set_run_state


def resolve_approval(service, gate_id: str, decision: str, resolved_by: str = 'user'):
    gate = service.store.get_approval_gate(gate_id)
    if gate is None:
        raise KeyError(gate_id)
    if decision not in {'approved', 'rejected'}:
        raise ValueError('decision must be approved or rejected')
    resolved = service.store.update_approval_gate(gate_id, status=decision, resolved_at=now_iso(), resolved_by=resolved_by)
    run = service.store.get_run(gate.run_id)
    if run is None:
        raise KeyError(gate.run_id)
    if decision == 'approved':
        service.store.update_agent_run(gate.run_id, state='planning', state_reason='Approval granted', current_phase='plan', next_transition='execute', approval_required=False)
        transition_type = 'approved'; to_state = 'planning'
    else:
        service.store.update_agent_run(gate.run_id, state='failed', state_reason='Approval rejected', current_phase='finalize', next_transition=None, approval_required=False, result_status='failure', ended_at=now_iso())
        transition_type = 'rejected'; to_state = 'failed'
    service.store.append_transition_event(actor_type='run', actor_id=gate.run_id, transition_type=transition_type, from_state=run.state, to_state=to_state, summary=f'Approval {decision}: {gate.title}', evidence_ids=[])
    return resolved


def emit_evidence(service, owner_type: str, owner_id: str, kind: str, title: str, summary: str, metadata_json: dict[str, Any] | None = None, artifact_ref: str | None = None):
    record = service.store.create_evidence_item(owner_type=owner_type, owner_id=owner_id, kind=kind, title=title, summary=summary, artifact_ref=artifact_ref, metadata_json=metadata_json, evidence_severity='info', is_completion_grade=False, ui_digest_text=None)
    service.evidence_store.log_observation(action_id=None, kind=kind, description=title, detail=summary)
    if artifact_ref:
        service.evidence_store.log_artifact(action_id=None, path=artifact_ref)
    return record


def get_next_action(service, run_id: str) -> NextActionRecord:
    run = service.store.get_run(run_id)
    approvals = service.store.list_approval_gates(run_id)
    blockers = service.store.list_blocking_issues(run_id)
    return derive_next_action(run, approvals, blockers)


def interrupt_run(service, run_id: str, interrupt_type: str, message: str | None = None):
    run = service.store.get_run(run_id)
    if run is None:
        raise KeyError(run_id)
    if run.state in {'completed', 'failed', 'cancelled'}:
        raise ValueError('Cannot interrupt terminal run')
    target_state = 'planning'
    if run.state != 'planning' and not is_valid_run_transition(run.state, target_state):
        raise ValueError(f'Invalid run transition: {run.state} -> {target_state}')
    updated = service.store.update_agent_run(run_id, state=target_state, state_reason=message or f'Interrupt received: {interrupt_type}', current_phase='plan', next_transition='execute', pending_interrupt_count=run.pending_interrupt_count + 1, last_interrupt_at=now_iso(), interrupt_classification=interrupt_type if interrupt_type in {'refine', 'conflict', 'supersede'} else 'refine')
    service.store.append_transition_event(actor_type='run', actor_id=run_id, transition_type='interrupted', from_state=run.state, to_state=target_state, summary=f'{interrupt_type}: {message or "no message"}', evidence_ids=[])
    return updated


def advance_run(service, run_id: str, reason: str | None = None):
    run = service.store.get_run(run_id)
    if run is None:
        raise KeyError(run_id)
    if run.state in {'completed', 'failed', 'cancelled'}:
        raise ValueError('Cannot advance terminal run')
    if any(gate.status == 'pending' for gate in service.store.list_approval_gates(run_id)):
        raise ValueError('Cannot advance run with pending approval gate')
    if any(issue.status == 'open' for issue in service.store.list_blocking_issues(run_id)):
        raise ValueError('Cannot advance run with open blocking issue')
    transition = advance_run_state(run.state, reason=reason)
    return set_run_state(service, run_id, new_state=transition['new_state'], state_reason=transition['state_reason'], current_phase=transition['current_phase'], next_transition=transition['next_transition'], result_status=transition['result_status'])
