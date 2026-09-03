from __future__ import annotations


def has_active_workspace(workspaces: list[dict]) -> bool:
    return any((workspace or {}).get('state') == 'active' for workspace in (workspaces or []))


def should_surface(suggestion: dict, allow_visible: bool, has_active: bool, visible_count: int, max_visible: int) -> tuple[bool, str | None]:
    if not allow_visible:
        return False, 'disabled_by_user'
    if visible_count >= max_visible:
        return False, 'visibility_cap'
    mode = suggestion.get('assistance_mode')
    urgency = suggestion.get('urgency')
    workspace_active = suggestion.get('workspace_state') == 'active'
    priority = float(suggestion.get('priority_score', 0) or 0)
    if has_active and not workspace_active and mode == 'prepare' and urgency != 'high':
        return False, 'active_workspace_focus'
    if priority < 0.55 and urgency == 'low':
        return False, 'low_relevance'
    return True, None
