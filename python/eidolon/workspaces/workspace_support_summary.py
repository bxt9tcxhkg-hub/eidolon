from __future__ import annotations

from eidolon.workspaces.project_model import Project


def workspace_state_from_project(project: Project) -> str:
    status = str(project.status or 'active')
    if status == 'paused':
        return 'suspended'
    if status in {'completed', 'archived', 'done'}:
        return 'archived'
    return 'active'


def project_summary(project: Project) -> dict:
    elements = list(project.elements or [])
    blocked = [e for e in elements if e.status == 'blocked']
    in_progress = [e for e in elements if e.status == 'in_progress']
    ready = [e for e in elements if e.status in {'planned', 'ready', 'idea'}]
    done = [e for e in elements if e.status == 'done']
    inbox_open = [item for item in (project.inbox or []) if not item.get('processed')]
    return {
        'total': len(elements),
        'blocked': len(blocked),
        'in_progress': len(in_progress),
        'ready': len(ready),
        'done': len(done),
        'dependencies': sum(len(e.dependencies or []) for e in elements),
        'blocked_items': [{'id': e.id, 'label': e.title, 'blocker_reason': e.description or 'Blockiert'} for e in blocked[:5]],
        'inbox_open': len(inbox_open),
    }


def next_actions_from_project(project: Project) -> list[str]:
    actions: list[str] = []
    elements = list(project.elements or [])
    blocked = [e for e in elements if e.status == 'blocked']
    if blocked:
        actions.append(f"Blocker bei '{blocked[0].title}' auflösen")
    if not any(e.status == 'in_progress' for e in elements):
        candidate = next((e for e in elements if e.status in {'planned', 'ready', 'idea'}), None)
        if candidate:
            actions.append(f'Nächsten Schritt starten: {candidate.title}')
    if any(not item.get('processed') for item in (project.inbox or [])):
        actions.append(f"Inbox strukturieren ({sum(1 for item in (project.inbox or []) if not item.get('processed'))} offen)")
    if elements and not any(e.element_type in {'deliverable', 'milestone'} for e in elements):
        actions.append('Ergebnis oder Meilenstein sichtbar machen')
    if len(elements) >= 3 and not any(e.dependencies for e in elements):
        actions.append('Abhängigkeiten zwischen Elementen sichtbar machen')
    return actions[:5]
