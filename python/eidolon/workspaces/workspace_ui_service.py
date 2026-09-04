"""Workspace-UI-Service — verbindet Registry mit der Web-UI."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from eidolon.operate.service import get_operate_service
from eidolon.workspaces.project_model import get_project_service
from eidolon.workspaces.registry import WorkspaceRegistry
from eidolon.workspaces.workspace_actions import execute_workspace_action
from eidolon.workspaces.workspace_payloads import (
    merged_workspace_payload,
    overview_payload,
    project_to_workspace_record,
    workspace_detail_payload,
    unified_work_context,
)
from eidolon.workspaces.project_formation_apply import apply_workspace_formation
from eidolon.workspaces.work_truth import work_truth_fields


class WorkspaceUIService:
    """Bereitet Workspace-Daten für die Web-UI auf."""

    def __init__(self, project_root: Path):
        self._root = Path(project_root)
        self._registry = WorkspaceRegistry(self._root)
        self._project_service = get_project_service(self._root)
        self._operate_service = get_operate_service(self._root)

    def _project_to_workspace(self, project) -> dict[str, Any]:
        return project_to_workspace_record(project, self._registry)

    def _merged_workspace_payload(self) -> dict[str, Any]:
        return merged_workspace_payload(self._project_service, self._registry)

    def get_runtime_payload(self) -> dict:
        return self._merged_workspace_payload()

    def get_unified_work_context(self, message: str = '', session: dict[str, Any] | None = None, source: str = 'workspace') -> dict[str, Any]:
        data = self._merged_workspace_payload()
        return unified_work_context(self._registry, self._operate_service, data, message=message, session=session, source=source)

    def get_overview(self) -> dict:
        data = self._merged_workspace_payload()
        return overview_payload(self._registry, self._operate_service, data)

    def get_work_truth(self, *, project: dict | None = None) -> dict:
        return work_truth_fields(self.get_overview(), project=project)

    def apply_formation(self, workspace_id: str, to_state: str, *, confirmed: bool = False, reason: str = '') -> dict:
        return apply_workspace_formation(self, workspace_id, to_state, confirmed=confirmed, reason=reason)

    def get_workspace(self, workspace_id: str) -> dict | None:
        return workspace_detail_payload(self._project_service, self._registry, self._operate_service, workspace_id)

    def activate_workspace(self, workspace_id: str) -> dict:
        if workspace_id.startswith('project_'):
            project_id = workspace_id.removeprefix('project_')
            project = self._project_service.get_project(project_id)
            if project:
                project.status = 'active'
                project.updated_at = datetime.now(timezone.utc).isoformat()
                self._project_service._store.save_project(project)
                return self._project_to_workspace(project)
        return self._registry.set_workspace_state(workspace_id, 'active')

    def execute_workspace_action(self, workspace_id: str, module_id: str, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return execute_workspace_action(
            project_service=self._project_service,
            project_to_workspace_record=self._project_to_workspace,
            operate_service=self._operate_service,
            workspace_id=workspace_id,
            module_id=module_id,
            action=action,
            payload=payload,
        )

    def suspend_workspace(self, workspace_id: str) -> dict:
        if workspace_id.startswith('project_'):
            project_id = workspace_id.removeprefix('project_')
            project = self._project_service.get_project(project_id)
            if project:
                project.status = 'paused'
                project.updated_at = datetime.now(timezone.utc).isoformat()
                self._project_service._store.save_project(project)
                return self._project_to_workspace(project)
        return self._registry.set_workspace_state(workspace_id, 'suspended')

    def set_feature_flag(self, enabled: bool) -> dict:
        return self._registry.set_feature_flag(enabled)

    def refresh(self) -> dict:
        return self.get_overview()


_service: WorkspaceUIService | None = None


def get_workspace_ui_service(project_root: Path) -> WorkspaceUIService:
    global _service
    if _service is None:
        _service = WorkspaceUIService(project_root)
    return _service
