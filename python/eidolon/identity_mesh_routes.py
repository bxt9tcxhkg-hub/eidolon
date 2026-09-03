from __future__ import annotations

from typing import Any, Callable

from fastapi import FastAPI, HTTPException


def register_identity_mesh_routes(
    app: FastAPI,
    *,
    get_llm_backend: Callable[[], Any],
    get_bot_role_registry: Callable[[], Any],
    get_mesh_service: Callable[[], Any],
    get_http_port: Callable[[], int],
) -> None:
    def llm_backend():
        return get_llm_backend()
    def bot_role_registry():
        return get_bot_role_registry()
    def mesh_service():
        return get_mesh_service()

    @app.get('/identity')
    async def identity():
        llm_status = llm_backend().status()
        core_role = bot_role_registry().get_role('eidolon-core') or {}
        role_summary = bot_role_registry().summary()
        roles = bot_role_registry().list_roles()
        active_roles = [{
            'role_id': role.get('role_id'),
            'name': role.get('name'),
            'visibility': role.get('visibility'),
            'requires_user_approval': role.get('requires_user_approval'),
            'description_for_user': role.get('description_for_user', ''),
        } for role in roles if role.get('status') == 'active']
        defined_roles = [{
            'role_id': role.get('role_id'),
            'name': role.get('name'),
            'role_kind': role.get('role_kind'),
            'instantiation_policy': role.get('instantiation_policy'),
            'requires_user_approval': role.get('requires_user_approval'),
            'description_for_user': role.get('description_for_user', ''),
        } for role in roles if role.get('status') == 'defined']
        return {
            'name': 'Eidolon',
            'product_role': 'Zentrales agentisches Hauptsystem',
            'identity': 'Eidolon — zentrales agentisches Hauptsystem für Gespräch, Projektbildung, adaptive Arbeitsflächen und autonome Ausführung mit klaren Leitplanken.',
            'model': llm_status.get('model', '-'),
            'provider': llm_status.get('provider', '-'),
            'ollama_url': llm_status.get('ollama_url', '-'),
            'direct_counterpart_role': core_role.get('description_for_user', ''),
            'role_count': role_summary.get('total', 0),
            'active_role_count': role_summary.get('active', 0),
            'defined_role_count': role_summary.get('defined', 0),
            'role_kinds': role_summary.get('role_kinds', []),
            'active_roles': active_roles,
            'defined_roles': defined_roles,
        }

    @app.get('/bots/roles')
    async def bot_roles_list():
        return {'roles': bot_role_registry().list_roles(), 'summary': bot_role_registry().summary()}

    @app.get('/bots/roles/{role_id}')
    async def bot_roles_get(role_id: str):
        role = bot_role_registry().get_role(role_id)
        if not role:
            raise HTTPException(status_code=404, detail='Nicht gefunden')
        return {'role': role}

    @app.post('/bots/roles')
    async def bot_roles_create(request: dict):
        try:
            return {'ok': True, 'role': bot_role_registry().create_role(request)}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.put('/bots/roles/{role_id}')
    async def bot_roles_update(role_id: str, request: dict):
        try:
            return {'ok': True, 'role': bot_role_registry().update_role(role_id, request)}
        except KeyError:
            raise HTTPException(status_code=404, detail='Nicht gefunden')
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.delete('/bots/roles/{role_id}')
    async def bot_roles_delete(role_id: str):
        try:
            return {'ok': True, 'role': bot_role_registry().delete_role(role_id)}
        except KeyError:
            raise HTTPException(status_code=404, detail='Nicht gefunden')
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.get('/mesh/peers')
    async def mesh_peers():
        peers = mesh_service().scan_peers()
        return {'peers': [p.to_dict() for p in peers]}

    @app.post('/mesh/scan')
    async def mesh_scan():
        peers = mesh_service().scan_peers()
        return {'ok': True, 'peers': [p.to_dict() for p in peers], 'self': {'peer_id': mesh_service().peer_id, 'name': mesh_service().name, 'address': mesh_service().get_local_ip(), 'port': get_http_port()}}
