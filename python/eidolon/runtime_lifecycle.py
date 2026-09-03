from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from eidolon.core.capabilities import get_capability_registry
from eidolon.core.config import QUIC_PORT
from eidolon.mesh.transport.quic_server import EidolonQuicServer


def register_healing_checks(runtime_app) -> None:
    def runtime_check() -> dict[str, Any]:
        return {'ok': True, 'status': 'available', 'uptime_s': int(time.time() - runtime_app.server_start)}

    def backup_check() -> dict[str, Any]:
        stats = runtime_app._ns('backup_service', runtime_app.services.backup_service).get_stats()
        return {'ok': True, 'status': 'available', 'count': stats.get('count', 0), 'hidden_count': stats.get('hidden_count', 0)}

    def capability_check() -> dict[str, Any]:
        caps = get_capability_registry().list()
        available = sum(1 for cap in caps if cap.get('available'))
        return {'ok': available > 0, 'status': 'available' if available > 0 else 'degraded', 'available': available, 'total': len(caps)}

    def certificate_check() -> dict[str, Any]:
        certs = runtime_app.certificate_health()
        ok = bool(certs.get('ca_exists') and certs.get('cert_exists') and certs.get('key_exists') and certs.get('chain_valid') is not False and certs.get('days_left', 0) > 0)
        return {'ok': ok, 'status': 'available' if ok else 'degraded', **certs}

    for name, check in {'runtime': runtime_check, 'backups': backup_check, 'capabilities': capability_check, 'certificates': certificate_check}.items():
        runtime_app._ns('healing_service', runtime_app.services.healing_service).register_check(name, check)


async def start_runtime(runtime_app) -> None:
    register_healing_checks(runtime_app)
    backup_service = runtime_app._ns('backup_service', runtime_app.services.backup_service)
    if backup_service.get_stats().get('count', 0) < 1:
        try:
            backup_service.create_backup(runtime_app.project_root, reason='initial_runtime', created_by='runtime')
            print('Initiales Runtime-Backup erstellt')
        except Exception as exc:
            print(f'Initiales Runtime-Backup fehlgeschlagen: {exc}')
    await runtime_app._ns('healing_service', runtime_app.services.healing_service).start()
    try:
        runtime_app.quic_server_state['server'] = EidolonQuicServer(host='0.0.0.0', port=QUIC_PORT)
        await runtime_app.quic_server_state['server'].start()
        print(f'QUIC-Server gestartet auf Port {QUIC_PORT}')
    except Exception as exc:
        print(f'QUIC-Server konnte nicht gestartet werden: {exc}')


async def stop_runtime(runtime_app) -> None:
    if runtime_app.quic_server_state['server']:
        await runtime_app.quic_server_state['server'].stop()
        runtime_app.quic_server_state['server'] = None
    await runtime_app._ns('healing_service', runtime_app.services.healing_service).stop()


def build_lifespan(runtime_app):
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        await start_runtime(runtime_app)
        try:
            yield
        finally:
            await stop_runtime(runtime_app)
    return lifespan


def quic_runtime_status(runtime_app) -> dict[str, Any]:
    server = runtime_app.quic_server_state.get('server')
    listening = bool(server is not None and getattr(server, '_running', False))
    return {
        'available': listening,
        'listening': listening,
        'port': QUIC_PORT,
        'status': 'listening' if listening else 'not_wired',
        'detail': 'QUIC-Server läuft' if listening else 'Der Python-Server veröffentlicht derzeit keinen echten QUIC-Listener.',
    }
