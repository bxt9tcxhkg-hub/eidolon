from __future__ import annotations

from typing import Any, Callable

from fastapi import FastAPI, HTTPException

VALID_TABS = ["chat", "dashboard", "workspaces", "mesh", "goals", "identity", "code", "healing", "skills"]


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
        return {'ok': True, 'settings': payload['settings'], 'settings_meta': payload['meta'], 'source_counts': payload['source_counts']}

    @app.get('/settings/{area}')
    async def get_settings_area(area: str):
        payload = settings_store().get_area_with_meta(area)
        return {'ok': True, 'area': area, 'settings': payload['settings'], 'settings_meta': payload['meta']}

    @app.post('/settings/{area}')
    async def update_settings_area(area: str, request: dict):
        result = settings_store().set_area(area, request)
        if area == 'llm' and result.get('ok'):
            reconfigure_llm()
        return {'ok': True, 'area': area, **result}

    @app.post('/settings/{area}/reset')
    async def reset_settings_area(area: str):
        result = settings_store().reset_area(area)
        if area == 'llm' and result.get('ok'):
            reconfigure_llm()
        return {'ok': True, 'area': area, **result}
