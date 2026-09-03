from __future__ import annotations

from datetime import datetime, timezone


def load_snapshot(path, default):
    if not path.exists():
        return default
    try:
        import json
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def save_snapshot(path, data):
    import json
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def build_context_model(workspaces: list[dict]) -> dict:
    active = next((w for w in workspaces if w.get('product_state') == 'active_project'), None)
    candidates = [w for w in workspaces if w.get('product_state') == 'project_candidate']
    topics = [w for w in workspaces if w.get('product_state') == 'chat_topic']
    current = active or (candidates[0] if candidates else None)
    current_state = 'active_project' if active else 'project_candidate' if candidates else 'chat_topic' if topics else 'no_live_context'
    current_phase = 'execute' if active else 'form_project' if candidates else 'understand' if topics else 'await_input'
    next_transition = 'continue_execution' if active else 'promote_candidate_to_project' if candidates else 'structure_topic_into_candidate' if topics else None
    next_step = 'Aktiven Projektschritt sichtbar fortführen und verifizieren.' if active else 'Projektkandidaten in einen belastbaren Verantwortungsbereich überführen.' if candidates else 'Aus Gesprächssignalen einen klaren Projektkandidaten mit Fokus und Zuständigkeit formen.' if topics else 'Kein aktiver Gesprächs- oder Projektkontext vorhanden. Auf neue Live-Signale warten.'
    approval_state = 'project_role_requires_explicit_approval' if candidates and not active else ('within_current_guardrails' if (active or candidates or topics) else 'awaiting_live_input')
    return {'chat_topic_count': len(topics), 'project_candidate_count': len(candidates), 'active_project_count': 1 if active else 0, 'active_surface_project': active.get('workspace_id') if active else None, 'current_conversation_project': current.get('workspace_id') if current else None, 'active_project_label': active.get('topic_label') if active else None, 'current_focus_label': current.get('topic_label') if current else None, 'candidate_labels': [w.get('topic_label') for w in candidates if w.get('topic_label')], 'topic_labels': [w.get('topic_label') for w in topics if w.get('topic_label')], 'referenced_projects': [], 'context_shift_state': 'same_project' if active else 'possible_project_shift' if candidates else 'chat_topic_focus' if topics else 'awaiting_input', 'workflow_loop': ['verstehen', 'strukturieren', 'einordnen', 'organisieren', 'ausführen', 'verifizieren', 'fortsetzen'], 'current_context_state': current_state, 'current_phase': current_phase, 'next_transition': next_transition, 'next_step': next_step, 'approval_state': approval_state, 'responsible_role': 'eidolon-core'}
