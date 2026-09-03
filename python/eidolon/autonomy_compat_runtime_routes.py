from __future__ import annotations

from fastapi import FastAPI

from eidolon.autonomy_compat_helpers import active_workspace, deprecated_payload
from eidolon.autonomy_compat_status import build_cycle_payload, build_status_payload


def register_autonomy_compat_runtime_routes(app: FastAPI, *, autonomy_engine, operate_service, workspace_ui_service, health_callback, goal_deriver, build_operate_snapshot) -> None:
    @app.get('/autonomy/status')
    async def autonomy_status():
        return build_status_payload(autonomy_engine=autonomy_engine, workspace_ui_service=workspace_ui_service)

    @app.post('/autonomy/cycle')
    async def autonomy_run_cycle():
        health_data = await health_callback()
        reval = autonomy_engine().revalidate(goal_deriver, health_data, auto_close=True)
        inv = autonomy_engine().enforce_single_active()
        cycle = autonomy_engine().run_cycle()
        payload = workspace_ui_service().get_runtime_payload()
        workspace = active_workspace(payload)
        workspace_execution = None
        if workspace:
            orchestration = ((workspace.get('state_data') or {}).get('orchestration') or {})
            next_best = orchestration.get('next_best_action') or {}
            if next_best.get('module_id') and next_best.get('action'):
                try:
                    workspace_execution = workspace_ui_service().execute_workspace_action(workspace['workspace_id'], next_best['module_id'], next_best['action'], next_best.get('payload') or {})
                except Exception as exc:
                    workspace_execution = {'ok': False, 'error': str(exc), 'workspace_id': workspace.get('workspace_id')}
        return build_cycle_payload(cycle=cycle, reval=reval, inv=inv, workspace_execution=workspace_execution, operate_snapshot=build_operate_snapshot(operate_service()))

    @app.get('/autonomy/derive')
    async def autonomy_derive_preview():
        health_data = await health_callback()
        result = goal_deriver.derive_all(health_data)
        for proposal in result['proposals']:
            proposal['already_exists'] = autonomy_engine().has_open_problem(proposal['problem_key'])
        return deprecated_payload('/api/v1/operate/derive', ok=True, **result, operate=build_operate_snapshot(operate_service()))

    @app.post('/autonomy/derive/apply')
    async def autonomy_derive_apply(request: dict | None = None):
        health_data = await health_callback()
        result = goal_deriver.derive_all(health_data)
        wanted = (request or {}).get('problem_keys')
        created, skipped = [], []
        for proposal in result['proposals']:
            if wanted and proposal['problem_key'] not in wanted:
                continue
            if autonomy_engine().has_open_problem(proposal['problem_key']):
                skipped.append({'problem_key': proposal['problem_key'], 'reason': 'offenes Ziel existiert bereits'})
                continue
            goal = autonomy_engine().create_goal(title=proposal['title'], description=proposal['description'], category=proposal['category'], priority=proposal['priority'], steps=proposal['steps'], source=proposal['source'], evidence=proposal['evidence'], problem_key=proposal['problem_key'])
            created.append({'id': goal.id, 'title': goal.title, 'problem_key': goal.problem_key})
        return {'ok': True, 'created': created, 'skipped': skipped, 'created_count': len(created), 'skipped_count': len(skipped), 'deduplicated': result.get('deduplicated', 0)}

    @app.post('/autonomy/revalidate')
    async def autonomy_revalidate(request: dict | None = None):
        health_data = await health_callback()
        auto_close = bool((request or {}).get('auto_close', True))
        result = autonomy_engine().revalidate(goal_deriver, health_data, auto_close=auto_close)
        result['single_active'] = autonomy_engine().enforce_single_active()
        result.pop('ok', None)
        return deprecated_payload('/api/v1/operate/revalidate', ok=True, **result, operate=build_operate_snapshot(operate_service()))

    @app.post('/autonomy/enforce-invariants')
    async def autonomy_enforce_invariants():
        result = autonomy_engine().enforce_single_active()
        result.pop('ok', None)
        return deprecated_payload('/api/v1/operate/revalidate', ok=True, **result, operate=build_operate_snapshot(operate_service()))
