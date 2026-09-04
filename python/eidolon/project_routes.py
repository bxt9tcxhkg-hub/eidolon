from __future__ import annotations

from fastapi import FastAPI, HTTPException

from eidolon.project_route_support import brainstorm_project, process_project_inbox_item, project_suggestions, require_project, update_project_record, truth_payload
from eidolon.workspaces.project_formation import FormationError


def register_project_routes(app: FastAPI, *, get_project_service, get_workspace_ui_service, get_operate_service, project_element_cls, record_workspace_action) -> None:
    def project_service(): return get_project_service()
    def workspace_ui_service(): return get_workspace_ui_service()
    def operate_service(): return get_operate_service()

    @app.get('/projects')
    async def list_projects():
        return {'projects': [p.to_dict() for p in project_service().list_projects()]}

    @app.get('/projects/{project_id}')
    async def get_project(project_id: str):
        project = require_project(project_service().get_project(project_id)).to_dict()
        truth = workspace_ui_service().get_work_truth(project=project)
        return {'project': project, **truth}

    @app.get('/projects/{project_id}/overview')
    async def get_project_overview(project_id: str):
        overview = project_service().get_overview(project_id)
        if not overview:
            raise HTTPException(status_code=404, detail='Nicht gefunden')
        return overview

    @app.post('/projects')
    async def create_project(request: dict):
        project = project_service().create_project(title=request.get('title', ''), description=request.get('description', ''), domain=request.get('domain', ''))
        return truth_payload(workspace_ui_service, {'project': project.to_dict()}, project=project.to_dict())

    @app.put('/projects/{project_id}')
    async def update_project(project_id: str, request: dict):
        project = update_project_record(project_service, project_id, request)
        return truth_payload(workspace_ui_service, {'project': project.to_dict()}, project=project.to_dict())

    @app.delete('/projects/{project_id}')
    async def delete_project(project_id: str):
        project_service().delete_project(project_id)
        return truth_payload(workspace_ui_service, {'project_id': project_id}, project_id=project_id)

    @app.post('/projects/{project_id}/elements')
    async def add_element(project_id: str, request: dict):
        element = project_service().add_element(project_id, title=request.get('title', ''), description=request.get('description', ''), status=request.get('status', 'idea'), priority=request.get('priority', 0), element_type=request.get('element_type', 'task'), tags=request.get('tags', []), dependencies=request.get('dependencies', []), assigned_to=request.get('assigned_to', ''), due_at=request.get('due_at', ''), domain=request.get('domain', ''), domain_data=request.get('domain_data', {}), position=request.get("position", {"x": 0, "y": 0}), parent_id=request.get("parent_id"))
        if not element:
            raise HTTPException(status_code=404, detail='Projekt nicht gefunden')
        payload = workspace_ui_service().get_runtime_payload()
        operate = record_workspace_action(operate_service(), payload, workspace_id=f'project_{project_id}', module_id='board', action='add_card', mutation_payload={'element_id': element.id, 'status': request.get('status', 'idea')}, changed=True, before_summary={}, after_summary=None, element_id=element.id, selection_reason='Project element created via project endpoint')
        project = project_service().get_project(project_id)
        return truth_payload(workspace_ui_service, {'element': element.to_dict(), 'operate': operate}, project=project.to_dict() if project else None)

    @app.post('/projects/{project_id}/elements/reorder')
    async def reorder_elements(project_id: str, request: dict):
        project = project_service().reorder_elements(project_id, request.get('element_ids') or [])
        if not project:
            raise HTTPException(status_code=404, detail='Projekt nicht gefunden')
        return truth_payload(workspace_ui_service, {'project': project.to_dict()}, project=project.to_dict())

    @app.put('/projects/{project_id}/elements/{element_id}')
    async def update_element(project_id: str, element_id: str, request: dict):
        element = project_service().update_element(project_id, element_id, **request)
        if not element:
            raise HTTPException(status_code=404, detail='Nicht gefunden')
        return truth_payload(workspace_ui_service, {'element': element.to_dict()}, element=element.to_dict())

    @app.delete('/projects/{project_id}/elements/{element_id}')
    async def delete_element(project_id: str, element_id: str):
        if not project_service().delete_element(project_id, element_id):
            raise HTTPException(status_code=404, detail='Nicht gefunden')
        return truth_payload(workspace_ui_service, {'project_id': project_id, 'element_id': element_id}, project_id=project_id, element_id=element_id)

    @app.post('/projects/{project_id}/inbox')
    async def add_to_inbox(project_id: str, request: dict):
        item = project_service().add_to_inbox(project_id, text=request.get('text', ''), source=request.get('source', 'user'))
        if not item:
            raise HTTPException(status_code=404, detail='Projekt nicht gefunden')
        return truth_payload(workspace_ui_service, {'item': item}, item=item)

    @app.post('/projects/{project_id}/inbox/{item_id}/process')
    async def process_inbox_item(project_id: str, item_id: str, request: dict):
        _ = request
        element = process_project_inbox_item(project_service, project_element_cls, project_id, item_id)
        return truth_payload(workspace_ui_service, {'element': element.to_dict()}, element=element.to_dict())

    @app.post('/projects/{project_id}/suggestions')
    async def generate_suggestions(project_id: str):
        project = require_project(project_service().get_project(project_id))
        return {'ok': True, 'suggestions': project_suggestions(project)}

    @app.post('/projects/{project_id}/brainstorm')
    async def brainstorm_suggestions(project_id: str, request: dict):
        project = require_project(project_service().get_project(project_id))
        return {'ok': True, 'suggestions': brainstorm_project(project, request.get('text', ''))}

    @app.post('/workspaces/formation')
    async def apply_formation(request: dict):
        workspace_id = str(request.get('workspace_id') or '')
        to_state = str(request.get('to_state') or '')
        if not workspace_id or not to_state:
            raise HTTPException(status_code=400, detail='workspace_id und to_state sind erforderlich')
        try:
            result = workspace_ui_service().apply_formation(
                workspace_id,
                to_state,
                confirmed=bool(request.get('confirmed')),
                reason=str(request.get('reason') or ''),
            )
        except FormationError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return truth_payload(workspace_ui_service, result, project=result.get('project'), formation_result=result)
