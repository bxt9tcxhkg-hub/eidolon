from __future__ import annotations

from eidolon.chat_runtime_patterns import lower_text, normalize_text


_AUTH_MARKERS = (
    'authrequired',
    'www-authenticate',
    'no access token was provided',
    'bearer error',
    'resource_metadata',
    'mcp.',
    'access token',
)

_REDACTABLE_ERROR_MARKERS = _AUTH_MARKERS + (
    'reading additional input from stdin',
    'rmcp:transport:worker',
    'transport channel closed',
    'codex-fehler (exit',
)

_SOCIAL_CHAT_MARKERS = (
    'wer bist du',
    'stell dich vor',
    'erzähl mir von dir',
    'erzaehl mir von dir',
    'kennenlern',
    'plaudern',
    'smalltalk',
    'unterhalten',
    'lass uns reden',
    'lass uns plaudern',
    'wie geht es dir',
    'wie gehts dir',
)

_WORK_DRIFT_MARKERS = (
    'was soll ich als nächstes',
    'was soll ich als naechstes',
    'was soll ich für dich erledigen',
    'was soll ich fuer dich erledigen',
    'ich bin bereit.',
    'ich arbeite als eidolon',
    'wie kann ich helfen?',
    'projektarbeit',
    'arbeitsauftrag',
)

_SYNTHETIC_SESSION_PREFIXES = ('test-', 'verify-', 'debug-')
_SYNTHETIC_SESSION_EXACT = {'pre-restart-check'}


def sanitize_chat_error(exc: Exception) -> tuple[str, str, str]:
    raw = normalize_text(str(exc))
    lowered = lower_text(raw)
    if not raw:
        return (
            'Modelllauf fehlgeschlagen. Die Ursache wurde intern nicht brauchbar geliefert.',
            'Das Modell-Backend hat keine verwendbare Fehlermeldung geliefert.',
            'backend_unknown',
        )
    if 'usage limit' in lowered or 'rate limit' in lowered:
        return (
            'OpenAI ist aktuell wegen eines Usage-Limits nicht verfügbar.',
            'OpenAI Usage-Limit erreicht. Upgrade zu Pro oder warte auf Reset.',
            'openai_usage_limit',
        )
    if any(marker in lowered for marker in _AUTH_MARKERS):
        return (
            'Das OpenAI/Codex-Backend ist aktuell nicht einsatzbereit, weil für einen abhängigen Auth- oder MCP-Dienst keine gültige Anmeldung verfügbar ist.',
            'OpenAI/Codex ist aktuell nicht einsatzbereit: Für einen abhängigen Auth- oder MCP-Dienst fehlt eine gültige Anmeldung.',
            'backend_auth_unavailable',
        )
    if 'reading additional input from stdin' in lowered:
        return (
            'Codex konnte in diesem nicht-interaktiven Lauf keine zusätzliche Eingabe anfordern.',
            'Codex konnte in diesem nicht-interaktiven Lauf keine zusätzliche Eingabe anfordern.',
            'codex_stdin_request',
        )
    if 'codex-cli nicht gefunden' in lowered or 'codex cli nicht gefunden' in lowered:
        return (
            'Das OpenAI/Codex-Backend ist auf diesem System nicht installiert.',
            'Codex-CLI nicht gefunden. Installiere OpenAI Codex.',
            'codex_missing',
        )
    if 'codex ist nicht eingeloggt' in lowered:
        return (
            'Das OpenAI/Codex-Backend ist aktuell nicht angemeldet.',
            'Codex ist nicht eingeloggt. Führe `codex login` aus.',
            'codex_not_logged_in',
        )
    if 'timed out' in lowered or 'abgebrochen' in lowered or 'timeout' in lowered:
        return (
            'Das Modell-Backend hat nicht rechtzeitig geantwortet.',
            'Modelllauf abgebrochen oder Zeitlimit erreicht.',
            'backend_timeout',
        )
    return (
        'Das Modell-Backend ist fehlgeschlagen. Die interne Detailspur wird nicht in den Chat gespiegelt.',
        'Modelllauf fehlgeschlagen. Interne Fehlerspur aus Sicherheits- und Verständlichkeitsgründen unterdrückt.',
        'backend_failure',
    )


def sanitize_chat_error_text(raw_error_text: str) -> str | None:
    raw = normalize_text(raw_error_text)
    lowered = lower_text(raw)
    if not raw or not any(marker in lowered for marker in _REDACTABLE_ERROR_MARKERS):
        return None
    assistant_message, _public_error, _error_code = sanitize_chat_error(RuntimeError(raw))
    return f'Fehler: {assistant_message}'


def is_synthetic_chat_session_source(source: str | None) -> bool:
    lowered = lower_text(source or '')
    return lowered in _SYNTHETIC_SESSION_EXACT or any(lowered.startswith(prefix) for prefix in _SYNTHETIC_SESSION_PREFIXES)


def prune_synthetic_chat_sessions(sessions: list[dict]) -> bool:
    kept = [session for session in sessions if not is_synthetic_chat_session_source(session.get('source'))]
    if len(kept) == len(sessions):
        return False
    sessions[:] = kept
    return True


def _is_social_user_prompt(text: str) -> bool:
    lowered = lower_text(text)
    return any(marker in lowered for marker in _SOCIAL_CHAT_MARKERS)


def _is_work_drift_reply(text: str) -> bool:
    lowered = lower_text(text)
    return any(marker in lowered for marker in _WORK_DRIFT_MARKERS)


def _social_chat_repair_reply(user_text: str) -> str:
    lowered = lower_text(user_text)
    if 'wer bist du' in lowered or 'stell dich vor' in lowered or 'erzähl mir von dir' in lowered or 'erzaehl mir von dir' in lowered:
        return 'Ich bin Eidolon, das zentrale agentische Hauptsystem dieses Produkts. Aber wir können auch ganz normal sprechen — nicht jede Unterhaltung muss sofort in Arbeit übersetzt werden.'
    if 'kennenlern' in lowered:
        return 'Ich bin Eidolon, das zentrale agentische Hauptsystem dieses Produkts. Wenn du mich einfach normal kennenlernen willst, geht das auch ohne Arbeitsmodus: Wir können locker reden, Interessen abklopfen oder einfach schauen, wie ich antworte.'
    return 'Wir können hier auch ganz normal sprechen. Wenn du plaudern, etwas diskutieren oder mich einfach kennenlernen willst, antworte ich darauf ohne es künstlich in Projektarbeit umzudeuten.'


def scrub_chat_sessions(sessions: list[dict]) -> bool:
    changed = False
    for session in sessions:
        messages = session.get('messages')
        if not isinstance(messages, list):
            continue
        previous_user_text = ''
        for message in messages:
            if not isinstance(message, dict):
                continue
            role = message.get('role')
            content = message.get('content')
            if role == 'user' and isinstance(content, str):
                previous_user_text = content
                continue
            if role != 'assistant' or not isinstance(content, str):
                continue
            sanitized = sanitize_chat_error_text(content)
            if sanitized and sanitized != content:
                message['content'] = sanitized
                changed = True
                continue
            if previous_user_text and _is_social_user_prompt(previous_user_text) and _is_work_drift_reply(content):
                repaired = _social_chat_repair_reply(previous_user_text)
                if repaired != content:
                    message['content'] = repaired
                    changed = True
    return changed
