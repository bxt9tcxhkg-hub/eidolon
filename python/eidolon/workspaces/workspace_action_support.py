from __future__ import annotations

from typing import Any

from eidolon.workspaces.project_model import Project, ProjectElement
from eidolon.workspaces.workspace_support import project_summary


def require_project(project_service, workspace_id: str) -> Project:
    if not workspace_id.startswith('project_'):
        raise KeyError(workspace_id)
    project_id = workspace_id.removeprefix('project_')
    project = project_service.get_project(project_id)
    if not project:
        raise KeyError(workspace_id)
    return project


def indexed_element(elements: list[ProjectElement], payload: dict[str, Any]) -> ProjectElement:
    if not elements:
        raise ValueError('Projekt enthält noch keine Elemente')
    idx = max(0, min(int(payload.get('index', 0)), len(elements) - 1))
    return elements[idx]


def create_element(project_service, project_id: str, payload: dict[str, Any], default_title: str, default_notes: str):
    extras = {}
    if payload.get('sort_order') is not None:
        extras['sort_order'] = int(payload.get('sort_order') or 0)
    return project_service.add_element(project_id, title=str(payload.get('label') or default_title), description=str(payload.get('notes') or default_notes), status=str(payload.get('status') or 'planned'), priority=int(payload.get('priority', 0) or 0), element_type=str(payload.get('kind') or 'task'), assigned_to=str(payload.get('owner') or ''), dependencies=list(payload.get('dependency_ids') or []), position=payload.get('position') or {'x': 0, 'y': 0}, **extras)


def clean_selection_payload(payload: dict[str, Any]) -> tuple[dict[str, Any], str, Any, str]:
    selection_reason = str(payload.get('_selection_reason') or '')
    selection_score = payload.get('_selection_score')
    selection_source = str(payload.get('_selection_source') or 'workspace_orchestration')
    clean_payload = {k: v for k, v in payload.items() if not str(k).startswith('_')}
    return clean_payload, selection_reason, selection_score, selection_source
