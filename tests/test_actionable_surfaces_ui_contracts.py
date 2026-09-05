from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from eidolon.web_routes import read_root_html

ROOT = Path(__file__).resolve().parents[1]


class _RenderedIndexHtml:
    def read_text(self, encoding: str = 'utf-8') -> str:
        return read_root_html(ROOT)


INDEX_HTML = _RenderedIndexHtml()
CHAT_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
OPERATE_RENDER_JS = ROOT / 'python' / 'eidolon' / 'web' / 'operate-render-ui.js'
OPERATE_VIEW_JS = ROOT / 'python' / 'eidolon' / 'web' / 'operate-view-ui.js'
OPERATE_ACTIONS_JS = ROOT / 'python' / 'eidolon' / 'web' / 'operate-actions-ui.js'
WORKSPACE_PROJECT_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-project-ui.js'
WORKSPACE_VIEWS_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-views-ui.js'
APP_SHELL_JS = ROOT / 'python' / 'eidolon' / 'web' / 'app-shell.js'
SETTINGS_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'settings-ui.js'
COMPONENTS_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'app-components-base.css'
INDEX_HEAD = ROOT / 'python' / 'eidolon' / 'web' / 'fragments' / 'index-head.html'


def test_projektflaeche_idle_is_new_project_plus_board():
    html = INDEX_HTML.read_text()
    project_js = WORKSPACE_PROJECT_JS.read_text(encoding='utf-8')
    css = COMPONENTS_CSS.read_text(encoding='utf-8')
    assert 'id="ws-idle-hero"' in html
    assert 'id="ws-idle-line"' in html
    assert 'Noch kein Projekt' in html
    assert 'id="ws-idle-new-project"' in html
    assert '>Neues Projekt</button>' in html
    assert 'Lege ein Projekt an oder starte im Chat' in html
    assert 'id="ws-planning-scaffold-board"' in html
    for column in ('idea', 'planned', 'in_progress', 'blocked', 'done', 'archived'):
        assert 'data-plan-column="' + column + '"' in html
    assert 'id="ws-overview-card"' in html
    assert 'id="ws-overview-card" hidden' in html
    assert 'Operate-Zustand' in project_js
    assert 'overview.hidden = true' in project_js
    assert 'function syncWorkspaceIdleLayout' in project_js
    assert "panel.classList.toggle('workspaces-is-idle', idle)" in project_js
    assert '.workspaces-is-idle #ws-overview-card' in css
    assert html.find('id="ws-idle-hero"') < html.find('id="ws-planning-scaffold-board"')
    assert html.find('id="ws-overview-card"') < html.find('id="ws-idle-hero"')


def test_projektflaeche_open_project_is_board_first():
    html = INDEX_HTML.read_text()
    assert 'id="ws-project-title-edit"' in html
    assert 'id="ws-project-status-edit"' in html
    assert 'id="ws-project-secondary"' in html
    assert 'Im Chat öffnen' in html
    assert 'Arbeit zeigen' in html
    assert 'id="ws-elements-card"' in html
    assert html.find('id="ws-project-title-edit"') < html.find('id="ws-elements-card"')
    assert html.find('id="ws-elements-card"') < html.find('id="ws-project-slots"')
    assert html.find('id="ws-project-secondary"') < html.find('id="ws-elements-card"')
    assert html.find('data-tab-target="chat">Im Chat öffnen') < html.find('id="ws-elements-view"')
    assert 'id="ws-project-stats-details"' in html
    assert 'id="ws-project-slots-details"' in html
    assert html.find('id="ws-elements-card"') < html.find('id="ws-project-slots-details"')
    assert 'projectsCard.hidden = hasOpenProject' in WORKSPACE_PROJECT_JS.read_text(encoding='utf-8')


def test_arbeit_idle_has_three_clear_paths():
    html = INDEX_HTML.read_text()
    render_js = OPERATE_RENDER_JS.read_text(encoding='utf-8')
    actions_js = OPERATE_ACTIONS_JS.read_text(encoding='utf-8')
    css = COMPONENTS_CSS.read_text(encoding='utf-8')
    assert 'id="operate-idle-empty"' in html
    assert 'id="operate-idle-start-chat"' in html
    assert 'Im Chat starten' in html
    assert 'id="operate-idle-from-project"' in html
    assert 'Aus Projektfläche übernehmen' in html
    assert 'Hier siehst du Freigaben und den nächsten Schritt, sobald etwas läuft.' in html
    assert 'function syncOperateProjectPath' in render_js
    assert 'fromProject.hidden = !hasProject' in render_js
    assert 'async function takeOverFromProject' in actions_js
    assert "data-ui-action=\"takeOverFromProject\"" in html
    assert 'Kein aktiver Lauf. Starte im Chat oder übernimm reale Arbeit aus der Projektfläche.' not in html
    assert '.operate-idle-paths' in css
    assert '#operate-idle-from-project[hidden]' in css


