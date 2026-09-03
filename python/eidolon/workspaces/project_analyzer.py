"""Analysiert das Eidolon-Projekt und extrahier die Struktur für den Arbeitsbereich.

Liest die ROADMAP.md, die Dateistruktur und den Git-Status, um eine
vollständige Projektstruktur für die vier Ansichten zu erzeugen.
"""
from __future__ import annotations

from pathlib import Path

from eidolon.workspaces.project_analyzer_modules import scan_modules
from eidolon.workspaces.project_analyzer_roadmap import parse_roadmap
from eidolon.workspaces.project_analyzer_stats import git_status, project_stats


class ProjectAnalyzer:
    """Extrahiert die Projektstruktur aus dem Eidolon-Projekt."""

    def __init__(self, project_root: Path):
        self._root = Path(project_root)

    def analyze(self) -> dict:
        return {'title': 'Eidolon — Zentrales agentisches Hauptsystem', 'description': 'Zentrales agentisches Hauptsystem für Gespräch, Projektbildung, adaptive Arbeitsflächen und autonome Ausführung mit klaren Leitplanken.', 'domain': 'development', 'roadmap_items': parse_roadmap(self._root), 'modules': scan_modules(self._root), 'git_status': git_status(self._root), 'stats': project_stats(self._root)}


_analyzer: ProjectAnalyzer | None = None


def get_project_analyzer(project_root: Path) -> ProjectAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = ProjectAnalyzer(project_root)
    return _analyzer
