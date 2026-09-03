from __future__ import annotations

from dataclasses import asdict
from typing import Any
import json


def empty_plan_graph() -> dict[str, Any]:
    return {'nodes': {}, 'edges': {}, 'transitions': []}


def load_plan_graph(path) -> dict[str, Any]:
    if not path.exists():
        return {'plans': {}}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {'plans': {}}


def save_plan_graph(path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def ensure_plan_payload(data: dict[str, Any], plan_id: str) -> dict[str, Any]:
    plans = data.setdefault('plans', {})
    return plans.setdefault(plan_id, empty_plan_graph())


def transition_dict(transition) -> dict[str, Any]:
    return asdict(transition)


def apply_transition(plan: dict[str, Any], transition: dict[str, Any]) -> None:
    plan.setdefault('transitions', []).append(transition)
    from_node = transition['from_node']
    outcome = transition['outcome']
    to_node = transition['to_node']
    success = bool(transition['success'])
    node = plan.setdefault('nodes', {}).setdefault(from_node, {'visits': 0, 'successes': 0, 'failures': 0, 'outcomes': {}})
    node['visits'] += 1
    node['successes' if success else 'failures'] += 1
    outcome_entry = node.setdefault('outcomes', {}).setdefault(outcome, {'count': 0, 'successes': 0, 'failures': 0, 'last_to': to_node})
    outcome_entry['count'] += 1
    outcome_entry['last_to'] = to_node
    outcome_entry['successes' if success else 'failures'] += 1
    edge_key = f'{from_node}::{outcome}::{to_node}'
    edge = plan.setdefault('edges', {}).setdefault(edge_key, {'from_node': from_node, 'outcome': outcome, 'to_node': to_node, 'count': 0, 'successes': 0, 'failures': 0})
    edge['count'] += 1
    edge['successes' if success else 'failures'] += 1


def transition_confidence(plan: dict[str, Any], from_node: str, outcome: str) -> float:
    node = (plan.get('nodes') or {}).get(from_node) or {}
    outcome_entry = (node.get('outcomes') or {}).get(outcome) or {}
    count = float(outcome_entry.get('count', 0))
    if count <= 0:
        return 0.0
    return float(outcome_entry.get('successes', 0)) / count
