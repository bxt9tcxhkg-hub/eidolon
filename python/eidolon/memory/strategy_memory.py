from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from eidolon.core.config import state_path


class StrategyMemoryStore:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.path = state_path('autonomy', 'strategy_memory.json', project_root=self.project_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {'goal_action_stats': {}, 'goal_preferences': {}, 'workspace_action_stats': {}, 'workspace_preferences': {}}
        try:
            return json.loads(self.path.read_text(encoding='utf-8'))
        except Exception:
            return {'goal_action_stats': {}, 'goal_preferences': {}, 'workspace_action_stats': {}, 'workspace_preferences': {}}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def record_outcome(self, *, goal_type: str, action_type: str, success: bool, metadata: dict[str, Any] | None = None) -> None:
        goal_type = str(goal_type or 'operational')
        action_type = str(action_type or 'unknown')
        metadata = metadata or {}
        data = self._load()
        stats = data.setdefault('goal_action_stats', {})
        key = f'{goal_type}::{action_type}'
        entry = stats.setdefault(key, {
            'goal_type': goal_type,
            'action_type': action_type,
            'attempts': 0,
            'successes': 0,
            'failures': 0,
            'last_metadata': {},
        })
        entry['attempts'] += 1
        if success:
            entry['successes'] += 1
        else:
            entry['failures'] += 1
        entry['success_rate'] = round((entry['successes'] / entry['attempts']) if entry['attempts'] else 0.0, 3)
        entry['last_metadata'] = metadata
        pref = data.setdefault('goal_preferences', {}).setdefault(goal_type, {})
        pref[action_type] = entry['success_rate']

        workspace_type = str(metadata.get('workspace_type') or '')
        if workspace_type:
            ws_stats = data.setdefault('workspace_action_stats', {})
            ws_key = f'{workspace_type}::{action_type}'
            ws_entry = ws_stats.setdefault(ws_key, {
                'workspace_type': workspace_type,
                'action_type': action_type,
                'attempts': 0,
                'successes': 0,
                'failures': 0,
                'last_metadata': {},
            })
            ws_entry['attempts'] += 1
            if success:
                ws_entry['successes'] += 1
            else:
                ws_entry['failures'] += 1
            ws_entry['success_rate'] = round((ws_entry['successes'] / ws_entry['attempts']) if ws_entry['attempts'] else 0.0, 3)
            ws_entry['last_metadata'] = metadata
            ws_pref = data.setdefault('workspace_preferences', {}).setdefault(workspace_type, {})
            ws_pref[action_type] = ws_entry['success_rate']
        self._save(data)


    def get_workspace_action_confidence(self, workspace_type: str, action_type: str) -> float:
        data = self._load()
        key = f'{workspace_type or "workspace"}::{action_type or "unknown"}'
        return float(((data.get('workspace_action_stats') or {}).get(key) or {}).get('success_rate', 0.0))

    def get_action_confidence(self, goal_type: str, action_type: str) -> float:
        data = self._load()
        key = f'{goal_type}::{action_type}'
        return float(((data.get('goal_action_stats') or {}).get(key) or {}).get('success_rate', 0.0))

    def snapshot(self) -> dict[str, Any]:
        return self._load()
