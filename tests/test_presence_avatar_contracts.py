from pathlib import Path
import re
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
    assert 'data-presence-engine="still"' in html
    assert 'data-presence-phase="idle"' in html
    assert 'data-turn-phase="idle"' in html
    assert 'aria-label="Eidolon ist bereit"' in html
    assert 'src="/assets/media/eidolon-presence.png"' in html
    assert 'srcset="/assets/media/eidolon-presence.webp"' in html
    assert 'class="eidolon-presence-live"' in html
    assert 'id="eidolon-signature"' in html
    assert 'eidolon-signature hero' not in html
    assert 'chat-panel-heading' in html
    assert 'chat-composer-chrome' in html
    assert 'id="chat-eidolon-presence-park"' not in html
    assert html.count('id="chat-eidolon-presence"') == 1
    assert html.count('data-eidolon-presence') == 2
    assert html.count('data-presence-engine="still"') == 2
    heading = html.split('class="chat-panel-heading"', 1)[1].split('</div>', 1)[0]
    assert 'chat-eidolon-presence' not in heading
    assert 'id="chat-session-title"' in heading
    assert html.index('id="chat-messages"') < html.index('id="chat-eidolon-presence"')
    assert html.index('class="chat-composer-chrome"') < html.index('id="chat-eidolon-presence"')
    assert html.index('id="chat-eidolon-presence"') < html.index('id="chat-agent-status"')
    assert html.index('id="chat-agent-status"') < html.index('id="chat-input"')
    chrome = html.split('class="chat-composer-chrome"', 1)[1].split('class="chat-input"', 1)[0]
    assert 'id="chat-eidolon-presence"' in chrome
    assert 'id="chat-agent-status"' in chrome


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
    assert "Eidolon achtet auf die Eingabe" in shell
    assert "Eidolon achtet auf die Eingabe" in live
    assert 'setEidolonTurnPhase(phase)' in js
    assert 'data-presence-host' not in js
    assert 'function mountChatPresenceMark' not in js
    assert 'function parkChatPresenceMark' not in js
    assert 'function presenceStillMarkHtml' not in js
    assert "setChatAgentStatus('denkt', 'local')" in js
    assert "setChatAgentStatus('antwortet', 'response')" in js
    assert "setChatAgentStatus('arbeitet'" not in js
    assert "PHASE_ARBEITET" in routes
    assert "skill_execute:" in routes
    assert 'dataset.turnPhase' in live
    assert 'data-presence-phase' in live
    assert "phase === 'antwortet'" in live
    assert "phase === 'denkt' || phase === 'arbeitet'" in live
    assert "phase === 'schreibt'" in live
    assert 'getElementById(\'chat-messages\')' in live
    assert 'getElementById(\'chat-input\')' in live
    assert "addEventListener('focus'" in live
    assert "addEventListener('blur'" in live
    assert "addEventListener('input'" in live
    assert 'setPresenceComposerFocus(true)' in live
    assert 'setPresenceComposerFocus(false)' in live
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
    assert "getContext('experimental-webgl'" in live
    assert 'curl(' in live
    assert 'createPresenceCanvas2D' in live
    assert 'class="eidolon-presence-live"' in html
    assert 'function startEidolonPresence' in live
    assert 'function refreshEidolonPresenceMarks' in live
    assert 'function pruneDetachedPresenceMarks' in live
    assert 'function syncEidolonPresenceMotion' in live
    assert 'data-presence-engine' in live
    assert "setAttribute('data-presence-engine'" in live
    assert "kind: 'webgl'" in live
    assert "kind: 'canvas2d'" in live
    assert "'still'" in live


def _phase_knobs(live, name):
    match = re.search(
        rf'{name}:\s*\{{\s*warp:\s*([0-9.]+),\s*pulse:\s*([0-9.]+),\s*mote:\s*([0-9.]+),\s*gaze:\s*([0-9.]+),\s*drift:\s*([0-9.]+),\s*churn:\s*([0-9.]+),\s*rhythm:\s*([0-9.]+),\s*mode:\s*([0-9.]+)',
        live,
    )
    assert match, name
    return {
        'warp': float(match.group(1)),
        'pulse': float(match.group(2)),
        'mote': float(match.group(3)),
        'gaze': float(match.group(4)),
        'drift': float(match.group(5)),
        'churn': float(match.group(6)),
        'rhythm': float(match.group(7)),
        'mode': float(match.group(8)),
    }


def test_presence_idle_motion_is_readable_at_mark_size():
    live = PRESENCE_JS.read_text(encoding='utf-8')
    idle = _phase_knobs(live, 'idle')
    denkt = _phase_knobs(live, 'denkt')
    arbeitet = _phase_knobs(live, 'arbeitet')
    antwortet = _phase_knobs(live, 'antwortet')
    assert idle['warp'] >= 0.3
    assert idle['pulse'] >= 0.7
    assert idle['mote'] >= 0.75
    assert denkt['warp'] > idle['warp']
    assert arbeitet['warp'] > denkt['warp']
    assert antwortet['warp'] < denkt['warp']
    assert '0.010 + move * 0.036' not in live
    assert 'filament' in live
    assert 'uDrift' in live
    assert 'uChurn' in live
    assert 'uRhythm' in live
    assert 'loadPresenceTextureImage' in live
    assert "PRESENCE_STILL_PNG = '/assets/media/eidolon-presence.png'" in live
    assert 'presenceTextureUrl' in live
    assert 'replacePresenceCanvas' in live
    assert 'presenceWebGLUsable' in live


