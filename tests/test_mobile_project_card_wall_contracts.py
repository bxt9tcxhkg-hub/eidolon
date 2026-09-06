from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from eidolon.web_routes import read_root_html

ROOT = Path(__file__).resolve().parents[1]


class _RenderedIndexHtml:
    def read_text(self, encoding: str = 'utf-8') -> str:
        return read_root_html(ROOT)


INDEX_HTML = _RenderedIndexHtml()
WORKSPACE_VIEWS_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-views-ui.js'
WORKSPACE_PROJECT_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-project-ui.js'
COMPONENTS_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'app-components-base.css'
MOBILE_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'app-mobile.css'

PHONE_WIDTH_PX = 390
MOBILE_BREAKPOINT_PX = 768


def _media_max_width_block(css: str, max_width: int) -> str:
    pattern = re.compile(r'@media\s*\(max-width:\s*' + str(max_width) + r'px\)\s*\{', re.I)
    match = pattern.search(css)
    assert match, f'missing @media (max-width: {max_width}px)'
    start = match.end()
    depth = 1
    index = start
    while index < len(css) and depth:
        if css[index] == '{':
            depth += 1
        elif css[index] == '}':
            depth -= 1
        index += 1
    return css[start:index - 1]


def test_phone_390_is_inside_project_surface_breakpoint():
    assert PHONE_WIDTH_PX <= MOBILE_BREAKPOINT_PX


def test_mobile_projektflaeche_is_vertical_card_wall_at_390px():
    mobile = MOBILE_CSS.read_text(encoding='utf-8')
    views = WORKSPACE_VIEWS_JS.read_text(encoding='utf-8')
    html = INDEX_HTML.read_text()
    block = _media_max_width_block(mobile, MOBILE_BREAKPOINT_PX)

    assert '390px phones use the same vertical Kartenwand' in block
    assert 'flex-direction: column' in block
    assert 'overflow-x: hidden' in block
    assert 'scroll-snap-type: none' in block
    assert 'scroll-snap-type: x' not in block
    assert 'scroll-snap-align: start' not in block
    assert '.planning-wall-list' in block
    assert '.plan-card-status-chip' in block
    assert '.planning-idea-line' in block
    assert '#ws-planning-scaffold' in block
    assert 'display: none' in block
    assert '.ws-brainstorm-card' in block

    assert 'data-planning-layout="wall"' in views
    assert "matchMedia('(max-width: 768px)')" in views
    assert 'function renderPlanningWall' in views
    assert 'class="planning-board planning-wall"' in views
    assert 'plan-card-status-chip' in views
    assert 'class="planning-wall-list"' in views
    assert 'Noch keine Karten. Schreib oben eine Idee.' in views
    assert 'id="ws-idea-line"' in html
    assert 'id="ws-idea-title"' in html
    assert 'Idee als Karte anlegen' in html
    assert 'data-ui-action="submitIdeaLine"' in html
    assert 'Bausteine ergänzen' not in html


def test_desktop_planning_board_keeps_horizontal_columns():
    css = COMPONENTS_CSS.read_text(encoding='utf-8')
    views = WORKSPACE_VIEWS_JS.read_text(encoding='utf-8')
    html = INDEX_HTML.read_text()
    layout_chunks = [chunk for chunk in css.split('.planning-board {')[1:]]
    assert len(layout_chunks) >= 2
    layout = layout_chunks[-1].split('}', 1)[0]
    assert 'display: flex' in layout
    assert 'flex-wrap: nowrap' in layout
    assert 'overflow-x: auto' in layout
    assert 'flex-direction: column' not in layout
    assert 'grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))' not in css

    assert 'data-planning-layout="columns"' in views
    assert 'function renderPlanningColumns' in views
    assert 'class="planning-board"' in views
    assert 'planning-column-header' in views
    for column in ('idea', 'planned', 'in_progress', 'blocked', 'done', 'archived'):
        assert 'data-plan-column="' + column + '"' in html


def test_idea_line_creates_real_project_elements():
    views = WORKSPACE_VIEWS_JS.read_text(encoding='utf-8')
    html = INDEX_HTML.read_text()
    assert 'async function submitIdeaLine' in views
    assert "api('POST', '/projects/' + state.currentProjectId + '/elements'" in views
    assert "status: 'idea'" in views
    assert "element_type: 'idea'" in views
    assert "data-enter-action=\"submitIdeaLine\"" in html
    assert "data-ui-action=\"submitIdeaLine\"" in html
    assert 'submitIdeaLine' in views.split('Object.assign(window')[1]


def test_wall_cards_expose_status_chip_and_tap_menu():
    views = WORKSPACE_VIEWS_JS.read_text(encoding='utf-8')
    css = COMPONENTS_CSS.read_text(encoding='utf-8')
    assert 'function statusChip(status)' in views
    assert 'plan-card-status-chip' in views
    assert "ws.statusLabel(status || 'idea')" in views
    assert '.plan-card-wall .plan-card-face' in views
    assert "btn.click()" in views
    assert 'Kartenmenü' in views
    assert 'plan-card-status' in views
    assert "data-open-element-id" in views
    assert '.plan-card-status-chip' in css
    assert '.plan-card-wall' in css


def test_brainstorm_is_demoted_and_lands_as_draft_cards():
    html = INDEX_HTML.read_text()
    project_js = WORKSPACE_PROJECT_JS.read_text(encoding='utf-8')
    views = WORKSPACE_VIEWS_JS.read_text(encoding='utf-8')
    assert 'id="ws-brainstorm-card"' in html
    assert 'class="card ws-brainstorm-card"' in html
    assert 'Vorschläge vom Kernel' in html
    assert 'Bausteine ergänzen' not in html
    assert html.find('id="ws-elements-card"') < html.find('id="ws-brainstorm-card"')
    assert html.find('id="ws-idea-line"') < html.find('id="brainstorm-text"')
    assert 'function draftSuggestionCard' in views
    assert 'plan-card-draft' in views
    assert '>Vorschlag</span>' in views
    assert 'data-suggestion-action="accept"' in views
    assert 'Übernehmen' in views
    assert 'renderBoardView()' in project_js
    assert 'state.brainstormData.splice(index, 1)' in project_js
