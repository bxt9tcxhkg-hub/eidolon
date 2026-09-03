from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CodeFinding:
    file: str
    line: int
    kind: str  # 'todo', 'fixme', 'hack', 'complexity', 'noqa'
    text: str
    severity: str = 'info'  # 'info', 'warning', 'critical'


@dataclass
class FileMetrics:
    path: str
    loc: int = 0
    functions: int = 0
    classes: int = 0
    imports: int = 0
    todos: int = 0
    fixmes: int = 0
    complexity_score: int = 0


@dataclass
class DocFreshness:
    path: str
    last_modified: float
    size_bytes: int
    is_stale: bool = False


@dataclass
class ReflectionReport:
    generated_at: str
    code_findings: list[CodeFinding] = field(default_factory=list)
    file_metrics: list[FileMetrics] = field(default_factory=list)
    doc_freshness: list[DocFreshness] = field(default_factory=list)
    runtime_issues: list[dict[str, Any]] = field(default_factory=list)
    improvements: list[dict[str, Any]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
