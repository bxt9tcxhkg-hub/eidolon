from __future__ import annotations

from fastapi import FastAPI

from eidolon.core.llm_backend import configure_from_settings
from eidolon.core.settings_apply import apply_user_settings
from eidolon.operate_api_helpers import require_user_request
from eidolon.routes.api_response import api_v1_error, api_v1_ok


def register_operate_action_routes(app: FastAPI, *, runtime, get_operate_service, sync_operate_with_workspace_payload, build_operate_snapshot, workspace_ui_service, get_settings_store=None, get_llm_backend=None) -> None:
    @app.post('/api/v1/objectives')
    async def api_v1_create_objective(request: dict):
        service = get_operate_service()
        started = service.start_objective(
            user_request=require_user_request(request),
            title=request.get('title'),
            normalized_goal=request.get('normalized_goal'),
            scope_summary=request.get('scope_summary'),
            decomposition_mode=str(request.get('decomposition_mode') or 'undecided'),
            source_kind=str(request.get('source_kind') or 'chat'),
            current_view=str(request.get('current_view') or 'operate'),
            autonomy_mode=str(request.get('autonomy_mode') or 'bounded_autonomous'),
        )
        return api_v1_ok({key: value.to_dict() for key, value in started.items()})

    @app.post('/api/v1/session/sync-from-workspaces')
    async def api_v1_sync_from_workspaces():
        service = get_operate_service()
        synced = sync_operate_with_workspace_payload(service, workspace_ui_service.get_runtime_payload())
        if synced is None:
            return api_v1_ok({'session': None, 'objective': None, 'run': None, 'subagents': []})
        return api_v1_ok(build_operate_snapshot(service, synced['run'].id))

    @app.post('/api/v1/runs/{run_id}/advance')
    async def api_v1_advance_run(run_id: str, request: dict | None = None):
        request = request or {}
        try:
            service = get_operate_service()
            run = service.advance_run(run_id, reason=request.get('reason'))
        except KeyError:
            api_v1_error('run_not_found', 'Run nicht gefunden', status_code=404)
        except ValueError as exc:
            api_v1_error('invalid_transition', str(exc), status_code=400)
        return api_v1_ok({'run': run.to_dict()})

    @app.post('/api/v1/runs/{run_id}/request-approval')
    async def api_v1_request_approval(run_id: str, request: dict):
        title = str(request.get('title') or 'Freigabe erforderlich').strip()
        summary = str(request.get('summary') or 'Der aktuelle Schritt braucht eine Benutzerfreigabe').strip()
        action_type = str(request.get('action_type') or 'manual_review').strip()
        try:
            service = get_operate_service()
            approval = service.request_approval(run_id, title=title, summary=summary, action_type=action_type)
        except KeyError:
            api_v1_error('run_not_found', 'Run nicht gefunden', status_code=404)
        return api_v1_ok({'approval': approval.to_dict(), 'run': service.get_run(run_id).to_dict()})

    @app.post('/api/v1/runs/{run_id}/blockers/{blocking_issue_id}/resolve')
    async def api_v1_resolve_blocker(run_id: str, blocking_issue_id: str, request: dict | None = None):
        request = request or {}
        try:
            service = get_operate_service()
            updated_run = service.resolve_blocking_issue(blocking_issue_id, resume_state=str(request.get('resume_state') or 'planning'), state_reason=str(request.get('state_reason') or 'Blocking issue resolved'))
        except KeyError:
            api_v1_error('blocking_issue_not_found', 'Blocking Issue nicht gefunden', status_code=404)
        except ValueError as exc:
            api_v1_error('invalid_blocking_issue', str(exc), status_code=400)
        if updated_run.id != run_id:
            api_v1_error('run_mismatch', 'Blocking Issue gehört zu einem anderen Run', status_code=400)
        blocker = next((item for item in get_operate_service().list_blocking_issues(run_id) if item.id == blocking_issue_id), None)
        return api_v1_ok({'blocking_issue': blocker.to_dict() if blocker else None, 'run': updated_run.to_dict()})

    @app.post('/api/v1/runs/{run_id}/approval/{gate_id}')
    async def api_v1_resolve_approval(run_id: str, gate_id: str, request: dict | None = None):
        request = request or {}
        try:
            service = get_operate_service()
            approval = service.resolve_approval(gate_id, decision=str(request.get('decision') or 'approved'), resolved_by=str(request.get('resolved_by') or 'user'))
        except KeyError:
            api_v1_error('approval_not_found', 'Approval nicht gefunden', status_code=404)
        except ValueError as exc:
            api_v1_error('invalid_approval', str(exc), status_code=400)
        if approval.run_id != run_id:
            api_v1_error('run_mismatch', 'Approval gehört zu einem anderen Run', status_code=400)
        return api_v1_ok({'approval': approval.to_dict(), 'run': service.get_run(run_id).to_dict()})

    @app.post('/api/v1/runs/{run_id}/interrupt')
    async def api_v1_interrupt_run(run_id: str, request: dict):
        try:
            service = get_operate_service()
            updated_run = service.interrupt_run(run_id, interrupt_type=str(request.get('type') or 'redirect'), message=request.get('message'))
        except KeyError:
            api_v1_error('run_not_found', 'Run nicht gefunden', status_code=404)
        except ValueError as exc:
            api_v1_error('invalid_interrupt', str(exc), status_code=400)
        return api_v1_ok({'run': updated_run.to_dict()})

    @app.post('/api/v1/operate/settings/apply')
    async def api_v1_operate_apply_settings(request: dict):
        if get_settings_store is None:
            api_v1_error('settings_unavailable', 'Settings-Store ist nicht verdrahtet', status_code=503)
        payload = {
            'user_requested': bool(request.get('user_requested')),
            'area': request.get('area'),
            'values': request.get('values') or {},
            'reason': request.get('reason') or request.get('user_request') or 'Ausdrücklicher Nutzerwunsch über Operate',
            'error': request.get('error'),
        }

        def after_llm() -> None:
            if get_llm_backend is None:
                return
            configure_from_settings(get_settings_store().get_area('llm'), get_llm_backend())

        result = apply_user_settings(get_settings_store(), payload, after_llm=after_llm)
        if not result.get('ok'):
            api_v1_error('settings_apply_rejected', result.get('error') or 'Einstellungen nicht übernommen', status_code=400)
        public = {key: value for key, value in result.items() if key != 'settings' or isinstance(value, dict)}
        return api_v1_ok(public)
