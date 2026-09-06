from __future__ import annotations

from typing import Any

from eidolon.skills.chat_skill_turn import catalog_flags

BUILTIN_SKILLS: list[dict[str, Any]] = [
    {"name": "chat", "handler": "catalog", "description": "Allgemeiner Chat-Skill", "enabled": True, "priority": 0},
    {"name": "runtime_facts", "handler": "catalog", "description": "Liefert Fakten über den LLM-Runtime", "enabled": True, "priority": 0},
    {"name": "system_info", "handler": "file", "description": "System-Informationen vom Host", "enabled": True, "priority": 0},
    {"name": "goal_manager", "handler": "catalog", "description": "Verwalte autonome Ziele", "enabled": True, "priority": 0},
    {"name": "device_status", "handler": "file", "description": "Geräte und Mesh-Inbox", "enabled": True, "priority": 0},
    {"name": "mesh_send", "handler": "catalog", "description": "Nachricht an Peer senden", "enabled": True, "priority": 0},
    {"name": "note", "handler": "file", "description": "Notizen in notes.json", "enabled": True, "priority": 0},
    {"name": "file_organizer", "handler": "catalog", "description": "Dateien organisieren", "enabled": True, "priority": 0},
    {"name": "calendar", "handler": "catalog", "description": "Kalender-Verwaltung", "enabled": True, "priority": 0},
]


def annotate_builtin_skill(skill: dict[str, Any]) -> dict[str, Any]:
    return {**skill, **catalog_flags(str(skill.get('name') or ''))}


def lookup_builtin_enabled(name: str) -> bool:
    for skill in BUILTIN_SKILLS:
        if skill.get('name') == name:
            return bool(skill.get('enabled', True))
    return True
