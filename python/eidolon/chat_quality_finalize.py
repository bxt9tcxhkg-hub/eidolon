from __future__ import annotations

from eidolon.chat_runtime_patterns import normalize_text
from eidolon.chat_quality_checks import generic_help_offer, has_sufficient_context, identity_drift
from eidolon.chat_quality_fallbacks import build_grounded_fallback_reply


_NON_WORK_CLASSIFICATIONS = {'casual_chat', 'general_chat', 'general_chat_with_work_context'}
_WORK_CLASSIFICATIONS = {'repair_or_unblock', 'continue_existing_work', 'choose_direction', 'explore_possibilities', 'start_from_nothing', 'build', 'analyze', 'plan', 'decide'}
_NON_WORK_PUSH_MARKERS = (
    'was soll ich als nächstes',
    'was soll ich als naechstes',
    'was soll ich für dich erledigen',
    'was soll ich fuer dich erledigen',
    'ich arbeite als eidolon',
    'arbeitsauftrag',
    'projektarbeit',
    'weiterarbeiten',
)


def _classification(runtime_context: dict) -> str:
    return ((runtime_context.get('user_intent') or {}).get('classification') or 'unknown')


def _enforce_work_contract(runtime_context: dict) -> bool:
    intent = runtime_context.get('user_intent') or {}
    classification = _classification(runtime_context)
    if classification in _NON_WORK_CLASSIFICATIONS:
        return False
    return (bool(intent.get('is_work_oriented')) or classification in _WORK_CLASSIFICATIONS) and has_sufficient_context(runtime_context)


def _enforce_non_work_contract(runtime_context: dict) -> bool:
    return _classification(runtime_context) in _NON_WORK_CLASSIFICATIONS


def _non_work_reply_drift(reply: str, runtime_context: dict) -> bool:
    if not _enforce_non_work_contract(runtime_context):
        return False
    lowered = normalize_text(reply).casefold()
    return any(marker in lowered for marker in _NON_WORK_PUSH_MARKERS)


def finalize_chat_reply(reply: str, runtime_context: dict) -> tuple[str, dict]:
    reply = normalize_text(reply)
    quality = {
        'used_fallback': False,
        'identity_repaired': False,
        'generic_assistant_pattern': False,
        'non_work_drift': False,
        'intent_classification': (runtime_context.get('user_intent') or {}).get('classification'),
        'context_state': (runtime_context.get('workflow_state') or {}).get('current_context_state'),
        'contract_satisfied': True,
    }
    if identity_drift(reply):
        quality['identity_repaired'] = True
        reply = build_grounded_fallback_reply(runtime_context)
        quality['used_fallback'] = True
    if generic_help_offer(reply):
        quality['generic_assistant_pattern'] = True
        if _enforce_work_contract(runtime_context) or _enforce_non_work_contract(runtime_context):
            reply = build_grounded_fallback_reply(runtime_context)
            quality['used_fallback'] = True
    if _non_work_reply_drift(reply, runtime_context):
        quality['non_work_drift'] = True
        reply = build_grounded_fallback_reply(runtime_context)
        quality['used_fallback'] = True
    quality['contract_satisfied'] = not quality['generic_assistant_pattern'] and not quality['non_work_drift']
    return reply, quality
