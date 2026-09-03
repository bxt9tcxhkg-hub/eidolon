from __future__ import annotations

import json
from pathlib import Path

from eidolon.core.config import state_path
from eidolon.workspaces.domain_models import Task


class TaskStore:
    def __init__(self, project_root: Path):
        self._data_dir = state_path('user', 'workspace_domain_engine', project_root=project_root)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._tasks_file = self._data_dir / 'tasks.json'

    def load(self) -> dict[str, Task]:
        tasks: dict[str, Task] = {}
        if not self._tasks_file.exists():
            return tasks
        try:
            data = json.loads(self._tasks_file.read_text(encoding='utf-8'))
            for task_data in data.get('tasks', []):
                task = Task.from_dict(task_data)
                tasks[task.id] = task
        except (json.JSONDecodeError, OSError):
            return {}
        return tasks

    def save(self, tasks: dict[str, Task]) -> None:
        data = {'tasks': [task.to_dict() for task in tasks.values()]}
        try:
            self._tasks_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        except OSError:
            pass
