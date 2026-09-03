from __future__ import annotations

from typing import Any

BUILTIN_SKILLS: list[dict[str, Any]] = [
    {"name": "chat", "handler": "builtin", "description": "Allgemeiner Chat-Skill", "enabled": True, "priority": 0},
    {"name": "runtime_facts", "handler": "builtin", "description": "Liefert Fakten über den LLM-Runtime", "enabled": True, "priority": 0},
    {"name": "system_info", "handler": "builtin", "description": "System-Informationen", "enabled": True, "priority": 0},
    {"name": "goal_manager", "handler": "builtin", "description": "Verwalte autonome Ziele", "enabled": True, "priority": 0},
    {"name": "device_status", "handler": "builtin", "description": "Zeige verbundene Geräte", "enabled": True, "priority": 0},
    {"name": "mesh_send", "handler": "builtin", "description": "Nachricht an Peer senden", "enabled": True, "priority": 0},
    {"name": "note", "handler": "builtin", "description": "Notizen verwalten", "enabled": True, "priority": 0},
    {"name": "file_organizer", "handler": "builtin", "description": "Dateien organisieren", "enabled": True, "priority": 0},
]
