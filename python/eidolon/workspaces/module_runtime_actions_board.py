from __future__ import annotations

from typing import Any

from eidolon.workspaces.module_runtime_support import clamp_index


def _default_card(items: list[dict[str, Any]], payload: dict[str, Any]) -> dict[str, Any]:
    return {
        'id': payload.get('id') or f"card-{len(items) + 1}",
        'label': payload.get('label', 'Neue Aufgabe'),
        'status': payload.get('status', 'planned'),
        'kind': payload.get('kind', 'task'),
        'owner': payload.get('owner', 'eidolon'),
        'priority': payload.get('priority', 'medium'),
        'notes': payload.get('notes', ''),
        'blocker_reason': payload.get('blocker_reason', ''),
        'dependency_ids': list(payload.get('dependency_ids', [])),
    }


def apply_board_action(current: dict[str, Any], payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    current.setdefault('items', [])
    focus_card_id = None
    if payload.get('_action') == 'add_card':
        current['items'].append(_default_card(current['items'], payload))
    elif payload.get('_action') in {'set_status', 'block_card'} and current['items']:
        index = clamp_index(payload, current['items'])
        item = current['items'][index]
        item['status'] = payload.get('status', 'blocked' if payload.get('_action') == 'block_card' else 'in_progress')
        if item['status'] == 'blocked':
            item['blocker_reason'] = payload.get('blocker_reason', item.get('blocker_reason', '') or 'Blockiert')
        elif payload.get('clear_blocker', True):
            item['blocker_reason'] = ''
        focus_card_id = item.get('id')
    elif payload.get('_action') == 'complete_card' and current['items']:
        index = clamp_index(payload, current['items'])
        current['items'][index]['status'] = 'done'
        focus_card_id = current['items'][index].get('id')
    elif payload.get('_action') == 'rename_card' and current['items']:
        index = clamp_index(payload, current['items'])
        current['items'][index]['label'] = payload.get('label', current['items'][index]['label'])
        focus_card_id = current['items'][index].get('id')
    elif payload.get('_action') == 'assign_owner' and current['items']:
        index = clamp_index(payload, current['items'])
        current['items'][index]['owner'] = payload.get('owner', current['items'][index].get('owner', 'eidolon'))
        focus_card_id = current['items'][index].get('id')
    elif payload.get('_action') == 'set_priority' and current['items']:
        index = clamp_index(payload, current['items'])
        current['items'][index]['priority'] = payload.get('priority', current['items'][index].get('priority', 'medium'))
        focus_card_id = current['items'][index].get('id')
    elif payload.get('_action') == 'set_note' and current['items']:
        index = clamp_index(payload, current['items'])
        current['items'][index]['notes'] = payload.get('notes', current['items'][index].get('notes', ''))
        focus_card_id = current['items'][index].get('id')
    elif payload.get('_action') == 'delete_card' and current['items']:
        deleted = current['items'].pop(clamp_index(payload, current['items']))
        for item in current['items']:
            item['dependency_ids'] = [dependency for dependency in list(item.get('dependency_ids', [])) if dependency != deleted.get('id')]
    return current, focus_card_id
