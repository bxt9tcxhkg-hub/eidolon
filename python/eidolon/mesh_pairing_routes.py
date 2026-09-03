from __future__ import annotations

from typing import Any, Callable

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from eidolon.mesh_pairing_support import pairing_self_payload, pairing_status_payload, render_pairing_page


def register_mesh_pairing_routes(
    app: FastAPI,
    *,
    get_mesh_service: Callable[[], Any],
    get_http_port: Callable[[], int],
) -> None:
    def mesh_service():
        return get_mesh_service()

    def http_port() -> int:
        return get_http_port()

    @app.get('/pairing', response_class=HTMLResponse)
    async def pairing_page(code: str = '', name: str = ''):
        if not code:
            return HTMLResponse(content='<h1>Fehler: Kein Code</h1>', status_code=400)
        return HTMLResponse(content=render_pairing_page(code, name))

    @app.post('/mesh/pairing/create')
    async def mesh_create_pairing(request: dict | None = None):
        request = request or {}
        service = mesh_service()
        result = service.create_pairing(
            target_name=request.get('target_name', ''),
            target_address=request.get('target_address', ''),
            target_port=request.get('target_port', 0),
        )
        return {
            'ok': True,
            'code': result['code'],
            'qr_payload': result['qr_payload'],
            'qr_svg': service.generate_qr_svg(result['qr_payload']),
            'qr_png': service.generate_qr_png_data_url(result['qr_payload']),
            'qr_info': service.qr_debug_info(result['qr_payload']),
            'expires_in': result['expires_in'],
            'self': pairing_self_payload(service, http_port()),
        }

    @app.post('/mesh/pairing/accept')
    async def mesh_accept_pairing(request: Request, payload: dict):
        code = payload.get('code', '')
        if not code:
            return {'ok': False, 'error': 'Kein Code übergeben'}
        service = mesh_service()
        if payload.get('device_peer_id') or payload.get('device_public_key'):
            client_host = request.client.host if request.client else ''
            return service.accept_browser_device_pairing(
                code,
                device_name=payload.get('device_name') or 'Handy-Browser',
                peer_id=payload.get('device_peer_id') or '',
                public_key=payload.get('device_public_key') or '',
                address=client_host,
                user_agent=request.headers.get('user-agent', ''),
            )
        return service.accept_pairing(code)

    @app.post('/mesh/pairing/reject')
    async def mesh_reject_pairing(request: dict):
        code = request.get('code', '')
        if not code:
            return {'ok': False, 'error': 'Kein Code übergeben'}
        return {'ok': mesh_service()._pairing.reject_pairing(code)}

    @app.get('/mesh/pairing/pending')
    async def mesh_pending_pairings():
        return {'ok': True, 'pending': mesh_service().get_pending_requests()}

    @app.get('/mesh/pairing/paired')
    async def mesh_paired_peers():
        return {'ok': True, 'paired': mesh_service().get_paired_peers()}

    @app.delete("/mesh/pairing/paired/{peer_id}")
    async def mesh_unpair_peer(peer_id: str):
        return mesh_service().unpair_peer(peer_id)

    @app.get('/mesh/status')
    async def mesh_status():
        return pairing_status_payload(mesh_service(), http_port())
