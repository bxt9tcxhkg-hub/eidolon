from __future__ import annotations

from typing import Any


def autonomy_defaults() -> dict[str, Any]:
    return {'level': 'proactive', 'cycle_interval_s': 300, 'budget_recovery': 1.0, 'budget_planning': 1.0, 'budget_analysis': 1.0, 'budget_mesh': 0.5, 'budget_implementation': 1.0, 'budget_maintenance': 0.5, 'self_improvement_allowed': True, 'self_improvement_max_risk': 'medium', 'cooldown_action_s': 60, 'cooldown_repeated_fail_s': 300, 'goals': []}


def autonomy_enum_rules() -> dict[tuple[str, str], set[str]]:
    return {('autonomy', 'level'): {'passive', 'proactive', 'full'}, ('autonomy', 'self_improvement_max_risk'): {'low', 'medium', 'high'}}


def autonomy_int_rules() -> dict[tuple[str, str], tuple[int, int]]:
    return {('autonomy', 'cycle_interval_s'): (1, 86400), ('autonomy', 'cooldown_action_s'): (0, 86400), ('autonomy', 'cooldown_repeated_fail_s'): (0, 604800)}


def autonomy_float_rules() -> dict[tuple[str, str], tuple[float, float]]:
    return {('autonomy', 'budget_recovery'): (0.0, 10.0), ('autonomy', 'budget_planning'): (0.0, 10.0), ('autonomy', 'budget_analysis'): (0.0, 10.0), ('autonomy', 'budget_mesh'): (0.0, 10.0), ('autonomy', 'budget_implementation'): (0.0, 10.0), ('autonomy', 'budget_maintenance'): (0.0, 10.0)}
