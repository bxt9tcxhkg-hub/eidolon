from __future__ import annotations

from typing import Any

from eidolon.chat_runtime_patterns import normalize_text, session_history, runtime_context_json


def build_chat_prompts(base_prompt: str | None, runtime_context: dict[str, Any]) -> tuple[str, str]:
    identity = normalize_text(base_prompt) or 'Du bist Eidolon.'
    intent = runtime_context.get('user_intent') or {}
    classification = intent.get('classification') or 'unknown'
    work_oriented = bool(intent.get('is_work_oriented'))
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
        'Du bist nicht primär ein allgemeiner Chat-Assistent. Du bist der arbeitsführende Agent innerhalb eines laufenden Projekt- und Operate-Kontexts.',
        'Deine Aufgabe ist, Nutzerintention, Projektkontext, Workflow-Zustand und reale Fähigkeiten in Struktur, Richtung, Empfehlung und konkrete nächste Schritte zu überführen.',
        'Wenn genug Kontext vorhanden ist, antworte nicht mit generischen Hilfsangeboten.',
        'Bei offenen, arbeitsorientierten Eingaben sollst du die wahrscheinliche Intention benennen, 2-4 plausible Richtungen aus dem Kontext ableiten, eine begründete Empfehlung geben und einen konkreten nächsten Schritt anbieten.',
        'Frage nur dann zurück, wenn ohne die fehlende Information kein verantwortbarer nächster Schritt möglich ist.',
        'Erfinde keinen Projektzustand, keine Fähigkeiten, keine Evidenz und keine bereits erfolgte Ausführung.',
        'Eine starke Antwort ist kompakt, geerdet, richtungsbildend und umsetzbar.',
        'RUNTIME_CONTEXT_JSON:\n' + runtime_context_json(runtime_context),
    ])
    user_prompt = (
        'Arbeite auf Basis dieses aktuellen Verlaufs und der letzten Nachricht. '
        'Falls die Nachricht offen ist, führe die Arbeit mit Richtung, Empfehlung und nächstem Schritt.\n\n'
        f'SESSION_VERLAUF:\n{session_history(runtime_context)}\n\n'
        f'LETZTE_NACHRICHT:\n{latest_message}\n'
    )
    return '\n\n'.join(part for part in system_parts if part), user_prompt
