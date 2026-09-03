from __future__ import annotations

from typing import Any

from eidolon.workspaces.project_model import Project
from eidolon.workspaces.workspace_support import project_to_workspace


def project_to_workspace_record(project: Project, registry) -> dict[str, Any]:
    workspace = project_to_workspace(project, registry.orchestrator)
    registry.state_store.update_state(workspace['workspace_id'], workspace['state_data'])
    return workspace


def project_backed_workspaces(project_service, registry) -> list[dict[str, Any]]:
    return [project_to_workspace_record(project, registry) for project in project_service.list_projects()]
