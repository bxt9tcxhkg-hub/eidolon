from __future__ import annotations

from typing import Any


def normalize_text(value: str | None) -> str:
    return ' '.join(str(value or '').strip().split())


def lower_text(value: str | None) -> str:
    return normalize_text(value).casefold()


def recent_messages(session: dict[str, Any] | None, limit: int = 6) -> list[dict[str, str]]:
    items = list((session or {}).get('messages') or [])[-limit:]
    result = []
    for item in items:
        role = str(item.get('role') or 'assistant')
        content = normalize_text(item.get('content'))
        if content:
            result.append({'role': role, 'content': content[:400]})
    return result


def active_workspace(workspace_payload: dict[str, Any] | None) -> dict[str, Any] | None:
    workspaces = list((workspace_payload or {}).get('workspaces') or [])
    for workspace in workspaces:
        if workspace.get('product_state') == 'active_project':
            return workspace
    for workspace in workspaces:
        if workspace.get('state') == 'active':
            return workspace
    return None


def candidate_workspace(workspace_payload: dict[str, Any] | None) -> dict[str, Any] | None:
    for workspace in list((workspace_payload or {}).get('workspaces') or []):
        if workspace.get('product_state') == 'project_candidate':
            return workspace
    return None


def workspace_summary(workspace: dict[str, Any] | None) -> dict[str, Any]:
    module_data = (((workspace or {}).get('state_data') or {}).get('module_data') or {})
    board = module_data.get('board') or {}
    summary = dict(board.get('summary') or {})
    summary.setdefault('blocked', 0)
    summary.setdefault('in_progress', 0)
    summary.setdefault('ready', 0)
    summary.setdefault('done', 0)
    summary.setdefault('total', len(board.get('items') or []))
    summary.setdefault('blocked_items', [])
    return summary


def workspace_next_actions(workspace: dict[str, Any] | None) -> list[str]:
    state_data = (workspace or {}).get('state_data') or {}
    actions: list[str] = []
    for item in list(state_data.get('next_actions') or []):
        text = normalize_text(item)
        if text and text not in actions:
            actions.append(text)
    for item in ((((state_data.get('module_data') or {}).get('next_actions') or {}).get('items')) or []):
        text = normalize_text(item)
        if text and text not in actions:
            actions.append(text)
    return actions[:5]


def visible_suggestions(workspace_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    assistance = (workspace_payload or {}).get('proactive_assistance') or {}
    items = assistance.get('suggestions') or [] if isinstance(assistance, dict) else assistance
    visible = [item for item in items if not isinstance(item, dict) or item.get('user_visible', True)]
    return [item for item in visible if isinstance(item, dict)][:3]


def topics(workspace_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [item for item in list((workspace_payload or {}).get('topics') or []) if isinstance(item, dict)][:3]
