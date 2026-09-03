from __future__ import annotations


def is_live_backup(entry):
    metadata = entry.get('metadata') or {}
    if metadata.get('live_visible') is False or metadata.get('archived_contamination'):
        return False
    marker = ' '.join(str(entry.get(k, '')) for k in ('id', 'reason', 'created_by')).lower()
    non_live_markers = ('test', 'dogfood', 'verification', 'fixture')
    if any(token in marker for token in non_live_markers):
        return False
    restoring = str(metadata.get('restoring', '')).lower()
    if any(token in restoring for token in non_live_markers):
        return False
    return True


def stats(entries: list[dict], max_backups: int, backup_dir: str) -> dict:
    visible = [entry for entry in entries if is_live_backup(entry)]
    total = sum(entry['size_bytes'] for entry in visible)
    return {'count': len(visible), 'hidden_count': len(entries) - len(visible), 'max_backups': max_backups, 'total_size_bytes': total, 'total_size_mb': round(total / 1024 / 1024, 2), 'backup_dir': backup_dir}
