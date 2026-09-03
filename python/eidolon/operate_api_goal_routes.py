from __future__ import annotations

from fastapi import FastAPI

from eidolon.operate_api_helpers import normalize_steps, require_status, require_title
from eidolon.routes.api_response import api_v1_error, api_v1_ok


def register_operate_goal_routes(app: FastAPI, *, runtime, autonomy_engine, goal_deriver, workspace_ui_service, health_callback, autonomy_cycle_callback=None) -> None:
    @app.get('/api/v1/operate/goals')
    async def api_v1_operate_goals(status: str | None = None, category: str | None = None):
        return api_v1_ok(runtime.api_v1_goal_payload(status=status, category=category))

    @app.post('/api/v1/operate/goals')
    async def api_v1_operate_create_goal(request: dict):
        goal = autonomy_engine.create_goal(
            title=require_title(request),
            description=request.get('description', ''),
            category=request.get('category', 'system'),
            priority=request.get('priority', 1),
            steps=normalize_steps(request.get('steps')),
        )
        return api_v1_ok({'goal': goal.to_dict(), 'operate': runtime.api_v1_operate_snapshot()})

    @app.put('/api/v1/operate/goals/{goal_id}')
    async def api_v1_operate_update_goal(goal_id: str, request: dict):
        result = autonomy_engine.update_goal(goal_id, **request)
        if result.get('ok') is False:
            api_v1_error('goal_update_failed', str(result.get('error') or 'Ziel konnte nicht aktualisiert werden'))
        return api_v1_ok({**result, 'operate': runtime.api_v1_operate_snapshot()})

    @app.delete('/api/v1/operate/goals/{goal_id}')
    async def api_v1_operate_delete_goal(goal_id: str):
        result = autonomy_engine.delete_goal(goal_id)
        if result.get('ok') is False:
            api_v1_error('goal_delete_failed', str(result.get('error') or 'Ziel konnte nicht gelöscht werden'))
        return api_v1_ok({**result, 'operate': runtime.api_v1_operate_snapshot()})

    @app.post('/api/v1/operate/goals/{goal_id}/transition')
    async def api_v1_operate_transition_goal(goal_id: str, request: dict):
        result = autonomy_engine.transition(goal_id, require_status(request), error=request.get('error'))
        if result.get('ok') is False:
            api_v1_error('goal_transition_failed', str(result.get('error') or 'Statuswechsel fehlgeschlagen'))
        return api_v1_ok({**result, 'operate': runtime.api_v1_operate_snapshot()})

    @app.get('/api/v1/operate/derive')
    async def api_v1_operate_derive_preview():
        health_data = await health_callback()
        result = goal_deriver.derive_all(health_data)
        for proposal in result['proposals']:
            proposal['already_exists'] = autonomy_engine.has_open_problem(proposal['problem_key'])
        return api_v1_ok({**result, 'operate': runtime.api_v1_operate_snapshot()})

    @app.post('/api/v1/operate/revalidate')
    async def api_v1_operate_revalidate(request: dict | None = None):
        health_data = await health_callback()
        auto_close = bool((request or {}).get('auto_close', True))
        result = autonomy_engine.revalidate(goal_deriver, health_data, auto_close=auto_close)
        result['single_active'] = autonomy_engine.enforce_single_active()
        return api_v1_ok({**result, 'operate': runtime.api_v1_operate_snapshot()})

    @app.post('/api/v1/operate/cycle')
    async def api_v1_operate_run_cycle():
        if autonomy_cycle_callback is not None:
            cycle = await autonomy_cycle_callback()
            if isinstance(cycle, dict):
                cycle = {k: v for k, v in cycle.items() if k not in {'deprecated', 'canonical_path', 'operate'}}
            return api_v1_ok({**cycle, 'operate': runtime.api_v1_operate_snapshot()})

        health_data = await health_callback()
        reval = autonomy_engine.revalidate(goal_deriver, health_data, auto_close=True)
        inv = autonomy_engine.enforce_single_active()
        cycle = autonomy_engine.run_cycle()
        performed = list(cycle.get('performed', []))
        if reval.get('auto_closed'):
            performed.append(f"{reval['auto_closed']} Ziel(e) automatisch geschlossen (Problem behoben)")
        if inv.get('changed'):
            performed.append(f"{len(inv.get('paused', []))} Ziel(e) pausiert (nur eines darf aktiv sein)")
        if reval.get('regressions'):
            performed.append(f"{len(reval['regressions'])} Regression(en) erkannt")
        payload = workspace_ui_service.get_runtime_payload()
        active_workspace = next((w for w in payload.get('workspaces', []) if w.get('state') == 'active'), None)
        workspace_execution = None
        if active_workspace:
            orchestration = ((active_workspace.get('state_data') or {}).get('orchestration') or {})
            next_best = orchestration.get('next_best_action') or {}
            if next_best.get('module_id') and next_best.get('action'):
                try:
                    workspace_execution = workspace_ui_service.execute_workspace_action(active_workspace['workspace_id'], next_best['module_id'], next_best['action'], next_best.get('payload') or {})
                    if workspace_execution.get('ok'):
                        performed.append(f"Workspace-Aktion ausgeführt: {next_best.get('label') or next_best.get('action')}")
                except Exception as exc:
                    workspace_execution = {'ok': False, 'error': str(exc), 'workspace_id': active_workspace.get('workspace_id')}
                    performed.append(f'Workspace-Aktion fehlgeschlagen: {exc}')
        return api_v1_ok({**cycle, 'performed': performed, 'revalidation': {k: reval[k] for k in ('checked', 'resolved', 'still_open', 'unverifiable', 'auto_closed')}, 'regressions': reval.get('regressions', []), 'invariants': inv, 'workspace_execution': workspace_execution, 'operate': runtime.api_v1_operate_snapshot()})
