from __future__ import annotations

from datetime import datetime, timezone

from eidolon.workspaces.project_entities import Project


def project_overview(project: Project) -> dict:
    status_count = {}
    priority_count = {}
    blocked = []
    in_progress = []
    unprocessed_inbox = []

    for element in project.elements:
        status_count[element.status] = status_count.get(element.status, 0) + 1
        if element.priority > 0:
            priority_count[element.priority] = priority_count.get(element.priority, 0) + 1
        if element.status == 'blocked':
            blocked.append({'id': element.id, 'title': element.title, 'description': element.description})
        elif element.status == 'in_progress':
            in_progress.append({'id': element.id, 'title': element.title})

    for item in project.inbox:
        if not item.get('processed'):
            unprocessed_inbox.append(item)

    return {
        'project': project.to_dict(),
        'status_count': status_count,
        'priority_count': priority_count,
        'blocked': blocked,
        'in_progress': in_progress,
        'unprocessed_inbox': unprocessed_inbox,
        'total_elements': len(project.elements),
    }


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
