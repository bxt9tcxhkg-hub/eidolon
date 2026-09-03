from __future__ import annotations

from typing import Any


def apply_graph_action(module_data: dict[str, Any], current: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    current.setdefault('nodes', [])
    current.setdefault('edges', [])
    action = payload.get('_action')
    if action == 'add_dependency':
        edge = {'from': payload.get('from'), 'to': payload.get('to'), 'type': payload.get('type', 'depends_on')}
        if edge['from'] and edge['to'] and edge not in current['edges']:
            current['edges'].append(edge)
            board_state = module_data.get('board') or {}
            for item in board_state.get('items', []):
                if item.get('id') == edge['to']:
                    dependencies = list(item.get('dependency_ids', []))
                    if edge['from'] not in dependencies:
                        dependencies.append(edge['from'])
                        item['dependency_ids'] = dependencies
    elif action == 'remove_dependency':
        edge = {'from': payload.get('from'), 'to': payload.get('to'), 'type': payload.get('type', 'depends_on')}
        current['edges'] = [
            item for item in current['edges']
            if not (item.get('from') == edge['from'] and item.get('to') == edge['to'] and item.get('type', 'depends_on') == edge['type'])
        ]
        board_state = module_data.get('board') or {}
        for item in board_state.get('items', []):
            if item.get('id') == edge['to']:
                item['dependency_ids'] = [dependency for dependency in list(item.get('dependency_ids', [])) if dependency != edge['from']]
    elif action == 'add_node':
        current['nodes'].append({'id': payload.get('id'), 'label': payload.get('label', 'Neues Objekt'), 'status': payload.get('status', 'planned')})
    return current
