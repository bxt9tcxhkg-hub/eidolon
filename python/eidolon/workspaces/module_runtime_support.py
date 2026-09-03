from __future__ import annotations

from typing import Any


def clamp_index(payload: dict[str, Any], items: list[Any]) -> int:
    return max(0, min(int(payload.get('index', 0)), len(items) - 1))


def workspace_view(updated: dict[str, Any]) -> dict[str, Any]:
    return {'workspace_id': updated.get('workspace_id'), 'topic_label': updated.get('topic_label'), 'workspace_type': updated.get('workspace_type'), 'layout_template': updated.get('layout_template'), 'modules': updated.get('modules', []), 'metadata': {'needs': updated.get('needs', {})}, 'state_data': updated}


def sync_board_derivatives(module_data: dict[str, Any], focus_card_id: str | None = None) -> dict[str, Any]:
    board_state = module_data.get('board') or {}
    if not board_state.get('items'):
        return module_data
    blocked_items = [item for item in board_state.get('items', []) if item.get('status') == 'blocked']
    if 'board' in module_data:
        board_state['summary'] = {'total': len(board_state.get('items', [])), 'blocked': len(blocked_items), 'ready': sum(1 for item in board_state.get('items', []) if item.get('status') == 'ready'), 'in_progress': sum(1 for item in board_state.get('items', []) if item.get('status') == 'in_progress'), 'done': sum(1 for item in board_state.get('items', []) if item.get('status') == 'done'), 'dependencies': sum(len(item.get('dependency_ids', [])) for item in board_state.get('items', []))}
        board_state['blocked_items'] = [{'id': item.get('id'), 'label': item.get('label'), 'blocker_reason': item.get('blocker_reason') or 'Blockiert'} for item in blocked_items]
        module_data['board'] = board_state
    if 'graph' in module_data:
        graph_state = dict(module_data.get('graph') or {})
        items = board_state.get('items', [])
        graph_state['nodes'] = [{'id': item.get('id'), 'label': item.get('label'), 'status': item.get('status')} for item in items]
        generated_edges = []
        for item in items:
            for dep in item.get('dependency_ids', []):
                generated_edges.append({'from': dep, 'to': item.get('id'), 'type': 'depends_on'})
        module_data['graph'] = {**graph_state, 'edges': generated_edges}
    if 'details' in module_data:
        details_state = dict(module_data.get('details') or {})
        item_ids = [item.get('id') for item in board_state['items']]
        if focus_card_id in item_ids:
            details_state['selected_id'] = focus_card_id
        elif details_state.get('selected_id') not in item_ids:
            details_state['selected_id'] = board_state['items'][0].get('id')
        selected = next((item for item in board_state['items'] if item.get('id') == details_state.get('selected_id')), board_state['items'][0])
        details_state['selected_item'] = {'id': selected.get('id'), 'label': selected.get('label'), 'status': selected.get('status'), 'owner': selected.get('owner'), 'priority': selected.get('priority'), 'notes': selected.get('notes'), 'blocker_reason': selected.get('blocker_reason')}
        module_data['details'] = details_state
    if 'dependencies' in module_data and 'graph' in module_data:
        dep_state = dict(module_data.get('dependencies') or {})
        dep_state['items'] = list((module_data.get('graph') or {}).get('edges', []))
        module_data['dependencies'] = dep_state
    return module_data
