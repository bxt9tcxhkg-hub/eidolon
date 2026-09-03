from __future__ import annotations

from eidolon.core.autonomy_goal_ops import add_step, create_goal, delete_goal, delete_step, enforce_single_active, find_by_problem, get_stats, has_open_problem, next_best_action, run_cycle, toggle_step, transition, update_goal
from eidolon.core.autonomy_store import AutonomyStore
from eidolon.core.autonomy_verifier import revalidate


class AutonomyEngine:
    """Verwaltet autonome Ziele mit Persistenz."""

    def __init__(self, project_root):
        self.store = AutonomyStore(project_root)

    def create_goal(self, title: str, description: str = '', category: str = 'system', priority: int = 1, steps: list[str] | None = None, persist: bool = True, source: str = 'manual', evidence: str = '', problem_key: str = ''):
        return create_goal(self, title, description=description, category=category, priority=priority, steps=steps, persist=persist, source=source, evidence=evidence, problem_key=problem_key)

    def has_source(self, source: str) -> bool:
        return any(goal.source == source for goal in self.store.goals.values())

    def has_open_problem(self, problem_key: str) -> bool:
        return has_open_problem(self, problem_key)

    def find_by_problem(self, problem_key: str):
        return find_by_problem(self, problem_key)

    def get_goal(self, goal_id: str):
        return self.store.goals.get(goal_id)

    def list_goals(self, status: str | None = None, category: str | None = None):
        goals = list(self.store.goals.values())
        if status:
            goals = [goal for goal in goals if goal.status == status]
        if category:
            goals = [goal for goal in goals if goal.category == category]
        status_rank = {'active': 0, 'planned': 1, 'paused': 2, 'failed': 3, 'done': 4, 'cancelled': 5}
        goals.sort(key=lambda goal: (status_rank.get(goal.status, 9), -goal.priority, goal.title.lower()))
        return goals

    def update_goal(self, goal_id: str, **fields):
        return update_goal(self, goal_id, **fields)

    def delete_goal(self, goal_id: str):
        return delete_goal(self, goal_id)

    def transition(self, goal_id: str, new_status: str, error: str | None = None, allow_multi_active: bool = False):
        return transition(self, goal_id, new_status, error=error, allow_multi_active=allow_multi_active)

    def active_goal(self):
        for goal in self.store.goals.values():
            if goal.status == 'active':
                return goal
        return None

    def enforce_single_active(self):
        return enforce_single_active(self)

    def add_step(self, goal_id: str, title: str):
        return add_step(self, goal_id, title)

    def toggle_step(self, goal_id: str, step_id: str):
        return toggle_step(self, goal_id, step_id)

    def delete_step(self, goal_id: str, step_id: str):
        return delete_step(self, goal_id, step_id)

    def revalidate(self, deriver, health: dict, auto_close: bool = False):
        return revalidate(self, deriver, health, auto_close=auto_close)

    def next_best_action(self):
        return next_best_action(self)

    def run_cycle(self):
        return run_cycle(self)

    def get_stats(self):
        return get_stats(self)

    def get_log(self, limit: int = 30):
        return self.store.get_log(limit)
