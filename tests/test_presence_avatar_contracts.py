from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.web_routes import ALLOWED_ASSETS, read_root_html

ROOT = Path(__file__).resolve().parents[1]
PRESENCE_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'shell' / 'eidolon-presence.css'
APP_SHELL_JS = ROOT / 'python' / 'eidolon' / 'web' / 'app-shell.js'
CHAT_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
CHAT_ROUTES = ROOT / 'python' / 'eidolon' / 'chat_message_routes.py'


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
    assert 'id="eidolon-signature"' in html
    assert 'eidolon-signature hero' not in html
    assert html.count('id="chat-eidolon-presence"') == 1
    assert html.count('data-eidolon-presence') == 2


def test_presence_motion_binds_to_real_turn_phases_only():
    js = CHAT_UI_JS.read_text(encoding='utf-8')
    shell = APP_SHELL_JS.read_text(encoding='utf-8')
    routes = CHAT_ROUTES.read_text(encoding='utf-8')
    css = PRESENCE_CSS.read_text(encoding='utf-8')
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
    assert 'data-turn-phase="denkt"' in css
    assert 'data-turn-phase="arbeitet"' in css
    assert 'data-turn-phase="antwortet"' in css
    assert 'emotion' not in shell.lower()
    assert 'voice' not in css.lower()


def test_presence_reduced_motion_and_animation_setting_freeze_to_still():
    css = PRESENCE_CSS.read_text(encoding='utf-8')
    assert '@media (prefers-reduced-motion: reduce)' in css
    assert '[data-animations="off"] [data-eidolon-presence]' in css
    assert 'animation: none !important' in css
    assert 'object-position: 56% 42%' in css


def test_presence_assets_are_allowlisted_and_served_as_images():
    client = TestClient(agent_server.app)
    assert ALLOWED_ASSETS['media/eidolon-presence.png'] == 'image/png'
    assert ALLOWED_ASSETS['media/eidolon-presence.webp'] == 'image/webp'
    png = client.get('/assets/media/eidolon-presence.png')
    webp = client.get('/assets/media/eidolon-presence.webp')
    assert png.status_code == 200
    assert webp.status_code == 200
    assert png.headers['content-type'].startswith('image/png')
    assert webp.headers['content-type'].startswith('image/webp')
    assert png.content[:8] == b'\x89PNG\r\n\x1a\n'
    assert webp.content[:4] == b'RIFF'
