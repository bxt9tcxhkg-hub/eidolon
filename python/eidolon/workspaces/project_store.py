from __future__ import annotations

import json
from pathlib import Path

from eidolon.core.config import state_path
from eidolon.workspaces.project_entities import Project


class ProjectStore:
    def __init__(self, project_root: Path):
        self._root = Path(project_root)
        self._file = state_path('user', 'projects.json', project_root=self._root)
        self._file.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict:
        if not self._file.exists():
            return {'projects': []}
        try:
            return json.loads(self._file.read_text(encoding='utf-8'))
        except Exception:
            return {'projects': []}

    def _save(self, data: dict):
        self._file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    @staticmethod
    def _is_legacy_seed_project(project: Project) -> bool:
        return (
            project.title == 'Eidolon 2.0 — Agent Runtime'
            and project.description == 'Autonomer KI-Agent mit Mesh-Networking, Self-Healing und adaptiven Arbeitsbereichen.'
        )

    def list_projects(self) -> list[Project]:
        projects = [Project.from_dict(project) for project in self._load().get('projects', [])]
        return [project for project in projects if not self._is_legacy_seed_project(project)]

    def get_project(self, project_id: str) -> Project | None:
        for project in self._load().get('projects', []):
            if project.get('id') == project_id:
                materialized = Project.from_dict(project)
                return None if self._is_legacy_seed_project(materialized) else materialized
        return None

    def save_project(self, project: Project):
        data = self._load()
        projects = data.get('projects', [])
        for idx, existing in enumerate(projects):
            if existing.get('id') == project.id:
                projects[idx] = project.to_dict()
                break
        else:
            projects.append(project.to_dict())
        data['projects'] = projects
        self._save(data)

    def delete_project(self, project_id: str):
        data = self._load()
        data['projects'] = [project for project in data.get('projects', []) if project.get('id') != project_id]
        self._save(data)
