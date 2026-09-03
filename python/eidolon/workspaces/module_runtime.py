from __future__ import annotations

from typing import Any

from eidolon.workspaces.orchestration_memory import OrchestrationMemoryStore
from eidolon.workspaces.orchestrator import WorkspaceOrchestrator
from eidolon.workspaces.module_runtime_actions import apply_module_action
from eidolon.workspaces.module_runtime_support import sync_board_derivatives, workspace_view
from eidolon.workspaces.state import WorkspaceStateStore


class WorkspaceModuleRuntime:
    def __init__(self, state_store: WorkspaceStateStore):
        self.state_store = state_store
        self.orchestrator = WorkspaceOrchestrator(getattr(state_store, 'project_root', None))
        self.memory = OrchestrationMemoryStore(getattr(state_store, 'project_root', '.'))

    def apply_action(self, workspace_id: str, module_id: str, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        state = self.state_store.snapshot().get('workspaces', {}).get(workspace_id)
        if not state:
            raise KeyError(workspace_id)
        module_data = dict(state.get('module_data') or {})
        module_data, current, focus_card_id = apply_module_action(module_data, state, module_id, action, payload)
        module_data = sync_board_derivatives(module_data, focus_card_id=focus_card_id)
        updated = self.state_store.update_state(workspace_id, {'module_data': module_data})
        orchestration = self.orchestrator.evaluate(workspace_view(updated))
        updated = self.state_store.update_state(workspace_id, {'module_data': module_data, 'orchestration': orchestration})
        self.memory.record_outcome(workspace_type=updated.get('workspace_type', 'workspace'), module_id=module_id, action=action, success=True, metadata={'workspace_id': workspace_id, 'topic_label': updated.get('topic_label', ''), 'items': len(current.get('items', []) or []), 'entries': len(current.get('entries', []) or []), 'options': len(current.get('options', []) or [])})
        return {'workspace_id': workspace_id, 'module_id': module_id, 'action': action, 'module_state': current, 'workspace_state': updated, 'orchestration': orchestration}

    def record_feedback(self, workspace_id: str, module_id: str, action: str, success: bool, note: str = '') -> dict[str, Any]:
        state = self.state_store.snapshot().get('workspaces', {}).get(workspace_id)
        if not state:
            raise KeyError(workspace_id)
        self.memory.record_outcome(workspace_type=state.get('workspace_type', 'workspace'), module_id=module_id, action=action, success=bool(success), metadata={'workspace_id': workspace_id, 'note': note})
        orchestration = self.orchestrator.evaluate(workspace_view(state))
        updated = self.state_store.update_state(workspace_id, {'orchestration': orchestration})
        return {'ok': True, 'workspace_id': workspace_id, 'orchestration': orchestration, 'workspace_state': updated}
