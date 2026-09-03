from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from eidolon.core.config import state_path


class OrchestrationMemoryStore:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.path = state_path('user', 'orchestration_memory.json', project_root=self.project_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {'mode_action_stats': {}, 'mode_preferences': {}}
        try:
            return json.loads(self.path.read_text(encoding='utf-8'))
        except Exception:
            return {'mode_action_stats': {}, 'mode_preferences': {}}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def record_outcome(self, *, workspace_type: str, module_id: str, action: str, success: bool, metadata: dict[str, Any] | None = None) -> None:
        workspace_type = str(workspace_type or 'workspace')
        module_id = str(module_id or 'unknown')
        action = str(action or 'unknown')
        data = self._load()
        stats = data.setdefault('mode_action_stats', {})
        key = f'{workspace_type}::{module_id}::{action}'
        entry = stats.setdefault(key, {
            'workspace_type': workspace_type,
            'module_id': module_id,
            'action': action,
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
        entry['last_metadata'] = metadata or {}
        pref = data.setdefault('mode_preferences', {}).setdefault(workspace_type, {})
        pref[module_id] = max(entry['success_rate'], float(pref.get(module_id, 0.0)))
        self._save(data)

    def get_module_confidence(self, workspace_type: str, module_id: str, action: str) -> float:
        data = self._load()
        key = f'{workspace_type or "workspace"}::{module_id or "unknown"}::{action or "unknown"}'
        return float(((data.get('mode_action_stats') or {}).get(key) or {}).get('success_rate', 0.0))

    def snapshot(self) -> dict[str, Any]:
        return self._load()
