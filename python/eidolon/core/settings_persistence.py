from __future__ import annotations

import json
from pathlib import Path

from eidolon.core.settings_schema import DEFAULT_SETTINGS
from eidolon.core.settings_validation import clone_default_settings, derive_stored_values


def load_settings(path: Path) -> tuple[dict, dict]:
    if path.exists():
        try:
            stored = json.loads(path.read_text(encoding='utf-8'))
            stored_values = derive_stored_values(stored)
            settings = clone_default_settings()
            for area, values in stored_values.items():
                if area in DEFAULT_SETTINGS:
                    settings[area].update(values)
                else:
                    settings[area] = dict(values)
            return settings, stored_values
        except (json.JSONDecodeError, OSError):
            pass
    return clone_default_settings(), {}


def save_settings(path: Path, stored_values: dict) -> None:
    try:
        path.write_text(json.dumps(stored_values, indent=2, ensure_ascii=False), encoding='utf-8')
    except OSError:
        pass