def test_arbeit_run_keeps_priority_and_collapses_rest():
    html = INDEX_HTML.read_text()
    render_js = OPERATE_RENDER_JS.read_text(encoding='utf-8')
    view_js = OPERATE_VIEW_JS.read_text(encoding='utf-8')
    assert 'data-operate-priority="objective"' in html
    assert 'data-operate-priority="next"' in html
    assert 'data-operate-priority="approvals"' in html
    assert 'data-operate-priority="blockers"' in html
    assert 'id="operate-empty-details"' in html
    assert html.find('data-operate-priority="objective"') < html.find('id="operate-empty-details"')
    assert html.find('id="operate-approvals"') < html.find('id="operate-empty-details"')
    assert html.find('id="operate-empty-details"') < html.find('id="operate-state-bar"')
    assert html.find('id="operate-empty-details"') < html.find('data-operate-section="subagents"')
    assert html.find('id="operate-empty-details"') < html.find('data-operate-section="history"')
    assert "details.hidden = !hasRun" in render_js
    assert 'details.open = false' in render_js
    assert 'syncOperateEmptyLayout({' in view_js
    assert '/api/v1/operate/overview' in view_js
    assert 'function renderNextAction(runId, nextAction, approvals)' in render_js
    assert '>Freigeben</button>' in render_js
    assert '>Ablehnen</button>' in render_js
    assert "nextAction.kind === 'next_step' && nextAction.action_enabled && !pending.length" in render_js
    assert 'renderNextAction(run.id, nextAction, approvals)' in view_js


def test_action_motion_confirms_real_mutations_only():
    shell = APP_SHELL_JS.read_text(encoding='utf-8')
    settings = SETTINGS_UI_JS.read_text(encoding='utf-8')
    css = COMPONENTS_CSS.read_text(encoding='utf-8')
    head = INDEX_HEAD.read_text(encoding='utf-8')
    project_js = WORKSPACE_PROJECT_JS.read_text(encoding='utf-8')
    views_js = WORKSPACE_VIEWS_JS.read_text(encoding='utf-8')
    actions_js = OPERATE_ACTIONS_JS.read_text(encoding='utf-8')
    chat_js = CHAT_UI_JS.read_text(encoding='utf-8')
    assert 'function confirmAction(target, kind)' in shell
    assert 'function actionMotionEnabled()' in shell
    assert 'function applyUiMotionPreference(settings)' in shell
    assert "getAttribute('data-animations') === 'off'" in shell
    assert "prefers-reduced-motion: reduce" in shell
    assert "data-animations=\"on\"" in head
    assert 'applyUiMotionPreference(settings)' in settings
    assert '@keyframes action-confirm-flash' in css
    assert '@media (prefers-reduced-motion: reduce)' in css
    assert '[data-animations="off"] .action-confirm' in css
    assert "confirmAction(document.getElementById('panel-workspaces'), 'created')" in project_js
    assert "confirmAction(document.getElementById('ws-project-status-edit')" in project_js
    assert "confirmAction(moved || column, 'moved')" in views_js
    assert "confirmAction(card || document.getElementById('ws-elements-view')" in views_js
    assert 'plan-card-notes' in views_js
    assert '.plan-card-notes' in css
    assert "confirmAction(document.getElementById('operate-approvals')" in actions_js
    assert "confirmAction(document.getElementById('operate-next-action')" in actions_js
    assert 'resolveOperateApproval' in chat_js
    assert 'advanceOperateRun' in chat_js
    assert 'logo-breath' not in css
    assert 'signature-breathe' not in css
    assert "kind || 'settle'" in shell


def test_chat_stays_slim_default_entry():
    html = INDEX_HTML.read_text()
    shell = APP_SHELL_JS.read_text(encoding='utf-8')
    assert '<div id="panel-chat" class="tab-panel active chat-is-idle">' in html
    assert "let currentTab = 'chat';" in shell
    assert "const initialTab = (window.location.hash || '#chat').replace('#', '');" in shell
    assert 'id="chat-idle-prompt"' in html
    assert 'Woran sollen wir arbeiten?' in html
