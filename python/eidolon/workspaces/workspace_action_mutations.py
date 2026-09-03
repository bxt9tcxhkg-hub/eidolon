from __future__ import annotations

from eidolon.workspaces.workspace_action_support import create_element, indexed_element


def apply_project_workspace_action(project_service, project, module_id: str, action: str, payload: dict, result: dict, elements: list):
    changed = False
    if module_id == 'board':
        if action == 'add_card':
            created = create_element(project_service, project.id, payload, 'Neue Aufgabe', '')
            result['element_id'] = created.id if created else None
            changed = created is not None
        elif action in {'set_status', 'complete_card', 'rename_card', 'assign_owner', 'set_priority', 'set_note'}:
            element = indexed_element(elements, payload)
            updates = {}
            if action == 'set_status':
                updates['status'] = str(payload.get('status') or element.status)
                if payload.get('clear_blocker') and updates['status'] != 'blocked':
                    updates['description'] = ''
            elif action == 'complete_card':
                updates['status'] = 'done'
            elif action == 'rename_card':
                updates['title'] = str(payload.get('label') or element.title)
            elif action == 'assign_owner':
                updates['assigned_to'] = str(payload.get('owner') or '')
            elif action == 'set_priority':
                updates['priority'] = int(payload.get('priority', element.priority) or 0)
            elif action == 'set_note':
                updates['description'] = str(payload.get('notes') or '')
            updated = project_service.update_element(project.id, element.id, **updates)
            result['element_id'] = element.id
            changed = updated is not None
        elif action == 'delete_card':
            element = indexed_element(elements, payload)
            changed = project_service.delete_element(project.id, element.id)
            result['element_id'] = element.id
        else:
            raise ValueError(f'Nicht unterstützte Board-Aktion: {action}')
    elif module_id == 'next_actions':
        if action != 'add_item':
            raise ValueError(f'Nicht unterstützte Next-Actions-Aktion: {action}')
        created = create_element(project_service, project.id, payload, 'Nächsten konkreten Schritt ergänzen', 'Aus nächster Aktion abgeleitet')
        result['element_id'] = created.id if created else None
        changed = created is not None
    elif module_id == 'graph':
        if action not in {'add_dependency', 'remove_dependency'}:
            raise ValueError(f'Nicht unterstützte Graph-Aktion: {action}')
        source_id = payload.get('from')
        target = next((e for e in elements if e.id == payload.get('to')), None)
        if not target or not source_id:
            raise ValueError('Abhängigkeit braucht gültige from/to IDs')
        deps = list(target.dependencies or [])
        if action == 'add_dependency' and source_id not in deps:
            deps.append(source_id); changed = True
        if action == 'remove_dependency' and source_id in deps:
            deps.remove(source_id); changed = True
        if changed:
            project_service.update_element(project.id, target.id, dependencies=deps)
        result['element_id'] = target.id
    else:
        raise ValueError(f'Nicht unterstütztes Workspace-Modul: {module_id}')
    return changed, result
