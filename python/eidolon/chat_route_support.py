from __future__ import annotations

from typing import Any


def session_payload(chat_session_store, session_id: str | None, source: str, message: str, chat_runtime_payload):
    session = chat_session_store.get_session(session_id) if session_id else None
    runtime_context = chat_runtime_payload(message, source, session)
    return session, runtime_context


def operate_overview_from_context(runtime_context: dict[str, Any] | None) -> dict[str, Any]:
    operate = (runtime_context or {}).get('operate_context') or {}
    run_id = operate.get('run_id')
    run = None
    if run_id:
        run = {
            'id': run_id,
            'state': operate.get('run_state'),
            'state_reason': operate.get('run_state_reason'),
            'current_phase': operate.get('current_phase'),
            'pending_interrupt_count': int(operate.get('pending_interrupt_count') or 0),
            'interrupt_classification': operate.get('interrupt_classification'),
        }
    objective = None
    if operate.get('objective_id') or operate.get('objective_title'):
        objective = {'id': operate.get('objective_id'), 'title': operate.get('objective_title')}
    return {
        'run': run,
        'objective': objective,
        'blockers': list(operate.get('open_blockers') or []),
        'approvals': list(operate.get('pending_approvals') or []),
        'next_action': operate.get('next_action') or {'kind': 'none'},
        'source': 'chat_context',
    }


def truth_quality(runtime_context: dict) -> dict:
    return {'used_fallback': False, 'identity_repaired': False, 'generic_assistant_pattern': False, 'intent_classification': runtime_context.get('user_intent', {}).get('classification'), 'context_state': runtime_context.get('workflow_state', {}).get('current_context_state'), 'contract_satisfied': True, 'path': 'runtime_truth'}
