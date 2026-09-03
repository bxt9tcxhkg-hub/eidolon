from __future__ import annotations

from typing import Any, Callable

from fastapi import FastAPI, HTTPException


def register_certificate_routes(app: FastAPI, *, get_cert_manager: Callable[[], Any]) -> None:
    def cert_manager():
        return get_cert_manager()

    @app.get('/certificates')
    async def certificates_status():
        return {'ok': True, 'status': cert_manager().status()}

    @app.post('/certificates/generate')
    async def certificates_generate(request: dict | None = None):
        force = bool((request or {}).get('force', False))
        result = cert_manager().generate_all(force=force)
        result['chain'] = cert_manager().verify_chain()
        return result

    @app.get('/certificates/verify')
    async def certificates_verify():
        return cert_manager().verify_chain()

    @app.get('/certificates/inspect/{which}')
    async def certificates_inspect(which: str):
        paths = {
            'ca': cert_manager().ca_cert,
            'server': cert_manager().server_cert,
            'client': cert_manager().client_cert,
        }
        p = paths.get(which)
        if not p:
            raise HTTPException(status_code=400, detail='which muss ca, server oder client sein')
        if not p.exists():
            return {'ok': False, 'error': f'{which}-Zertifikat existiert nicht'}
        try:
            return {'ok': True, 'which': which, 'info': cert_manager().inspect(p)}
        except Exception as exc:
            return {'ok': False, 'error': str(exc)}
