from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from eidolon.core.autonomy_models import Goal, serialize_goals_payload
from eidolon.core.config import state_path


def now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


class AutonomyStore:
    def __init__(self, project_root: Path):
        self._root = Path(project_root)
        self._path = state_path('autonomy', 'goals.json', project_root=self._root)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._goals: dict[str, Goal] = {}
        self._log: list[dict] = []
        self.load()

    def load(self) -> None:
        if not self._path.exists():
            self.seed_defaults()
            return
        try:
            data = json.loads(self._path.read_text(encoding='utf-8'))
            for gd in data.get('goals', []):
                goal = Goal.from_dict(gd)
                self._goals[goal.id] = goal
            self._log = data.get('log', [])[-200:]
        except Exception:
            self.seed_defaults()

    def save(self) -> None:
        self._path.write_text(serialize_goals_payload(self._goals, self._log, now_iso()), encoding='utf-8')

    def seed_defaults(self) -> None:
        self._goals = {}
        self._log = []
        self.save()

    def add_log(self, goal_id: str, action: str, detail: str = '') -> None:
        self._log.append({'at': now_iso(), 'goal_id': goal_id, 'action': action, 'detail': detail})

    @property
    def goals(self) -> dict[str, Goal]:
        return self._goals

    def get_log(self, limit: int = 30) -> list[dict]:
        return list(reversed(self._log[-limit:]))
