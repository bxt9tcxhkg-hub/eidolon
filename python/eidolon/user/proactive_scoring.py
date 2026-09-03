from __future__ import annotations


def assistance_mode(topic: dict, workspace: dict | None) -> str:
    relevance = float(topic.get('action_relevance', 0))
    recurrence = float(topic.get('recurrence_score', 0))
    state = (workspace or {}).get('state', 'suggested')
    if state == 'active' and relevance >= 0.7:
        return 'execute'
    if state == 'active':
        return 'prepare'
    if recurrence >= 0.45 or relevance >= 0.75:
        return 'offer'
    return 'prepare'


def urgency(topic: dict) -> str:
    relevance = float(topic.get('action_relevance', 0))
    recurrence = float(topic.get('recurrence_score', 0))
    if relevance >= 0.85 or recurrence >= 0.55:
        return 'high'
    if relevance >= 0.65 or recurrence >= 0.35:
        return 'medium'
    return 'low'


def workspace_signal(workspace: dict | None) -> str:
    if not workspace:
        return 'Kein bestehender Arbeitsbereich vorhanden.'
    state = workspace.get('state', 'suggested')
    module_data = (workspace.get('state_data') or {}).get('module_data', {})
    summary = (module_data.get('board') or {}).get('summary') or {}
    if state == 'active' and summary:
        return f"Aktiver Bereich mit {summary.get('blocked', 0)} Blockern, {summary.get('in_progress', 0)} laufenden Aufgaben und {summary.get('ready', 0)} bereiten Schritten."
    return 'Aktiver Bereich vorhanden.' if state == 'active' else f'Vorhandener Bereich ist derzeit {state}.'


def priority_score(topic: dict, workspace: dict | None, mode: str, urgency_value: str) -> float:
    relevance = float(topic.get('action_relevance', 0))
    recurrence = float(topic.get('recurrence_score', 0))
    freshness = float(topic.get('freshness_score', 0))
    score = relevance * 0.45 + recurrence * 0.3 + freshness * 0.15
    state = (workspace or {}).get('state')
    if urgency_value == 'high':
        score += 0.1
    score += 0.12 if mode == 'execute' else (0.04 if mode == 'offer' else -0.05)
    if state == 'active':
        score += 0.18
        if mode == 'prepare':
            score += 0.02
    return round(min(1.0, max(0.0, score)), 3)


def message_for(topic: dict, workspace: dict | None, mode: str, needs_text: str) -> str:
    label = topic['label']
    entities = ', '.join((topic.get('entities') or [])[:2]) or 'keine markanten Signale'
    signal = workspace_signal(workspace)
    if mode == 'execute':
        return f"{label} ist akut genug für direkte Unterstützung. Schwerpunkt: {needs_text}. Signale: {entities}. {signal}"
    if mode == 'offer':
        return f"{label} taucht wiederholt und handlungsnah auf. Sichtbare Hilfe zu {needs_text} ist sinnvoll. Signale: {entities}. {signal}"
    return f"{label} zeichnet sich ab, aber ohne akuten Ausführungsdruck. Hintergrundvorbereitung für {needs_text}. Signale: {entities}. {signal}"
