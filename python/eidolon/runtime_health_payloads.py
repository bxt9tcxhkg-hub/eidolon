from __future__ import annotations

from datetime import datetime, timezone

from eidolon.core.runtime_problems import health_visible_problems


def health_payload(*, server_start: float, goal_stats: dict, backup_stats: dict, healing_state: dict, quic_status: dict, caps: list[dict], certs: dict, builtin_skills: list[dict], human_duration, http_port: int, quic_port: int) -> dict:
    uptime_s = int(__import__('time').time() - server_start)
    problems = health_visible_problems(certs=certs, backup_stats=backup_stats)
    unavailable = [cap['id'] for cap in caps if not cap['available']]
    status = 'degraded' if problems else 'ok_with_limits' if unavailable else 'ok'
    return {'status': status, 'problems': problems, 'components': {'knowledge_graph': {'available': True, 'stats': {'entities': 0, 'intents': 0}}, 'skills': {'available': True, 'count': len(builtin_skills), 'enabled': sum(1 for skill in builtin_skills if skill.get('enabled')), 'skill_ids': [skill['name'] for skill in builtin_skills]}, 'certificates': certs, 'quic_port': quic_status, 'self_healing': {'available': bool(healing_state.get('running')), 'status': 'running' if healing_state.get('running') else 'stopped', 'events': healing_state.get('total_checks', 0), 'checks_registered': healing_state.get('checks_registered', []), 'detail': 'SelfHealingService ist gestartet und führt registrierte Health-Checks aus.' if healing_state.get('running') else 'SelfHealingService ist verdrahtet, läuft aber aktuell nicht.'}, 'mesh_metrics': {'avg_latency': 0, 'peer_count': 0, 'msg_rate_per_sec': 0.0, 'total_messages': 0, 'uptime_seconds': uptime_s}, 'capabilities': {'capabilities': caps, 'count': len(caps), 'total': len(caps), 'available': sum(1 for cap in caps if cap['available']), 'unavailable_ids': unavailable}, 'evidence': {'verified': 0, 'blocked': 0, 'available': True}, 'goals': {'total': goal_stats.get('total', 0), 'active': goal_stats.get('active_count', 0), 'done': goal_stats.get('done_count', 0), 'overall_progress': goal_stats.get('overall_progress', 0.0), 'by_status': goal_stats.get('by_status', {})}, 'backups': {'count': backup_stats.get('count', 0), 'max': backup_stats.get('max_backups', 0), 'total_size_mb': backup_stats.get('total_size_mb', 0)}}, 'server_port': http_port, 'quic_port': quic_port, 'uptime_seconds': uptime_s, 'uptime_human': human_duration(uptime_s), 'checked_at': datetime.now(timezone.utc).isoformat()}
