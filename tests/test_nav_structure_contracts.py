from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from eidolon.web.nav_contract import (
    CHAT_IDLE_FORBIDDEN_IDS,
    CHAT_IDLE_REQUIRED_IDS,
    HONESTY_HINTS,
    MORE_GROUPS,
    MORE_SUMMARY,
    PRIMARY_TABS,
    all_page_entries,
    honesty_hint,
    inject_nav,
    iter_more_items,
    more_surface_tabs,
    primary_tabs,
)
from eidolon.web_routes import read_root_html


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL_JS = (ROOT / 'python' / 'eidolon' / 'web' / 'app-shell.js').read_text(encoding='utf-8')
INDEX_HEAD = (ROOT / 'python' / 'eidolon' / 'web' / 'fragments' / 'index-head.html').read_text(encoding='utf-8')
INDEX_FOOTER = (ROOT / 'python' / 'eidolon' / 'web' / 'fragments' / 'index-healing-footer.html').read_text(encoding='utf-8')


def _html() -> str:
    return read_root_html(ROOT)


def _panel(html: str, panel_id: str) -> str:
    start = html.find(f'id="{panel_id}"')
    assert start > 0, panel_id
    nxt = html.find('id="panel-', start + 8)
    return html[start: nxt if nxt > 0 else start + 4000]


def test_nav_contract_everyday_path_is_chat_projekte_arbeit():
    assert primary_tabs() == ('chat', 'workspaces', 'operate')
    assert [item['nav_label'] for item in PRIMARY_TABS] == ['Chat', 'Projekte', 'Arbeit']
    assert [item['mobile_label'] for item in PRIMARY_TABS] == ['Chat', 'Projekte', 'Arbeit']
    assert MORE_SUMMARY == 'Mehr'


def test_nav_contract_keeps_system_surfaces_under_mehr():
    tabs = more_surface_tabs()
    for required in (
        'dashboard',
        'healing',
        'skills',
        'mesh',
        'code',
        'execution',
        'pods',
        'settings',
    ):
        assert required in tabs
    assert 'chat' not in tabs
    assert 'workspaces' not in tabs
    assert 'operate' not in tabs
    assert 'llm' not in tabs
    assert any(item.get('settings_area') == 'llm' for item in iter_more_items())


def test_k3_catalog_and_pod_ledger_keep_honest_mehr_labels():
    skills = next(item for item in iter_more_items() if item['tab'] == 'skills')
    pods = next(item for item in iter_more_items() if item['tab'] == 'pods')
    assert skills['honesty'] == 'catalog'
    assert pods['honesty'] == 'ledger'
    assert honesty_hint(skills) == HONESTY_HINTS['catalog'] == 'nicht ausführbar'
    assert honesty_hint(pods) == HONESTY_HINTS['ledger'] == 'keine eigenen Prozesse'
    assert 'Katalog' in skills['nav_label']
    assert 'Protokoll' in pods['nav_label']


def test_rendered_sidebar_primary_excludes_system_panels():
    html = _html()
    primary_block = html.split('<!--EIDOLON_NAV_SIDEBAR_PRIMARY_BEGIN-->')[1].split(
        '<!--EIDOLON_NAV_SIDEBAR_PRIMARY_END-->'
    )[0]
    more_block = html.split('<!--EIDOLON_NAV_SIDEBAR_MORE_BEGIN-->')[1].split(
        '<!--EIDOLON_NAV_SIDEBAR_MORE_END-->'
    )[0]
    assert '<summary>Mehr</summary>' in html
    assert 'Mehr Flächen' not in html
    for item in PRIMARY_TABS:
        assert f'data-tab="{item["tab"]}"' in primary_block
        assert f'> {item["nav_label"]}</li>' in primary_block
        assert f'data-tab="{item["tab"]}"' not in more_block
    for tab in more_surface_tabs():
        assert f'data-tab="{tab}"' not in primary_block
        assert f'data-tab="{tab}"' in more_block
    assert 'class="chat-session-rail"' in primary_block
    assert 'nav-group-title">Betrieb</div>' in more_block
    assert 'nav-group-title">Technik</div>' in more_block
    assert 'KI-Verbindung' in more_block
    assert 'data-settings-area="llm"' in more_block


