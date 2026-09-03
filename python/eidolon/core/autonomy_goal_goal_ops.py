from __future__ import annotations

import uuid

from eidolon.core.autonomy_models import CATEGORIES, Goal, Step
from eidolon.core.autonomy_store import now_iso


def create_goal(engine, title: str, description: str = '', category: str = 'system', priority: int = 1, steps: list[str] | None = None, persist: bool = True, source: str = 'manual', evidence: str = '', problem_key: str = '') -> Goal:
    gid = str(uuid.uuid4())[:8]
    now = now_iso()
    goal = Goal(id=gid, title=title.strip() or 'Unbenannt', description=description.strip(), category=category if category in CATEGORIES else 'system', status='planned', priority=max(1, min(5, int(priority))), steps=[Step(id=str(uuid.uuid4())[:6], title=step) for step in (steps or [])], created_at=now, updated_at=now, source=source, evidence=evidence, problem_key=problem_key)
    engine.store.goals[gid] = goal
    engine.store.add_log(gid, 'created', f'{title} [{source}]')
    if persist:
        engine.store.save()
    return goal


def update_goal(engine, goal_id: str, **fields) -> dict:
    goal = engine.store.goals.get(goal_id)
    if not goal:
        return {'ok': False, 'error': 'Ziel nicht gefunden'}
    for key in ('title', 'description', 'category', 'priority', 'progress'):
        if key in fields and fields[key] is not None:
            if key == 'priority':
                goal.priority = max(1, min(5, int(fields[key])))
            elif key == 'progress':
                goal.progress = max(0.0, min(1.0, float(fields[key])))
            elif key == 'category':
                if fields[key] in CATEGORIES:
                    goal.category = fields[key]
            else:
                setattr(goal, key, str(fields[key]))
    goal.updated_at = now_iso()
    engine.store.add_log(goal_id, 'updated', ', '.join(key for key in fields if fields[key] is not None))
    engine.store.save()
    return {'ok': True, 'goal': goal.to_dict()}


def delete_goal(engine, goal_id: str) -> dict:
    if goal_id not in engine.store.goals:
        return {'ok': False, 'error': 'Ziel nicht gefunden'}
    title = engine.store.goals[goal_id].title
    del engine.store.goals[goal_id]
    engine.store.add_log(goal_id, 'deleted', title)
    engine.store.save()
    return {'ok': True, 'deleted': goal_id}
