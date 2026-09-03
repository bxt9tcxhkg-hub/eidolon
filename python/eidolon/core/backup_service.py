"""Backup-Service für Eidolon."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from eidolon.core.backup_actions import create_backup, restore_backup
from eidolon.core.backup_catalog import load_catalog, save_catalog
from eidolon.core.backup_models import BackupEntry
from eidolon.core.backup_utils import entry_metadata, entry_value, is_live_backup
from eidolon.core.config import state_path


class BackupService:
    """Erstellt und verwaltet Backups von Verzeichnissen."""

    @staticmethod
    def _entry_value(entry: BackupEntry | dict[str, Any], field: str, default: Any = None) -> Any:
        return entry_value(entry, field, default)

    @classmethod
    def _entry_metadata(cls, entry: BackupEntry | dict[str, Any]) -> dict[str, Any]:
        return entry_metadata(entry)

    def __init__(self, project_root: Path, max_backups: int = 10):
        self._root = Path(project_root)
        self._backup_dir = state_path('backups', project_root=self._root)
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        self._max_backups = max_backups
        self._catalog_path = self._backup_dir / 'catalog.json'
        self._entries: list[BackupEntry] = []
        self._load_catalog()

    def _load_catalog(self):
        self._entries = load_catalog(self._catalog_path)

    def _save_catalog(self):
        save_catalog(self._catalog_path, self._entries)

    def create_backup(self, source_dir: str | Path, reason: str = 'manual', created_by: str = 'manual', metadata: dict[str, Any] | None = None) -> BackupEntry:
        return create_backup(self, source_dir, reason=reason, created_by=created_by, metadata=metadata)

    def restore_backup(self, backup_id: str, target_dir: str | Path | None = None) -> Path:
        return restore_backup(self, backup_id, target_dir=target_dir)

    def get_backup(self, backup_id: str) -> BackupEntry | None:
        for entry in self._entries:
            if self._entry_value(entry, 'id') == backup_id:
                return entry
        return None

    def list_backups(self, limit: int | None = None) -> list[BackupEntry]:
        entries = [entry for entry in reversed(self._entries) if self.is_live_backup(entry)]
        return entries[:limit] if limit else entries

    def list_all_backups(self, limit: int | None = None) -> list[BackupEntry]:
        entries = list(reversed(self._entries))
        return entries[:limit] if limit else entries

    @staticmethod
    def is_live_backup(entry: BackupEntry) -> bool:
        return is_live_backup(entry)

    def delete_backup(self, backup_id: str) -> bool:
        entry = self.get_backup(backup_id)
        if entry is None:
            return False
        from shutil import rmtree
        backup_path = Path(self._entry_value(entry, 'backup_dir'))
        if backup_path.exists():
            rmtree(backup_path, ignore_errors=True)
        self._entries.remove(entry)
        self._save_catalog()
        return True

    def get_stats(self) -> dict[str, Any]:
        visible_entries = [entry for entry in self._entries if self.is_live_backup(entry)]
        total_size = sum(int(self._entry_value(entry, 'size_bytes', 0) or 0) for entry in visible_entries)
        return {'count': len(visible_entries), 'hidden_count': len(self._entries) - len(visible_entries), 'max_backups': self._max_backups, 'total_size_bytes': total_size, 'total_size_mb': round(total_size / 1024 / 1024, 2), 'backup_dir': str(self._backup_dir)}


_backup_service: BackupService | None = None


def get_backup_service(project_root: Path | None = None) -> BackupService:
    global _backup_service
    if _backup_service is None:
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent.parent.parent
        _backup_service = BackupService(project_root)
    return _backup_service
