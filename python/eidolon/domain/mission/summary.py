from __future__ import annotations

from typing import Any

from .product_phases import build_phase_preservation_payload
from .state_machine import normalize_next_transition, normalize_phase_for_state


def build_run_summary(run, objective=None) -> dict[str, Any]:
    if run is None:
        return {}
    data = run.to_dict() if hasattr(run, 'to_dict') else dict(run)
    canonical_phase = normalize_phase_for_state(data.get('state'), data.get('current_phase'))
    canonical_next = normalize_next_transition(data.get('state'), data.get('next_transition'))
    data['canonical_phase'] = canonical_phase
    data['canonical_next_transition'] = canonical_next
    data['phase_preservation'] = build_phase_preservation_payload(
        run_state=data.get('state'),
        current_phase=data.get('current_phase'),
        context_state=None,
        has_objective=objective is not None,
        current_view=None,
        has_subagents=False,
        has_blocker=bool(data.get('blocking_issue_id')),
        has_approval=bool(data.get('approval_required')),
        result_status=data.get('result_status'),
    )
    if objective is not None:
        data['objective_title'] = getattr(objective, 'title', None)
        data['objective_goal'] = getattr(objective, 'normalized_goal', None)
    return data
