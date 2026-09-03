from __future__ import annotations

from typing import Any

from eidolon.workspaces.module_runtime_support import clamp_index


def apply_status_tracker_action(current: dict[str, Any], action: str, payload: dict[str, Any]) -> dict[str, Any]:
    current.setdefault('entries', [])
    if action == 'add_entry':
        current['entries'].append({'label': payload.get('label', 'Eintrag'), 'status': payload.get('status', 'open')})
    elif action == 'set_status' and current['entries']:
        current['entries'][clamp_index(payload, current['entries'])]['status'] = payload.get('status', 'open')
    return current


def apply_decision_matrix_action(current: dict[str, Any], action: str, payload: dict[str, Any]) -> dict[str, Any]:
    current.setdefault('options', [])
    if action == 'add_option':
        current['options'].append({'label': payload.get('label', 'Option'), 'score': float(payload.get('score', 0.0))})
    elif action == 'rank' and current['options']:
        current['options'] = sorted(current['options'], key=lambda item: item.get('score', 0.0), reverse=True)
    return current


def apply_next_actions_action(current: dict[str, Any], state: dict[str, Any], action: str, payload: dict[str, Any]) -> dict[str, Any]:
    current.setdefault('items', list(state.get('next_actions', [])))
    if action == 'add_item':
        current['items'].append(payload.get('label', 'Neuer Schritt'))
    elif action == 'complete_item' and current['items']:
        index = clamp_index(payload, current['items'])
        current['items'][index] = '✓ ' + current['items'][index].lstrip('✓ ')
    return current


def apply_details_action(current: dict[str, Any], action: str, payload: dict[str, Any]) -> dict[str, Any]:
    if action == 'select_item':
        current['selected_id'] = payload.get('selected_id')
    elif action == 'set_focus_note':
        current['focus_note'] = payload.get('focus_note', 'Fokus aktualisiert')
    elif action == 'set_summary':
        current['summary'] = payload.get('summary', current.get('summary', ''))
    return current


def apply_dependencies_action(current: dict[str, Any], action: str, payload: dict[str, Any]) -> dict[str, Any]:
    current.setdefault('items', [])
    dependency = {'from': payload.get('from'), 'to': payload.get('to'), 'type': payload.get('type', 'depends_on')}
    if action == 'add_dependency':
        if dependency['from'] and dependency['to'] and dependency not in current['items']:
            current['items'].append(dependency)
    elif action == 'remove_dependency':
        current['items'] = [
            item for item in current['items']
            if not (item.get('from') == dependency['from'] and item.get('to') == dependency['to'] and item.get('type', 'depends_on') == dependency['type'])
        ]
    return current


def apply_journal_action(current: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    current.setdefault('entries', [])
    if payload.get('_action') == 'add_entry':
        current['entries'].append(payload.get('text', 'Neue Reflexion'))
    return current


def apply_fallback_action(current: dict[str, Any], action: str, payload: dict[str, Any]) -> dict[str, Any]:
    current.setdefault('events', [])
    current['events'].append({'action': action, 'payload': payload})
    return current
