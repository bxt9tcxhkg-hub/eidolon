from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from eidolon.chat_error_support import is_synthetic_chat_session_source
from eidolon.work_context_intent import resolve_open_intent
from eidolon.workspaces.vorhaben_extract import extract_vorhaben, looks_like_vorhaben


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def skip_candidate_capture(source: str | None) -> bool:
    lowered = str(source or '').strip().casefold()
    if not lowered:
        return False
    return is_synthetic_chat_session_source(source) or lowered == 'test' or lowered.startswith('test')


def _workspace_id_for(title: str) -> str:
    token = hashlib.sha1(title.casefold().encode('utf-8')).hexdigest()[:10]
    return f'ws_msg_{token}'


def _has_active_project(payload: dict[str, Any] | None) -> bool:
    for workspace in list((payload or {}).get('workspaces') or []):
        if workspace.get('product_state') == 'active_project':
            return True
    return False


def persist_message_candidate(registry, extracted: dict[str, Any]) -> dict[str, Any]:
    title = str(extracted.get('title') or 'Neues Vorhaben')
    workspace_id = _workspace_id_for(title)
    data = registry.snapshot()
    workspaces = list(data.get('workspaces') or [])
    existing = next((item for item in workspaces if item.get('workspace_id') == workspace_id), None)
    if existing and existing.get('product_state') == 'active_project':
        return existing
    metadata = {
        **dict((existing or {}).get('metadata') or {}),
        'source': 'message_candidate',
        'source_message': extracted.get('source_message') or '',
        'project_description': extracted.get('summary') or '',
        'formation_confirmed': False,
        'formation_source': 'visible_proactive_formation',
        'product_state': 'project_candidate',
        'stored_product_state': 'project_candidate',
        'action_relevance': float(extracted.get('action_relevance') or 0.8),
        'recurrence_score': float(extracted.get('recurrence_score') or 0.35),
        'why': extracted.get('why') or 'Du hast ein Vorhaben beschrieben, das mehr als eine einzelne Antwort braucht.',
        'plan_cards': list(extracted.get('cards') or []),
        'consequential_approval': extracted.get('approval'),
    }
    workspace = {
        **dict(existing or {}),
        'workspace_id': workspace_id,
        'topic_label': title,
        'workspace_type': 'project_workspace',
        'layout_template': 'hybrid',
        'modules': ['board', 'next_actions', 'notes', 'details'],
        'state': 'suggested',
        'product_state': 'project_candidate',
        'health': 'ok',
        'last_updated': _now(),
        'metadata': metadata,
        'overview': extracted.get('summary') or title,
    }
    if existing:
        workspaces = [workspace if item.get('workspace_id') == workspace_id else item for item in workspaces]
    else:
        workspaces.append(workspace)
    data['workspaces'] = workspaces
    registry._save(data)
    return workspace


def capture_message_candidate(ui_service, message: str, session: dict[str, Any] | None = None, *, source: str = 'chat') -> dict[str, Any] | None:
    if skip_candidate_capture(source):
        return None
    text = str(message or '').strip()
    if not text:
        return None
    payload = ui_service.get_runtime_payload()
    intent = resolve_open_intent(text, workspace_payload=payload, session=session)
    vorhaben = extract_vorhaben(text)
    if not vorhaben:
        return None
    if intent.get('classification') == 'casual_chat':
        return None
    if _has_active_project(payload) and intent.get('classification') in {'continue_existing_work', 'repair_or_unblock', 'general_chat_with_work_context'}:
        return None
    if not (intent.get('is_work_oriented') or looks_like_vorhaben(text)):
        return None
    return persist_message_candidate(ui_service._registry, vorhaben)


def is_preserved_workspace(workspace: dict[str, Any] | None) -> bool:
    workspace = workspace or {}
    metadata = workspace.get('metadata') or {}
    if metadata.get('source') == 'message_candidate':
        return True
    if str(metadata.get('formation_source') or '') in {'visible_proactive_formation', 'user_confirmed_promotion'}:
        return True
    return workspace.get('product_state') in {'project_candidate', 'active_project'} and metadata.get('source_message')
