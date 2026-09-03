from __future__ import annotations

from pathlib import Path
import json


def load_catalog(path: Path) -> list[dict]:
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            return data.get('entries', [])
        except Exception:
            return []
    return []


def save_catalog(path: Path, entries: list[dict]) -> None:
    path.write_text(json.dumps({'entries': entries}, indent=2), encoding='utf-8')
