from __future__ import annotations

from typing import Any

from .models import ReflectionReport


# Generic phrases that indicate fake self-reflection
GENERIC_PHRASES = [
    "ich würde mich fragen",
    "ich würde mich analysieren",
    "ich würde identifizieren",
    "ich würde meine fähigkeiten verbessern",
    "ich würde besser kommunizieren",
    "ich würde optionen vorstellen",
    "das ist eine interessante frage",
    "ich denke, ich verstehe",
]


def _is_generic_response(text: str) -> bool:
    """Check if a response contains only generic self-reflection phrases."""
    text_lower = text.lower()
    generic_count = sum(1 for phrase in GENERIC_PHRASES if phrase in text_lower)
    # If more than 2 generic phrases found, it's likely fake
    return generic_count >= 2


def _summarize_report(report: ReflectionReport) -> dict[str, Any]:
    """Summarize the technical report for LLM context."""
    summary = report.summary
    
    # Group improvements by priority
    by_priority = {}
    for imp in report.improvements:
        priority = imp.get('priority', 'low')
        by_priority.setdefault(priority, []).append(imp)
    
    # Group improvements by category
    by_category = {}
    for imp in report.improvements:
        category = imp.get('category', 'other')
        by_category.setdefault(category, []).append(imp)
    
    # Find top issues
    critical = by_priority.get('critical', [])
    high = by_priority.get('high', [])
    
    # Find most complex files
    complex_files = sorted(
        report.file_metrics,
        key=lambda m: m.complexity_score,
        reverse=True,
    )[:5]
    
    # Find largest files
    large_files = sorted(
        report.file_metrics,
        key=lambda m: m.loc,
        reverse=True,
    )[:5]
    
    return {
        'total_files': summary.get('total_files', 0),
        'total_loc': summary.get('total_loc', 0),
        'total_improvements': summary.get('total_improvements', 0),
        'critical_count': len(critical),
        'high_count': len(high),
        'critical_improvements': critical,
        'high_improvements': high,
        'improvements_by_category': by_category,
        'top_complex_files': [
            {'path': f.path, 'complexity': f.complexity_score, 'loc': f.loc}
            for f in complex_files
        ],
        'top_large_files': [
            {'path': f.path, 'loc': f.loc}
            for f in large_files
        ],
        'runtime_issues': report.runtime_issues,
        'stale_docs': len([d for d in report.doc_freshness if d.is_stale]),
    }


def _build_reflection_prompt(summary: dict[str, Any], user_question: str) -> str:
    """Build a prompt that forces data-driven self-reflection."""
    
    # Build improvements text
    improvements_text = []
    
    if summary['critical_improvements']:
        improvements_text.append("KRITISCHE PROBLEME:")
        for imp in summary['critical_improvements']:
            improvements_text.append(f"  - [{imp['category']}] {imp['target']}: {imp['issue']}")
            improvements_text.append(f"    Vorschlag: {imp['suggestion']}")
    
    if summary['high_improvements']:
        improvements_text.append("WICHTIGE VERBESSERUNGEN:")
        for imp in summary['high_improvements']:
            improvements_text.append(f"  - [{imp['category']}] {imp['target']}: {imp['issue']}")
            improvements_text.append(f"    Vorschlag: {imp['suggestion']}")
    
    if not improvements_text:
        improvements_text.append("Keine kritischen oder wichtigen Probleme gefunden.")
    
    # Build runtime issues text
    runtime_text = []
    for issue in summary.get('runtime_issues', []):
        runtime_text.append(f"  - [{issue['severity']}] {issue['description']}")
    
    # Build complex files text
    complex_text = []
    for f in summary.get('top_complex_files', []):
        complex_text.append(f"  - {f['path']}: complexity={f['complexity']}, LOC={f['loc']}")
    
    # Build large files text
    large_text = []
    for f in summary.get('top_large_files', []):
        large_text.append(f"  - {f['path']}: LOC={f['loc']}")
    
    prompt = f"""Du bist Eidolon und sollst eine echte Selbstreflexion durchführen. Nutze NUR die folgenden konkreten Daten.

NUTZERFRAGE: {user_question}

AKTUELLER SYSTEM-STATUS:
- Dateien: {summary['total_files']}
- Gesamt-LOC: {summary['total_loc']}
- Veraltete Docs: {summary['stale_docs']}

{chr(10).join(improvements_text)}

RUNTIME-PROBLEME:
{chr(10).join(runtime_text) if runtime_text else '  Keine.'}

KOMPLEXESTE DATEIEN:
{chr(10).join(complex_text) if complex_text else '  Keine.'}

GRÖSSTE DATEIEN:
{chr(10).join(large_text) if large_text else '  Keine.'}

REGELN:
1. Antworte NUR mit konkreten, datengestützten Aussagen
2. Vermeide generische Floskeln wie "ich würde mich fragen" oder "ich würde meine Fähigkeiten verbessern"
3. Nenne spezifische Dateien, Metriken und Vorschläge
4. Priorisiere nach kritischem > wichtig > mittel > niedrig
5. Sei ehrlich über Lücken und Schwächen

Antworte jetzt mit einer echten Selbstreflexion basierend auf diesen Daten:"""
    
    return prompt


class SemanticReflector:
    """Translates technical self-reflection reports into natural language."""
    
    def reflect(self, report: ReflectionReport, user_question: str = "") -> str:
        """Generate a data-driven self-reflection response."""
        summary = _summarize_report(report)
        return _build_reflection_prompt(summary, user_question)
    
    def generate_report_text(self, report: ReflectionReport) -> str:
        """Generate a human-readable report from technical data."""
        summary = _summarize_report(report)
        
        lines = [
            "=== EIDOLON SELBSTREFLEXION ===",
            f"Generiert: {report.generated_at}",
            "",
            f"Codebase: {summary['total_files']} Dateien, {summary['total_loc']} LOC",
            f"Veraltete Dokumente: {summary['stale_docs']}",
            "",
        ]
        
        if summary['critical_improvements']:
            lines.append("KRITISCHE PROBLEME:")
            for imp in summary['critical_improvements']:
                lines.append(f"  ⚠️  [{imp['category']}] {imp['target']}")
                lines.append(f"      {imp['issue']}")
                lines.append(f"      → {imp['suggestion']}")
            lines.append("")
        
        if summary['high_improvements']:
            lines.append("WICHTIGE VERBESSERUNGEN:")
            for imp in summary['high_improvements']:
                lines.append(f"  🔶 [{imp['category']}] {imp['target']}")
                lines.append(f"      {imp['issue']}")
                lines.append(f"      → {imp['suggestion']}")
            lines.append("")
        
        if summary.get('runtime_issues'):
            lines.append("RUNTIME-PROBLEME:")
            for issue in summary['runtime_issues']:
                lines.append(f"  🔴 [{issue['severity']}] {issue['description']}")
            lines.append("")
        
        if summary.get('top_complex_files'):
            lines.append("KOMPLEXESTE DATEIEN:")
            for f in summary['top_complex_files']:
                lines.append(f"  📊 {f['path']}: complexity={f['complexity']}, LOC={f['loc']}")
            lines.append("")
        
        return "\n".join(lines)
