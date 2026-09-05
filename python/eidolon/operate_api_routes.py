from __future__ import annotations

from fastapi import FastAPI

from eidolon.operate_api_action_routes import register_operate_action_routes
from eidolon.operate_api_goal_routes import register_operate_goal_routes
from eidolon.operate_api_session_routes import register_operate_session_routes
from eidolon.operate_api_runs_routes import register_operate_runs_routes
from eidolon.operate_api_overview_routes import register_operate_overview_routes
from eidolon.operate_api_read_routes import register_operate_self_reflection_routes
from eidolon.operate_api_self_reflection_chat import register_self_reflection_chat_route
from eidolon.routes.operate_runtime import OperateRouteRuntime


def register_operate_api_routes(
    app: FastAPI,
    *,
    get_operate_service,
    autonomy_engine,
    goal_deriver,
    workspace_ui_service,
    health_callback,
    sync_operate_with_workspace_payload,
    build_operate_snapshot,
    goal_categories,
    autonomy_cycle_callback=None,
    llm_backend=None,
    get_settings_store=None,
) -> None:
    runtime = OperateRouteRuntime(
        get_operate_service=get_operate_service,
        workspace_ui_service=workspace_ui_service,
        sync_operate_with_workspace_payload=sync_operate_with_workspace_payload,
        build_operate_snapshot=build_operate_snapshot,
        autonomy_engine=autonomy_engine,
        goal_categories=goal_categories,
    )
    register_operate_session_routes(app, runtime=runtime, get_operate_service=get_operate_service, workspace_ui_service=workspace_ui_service)
    register_operate_runs_routes(app, runtime=runtime, get_operate_service=get_operate_service, workspace_ui_service=workspace_ui_service)
    register_operate_overview_routes(app, runtime=runtime, get_operate_service=get_operate_service, workspace_ui_service=workspace_ui_service)
    register_operate_self_reflection_routes(app, runtime=runtime, get_operate_service=get_operate_service, workspace_ui_service=workspace_ui_service)
    register_operate_goal_routes(app, runtime=runtime, autonomy_engine=autonomy_engine, goal_deriver=goal_deriver, workspace_ui_service=workspace_ui_service, health_callback=health_callback, autonomy_cycle_callback=autonomy_cycle_callback)
    register_operate_action_routes(app, runtime=runtime, get_operate_service=get_operate_service, sync_operate_with_workspace_payload=sync_operate_with_workspace_payload, build_operate_snapshot=build_operate_snapshot, workspace_ui_service=workspace_ui_service, get_settings_store=get_settings_store, get_llm_backend=(lambda: llm_backend) if llm_backend is not None else None)
    if llm_backend is not None:
        register_self_reflection_chat_route(app, get_operate_service=get_operate_service, get_llm_backend=lambda: llm_backend)
