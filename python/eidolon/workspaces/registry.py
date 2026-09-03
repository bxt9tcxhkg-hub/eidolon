from __future__ import annotations

from pathlib import Path
from typing import Any

from eidolon.core.config import state_path
from eidolon.user.proactive_assistance import ProactiveAssistanceStore
from eidolon.user.topic_attention import TopicAttentionStore
from eidolon.user.user_model import UserModelStore
from eidolon.workspaces.generator import WorkspaceGenerator
from eidolon.workspaces.orchestrator import WorkspaceOrchestrator
from eidolon.workspaces.registry_proposals import propose_from_topics
from eidolon.workspaces.registry_support import build_context_model, load_snapshot, save_snapshot
from eidolon.workspaces.state import WorkspaceStateStore


class WorkspaceRegistry:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.path = state_path('user', 'workspaces.json', project_root=self.project_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.user_model = UserModelStore(self.project_root)
        self.topics = TopicAttentionStore(self.project_root)
        self.generator = WorkspaceGenerator(self.project_root)
        self.state_store = WorkspaceStateStore(self.project_root)
        self.proactive_store = ProactiveAssistanceStore(self.project_root)
        self.orchestrator = WorkspaceOrchestrator(self.project_root)

    def _load(self) -> dict[str, Any]:
        return load_snapshot(self.path, {'workspaces': [], 'feature_flags': {'workspace_adaptive_modules': True}})

    def _save(self, data: dict[str, Any]) -> None:
        save_snapshot(self.path, data)

    def snapshot(self) -> dict[str, Any]:
        data = self._load()
        if not self.path.exists():
            self._save(data)
        return data

    def feature_enabled(self) -> bool:
        return bool(self.snapshot().get('feature_flags', {}).get('workspace_adaptive_modules', True))

    def propose_from_topics(self) -> dict[str, Any]:
        return propose_from_topics(self)

    def build_context_model(self, workspaces: list[dict[str, Any]]) -> dict[str, Any]:
        return build_context_model(workspaces)

    def set_workspace_state(self, workspace_id: str, state: str) -> dict[str, Any]:
        from eidolon.workspaces.contracts import map_workspace_state_to_product_state
        from datetime import datetime, timezone
        data = self.snapshot()
        for workspace in data.get('workspaces', []):
            if workspace.get('workspace_id') == workspace_id:
                workspace['state'] = state
                workspace['product_state'] = map_workspace_state_to_product_state(state, workspace.get('metadata') or {})
                workspace['last_updated'] = datetime.now(timezone.utc).isoformat()
                self._save(data)
                return workspace
        raise KeyError(workspace_id)

    def set_feature_flag(self, enabled: bool) -> dict[str, Any]:
        data = self.snapshot()
        data.setdefault('feature_flags', {})['workspace_adaptive_modules'] = bool(enabled)
        self._save(data)
        return data
