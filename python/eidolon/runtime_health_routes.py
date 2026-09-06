from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI

from eidolon.runtime_health_payloads import health_payload
from eidolon.runtime_health_system import system_metrics_payload, system_storage_payload


def register_runtime_health_routes(
    app: FastAPI,
    *,
    get_server_start: Callable[[], float],
    get_autonomy_engine: Callable[[], Any],
    get_backup_service: Callable[[], Any],
    get_healing_service: Callable[[], Any],
    get_capability_registry: Callable[[], Any],
    get_builtin_skills: Callable[[], list[dict[str, Any]]],
    get_certificate_health: Callable[[], dict[str, Any]],
    get_quic_runtime_status: Callable[[], dict[str, Any]],
    human_duration: Callable[[int], str],
    get_http_port: Callable[[], int],
    get_quic_port: Callable[[], int],
    project_root: Path,
    get_mesh_service: Callable[[], Any] | None = None,
) -> Any:
    def server_start() -> float: return get_server_start()

    @app.get('/health')
    async def health():
        goal_stats = get_autonomy_engine().get_stats(); backup_stats = get_backup_service().get_stats(); healing_state = get_healing_service().get_state(); quic_status = get_quic_runtime_status(); certs = get_certificate_health()
        caps = []
        for cap in get_capability_registry().list():
            caps.append({**cap, 'available': quic_status['available'], 'detail': quic_status['detail']} if cap.get('id') == 'mesh.quic' else cap)
        return health_payload(server_start=server_start(), goal_stats=goal_stats, backup_stats=backup_stats, healing_state=healing_state, quic_status=quic_status, caps=caps, certs=certs, builtin_skills=get_builtin_skills(), human_duration=human_duration, http_port=get_http_port(), quic_port=get_quic_port(), get_mesh_service=get_mesh_service)

    @app.get('/capabilities')
    async def capabilities():
        return (await health())['components']['capabilities']

    @app.get('/mesh/quic-status')
    async def mesh_quic_status():
        return {'ok': True, **get_quic_runtime_status()}

    @app.get('/system/metrics')
    async def system_metrics():
        return system_metrics_payload(server_start(), human_duration, get_http_port(), get_quic_port(), project_root)

    @app.get('/system/storage')
    async def system_storage():
        return system_storage_payload(project_root)

    return health
