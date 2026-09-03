from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .models import CodeFinding, FileMetrics


def _scan_python_file(path: Path) -> FileMetrics:
    """Scan a Python file for metrics."""
    metrics = FileMetrics(path=str(path))
    try:
        source = path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return metrics

    metrics.loc = len(source.splitlines())

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return metrics

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            metrics.functions += 1
        elif isinstance(node, ast.ClassDef):
            metrics.classes += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            metrics.imports += 1

    # Count TODO/FIXME/HACK comments
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith('#'):
            comment = stripped[1:].strip().lower()
            if 'todo' in comment[:4]:
                metrics.todos += 1
            elif 'fixme' in comment[:5]:
                metrics.fixmes += 1
            elif 'hack' in comment[:4]:
                metrics.fixmes += 1

    # Simple complexity: count branches
    COMPLEXITY_NODES = (ast.If, ast.For, ast.While, ast.With, ast.Try)
    for node in ast.walk(tree):
        if isinstance(node, COMPLEXITY_NODES):
            metrics.complexity_score += 1

    return metrics


def _extract_findings(path: Path, root: Path, source: str, findings: list[CodeFinding]) -> None:
    """Extract code findings from a file."""
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if not stripped.startswith('#'):
            continue
        comment = stripped[1:].strip().lower()
        if comment.startswith('todo'):
            findings.append(CodeFinding(
                file=str(path.relative_to(root)),
                line=i,
                kind='todo',
                text=stripped,
                severity='info',
            ))
        elif comment.startswith('fixme'):
            findings.append(CodeFinding(
                file=str(path.relative_to(root)),
                line=i,
                kind='fixme',
                text=stripped,
                severity='warning',
            ))
        elif comment.startswith('hack'):
            findings.append(CodeFinding(
                file=str(path.relative_to(root)),
                line=i,
                kind='hack',
                text=stripped,
                severity='warning',
            ))


def scan_codebase(root: Path, extensions: tuple[str, ...] = ('.py',)) -> tuple[list[FileMetrics], list[CodeFinding]]:
    """Scan the codebase for metrics and findings."""
    metrics: list[FileMetrics] = []
    findings: list[CodeFinding] = []
    SKIP_DIRS = {'__pycache__', '.venv', 'node_modules'}

    for ext in extensions:
        for path in root.rglob(f'*{ext}'):
            if any(skip in path.parts for skip in SKIP_DIRS):
                continue
            file_metrics = _scan_python_file(path)
            metrics.append(file_metrics)

            try:
                source = path.read_text(encoding='utf-8', errors='replace')
            except Exception:
                continue

            _extract_findings(path, root, source, findings)

    return metrics, findings
