from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from eidolon.workspaces.board_seed import finish_confirmed_project
from eidolon.workspaces.project_formation import FormationError, apply_transition


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _find_workspace(payload: dict[str, Any], workspace_id: str) -> dict[str, Any] | None:
    for workspace in list(payload.get('workspaces') or []):
        if workspace.get('workspace_id') == workspace_id:
            return workspace
    return None


def _sync_operate_context_kind(operate_service, to_state: str, workspace_id: str, reason: str) -> None:
    session = operate_service.get_current_session()
    if session is None:
        return
    operate_service.store.update_session(session.id, context_kind=to_state, linked_workspace_id=workspace_id, surface_reason=reason)


def apply_workspace_formation(ui_service, workspace_id: str, to_state: str, *, confirmed: bool = False, reason: str = '', seed_board: bool | None = None) -> dict[str, Any]:
    snapshot = ui_service._registry.snapshot()
    workspace = _find_workspace(snapshot, workspace_id)
    if workspace is None:
        workspace = _find_workspace(ui_service.get_overview(), workspace_id)
    if workspace is None:
        raise FormationError(f'Workspace nicht gefunden: {workspace_id}')
    from_state = str(workspace.get('product_state') or 'chat_topic')
    result = apply_transition(from_state, to_state, confirmed=confirmed, reason=reason)
    should_seed = seed_board if seed_board is not None else bool(to_state == 'active_project' and confirmed)
    if not result['changed']:
        project = None
        seeded: list[Any] = []
        approval = None
        if to_state == 'active_project' and should_seed:
            project_id = workspace_id.removeprefix('project_') if str(workspace_id).startswith('project_') else str((workspace.get('metadata') or {}).get('project_id') or '')
            project = ui_service._project_service.get_project(project_id) if project_id else None
            project, seeded, approval = finish_confirmed_project(ui_service, workspace, project, seed_board=True)
            if project is not None:
                workspace = ui_service._project_to_workspace(project)
        return {**result, 'workspace': workspace, 'project': project.to_dict() if project else None, 'seeded_elements': [item.to_dict() for item in seeded], 'approval': approval}

    project = None
    if to_state == 'active_project' and not str(workspace_id).startswith('project_'):
        project = ui_service._project_service.create_project(
            title=str(workspace.get('topic_label') or 'Neues Projekt'),
            description=str((workspace.get('metadata') or {}).get('project_description') or workspace.get('overview') or ''),
            domain=str((workspace.get('metadata') or {}).get('project_domain') or 'general'),
        )
        project.metadata = {
            **dict(project.metadata or {}),
            'formation_confirmed': True,
            'formation_source': 'user_confirmed_promotion',
            'product_state': 'active_project',
            'source_workspace_id': workspace_id,
            'source_message': (workspace.get('metadata') or {}).get('source_message') or '',
        }
        project.status = 'in_progress'
        project.updated_at = _now()
        ui_service._project_service._store.save_project(project)
        try:
            ui_service._registry.set_workspace_state(workspace_id, 'suspended')
        except KeyError:
            pass
        project, seeded, approval = finish_confirmed_project(ui_service, workspace, project, seed_board=should_seed)
        created = ui_service._project_to_workspace(project)
        _sync_operate_context_kind(ui_service._operate_service, 'active_project', created.get('workspace_id') or f'project_{project.id}', result['reason'])
        return {**result, 'workspace': created, 'project': project.to_dict(), 'seeded_elements': [item.to_dict() for item in seeded], 'approval': approval}

    if str(workspace_id).startswith('project_'):
        project_id = workspace_id.removeprefix('project_')
        project_obj = ui_service._project_service.get_project(project_id)
        if project_obj is None:
            raise FormationError(f'Projekt nicht gefunden: {project_id}')
        project_obj.metadata = {
            **dict(project_obj.metadata or {}),
            'formation_confirmed': bool(result.get('formation_confirmed')),
            'formation_source': result.get('formation_source'),
            'product_state': to_state,
        }
        if to_state == 'active_project' and project_obj.status in {'', 'active', 'planned'}:
            project_obj.status = 'in_progress'
        project_obj.updated_at = _now()
        ui_service._project_service._store.save_project(project_obj)
        if to_state == 'active_project' and should_seed:
            project_obj, seeded, approval = finish_confirmed_project(ui_service, workspace, project_obj, seed_board=True)
        else:
            seeded, approval = [], None
        updated = ui_service._project_to_workspace(project_obj)
        _sync_operate_context_kind(ui_service._operate_service, to_state, updated.get('workspace_id') or workspace_id, result['reason'])
        return {**result, 'workspace': updated, 'project': project_obj.to_dict(), 'seeded_elements': [item.to_dict() for item in seeded], 'approval': approval}

    metadata = dict(workspace.get('metadata') or {})
    metadata['formation_confirmed'] = bool(result.get('formation_confirmed'))
    metadata['formation_source'] = result.get('formation_source')
    metadata['product_state'] = to_state
    metadata['stored_product_state'] = to_state
    data = ui_service._registry.snapshot()
    for item in data.get('workspaces', []):
        if item.get('workspace_id') == workspace_id:
            item['product_state'] = to_state
            item['metadata'] = metadata
            item['last_updated'] = _now()
            if to_state == 'project_candidate' and item.get('state') == 'suggested':
                item['state'] = 'prepared'
            ui_service._registry._save(data)
            _sync_operate_context_kind(ui_service._operate_service, to_state, workspace_id, result['reason'])
            return {**result, 'workspace': item, 'project': None, 'seeded_elements': [], 'approval': None}
    raise FormationError(f'Workspace konnte nicht persistiert werden: {workspace_id}')
