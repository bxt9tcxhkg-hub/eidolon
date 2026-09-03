from __future__ import annotations

import json
from typing import Any

GENERIC_ASSISTANT_PATTERNS = [
    'wie kann ich helfen',
    'wie kann ich dir helfen',
    'wie kann ich dir im kontext',
    'how can i help',
    'what would you like to do',
    'let me know what you need',
    'womit soll ich helfen',
    'was möchtest du machen',
    'wobei soll ich helfen',
]

OPEN_WORK_PATTERNS = [
    'was können wir',
    'was koennen wir',
    'was können wir zwei',
    'was koennen wir zwei',
    'wie gehen wir das an',
    'und jetzt',
    'wie weiter',
    'wo fangen wir an',
    'lass mal schauen',
    'lass uns schauen',
    'was machen wir jetzt',
    'wie packen wir das an',
    'what can we do',
    'where do we start',
]

ACTION_HINTS: dict[str, tuple[str, ...]] = {
    'repair': ('fix', 'repar', 'debug', 'fehler', 'bug', 'entstör', 'unblock', 'blocker'),
    'build': ('bau', 'build', 'implement', 'umsetzen', 'create', 'erstellen', 'entwickeln'),
    'analyze': ('analys', 'warum', 'ursache', 'check', 'prüf', 'review', 'inspect'),
    'plan': ('plan', 'struktur', 'roadmap', 'prioris', 'schritte', 'nächste schritte'),
    'decide': ('entscheide', 'abwäg', 'option', 'vergleich', 'choose', 'pick'),
}


def normalize_text(value: str | None) -> str:
    return ' '.join(str(value or '').strip().split())


def lower_text(value: str | None) -> str:
    return normalize_text(value).casefold()


def session_history(runtime_context: dict[str, Any]) -> str:
    recent_messages = runtime_context.get('session_context', {}).get('recent_messages') or []
    if not recent_messages:
        return '- Noch kein relevanter Verlauf vorhanden.'
    return '\n'.join(
        f"- {item.get('role', 'assistant')}: {item.get('content', '')}"
        for item in recent_messages[-6:]
    )


def runtime_context_json(runtime_context: dict[str, Any]) -> str:
    return json.dumps(runtime_context, ensure_ascii=False, indent=2)
