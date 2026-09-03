from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException


def ok_payload(data: dict[str, Any], **extra) -> dict[str, Any]:
    return {'ok': True, 'data': data, 'error': None, **extra}


def require_project(project, detail: str = 'Nicht gefunden'):
    if not project:
        raise HTTPException(status_code=404, detail=detail)
    return project


def update_project_record(project_service, project_id: str, request: dict):
    project = require_project(project_service().get_project(project_id))
    for key, value in request.items():
        if hasattr(project, key):
            setattr(project, key, value)
    project.updated_at = datetime.now(timezone.utc).isoformat()
    project_service()._store.save_project(project)
    return project


def process_project_inbox_item(project_service, project_element_cls, project_id: str, item_id: str):
    project = require_project(project_service().get_project(project_id), detail='Projekt nicht gefunden')
    item = next((entry for entry in project.inbox if entry.get('id') == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail='Item nicht gefunden')
    element = project_element_cls(id=str(uuid.uuid4())[:8], title=item.get('text', '')[:60], description=item.get('text', ''), status='idea', element_type='task')
    project.elements.append(element)
    item['processed'] = True
    item['element_id'] = element.id
    project.updated_at = datetime.now(timezone.utc).isoformat()
    project_service()._store.save_project(project)
    return element


def project_suggestions(project) -> list[dict[str, Any]]:
    elements = project.elements
    existing_titles = {element.title.lower() for element in elements}
    inbox_open = len([item for item in project.inbox if not item.get('processed')])
    task_like = [element for element in elements if element.element_type in {'task', 'milestone', 'deliverable'}]
    in_progress = [element for element in elements if element.status == 'in_progress']
    blocked = [element for element in elements if element.status == 'blocked']
    ready_or_planned = [element for element in elements if element.status in {'planned', 'ready', 'idea'}]
    with_dependencies = [element for element in elements if element.dependencies]
    unassigned = [element for element in elements if not (element.assigned_to or '').strip()]
    has_deliverable = any(element.element_type in {'deliverable', 'milestone'} for element in elements)
    has_goal_signal = bool(project.description.strip()) or has_deliverable
    candidates = []
    if not has_goal_signal:
        candidates.append({'title': 'Zielbild schärfen', 'reason': 'Das Projekt hat noch kein klar sichtbares Ergebnis oder Zielobjekt.', 'kind': 'clarify_goal', 'evidence': {'description_present': bool(project.description.strip()), 'deliverable_present': has_deliverable}})
    if task_like and not in_progress and ready_or_planned:
        candidates.append({'title': 'Nächsten Schritt starten', 'reason': 'Es gibt strukturierte Arbeit, aber aktuell keinen laufenden Schritt.', 'kind': 'start_execution', 'evidence': {'task_like': len(task_like), 'in_progress': len(in_progress), 'ready_or_planned': len(ready_or_planned)}})
    if blocked:
        candidates.append({'title': 'Blocker auflösen', 'reason': f'Es gibt {len(blocked)} blockierte Elemente, die den Fluss bremsen.', 'kind': 'resolve_blocker', 'evidence': {'blocked_titles': [element.title for element in blocked[:3]], 'blocked_count': len(blocked)}})
    if len(elements) >= 3 and len(with_dependencies) == 0:
        candidates.append({'title': 'Abhängigkeiten sichtbar machen', 'reason': 'Mehrere Elemente existieren, aber ihre Reihenfolge oder Abhängigkeiten sind noch nicht modelliert.', 'kind': 'show_dependencies', 'evidence': {'element_count': len(elements), 'dependency_edges': len(with_dependencies)}})
    if len(elements) >= 2 and len(unassigned) >= 2:
        candidates.append({'title': 'Verantwortung zuweisen', 'reason': 'Mehrere Elemente sind noch keiner Person oder Rolle zugeordnet.', 'kind': 'assign_ownership', 'evidence': {'unassigned_titles': [element.title for element in unassigned[:3]], 'unassigned_count': len(unassigned)}})
    if elements and not has_deliverable:
        candidates.append({'title': 'Ergebnis definieren', 'reason': 'Es gibt Arbeitselemente, aber noch keinen sichtbaren Ergebnis- oder Abnahmepunkt.', 'kind': 'define_deliverable', 'evidence': {'element_count': len(elements), 'deliverable_present': has_deliverable}})
    if inbox_open:
        candidates.append({'title': 'Inbox in Struktur überführen', 'reason': f'Es liegen noch {inbox_open} unstrukturierte Eingänge vor.', 'kind': 'process_inbox', 'evidence': {'open_inbox_count': inbox_open}})
    return [candidate for candidate in candidates if candidate['title'].lower() not in existing_titles][:5]


def brainstorm_project(project, user_text: str) -> list[dict[str, Any]]:
    elements = project.elements
    def find_first(predicate):
        for element in elements:
            if predicate(element):
                return element.id
        return None
    milestone_id = find_first(lambda element: element.element_type in {'milestone', 'deliverable'})
    blocked_id = find_first(lambda element: element.status == 'blocked')
    unassigned_id = find_first(lambda element: not (element.assigned_to or '').strip())
    suggestions = []
    if not project.description.strip() and not any(element.element_type in {'deliverable', 'milestone'} for element in elements):
        suggestions.append({'title': 'Ziel oder Ergebnisobjekt ergänzen', 'reason': 'Es fehlt ein klarer Zielanker für das Projekt.', 'type': 'fehlt', 'connect_to': milestone_id, 'evidence': {'description_present': False, 'deliverable_present': False}})
    if elements and not any(element.status == 'in_progress' for element in elements):
        suggestions.append({'title': 'Aktiven Arbeitsschritt markieren', 'reason': 'Der aktuelle Fokus ist nicht sichtbar, obwohl bereits Elemente existieren.', 'type': 'verbessern', 'connect_to': elements[0].id, 'evidence': {'in_progress': 0, 'element_count': len(elements)}})
    if len(elements) >= 3 and not any(element.dependencies for element in elements):
        suggestions.append({'title': 'Abhängigkeiten ergänzen', 'reason': 'Mehrere Elemente sind vorhanden, aber ihre Reihenfolge ist noch nicht nachvollziehbar.', 'type': 'fehlt', 'connect_to': elements[0].id, 'evidence': {'element_count': len(elements), 'dependency_edges': 0}})
    if any(element.status == 'blocked' for element in elements):
        suggestions.append({'title': 'Blockergrund konkretisieren', 'reason': 'Blockierte Elemente sollten mit einem sichtbaren Entstörungsschritt verbunden werden.', 'type': 'verbessern', 'connect_to': blocked_id, 'evidence': {'blocked_count': sum(1 for element in elements if element.status == 'blocked')}})
    if sum(1 for element in elements if not (element.assigned_to or '').strip()) >= 2:
        suggestions.append({'title': 'Verantwortung explizit machen', 'reason': 'Mehrere Elemente haben noch keine klare Zuständigkeit.', 'type': 'fehlt', 'connect_to': unassigned_id, 'evidence': {'unassigned_count': sum(1 for element in elements if not (element.assigned_to or '').strip())}})
    if project.inbox and any(not item.get('processed') for item in project.inbox):
        suggestions.append({'title': 'Inbox-Eingänge strukturieren', 'reason': 'Offene Eingänge liegen noch außerhalb der Projektstruktur.', 'type': 'verbessern', 'connect_to': None, 'evidence': {'open_inbox_count': sum(1 for item in project.inbox if not item.get('processed'))}})
    if user_text:
        suggestions.append({'title': f"Kontextpunkt einordnen: '{user_text[:40]}'", 'reason': 'Neuer Input sollte an Ziel, Schritt oder Entscheidung im Projekt angehängt werden.', 'type': 'kontext', 'connect_to': milestone_id or (elements[0].id if elements else None), 'evidence': {'user_text_excerpt': user_text[:80]}})
    return suggestions[:7]
