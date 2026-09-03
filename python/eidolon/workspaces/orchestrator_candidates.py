from __future__ import annotations

from eidolon.workspaces.orchestrator_support import compose


def _find_duplicate_board_action(board_data: dict, suggested_label: str) -> tuple[int, dict] | None:
    """Find a duplicate action on the board."""
    board_items = board_data.get('items') or []
    normalized_label = suggested_label.strip().casefold()
    for idx, item in enumerate(board_items):
        existing_label = str(item.get('label') or item.get('title') or '').strip().casefold()
        existing_status = str(item.get('status') or '')
        if existing_status not in {'done', 'archived'} and existing_label == normalized_label:
            return idx, item
    return None


def candidate_next_actions(orchestrator, workspace_type: str, data: dict, board_data: dict, needs: dict):
    items = data.get('items') or []
    open_items = [item for item in items if not str(item).startswith('✓')]
    score = 0.45 + min(0.4, float(needs.get('planning', 0)) * 0.35) + (0.15 if len(open_items) < 3 else 0)
    if workspace_type == 'project_workspace':
        suggested_label = str(open_items[0]) if open_items else 'Nächsten konkreten Schritt ergänzen'
        duplicate = _find_duplicate_board_action(board_data, suggested_label)
        if duplicate:
            idx, item = duplicate
            return compose(orchestrator, workspace_type, 'board', 'set_priority', 'Vorhandenen konkreten Schritt schärfen', score - 0.12, 'Ein offener generischer Folgeschritt existiert bereits; statt Duplikat wird der vorhandene Schritt priorisiert.', {'index': idx, 'priority': max(3, int(item.get('priority') or 0))})
        return compose(orchestrator, workspace_type, 'board', 'add_card', 'Nächsten konkreten Schritt ergänzen', score - 0.08, 'Planungslast hoch oder zu wenige konkrete nächste Schritte vorhanden; für Projekt-Workspaces wird daraus direkt ein echtes Arbeitselement erzeugt.', {'label': suggested_label, 'status': 'planned', 'notes': 'Aus nächster Aktion abgeleitet'})
    return compose(orchestrator, workspace_type, 'next_actions', 'add_item', 'Nächsten konkreten Schritt ergänzen', score, 'Planungslast hoch oder zu wenige konkrete nächste Schritte vorhanden.', {'label': 'Nächsten konkreten Schritt ergänzen'})


def _find_ready_candidates(items: list) -> list[tuple[int, dict]]:
    """Find items that are ready to execute (all dependencies met)."""
    done_ids = {item.get('id') for item in items if item.get('status') == 'done'}
    ready = []
    for idx, item in enumerate(items):
        deps = list(item.get('dependency_ids', []))
        if item.get('status') in {'ready', 'planned'} and all(dep in done_ids for dep in deps):
            ready.append((idx, item))
    return ready


def _find_missing_edges(items: list, edges: list) -> tuple[str, str] | None:
    """Find a missing edge in the graph."""
    edge_pairs = {(edge.get('from'), edge.get('to')) for edge in edges if isinstance(edge, dict)}
    for item in items:
        for dep in list(item.get('dependency_ids', [])):
            pair = (dep, item.get('id'))
            if pair not in edge_pairs:
                return pair
    return None


def _find_candidate_edges(items: list, edges: list) -> tuple[str, str] | None:
    """Find candidate edges to add to the graph."""
    edge_pairs = {(edge.get('from'), edge.get('to')) for edge in edges if isinstance(edge, dict)}
    candidate_pairs = []
    for idx in range(len(items) - 1):
        left = items[idx].get('id'); right = items[idx + 1].get('id')
        if left and right and left != right and (left, right) not in edge_pairs:
            candidate_pairs.append((left, right))
    for left in items:
        for right in items:
            left_id = left.get('id'); right_id = right.get('id')
            if left_id and right_id and left_id != right_id and (left_id, right_id) not in edge_pairs and (left_id, right_id) not in candidate_pairs:
                candidate_pairs.append((left_id, right_id))
    return candidate_pairs[0] if candidate_pairs else None


