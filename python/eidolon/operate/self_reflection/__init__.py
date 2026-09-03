from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import ReflectionReport
from .code_scanner import scan_codebase
from .runtime_checker import check_doc_freshness, check_runtime_issues


def _generate_improvements(
    file_metrics: list,
    findings: list,
    doc_freshness: list,
    runtime_issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Generate prioritized improvement suggestions."""
    improvements: list[dict[str, Any]] = []

    # Critical: Large files
    large_files = [m for m in file_metrics if m.loc > 500]
    for m in large_files:
        improvements.append({
            'priority': 'high',
            'category': 'maintainability',
            'target': m.path,
            'issue': f'File has {m.loc} LOC (threshold: 500)',
            'suggestion': 'Split into smaller modules along domain boundaries',
            'effort': 'medium',
        })

    # Critical: High complexity files
    complex_files = [m for m in file_metrics if m.complexity_score > 20]
    for m in complex_files:
        improvements.append({
            'priority': 'high',
            'category': 'maintainability',
            'target': m.path,
            'issue': f'File has complexity score {m.complexity_score} (threshold: 20)',
            'suggestion': 'Extract helper functions, reduce nesting',
            'effort': 'medium',
        })

    # Warning: FIXMEs
    fixmes = [f for f in findings if f.kind == 'fixme']
    for f in fixmes:
        improvements.append({
            'priority': 'medium',
            'category': 'code_quality',
            'target': f.file,
            'issue': f'FIXME at line {f.line}: {f.text}',
            'suggestion': 'Resolve or create tracking issue',
            'effort': 'low',
        })

    # Warning: Stale docs
    stale_docs = [d for d in doc_freshness if d.is_stale]
    for d in stale_docs:
        improvements.append({
            'priority': 'medium',
            'category': 'documentation',
            'target': d.path,
            'issue': f'Document has not been updated in > 30 days',
            'suggestion': 'Review and update to reflect current code state',
            'effort': 'low',
        })

    # Critical: Runtime issues
    for issue in runtime_issues:
        if issue['severity'] == 'critical':
            improvements.append({
                'priority': 'critical',
                'category': 'runtime',
                'target': 'operate.db',
                'issue': issue['description'],
                'suggestion': 'Investigate and resolve immediately',
                'effort': 'high',
            })
        elif issue['severity'] == 'warning':
            improvements.append({
                'priority': 'medium',
                'category': 'runtime',
                'target': 'operate.db',
                'issue': issue['description'],
                'suggestion': 'Review and clean up',
                'effort': 'low',
            })

    # Info: TODOs
    todos = [f for f in findings if f.kind == 'todo']
    if len(todos) > 10:
        improvements.append({
            'priority': 'low',
            'category': 'code_quality',
            'target': 'codebase',
            'issue': f'{len(todos)} TODO comments found',
            'suggestion': 'Review and triage: resolve, create issues, or remove',
            'effort': 'low',
        })

    # Sort by priority
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    improvements.sort(key=lambda x: priority_order.get(x['priority'], 99))

    return improvements


def generate_self_reflection_report(
    project_root: Path,
    docs_root: Path,
    db_path: Path | None = None,
) -> ReflectionReport:
    """Generate a comprehensive self-reflection report."""
    report = ReflectionReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    # Scan code
    report.file_metrics, report.code_findings = scan_codebase(project_root)

    # Check docs
    report.doc_freshness = check_doc_freshness(docs_root)

    # Check runtime
    if db_path:
        report.runtime_issues = check_runtime_issues(db_path)

    # Generate improvements
    report.improvements = _generate_improvements(
        report.file_metrics,
        report.code_findings,
        report.doc_freshness,
        report.runtime_issues,
    )

    # Summary
    total_loc = sum(m.loc for m in report.file_metrics)
    total_files = len(report.file_metrics)
    total_findings = len(report.code_findings)
    stale_docs = len([d for d in report.doc_freshness if d.is_stale])
    critical_improvements = len([i for i in report.improvements if i['priority'] == 'critical'])
    high_improvements = len([i for i in report.improvements if i['priority'] == 'high'])

    report.summary = {
        'total_files': total_files,
        'total_loc': total_loc,
        'total_findings': total_findings,
        'stale_docs': stale_docs,
        'critical_improvements': critical_improvements,
        'high_improvements': high_improvements,
        'total_improvements': len(report.improvements),
    }

    return report


def report_to_dict(report: ReflectionReport) -> dict[str, Any]:
    """Convert report to JSON-serializable dict."""
    return {
        'generated_at': report.generated_at,
        'summary': report.summary,
        'improvements': report.improvements,
        'runtime_issues': report.runtime_issues,
        'code_findings': [
            {
                'file': f.file,
                'line': f.line,
                'kind': f.kind,
                'text': f.text,
                'severity': f.severity,
            }
            for f in report.code_findings
        ],
        'file_metrics': [
            {
                'path': m.path,
                'loc': m.loc,
                'functions': m.functions,
                'classes': m.classes,
                'complexity_score': m.complexity_score,
                'todos': m.todos,
                'fixmes': m.fixmes,
            }
            for m in report.file_metrics
            if m.loc > 0
        ],
        'doc_freshness': [
            {
                'path': d.path,
                'last_modified': datetime.fromtimestamp(d.last_modified).isoformat(),
                'size_bytes': d.size_bytes,
                'is_stale': d.is_stale,
            }
            for d in report.doc_freshness
        ],
    }
