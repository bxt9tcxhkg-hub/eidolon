"""Seed planning cards from a confirmed Vorhaben.

Idempotenz / Replace-with-care
------------------------------
- Seeded cards are tagged ``seed:vorhaben`` plus ``slot:<id>``.
- Re-seed never creates a second card for the same slot or the same title
  (case-insensitive). Existing titles and ``slot:*`` tags win.
- Cards without the seed tag are treated as user-owned and are never
  replaced, renamed, or deleted.
- Seed cards that still carry ``seed:vorhaben`` keep their current title and
  notes; a second seed is a no-op for those slots instead of rewriting them.
- An empty board is filled once. A second confirm/seed only fills missing
  slots, so the board is not spammed with duplicates.
"""

from __future__ import annotations

from typing import Any

from eidolon.operate.bridge import sync_operate_with_workspace_payload
from eidolon.workspaces.vorhaben_extract import extract_consequential_approval, extract_planning_cards

SEED_TAG = 'seed:vorhaben'


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


def _slot_tag(element) -> str:
    for tag in list(getattr(element, 'tags', None) or []):
        text = str(tag)
        if text.startswith('slot:'):
            return text
    return ''


def _existing_seed_keys(project) -> tuple[set[str], set[str]]:
    slots: set[str] = set()
    titles: set[str] = set()
    for element in list(getattr(project, 'elements', None) or []):
        title = str(getattr(element, 'title', '') or '').strip().casefold()
        if title:
            titles.add(title)
        slot = _slot_tag(element)
        if slot:
            slots.add(slot)
    return slots, titles


def seed_project_board(project_service, project, source_text: str) -> list[Any]:
    if project is None:
        return []
    cards = extract_planning_cards(source_text, title=str(getattr(project, 'title', '') or ''))
    existing_slots, existing_titles = _existing_seed_keys(project)
    created = []
    for card in cards:
        title = str(card.get('title') or '').strip()
        slot = str(card.get('slot') or 'open')
        slot_tag = f'slot:{slot}'
        if not title or title.casefold() in existing_titles or slot_tag in existing_slots:
            continue
        metadata = dict(card.get('metadata') or {})
        metadata.setdefault('subtitle', card.get('subtitle') or card.get('description') or '')
        element = project_service.add_element(
            project.id,
            title=title,
            description=str(card.get('description') or ''),
            status=str(card.get('status') or 'planned'),
            element_type='task',
            tags=[slot_tag, SEED_TAG],
            domain_data=metadata,
        )
        if element is not None:
            created.append(element)
            existing_titles.add(title.casefold())
            existing_slots.add(slot_tag)
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
