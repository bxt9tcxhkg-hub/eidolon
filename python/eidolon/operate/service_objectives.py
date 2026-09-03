from __future__ import annotations

from eidolon.domain.mission.state_machine import normalize_next_transition, normalize_phase_for_state
from eidolon.domain.mission.state_machine import product_phase_for_state
from eidolon.operate.service_support import normalize_goal, normalize_title, set_run_state, scope_summary as normalize_scope_summary


def start_objective(service, user_request: str, *, title: str | None = None, normalized_goal: str | None = None, scope_summary: str | None = None, decomposition_mode: str = 'undecided', source_kind: str = 'chat', current_view: str = 'operate', autonomy_mode: str = 'bounded_autonomous') -> dict[str, object]:
    session = service.store.create_session(title=normalize_title(user_request, title), source_kind=source_kind, current_view=current_view)
    objective = service.store.create_objective(session_id=session.id, title=normalize_title(user_request, title), user_request=user_request, normalized_goal=normalize_goal(user_request, normalized_goal), scope_summary=normalize_scope_summary(scope_summary), decomposition_mode=decomposition_mode, status='active')
    run = service.store.create_agent_run(session_id=session.id, objective_id=objective.id, state='understanding', state_reason='New objective created', current_phase=normalize_phase_for_state('understanding'), next_transition=normalize_next_transition('understanding'), autonomy_mode=autonomy_mode, product_phase=product_phase_for_state('understanding'), phase_provenance='runtime_mapping')
    service.store.append_transition_event(actor_type='run', actor_id=run.id, transition_type='state_change', from_state=None, to_state='understanding', summary='Objective entered understanding phase', evidence_ids=[])
    session = service.store.update_session(session.id, current_run_id=run.id, current_objective_id=objective.id)
    return {'session': session, 'objective': objective, 'run': run}


def spawn_subagent_run(service, run_id: str, display_name: str, function_type: str, mission: str, state_reason: str, assigned_by: str = 'system'):
    run = service.store.get_run(run_id)
    if run is None:
        raise KeyError(run_id)
    subagent = service.store.create_subagent_run(parent_run_id=run_id, objective_id=run.objective_id, display_name=display_name, function_type=function_type, mission=mission, state='queued', state_reason=state_reason, assigned_by=assigned_by)
    service.store.append_transition_event(actor_type='subagent', actor_id=subagent.id, transition_type='spawned', from_state=None, to_state='queued', summary=f'{display_name} spawned', evidence_ids=[])
    return subagent


def open_blocking_issue(service, run_id: str, title: str, summary: str, category: str = 'runtime_error', requires_user_action: bool = True, resolution_hint: str | None = None):
    run = service.store.get_run(run_id)
    if run is None:
        raise KeyError(run_id)
    issue = service.store.create_blocking_issue(owner_type='run', owner_id=run_id, category=category, title=title, summary=summary, requires_user_action=requires_user_action, resolution_hint=resolution_hint)
    set_run_state(service, run_id, new_state='blocked', state_reason=summary, current_phase=run.current_phase, next_transition=None)
    updated = service.store.update_agent_run(run_id, blocking_issue_id=issue.id)
    return issue, updated


def resolve_blocking_issue(service, issue_id: str, resume_state: str = 'planning', state_reason: str = 'Blocking issue resolved'):
    issue = service.store.get_blocking_issue(issue_id)
    if issue is None:
        raise KeyError(issue_id)
    if issue.owner_type != 'run':
        raise ValueError('Only run-owned blocking issues are currently supported')
    service.store.update_blocking_issue(issue_id, status='resolved')
    run = service.store.get_run(issue.owner_id)
    if run is None:
        raise KeyError(issue.owner_id)
    updated = service.store.update_agent_run(issue.owner_id, blocking_issue_id=None)
    if updated.state != resume_state:
        updated = set_run_state(service, issue.owner_id, resume_state, state_reason, current_phase='plan' if resume_state == 'planning' else updated.current_phase, next_transition='execute' if resume_state == 'planning' else updated.next_transition)
    return updated


def request_approval(service, run_id: str, title: str, summary: str, action_type: str):
    run = service.store.get_run(run_id)
    if run is None:
        raise KeyError(run_id)
    gate = service.store.create_approval_gate(run_id=run_id, title=title, summary=summary, action_type=action_type)
    service.store.update_agent_run(run_id, state='waiting', state_reason=summary, current_phase='plan', next_transition='execute', approval_required=True, product_phase=product_phase_for_state('waiting'))
    service.store.append_transition_event(actor_type='run', actor_id=run_id, transition_type='blocked', from_state=run.state, to_state='waiting', summary=f'Approval requested: {title}', evidence_ids=[])
    return gate
