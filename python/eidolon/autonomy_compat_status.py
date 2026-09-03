from __future__ import annotations

from eidolon.autonomy_compat_helpers import active_workspace, deprecated_payload


def build_status_payload(*, autonomy_engine, workspace_ui_service):
    payload = workspace_ui_service().get_runtime_payload()
    workspace = active_workspace(payload)
    goal_next_action = autonomy_engine().next_best_action()
    workspace_next_action = (((workspace or {}).get('state_data') or {}).get('orchestration') or {}).get('next_best_action') or None
    effective_next_action = {**workspace_next_action, 'source': 'workspace_orchestration'} if workspace_next_action else ({**goal_next_action, 'source': 'goal_engine'} if goal_next_action else None)
    return deprecated_payload('/api/v1/operate/overview', ok=True, stats=autonomy_engine().get_stats(), goal_next_action=goal_next_action, effective_next_action=effective_next_action, context_model=payload.get('context_model', {}), active_workspace={
        'workspace_id': workspace.get('workspace_id'),
        'topic_label': workspace.get('topic_label'),
        'workspace_type': workspace.get('workspace_type'),
        'state': workspace.get('state'),
        'project_id': (workspace.get('metadata') or {}).get('project_id'),
        'project_status': (workspace.get('metadata') or {}).get('project_status'),
        'orchestration': ((workspace.get('state_data') or {}).get('orchestration') or {}),
    } if workspace else None)


def build_cycle_payload(*, cycle: dict, reval: dict, inv: dict, workspace_execution, operate_snapshot):
    performed = list(cycle.get('performed', []))
    if reval.get('auto_closed'):
        performed.append(f"{reval['auto_closed']} Ziel(e) automatisch geschlossen (Problem behoben)")
    if inv.get('changed'):
        performed.append(f"{len(inv.get('paused', []))} Ziel(e) pausiert (nur eines darf aktiv sein)")
    if reval.get('regressions'):
        performed.append(f"{len(reval['regressions'])} Regression(en) erkannt")
    payload = dict(cycle)
    payload['performed'] = performed
    payload['revalidation'] = {k: reval[k] for k in ('checked', 'resolved', 'still_open', 'unverifiable', 'auto_closed')}
    payload['regressions'] = reval.get('regressions', [])
    payload['invariants'] = inv
    payload['workspace_execution'] = workspace_execution
    payload['operate'] = operate_snapshot
    return deprecated_payload('/api/v1/operate/cycle', **payload)
