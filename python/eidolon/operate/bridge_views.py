from __future__ import annotations

from typing import Any

from eidolon.operate.service import OperateService


def history_entries_for_run(service: OperateService, run_id: str) -> list[dict[str, Any]]:
    transitions = [
        {'id': item.id, 'kind': 'transition', 'timestamp': item.created_at, 'title': item.transition_type, 'summary': item.summary, 'actor_type': item.actor_type, 'actor_id': item.actor_id, 'from_state': item.from_state, 'to_state': item.to_state}
        for item in service.list_transition_events(run_id)
    ]
    subagents = [
        {'id': item.id, 'kind': 'subagent', 'timestamp': item.updated_at, 'title': item.display_name, 'summary': item.mission, 'state': item.state, 'result_status': item.result_status}
        for item in service.list_subagent_runs(run_id)
    ]
    blockers = [
        {'id': item.id, 'kind': 'blocker', 'timestamp': item.updated_at, 'title': item.title, 'summary': item.summary, 'state': item.status}
        for item in service.list_blocking_issues(run_id)
    ]
    approvals = [
        {'id': item.id, 'kind': 'approval', 'timestamp': item.resolved_at or item.requested_at, 'title': item.title, 'summary': item.summary, 'state': item.status}
        for item in service.list_approval_gates(run_id)
    ]
    evidence = [
        {'id': item.id, 'kind': 'evidence', 'timestamp': item.created_at, 'title': item.title, 'summary': item.summary, 'state': item.kind}
        for item in service.list_evidence_items(run_id)
    ]
    return sorted(transitions + subagents + blockers + approvals + evidence, key=lambda item: (item.get('timestamp') or '', item.get('id') or ''))


def work_graph_for_run(service: OperateService, run_id: str) -> dict[str, Any]:
    run = service.get_run(run_id)
    if run is None:
        return {'nodes': [], 'edges': []}
    objective = service.get_objective(run.objective_id)
    nodes = [{'id': run.id, 'kind': 'run', 'label': run.state, 'title': run.state_reason, 'state': run.state}]
    edges = []
    if objective is not None:
        nodes.append({'id': objective.id, 'kind': 'objective', 'label': objective.title, 'title': objective.normalized_goal, 'state': objective.status})
        edges.append({'from': objective.id, 'to': run.id, 'type': 'drives'})
    for subagent in service.list_subagent_runs(run_id):
        nodes.append({'id': subagent.id, 'kind': 'subagent', 'label': subagent.display_name, 'title': subagent.mission, 'state': subagent.state})
        edges.append({'from': run.id, 'to': subagent.id, 'type': 'spawned'})
    for blocker in service.list_blocking_issues(run_id):
        nodes.append({'id': blocker.id, 'kind': 'blocker', 'label': blocker.title, 'title': blocker.summary, 'state': blocker.status})
        edges.append({'from': run.id, 'to': blocker.id, 'type': 'blocked_by'})
    for approval in service.list_approval_gates(run_id):
        nodes.append({'id': approval.id, 'kind': 'approval', 'label': approval.title, 'title': approval.summary, 'state': approval.status})
        edges.append({'from': run.id, 'to': approval.id, 'type': 'awaits_approval'})
    for item in service.list_evidence_items(run_id):
        nodes.append({'id': item.id, 'kind': 'evidence', 'label': item.title, 'title': item.summary, 'state': item.kind})
        edges.append({'from': run.id, 'to': item.id, 'type': 'evidenced_by'})
    return {'nodes': nodes, 'edges': edges}
