from __future__ import annotations

from typing import Any

from eidolon.work_context_support import active_workspace, candidate_workspace, lower_text, recent_messages, workspace_summary, normalize_text


OPEN_WORK_PATTERNS = [
    'was können wir', 'was koennen wir', 'was können wir zwei', 'was koennen wir zwei',
    'wie gehen wir das an', 'und jetzt', 'wie weiter', 'wo fangen wir an', 'lass mal schauen',
    'lass uns schauen', 'was machen wir jetzt', 'wie packen wir das an', 'what can we do', 'where do we start',
]

SOCIAL_CHAT_PATTERNS = [
    'wer bist du', 'stell dich vor', 'erzähl mir von dir', 'erzaehl mir von dir',
    'ich will dich kennenlernen', 'ich will dass du mich kennenlernst', 'ich möchte dich kennenlernen',
    'ich moechte dich kennenlernen', 'kennenlernen', 'wie geht es dir', 'wie gehts dir',
    'lass uns reden', 'lass uns plaudern', 'plaudern', 'plauder', 'reden', 'unterhalten', 'smalltalk',
]

ACTION_HINTS: dict[str, tuple[str, ...]] = {
    'repair': ('fix', 'repar', 'debug', 'fehler', 'bug', 'entstör', 'unblock', 'blocker'),
    'build': ('bau', 'build', 'implement', 'umsetzen', 'create', 'erstellen', 'entwickeln', 'setz', 'do it'),
    'analyze': ('analys', 'warum', 'ursache', 'check', 'prüf', 'review', 'inspect'),
    'plan': ('plan', 'struktur', 'roadmap', 'prioris', 'schritte', 'nächste schritte'),
    'decide': ('entscheide', 'abwäg', 'option', 'vergleich', 'choose', 'pick'),
}


def _is_social_chat(text: str, lowered: str, explicit_mode: str) -> bool:
    if explicit_mode != 'unknown':
        return False
    if any(pattern in lowered for pattern in SOCIAL_CHAT_PATTERNS):
        return True
    tokens = text.split()
    if '?' in text and len(tokens) <= 6 and any(token in lowered for token in ('wer bist', 'what are you', 'who are you', 'wie geht', 'how are you')):
        return True
    return False


def resolve_open_intent(message: str, workspace_payload: dict[str, Any] | None = None, session: dict[str, Any] | None = None) -> dict[str, Any]:
    text = normalize_text(message)
    lowered = lower_text(text)
    context_model = (workspace_payload or {}).get('context_model') or {}
    active = active_workspace(workspace_payload)
    candidate = candidate_workspace(workspace_payload)
    active_summary = workspace_summary(active)
    has_blockers = int(active_summary.get('blocked', 0) or 0) > 0
    recent = recent_messages(session)

    explicit_mode = 'unknown'
    for mode, hints in ACTION_HINTS.items():
        if any(hint in lowered for hint in hints):
            explicit_mode = mode
            break

    open_work = any(pattern in lowered for pattern in OPEN_WORK_PATTERNS)
    if not open_work and '?' in text and len(text.split()) <= 10 and any(token in lowered for token in ('können', 'koennen', 'machen', 'weiter', 'start', 'anstellen', 'angehen')):
        open_work = True
    social_chat = _is_social_chat(text, lowered, explicit_mode)
    work_oriented = not social_chat and (open_work or explicit_mode != 'unknown')

    if social_chat:
        classification, mode_hint = 'casual_chat', 'chat'
    elif explicit_mode == 'repair' or has_blockers:
        classification, mode_hint = 'repair_or_unblock', 'repair'
    elif active:
        classification = 'continue_existing_work' if open_work else (explicit_mode if explicit_mode != 'unknown' else 'general_chat_with_work_context')
        mode_hint = 'continue' if classification == 'continue_existing_work' else (explicit_mode if explicit_mode != 'unknown' else 'chat')
    elif candidate:
        classification = 'choose_direction' if open_work else ('plan' if explicit_mode == 'unknown' else explicit_mode)
        mode_hint = 'decide' if open_work else explicit_mode
    elif context_model.get('chat_topic_count'):
        classification = 'explore_possibilities' if open_work else ('analyze' if explicit_mode == 'unknown' else explicit_mode)
        mode_hint = 'explore' if open_work else explicit_mode
    elif open_work:
        classification, mode_hint = 'start_from_nothing', 'explore'
    elif explicit_mode != 'unknown':
        classification = mode_hint = explicit_mode
    elif recent and any(token in lower_text(recent) for token in ('projekt', 'issue', 'bug', 'fix', 'plan', 'task', 'umsetzen')):
        classification, mode_hint = 'continue_existing_work', 'continue'
        work_oriented = True
    else:
        classification, mode_hint = 'general_chat', 'chat'

    return {
        'latest_message': text,
        'is_open_work_prompt': open_work,
        'is_work_oriented': work_oriented,
        'classification': classification,
        'mode_hint': mode_hint,
        'explicit_mode': explicit_mode,
        'reason': (
            'social_chat_prompt' if social_chat else
            'active_workspace_blocked' if has_blockers else
            'active_workspace_present' if active else
            'project_candidate_present' if candidate else
            'chat_topic_present' if context_model.get('chat_topic_count') else
            'open_work_prompt' if open_work else 'message_pattern'
        ),
    }
