from __future__ import annotations

from typing import Any


GENERIC_SLOT_ORDER = ('context', 'goal', 'status', 'owner', 'next', 'approval', 'blocker', 'inbox', 'evidence')
SLOT_TITLES = {
    'context': 'Kontext',
    'goal': 'Ziel',
    'status': 'Zustand',
    'owner': 'Zuständigkeit',
    'next': 'Nächster Schritt',
    'approval': 'Freigabe',
    'blocker': 'Blocker',
    'inbox': 'Unsortiert',
    'evidence': 'Evidenz',
}


def _row(label: str, value: Any) -> dict[str, str] | None:
    text = str(value or '').strip()
    if not text:
        return None
    return {'label': label, 'value': text}


def _pending(items: list[Any], *status_keys: str) -> list[Any]:
    result = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        status = str(item.get('status') or '')
        if not status or status in status_keys or item.get('is_pending') or item.get('is_open'):
            result.append(item)
    return result


def _slot(kind: str, rows: list[dict[str, str]], *, source: str, empty: str) -> dict[str, Any]:
    filled = [row for row in rows if row]
    return {
        'kind': kind,
        'title': SLOT_TITLES[kind],
        'source': source,
        'rows': filled,
        'empty': empty if not filled else '',
        'populated': bool(filled),
    }


def build_generic_slots(*, project: dict[str, Any] | None = None, work_kernel: dict[str, Any] | None = None, operate: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    project = project or {}
    kernel = work_kernel or {}
    operate = operate or {}
    workflow = kernel.get('workflow_state') or {}
    project_ctx = kernel.get('project_context') or {}
    operate_ctx = kernel.get('operate_context') or {}
    semantic = ((kernel.get('workspace_context') or {}).get('active_workspace') or {})
    elements = list(project.get('elements') or [])
    inbox = [item for item in list(project.get('inbox') or []) if not item.get('processed')]
    approvals = _pending(operate_ctx.get('pending_approvals') or operate.get('approvals') or [], 'pending')
    blockers = _pending(operate_ctx.get('open_blockers') or operate.get('blockers') or [], 'open')
    blocked_elements = [item for item in elements if item.get('status') == 'blocked']
    next_action = operate_ctx.get('next_action') or operate.get('next_action') or {}
    in_progress = next((item for item in elements if item.get('status') == 'in_progress'), None)
    planned = next((item for item in elements if item.get('status') in {'planned', 'ready'}), None)
    evidence = list(operate.get('evidence') or [])[:3]
    owner = semantic.get('topic_label') and (semantic.get('summary') or {})
    slots = [
        _slot('context', [
            _row('Titel', project.get('title') or project_ctx.get('active_project_title') or project_ctx.get('candidate_project_title')),
            _row('Kontext', workflow.get('current_context_state')),
            _row('Phase', workflow.get('current_phase')),
            _row('Beschreibung', project.get('description')),
        ], source='work_kernel', empty='Kein geladener Projektkontext.'),
        _slot('goal', [
            _row('Ziel', project_ctx.get('active_goal') or (operate.get('objective') or {}).get('title') or operate_ctx.get('objective_title')),
            _row('Problem', project_ctx.get('active_problem')),
        ], source='work_kernel', empty='Kein belastbares Ziel im Kernel.'),
        _slot('status', [
            _row('Projekt', project.get('status')),
            _row('Operate', operate_ctx.get('run_state') or (operate.get('run') or {}).get('state')),
            _row('Elemente', len(elements) if project else None),
        ], source='work_kernel', empty='Kein gemeinsamer Zustand.'),
        _slot('owner', [
            _row('Rolle', 'eidolon-core'),
            _row('Fokus', semantic.get('topic_label') or project.get('title')),
            _row('Board', owner.get('in_progress') if isinstance(owner, dict) else None),
        ], source='work_kernel', empty='Keine Zuständigkeit modelliert.'),
        _slot('next', [
            _row('Operate', next_action.get('summary') or next_action.get('title') or workflow.get('next_step')),
            _row('Element', (in_progress or planned or {}).get('title') if (in_progress or planned) else None),
        ], source='work_kernel', empty='Kein nächster Schritt aus dem Kernel.'),
        _slot('approval', [
            _row(item.get('title') or 'Freigabe', item.get('summary') or item.get('status') or 'ausstehend')
            for item in approvals[:3]
        ], source='operate', empty='Keine offenen Freigaben.'),
        _slot('blocker', [
            *[_row(item.get('title') or 'Blocker', item.get('summary') or item.get('resolution_hint') or 'offen') for item in blockers[:3]],
            *[_row(item.get('title') or 'Element', item.get('description') or 'blockiert') for item in blocked_elements[:3]],
        ], source='work_kernel', empty='Keine offenen Blocker.'),
        _slot('inbox', [
            _row('Eingang', item.get('text') or item.get('id')) for item in inbox[:4]
        ], source='project', empty='Keine offenen Eingänge.'),
        _slot('evidence', [
            _row(item.get('title') or item.get('kind') or 'Evidenz', item.get('summary') or item.get('digest') or item.get('kind'))
            for item in evidence
        ], source='operate', empty='Keine Evidenz im aktuellen Lauf.'),
    ]
    always = {'context', 'goal', 'status', 'next'}
    return [slot for slot in slots if slot['kind'] in always or slot['populated']]
