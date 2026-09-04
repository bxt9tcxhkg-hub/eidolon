from __future__ import annotations

import uuid
from pathlib import Path

from eidolon.workspaces.project_entities import Project, ProjectElement
from eidolon.workspaces.project_store import ProjectStore
from eidolon.workspaces.project_support import now_iso, project_overview


class ProjectService:
    def __init__(self, project_root: Path):
        self._root = Path(project_root)
        self._store = ProjectStore(self._root)

    def create_project(self, title: str, description: str = '', domain: str = '') -> Project:
        project = Project(id=str(uuid.uuid4())[:12], title=title, description=description, domain=domain)
        self._store.save_project(project)
        return project

    def get_project(self, project_id: str) -> Project | None:
        return self._store.get_project(project_id)

    def list_projects(self) -> list[Project]:
        return self._store.list_projects()

    def delete_project(self, project_id: str):
        self._store.delete_project(project_id)

    def add_element(self, project_id: str, title: str, **kwargs) -> ProjectElement | None:
        project = self._store.get_project(project_id)
        if not project:
            return None
        element = ProjectElement(id=str(uuid.uuid4())[:8], title=title, **kwargs)
        project.elements.append(element)
        project.updated_at = now_iso()
        self._store.save_project(project)
        return element

    def update_element(self, project_id: str, element_id: str, **kwargs) -> ProjectElement | None:
        project = self._store.get_project(project_id)
        if not project:
            return None
        for element in project.elements:
            if element.id == element_id:
                for key, value in kwargs.items():
                    if hasattr(element, key):
                        setattr(element, key, value)
                element.updated_at = now_iso()
                project.updated_at = now_iso()
                self._store.save_project(project)
                return element
        return None

    def reorder_elements(self, project_id: str, element_ids: list[str]) -> Project | None:
        project = self._store.get_project(project_id)
        if not project:
            return None
        known = {element.id: element for element in project.elements}
        seen: set[str] = set()
        ordered: list[ProjectElement] = []
        for element_id in element_ids:
            element = known.get(element_id)
            if element and element_id not in seen:
                ordered.append(element)
                seen.add(element_id)
        for element in project.elements:
            if element.id not in seen:
                ordered.append(element)
        project.elements = ordered
        project.updated_at = now_iso()
        self._store.save_project(project)
        return project

    def delete_element(self, project_id: str, element_id: str) -> bool:
        project = self._store.get_project(project_id)
        if not project:
            return False
        project.elements = [element for element in project.elements if element.id != element_id]
        for element in project.elements:
            if element_id in element.dependencies:
                element.dependencies.remove(element_id)
        project.updated_at = now_iso()
        self._store.save_project(project)
        return True

    def add_to_inbox(self, project_id: str, text: str, source: str = 'user') -> dict | None:
        project = self._store.get_project(project_id)
        if not project:
            return None
        item = {'id': str(uuid.uuid4())[:8], 'text': text, 'source': source, 'created_at': now_iso(), 'processed': False}
        project.inbox.append(item)
        project.updated_at = now_iso()
        self._store.save_project(project)
        return item

    def get_overview(self, project_id: str) -> dict | None:
        project = self._store.get_project(project_id)
        if not project:
            return None
        return project_overview(project)