def test_presence_three_moments_have_distinct_signatures():
    live = PRESENCE_JS.read_text(encoding='utf-8')
    css = PRESENCE_CSS.read_text(encoding='utf-8')
    shell = APP_SHELL_JS.read_text(encoding='utf-8')
    html = _html()
    schreibt = _phase_knobs(live, 'schreibt')
    denkt = _phase_knobs(live, 'denkt')
    antwortet = _phase_knobs(live, 'antwortet')
    idle = _phase_knobs(live, 'idle')
    assert schreibt['mode'] == 1
    assert denkt['mode'] == 2
    assert antwortet['mode'] == 4
    assert schreibt['drift'] > denkt['drift']
    assert schreibt['drift'] > antwortet['drift']
    assert schreibt['churn'] < denkt['churn']
    assert antwortet['churn'] < denkt['churn']
    assert denkt['rhythm'] > antwortet['rhythm'] > schreibt['rhythm']
    assert antwortet['gaze'] > denkt['gaze']
    assert idle['warp'] < denkt['warp']
    assert idle['churn'] < denkt['churn']
    assert idle['drift'] < schreibt['drift']
    assert "turn === 'idle' && presenceFocusComposer" in live
    assert "el.setAttribute('data-presence-phase', visual)" in live
    assert "el.classList.toggle(cls, cls === 'is-' + visual)" in live
    assert 'is-schreibt' in live and 'is-denkt' in live and 'is-antwortet' in live
    assert 'isWrite' in live and 'isThink' in live and 'isSpeak' in live
    assert 'horiz' in live
    assert 'mode === 1' in live
    assert 'mode === 2 || mode === 3' in live
    assert 'mode === 4' in live
    assert "phase === 'schreibt'" in live
    assert '[data-presence-phase="schreibt"]' in css
    assert '[data-presence-phase="denkt"]' in css
    assert '[data-presence-phase="antwortet"]' in css
    assert 'data-presence-phase="idle"' in html
    assert "Eidolon achtet auf die Eingabe" in live
    assert "Eidolon denkt" in live
    assert "Eidolon antwortet" in live
    assert "Eidolon achtet auf die Eingabe" in shell
    assert "setChatAgentStatus('arbeitet'" not in CHAT_UI_JS.read_text(encoding='utf-8')


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
    assert "setPresenceEngineAttr(mark.root, 'still')" in live


def test_presence_sits_above_composer_not_on_transcript_rows():
    css = PRESENCE_CSS.read_text(encoding='utf-8')
    thread = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'chat' / 'chat-thread.css'
    thread_css = thread.read_text(encoding='utf-8')
    rail = SESSION_RAIL_CSS.read_text(encoding='utf-8')
    mobile = MOBILE_CSS.read_text(encoding='utf-8')
    js = CHAT_UI_JS.read_text(encoding='utf-8')
    html = _html()
    assert 'max-width: 56px' in css
    assert 'max-height: 56px' in css
    assert 'max-width: 48px' in css
    assert 'width: 42px' in css
    assert 'display: block' in css
    assert '.eidolon-presence-turn' not in css
    assert '.chat-composer-chrome' in thread_css
    assert '.chat-turn-presence' not in thread_css
    assert 'data-presence-host' not in thread_css
    assert 'grid-template-columns: auto minmax(0, 1fr)' not in thread_css
    assert 'max-height: min(78vh, 800px)' in rail
    assert 'overflow-y: auto' in thread_css
    assert 'min-height: 0' in thread_css.split('.chat-messages')[1].split('.chat-project-door')[0]
    assert 'flex: 0 0 auto' in thread_css.split('.chat-input-shell')[1]
    assert 'width: 36px' in mobile
    assert 'max-width: 36px' in mobile
    assert '.chat-panel-heading' in rail
    assert 'eidolon-signature hero' not in html
    assert 'chat-home-hero' not in html
    assert 'function mountChatPresenceMark' not in js
    assert 'data-presence-host' not in js
    assert 'eidolon-presence' not in js.split('function renderChatTurn')[1].split('function renderChatStatusTurn')[0]


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
    assert 'no-cache' in js.headers.get('cache-control', '').lower()
    assert 'no-store' in js.headers.get('cache-control', '').lower()
    html = _html()
    assert '/assets/eidolon-presence.js?v=20260906-phases' in html
    assert "PRESENCE_ASSET_VERSION = '20260906-phases'" in PRESENCE_JS.read_text(encoding='utf-8')
    versioned = client.get('/assets/eidolon-presence.js?v=20260906-phases')
    assert versioned.status_code == 200
    assert 'no-cache' in versioned.headers.get('cache-control', '').lower()
    assert b'PRESENCE_STILL_PNG' in versioned.content
