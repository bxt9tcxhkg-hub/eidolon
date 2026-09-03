from __future__ import annotations

from pathlib import Path
from typing import Any

from eidolon.core.backup_models import BackupEntry

NON_LIVE_MARKERS = ('test', 'dogfood', 'verification', 'fixture')
IGNORE_PATTERNS = ['__pycache__', '*.pyc', '*.pyo', '.git', '*.egg-info', 'node_modules', '.tox', '.pytest_cache', '*.so', '*.dylib', '*.pyd']


def entry_value(entry: BackupEntry | dict[str, Any], field: str, default: Any = None) -> Any:
    return entry.get(field, default) if isinstance(entry, dict) else getattr(entry, field, default)


def entry_metadata(entry: BackupEntry | dict[str, Any]) -> dict[str, Any]:
    metadata = entry_value(entry, 'metadata', {})
    return metadata if isinstance(metadata, dict) else {}


def is_live_backup(entry: BackupEntry | dict[str, Any]) -> bool:
    metadata = entry_metadata(entry)
    if metadata.get('live_visible') is False or metadata.get('archived_contamination'):
        return False
    marker = f"{entry_value(entry, 'id', '')} {entry_value(entry, 'reason', '')} {entry_value(entry, 'created_by', '')}".lower()
    if any(token in marker for token in NON_LIVE_MARKERS):
        return False
    restoring = str(metadata.get('restoring', '')).lower()
    return not any(token in restoring for token in NON_LIVE_MARKERS)


def count_files(path: Path) -> tuple[int, int]:
    total_size = 0
    file_count = 0
    if path.is_dir():
        for item in path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
                file_count += 1
    elif path.is_file():
        total_size = path.stat().st_size
        file_count = 1
    return total_size, file_count
