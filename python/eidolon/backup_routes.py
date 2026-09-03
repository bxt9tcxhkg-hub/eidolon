from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI


def _entry_payload(entry: Any) -> dict[str, Any]:
    if isinstance(entry, dict):
        return dict(entry)
    return {
        'id': entry.id,
        'timestamp': entry.timestamp,
        'reason': entry.reason,
        'created_by': entry.created_by,
        'file_count': entry.file_count,
        'size_bytes': entry.size_bytes,
        'source_dir': entry.source_dir,
        'backup_dir': entry.backup_dir,
        'metadata': entry.metadata,
    }


def register_backup_routes(
    app: FastAPI,
    *,
    project_root: Path,
    get_backup_service: Callable[[], Any],
) -> None:
    def backup_service():
        return get_backup_service()

    @app.get("/backups")
    async def list_backups():
        backups = [{k: v for k, v in _entry_payload(b).items() if k in {'id','timestamp','reason','created_by','file_count','size_bytes','source_dir'}} for b in backup_service().list_backups()]
        return {"ok": True, "backups": backups, **backup_service().get_stats()}

    @app.post("/backups/create")
    async def create_backup(request: dict):
        source = request.get("source_dir", "python")
        reason = request.get("reason", "manual")
        target = project_root / source
        if not target.exists():
            return {"ok": False, "error": f"Nicht gefunden: {source}"}
        entry = _entry_payload(backup_service().create_backup(target, reason=reason, created_by='user'))
        return {'ok': True, 'id': entry['id'], 'file_count': entry['file_count'], 'size_bytes': entry['size_bytes'], 'timestamp': entry['timestamp']}

    @app.post("/backups/{backup_id}/restore")
    async def restore_backup(backup_id: str, request: dict | None = None):
        entry = backup_service().get_backup(backup_id)
        if not entry:
            return {"ok": False, "error": "Backup nicht gefunden"}
        target = (request or {}).get("target_dir")
        if target:
            target = project_root / target
        try:
            restored_path = backup_service().restore_backup(backup_id, target)
            return {"ok": True, "restored_to": str(restored_path), "backup_id": backup_id}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @app.delete("/backups/{backup_id}")
    async def delete_backup(backup_id: str):
        success = backup_service().delete_backup(backup_id)
        return {"ok": success}
