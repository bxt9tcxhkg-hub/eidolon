from __future__ import annotations

from fastapi import FastAPI

from eidolon.domain.mission.product_phases import build_phase_preservation_payload
from eidolon.domain.mission.summary import build_run_summary
from eidolon.routes.api_response import api_v1_error, api_v1_ok


def register_operate_runs_routes(app: FastAPI, *, runtime, get_operate_service, workspace_ui_service) -> None:
    @app.get('/api/v1/runs/current')
    async def api_v1_current_run():
        runtime.ensure_operate_bootstrap_from_workspace()
        service = get_operate_service()
        session = service.get_current_session()
        run = service.get_current_run()
        payload = None
        if run:
            objective = service.get_objective(run.objective_id)
            work_kernel = workspace_ui_service.get_unified_work_context(source='operate')
            context_state = ((work_kernel or {}).get('workflow_state') or {}).get('current_context_state')
            run_summary = build_run_summary(run, objective)
            run_summary['phase_preservation'] = build_phase_preservation_payload(
                run_state=run_summary.get('state'),
                current_phase=run_summary.get('current_phase'),
                context_state=context_state,
                has_objective=objective is not None,
                current_view=getattr(session, 'current_view', None),
                has_subagents=bool(service.list_subagent_runs(run.id)),
                has_blocker=bool(service.list_blocking_issues(run.id)),
                has_approval=bool(service.list_approval_gates(run.id)),
                result_status=run_summary.get('result_status'),
            )
            payload = {'run': run_summary, 'objective': objective.to_dict() if objective else None}
        return api_v1_ok(payload)

    @app.get('/api/v1/runs/{run_id}/subagents')
    async def api_v1_run_subagents(run_id: str):
        runtime.api_v1_run_or_404(run_id)
        return api_v1_ok({'subagents': [item.to_dict() for item in get_operate_service().list_subagent_runs(run_id)]})

    @app.get('/api/v1/runs/{run_id}/evidence')
    async def api_v1_run_evidence(run_id: str):
        runtime.api_v1_run_or_404(run_id)
        return api_v1_ok({'evidence': [item.to_dict() for item in get_operate_service().list_evidence_items(run_id)]})

    @app.get('/api/v1/runs/{run_id}/transitions')
    async def api_v1_run_transitions(run_id: str):
        runtime.api_v1_run_or_404(run_id)
        return api_v1_ok({'transitions': [item.to_dict() for item in get_operate_service().list_transition_events(run_id)]})

    @app.get('/api/v1/runs/{run_id}/blockers')
    async def api_v1_run_blockers(run_id: str):
        runtime.api_v1_run_or_404(run_id)
        return api_v1_ok({'blockers': [item.to_dict() for item in get_operate_service().list_blocking_issues(run_id)]})

    @app.get('/api/v1/runs/{run_id}/approvals')
    async def api_v1_run_approvals(run_id: str):
        runtime.api_v1_run_or_404(run_id)
        return api_v1_ok({'approvals': [item.to_dict() for item in get_operate_service().list_approval_gates(run_id)]})

    @app.get('/api/v1/runs/{run_id}/next-action')
    async def api_v1_run_next_action(run_id: str):
        runtime.api_v1_run_or_404(run_id)
        return api_v1_ok({'next_action': get_operate_service().get_next_action(run_id).to_dict()})

    @app.get('/api/v1/runs/{run_id}/history')
    async def api_v1_run_history(run_id: str):
        runtime.api_v1_run_or_404(run_id)
        snapshot = runtime.api_v1_operate_snapshot(run_id)
        return api_v1_ok({'history': snapshot.get('history', [])})

    @app.get('/api/v1/runs/{run_id}/work-graph')
    async def api_v1_run_work_graph(run_id: str):
        runtime.api_v1_run_or_404(run_id)
        snapshot = runtime.api_v1_operate_snapshot(run_id)
        return api_v1_ok(snapshot.get('work_graph', {'nodes': [], 'edges': []}))
