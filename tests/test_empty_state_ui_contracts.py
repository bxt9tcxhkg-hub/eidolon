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
WORKSPACE_PROJECT_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-project-ui.js'
WORKSPACE_VIEWS_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-views-ui.js'
APP_SHELL_JS = ROOT / 'python' / 'eidolon' / 'web' / 'app-shell.js'
DASHBOARD_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'dashboard-ui.js'
CHAT_THREAD_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'chat' / 'chat-thread.css'
SESSION_RAIL_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'chat' / 'chat-session-rail.css'
COMPONENTS_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'app-components-base.css'
CANVAS_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'app-canvas.css'


def test_chat_empty_state_is_radically_slim():
    html = INDEX_HTML.read_text()
    js = CHAT_UI_JS.read_text(encoding='utf-8')
    css = CHAT_THREAD_CSS.read_text(encoding='utf-8')
    assert 'id="panel-chat"' in html
    assert 'chat-is-idle' in html
    assert 'id="chat-idle-prompt"' in html
    assert 'Woran sollen wir arbeiten?' in html
    assert 'id="chat-project-door"' in html
    assert 'id="chat-session-title"' in html
    assert 'id="chat-landing-panels"' not in html
    assert 'id="chat-context-summary"' not in html
    assert 'Gerade aktiv' not in html
    assert 'Braucht deine Entscheidung' not in html
    assert 'id="chat-runtime-problems"' not in html
    assert 'id="chat-formation"' in html
    assert 'id="chat-operate-actions"' in html
    assert 'function chatHasUserMessage' in js
    assert 'function syncChatIdleLayout' in js
    assert 'function renderChatProjectDoor' in js
    assert 'const idle = !chatHasUserMessage();' in js
    assert "panel.classList.toggle('chat-is-idle', idle)" in js
    assert '.chat-project-door' in css
    assert '.chat-is-idle #chat-formation' in css
    assert '.chat-is-idle #chat-operate-actions' in css
    assert "el.innerHTML = '<div class=\"empty chat-idle-hint\">Bereit, wenn du es bist.</div>'" in js
    assert 'Schreibe oben dein Ziel, damit Eidolon einen realen Arbeitskontext aufbauen kann.' not in js
    assert '<div id="panel-operate" class="tab-panel active">' not in html
    assert 'data-tab="chat" data-tab-target="chat"' in html


def test_operate_empty_state_hides_empty_section_wall():
    html = INDEX_HTML.read_text()
    render_js = OPERATE_RENDER_JS.read_text(encoding='utf-8')
    view_js = OPERATE_VIEW_JS.read_text(encoding='utf-8')
    css = COMPONENTS_CSS.read_text(encoding='utf-8')
    assert 'id="operate-idle-empty"' in html
    assert 'Im Chat starten' in html
    assert 'Aus Projektfläche übernehmen' in html
    assert 'sobald etwas läuft' in html
    assert 'id="operate-work-trace"' in html
    assert 'id="operate-empty-details"' in html
    assert 'data-operate-section="objective"' in html
    assert 'data-operate-section="approvals"' in html
    assert 'data-operate-section="blockers"' in html
    assert 'data-operate-section="subagents"' in html
    assert 'data-operate-section="evidence"' in html
    assert 'data-operate-section="history"' in html
    assert 'data-operate-section="workgraph"' in html
    assert 'data-operate-section="transitions"' in html
    assert 'id="operate-state-bar"' in html
    assert 'id="operate-next-action"' in html
    assert 'function syncOperateEmptyLayout' in render_js
    assert "panel.classList.toggle('operate-is-idle', !hasRun)" in render_js
    assert 'syncOperateEmptyLayout({ hasRun: false })' in view_js
    assert 'syncOperateEmptyLayout({' in view_js
    assert '.operate-is-idle [data-operate-section]' in css
    assert 'id="operate-objective-card"' in html
    assert '/api/v1/operate/overview' in view_js


def test_projektflaeche_empty_shows_planning_scaffold():
    html = INDEX_HTML.read_text()
    project_js = WORKSPACE_PROJECT_JS.read_text(encoding='utf-8')
    views_js = WORKSPACE_VIEWS_JS.read_text(encoding='utf-8')
    assert 'id="ws-planning-scaffold"' in html
    assert 'id="ws-planning-scaffold-board"' in html
    for column in ('idea', 'planned', 'in_progress', 'blocked', 'done', 'archived'):
        assert 'data-plan-column="' + column + '"' in html
    for label in ('Zusammengehörig', 'Geplant', 'In Arbeit', 'Fertig', 'Archiv'):
        assert label in html
    assert '+ Neues Projekt' in html
    assert 'id="ws-idle-hero"' in html
    assert 'Noch kein Projekt' in html
    assert '>Neues Projekt</button>' in html
    assert 'function syncWorkspaceIdleLayout' in project_js
    assert 'Keine Elemente für das Board vorhanden' not in views_js
    assert "['idea', 'Zusammengehörig']" in views_js
    assert "['archived', 'Archiv']" in views_js


def test_nav_highlight_tracks_visible_surface():
    html = INDEX_HTML.read_text()
    shell = APP_SHELL_JS.read_text(encoding='utf-8')
    rail = SESSION_RAIL_CSS.read_text(encoding='utf-8')
    assert 'function syncNavHighlight(tabId)' in shell
    assert "n.classList.toggle('active', on)" in shell
    assert "window.addEventListener('hashchange'" in shell
    assert 'onclick="openChatSession(' in CHAT_UI_JS.read_text(encoding='utf-8')
    assert 'async function openChatSession(sessionId)' in CHAT_UI_JS.read_text(encoding='utf-8')
    assert 'aria-current="page"' in html
    assert '.nav-item[data-tab="chat"].active + .chat-session-rail' in rail
    assert 'data-tab="chat" data-tab-target="chat"' in html
    assert 'data-tab="workspaces" data-tab-target="workspaces"' in html
    assert 'data-tab="operate" data-tab-target="operate"' in html


def test_local_runtime_status_is_quiet_and_honest():
    js = DASHBOARD_UI_JS.read_text(encoding='utf-8')
    css = CANVAS_CSS.read_text(encoding='utf-8')
    assert 'function describeLocalRuntimeStatus' in js
    assert 'function applyLocalRuntimeStatus' in js
    assert 'Lokal verbunden' in js
    assert 'Backend nicht erreichbar' in js
    assert 'Lokal eingeschränkt:' in js
    assert "label: 'Lokal'" in js
    assert "label: 'Lokal · Grenzen'" in js
    assert "tone: 'quiet'" in js
    assert "el.title = info.title" in js
    assert "wsStatus.innerHTML = '<span class=\"dot\"></span> ' + escapeHtml(d.status === 'ok' ? 'Lokal verbunden' : 'Lokal eingeschränkt')" not in js
    assert 'kein voller Mesh-/QUIC-Status' in js
    assert '.ws-status.limited .dot' in css
    assert 'font-size: 0.72rem' in css
    assert 'z-index: 51' in css
