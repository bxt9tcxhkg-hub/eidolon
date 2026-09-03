from __future__ import annotations

from typing import Any

from eidolon.workspaces.domain_models import now_iso


def transition_task(engine, task_id: str, new_status: str) -> dict[str, Any]:
    task = engine._tasks.get(task_id)
    if not task:
        return {'ok': False, 'error': 'Nicht gefunden'}
    result = task.transition(new_status)
    if result['ok']:
        engine._save()
    return result


def set_blocker(engine, task_id: str, reason: str) -> dict[str, Any]:
    task = engine._tasks.get(task_id)
    if not task:
        return {'ok': False, 'error': 'Nicht gefunden'}
    task.blocker_reason = reason
    task.status = 'blocked'
    task.updated_at = now_iso()
    engine._save()
    return {'ok': True, 'task': task.to_dict()}


def resolve_blocker(engine, task_id: str, target_status: str = 'ready') -> dict[str, Any]:
    task = engine._tasks.get(task_id)
    if not task:
        return {'ok': False, 'error': 'Nicht gefunden'}
    if task.status != 'blocked':
        return {'ok': False, 'error': 'Task ist nicht blockiert'}
    task.blocker_reason = ''
    return transition_task(engine, task_id, target_status)


def add_dependency(engine, task_id: str, depends_on_id: str) -> dict[str, Any]:
    task = engine._tasks.get(task_id)
    if not task:
        return {'ok': False, 'error': 'Nicht gefunden'}
    if depends_on_id not in engine._tasks:
        return {'ok': False, 'error': f'Ziel-Task {depends_on_id} nicht gefunden'}
    if depends_on_id == task_id:
        return {'ok': False, 'error': 'Selbstabhängigkeit nicht erlaubt'}
    if depends_on_id not in task.dependencies:
        task.dependencies.append(depends_on_id)
        task.updated_at = now_iso()
        engine._save()
    return {'ok': True, 'task': task.to_dict()}


def remove_dependency(engine, task_id: str, depends_on_id: str) -> dict[str, Any]:
    task = engine._tasks.get(task_id)
    if not task:
        return {'ok': False, 'error': 'Nicht gefunden'}
    if depends_on_id in task.dependencies:
        task.dependencies.remove(depends_on_id)
        task.updated_at = now_iso()
        engine._save()
    return {'ok': True, 'task': task.to_dict()}