def test_mobile_bar_is_everyday_path_plus_mehr():
    html = _html()
    bar = html.split('<!--EIDOLON_NAV_MOBILE_BAR_BEGIN-->')[1].split('<!--EIDOLON_NAV_MOBILE_BAR_END-->')[0]
    sheet = html.split('<!--EIDOLON_NAV_MOBILE_MORE_BEGIN-->')[1].split('<!--EIDOLON_NAV_MOBILE_MORE_END-->')[0]
    labels = re.findall(r'<span>([^<]+)</span>', bar)
    assert labels == ['Chat', 'Projekte', 'Arbeit', 'Mehr']
    assert 'data-ui-action="toggleMobileMore"' in bar
    for tab in more_surface_tabs():
        assert f'data-tab="{tab}"' not in bar
        assert f'data-tab-target="{tab}"' in sheet
    assert 'data-nav-group="betrieb"' in sheet
    assert 'data-nav-group="technik"' in sheet
    assert 'nicht ausführbar' in sheet
    assert 'keine eigenen Prozesse' in sheet
    assert 'data-settings-area="llm"' in sheet
    assert 'Fähigkeiten-Katalog' in sheet
    assert 'Helfer-Protokoll' in sheet


def test_fragment_markers_exist_so_nav_is_injected():
    for marker in (
        '<!--EIDOLON_NAV_SIDEBAR_PRIMARY_BEGIN-->',
        '<!--EIDOLON_NAV_SIDEBAR_PRIMARY_END-->',
        '<!--EIDOLON_SESSION_RAIL_BEGIN-->',
        '<!--EIDOLON_SESSION_RAIL_END-->',
        '<!--EIDOLON_NAV_SIDEBAR_MORE_BEGIN-->',
        '<!--EIDOLON_NAV_SIDEBAR_MORE_END-->',
        '<summary>Mehr</summary>',
    ):
        assert marker in INDEX_HEAD
    for marker in (
        '<!--EIDOLON_NAV_MOBILE_BAR_BEGIN-->',
        '<!--EIDOLON_NAV_MOBILE_BAR_END-->',
        '<!--EIDOLON_NAV_MOBILE_MORE_BEGIN-->',
        '<!--EIDOLON_NAV_MOBILE_MORE_END-->',
    ):
        assert marker in INDEX_FOOTER
    raw = INDEX_HEAD + INDEX_FOOTER
    assert 'data-tab="dashboard"' not in raw
    assert 'data-tab="skills"' not in raw
    injected = inject_nav(raw)
    assert 'data-tab="dashboard"' in injected
    assert 'Fähigkeiten-Katalog' in injected


def test_shell_page_titles_match_nav_contract():
    pages = all_page_entries()
    for tab, item in pages.items():
        assert f"{tab}: {{ title: '{item['title']}'" in APP_SHELL_JS
        assert item['subtitle'] in APP_SHELL_JS
    assert "showTab(tabId, options)" in APP_SHELL_JS
    assert 'settingsArea' in APP_SHELL_JS
    assert 'dataset.settingsArea' in APP_SHELL_JS
    assert "let currentTab = 'chat';" in APP_SHELL_JS
    assert "const primary = ['chat', 'workspaces', 'operate'];" in APP_SHELL_JS


def test_chat_idle_stays_a_door_without_system_walls():
    html = _html()
    chat = _panel(html, 'panel-chat')
    assert 'chat-is-idle' in chat
    for required in CHAT_IDLE_REQUIRED_IDS:
        assert f'id="{required}"' in chat
    for forbidden in CHAT_IDLE_FORBIDDEN_IDS:
        assert f'id="{forbidden}"' not in chat
    assert 'Capability' not in chat
    assert 'Health-Check' not in chat
    assert 'Healing' not in chat
    for forbidden in ('health-badge', 'capabilities-summary', 'llm-connection-status'):
        assert f'id="{forbidden}"' in html
        assert f'id="{forbidden}"' not in chat


def test_mehr_groups_cover_betrieb_and_technik():
    assert [group['id'] for group in MORE_GROUPS] == ['betrieb', 'technik']
    betrieb = {item['nav_label'] for item in MORE_GROUPS[0]['items']}
    technik = {item['nav_label'] for item in MORE_GROUPS[1]['items']}
    assert {'Einstellungen', 'KI-Verbindung', 'Geräte (Mesh)', 'Identität', 'Sicherungen'} <= betrieb
    assert {
        'Systemstatus',
        'Healing',
        'Fähigkeiten-Katalog',
        'Code-Reparatur',
        'Autonomie-Ziele',
        'Helfer-Protokoll',
        'Ausführung',
    } <= technik
