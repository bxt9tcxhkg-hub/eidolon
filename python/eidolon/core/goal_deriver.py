"""Ziel-Ableitung aus echtem Systemzustand — mit Revalidierung.

Zentrale Regeln:
1. Jedes Problem hat einen kanonischen `problem_key` (nicht nur eine Quelle).
2. `verify()` prüft, ob ein Problem NOCH existiert.
3. Beschreibung und Beleg werden nie eingefroren — sie können neu erhoben werden.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from eidolon.core.goal_deriver_health import from_capabilities, from_certificates
from eidolon.core.goal_deriver_keys import KEY_BACKUPS, KEY_CAP_PREFIX, KEY_CERTIFICATES, KEY_ROADMAP_PREFIX, KEY_RUST_STUBS
from eidolon.core.goal_deriver_sources import from_roadmap, from_rust_stubs
from eidolon.core.goal_deriver_verify import derive_all, from_backups, verify_problem


class GoalDeriver:
    """Leitet Ziele aus messbarem Systemzustand ab und revalidiert sie."""

    def __init__(self, project_root: Path):
        self._root = Path(project_root)

    def from_capabilities(self, health: dict[str, Any]) -> list[dict[str, Any]]:
        return from_capabilities(health)

    def from_certificates(self, health: dict[str, Any]) -> list[dict[str, Any]]:
        return from_certificates(health)

    def from_roadmap(self) -> list[dict[str, Any]]:
        return from_roadmap(self._root)

    def from_rust_stubs(self) -> list[dict[str, Any]]:
        return from_rust_stubs(self._root)

    def from_backups(self) -> list[dict[str, Any]]:
        return from_backups(self._root)

    def verify(self, problem_key: str, health: dict[str, Any]) -> dict[str, Any]:
        return verify_problem(self._root, problem_key, health)

    def derive_all(self, health: dict[str, Any] | None = None) -> dict[str, Any]:
        return derive_all(self._root, health, from_capabilities_fn=from_capabilities, from_certificates_fn=from_certificates)


__all__ = [
    'GoalDeriver',
    'KEY_BACKUPS',
    'KEY_CAP_PREFIX',
    'KEY_CERTIFICATES',
    'KEY_ROADMAP_PREFIX',
    'KEY_RUST_STUBS',
]