def candidate_board(orchestrator, workspace_type: str, data: dict, graph_data: dict, needs: dict):
    items = data.get('items') or []
    blocked = [item for item in items if item.get('status') == 'blocked']
    in_progress = [item for item in items if item.get('status') == 'in_progress']
    edges = graph_data.get('edges') or []
    ready_candidates = _find_ready_candidates(items)
    if blocked:
        target_index = next((idx for idx, item in enumerate(items) if item.get('status') == 'blocked'), 0)
        blocker = blocked[0].get('blocker_reason') or 'Blockade sichtbar'
        return compose(orchestrator, workspace_type, 'board', 'set_status', 'Blocker auflösen', 0.96, f'Mindestens eine Aufgabe ist blockiert ({blocker}) und braucht sichtbare Entstörung.', {'index': target_index, 'status': 'ready', 'clear_blocker': True})
    if not in_progress and ready_candidates:
        target_index, target = ready_candidates[0]
        return compose(orchestrator, workspace_type, 'board', 'set_status', 'Ausführbare Aufgabe starten', 0.91, f"{target.get('label')} ist ohne offene Abhängigkeit ausführbar.", {'index': target_index, 'status': 'in_progress'})
    if not in_progress and items:
        return compose(orchestrator, workspace_type, 'board', 'set_status', 'Nächste Aufgabe starten', 0.88, 'Es gibt Arbeit, aber noch keine laufende Aufgabe.', {'index': 0, 'status': 'in_progress'})
    missing_edge = _find_missing_edges(items, edges)
    if missing_edge:
        return compose(orchestrator, workspace_type, 'graph', 'add_dependency', 'Abhängigkeit sichtbar machen', 0.69 + min(0.2, float(needs.get('planning', 0)) * 0.25), 'Board kennt eine Abhängigkeit, aber der Graph zeigt sie noch nicht explizit.', {'from': missing_edge[0], 'to': missing_edge[1], 'type': 'depends_on'})
    if len(edges) < max(1, len(items) - 1):
        chosen = _find_candidate_edges(items, edges)
        if chosen:
            return compose(orchestrator, workspace_type, 'graph', 'add_dependency', 'Abhängigkeit sichtbar machen', 0.61 + min(0.2, float(needs.get('planning', 0)) * 0.25), 'Die Projektstruktur braucht noch explizite Abhängigkeiten.', {'from': chosen[0], 'to': chosen[1], 'type': 'depends_on'})
    return compose(orchestrator, workspace_type, 'board', 'add_card', 'Neue Projektaufgabe ergänzen', 0.55 + min(0.2, float(needs.get('execution', 0)) * 0.25), 'Projektboard vorhanden, aber weiterer operativer Schritt ist sinnvoll.', {'label': 'Neue Projektaufgabe', 'status': 'planned'})


def candidate_tracker(orchestrator, workspace_type: str, data: dict, needs: dict):
    entries = data.get('entries') or []
    open_entries = [entry for entry in entries if entry.get('status') != 'done']
    score = 0.25 + min(0.5, float(needs.get('tracking', 0)) * 0.5) + (0.2 if not open_entries else 0)
    return compose(orchestrator, workspace_type, 'status_tracker', 'add_entry', 'Neuen Tracking-Punkt erfassen', score, 'Tracking-Signal hoch oder noch kein belastbarer Statusanker vorhanden.', {'label': 'Neuer Tracking-Punkt', 'status': 'open'})


def candidate_decision(orchestrator, workspace_type: str, data: dict, needs: dict):
    options = data.get('options') or []
    score = 0.2 + min(0.55, float(needs.get('decision', 0)) * 0.6) + (0.2 if len(options) < 2 else 0)
    action = 'add_option' if len(options) < 2 else 'rank'
    return compose(orchestrator, workspace_type, 'decision_matrix', action, 'Entscheidungsoption ergänzen' if action == 'add_option' else 'Optionen priorisieren', score, 'Entscheidungsdruck erkannt oder zu wenige Optionen für belastbares Abwägen vorhanden.', {'label': 'Neue Option', 'score': 0.5} if action == 'add_option' else {})


def candidate_reflection(orchestrator, workspace_type: str, data: dict, needs: dict):
    entries = data.get('entries') or []
    score = 0.15 + min(0.45, float(needs.get('reflection', 0)) * 0.6) + (0.15 if not entries else 0)
    return compose(orchestrator, workspace_type, 'reflection', 'add_entry', 'Reflexion festhalten', score, 'Reflexions-/Belastungssignale erkannt oder noch kein Selbstbild im Workspace vorhanden.', {'text': 'Reflexion festhalten'})


def autonomy_posture(needs: dict, ranked: list[dict]) -> str:
    top = ranked[0]['module_id'] if ranked else 'next_actions'
    if float(needs.get('decision', 0)) >= 0.8:
        return 'decision_support'
    if top == 'status_tracker':
        return 'tracking_support'
    if top == 'reflection':
        return 'reflection_support'
    return 'planning_support'
