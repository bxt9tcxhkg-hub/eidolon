from __future__ import annotations

from eidolon.core.autonomy_models import TERMINAL_STATES, Goal, Step
from eidolon.core.autonomy_store import now_iso


def enforce_single_active(engine) -> dict:
    actives = [goal for goal in engine.store.goals.values() if goal.status == 'active']
    if len(actives) <= 1:
        return {'ok': True, 'changed': False, 'active_count': len(actives)}
    actives.sort(key=lambda goal: (-goal.priority, -goal.computed_progress()))
    keep, rest = actives[0], actives[1:]
    for goal in rest:
        goal.status = 'paused'
        goal.updated_at = now_iso()
        engine.store.add_log(goal.id, 'auto_paused', 'Invariante: nur ein Ziel aktiv')
    engine.store.save()
    return {'ok': True, 'changed': True, 'kept': {'id': keep.id, 'title': keep.title}, 'paused': [{'id': goal.id, 'title': goal.title} for goal in rest]}


def next_best_action(engine) -> dict:
    active = engine.list_goals(status='active')
    if active:
        goal = active[0]
        open_steps = [step for step in goal.steps if isinstance(step, Step) and not step.done]
        if open_steps:
            return {'action': 'complete_step', 'goal_id': goal.id, 'goal_title': goal.title, 'step_id': open_steps[0].id, 'step_title': open_steps[0].title, 'reason': f"Aktives Ziel '{goal.title}' hat {len(open_steps)} offene Schritte"}
        return {'action': 'finish_goal', 'goal_id': goal.id, 'goal_title': goal.title, 'reason': 'Alle Schritte erledigt — Ziel kann abgeschlossen werden'}
    planned = engine.list_goals(status='planned')
    if planned:
        goal = planned[0]
        return {'action': 'start_goal', 'goal_id': goal.id, 'goal_title': goal.title, 'reason': f"Kein aktives Ziel — '{goal.title}' hat höchste Priorität ({goal.priority})"}
    failed = engine.list_goals(status='failed')
    if failed:
        goal = failed[0]
        return {'action': 'retry_goal', 'goal_id': goal.id, 'goal_title': goal.title, 'reason': f"Fehlgeschlagenes Ziel '{goal.title}': {goal.last_error}"}
    return {'action': 'idle', 'reason': 'Keine offenen Ziele'}


def run_cycle(engine) -> dict:
    action = next_best_action(engine)
    performed: list[str] = []
    if action['action'] == 'start_goal':
        from eidolon.core.autonomy_goal_mutations import transition
        result = transition(engine, action['goal_id'], 'active')
        if result.get('ok'):
            performed.append(f"Ziel '{action['goal_title']}' aktiviert")
    for goal in engine.list_goals(status='active'):
        goal.cycles_run += 1
    engine.store.save()
    return {'ok': True, 'at': now_iso(), 'next_best_action': action, 'performed': performed}


def get_stats(engine) -> dict:
    goals = list(engine.store.goals.values())
    by_status: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for goal in goals:
        by_status[goal.status] = by_status.get(goal.status, 0) + 1
        by_category[goal.category] = by_category.get(goal.category, 0) + 1
    active = [goal for goal in goals if goal.status == 'active']
    overall = round(sum(goal.computed_progress() for goal in goals) / len(goals), 3) if goals else 0.0
    return {'total': len(goals), 'by_status': by_status, 'by_category': by_category, 'active_count': len(active), 'done_count': by_status.get('done', 0), 'overall_progress': overall, 'total_steps': sum(len(goal.steps) for goal in goals), 'done_steps': sum(1 for goal in goals for step in goal.steps if (step.done if isinstance(step, Step) else False))}


def has_open_problem(engine, problem_key: str) -> bool:
    return bool(problem_key) and any(goal.problem_key == problem_key and goal.status not in TERMINAL_STATES for goal in engine.store.goals.values())


def find_by_problem(engine, problem_key: str) -> Goal | None:
    for goal in engine.store.goals.values():
        if goal.problem_key == problem_key and goal.status not in TERMINAL_STATES:
            return goal
    return None
