from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from eidolon.core.config import GRAPH_DB
from eidolon.core.evidence import get_evidence_store
from eidolon.core.runtime_problems import health_visible_problems


def knowledge_graph_health_payload() -> dict[str, Any]:
    path = Path(GRAPH_DB)
    if not path.exists():
        return {
            'available': False,
            'stats': None,
            'detail': 'Kein persistierter Knowledge Graph (Datei fehlt). Health erfindet keine Entitätenzahl.',
        }
    try:
        with sqlite3.connect(str(path)) as conn:
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
            if 'entities' not in tables:
                return {
                    'available': False,
                    'stats': None,
                    'detail': 'Graph-Datei existiert, hat aber kein Entity-Schema.',
                }
            entities = int(conn.execute('SELECT COUNT(*) FROM entities').fetchone()[0])
            intents = int(conn.execute('SELECT COUNT(*) FROM intents').fetchone()[0]) if 'intents' in tables else 0
        return {
            'available': True,
            'stats': {'entities': entities, 'intents': intents},
            'detail': 'Zählung aus persistiertem Graph-Store.',
        }
    except Exception as exc:
        return {
            'available': False,
            'stats': None,
            'detail': f'Knowledge Graph nicht lesbar: {exc}',
        }


def evidence_health_payload() -> dict[str, Any]:
    try:
        store = get_evidence_store()
        verified = len(store.get_verifications(status='verified'))
        blocked = len(store.get_blocked())
        return {
            'available': True,
            'verified': verified,
            'blocked': blocked,
            'detail': 'Zählung aus dem SQLite Evidence Store.',
        }
    except Exception as exc:
        return {
            'available': False,
            'verified': None,
            'blocked': None,
            'detail': f'Evidence Store nicht lesbar: {exc}',
        }


def mesh_metrics_payload(get_mesh_service: Callable[[], Any] | None, uptime_s: int) -> dict[str, Any]:
    if get_mesh_service is None:
        return {
            'available': False,
            'peer_count': None,
            'paired_count': None,
            'avg_latency': None,
            'msg_rate_per_sec': None,
            'total_messages': None,
            'uptime_seconds': uptime_s,
            'metrics_complete': False,
            'detail': 'Mesh-Service ist an /health nicht angebunden. Latenz wird nicht gemessen.',
        }
    try:
        service = get_mesh_service()
        peers = service.scan_peers()
        paired = service.get_paired_peers()
        return {
            'available': True,
            'peer_count': len(peers),
            'paired_count': len(paired),
            'avg_latency': None,
            'msg_rate_per_sec': None,
            'total_messages': None,
            'uptime_seconds': uptime_s,
            'metrics_complete': False,
            'detail': 'Peer-Zahlen aus dem Mesh-Store. Latenz und Nachrichtenrate werden nicht gemessen.',
        }
    except Exception as exc:
        return {
            'available': False,
            'peer_count': None,
            'paired_count': None,
            'avg_latency': None,
            'msg_rate_per_sec': None,
            'total_messages': None,
            'uptime_seconds': uptime_s,
            'metrics_complete': False,
            'detail': f'Mesh-Store nicht lesbar: {exc}',
        }


def skills_health_payload(builtin_skills: list[dict]) -> dict[str, Any]:
    from eidolon.skills.live_skills import LIVE_SKILL_IDS

    listed_live = [skill['name'] for skill in builtin_skills if skill.get('name') in LIVE_SKILL_IDS]
    live = listed_live or sorted(LIVE_SKILL_IDS)
    return {
        'available': bool(live),
        'catalog_only': not bool(live),
        'count': len(builtin_skills),
        'enabled': sum(1 for skill in builtin_skills if skill.get('enabled')),
        'executable_count': len(live),
        'live_skills': live,
        'skill_ids': [skill['name'] for skill in builtin_skills if skill.get('name')],
        'detail': (
            f'Chat kann {len(live)} Skills ausführen ({", ".join(live)}). '
            'Übrige Einträge sind Katalog, nicht verdrahtet.'
        ),
    }


def health_payload(
    *,
    server_start: float,
    goal_stats: dict,
    backup_stats: dict,
    healing_state: dict,
    quic_status: dict,
    caps: list[dict],
    certs: dict,
    builtin_skills: list[dict],
    human_duration,
    http_port: int,
    quic_port: int,
    get_mesh_service: Callable[[], Any] | None = None,
) -> dict:
    uptime_s = int(__import__('time').time() - server_start)
    problems = health_visible_problems(certs=certs, backup_stats=backup_stats)
    unavailable = [cap['id'] for cap in caps if not cap['available']]
    status = 'degraded' if problems else 'ok_with_limits' if unavailable else 'ok'
    knowledge_graph = knowledge_graph_health_payload()
    evidence = evidence_health_payload()
    mesh_metrics = mesh_metrics_payload(get_mesh_service, uptime_s)
    skills = skills_health_payload(builtin_skills)
    return {
        'status': status,
        'problems': problems,
        'components': {
            'knowledge_graph': knowledge_graph,
            'skills': skills,
            'certificates': certs,
            'quic_port': quic_status,
            'self_healing': {
                'available': bool(healing_state.get('running')),
                'status': 'running' if healing_state.get('running') else 'stopped',
                'events': healing_state.get('total_checks', 0),
                'checks_registered': healing_state.get('checks_registered', []),
                'detail': 'SelfHealingService ist gestartet und führt registrierte Health-Checks aus.' if healing_state.get('running') else 'SelfHealingService ist verdrahtet, läuft aber aktuell nicht.',
            },
            'mesh_metrics': mesh_metrics,
            'capabilities': {
                'capabilities': caps,
                'count': len(caps),
                'total': len(caps),
                'available': sum(1 for cap in caps if cap['available']),
                'unavailable_ids': unavailable,
            },
            'evidence': evidence,
            'goals': {
                'total': goal_stats.get('total', 0),
                'active': goal_stats.get('active_count', 0),
                'done': goal_stats.get('done_count', 0),
                'overall_progress': goal_stats.get('overall_progress', 0.0),
                'by_status': goal_stats.get('by_status', {}),
            },
            'backups': {
                'count': backup_stats.get('count', 0),
                'max': backup_stats.get('max_backups', 0),
                'total_size_mb': backup_stats.get('total_size_mb', 0),
            },
        },
        'server_port': http_port,
        'quic_port': quic_port,
        'uptime_seconds': uptime_s,
        'uptime_human': human_duration(uptime_s),
        'checked_at': datetime.now(timezone.utc).isoformat(),
    }
