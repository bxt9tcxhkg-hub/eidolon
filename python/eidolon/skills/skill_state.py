from __future__ import annotations

import json
from pathlib import Path


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(path: Path, skills: dict) -> None:
    data = {name: {'enabled': skill.enabled, 'priority': skill.priority} for name, skill in skills.items()}
    try:
        path.write_text(json.dumps(data, indent=2))
    except OSError:
        pass
