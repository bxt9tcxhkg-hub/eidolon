from __future__ import annotations

from eidolon.operate.contracts import NextActionRecord


def derive_next_action(run, approvals, blockers) -> NextActionRecord:
    pending_approvals = [item for item in approvals if getattr(item, 'status', None) == 'pending']
    open_blockers = [item for item in blockers if getattr(item, 'status', None) == 'open']

    if pending_approvals:
        gate = pending_approvals[0]
        return NextActionRecord(
            kind='approval_request',
            title=gate.title,
            summary=gate.summary,
            evidence_refs=[],
            action_label='Entscheidung geben',
            action_enabled=True,
            action_reason_disabled=None,
        )

    if open_blockers:
        blocker = open_blockers[0]
        return NextActionRecord(
            kind='blocking_condition',
            title=blocker.title,
            summary=blocker.summary,
            evidence_refs=[],
            action_label='Blocker auflösen',
            action_enabled=bool(getattr(blocker, 'requires_user_action', False)),
            action_reason_disabled=None if getattr(blocker, 'requires_user_action', False) else 'Blocker braucht keine direkte Nutzeraktion',
        )

    if run is None or getattr(run, 'state', None) in {'completed', 'failed', 'cancelled'}:
        return NextActionRecord(
            kind='none',
            title=None,
            summary=None,
            evidence_refs=[],
            action_label=None,
            action_enabled=False,
            action_reason_disabled=None,
        )

    phase = getattr(run, 'current_phase', None) or 'understand'
    transition = getattr(run, 'next_transition', None)
    summary = getattr(run, 'state_reason', None) or 'Nächsten sinnvollen Arbeitsschritt fortsetzen.'
    return NextActionRecord(
        kind='next_step',
        title=f'Weiter von Phase {phase}',
        summary=summary,
        evidence_refs=[],
        action_label='Weiter',
        action_enabled=True,
        action_reason_disabled=None if transition else 'Kein weiterer Zustandsübergang definiert',
    )
