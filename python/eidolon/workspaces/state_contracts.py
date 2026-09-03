from __future__ import annotations


def normalize_workspace_contract(workspace: dict) -> dict:
    normalized = dict(workspace)
    modules = list(normalized.get('modules', []))
    project_core = {'board', 'graph', 'dependencies', 'details'}
    if normalized.get('workspace_type') == 'project_workspace' and project_core.intersection(modules):
        for required in ['board', 'graph', 'dependencies', 'next_actions', 'details']:
            if required not in modules:
                modules.append(required)
    normalized['modules'] = modules
    return normalized
