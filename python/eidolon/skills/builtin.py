from __future__ import annotations
from pathlib import Path


SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


def ensure_builtin_skills() -> None:
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    skills = [
        {
            "id": "calendar-summarize",
            "name": "Kalender zusammenfassen",
            "description": "Fasst Kalendereinträge der nächsten 24h zusammen.",
            "tags": ["calendar", "summary", "daily"],
            "handler": "builtin.calendar_summarize",
            "params": {},
        },
        {
            "id": "system-info",
            "name": "Systeminfo",
            "description": "Zeigt Hostname, Plattform und Python-Version.",
            "tags": ["system", "info", "host"],
            "handler": "builtin.system_info",
            "params": {},
        },
        {
            "id": "chat",
            "name": "Chat mit Eidolon",
            "description": "Verwende Eidolon als KI-Assistent für natürliche Konversation.",
            "tags": ["chat", "conversation", "assistant"],
            "handler": "builtin.chat",
            "params": {"text": "string"},
        },
    ]
    import json
    for skill in skills:
        target = SKILLS_DIR / f"{skill['id']}.json"
        if not target.exists():
            target.write_text(json.dumps(skill, ensure_ascii=False, indent=2), encoding="utf-8")
