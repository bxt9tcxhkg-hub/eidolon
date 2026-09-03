from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def refresh_project_derived_state(current: dict[str, Any]) -> dict[str, Any]:
    module_data = current.setdefault('module_data', {})
    board = module_data.get('board') or {}
    items = board.get('items') or []
    if not items:
        board['summary'] = {'total': 0, 'blocked': 0, 'ready': 0, 'in_progress': 0, 'done': 0, 'dependencies': 0}
        board['blocked_items'] = []
        module_data['board'] = board
        if 'graph' in module_data:
            module_data['graph'] = {'nodes': [], 'edges': []}
        if 'dependencies' in module_data:
            module_data['dependencies'] = {'items': []}
        if 'details' in module_data:
            details = dict(module_data.get('details') or {})
            details['selected_id'] = None
            details['selected_item'] = None
            module_data['details'] = details
        current['module_data'] = module_data
        return current
    blocked_items = [item for item in items if item.get('status') == 'blocked']
    board['summary'] = {'total': len(items), 'blocked': len(blocked_items), 'ready': sum(1 for item in items if item.get('status') == 'ready'), 'in_progress': sum(1 for item in items if item.get('status') == 'in_progress'), 'done': sum(1 for item in items if item.get('status') == 'done'), 'dependencies': sum(len(item.get('dependency_ids', [])) for item in items)}
    board['blocked_items'] = [{'id': item.get('id'), 'label': item.get('label'), 'blocker_reason': item.get('blocker_reason') or 'Blockiert'} for item in blocked_items]
    module_data['board'] = board
    if 'graph' in module_data:
        graph = dict(module_data.get('graph') or {})
        graph['nodes'] = [{'id': item.get('id'), 'label': item.get('label'), 'status': item.get('status')} for item in items]
        graph['edges'] = [{'from': dep, 'to': item.get('id'), 'type': 'depends_on'} for item in items for dep in item.get('dependency_ids', [])]
        module_data['graph'] = graph
    if 'dependencies' in module_data:
        module_data['dependencies'] = {'items': list((module_data.get('graph') or {}).get('edges', []))}
    if 'details' in module_data:
        details = dict(module_data.get('details') or {})
        item_ids = [item.get('id') for item in items]
        if details.get('selected_id') not in item_ids:
            details['selected_id'] = items[0].get('id')
        selected = next((item for item in items if item.get('id') == details.get('selected_id')), items[0])
        details['selected_item'] = {'id': selected.get('id'), 'label': selected.get('label'), 'status': selected.get('status'), 'owner': selected.get('owner'), 'priority': selected.get('priority'), 'notes': selected.get('notes'), 'blocker_reason': selected.get('blocker_reason')}
        module_data['details'] = details
    current['module_data'] = module_data
    return current


def build_default_module_data(modules: list[str], next_actions: list[str], workspace: dict[str, Any] | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {}
    workspace = workspace or {}
    topic = workspace.get('topic_label', 'Projekt')
    for module in modules:
        if module == 'status_tracker':
            data[module] = {'entries': [], 'empty_state': 'Noch keine belastbaren Statusdaten vorhanden.'}
        elif module == 'decision_matrix':
            data[module] = {'options': [], 'empty_state': 'Noch keine belastbaren Entscheidungsoptionen vorhanden.'}
        elif module == 'next_actions':
            data[module] = {'items': list(next_actions)}
        elif module == 'board':
            data[module] = {'items': []}
        elif module == 'graph':
            data[module] = {'nodes': [], 'edges': []}
        elif module == 'details':
            data[module] = {'selected_id': None, 'summary': f'Noch kein belastbarer Arbeitsinhalt für {topic}', 'focus_note': 'Arbeitsinhalte erst nach realer Erfassung ableiten.'}
        elif module == 'dependencies':
            data[module] = {'items': []}
        elif module in {'journal', 'reflection'}:
            data[module] = {'entries': []}
        else:
            data[module] = {'events': []}
    return data


def build_default_state(workspace: dict[str, Any]) -> dict[str, Any]:
    topic = workspace.get('topic_label', 'Workspace')
    modules = workspace.get('modules', [])
    state = {
        'workspace_id': workspace['workspace_id'],
        'topic_label': topic,
        'workspace_type': workspace.get('workspace_type'),
        'layout_template': workspace.get('layout_template'),
        'modules': modules,
        'needs': (workspace.get('metadata') or {}).get('needs', {}),
        'overview': f'Noch kein belastbarer Arbeitsinhalt für {topic}.',
        'next_actions': [],
        'evidence': [],
        'notes': [],
        'status': 'prepared',
        'module_data': build_default_module_data(modules, [], workspace),
        'orchestration': {'recommended_mode': 'next_actions', 'ranked_modes': [], 'next_best_action': None, 'autonomy_posture': 'planning_support'},
        'state_origin': 'empty_until_real_input',
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    return refresh_project_derived_state(state)
