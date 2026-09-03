from __future__ import annotations

from typing import Any

from eidolon.operate.bridge_workspace import align_run_state_from_summary, derive_decomposition_mode, select_active_workspace, spawn_bootstrap_subagents, workspace_next_actions, workspace_seed_from_record, workspace_summary


def sync_operate_with_workspace_payload(service, payload: dict[str, Any] | None) -> dict[str, Any] | None:
    current_run = service.get_current_run()
    if current_run is not None:
        session = service.get_current_session()
        objective = service.get_objective(current_run.objective_id) if current_run.objective_id else None
        return {'session': session, 'objective': objective, 'run': current_run}
    workspace = select_active_workspace(payload)
    if workspace is None:
        return None
    summary = workspace_summary(workspace)
    next_actions = workspace_next_actions(workspace)
    title, user_request, workspace_id, project_id = workspace_seed_from_record(workspace)
    normalized_goal = next_actions[0] if next_actions else f'Advance active workspace: {title}'
    scope_summary = f"workspace_id={workspace_id}; blocked={summary.get('blocked', 0)}; in_progress={summary.get('in_progress', 0)}; ready={summary.get('ready', 0)}; done={summary.get('done', 0)}"
    started = service.start_objective(user_request=user_request, title=title, normalized_goal=normalized_goal, scope_summary=scope_summary, decomposition_mode=derive_decomposition_mode(summary, next_actions), source_kind='workspace_bridge', current_view='operate', autonomy_mode='bounded_autonomous')
    run = started['run']
    service.emit_evidence(owner_type='run', owner_id=run.id, kind='workspace_context', title='Operate bootstrapped from active workspace', summary=f"{title}: blocked={summary.get('blocked', 0)}, in_progress={summary.get('in_progress', 0)}, ready={summary.get('ready', 0)}, done={summary.get('done', 0)}", metadata_json={'workspace_id': workspace_id, 'workspace_type': workspace.get('workspace_type'), 'project_id': project_id, 'next_actions': next_actions})
    updated_run = service.set_run_state(run.id, new_state='planning', state_reason='Bootstrapped from active workspace context', current_phase='plan', next_transition='execute')
    spawn_bootstrap_subagents(service, run.id, summary, next_actions)
    align_run_state_from_summary(service, run.id, summary)
    return {'session': service.get_current_session(), 'objective': started['objective'], 'run': service.get_run(updated_run.id)}
