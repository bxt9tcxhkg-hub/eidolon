from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.web_routes import ALLOWED_ASSETS, read_root_html

ROOT = Path(__file__).resolve().parents[1]
PRESENCE_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'shell' / 'eidolon-presence.css'
PRESENCE_JS = ROOT / 'python' / 'eidolon' / 'web' / 'eidolon-presence.js'
APP_SHELL_JS = ROOT / 'python' / 'eidolon' / 'web' / 'app-shell.js'
CHAT_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
CHAT_ROUTES = ROOT / 'python' / 'eidolon' / 'chat_message_routes.py'
MOBILE_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'app-mobile.css'
SESSION_RAIL_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'chat' / 'chat-session-rail.css'


def _html():
    return read_root_html(ROOT)


def test_chat_presence_slot_uses_approved_still_and_german_aria():
    html = _html()
    assert 'id="chat-eidolon-presence"' in html
    assert 'data-eidolon-presence' in html
    assert 'data-turn-phase="idle"' in html
    assert 'aria-label="Eidolon ist bereit"' in html
    assert 'src="/assets/media/eidolon-presence.png"' in html
    assert 'srcset="/assets/media/eidolon-presence.webp"' in html
    assert 'class="eidolon-presence-live"' in html
    assert 'id="eidolon-signature"' in html
    assert 'eidolon-signature hero' not in html
    assert 'chat-panel-heading' in html
    assert html.count('id="chat-eidolon-presence"') == 1
    assert html.count('data-eidolon-presence') == 2
    assert html.index('id="chat-eidolon-presence"') < html.index('id="chat-session-title"')
    assert html.index('id="chat-eidolon-presence"') < html.index('id="chat-agent-status"')


def test_presence_motion_binds_to_real_turn_phases_only():
    js = CHAT_UI_JS.read_text(encoding='utf-8')
    shell = APP_SHELL_JS.read_text(encoding='utf-8')
    routes = CHAT_ROUTES.read_text(encoding='utf-8')
    live = PRESENCE_JS.read_text(encoding='utf-8')
    assert 'function setEidolonTurnPhase(phase)' in shell
    assert "phase === 'denkt' || phase === 'arbeitet' || phase === 'antwortet'" in shell
    assert "Eidolon denkt" in shell
    assert "Eidolon arbeitet" in shell
    assert "Eidolon antwortet" in shell
    assert 'setEidolonTurnPhase(phase)' in js
    assert "setChatAgentStatus('denkt', 'local')" in js
    assert "setChatAgentStatus('antwortet', 'response')" in js
    assert "setChatAgentStatus('arbeitet'" not in js
    assert "PHASE_ARBEITET" not in routes
    assert 'dataset.turnPhase' in live
    assert "phase === 'antwortet'" in live
    assert "phase === 'denkt' || phase === 'arbeitet'" in live
    assert 'getElementById(\'chat-messages\')' in live
    assert 'getElementById(\'chat-input\')' in live
    assert 'emotion ai' not in shell.lower()
    assert 'emotionserkennung' not in live.lower()
    assert 'emotion detection' not in live.lower()
    assert 'voice' not in live.lower()


def test_presence_uses_internal_warp_not_bitmap_pan_zoom():
    css = PRESENCE_CSS.read_text(encoding='utf-8')
    live = PRESENCE_JS.read_text(encoding='utf-8')
    html = _html()
    assert 'presence-smoke-drift' not in css
    assert 'presence-smoke-micro' not in css
    assert '@keyframes' not in css
    assert 'translate(' not in css
    assert 'rotate(' not in css
    assert 'scale(' not in css
    assert 'getContext(\'webgl\'' in live
    assert 'curl(' in live
    assert 'createPresenceCanvas2D' in live
    assert 'class="eidolon-presence-live"' in html
    assert 'function startEidolonPresence' in live
    assert 'function syncEidolonPresenceMotion' in live


def test_presence_reduced_motion_and_animation_setting_freeze_to_still():
    css = PRESENCE_CSS.read_text(encoding='utf-8')
    live = PRESENCE_JS.read_text(encoding='utf-8')
    shell = APP_SHELL_JS.read_text(encoding='utf-8')
    assert '@media (prefers-reduced-motion: reduce)' in css
    assert '[data-animations="off"] [data-eidolon-presence]' in css
    assert 'display: none !important' in css
    assert 'object-position: 56% 42%' in css
    assert "getAttribute('data-animations') === 'off'" in live
    assert "prefers-reduced-motion: reduce" in live
    assert 'syncEidolonPresenceMotion()' in shell


def test_presence_stays_a_mark_near_title_not_a_hero():
    css = PRESENCE_CSS.read_text(encoding='utf-8')
    mobile = MOBILE_CSS.read_text(encoding='utf-8')
    heading = SESSION_RAIL_CSS.read_text(encoding='utf-8')
    html = _html()
    assert 'max-width: 56px' in css
    assert 'max-height: 56px' in css
    assert 'width: 48px' in css
    assert 'width: 42px' in css
    assert 'max-width: 42px' in mobile
    assert '.chat-panel-heading' in heading
    assert 'eidolon-signature hero' not in html
    assert 'chat-home-hero' not in html


def test_presence_assets_are_allowlisted_and_served_as_images():
    client = TestClient(agent_server.app)
    assert ALLOWED_ASSETS['media/eidolon-presence.png'] == 'image/png'
    assert ALLOWED_ASSETS['media/eidolon-presence.webp'] == 'image/webp'
    assert ALLOWED_ASSETS['eidolon-presence.js'] == 'application/javascript'
    png = client.get('/assets/media/eidolon-presence.png')
    webp = client.get('/assets/media/eidolon-presence.webp')
    js = client.get('/assets/eidolon-presence.js')
    assert png.status_code == 200
    assert webp.status_code == 200
    assert js.status_code == 200
    assert png.headers['content-type'].startswith('image/png')
    assert webp.headers['content-type'].startswith('image/webp')
    assert 'javascript' in js.headers['content-type']
    assert png.content[:8] == b'\x89PNG\r\n\x1a\n'
    assert webp.content[:4] == b'RIFF'
    assert b'function startEidolonPresence' in js.content
