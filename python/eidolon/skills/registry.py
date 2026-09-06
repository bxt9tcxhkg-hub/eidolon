"""Skill-Registry mit Management-Funktionen (ein/aus schalten, Priorität)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from eidolon.core.config import state_path
from eidolon.skills.skill_catalog import builtin_skills, file_skills
from eidolon.skills.skill_routing import extract_skill_name
from eidolon.skills.skill_state import load_state, save_state
from eidolon.skills.skill_types import Skill


class SkillRegistry:
    """Zentrale Skill-Registry mit Management-Funktionen."""

    def __init__(self, skills_dir: str | Path):
        self.skills_dir = Path(skills_dir)
        self.skills: dict[str, Skill] = {}
        self._state_file = state_path('user', 'skill_state.json')
        self._state_file.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        if not self.skills:
            self.skills = builtin_skills()
            self.skills.update(file_skills(self.skills_dir, self.skills))
        self._restore_state()

    def _restore_state(self) -> None:
        for name, state in load_state(self._state_file).items():
            if name in self.skills:
                if 'enabled' in state:
                    self.skills[name].enabled = state['enabled']
                if 'priority' in state:
                    self.skills[name].priority = state['priority']

    def _save_state(self) -> None:
        save_state(self._state_file, self.skills)

    def enable(self, name: str) -> dict[str, Any]:
        if name not in self.skills:
            return {'ok': False, 'error': f'Skill nicht gefunden: {name}'}
        self.skills[name].enabled = True
        self._save_state()
        return {'ok': True, 'skill': name, 'enabled': True}

    def disable(self, name: str) -> dict[str, Any]:
        if name not in self.skills:
            return {'ok': False, 'error': f'Skill nicht gefunden: {name}'}
        self.skills[name].enabled = False
        self._save_state()
        return {'ok': True, 'skill': name, 'enabled': False}

    def toggle(self, name: str) -> dict[str, Any]:
        if name not in self.skills:
            return {'ok': False, 'error': f'Skill nicht gefunden: {name}'}
        self.skills[name].enabled = not self.skills[name].enabled
        self._save_state()
        return {'ok': True, 'skill': name, 'enabled': self.skills[name].enabled}

    def set_priority(self, name: str, priority: int) -> dict[str, Any]:
        if name not in self.skills:
            return {'ok': False, 'error': f'Skill nicht gefunden: {name}'}
        self.skills[name].priority = priority
        self._save_state()
        return {'ok': True, 'skill': name, 'priority': priority}

    def get_state(self, name: str) -> dict[str, Any]:
        if name not in self.skills:
            return {'ok': False, 'error': f'Skill nicht gefunden: {name}'}
        return {'ok': True, 'skill': self.skills[name].to_dict()}

    def list_all(self) -> list[dict[str, Any]]:
        return [skill.to_dict() for skill in self.skills.values()]

    def list_enabled(self) -> list[dict[str, Any]]:
        return [skill.to_dict() for skill in self.skills.values() if skill.enabled]

    def execute(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        skill = self.skills.get(name)
        if not skill:
            return {'ok': False, 'wired': False, 'executed': False, 'reply': f'Skill nicht gefunden: {name}'}
        if not skill.enabled:
            return {'ok': False, 'wired': bool(skill.runtime_wired), 'executed': False, 'reply': f'Skill deaktiviert: {name}'}
        try:
            result = skill.fn(payload or {})
            if isinstance(result, dict):
                return result
            return {'ok': False, 'wired': bool(skill.runtime_wired), 'executed': False, 'reply': 'Skill lieferte kein Objekt'}
        except Exception as exc:
            return {'ok': False, 'wired': bool(skill.runtime_wired), 'executed': True, 'reply': f'Fehler bei {name}: {exc}'}

    def skill_registry_extract(self, text: str) -> str | None:
        return extract_skill_name(text)
