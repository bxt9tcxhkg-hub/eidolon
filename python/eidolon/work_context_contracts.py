from __future__ import annotations

from typing import Any

from eidolon.work_context_support import recent_messages


def derive_capabilities(active, candidate, operate_run, operate_subagents, capability_payload, llm_status: dict[str, Any]) -> dict[str, Any]:
    available_runtime_capabilities = sorted({str(item.get('id')) for item in list(capability_payload or []) if isinstance(item, dict) and item.get('available')})
    return {
        'can_analyze': True,
        'can_plan': True,
        'can_summarize': True,
        'can_propose_options': True,
        'can_edit_workspace_state': bool(active),
        'can_create_tasks': bool(active or candidate),
        'can_execute_actions': bool(operate_run or active),
        'can_spawn_specialists': bool(operate_subagents or operate_run),
        'requires_approval_for_external_actions': True,
        'available_runtime_capabilities': available_runtime_capabilities,
        'provider': llm_status.get('provider'),
        'model': llm_status.get('model'),
    }


def session_context(session: dict[str, Any] | None, source: str, operate_session: dict[str, Any]) -> dict[str, Any]:
    return {
        'session_id': (session or {}).get('session_id'),
        'source': source,
        'message_count': int((session or {}).get('message_count') or len((session or {}).get('messages') or [])),
        'recent_messages': recent_messages(session),
        'current_view': operate_session.get('current_view') or 'chat',
    }


def operate_context(operate_session: dict[str, Any], operate_objective: dict[str, Any], operate_run: dict[str, Any], operate_next_action: dict[str, Any], operate_blockers: list[dict], operate_approvals: list[dict], operate_subagents: list[dict]) -> dict[str, Any]:
    return {
        'session_id': operate_session.get('id'),
        'session_title': operate_session.get('title'),
        'current_view': operate_session.get('current_view'),
        'objective_id': operate_objective.get('id'),
        'objective_title': operate_objective.get('title'),
        'run_id': operate_run.get('id'),
        'run_state': operate_run.get('state'),
        'next_action': operate_next_action,
        'approval_count': len(operate_approvals),
        'blocker_count': len(operate_blockers),
        'subagent_count': len(operate_subagents),
    }


def workspace_context(active, candidate, active_summary: dict[str, Any], next_actions: list[str], shown_suggestions: list[dict], shown_topics: list[dict]) -> dict[str, Any]:
    return {
        'active_workspace': {
            'workspace_id': (active or {}).get('workspace_id'),
            'topic_label': (active or {}).get('topic_label'),
            'workspace_type': (active or {}).get('workspace_type'),
            'state': (active or {}).get('state'),
            'summary': active_summary,
            'next_actions': next_actions,
        } if active else None,
        'candidate_workspace': {
            'workspace_id': (candidate or {}).get('workspace_id'),
            'topic_label': (candidate or {}).get('topic_label'),
            'workspace_type': (candidate or {}).get('workspace_type'),
            'state': (candidate or {}).get('state'),
        } if candidate else None,
        'visible_suggestions': shown_suggestions,
        'topics': shown_topics,
    }
