from __future__ import annotations

from typing import Any


def overview_user_payload(user: dict[str, Any]) -> dict[str, Any]:
    preference_sources = user.get('preference_sources', {}) or {}
    return {
        'preferred_project_view': user.get('preferred_project_view', 'hybrid'),
        'prefers_visual_planning': user.get('prefers_visual_planning', True),
        'prefers_autonomy': user.get('prefers_autonomy', False),
        'ui_density': user.get('ui_density', 'comfortable'),
        'preference_sources': preference_sources,
        'preferences_are_defaults': all(source == 'default' for source in preference_sources.values()) if preference_sources else True,
    }
