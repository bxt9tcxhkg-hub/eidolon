from __future__ import annotations

from fastapi import FastAPI

from eidolon.domain.mission.product_phases import build_phase_preservation_payload
from eidolon.operate.bridge_snapshot import build_compact_operate_snapshot
from eidolon.routes.api_response import api_v1_ok
from eidolon.workspaces.generic_slots import build_generic_slots


def register_operate_overview_routes(app: FastAPI, *, runtime, get_operate_service, workspace_ui_service) -> None:
    @app.get('/api/v1/operate/overview')
    async def api_v1_operate_overview():
        service = get_operate_service()
        run = service.get_current_run()
        snapshot = build_compact_operate_snapshot(service, run.id if run else None)
        work_kernel = workspace_ui_service.get_unified_work_context(source='operate')
        context_state = ((work_kernel or {}).get('workflow_state') or {}).get('current_context_state')
        if snapshot.get('run'):
            snapshot['run']['phase_preservation'] = build_phase_preservation_payload(
                run_state=snapshot['run'].get('state'),
                current_phase=snapshot['run'].get('current_phase'),
                context_state=context_state,
                has_objective=bool(snapshot.get('objective')),
                current_view=(snapshot.get('session') or {}).get('current_view'),
                has_subagents=bool(snapshot.get('counts', {}).get('subagents')),
                has_blocker=bool(snapshot.get('counts', {}).get('blockers')),
                has_approval=bool(snapshot.get('counts', {}).get('approvals')),
                result_status=snapshot['run'].get('result_status'),
            )
        formation = (work_kernel or {}).get('formation')
        slots = build_generic_slots(work_kernel=work_kernel, operate=snapshot)
        return api_v1_ok({**snapshot, 'work_kernel': work_kernel, 'formation': formation, 'generic_slots': slots})
