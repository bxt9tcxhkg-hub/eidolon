from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from eidolon.core.config import state_path
from eidolon.memory.graph_support import apply_transition, ensure_plan_payload, load_plan_graph, save_plan_graph, transition_confidence, transition_dict


class KnowledgeGraph:
    def __init__(self):
        self.entities: dict[str, dict[str, Any]] = {}
        self.intents: list[dict[str, Any]] = []

    def _init_schema(self) -> None:
        return None

    def get_stats(self) -> dict[str, Any]:
        return {'entities': len(self.entities), 'intents': len(self.intents)}

    def add_entity(self, entity_id: str, entity_type: str, payload: dict[str, Any]) -> None:
        self.entities[entity_id] = {'type': entity_type, 'payload': payload}

    def store_intent(self, intent_id: str, name: str, confidence: float, params: dict[str, Any], skill_id: str) -> None:
        self.intents.append({'intent_id': intent_id, 'name': name, 'confidence': confidence, 'params': params, 'skill_id': skill_id})


@dataclass
class PlanTransition:
    plan_id: str
    from_node: str
    outcome: str
    to_node: str
    success: bool
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return transition_dict(self)


class PlanGraphStore:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.path = state_path('autonomy', 'plan_graph_store.json', project_root=self.project_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        return load_plan_graph(self.path)

    def _save(self, data: dict[str, Any]) -> None:
        save_plan_graph(self.path, data)

    def ensure_plan(self, plan_id: str) -> dict[str, Any]:
        data = self._load()
        plan = ensure_plan_payload(data, plan_id)
        self._save(data)
        return plan

    def record_transition(self, *, plan_id: str, from_node: str, outcome: str, to_node: str, success: bool, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        data = self._load()
        plan = ensure_plan_payload(data, plan_id)
        transition = PlanTransition(plan_id=plan_id, from_node=from_node, outcome=outcome, to_node=to_node, success=success, metadata=metadata or {}).to_dict()
        apply_transition(plan, transition)
        self._save(data)
        return transition

    def get_plan(self, plan_id: str) -> dict[str, Any]:
        data = self._load()
        return (data.get('plans') or {}).get(plan_id, ensure_plan_payload({}, plan_id))

    def get_transition_confidence(self, *, plan_id: str, from_node: str, outcome: str) -> float:
        return transition_confidence(self.get_plan(plan_id), from_node, outcome)

    def snapshot(self) -> dict[str, Any]:
        return self._load()
