"""Selbstverbesserung: Domänen-Workspaces mit echter Aufgabenlogik.

Dieses Modul erweitert die generischen Workspace-Module um domänenspezifische
Aufgabenlogik — z.B. Projektmanagement mit echten Abhängigkeiten, Task-Status-Übergängen,
Deadline-Tracking und Next-Best-Action-Begründungen.
"""
from __future__ import annotations

from pathlib import Path

from eidolon.workspaces.domain_engine_mutations import add_dependency, remove_dependency, resolve_blocker, set_blocker, transition_task
from eidolon.workspaces.domain_engine_tasks import create_task, delete_task, get_task, list_tasks, update_task
from eidolon.workspaces.domain_engine_views import get_dependency_status, next_action, stats
from eidolon.workspaces.domain_models import Task
from eidolon.workspaces.domain_store import TaskStore


class WorkspaceDomainEngine:
    """Echte Aufgabenlogik für Domänen-Workspaces."""

    def __init__(self, project_root: Path):
        self._store = TaskStore(project_root)
        self._tasks: dict[str, Task] = self._store.load()

    def _save(self) -> None:
        self._store.save(self._tasks)

    def create_task(self, title: str, description: str = '', domain: str = 'project', priority: int = 0, owner: str = '', dependencies: list[str] | None = None, due_at: str = '', tags: list[str] | None = None) -> dict: return create_task(self, title=title, description=description, domain=domain, priority=priority, owner=owner, dependencies=dependencies, due_at=due_at, tags=tags)
    def get_task(self, task_id: str) -> dict: return get_task(self, task_id)
    def update_task(self, task_id: str, **kwargs) -> dict: return update_task(self, task_id, **kwargs)
    def delete_task(self, task_id: str) -> dict: return delete_task(self, task_id)
    def list_tasks(self, domain: str | None = None, status: str | None = None, owner: str | None = None) -> list[dict]: return list_tasks(self, domain=domain, status=status, owner=owner)
    def transition_task(self, task_id: str, new_status: str) -> dict: return transition_task(self, task_id, new_status)
    def set_blocker(self, task_id: str, reason: str) -> dict: return set_blocker(self, task_id, reason)
    def resolve_blocker(self, task_id: str, target_status: str = 'ready') -> dict: return resolve_blocker(self, task_id, target_status)
    def add_dependency(self, task_id: str, depends_on_id: str) -> dict: return add_dependency(self, task_id, depends_on_id)
    def remove_dependency(self, task_id: str, depends_on_id: str) -> dict: return remove_dependency(self, task_id, depends_on_id)
    def get_dependency_status(self, task_id: str) -> dict: return get_dependency_status(self, task_id)
    def next_best_action(self, workspace_type: str = 'project') -> dict: return next_action(self, workspace_type)
    def get_stats(self, workspace_type: str = 'project') -> dict: return stats(self, workspace_type)


_engine: WorkspaceDomainEngine | None = None


def get_domain_engine(project_root: Path) -> WorkspaceDomainEngine:
    global _engine
    if _engine is None:
        _engine = WorkspaceDomainEngine(project_root)
    return _engine
