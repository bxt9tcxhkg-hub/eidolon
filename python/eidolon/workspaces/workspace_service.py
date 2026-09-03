"""Workspace-Service — verbindet die UI mit dem Domain Engine.

Bietet echtes CRUD an: Anlegen, Statuswechsel, Dependencies, Next-Best-Action.
Die Daten werden persistent gespeichert.
"""
from __future__ import annotations

from pathlib import Path

from eidolon.workspaces.domain_engine import get_domain_engine
from eidolon.workspaces.domain_models import VALID_TRANSITIONS
from eidolon.workspaces.workspace_service_support import allowed_transitions, domain_statuses, list_domains, overview
from eidolon.workspaces.workspace_service_tasks import add_dependency, create_task, delete_task, get_dependency_status, get_stats, get_task, list_tasks, next_best_action, remove_dependency, resolve_blocker, set_blocker, transition_task, update_task


class WorkspaceService:
    """Verwaltet Aufgaben in Domänen-Workspaces."""

    def __init__(self, project_root: Path):
        self._root = Path(project_root)
        self._engine = get_domain_engine(self._root)
        self._domains = list(VALID_TRANSITIONS.keys())

    def list_domains(self) -> list[dict]: return list_domains(self._domains)
    def domain_statuses(self, domain: str) -> dict[str, list[str]]: return domain_statuses(domain)
    def create_task(self, title: str, description: str = '', domain: str = 'project', priority: int = 0, dependencies: list[str] | None = None, due_at: str = '', tags: list[str] | None = None) -> dict: return create_task(self._engine, title=title, description=description, domain=domain, priority=priority, dependencies=dependencies, due_at=due_at, tags=tags)
    def get_task(self, task_id: str) -> dict: return get_task(self._engine, task_id)
    def update_task(self, task_id: str, **kwargs) -> dict: return update_task(self._engine, task_id, **kwargs)
    def delete_task(self, task_id: str) -> dict: return delete_task(self._engine, task_id)
    def list_tasks(self, domain: str | None = None, status: str | None = None) -> list[dict]: return list_tasks(self._engine, domain=domain, status=status)
    def transition_task(self, task_id: str, new_status: str) -> dict: return transition_task(self._engine, task_id, new_status)
    def allowed_transitions(self, task_id: str) -> list[str]: return allowed_transitions(self._engine, task_id)
    def set_blocker(self, task_id: str, reason: str) -> dict: return set_blocker(self._engine, task_id, reason)
    def resolve_blocker(self, task_id: str) -> dict: return resolve_blocker(self._engine, task_id)
    def add_dependency(self, task_id: str, depends_on_id: str) -> dict: return add_dependency(self._engine, task_id, depends_on_id)
    def remove_dependency(self, task_id: str, depends_on_id: str) -> dict: return remove_dependency(self._engine, task_id, depends_on_id)
    def get_dependency_status(self, task_id: str) -> dict: return get_dependency_status(self._engine, task_id)
    def next_best_action(self, domain: str = 'project') -> dict: return next_best_action(self._engine, domain)
    def get_stats(self, domain: str = 'project') -> dict: return get_stats(self._engine, domain)
    def get_overview(self) -> dict: return overview(self._engine, self._domains, list_domains)


_service: WorkspaceService | None = None


def get_workspace_service(project_root: Path) -> WorkspaceService:
    global _service
    if _service is None:
        _service = WorkspaceService(project_root)
    return _service
