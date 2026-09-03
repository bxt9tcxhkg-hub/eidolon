from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from eidolon.core.config import resolve_state_root, state_path


def system_metrics_payload(server_start: float, human_duration, http_port: int, quic_port: int, project_root: Path) -> dict[str, Any]:
    import platform, sys as _sys, time as _time
    uptime_s = int(_time.time() - server_start)
    out = {'ok': True, 'uptime_seconds': uptime_s, 'uptime_human': human_duration(uptime_s), 'started_at': datetime.fromtimestamp(server_start, tz=timezone.utc).isoformat(), 'python_version': _sys.version.split()[0], 'platform': f'{platform.system()} {platform.release()}', 'http_port': http_port, 'quic_port': quic_port, 'project_root': str(project_root)}
    try:
        import psutil
        process = psutil.Process(os.getpid())
        with process.oneshot():
            out['process'] = {'available': True, 'pid': process.pid, 'memory_mb': round(process.memory_info().rss / 1024 / 1024, 1), 'cpu_percent': process.cpu_percent(interval=0.1), 'threads': process.num_threads()}
        vm = psutil.virtual_memory(); du = psutil.disk_usage(str(project_root))
        out['system'] = {'available': True, 'cpu_percent': psutil.cpu_percent(interval=0.1), 'cpu_count': psutil.cpu_count(), 'ram_used_gb': round(vm.used / 1024**3, 1), 'ram_total_gb': round(vm.total / 1024**3, 1), 'ram_percent': vm.percent, 'disk_free_gb': round(du.free / 1024**3, 1), 'disk_percent': du.percent}
    except ImportError:
        out['process'] = {'available': False, 'reason': 'psutil nicht installiert', 'pid': os.getpid()}
        out['system'] = {'available': False, 'reason': 'psutil nicht installiert'}
    return out


def system_storage_payload(project_root: Path) -> dict[str, Any]:
    state_root = resolve_state_root(project_root)
    def dir_stats(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {'exists': False, 'files': 0, 'size_mb': 0.0}
        files = 0; size = 0
        for file in path.rglob('*'):
            if file.is_file():
                files += 1
                try: size += file.stat().st_size
                except OSError: pass
        return {'exists': True, 'files': files, 'size_mb': round(size / 1024 / 1024, 2)}
    return {'ok': True, 'state_root': str(state_root), 'areas': {area: dir_stats(state_path(area, project_root=project_root)) for area in ['backups','autonomy','mesh','user','voice','generated','browser','evidence','operate']}}
