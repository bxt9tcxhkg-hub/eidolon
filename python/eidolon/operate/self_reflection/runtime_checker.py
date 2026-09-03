from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any

from .models import DocFreshness


def check_doc_freshness(docs_root: Path, threshold_days: int = 30) -> list[DocFreshness]:
    """Check documentation freshness."""
    results: list[DocFreshness] = []
    now = time.time()
    threshold_seconds = threshold_days * 86400

    for path in docs_root.rglob('*.md'):
        try:
            stat = path.stat()
            age = now - stat.st_mtime
            results.append(DocFreshness(
                path=str(path.relative_to(docs_root)),
                last_modified=stat.st_mtime,
                size_bytes=stat.st_size,
                is_stale=age > threshold_seconds,
            ))
        except Exception:
            continue

    return results


def check_runtime_issues(db_path: Path) -> list[dict[str, Any]]:
    """Check for runtime issues in the Operate DB."""
    issues: list[dict[str, Any]] = []

    if not db_path.exists():
        return issues

    try:
        with sqlite3.connect(db_path) as conn:
            _check_orphaned_subagents(conn, issues)
            _check_stale_approvals(conn, issues)
            _check_open_blockers(conn, issues)
            _check_stuck_runs(conn, issues)
    except Exception as e:
        issues.append({
            'kind': 'db_error',
            'count': 0,
            'severity': 'warning',
            'description': f'Could not analyze runtime DB: {e}',
        })

    return issues


def _check_orphaned_subagents(conn, issues: list[dict[str, Any]]) -> None:
    orphaned = conn.execute(
        'SELECT COUNT(*) FROM subagent_runs WHERE parent_run_id NOT IN (SELECT id FROM agent_runs)'
    ).fetchone()[0]
    if orphaned > 0:
        issues.append({
            'kind': 'orphaned_subagents',
            'count': orphaned,
            'severity': 'warning',
            'description': f'{orphaned} subagent_runs have no parent agent_run',
        })


def _check_stale_approvals(conn, issues: list[dict[str, Any]]) -> None:
    stale_approvals = conn.execute(
        "SELECT COUNT(*) FROM approval_gates WHERE status = 'pending'"
    ).fetchone()[0]
    if stale_approvals > 0:
        issues.append({
            'kind': 'stale_pending_approvals',
            'count': stale_approvals,
            'severity': 'info',
            'description': f'{stale_approvals} approval_gates are still pending',
        })


def _check_open_blockers(conn, issues: list[dict[str, Any]]) -> None:
    open_blockers = conn.execute(
        "SELECT COUNT(*) FROM blocking_issues WHERE status = 'open'"
    ).fetchone()[0]
    if open_blockers > 0:
        issues.append({
            'kind': 'open_blockers',
            'count': open_blockers,
            'severity': 'warning',
            'description': f'{open_blockers} blocking_issues are still open',
        })


def _check_stuck_runs(conn, issues: list[dict[str, Any]]) -> None:
    stuck_runs = conn.execute(
        "SELECT COUNT(*) FROM agent_runs WHERE state NOT IN ('completed', 'failed', 'cancelled') AND updated_at < datetime('now', '-1 day')"
    ).fetchone()[0]
    if stuck_runs > 0:
        issues.append({
            'kind': 'stuck_runs',
            'count': stuck_runs,
            'severity': 'critical',
            'description': f'{stuck_runs} agent_runs are stuck in non-terminal state for > 24h',
        })
