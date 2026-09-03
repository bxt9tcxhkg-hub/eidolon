"""Projekt-Struktur für Eidolon."""
from __future__ import annotations

from pathlib import Path

from eidolon.workspaces.project_entities import Project, ProjectElement
from eidolon.workspaces.project_service import ProjectService
from eidolon.workspaces.project_store import ProjectStore

__all__ = [
    'Project',
    'ProjectElement',
    'ProjectService',
    'ProjectStore',
    'get_project_service',
]

_service: ProjectService | None = None


def get_project_service(project_root: Path) -> ProjectService:
    global _service
    if _service is None:
        _service = ProjectService(project_root)
    return _service
