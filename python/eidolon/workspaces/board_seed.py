from __future__ import annotations

from typing import Any

from eidolon.operate.bridge import sync_operate_with_workspace_payload
from eidolon.workspaces.vorhaben_extract import extract_consequential_approval, extract_planning_cards


def source_text_from_workspace(workspace: dict[str, Any] | None, project=None) -> str:
    workspace = workspace or {}
    metadata = workspace.get('metadata') or {}
    parts = [
        metadata.get('source_message'),
        metadata.get('project_description'),
        workspace.get('overview'),
        workspace.get('topic_label'),
        getattr(project, 'description', None),
        getattr(project, 'title', None),
    ]
    return next((str(part).strip() for part in parts if str(part or '').strip()), '')


def seed_project_board(project_service, project, source_text: str) -> list[Any]:
    if project is None:
        return []
    existing = {str(element.title or '').casefold() for element in list(project.elements or [])}
    if existing:
        return []
    cards = extract_planning_cards(source_text, title=str(project.title or ''))
    created = []
    for card in cards:
        title = str(card.get('title') or '').strip()
        if not title or title.casefold() in existing:
            continue
        element = project_service.add_element(
            project.id,
            title=title,
            description=str(card.get('description') or ''),
            status=str(card.get('status') or 'planned'),
            element_type='task',
            tags=[f"slot:{card.get('slot') or 'open'}"],
        )
        if element is not None:
            created.append(element)
            existing.add(title.casefold())
    return created


def maybe_request_consequential_approval(ui_service, source_text: str) -> dict[str, Any] | None:
    spec = extract_consequential_approval(source_text)
    if spec is None:
        return None
    operate = ui_service._operate_service
    payload = ui_service.get_runtime_payload()
    synced = sync_operate_with_workspace_payload(operate, payload)
    run = (synced or {}).get('run') or operate.get_current_run()
    if run is None:
        return None
    pending = [item for item in operate.list_approval_gates(run.id) if getattr(item, 'status', None) == 'pending']
    if pending:
        return pending[0].to_dict()
    gate = operate.request_approval(run.id, title=spec['title'], summary=spec['summary'], action_type=spec['action_type'])
    return gate.to_dict()


def finish_confirmed_project(ui_service, workspace: dict[str, Any], project, *, seed_board: bool) -> tuple[Any, list[Any], dict[str, Any] | None]:
    if project is None:
        return None, [], None
    source_text = source_text_from_workspace(workspace, project)
    created = seed_project_board(ui_service._project_service, project, source_text) if seed_board else []
    project = ui_service._project_service.get_project(project.id) or project
    approval = maybe_request_consequential_approval(ui_service, source_text)
    return project, created, approval
