from __future__ import annotations

from typing import Any


def human_duration(seconds: int) -> str:
    if seconds < 60:
        return f'{seconds}s'
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f'{minutes}m {seconds}s'
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f'{hours}h {minutes}m'
    days, hours = divmod(hours, 24)
    return f'{days}d {hours}h'


def latest_session_user_message(session: dict[str, Any] | None) -> str:
    messages = list((session or {}).get('messages') or [])
    for item in reversed(messages):
        if str(item.get('role')) == 'user':
            return str(item.get('content') or '')
    return ''


def chat_runtime_truth_reply(message: str, llm_backend: Any) -> str | None:
    lowered = str(message or '').strip().casefold()
    if any(token in lowered for token in ('welches modell', 'which model', 'what model', 'welcher provider', 'which provider', 'running on', 'läufst du', 'laeufst du')):
        status = llm_backend.status()
        return (
            'Ich bin Eidolon, das zentrale agentische Hauptsystem dieses Produkts. '
            f"Aktuell läuft der Chat mit dem Modell {status.get('model') or 'unbekannt'} "
            f"über den Provider {status.get('provider') or 'unbekannt'}."
        )
    if any(token in lowered for token in ('wer bist du', 'stell dich vor', 'erzähl mir von dir', 'erzaehl mir von dir', 'kennenlern')):
        return (
            'Ich bin Eidolon, das zentrale agentische Hauptsystem dieses Produkts. '
            'Wenn du mich einfach normal kennenlernen willst, geht das auch ohne Arbeitsmodus: '
            'Wir können locker reden, Interessen abklopfen oder einfach schauen, wie ich antworte.'
        )
    return None
