from __future__ import annotations

from typing import Any

from eidolon.domain.approvals.presentation import present_approvals
from eidolon.domain.blockers.presentation import present_blockers
from eidolon.domain.evidence.presentation import present_evidence
from eidolon.domain.mission.summary import build_run_summary
from eidolon.domain.pods.presentation import summarize_subagent_runs
from eidolon.operate.bridge_views import history_entries_for_run, work_graph_for_run


def build_operate_snapshot(service, run_id: str | None = None) -> dict[str, Any]:
    session = service.get_current_session()
    run = service.get_run(run_id) if run_id else service.get_current_run()
    objective = service.get_objective(run.objective_id) if run else None
    subagent_records = service.list_subagent_runs(run.id) if run else []
    blocker_records = service.list_blocking_issues(run.id) if run else []
    approval_records = service.list_approval_gates(run.id) if run else []
    evidence_records = service.list_evidence_items(run.id) if run else []
    subagents = summarize_subagent_runs(subagent_records) if run else []
    blockers = present_blockers(blocker_records) if run else []
    approvals = present_approvals(approval_records) if run else []
    evidence = present_evidence(evidence_records) if run else []
    transitions = [item.to_dict() for item in service.list_transition_events(run.id)] if run else []
    history = history_entries_for_run(service, run.id) if run else []
    work_graph = work_graph_for_run(service, run.id) if run else {'nodes': [], 'edges': []}
    next_action = service.get_next_action(run.id).to_dict() if run else None
    return {'session': session.to_dict() if session else None, 'objective': objective.to_dict() if objective else None, 'run': build_run_summary(run, objective) if run else None, 'subagents': subagents, 'active_pods': [item for item in subagents if item.get('is_active')], 'blockers': blockers, 'approvals': approvals, 'evidence': evidence, 'transitions': transitions, 'history': history, 'work_graph': work_graph, 'next_action': next_action}


def build_compact_operate_snapshot(service, run_id: str | None = None) -> dict[str, Any]:
    snapshot = build_operate_snapshot(service, run_id)
    run = snapshot.get('run') or {}
    run_id_value = run.get('id')
    subagents = list(snapshot.get('subagents') or [])
    active_pods = list(snapshot.get('active_pods') or [])
    blockers = list(snapshot.get('blockers') or [])
    approvals = list(snapshot.get('approvals') or [])
    evidence = list(snapshot.get('evidence') or [])
    transitions = list(snapshot.get('transitions') or [])
    history = list(snapshot.get('history') or [])
    work_graph = snapshot.get('work_graph') or {'nodes': [], 'edges': []}
    return {
        'session': snapshot.get('session'),
        'objective': snapshot.get('objective'),
        'run': run,
        'subagents': subagents[:3],
        'active_pods': active_pods[:3],
        'blockers': blockers[:3],
        'approvals': approvals[:3],
        'evidence': evidence[:5],
        'next_action': snapshot.get('next_action'),
        'counts': {
            'subagents': len(subagents),
            'active_pods': len(active_pods),
            'blockers': len(blockers),
            'approvals': len(approvals),
            'evidence': len(evidence),
            'transitions': len(transitions),
            'history': len(history),
            'work_graph_nodes': len(work_graph.get('nodes') or []),
            'work_graph_edges': len(work_graph.get('edges') or []),
        },
        'deep_links': {
            'subagents': f'/api/v1/runs/{run_id_value}/subagents' if run_id_value else None,
            'evidence': f'/api/v1/runs/{run_id_value}/evidence' if run_id_value else None,
            'transitions': f'/api/v1/runs/{run_id_value}/transitions' if run_id_value else None,
            'history': f'/api/v1/runs/{run_id_value}/history' if run_id_value else None,
            'work_graph': f'/api/v1/runs/{run_id_value}/work-graph' if run_id_value else None,
            'blockers': f'/api/v1/runs/{run_id_value}/blockers' if run_id_value else None,
            'approvals': f'/api/v1/runs/{run_id_value}/approvals' if run_id_value else None,
        },
    }
