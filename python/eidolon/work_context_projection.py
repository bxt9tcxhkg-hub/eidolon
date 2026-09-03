from __future__ import annotations

from typing import Any

from eidolon.domain.mission.state_machine import normalize_next_transition, normalize_phase_for_state
from eidolon.work_context_support import active_workspace, candidate_workspace, normalize_text, topics, visible_suggestions, workspace_next_actions, workspace_summary


def derive_workspace_context(workspace_payload: dict[str, Any], operate_snapshot: dict[str, Any]):
    context_model = workspace_payload.get('context_model') or {}
    operate_run = operate_snapshot.get('run') or {}
    operate_objective = operate_snapshot.get('objective') or {}
    operate_session = operate_snapshot.get('session') or {}
    operate_next_action = operate_snapshot.get('next_action') or {}
    operate_blockers = list(operate_snapshot.get('blockers') or [])
    operate_approvals = list(operate_snapshot.get('approvals') or [])
    operate_subagents = list(operate_snapshot.get('subagents') or [])
    active = active_workspace(workspace_payload)
    candidate = candidate_workspace(workspace_payload)
    active_summary = workspace_summary(active)
    next_actions = workspace_next_actions(active or candidate)
    shown_suggestions = visible_suggestions(workspace_payload)
    shown_topics = topics(workspace_payload)
    blocked_items = [
        {'label': normalize_text(item.get('label') or item.get('title')), 'reason': normalize_text(item.get('blocker_reason') or item.get('reason') or 'Blockiert')}
        for item in list(active_summary.get('blocked_items') or [])[:3]
        if normalize_text(item.get('label') or item.get('title'))
    ]
    return {
        'context_model': context_model,
        'operate_run': operate_run,
        'operate_objective': operate_objective,
        'operate_session': operate_session,
        'operate_next_action': operate_next_action,
        'operate_blockers': operate_blockers,
        'operate_approvals': operate_approvals,
        'operate_subagents': operate_subagents,
        'active': active,
        'candidate': candidate,
        'active_summary': active_summary,
        'next_actions': next_actions,
        'shown_suggestions': shown_suggestions,
        'shown_topics': shown_topics,
        'blocked_items': blocked_items,
    }


def derive_project_context(context_bits: dict[str, Any], user_model: dict[str, Any]) -> dict[str, Any]:
    active = context_bits['active']; candidate = context_bits['candidate']; next_actions = context_bits['next_actions']; blocked_items = context_bits['blocked_items']; shown_suggestions = context_bits['shown_suggestions']; shown_topics = context_bits['shown_topics']; operate_objective = context_bits['operate_objective']
    known_constraints = [item['reason'] for item in blocked_items if item.get('reason')]
    active_goal = (((active or {}).get('semantic_frame') or {}).get('primary_goal') or operate_objective.get('normalized_goal') or operate_objective.get('title') or (next_actions[0] if next_actions else None))
    active_problem = blocked_items[0]['label'] if blocked_items else None
    return {
        'active_project_id': (active or {}).get('workspace_id'),
        'active_project_title': (active or {}).get('topic_label'),
        'candidate_project_id': (candidate or {}).get('workspace_id'),
        'candidate_project_title': (candidate or {}).get('topic_label'),
        'active_goal': active_goal,
        'active_problem': active_problem,
        'known_constraints': known_constraints,
        'known_preferences': [
            f"language:{user_model.get('language', 'de')}",
            f"preferred_project_view:{user_model.get('preferred_project_view', 'hybrid')}",
            f"prefers_autonomy:{bool(user_model.get('prefers_autonomy', False))}",
            f"prefers_visual_planning:{bool(user_model.get('prefers_visual_planning', False))}",
        ],
        'relevant_artifacts': [item for item in [(active or {}).get('workspace_id'), (candidate or {}).get('workspace_id')] if item],
        'unresolved_questions': [item.get('topic_label') for item in shown_suggestions if item.get('topic_label')][:3],
        'recent_decisions': [],
        'topic_labels': [item.get('label') for item in shown_topics if item.get('label')],
    }


def derive_workflow_state(context_bits: dict[str, Any], user_model: dict[str, Any]) -> dict[str, Any]:
    context_model = context_bits['context_model']; operate_run = context_bits['operate_run']; operate_next_action = context_bits['operate_next_action']; operate_approvals = context_bits['operate_approvals']; active = context_bits['active']; blocked_items = context_bits['blocked_items']; operate_objective = context_bits['operate_objective']
    autonomy_preference = 'continue_until_blocked' if user_model.get('prefers_autonomy') else 'propose_first'
    current_context_state = context_model.get('current_context_state') or ('active_project' if active or operate_objective else 'no_live_context')
    current_phase = context_model.get('current_phase') or operate_run.get('canonical_phase') or normalize_phase_for_state(operate_run.get('state'), operate_run.get('current_phase')) or ('execute' if active else 'understand')
    next_transition_hint = context_model.get('next_transition') or operate_run.get('canonical_next_transition') or normalize_next_transition(operate_run.get('state'), operate_run.get('next_transition'))
    next_step = context_model.get('next_step') or operate_next_action.get('summary') or operate_next_action.get('title')
    if operate_run and not next_step and operate_run.get('state_reason'):
        next_step = operate_run.get('state_reason')
    return {
        'autonomy_preference': autonomy_preference,
        'current_phase': current_phase,
        'current_context_state': current_context_state,
        'next_transition_hint': next_transition_hint,
        'next_step': next_step,
        'blockers': blocked_items,
        'risks': [item['reason'] for item in blocked_items[:3]],
        'open_threads': [item.get('topic_label') for item in context_bits['shown_suggestions'] if item.get('topic_label')],
        'operate_run_state': operate_run.get('state'),
        'approval_required': bool(operate_run.get('approval_required') or operate_approvals),
        'pending_interrupt_count': int(operate_run.get('pending_interrupt_count') or 0),
    }
