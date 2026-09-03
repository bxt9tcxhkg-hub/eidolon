from __future__ import annotations

from eidolon.core.autonomy_models import GOAL_TRANSITIONS, Step
from eidolon.core.autonomy_store import now_iso


def transition(engine, goal_id: str, new_status: str, error: str | None = None, allow_multi_active: bool = False) -> dict:
    goal = engine.store.goals.get(goal_id)
    if not goal:
        return {'ok': False, 'error': 'Ziel nicht gefunden'}
    allowed = GOAL_TRANSITIONS.get(goal.status, [])
    if new_status not in allowed:
        return {'ok': False, 'error': f'Übergang {goal.status} → {new_status} nicht erlaubt', 'allowed': allowed}
    auto_paused: list[str] = []
    if new_status == 'active' and not allow_multi_active:
        for other in engine.store.goals.values():
            if other.id != goal_id and other.status == 'active':
                other.status = 'paused'
                other.updated_at = now_iso()
                auto_paused.append(other.title)
                engine.store.add_log(other.id, 'auto_paused', f"pausiert, weil '{goal.title}' aktiviert wurde")
    old = goal.status
    goal.status = new_status
    goal.updated_at = now_iso()
    if new_status == 'active' and not goal.started_at:
        goal.started_at = now_iso()
    if new_status == 'done':
        goal.completed_at = now_iso()
        goal.progress = 1.0
        for step in goal.steps:
            if isinstance(step, Step):
                step.done = True
                step.completed_at = step.completed_at or now_iso()
    if new_status == 'failed':
        goal.last_error = error or 'Unbekannter Fehler'
    if new_status != 'failed':
        goal.last_error = None
    engine.store.add_log(goal_id, 'transition', f'{old} → {new_status}')
    engine.store.save()
    return {'ok': True, 'goal': goal.to_dict(), 'from': old, 'to': new_status, 'auto_paused': auto_paused}
