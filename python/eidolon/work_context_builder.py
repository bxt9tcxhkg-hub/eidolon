from __future__ import annotations

from typing import Any

from eidolon.work_context_contracts import derive_capabilities, operate_context, session_context, workspace_context
from eidolon.work_context_intent import resolve_open_intent
from eidolon.work_context_projection import derive_project_context, derive_workflow_state, derive_workspace_context
from eidolon.workspaces.work_truth import describe_formation


def build_unified_work_context(message: str, session: dict[str, Any] | None, source: str, workspace_payload: dict[str, Any] | None, llm_status: dict[str, Any] | None, capability_payload: list[dict[str, Any]] | None, user_model: dict[str, Any] | None, operate_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    workspace_payload = workspace_payload or {}
    llm_status = llm_status or {}
    user_model = user_model or {}
    operate_snapshot = operate_snapshot or {}
    context_bits = derive_workspace_context(workspace_payload, operate_snapshot)
    intent = resolve_open_intent(message, workspace_payload=workspace_payload, session=session)
    workflow = derive_workflow_state(context_bits, user_model)
    return {
        'product': {'name': 'Eidolon', 'mode': 'work_leading_agent', 'primary_surface': 'chat', 'active_surface': 'chat', 'identity_summary': 'Eidolon is a work-leading agent inside a project workspace, not a generic assistant.'},
        'user_intent': {**intent, 'autonomy_preference': workflow['autonomy_preference']},
        'project_context': derive_project_context(context_bits, user_model),
        'workflow_state': {key: value for key, value in workflow.items() if key != 'autonomy_preference'},
        'capabilities': derive_capabilities(context_bits['active'], context_bits['candidate'], context_bits['operate_run'], context_bits['operate_subagents'], capability_payload, llm_status),
        'truth_contract': {'must_not_invent_state': True, 'must_not_invent_capabilities': True, 'must_distinguish_fact_from_inference': True, 'must_return_empty_recommendations_if_no_basis': True},
        'response_policy': {'default_open_intent_mode': 'orient_and_propose', 'require_recommendation_when_possible': True, 'require_next_step_when_possible': True, 'forbid_generic_help_offer': True, 'ask_only_on_real_blocker': True},
        'session_context': session_context(session, source, context_bits['operate_session']),
        'operate_context': operate_context(context_bits['operate_session'], context_bits['operate_objective'], context_bits['operate_run'], context_bits['operate_next_action'], context_bits['operate_blockers'], context_bits['operate_approvals'], context_bits['operate_subagents']),
        'workspace_context': workspace_context(context_bits['active'], context_bits['candidate'], context_bits['active_summary'], context_bits['next_actions'], context_bits['shown_suggestions'], context_bits['shown_topics']),
        'formation': describe_formation(workspace_payload, operate_snapshot),
    }
