from __future__ import annotations

from typing import Any

from eidolon.chat_runtime_patterns import normalize_text, session_history, runtime_context_json


def build_chat_prompts(base_prompt: str | None, runtime_context: dict[str, Any]) -> tuple[str, str]:
    identity = normalize_text(base_prompt) or 'Du bist Eidolon.'
    intent = runtime_context.get('user_intent') or {}
    classification = intent.get('classification') or 'unknown'
    latest_message = intent.get('latest_message', '')

    system_parts = [identity]
    if classification in {'casual_chat', 'general_chat', 'general_chat_with_work_context'}:
        system_parts.extend([
            'Du bist Eidolon. Antworte auf soziale, persönliche oder allgemein-konversationelle Nachrichten als normaler Gesprächspartner.',
            'Deute lockere oder persönliche Nachrichten nicht automatisch in Projektarbeit, nächste Schritte oder operative Empfehlungen um.',
            'Wenn ein aktiver Arbeitskontext existiert, darfst du ihn kennen, aber nur dann aktivieren, wenn die Nachricht wirklich nach Arbeit, Planung, Analyse oder Umsetzung klingt.',
            'Bleibe ehrlich, direkt und natürlich. Erfinde keine Fähigkeiten, keine Nähe und keinen Projektfortschritt.',
            'RUNTIME_CONTEXT_JSON:\n' + runtime_context_json(runtime_context),
        ])
        user_prompt = (
            'Antworte auf Basis dieses Verlaufs und der letzten Nachricht als normale Unterhaltung. '
            'Nur wenn die Nachricht klar arbeitsorientiert ist, sollst du in Arbeitsmodus wechseln.\n\n'
            f'SESSION_VERLAUF:\n{session_history(runtime_context)}\n\n'
            f'LETZTE_NACHRICHT:\n{latest_message}\n'
        )
        return '\n\n'.join(part for part in system_parts if part), user_prompt

    system_parts.extend([
        'Du bist Eidolon. Bei arbeitsorientierten Nachrichten antwortest du als knapper Mitspieler, nicht als Essay-Berater.',
        'Antworte in höchstens 3–5 kurzen Zeilen. Kein Schema aus Intention, Richtungen oder Empfehlung. Keine Follow-up-Kataloge.',
        'Höchstens eine nächste Aktion oder eine Klärungsfrage — nicht beides, nicht eine Liste.',
        'Struktur lieber aufs Board legen („lege ich als Karte an“) statt im Chat aufzulisten.',
        'Frage nur zurück, wenn ohne die fehlende Information kein verantwortbarer nächster Zug möglich ist.',
        'Erfinde keinen Projektzustand, keine Fähigkeiten, keine Evidenz und keine bereits erfolgte Ausführung.',
        'RUNTIME_CONTEXT_JSON:\n' + runtime_context_json(runtime_context),
    ])
    user_prompt = (
        'Antworte auf Basis dieses Verlaufs und der letzten Nachricht. '
        'Kurz halten. Wenn Struktur nötig ist, biete eine Karte an statt eines Katalogs.\n\n'
        f'SESSION_VERLAUF:\n{session_history(runtime_context)}\n\n'
        f'LETZTE_NACHRICHT:\n{latest_message}\n'
    )
    return '\n\n'.join(part for part in system_parts if part), user_prompt
