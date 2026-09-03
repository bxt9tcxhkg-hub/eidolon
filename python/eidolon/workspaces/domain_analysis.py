from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from eidolon.workspaces.domain_models import Task


def dependency_status(tasks: dict[str, Task], task_id: str) -> dict[str, Any]:
    task = tasks.get(task_id)
    if not task:
        return {'ok': False, 'error': 'Nicht gefunden'}
    deps_status = []
    all_done = True
    for dep_id in task.dependencies:
        dep = tasks.get(dep_id)
        if dep:
            done = dep.status == 'done'
            deps_status.append({'id': dep_id, 'title': dep.title, 'status': dep.status, 'done': done})
            if not done:
                all_done = False
        else:
            deps_status.append({'id': dep_id, 'title': '?', 'status': 'unknown', 'done': False})
            all_done = False
    return {'ok': True, 'task_id': task_id, 'all_dependencies_done': all_done, 'dependencies': deps_status}


def next_best_action(tasks: dict[str, Task], workspace_type: str = 'project') -> dict[str, Any]:
    scoped = [t for t in tasks.values() if t.domain == workspace_type or workspace_type == 'all']
    actionable = []
    for task in scoped:
        if task.status in ('done', 'cancelled', 'archived'):
            continue
        dep_state = dependency_status(tasks, task.id)
        actionable.append((task, dep_state.get('all_dependencies_done', False), task.priority))
    actionable.sort(key=lambda item: (-int(item[2]), -item[1]))
    if not actionable:
        return {'ok': True, 'action': None, 'reason': 'Keine ausführbaren Tasks'}
    task = actionable[0][0]
    if task.status == 'blocked':
        return {'ok': True, 'action': 'resolve_blocker', 'task_id': task.id, 'title': task.title, 'blocker': task.blocker_reason}
    if task.status in ('backlog', 'todo'):
        return {'ok': True, 'action': 'start_task', 'task_id': task.id, 'title': task.title, 'priority': task.priority}
    if task.status == 'ready':
        return {'ok': True, 'action': 'execute_task', 'task_id': task.id, 'title': task.title}
    return {'ok': True, 'action': 'continue_task', 'task_id': task.id, 'title': task.title, 'status': task.status}


def task_stats(tasks: dict[str, Task], workspace_type: str = 'project') -> dict[str, Any]:
    scoped = [t for t in tasks.values() if t.domain == workspace_type]
    statuses: dict[str, int] = {}
    for task in scoped:
        statuses[task.status] = statuses.get(task.status, 0) + 1
    blocked = [t for t in scoped if t.status == 'blocked']
    overdue = []
    now = datetime.now(timezone.utc)
    for task in scoped:
        if task.due_at and task.status != 'done':
            try:
                due = datetime.fromisoformat(task.due_at.replace('Z', '+00:00'))
                if due < now:
                    overdue.append({'id': task.id, 'title': task.title, 'due': task.due_at})
            except ValueError:
                pass
    return {
        'total': len(scoped),
        'statuses': statuses,
        'blocked_count': len(blocked),
        'overdue_count': len(overdue),
        'blocked': [{'id': t.id, 'title': t.title, 'reason': t.blocker_reason} for t in blocked],
        'overdue': overdue,
    }
