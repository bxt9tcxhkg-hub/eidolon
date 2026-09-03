from __future__ import annotations

from typing import Any

from eidolon.operate.service import OperateService


def spawn_bootstrap_subagents(service: OperateService, run_id: str, summary: dict[str, Any], next_actions: list[str]) -> None:
    created: set[tuple[str, str]] = set()
    for blocker in list(summary.get('blocked_items') or [])[:3]:
        label = str(blocker.get('label') or blocker.get('title') or '').strip()
        if not label:
            continue
        mission = f'Resolve blocker: {label}'
        key = ('blocker', mission)
        if key in created:
            continue
        service.spawn_subagent_run(
            run_id=run_id,
            display_name='Blocker Resolver',
            function_type='resolver',
            mission=mission,
            state_reason=str(blocker.get('blocker_reason') or 'Open blocker from active workspace'),
            assigned_by='workspace_bridge',
        )
        created.add(key)
    for action in next_actions[:3]:
        normalized = action.replace('Nächsten Schritt starten:', '').strip()
        mission = normalized or action
        key = ('action', mission)
        if key in created:
            continue
        service.spawn_subagent_run(
            run_id=run_id,
            display_name='Execution Stream',
            function_type='executor',
            mission=mission,
            state_reason='Derived from active workspace next actions',
            assigned_by='workspace_bridge',
        )
        created.add(key)
    if int(summary.get('done', 0)) > 0:
        mission = 'Verify completed project outputs against current objective state'
        key = ('verify', mission)
        if key not in created:
            service.spawn_subagent_run(
                run_id=run_id,
                display_name='Verification Stream',
                function_type='verifier',
                mission=mission,
                state_reason='Project already has completed items that need verification context',
                assigned_by='workspace_bridge',
            )


def workspace_seed_from_record(workspace: dict[str, Any]) -> tuple[str, str, str, str]:
    metadata = workspace.get('metadata') or {}
    state_data = workspace.get('state_data') or {}
    title = str(workspace.get('topic_label') or metadata.get('project_id') or 'Active Workspace').strip()
    user_request = str(metadata.get('project_description') or state_data.get('overview') or title).strip()
    workspace_id = str(workspace.get('workspace_id') or '')
    return title, user_request, workspace_id, str(metadata.get('project_id') or '')
