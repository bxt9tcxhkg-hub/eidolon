from __future__ import annotations

from typing import Any, Callable

from fastapi import FastAPI, HTTPException

from eidolon.core.llm_config_store import load_openai_api_key
from eidolon.core.llm_secrets import contains_secret
from eidolon.core.settings_apply import apply_user_settings

VALID_TABS = ["chat", "dashboard", "workspaces", "mesh", "goals", "identity", "code", "healing", "skills"]
SECRET_SETTING_KEYS = {'api_key', 'openai_api_key', 'client_secret', 'secret', 'raw_key'}


def _redact_tree(value):
    if isinstance(value, dict):
        return {key: '***' if key in SECRET_SETTING_KEYS else _redact_tree(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact_tree(item) for item in value]
    return value


def _public_payload(payload: dict):
    public = _redact_tree(payload)
    if contains_secret(repr(public), load_openai_api_key()):
        return {'ok': False, 'error': 'Antwort würde ein Geheimnis enthalten und wurde unterdrückt.'}
    if isinstance(public, dict):
        return public
    return payload


def register_settings_routes(
    app: FastAPI,
    *,
    get_settings_store: Callable[[], Any],
    reconfigure_llm: Callable[[], None],
) -> None:
    def settings_store():
        return get_settings_store()

    @app.post('/tab-settings/{tab}')
    async def save_tab_settings(tab: str, request: dict):
        if tab not in VALID_TABS:
            raise HTTPException(status_code=400, detail='Invalid tab')
        result = settings_store().set_area('tab_' + tab, request)
        return {'ok': True, 'tab': tab, **result}

    @app.get('/tab-settings/{tab}')
    async def get_tab_settings(tab: str):
        if tab not in VALID_TABS:
            raise HTTPException(status_code=400, detail='Invalid tab')
        settings = settings_store().get_all('tab_' + tab)
        return {'ok': True, 'tab': tab, 'settings': settings}

    @app.get('/settings')
    async def get_all_settings():
        payload = settings_store().get_all_with_meta()
        return _public_payload({'ok': True, 'settings': payload['settings'], 'settings_meta': payload['meta'], 'source_counts': payload['source_counts']})

    @app.post('/settings/apply')
    async def apply_settings_from_agent(request: dict):
        payload = {
            'user_requested': bool(request.get('user_requested')),
            'area': request.get('area'),
            'values': request.get('values') or {},
            'reason': request.get('reason') or 'Ausdrücklicher Nutzerwunsch',
            'error': request.get('error'),
        }
        result = apply_user_settings(settings_store(), payload, after_llm=reconfigure_llm)
        return _public_payload(result)

    @app.get('/settings/{area}')
    async def get_settings_area(area: str):
        payload = settings_store().get_area_with_meta(area)
        return _public_payload({'ok': True, 'area': area, 'settings': payload['settings'], 'settings_meta': payload['meta']})

    @app.post('/settings/{area}')
    async def update_settings_area(area: str, request: dict):
        safe_request = {key: value for key, value in request.items() if key not in SECRET_SETTING_KEYS}
        result = settings_store().set_area(area, safe_request)
        if area == 'llm' and result.get('ok'):
            reconfigure_llm()
        return _public_payload({'ok': True, 'area': area, **result})

    @app.post('/settings/{area}/reset')
    async def reset_settings_area(area: str):
        result = settings_store().reset_area(area)
        if area == 'llm' and result.get('ok'):
            reconfigure_llm()
        return {'ok': True, 'area': area, **result}
