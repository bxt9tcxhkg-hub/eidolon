from __future__ import annotations

from pathlib import Path

from eidolon.core.evidence import get_evidence_store
from eidolon.operate.service_objectives import open_blocking_issue, request_approval, resolve_blocking_issue, spawn_subagent_run, start_objective
from eidolon.operate.service_support import advance_run, emit_evidence, get_next_action, interrupt_run, resolve_approval, set_run_state, set_subagent_state
from eidolon.operate.store import OperateStore


class OperateService:
    def __init__(self, project_root: str | Path, db_path: str | Path | None = None, evidence_store=None):
        self.project_root = Path(project_root)
        self.store = OperateStore(db_path)
        self.evidence_store = evidence_store if evidence_store is not None else get_evidence_store()

    def start_objective(self, user_request: str, title: str | None = None, normalized_goal: str | None = None, scope_summary: str | None = None, decomposition_mode: str = 'undecided', source_kind: str = 'chat', current_view: str = 'operate', autonomy_mode: str = 'bounded_autonomous') -> dict[str, object]:
        return start_objective(self, user_request, title=title, normalized_goal=normalized_goal, scope_summary=scope_summary, decomposition_mode=decomposition_mode, source_kind=source_kind, current_view=current_view, autonomy_mode=autonomy_mode)

    def get_current_session(self):
        return self.store.get_current_session()

    def get_current_run(self):
        session = self.store.get_current_session()
        return self.store.get_run(session.current_run_id) if session and session.current_run_id else None

    def get_session(self, session_id: str):
        return self.store.get_session(session_id)

    def get_run(self, run_id: str):
        return self.store.get_run(run_id)

    def get_objective(self, objective_id: str):
        return self.store.get_objective(objective_id)

    def list_subagent_runs(self, run_id: str):
        return self.store.list_subagent_runs(run_id)

    def list_blocking_issues(self, run_id: str):
        return self.store.list_blocking_issues(run_id)

    def list_approval_gates(self, run_id: str):
        return self.store.list_approval_gates(run_id)

    def list_transition_events(self, run_id: str):
        return self.store.list_transition_events(run_id)

    def list_evidence_items(self, run_id: str):
        return self.store.list_evidence_items(run_id)

    def set_run_state(self, run_id: str, new_state: str, state_reason: str, current_phase: str | None = None, next_transition: str | None = None, result_status: str | None = None):
        return set_run_state(self, run_id, new_state, state_reason, current_phase=current_phase, next_transition=next_transition, result_status=result_status)

    def spawn_subagent_run(self, run_id: str, display_name: str, function_type: str, mission: str, state_reason: str, assigned_by: str = 'system'):
        return spawn_subagent_run(self, run_id, display_name, function_type, mission, state_reason, assigned_by=assigned_by)

    def set_subagent_state(self, subagent_id: str, new_state: str, state_reason: str, result_status: str | None = None):
        return set_subagent_state(self, subagent_id, new_state, state_reason, result_status=result_status)

    def open_blocking_issue(self, run_id: str, title: str, summary: str, category: str = 'runtime_error', requires_user_action: bool = True, resolution_hint: str | None = None):
        return open_blocking_issue(self, run_id, title, summary, category=category, requires_user_action=requires_user_action, resolution_hint=resolution_hint)

    def resolve_blocking_issue(self, issue_id: str, resume_state: str = 'planning', state_reason: str = 'Blocking issue resolved'):
        return resolve_blocking_issue(self, issue_id, resume_state=resume_state, state_reason=state_reason)

    def request_approval(self, run_id: str, title: str, summary: str, action_type: str):
        return request_approval(self, run_id, title, summary, action_type)

    def resolve_approval(self, gate_id: str, decision: str, resolved_by: str = 'user'):
        return resolve_approval(self, gate_id, decision, resolved_by=resolved_by)

    def emit_evidence(self, owner_type: str, owner_id: str, kind: str, title: str, summary: str, metadata_json: dict | None = None, artifact_ref: str | None = None):
        return emit_evidence(self, owner_type, owner_id, kind, title, summary, metadata_json=metadata_json, artifact_ref=artifact_ref)

    def get_next_action(self, run_id: str):
        return get_next_action(self, run_id)

    def interrupt_run(self, run_id: str, interrupt_type: str, message: str | None = None):
        return interrupt_run(self, run_id, interrupt_type, message=message)

    def advance_run(self, run_id: str, reason: str | None = None):
        return advance_run(self, run_id, reason=reason)


def get_operate_service(project_root: str | Path, db_path: str | Path | None = None, evidence_store=None) -> OperateService:
    return OperateService(project_root=project_root, db_path=db_path, evidence_store=evidence_store)
