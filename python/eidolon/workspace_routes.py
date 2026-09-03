from __future__ import annotations

from typing import Any, Callable

from fastapi import FastAPI

from eidolon.workspace_context_routes import register_workspace_context_routes
from eidolon.workspace_mutation_routes import register_workspace_mutation_routes


def register_workspace_routes(app: FastAPI, *, get_workspace_ui_service: Callable[[], Any], get_workspace_service: Callable[[], Any]) -> None:
    workspace_ui_service = lambda: get_workspace_ui_service()
    workspace_service = lambda: get_workspace_service()
    register_workspace_context_routes(app, workspace_ui_service=workspace_ui_service, workspace_service=workspace_service)
    register_workspace_mutation_routes(app, workspace_ui_service=workspace_ui_service, workspace_service=workspace_service)
