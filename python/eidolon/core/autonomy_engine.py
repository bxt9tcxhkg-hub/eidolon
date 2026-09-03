"""Autonomie-Engine für Eidolon — Ziele, Zyklen, Fortschritt."""
from __future__ import annotations

from pathlib import Path

from eidolon.core.autonomy_models import CATEGORIES, GOAL_TRANSITIONS, TERMINAL_STATES, Goal, Step
from eidolon.core.autonomy_runtime import AutonomyEngine

__all__ = [
    'AutonomyEngine',
    'CATEGORIES',
    'GOAL_TRANSITIONS',
    'Goal',
    'Step',
    'TERMINAL_STATES',
    'get_autonomy_engine',
]

_engine: AutonomyEngine | None = None


def get_autonomy_engine(project_root: Path) -> AutonomyEngine:
    global _engine
    if _engine is None:
        _engine = AutonomyEngine(project_root)
    return _engine
