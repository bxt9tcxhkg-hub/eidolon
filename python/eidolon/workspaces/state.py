from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

from eidolon.core.config import state_path
from eidolon.workspaces.state_contracts import normalize_workspace_contract
from eidolon.workspaces.state_support import build_default_module_data, build_default_state, refresh_project_derived_state


class WorkspaceStateStore:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.path = state_path('user', 'workspace_state.json', project_root=self.project_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {'workspaces': {}}
        try:
            return json.loads(self.path.read_text(encoding='utf-8'))
        except Exception:
            return {'workspaces': {}}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def snapshot(self) -> dict[str, Any]:
        data = self._load()
        if not self.path.exists():
            self._save(data)
        return data

    def ensure_workspace_state(self, workspace: dict[str, Any]) -> dict[str, Any]:
        data = self.snapshot()
        workspaces = data.setdefault('workspaces', {})
        workspace_id = workspace['workspace_id']
        normalized = normalize_workspace_contract(workspace)
        if workspace_id not in workspaces:
            workspaces[workspace_id] = build_default_state(normalized)
        else:
            current = workspaces[workspace_id]
            current['topic_label'] = normalized.get('topic_label', current.get('topic_label'))
            current['workspace_type'] = normalized.get('workspace_type', current.get('workspace_type'))
            current['layout_template'] = normalized.get('layout_template', current.get('layout_template'))
            current['modules'] = normalized.get('modules', current.get('modules', []))
            current['needs'] = (normalized.get('metadata') or {}).get('needs', current.get('needs', {}))
            current.setdefault('module_data', {})
            defaults = build_default_module_data(normalized.get('modules', []), current.get('next_actions', []), normalized)
            for module_name, module_default in defaults.items():
                existing_module = current['module_data'].get(module_name)
                legacy_empty = existing_module is not None and ((module_name == 'board' and 'items' not in existing_module) or (module_name == 'graph' and ('nodes' not in existing_module or 'edges' not in existing_module)) or (module_name == 'details' and 'selected_id' not in existing_module) or (module_name == 'dependencies' and 'items' not in existing_module))
                if existing_module is None or legacy_empty:
                    current['module_data'][module_name] = module_default
            current.setdefault('orchestration', {'recommended_mode': 'next_actions', 'ranked_modes': [], 'next_best_action': None, 'autonomy_posture': 'planning_support'})
            current = refresh_project_derived_state(current)
            current['updated_at'] = datetime.now(timezone.utc).isoformat()
            workspaces[workspace_id] = current
        workspaces[workspace_id] = refresh_project_derived_state(workspaces[workspace_id])
        self._save(data)
        return workspaces[workspace_id]

    def update_state(self, workspace_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        data = self.snapshot()
        current = data.setdefault('workspaces', {}).setdefault(workspace_id, {})
        current.update(updates)
        current['updated_at'] = datetime.now(timezone.utc).isoformat()
        self._save(data)
        return current
