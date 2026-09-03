from __future__ import annotations

from typing import Any, Callable

from fastapi import FastAPI

from eidolon.autonomy_compat_goal_routes import register_autonomy_goal_routes
from eidolon.autonomy_compat_runtime_routes import register_autonomy_compat_runtime_routes


def register_autonomy_compat_routes(
    app: FastAPI,
    *,
    get_autonomy_engine: Callable[[], Any],
    get_operate_service: Callable[[], Any],
    get_workspace_ui_service: Callable[[], Any],
    health_callback: Callable[[], Any],
    goal_deriver: Any,
    goal_categories: list[str],
    build_operate_snapshot: Callable[[Any], dict[str, Any]],
) -> None:
    autonomy_engine = lambda: get_autonomy_engine()
    operate_service = lambda: get_operate_service()
    workspace_ui_service = lambda: get_workspace_ui_service()
    register_autonomy_goal_routes(app, autonomy_engine=autonomy_engine, operate_service=operate_service, goal_categories=goal_categories, build_operate_snapshot=build_operate_snapshot)
    register_autonomy_compat_runtime_routes(app, autonomy_engine=autonomy_engine, operate_service=operate_service, workspace_ui_service=workspace_ui_service, health_callback=health_callback, goal_deriver=goal_deriver, build_operate_snapshot=build_operate_snapshot)
