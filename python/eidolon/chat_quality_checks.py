from __future__ import annotations

from eidolon.chat_runtime_patterns import GENERIC_ASSISTANT_PATTERNS, lower_text


def generic_help_offer(reply: str) -> bool:
    lowered = lower_text(reply)
    return any(pattern in lowered for pattern in GENERIC_ASSISTANT_PATTERNS)


def identity_drift(reply: str) -> bool:
    lowered = lower_text(reply)
    bad_patterns = ['avatar der', 'final fantasy', 'genshin impact', 'eorzea', 'teyvat', 'ich bin ein geist', 'ich bin ein schatten', 'ich bin ein avatar', 'spiel-, film- oder fantasy']
    if any(pattern in lowered for pattern in bad_patterns):
        return True
    return 'ich bin eidolon' in lowered and 'system' not in lowered and 'produkt' not in lowered


def has_sufficient_context(runtime_context: dict) -> bool:
    workflow_state = runtime_context.get('workflow_state') or {}
    project_context = runtime_context.get('project_context') or {}
    session_context = runtime_context.get('session_context') or {}
    return any([workflow_state.get('current_context_state') not in {None, 'no_live_context'}, project_context.get('active_project_id'), project_context.get('candidate_project_id'), project_context.get('topic_labels'), int(session_context.get('message_count') or 0) > 1])
