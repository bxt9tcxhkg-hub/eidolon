from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.web_routes import read_root_html

ROOT = Path(__file__).resolve().parents[1]


class _RenderedIndexHtml:
    def read_text(self, encoding: str = 'utf-8') -> str:
        return read_root_html(ROOT)


INDEX_HTML = _RenderedIndexHtml()
OPERATE_JS = ROOT / 'python' / 'eidolon' / 'web' / 'operate-ui.js'
OPERATE_RENDER_JS = ROOT / 'python' / 'eidolon' / 'web' / 'operate-render-ui.js'
OPERATE_ACTIONS_JS = ROOT / 'python' / 'eidolon' / 'web' / 'operate-actions-ui.js'
OPERATE_VIEW_JS = ROOT / 'python' / 'eidolon' / 'web' / 'operate-view-ui.js'
APP_SHELL_JS = ROOT / 'python' / 'eidolon' / 'web' / 'app-shell.js'
CHAT_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
GOALS_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'goals-ui.js'
PODS_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'pods-ui.js'
EXECUTION_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'execution-ui.js'
APP_WEB_JS = '\n'.join([p.read_text(encoding='utf-8') for p in [APP_SHELL_JS, CHAT_UI_JS, GOALS_UI_JS]])
OPERATE_WEB_JS = '\n'.join([p.read_text(encoding='utf-8') for p in [OPERATE_JS, OPERATE_RENDER_JS, OPERATE_ACTIONS_JS, OPERATE_VIEW_JS, PODS_UI_JS, EXECUTION_UI_JS]])
WORKSPACE_WEB_JS = '\n'.join([p.read_text(encoding='utf-8') for p in [ROOT / 'python' / 'eidolon' / 'web' / 'workspace-ui.js', ROOT / 'python' / 'eidolon' / 'web' / 'workspace-project-ui.js', ROOT / 'python' / 'eidolon' / 'web' / 'workspace-canvas-ui.js']])


def test_operate_ui_panel_and_anchors_exist():
    html = INDEX_HTML.read_text(encoding='utf-8')
    assert 'id="panel-chat"' in html
    assert 'id="panel-workspaces"' in html
    assert 'id="panel-dashboard"' in html
    assert 'id="panel-mesh"' in html
    assert 'data-tab="chat"' in html
    assert 'data-tab="workspaces"' in html
    assert 'data-tab="dashboard"' in html
    assert 'data-tab="mesh"' in html
    assert 'id="chat-active-summary"' in html
    assert 'id="chat-decision-summary"' in html
    assert 'id="chat-recent-summary"' in html
    assert 'id="chat-context-state"' in html
    assert 'id="chat-intent-mode"' in html
    assert 'id="chat-next-step"' in html
    assert 'id="pods-list"' in html
    assert 'id="pod-detail"' in html
    assert 'id="panel-execution"' in html
    assert 'id="execution-summary"' in html
    assert 'id="execution-capabilities"' in html
    assert 'id="execution-devices"' in html
    assert '/assets/pods-ui.js' in html
    assert '/assets/execution-ui.js' in html
    shell = APP_WEB_JS
    assert "let currentTab = 'chat';" in shell
    assert "const LANDING_TAB = 'chat';" in shell
    assert 'function resolveInitialTab()' in shell
    assert "function showTab(tabId)" in shell


def test_operate_ui_script_targets_api_v1_contracts():
    js = OPERATE_WEB_JS
    assert '/api/v1/operate/overview' in js
    assert '/api/v1/session/sync-from-workspaces' in js
    assert '/api/v1/runs/' in js
    assert '/history' in js
    assert '/work-graph' in js
    assert '/advance' in js
    assert '/request-approval' in js
    assert '/blockers/' in js
    assert '/approval/' in js
    assert 'subagents' in js
    assert 'evidence' in js
    assert 'next_action' in js
    assert 'transitions' in js
    assert 'history' in js
    assert 'work_graph' in js
    pods_js = ROOT / 'python' / 'eidolon' / 'web' / 'pods-ui.js'
    execution_js = ROOT / 'python' / 'eidolon' / 'web' / 'execution-ui.js'
    assert 'loadPodsView' in pods_js.read_text(encoding='utf-8')
    assert 'openPodDetail' in pods_js.read_text(encoding='utf-8')
    assert 'loadExecutionView' in execution_js.read_text(encoding='utf-8')


def test_operate_ui_asset_and_page_are_served():
    client = TestClient(agent_server.app)
    root = client.get('/')
    assert root.status_code == 200
    assert 'panel-chat' in root.text
    assert 'panel-workspaces' in root.text
    assert 'panel-dashboard' in root.text
    assert 'panel-mesh' in root.text
    assert 'chat-active-summary' in root.text
    assert 'chat-decision-summary' in root.text
    assert 'chat-recent-summary' in root.text
    assert 'chat-context-state' in root.text
    assert 'chat-intent-mode' in root.text
    assert 'chat-next-step' in root.text
    assert 'panel-pods' in root.text
    assert 'pods-list' in root.text
    assert 'pod-detail' in root.text
    assert 'panel-execution' in root.text
    assert 'execution-summary' in root.text
    assert 'execution-capabilities' in root.text
    assert 'execution-devices' in root.text
    assert '/assets/pods-ui.js' in root.text
    assert '/assets/execution-ui.js' in root.text

    assert client.get('/assets/pods-ui.js').status_code == 200
    assert client.get('/assets/execution-ui.js').status_code == 200


def test_workspace_and_goals_ui_scripts_now_reference_operate_kernel():
    html = INDEX_HTML.read_text(encoding='utf-8')
    workspace_js = WORKSPACE_WEB_JS

    assert '/workspaces' in workspace_js
    assert '/assets/workspace-project-ui.js' in html
    assert '/assets/workspace-canvas-ui.js' in html
    assert 'operate' in workspace_js
    shell = APP_WEB_JS
    assert '/api/v1/operate/overview' in shell
    assert 'Operate-Zustand' in workspace_js
    assert "/api/v1/operate/goals" in shell
    assert "/api/v1/operate/cycle" in shell


def test_goals_ui_uses_inline_composer_not_modal_overlay():
    html = INDEX_HTML.read_text(encoding='utf-8')
    assert 'id="goal-composer-card"' in html
    assert 'id="goal-inline-title"' in html
    assert 'id="goal-inline-description"' in html
    assert 'id="goal-inline-category"' in html
    assert 'id="goal-inline-priority"' in html
    assert 'id="goal-inline-steps"' in html
    assert 'id="goal-modal"' not in html
