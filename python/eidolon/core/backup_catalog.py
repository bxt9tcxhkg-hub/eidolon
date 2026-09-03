from __future__ import annotations

import json
from pathlib import Path

from eidolon.core.backup_models import BackupEntry


def load_catalog(path: Path) -> list[BackupEntry]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return [BackupEntry(**entry) for entry in data.get('entries', [])]
    except (json.JSONDecodeError, TypeError):
        return []


def save_catalog(path: Path, entries: list[BackupEntry]) -> None:
    payload = {'entries': [entry.__dict__ for entry in entries]}
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
