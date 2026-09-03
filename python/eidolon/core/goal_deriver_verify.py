from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from eidolon.core.config import state_path
from eidolon.core.goal_deriver_keys import KEY_BACKUPS, KEY_CAP_PREFIX, KEY_CERTIFICATES, KEY_ROADMAP_PREFIX, KEY_RUST_STUBS
from eidolon.core.goal_deriver_health import verify_capability, verify_certificates
from eidolon.core.goal_deriver_sources import from_roadmap, from_rust_stubs, verify_roadmap, verify_rust_stubs


def backup_count(project_root: Path) -> int | None:
    catalog = state_path('backups', 'catalog.json', project_root=project_root)
    if not catalog.exists():
        return None
    try:
        return len(json.loads(catalog.read_text(encoding='utf-8')).get('entries', []))
    except Exception:
        return None


def from_backups(project_root: Path) -> list[dict[str, Any]]:
    count = backup_count(project_root)
    if count is None:
        return [{
            'problem_key': KEY_BACKUPS,
            'title': 'Erstes Backup anlegen',
            'description': 'Es existiert kein Backup-Katalog — ein fehlgeschlagener Self-Repair wäre nicht rückholbar.',
            'category': 'maintenance',
            'priority': 5,
            'source': 'data/backups/catalog.json',
            'evidence': 'Katalogdatei fehlt',
            'steps': ['Backup über die UI erstellen', 'Restore einmal testen'],
        }]
    if count < 2:
        return [{
            'problem_key': KEY_BACKUPS,
            'title': 'Backup-Abdeckung erhöhen',
            'description': f'Nur {count} Backup vorhanden. Für sichere Rollbacks sind mehrere Stände nötig.',
            'category': 'maintenance',
            'priority': 3,
            'source': 'data/backups/catalog.json',
            'evidence': f'{count} Einträge im Katalog',
            'steps': ['Weiteres Backup anlegen', 'Restore verifizieren'],
        }]
    return []


def verify_backups(project_root: Path) -> tuple[bool, str]:
    count = backup_count(project_root)
    if count is None:
        return True, 'Katalogdatei fehlt'
    if count < 2:
        return True, f'nur {count} Backup vorhanden'
    return False, f'{count} Backups vorhanden'


def verify_problem(project_root: Path, problem_key: str, health: dict[str, Any]) -> dict[str, Any]:
    try:
        if problem_key == KEY_CERTIFICATES:
            open_, evidence = verify_certificates(health)
        elif problem_key.startswith(KEY_CAP_PREFIX):
            open_, evidence = verify_capability(health, problem_key[len(KEY_CAP_PREFIX):])
        elif problem_key == KEY_RUST_STUBS:
            open_, evidence = verify_rust_stubs(project_root)
        elif problem_key == KEY_BACKUPS:
            open_, evidence = verify_backups(project_root)
        elif problem_key.startswith(KEY_ROADMAP_PREFIX):
            open_, evidence = verify_roadmap(project_root, problem_key[len(KEY_ROADMAP_PREFIX):])
        else:
            return {'still_open': None, 'evidence': 'keine Prüfregel', 'checkable': False}
        return {'still_open': open_, 'evidence': evidence, 'checkable': True}
    except Exception as exc:
        return {'still_open': None, 'evidence': f'Prüffehler: {exc}', 'checkable': False}


def derive_all(project_root: Path, health: dict[str, Any] | None = None, *, from_capabilities_fn, from_certificates_fn) -> dict[str, Any]:
    health = health or {}
    buckets = {
        'capabilities': from_capabilities_fn(health),
        'certificates': from_certificates_fn(health),
        'roadmap': from_roadmap(project_root),
        'rust_stubs': from_rust_stubs(project_root),
        'backups': from_backups(project_root),
    }
    merged: dict[str, dict[str, Any]] = {}
    for items in buckets.values():
        for proposal in items:
            key = proposal['problem_key']
            if key not in merged:
                merged[key] = {**proposal, 'also_reported_by': []}
            else:
                prev = merged[key]
                if proposal['priority'] > prev['priority']:
                    also = prev['also_reported_by'] + [prev['source']]
                    merged[key] = {**proposal, 'also_reported_by': also}
                else:
                    prev['also_reported_by'].append(proposal['source'])
    proposals = sorted(merged.values(), key=lambda item: -item['priority'])
    return {
        'proposals': proposals,
        'by_source': {key: len(value) for key, value in buckets.items()},
        'total': len(proposals),
        'deduplicated': sum(len(value) for value in buckets.values()) - len(proposals),
    }
