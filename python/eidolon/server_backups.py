from __future__ import annotations

from datetime import datetime
from pathlib import Path

from eidolon.core.config import state_path
from eidolon.server_backups_catalog import load_catalog, save_catalog
from eidolon.server_backups_files import copy_source_tree, restore_tree, rotate_entries
from eidolon.server_backups_views import is_live_backup, stats


class BackupService:
    def __init__(self, project_root: Path, max_backups: int = 10):
        self._root = Path(project_root)
        self._backup_dir = state_path('backups', project_root=self._root)
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        self._max_backups = max_backups
        self._catalog_path = self._backup_dir / 'catalog.json'
        self._entries = load_catalog(self._catalog_path)

    def _save_catalog(self):
        save_catalog(self._catalog_path, self._entries)

    def _rotate(self):
        rotate_entries(self)

    def create_backup(self, source_dir, reason='manual', created_by='manual', metadata=None):
        source = Path(source_dir)
        if not source.exists():
            raise FileNotFoundError(f'Nicht gefunden: {source}')
        timestamp = datetime.now()
        backup_id = timestamp.strftime('%Y%m%d_%H%M%S')
        if reason:
            backup_id += f'_{reason[:20]}'
        backup_path = self._backup_dir / backup_id
        if backup_path.exists():
            __import__('shutil').rmtree(backup_path, ignore_errors=True)
        size, count = copy_source_tree(source, backup_path)
        entry = {'id': backup_id, 'timestamp': timestamp.isoformat(), 'reason': reason, 'source_dir': str(source), 'backup_dir': str(backup_path), 'size_bytes': size, 'file_count': count, 'created_by': created_by, 'metadata': metadata or {}}
        self._entries.append(entry)
        self._rotate()
        self._save_catalog()
        return entry

    def restore_backup(self, backup_id, target_dir=None):
        entry = self.get_backup(backup_id)
        if not entry:
            raise FileNotFoundError(f'Backup nicht gefunden: {backup_id}')
        backup_path = Path(entry['backup_dir'])
        if not backup_path.exists():
            raise FileNotFoundError(f'Backup-Verzeichnis nicht gefunden: {backup_path}')
        target = Path(target_dir or entry['source_dir'])
        return restore_tree(self, backup_path, target, backup_id)

    def get_backup(self, backup_id):
        for entry in self._entries:
            if entry['id'] == backup_id:
                return entry
        return None

    @staticmethod
    def is_live_backup(entry):
        return is_live_backup(entry)

    def list_backups(self, limit=None):
        entries = [entry for entry in reversed(self._entries) if self.is_live_backup(entry)]
        return entries[:limit] if limit else entries

    def list_all_backups(self, limit=None):
        entries = list(reversed(self._entries))
        return entries[:limit] if limit else entries

    def delete_backup(self, backup_id):
        entry = self.get_backup(backup_id)
        if not entry:
            return False
        backup_path = Path(entry['backup_dir'])
        if backup_path.exists():
            __import__('shutil').rmtree(backup_path, ignore_errors=True)
        self._entries.remove(entry)
        self._save_catalog()
        return True

    def get_stats(self):
        return stats(self._entries, self._max_backups, str(self._backup_dir))
