from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response


ALLOWED_ASSETS = {
    'app-shell.css': 'text/css',
    'app-components.css': 'text/css',
    'app-canvas.css': 'text/css',
    'app-mobile.css': 'text/css',
    'components/app-components-base.css': 'text/css',
    'components/app-components-chat.css': 'text/css',
    'components/app-components-goals.css': 'text/css',
    'components/chat/chat-session-rail.css': 'text/css',
    'components/chat/chat-session-items.css': 'text/css',
    'components/chat/chat-thread.css': 'text/css',
    'components/goals/goal-cards.css': 'text/css',
    'components/goals/goal-workflow.css': 'text/css',
    'components/goals/goal-runtime.css': 'text/css',
    'components/shell/shell-theme.css': 'text/css',
    'components/shell/shell-layout.css': 'text/css',
    'components/shell/shell-header.css': 'text/css',
    'code-repair-ui.js': 'application/javascript',
    'healing-ui.js': 'application/javascript',
    'skills-backups-ui.js': 'application/javascript',
    'settings-ui.js': 'application/javascript',
    'workspace-views-ui.js': 'application/javascript',
    'workspace-element-composer-ui.js': 'application/javascript',
    'app-shell.js': 'application/javascript',
    'chat-ui.js': 'application/javascript',
    'dashboard-ui.js': 'application/javascript',
    'goals-ui.js': 'application/javascript',
    'admin-ui.js': 'application/javascript',
    'workspace-ui.js': 'application/javascript',
    'workspace-project-ui.js': 'application/javascript',
    'workspace-canvas-ui.js': 'application/javascript',
    'operate-ui.js': 'application/javascript',
    'operate-render-ui.js': 'application/javascript',
    'operate-actions-ui.js': 'application/javascript',
    'operate-view-ui.js': 'application/javascript',
    'pods-ui.js': 'application/javascript',
    'execution-ui.js': 'application/javascript',
}
ROOT_PAGE_FRAGMENTS = [
    'index-head.html',
    'index-operate-chat-dashboard.html',
    'index-workspaces-goals.html',
    'index-healing-footer.html',
]


def get_web_root(project_root: Path) -> Path:
    return Path(project_root) / 'python' / 'eidolon' / 'web'


def read_root_html(project_root: Path) -> str:
    web_root = get_web_root(project_root)
    fragments_root = web_root / 'fragments'
    return ''.join((fragments_root / name).read_text(encoding='utf-8') for name in ROOT_PAGE_FRAGMENTS)


def register_web_routes(app: FastAPI, project_root: Path) -> None:
    web_root = get_web_root(project_root)

    @app.get('/', response_class=HTMLResponse)
    async def root():
        return HTMLResponse(content=read_root_html(project_root))

    @app.get('/assets/{asset_path:path}')
    async def web_asset(asset_path: str):
        normalized = asset_path.strip('/').replace('\\', '/')
        media_type = ALLOWED_ASSETS.get(normalized)
        if media_type is None:
            raise HTTPException(status_code=404, detail='Asset nicht gefunden')
        resolved_path = (web_root / normalized).resolve()
        if web_root.resolve() not in resolved_path.parents:
            raise HTTPException(status_code=404, detail='Asset nicht gefunden')
        if not resolved_path.exists():
            raise HTTPException(status_code=404, detail='Asset nicht gefunden')
        return Response(content=resolved_path.read_text(encoding='utf-8'), media_type=media_type)
