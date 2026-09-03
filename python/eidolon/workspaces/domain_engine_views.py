from __future__ import annotations

from typing import Any

from eidolon.workspaces.domain_analysis import dependency_status, next_best_action, task_stats


def get_dependency_status(engine, task_id: str) -> dict[str, Any]:
    return dependency_status(engine._tasks, task_id)


def next_action(engine, workspace_type: str = 'project') -> dict[str, Any]:
    return next_best_action(engine._tasks, workspace_type)


def stats(engine, workspace_type: str = 'project') -> dict[str, Any]:
    return task_stats(engine._tasks, workspace_type)
