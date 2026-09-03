from __future__ import annotations

from pathlib import Path
from typing import Any


def self_reflect_candidates(project_root: Path, code_analyzer: Any, limit: int = 5) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for rel in [
        'python/agent_server.py',
        'python/eidolon/web/index.html',
        'python/eidolon/web/app-shell.js',
        'python/eidolon/workspaces/workspace_ui_service.py',
    ]:
        target = project_root / rel
        if not target.exists():
            continue
        analysis = code_analyzer.analyze_file(str(target))
        if isinstance(analysis, dict) and not analysis.get('error'):
            candidates.append({
                'file': rel,
                'maintainability': analysis.get('maintainability'),
                'complexity': analysis.get('complexity'),
                'lines': analysis.get('lines'),
                'long_functions': analysis.get('long_functions', []),
            })
    candidates.sort(key=lambda item: ((item.get('maintainability') or 100), -int(item.get('lines') or 0)))
    return candidates[: max(1, min(limit, 20))]
