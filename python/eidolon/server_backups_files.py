from __future__ import annotations

from pathlib import Path
import os
import shutil


def rotate_entries(service) -> None:
    while len(service._entries) > service._max_backups:
        oldest = service._entries.pop(0)
        backup_path = Path(oldest['backup_dir'])
        if backup_path.exists():
            shutil.rmtree(backup_path, ignore_errors=True)


def copy_source_tree(source: Path, backup_path: Path) -> tuple[int, int]:
    ignore_dirs = {'__pycache__', '.git', 'node_modules', '.tox', '.pytest_cache', 'data', 'mesh', 'memory', 'persist', 'search_cache', 'notes'}
    ignore_exts = {'.pyc', '.pyo', '.so', '.dylib', '.pyd', '.bak', '.tmp', '.log'}
    ignore_names = {'nul', 'con', 'prn', 'aux', 'com1', 'lpt1', 'com2', 'lpt2', 'com3', 'lpt3'}
    for root, dirs, files in os.walk(source):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.endswith('.egg-info') and d.lower() not in ignore_names]
        rel = Path(root).relative_to(source)
        target = backup_path / rel
        target.mkdir(parents=True, exist_ok=True)
        for file_name in files:
            if any(file_name.endswith(ext) for ext in ignore_exts) or file_name.lower() in ignore_names:
                continue
            shutil.copy2(Path(root) / file_name, target / file_name)
    size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
    count = sum(1 for f in backup_path.rglob('*') if f.is_file())
    return size, count


def restore_tree(service, backup_path: Path, target: Path, backup_id: str):
    if target.exists():
        service.create_backup(target, reason='pre_restore', created_by='auto', metadata={'restoring': backup_id})
        shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)
    for item in backup_path.iterdir():
        destination = target / item.name
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)
    return target
