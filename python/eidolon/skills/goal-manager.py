"""Ziel-Manager-Skill: Verwaltet langfristige Ziele."""
from datetime import datetime, timezone
import json

from eidolon.core.config import state_path

def run(params: dict) -> dict:
    goals_path = state_path('persistence', 'goals.json')
    goals_path.parent.mkdir(parents=True, exist_ok=True)
    
    goals = []
    if goals_path.exists():
        goals = json.loads(goals_path.read_text())
    
    action = params.get("action", "list")
    
    if action == "add":
        goal = {
            "id": str(len(goals) + 1),
            "title": params.get("goal", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }
        goals.append(goal)
    elif action == "list":
        return {"goals": goals, "total": len(goals)}
    elif action == "complete":
        goal_id = params.get("id")
        for g in goals:
            if g["id"] == goal_id:
                g["status"] = "completed"
    
    goals_path.write_text(json.dumps(goals, indent=2))
    return {"goals": goals, "total": len(goals)}
