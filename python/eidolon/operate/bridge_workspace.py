from __future__ import annotations

from typing import Any

from eidolon.operate.bridge_workspace_bootstrap import spawn_bootstrap_subagents, workspace_seed_from_record
from eidolon.operate.bridge_workspace_transitions import align_run_state_from_summary, derive_decomposition_mode
from eidolon.work_context_support import workspace_next_actions, workspace_summary


def select_active_workspace(payload: dict[str, Any] | None) -> dict[str, Any] | None:
    workspaces = list((payload or {}).get('workspaces') or [])
    for workspace in workspaces:
        if workspace.get('state') == 'active' and workspace.get('workspace_type') == 'project_workspace':
            return workspace
    for workspace in workspaces:
        if workspace.get('state') == 'active':
            return workspace
    return None


__all__ = [
    'align_run_state_from_summary',
    'derive_decomposition_mode',
    'select_active_workspace',
    'spawn_bootstrap_subagents',
    'workspace_next_actions',
    'workspace_seed_from_record',
    'workspace_summary',
]
