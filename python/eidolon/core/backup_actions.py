from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from eidolon.core.backup_models import BackupEntry
from eidolon.core.backup_utils import IGNORE_PATTERNS, count_files, entry_value


def rotate_entries(service) -> None:
    while len(service._entries) > service._max_backups:
        oldest = service._entries.pop(0)
        backup_path = Path(oldest.backup_dir)
        if backup_path.exists():
            shutil.rmtree(backup_path, ignore_errors=True)


def create_backup(service, source_dir: str | Path, reason: str = 'manual', created_by: str = 'manual', metadata: dict[str, Any] | None = None) -> BackupEntry:
    source = Path(source_dir)
    if not source.exists():
        raise FileNotFoundError(f'Quellverzeichnis nicht gefunden: {source}')
    timestamp = datetime.now()
    backup_id = timestamp.strftime('%Y%m%d_%H%M%S') + (f'_{reason[:20]}' if reason else '')
    backup_path = service._backup_dir / backup_id
    if source.is_dir():
        shutil.copytree(source, backup_path, ignore=shutil.ignore_patterns(*IGNORE_PATTERNS))
    else:
        backup_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, backup_path / source.name)
    size_bytes, file_count = count_files(backup_path)
    entry = BackupEntry(id=backup_id, timestamp=timestamp.isoformat(), reason=reason, source_dir=str(source), backup_dir=str(backup_path), size_bytes=size_bytes, file_count=file_count, created_by=created_by, metadata=metadata or {})
    service._entries.append(entry)
    rotate_entries(service)
    service._save_catalog()
    return entry


def restore_backup(service, backup_id: str, target_dir: str | Path | None = None) -> Path:
    entry = service.get_backup(backup_id)
    if entry is None:
        raise FileNotFoundError(f'Backup nicht gefunden: {backup_id}')
    backup_path = Path(entry_value(entry, 'backup_dir'))
    if not backup_path.exists():
        raise FileNotFoundError(f'Backup-Verzeichnis nicht gefunden: {backup_path}')
    target = Path(target_dir or entry.source_dir)
    if target.exists():
        service.create_backup(target, reason='pre_restore', created_by='auto', metadata={'restoring': backup_id})
        shutil.rmtree(target, ignore_errors=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    if backup_path.is_dir():
        shutil.copytree(backup_path, target, dirs_exist_ok=True)
    else:
        shutil.copy2(backup_path, target)
    return target
