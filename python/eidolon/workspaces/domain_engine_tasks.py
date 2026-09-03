from __future__ import annotations

import uuid
from typing import Any

from eidolon.workspaces.domain_models import Task, now_iso, start_status_for_domain


def create_task(engine, title: str, description: str = '', domain: str = 'project', priority: int = 0, owner: str = '', dependencies: list[str] | None = None, due_at: str = '', tags: list[str] | None = None) -> dict[str, Any]:
    task_id = str(uuid.uuid4())[:12]
    task = Task(id=task_id, title=title, description=description, status=start_status_for_domain(domain), domain=domain, priority=priority, owner=owner, dependencies=dependencies or [], due_at=due_at, tags=tags or [])
    engine._tasks[task_id] = task
    engine._save()
    return {'ok': True, 'task': task.to_dict()}


def get_task(engine, task_id: str) -> dict[str, Any]:
    task = engine._tasks.get(task_id)
    return {'ok': True, 'task': task.to_dict()} if task else {'ok': False, 'error': 'Nicht gefunden'}


def update_task(engine, task_id: str, **kwargs: Any) -> dict[str, Any]:
    task = engine._tasks.get(task_id)
    if not task:
        return {'ok': False, 'error': 'Nicht gefunden'}
    for key, value in kwargs.items():
        if hasattr(task, key):
            setattr(task, key, value)
    task.updated_at = now_iso()
    engine._save()
    return {'ok': True, 'task': task.to_dict()}


def delete_task(engine, task_id: str) -> dict[str, Any]:
    if task_id not in engine._tasks:
        return {'ok': False, 'error': 'Nicht gefunden'}
    del engine._tasks[task_id]
    engine._save()
    return {'ok': True}


def list_tasks(engine, domain: str | None = None, status: str | None = None, owner: str | None = None) -> list[dict[str, Any]]:
    tasks = list(engine._tasks.values())
    if domain:
        tasks = [task for task in tasks if task.domain == domain]
    if status:
        tasks = [task for task in tasks if task.status == status]
    if owner:
        tasks = [task for task in tasks if task.owner == owner]
    tasks.sort(key=lambda task: (-task.priority, task.created_at))
    return [task.to_dict() for task in tasks]
