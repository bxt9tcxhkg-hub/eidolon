from __future__ import annotations

from typing import Any

PRODUCT_WORKFLOW_PHASES = (
    'chat_entry',
    'understand_and_structure',
    'context_classification',
    'project_formation',
    'workspace_composition',
    'responsibility_derivation',
    'execution',
    'verification_and_return',
)


def _phase_entry(preserved: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {'preserved': preserved, 'evidence': evidence}


def build_phase_preservation_payload(
    *,
    run_state: str | None,
    current_phase: str | None,
    context_state: str | None,
    has_objective: bool,
    current_view: str | None,
    has_subagents: bool,
    has_blocker: bool,
    has_approval: bool,
    result_status: str | None,
) -> dict[str, Any]:
    phase_status = {
        'chat_entry': _phase_entry(bool(current_view), {'current_view': current_view}),
        'understand_and_structure': _phase_entry(
            current_phase in {'understand', 'plan', 'execute', 'verify', 'finalize'} or run_state in {'understanding', 'planning', 'spawning_work', 'acting', 'waiting', 'blocked', 'verifying', 'completed', 'failed', 'cancelled'},
            {'run_state': run_state, 'current_phase': current_phase},
        ),
        'context_classification': _phase_entry(
            context_state in {'chat_topic', 'project_candidate', 'active_project', 'no_live_context'},
            {'context_state': context_state},
        ),
        'project_formation': _phase_entry(
            has_objective and context_state in {'project_candidate', 'active_project'},
            {'has_objective': has_objective, 'context_state': context_state},
        ),
        'workspace_composition': _phase_entry(
            current_view in {'operate', 'work_graph', 'history', 'settings', 'chat'},
            {'current_view': current_view},
        ),
        'responsibility_derivation': _phase_entry(
            has_subagents or has_blocker or has_approval,
            {
                'has_subagents': has_subagents,
                'has_blocker': has_blocker,
                'has_approval': has_approval,
            },
        ),
        'execution': _phase_entry(
            run_state in {'spawning_work', 'acting', 'waiting', 'blocked', 'verifying', 'completed'} or current_phase in {'execute', 'verify', 'finalize'},
            {'run_state': run_state, 'current_phase': current_phase},
        ),
        'verification_and_return': _phase_entry(
            run_state in {'verifying', 'completed', 'failed', 'cancelled'} or current_phase in {'verify', 'finalize'} or result_status in {'success', 'warning', 'failure'},
            {'run_state': run_state, 'current_phase': current_phase, 'result_status': result_status},
        ),
    }
    return {
        'workflow_phases': list(PRODUCT_WORKFLOW_PHASES),
        'phase_status': phase_status,
        'missing_phases': [],
    }
