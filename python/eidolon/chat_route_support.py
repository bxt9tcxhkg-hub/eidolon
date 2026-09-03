from __future__ import annotations


def session_payload(chat_session_store, session_id: str | None, source: str, message: str, chat_runtime_payload):
    session = chat_session_store.get_session(session_id) if session_id else None
    runtime_context = chat_runtime_payload(message, source, session)
    return session, runtime_context


def truth_quality(runtime_context: dict) -> dict:
    return {'used_fallback': False, 'identity_repaired': False, 'generic_assistant_pattern': False, 'intent_classification': runtime_context.get('user_intent', {}).get('classification'), 'context_state': runtime_context.get('workflow_state', {}).get('current_context_state'), 'contract_satisfied': True, 'path': 'runtime_truth'}
