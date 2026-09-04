from __future__ import annotations

from datetime import datetime, timezone

from eidolon.workspaces.contracts import build_workspace_semantic_frame, map_workspace_state_to_product_state
from eidolon.workspaces.workspace_support_summary import next_actions_from_project, project_summary, workspace_state_from_project


def project_items(project) -> list[dict]:
    items = []
    for element in project.elements or []:
        items.append({
            'id': element.id,
            'label': element.title,
            'status': element.status,
            'kind': element.element_type,
            'owner': element.assigned_to or 'unassigned',
            'priority': element.priority,
            'notes': element.description,
            'blocker_reason': element.description if element.status == 'blocked' else '',
            'dependency_ids': list(element.dependencies or []),
            'position': dict(element.position or {'x': 0, 'y': 0}),
            'due_at': element.due_at,
            'parent_id': element.parent_id,
        })
    return items


def project_to_workspace(project, orchestrator) -> dict:
    state = workspace_state_from_project(project)
    now = datetime.now(timezone.utc).isoformat()
    modules = ['board', 'graph', 'dependencies', 'next_actions', 'details']
    items = project_items(project)
    summary = project_summary(project)
    details_selected = items[0] if items else None
    state_data = {
        'workspace_id': f'project_{project.id}',
        'topic_label': project.title,
        'workspace_type': 'project_workspace',
        'layout_template': 'hybrid',
        'modules': modules,
        'needs': {'planning': 0.9, 'execution': 0.95, 'tracking': 0.6},
        'overview': project.description or f'Projektfläche für {project.title}',
        'next_actions': next_actions_from_project(project),
        'evidence': [{'source': 'project_model', 'project_id': project.id, 'updated_at': project.updated_at}],
        'notes': [],
        'status': 'active' if state == 'active' else ('archived' if state == 'archived' else 'prepared'),
        'state_origin': 'project_model',
        'updated_at': now,
        'module_data': {
            'board': {'items': items, 'summary': summary, 'blocked_items': summary['blocked_items']},
            'graph': {'nodes': [{'id': item['id'], 'label': item['label'], 'status': item['status']} for item in items], 'edges': [{'from': dep, 'to': item['id'], 'type': 'depends_on'} for item in items for dep in item.get('dependency_ids', [])]},
            'dependencies': {'items': [{'from': dep, 'to': item['id'], 'type': 'depends_on'} for item in items for dep in item.get('dependency_ids', [])]},
            'next_actions': {'items': next_actions_from_project(project)},
            'details': {'selected_id': details_selected.get('id') if details_selected else None, 'selected_item': details_selected, 'summary': project.description or f'Direkter Projektkontext für {project.title}', 'focus_note': 'Direkt aus realen Projektelementen abgeleitet.'},
        },
    }
    workspace = {
        'workspace_id': f'project_{project.id}', 'topic_label': project.title, 'workspace_type': 'project_workspace', 'layout_template': 'hybrid', 'modules': modules, 'render_slot': 'adaptive-workspace-host', 'feature_flag': 'workspace_adaptive_modules', 'safe_mode': 'sandboxed', 'mutable_core_areas': [],
        'metadata': {
            'project_id': project.id,
            'project_status': project.status,
            'project_domain': project.domain,
            'project_description': project.description,
            'source': 'project_model',
            'needs': state_data['needs'],
            'formation_confirmed': (project.metadata or {}).get('formation_confirmed', True),
            'formation_source': (project.metadata or {}).get('formation_source', 'user_created_project'),
            'product_state': (project.metadata or {}).get('product_state') or 'active_project',
            'stored_product_state': (project.metadata or {}).get('product_state') or 'active_project',
        },
        'state': state,
        'product_state': map_workspace_state_to_product_state(state, {
            'action_relevance': 1.0,
            'recurrence_score': 1.0,
            'formation_confirmed': (project.metadata or {}).get('formation_confirmed', True),
            'formation_source': (project.metadata or {}).get('formation_source', 'user_created_project'),
            'stored_product_state': (project.metadata or {}).get('product_state') or 'active_project',
        }),
        'health': 'ok', 'last_updated': now, 'state_data': state_data,
    }
    orchestration = orchestrator.evaluate(workspace)
    semantic_frame = build_workspace_semantic_frame(workspace, {**state_data, 'orchestration': orchestration})
    state_data['orchestration'] = orchestration
    state_data['semantic_frame'] = semantic_frame
    state_data['product_state'] = semantic_frame['active_context']
    workspace['state_data'] = state_data
    workspace['semantic_frame'] = semantic_frame
    workspace['product_state'] = semantic_frame['active_context']
    return workspace
