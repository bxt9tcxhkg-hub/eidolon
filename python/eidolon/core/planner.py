from __future__ import annotations
import uuid
from typing import Any

from eidolon.core.agent_core import ProactiveAgent


class GoalPlanner:
    def __init__(self, llm: Any | None = None) -> None:
        self.llm = llm
        self.agent = ProactiveAgent(llm=llm)

    async def plan_goal(self, text: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        goal_id = uuid.uuid4().hex[:8]
        goal = {
            "id": goal_id,
            "title": "User Goal",
            "description": text,
            "success_criteria": [text],
            "status": "pending",
            "created_at": __import__("datetime").datetime.utcnow().isoformat(),
        }
        sub1_id = uuid.uuid4().hex[:8]
        sub2_id = uuid.uuid4().hex[:8]
        subs = [
            {"id": sub1_id, "goal_id": goal_id, "title": "Kontext aufnehmen", "depends_on": [], "status": "pending", "result": None},
            {"id": sub2_id, "goal_id": goal_id, "title": "Plan ausfuehren", "depends_on": [sub1_id], "status": "pending", "result": None},
        ]
        self.agent.goals[goal_id] = goal
        for sub in subs:
            self.agent.subtasks[sub["id"]] = sub
        self.agent.state["last_goal_id"] = goal_id
        return goal, subs
