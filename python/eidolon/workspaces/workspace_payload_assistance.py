from __future__ import annotations

from typing import Any


def _workspace_board_summary(workspace: dict[str, Any]) -> dict[str, Any]:
    board = ((workspace.get('state_data') or {}).get('module_data') or {}).get('board') or {}
    return dict(board.get('summary') or {})


def _blocked_project_suggestion(workspace: dict[str, Any]) -> dict[str, Any]:
    return {
        'suggestion_id': f"assist_project_blocked_{workspace['workspace_id']}",
        'topic_label': workspace.get('topic_label'),
        'workspace_id': workspace.get('workspace_id'),
        'workspace_state': workspace.get('state'),
        'workspace_type': workspace.get('workspace_type'),
        'confidence': 0.95,
        'priority_score': 0.98,
        'message': f"{workspace.get('topic_label')} hat sichtbare Blocker und braucht direkte Entstörung.",
        'status': 'new',
        'kind': 'project_blocker',
        'assistance_mode': 'execute',
        'urgency': 'high',
        'user_visible': True,
        'suppressed_reason': None,
    }


def _startable_project_suggestion(workspace: dict[str, Any]) -> dict[str, Any]:
    return {
        'suggestion_id': f"assist_project_start_{workspace['workspace_id']}",
        'topic_label': workspace.get('topic_label'),
        'workspace_id': workspace.get('workspace_id'),
        'workspace_state': workspace.get('state'),
        'workspace_type': workspace.get('workspace_type'),
        'confidence': 0.88,
        'priority_score': 0.9,
        'message': f"{workspace.get('topic_label')} hat bereite Schritte, aber keinen laufenden Fokus.",
        'status': 'new',
        'kind': 'start_execution',
        'assistance_mode': 'execute',
        'urgency': 'medium',
        'user_visible': True,
        'suppressed_reason': None,
    }


def merge_proactive_assistance(
    project_workspaces: list[dict[str, Any]],
    topic_payload: dict[str, Any],
    merged_workspaces: list[dict[str, Any]],
) -> dict[str, Any] | Any:
    suggestions = topic_payload.get('proactive_assistance', {})
    if not isinstance(suggestions, dict):
        return suggestions
    suggestion_list = list(suggestions.get('suggestions', []))
    for workspace in project_workspaces:
        summary = _workspace_board_summary(workspace)
        if summary.get('blocked'):
            suggestion_list.insert(0, _blocked_project_suggestion(workspace))
        elif summary.get('in_progress') == 0 and summary.get('ready'):
            suggestion_list.insert(0, _startable_project_suggestion(workspace))
    return {
        **suggestions,
        'suggestions': suggestion_list[:6],
        'policy': {
            **suggestions.get('policy', {}),
            'has_active_workspace': any(workspace.get('state') == 'active' for workspace in merged_workspaces),
        },
    }
