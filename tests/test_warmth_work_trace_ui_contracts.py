from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from eidolon.web_routes import read_root_html

ROOT = Path(__file__).resolve().parents[1]


class _RenderedIndexHtml:
    def read_text(self, encoding: str = 'utf-8') -> str:
        return read_root_html(ROOT)


INDEX_HTML = _RenderedIndexHtml()
APP_SHELL_JS = ROOT / 'python' / 'eidolon' / 'web' / 'app-shell.js'
CHAT_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
OPERATE_VIEW_JS = ROOT / 'python' / 'eidolon' / 'web' / 'operate-view-ui.js'
WORKSPACE_PROJECT_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-project-ui.js'
THEME_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'shell' / 'shell-theme.css'
LAYOUT_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'shell' / 'shell-layout.css'
PRESENCE_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'shell' / 'eidolon-presence.css'
THREAD_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'chat' / 'chat-thread.css'
BASE_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'app-components-base.css'
CANVAS_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'app-canvas.css'


def test_dark_theme_keeps_warm_character_without_light_flip():
    theme = THEME_CSS.read_text(encoding='utf-8')
    layout = LAYOUT_CSS.read_text(encoding='utf-8')
    presence = PRESENCE_CSS.read_text(encoding='utf-8')
    html = INDEX_HTML.read_text()
    assert 'data-theme="dark"' in html
    assert '--bg: #16130f' in theme
    assert '--accent: #d9a15c' in theme
    assert '--font-display' in theme
    assert '#0b0d12' not in theme
    assert '#4a7dff' not in theme
    assert '[data-theme="light"]' in theme
    assert 'data-theme="light"' not in html
    assert 'presence-smoke-drift' not in presence
    assert 'eidolon-presence-live' in presence
    assert 'data-eidolon-presence' in html
    assert 'class="eidolon-presence-live"' in html
    assert 'prefers-reduced-motion' in presence
    assert 'prefers-reduced-motion' in layout


def test_slim_idle_chat_is_warmed_not_refilled():
    html = INDEX_HTML.read_text()
    css = THREAD_CSS.read_text(encoding='utf-8')
    js = CHAT_UI_JS.read_text(encoding='utf-8')
    assert 'chat-is-idle' in html
    assert 'id="chat-idle-prompt"' in html
    assert 'Woran sollen wir arbeiten?' in html
    assert 'id="chat-project-door"' in html
    assert 'id="chat-work-trace"' not in html
    assert '.chat-project-door' in css
    assert '.chat-is-idle #chat-formation' in css
    assert 'font-family: var(--font-display)' in css
    assert 'start-suggestion' not in html
    assert 'chip-start' not in html
    assert 'id="chat-home-suggestions"' not in html
    assert "el.innerHTML = '<div class=\"empty chat-idle-hint\">Bereit, wenn du es bist.</div>'" in js
    assert 'Noch kein Gesprächskontext.' not in js


def test_work_trace_uses_real_kernel_and_session_signals():
    html = INDEX_HTML.read_text()
    shell = APP_SHELL_JS.read_text(encoding='utf-8')
    chat = CHAT_UI_JS.read_text(encoding='utf-8')
    operate = OPERATE_VIEW_JS.read_text(encoding='utf-8')
    workspace = WORKSPACE_PROJECT_JS.read_text(encoding='utf-8')
    css = BASE_CSS.read_text(encoding='utf-8')
    for marker in ('id="operate-work-trace"', 'id="ws-work-trace"', 'data-work-trace'):
        assert marker in html
    assert 'id="chat-work-trace"' not in html
    assert 'function describeWorkTrace' in shell
    assert 'function pickRecentLocalWork' in shell
    assert 'function refreshWorkTraces' in shell
    assert 'nichts wartet' in shell
    assert 'dein Impuls' in shell
    assert "title !== 'Neue Unterhaltung'" in shell
    assert 'refreshWorkTraces(data)' in chat
    assert 'refreshWorkTraces(data)' in operate
    assert 'refreshWorkTraces({' in workspace
    assert 'work-trace-breathe' in css
    assert 'progress-bar' not in css
    assert 'demo-run' not in shell
    assert 'fake' not in shell.lower()


def test_operate_idle_is_living_empty_not_tombstone():
    html = INDEX_HTML.read_text()
    css = BASE_CSS.read_text(encoding='utf-8')
    assert 'Noch kein laufender Schritt.' in html
    assert 'Im Chat starten' in html
    assert 'class="operate-idle-paths"' in html
    assert 'id="operate-work-trace"' in html
    assert 'Der Kern atmet' not in html
    assert '.operate-idle-paths' in css
    assert '.work-trace-pulse' in css


def test_status_badge_stays_honest_and_warmer():
    css = CANVAS_CSS.read_text(encoding='utf-8')
    js = (ROOT / 'python' / 'eidolon' / 'web' / 'dashboard-ui.js').read_text(encoding='utf-8')
    assert "label: 'Lokal'" in js
    assert "label: 'Lokal · Grenzen'" in js
    assert 'kein voller Mesh-/QUIC-Status' in js
    assert '.ws-status.limited .dot' in css
    assert 'border-radius: 999px' in css
    assert 'z-index: 51' in css
