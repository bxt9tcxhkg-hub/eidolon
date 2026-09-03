from __future__ import annotations

from pathlib import Path
from typing import Any

from eidolon.workspaces.orchestration_memory import OrchestrationMemoryStore
from eidolon.workspaces.orchestrator_candidates import autonomy_posture, candidate_board, candidate_decision, candidate_next_actions, candidate_reflection, candidate_tracker
from eidolon.workspaces.orchestrator_support import default_snapshot


class WorkspaceOrchestrator:
    def __init__(self, project_root: str | Path | None = None):
        self.memory = OrchestrationMemoryStore(project_root) if project_root is not None else None

    def evaluate(self, workspace: dict[str, Any], topic: dict[str, Any] | None = None) -> dict[str, Any]:
        state = workspace.get('state_data') or {}
        module_data = state.get('module_data') or {}
        needs = (workspace.get('metadata') or {}).get('needs') or state.get('needs') or {}
        workspace_type = str(workspace.get('workspace_type') or state.get('workspace_type') or 'workspace')
        candidates = [candidate_next_actions(self, workspace_type, module_data.get('next_actions', {}), module_data.get('board', {}), needs)]
        if 'board' in module_data:
            candidates.append(candidate_board(self, workspace_type, module_data.get('board', {}), module_data.get('graph', {}), needs))
        if 'status_tracker' in module_data:
            candidates.append(candidate_tracker(self, workspace_type, module_data.get('status_tracker', {}), needs))
        if 'decision_matrix' in module_data:
            candidates.append(candidate_decision(self, workspace_type, module_data.get('decision_matrix', {}), needs))
        if 'journal' in module_data or 'reflection' in module_data:
            candidates.append(candidate_reflection(self, workspace_type, module_data.get('journal') or module_data.get('reflection', {}), needs))
        ranked = sorted([candidate for candidate in candidates if candidate], key=lambda item: item['priority_score'], reverse=True)
        next_best = ranked[0] if ranked else {'module_id': 'next_actions', 'action': 'add_item', 'label': 'Nächsten Schritt konkretisieren', 'priority_score': 0.1, 'reason': 'Fallback: kein stärkeres Signal vorhanden.', 'payload': {'label': 'Nächsten Schritt konkretisieren'}, 'learned_confidence': 0.0}
        return default_snapshot(workspace, next_best, ranked, autonomy_posture(needs, ranked), self.memory is not None)
