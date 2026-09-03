from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path


def git_status(project_root: Path) -> dict:
    try:
        import subprocess
        result = subprocess.run(['git', 'log', '--oneline', '-10'], capture_output=True, text=True, cwd=str(project_root))
        commits = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        return {'recent_commits': commits, 'last_update': commits[0] if commits else 'unbekannt'}
    except Exception:
        return {'recent_commits': [], 'last_update': 'unbekannt'}


def project_stats(project_root: Path) -> dict:
    py_files = list((project_root / 'python').rglob('*.py'))
    rs_files = list((project_root / 'crates').rglob('*.rs'))
    md_files = list(project_root.glob('*.md'))
    total_lines = 0
    for f in py_files[:50]:
        try:
            total_lines += len(f.read_text(encoding='utf-8', errors='replace').splitlines())
        except Exception:
            pass
    return {'python_files': len(py_files), 'rust_files': len(rs_files), 'markdown_files': len(md_files), 'sampled_python_lines': total_lines, 'generated_at': datetime.now(timezone.utc).isoformat(), 'project_root': str(project_root), 'basename': os.path.basename(project_root)}
