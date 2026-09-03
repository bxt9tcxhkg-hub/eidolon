from __future__ import annotations

from fastapi import FastAPI, HTTPException

from eidolon.autonomy_compat_helpers import deprecated_payload, normalize_steps


def register_autonomy_goal_routes(app: FastAPI, *, autonomy_engine, operate_service, goal_categories, build_operate_snapshot) -> None:
    @app.get('/autonomy/goals')
    async def autonomy_goals(status: str | None = None, category: str | None = None):
        goals = autonomy_engine().list_goals(status=status, category=category)
        return deprecated_payload('/api/v1/operate/goals', operate=build_operate_snapshot(operate_service()), goals=[goal.to_dict() for goal in goals], stats=autonomy_engine().get_stats(), categories=goal_categories)

    @app.get('/autonomy/goals/{goal_id}')
    async def autonomy_goal_detail(goal_id: str):
        goal = autonomy_engine().get_goal(goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail='Ziel nicht gefunden')
        return {'ok': True, 'goal': goal.to_dict()}

    @app.post('/autonomy/goals')
    async def autonomy_create_goal(request: dict):
        title = (request.get('title') or '').strip()
        if not title:
            return {'ok': False, 'error': 'Titel erforderlich'}
        goal = autonomy_engine().create_goal(title=title, description=request.get('description', ''), category=request.get('category', 'system'), priority=request.get('priority', 1), steps=normalize_steps(request.get('steps')))
        return deprecated_payload('/api/v1/operate/goals', operate=build_operate_snapshot(operate_service()), goal=goal.to_dict())

    @app.put('/autonomy/goals/{goal_id}')
    async def autonomy_update_goal(goal_id: str, request: dict):
        return autonomy_engine().update_goal(goal_id, **request)

    @app.delete('/autonomy/goals/{goal_id}')
    async def autonomy_delete_goal(goal_id: str):
        return autonomy_engine().delete_goal(goal_id)

    @app.post('/autonomy/goals/{goal_id}/transition')
    async def autonomy_transition_goal(goal_id: str, request: dict):
        new_status = request.get('status', '')
        if not new_status:
            return {'ok': False, 'error': 'Status erforderlich'}
        return autonomy_engine().transition(goal_id, new_status, error=request.get('error'))

    @app.post('/autonomy/goals/{goal_id}/steps')
    async def autonomy_add_step(goal_id: str, request: dict):
        title = (request.get('title') or '').strip()
        if not title:
            return {'ok': False, 'error': 'Titel erforderlich'}
        return autonomy_engine().add_step(goal_id, title)

    @app.post('/autonomy/goals/{goal_id}/steps/{step_id}/toggle')
    async def autonomy_toggle_step(goal_id: str, step_id: str):
        return autonomy_engine().toggle_step(goal_id, step_id)

    @app.delete('/autonomy/goals/{goal_id}/steps/{step_id}')
    async def autonomy_delete_step(goal_id: str, step_id: str):
        return autonomy_engine().delete_step(goal_id, step_id)

    @app.get('/autonomy/next-best-action')
    async def autonomy_nba():
        return {'ok': True, 'next_best_action': autonomy_engine().next_best_action()}

    @app.get('/autonomy/stats')
    async def autonomy_stats():
        return deprecated_payload('/api/v1/operate/goals', ok=True, stats=autonomy_engine().get_stats(), operate=build_operate_snapshot(operate_service()))

    @app.get('/autonomy/log')
    async def autonomy_log(limit: int = 30):
        return deprecated_payload('/api/v1/operate/overview', ok=True, log=autonomy_engine().get_log(limit), operate=build_operate_snapshot(operate_service()))
