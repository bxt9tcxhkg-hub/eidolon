from __future__ import annotations

from .contracts import ACTIVE_SUBAGENT_STATES


def summarize_subagent_runs(records):
    result = []
    for item in records:
        result.append({
            'id': item.id,
            'parent_run_id': item.parent_run_id,
            'objective_id': item.objective_id,
            'display_name': item.display_name,
            'function_type': item.function_type,
            'function_family': item.function_type,
            'mission': item.mission,
            'state': item.state,
            'state_reason': item.state_reason,
            'assigned_by': item.assigned_by,
            'blocking_issue_id': item.blocking_issue_id,
            'evidence_count': item.evidence_count,
            'output_count': item.output_count,
            'result_status': item.result_status,
            'started_at': item.started_at,
            'updated_at': item.updated_at,
            'ended_at': item.ended_at,
            'is_active': item.state in ACTIVE_SUBAGENT_STATES,
        })
    return result
