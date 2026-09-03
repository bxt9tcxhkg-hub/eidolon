from __future__ import annotations

from pathlib import Path


def scan_modules(project_root: Path) -> list[dict]:
    modules = []
    src = project_root / 'python' / 'eidolon'
    if not src.exists():
        return modules
    for item in sorted(src.iterdir()):
        if item.is_dir() and not item.name.startswith('__'):
            py_files = list(item.glob('*.py'))
            modules.append({'name': item.name, 'path': str(item.relative_to(project_root)), 'files': len(py_files), 'functions': sum(1 for f in py_files for line in f.read_text(encoding='utf-8', errors='replace').splitlines() if line.strip().startswith('def ')), 'status': 'active' if py_files else 'empty'})
    return modules
