from __future__ import annotations

from typing import Any


def llm_visible_problems(status: dict[str, Any] | None) -> list[str]:
    problems: list[str] = []
    status = status or {}
    connection = status.get('connection') or {}
    if connection.get('status') in {'missing', 'error'} and connection.get('detail'):
        problems.append(str(connection['detail']))
    provider = status.get('provider')
    if provider == 'openai_oauth':
        openai = status.get('openai') or {}
        if not openai.get('configured') and openai.get('detail'):
            detail = str(openai['detail'])
            if detail not in problems:
                problems.append(detail)
    chain = status.get('fallback_chain') or []
    if not chain:
        problems.append('Ersatzkette ist leer. Chat nutzt nur den gewählten Anbieter, bis eine gültige Kette gesetzt ist.')
    return problems


def healing_visible_problems(healing_state: dict[str, Any] | None) -> list[str]:
    problems: list[str] = []
    state = healing_state or {}
    blocked = state.get('blocked') or {}
    if isinstance(blocked, dict):
        for name, info in blocked.items():
            if info:
                problems.append(f'Healing-Check blockiert: {name}')
    return problems


def health_visible_problems(*, certs: dict[str, Any] | None = None, backup_stats: dict[str, Any] | None = None) -> list[str]:
    problems: list[str] = []
    if certs is not None and not certs.get('complete'):
        problems.append('Zertifikate unvollständig')
    if certs is not None and certs.get('chain_valid') is False:
        problems.append('Zertifikatskette ungültig')
    if backup_stats is not None and backup_stats.get('count', 0) < 1:
        problems.append('kein Backup vorhanden')
    return problems


def collect_visible_problems(*, llm_status: dict[str, Any] | None = None, healing_state: dict[str, Any] | None = None, health_problems: list[str] | None = None) -> list[str]:
    problems: list[str] = []
    for item in llm_visible_problems(llm_status) + healing_visible_problems(healing_state) + list(health_problems or []):
        if item and item not in problems:
            problems.append(item)
    return problems


def describe_runtime_problems(problems: list[str], *, llm_status: dict[str, Any] | None = None) -> str:
    status = llm_status or {}
    provider = status.get('provider') or 'unbekannt'
    model = status.get('model') or 'unbekannt'
    if not problems:
        return (
            f'Aktuell sind keine erkannten Verbindungs- oder Healing-Probleme gemeldet. '
            f'Chat läuft über {provider} / {model}.'
        )
    return (
        f'Erkannte Probleme ({len(problems)}): ' + '; '.join(problems[:6]) +
        f' Aktiver Anbieter: {provider} / {model}. Es werden keine Schlüsselwerte gezeigt.'
    )
