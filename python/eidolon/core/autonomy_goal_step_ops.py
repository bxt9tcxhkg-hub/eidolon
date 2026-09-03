from __future__ import annotations

import uuid

from eidolon.core.autonomy_models import Step
from eidolon.core.autonomy_store import now_iso


def add_step(engine, goal_id: str, title: str) -> dict:
    goal = engine.store.goals.get(goal_id)
    if not goal:
        return {'ok': False, 'error': 'Ziel nicht gefunden'}
    step = Step(id=str(uuid.uuid4())[:6], title=title.strip())
    goal.steps.append(step)
    goal.updated_at = now_iso()
    engine.store.add_log(goal_id, 'step_added', title)
    engine.store.save()
    return {'ok': True, 'step': step.to_dict(), 'goal': goal.to_dict()}


def toggle_step(engine, goal_id: str, step_id: str) -> dict:
    goal = engine.store.goals.get(goal_id)
    if not goal:
        return {'ok': False, 'error': 'Ziel nicht gefunden'}
    for step in goal.steps:
        if isinstance(step, Step) and step.id == step_id:
            step.done = not step.done
            step.completed_at = now_iso() if step.done else None
            goal.updated_at = now_iso()
            engine.store.add_log(goal_id, 'step_toggled', f'{step.title} → {step.done}')
            auto_done = False
            if goal.status == 'active' and all(item.done for item in goal.steps if isinstance(item, Step)):
                goal.status = 'done'
                goal.completed_at = now_iso()
                engine.store.add_log(goal_id, 'auto_completed', 'alle Schritte erledigt')
                auto_done = True
            engine.store.save()
            return {'ok': True, 'goal': goal.to_dict(), 'auto_completed': auto_done}
    return {'ok': False, 'error': 'Schritt nicht gefunden'}


def delete_step(engine, goal_id: str, step_id: str) -> dict:
    goal = engine.store.goals.get(goal_id)
    if not goal:
        return {'ok': False, 'error': 'Ziel nicht gefunden'}
    before = len(goal.steps)
    goal.steps = [step for step in goal.steps if not (isinstance(step, Step) and step.id == step_id)]
    if len(goal.steps) == before:
        return {'ok': False, 'error': 'Schritt nicht gefunden'}
    goal.updated_at = now_iso()
    engine.store.save()
    return {'ok': True, 'goal': goal.to_dict()}
