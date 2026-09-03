from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from eidolon.core.config import state_path

DEFAULT_USER_MODEL: dict[str, Any] = {
    'user_id': 'default',
    'language': 'de',
    'prefers_autonomy': True,
    'prefers_visual_planning': True,
    'preferred_project_view': 'hybrid',
    'prefers_function_over_design': True,
    'task_granularity': 'small',
    'likes_dependency_visibility': True,
    'ui_density': 'medium',
    'workspace_affinities': {},
    'workspace_preferences': {
        'default_layout': 'hybrid',
        'allow_proactive_suggestions': True,
        'core_shell_locked': True,
    },
    'preference_sources': {
        'language': 'default',
        'prefers_autonomy': 'default',
        'prefers_visual_planning': 'default',
        'preferred_project_view': 'default',
        'prefers_function_over_design': 'default',
        'task_granularity': 'default',
        'likes_dependency_visibility': 'default',
        'ui_density': 'default',
        'workspace_preferences': 'default',
    },
}


class UserModelStore:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.path = state_path('user', 'user_model.json', project_root=self.project_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return DEFAULT_USER_MODEL.copy()
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            merged = DEFAULT_USER_MODEL.copy()
            merged.update(data)
            merged['workspace_preferences'] = {
                **DEFAULT_USER_MODEL['workspace_preferences'],
                **(data.get('workspace_preferences') or {}),
            }
            merged['workspace_affinities'] = data.get('workspace_affinities') or {}
            merged['preference_sources'] = {
                **DEFAULT_USER_MODEL.get('preference_sources', {}),
                **(data.get('preference_sources') or {}),
            }
            return merged
        except Exception:
            return DEFAULT_USER_MODEL.copy()

    def _save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def get(self) -> dict[str, Any]:
        data = self._load()
        if not self.path.exists():
            self._save(data)
        return data

    def update_preferences(self, updates: dict[str, Any]) -> dict[str, Any]:
        current = self.get()
        for key, value in (updates or {}).items():
            if key == 'workspace_preferences' and isinstance(value, dict):
                current['workspace_preferences'] = {
                    **current.get('workspace_preferences', {}),
                    **value,
                }
                current.setdefault('preference_sources', {})['workspace_preferences'] = 'explicit'
            else:
                current[key] = value
                current.setdefault('preference_sources', {})[key] = 'explicit'
        self._save(current)
        return current
