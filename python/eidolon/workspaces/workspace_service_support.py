from __future__ import annotations

from eidolon.workspaces.domain_models import DOMAIN_MODULES, VALID_TRANSITIONS


def list_domains(domains: list[str]) -> list[dict]:
    return [{'id': d, 'label': d.capitalize(), 'modules': DOMAIN_MODULES.get(d, []), 'start_status': 'backlog' if d == 'project' else 'draft' if d == 'knowledge' else 'todo'} for d in domains]


def domain_statuses(domain: str) -> dict[str, list[str]]:
    return VALID_TRANSITIONS.get(domain, {})


def allowed_transitions(engine, task_id: str) -> list[str]:
    task = engine._tasks.get(task_id)
    if not task:
        return []
    return VALID_TRANSITIONS.get(task.domain, {}).get(task.status, [])


def overview(engine, domains: list[str], list_domains_fn) -> dict:
    all_tasks = engine.list_tasks()
    by_domain: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for t in all_tasks:
        by_domain[t['domain']] = by_domain.get(t['domain'], 0) + 1
        by_status[t['status']] = by_status.get(t['status'], 0) + 1
    return {'total': len(all_tasks), 'by_domain': by_domain, 'by_status': by_status, 'domains': list_domains_fn(domains)}
