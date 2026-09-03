from __future__ import annotations
import uuid
from typing import Any

from eidolon.core.world_model import WorldStore, Device
from eidolon.core.sync import SyncState, SyncOp


class ProactiveAgent:
    def __init__(self, llm: Any | None = None) -> None:
        self.llm = llm
        self.goals: dict[str, Any] = {}
        self.subtasks: dict[str, Any] = {}
        self.state: dict[str, Any] = {"last_goal_id": None}

    def ingest_user_message(self, message: str) -> None:
        goals = list(self.goals.keys())
        self.state["last_goal_id"] = goals[-1] if goals else None

    def tick(self) -> str | None:
        gid = self.state.get("last_goal_id")
        if not gid:
            return None
        goal = self.goals.get(gid)
        if not goal or goal.get("status") == "done":
            return None
        for sub in self.subtasks.values():
            if sub.get("goal_id") == gid and sub.get("status") == "pending":
                deps = sub.get("depends_on", [])
                if all(self.subtasks.get(dep, {}).get("status") == "done" for dep in deps):
                    sub["status"] = "done"
                    sub["result"] = f'Subtask "{sub["title"]}" ausgefuehrt.'
                    return f'Subtask "{sub["title"]}" abgeschlossen.'
        goal["status"] = "done"
        return f'Goal "{goal.get("title", "Goal")}" abgeschlossen.'
