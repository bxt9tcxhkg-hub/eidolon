from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


GOAL_TRANSITIONS: dict[str, list[str]] = {
    "planned": ["active", "cancelled"],
    "active": ["paused", "done", "failed", "cancelled"],
    "paused": ["active", "cancelled"],
    "done": [],
    "failed": ["active"],
    "cancelled": [],
}

TERMINAL_STATES = {"done", "cancelled"}

CATEGORIES = ["system", "documentation", "monitoring", "development", "research", "maintenance"]


@dataclass
class Step:
    id: str
    title: str
    done: bool = False
    completed_at: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Goal:
    id: str
    title: str
    description: str = ""
    category: str = "system"
    status: str = "planned"
    priority: int = 1
    progress: float = 0.0
    steps: list[Step] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    started_at: str | None = None
    completed_at: str | None = None
    last_error: str | None = None
    cycles_run: int = 0
    source: str = "manual"
    evidence: str = ""
    problem_key: str = ""
    verified_at: str = ""
    verify_state: str = "unknown"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["steps"] = [s.to_dict() if isinstance(s, Step) else s for s in self.steps]
        d["progress"] = self.computed_progress()
        d["steps_done"] = sum(1 for s in self.steps if (s.done if isinstance(s, Step) else s.get("done")))
        d["steps_total"] = len(self.steps)
        d["allowed_transitions"] = GOAL_TRANSITIONS.get(self.status, [])
        return d

    def computed_progress(self) -> float:
        if self.steps:
            done = sum(1 for s in self.steps if (s.done if isinstance(s, Step) else s.get("done")))
            return round(done / len(self.steps), 3)
        if self.status == "done":
            return 1.0
        return round(self.progress, 3)

    @classmethod
    def from_dict(cls, data: dict) -> "Goal":
        steps = [Step(**s) if isinstance(s, dict) else s for s in data.get("steps", [])]
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            title=data.get("title", "Unbenannt"),
            description=data.get("description", ""),
            category=data.get("category", "system"),
            status=data.get("status", "planned"),
            priority=int(data.get("priority", 1)),
            progress=float(data.get("progress", 0.0)),
            steps=steps,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            last_error=data.get("last_error"),
            cycles_run=int(data.get("cycles_run", 0)),
            source=data.get("source", "manual"),
            evidence=data.get("evidence", ""),
            problem_key=data.get("problem_key", ""),
            verified_at=data.get("verified_at", ""),
            verify_state=data.get("verify_state", "unknown"),
        )


def serialize_goals_payload(goals: dict[str, Goal], log: list[dict], saved_at: str) -> str:
    payload = {
        "goals": [g.to_dict() for g in goals.values()],
        "log": log[-200:],
        "saved_at": saved_at,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
