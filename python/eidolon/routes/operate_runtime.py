from __future__ import annotations

from typing import Any, Callable

from eidolon.routes.api_response import api_v1_error


class OperateRouteRuntime:
    def __init__(
        self,
        *,
        get_operate_service: Callable[[], Any],
        workspace_ui_service: Any,
        sync_operate_with_workspace_payload: Callable[[Any, dict[str, Any] | None], Any],
        build_operate_snapshot: Callable[[Any, str | None], dict[str, Any]],
        autonomy_engine: Any,
        goal_categories: list[str],
    ) -> None:
        self.get_operate_service = get_operate_service
        self.workspace_ui_service = workspace_ui_service
        self.sync_operate_with_workspace_payload = sync_operate_with_workspace_payload
        self.build_operate_snapshot = build_operate_snapshot
        self.autonomy_engine = autonomy_engine
        self.goal_categories = goal_categories

    def ensure_operate_bootstrap_from_workspace(self) -> None:
        service = self.get_operate_service()
        if service.get_current_run() is not None:
            return
        payload = self.workspace_ui_service.get_runtime_payload()
        self.sync_operate_with_workspace_payload(self.get_operate_service(), payload)

    def api_v1_run_or_404(self, run_id: str):
        service = self.get_operate_service()
        run = service.get_run(run_id)
        if run is None:
            api_v1_error('run_not_found', 'Run nicht gefunden', status_code=404)
        return run

    def api_v1_operate_snapshot(self, run_id: str | None = None):
        self.ensure_operate_bootstrap_from_workspace()
        return self.build_operate_snapshot(self.get_operate_service(), run_id)

    def api_v1_goal_payload(self, status: str | None = None, category: str | None = None):
        return {
            'goals': [g.to_dict() for g in self.autonomy_engine.list_goals(status=status, category=category)],
            'stats': self.autonomy_engine.get_stats(),
            'categories': self.goal_categories,
            'operate': self.api_v1_operate_snapshot(),
        }
