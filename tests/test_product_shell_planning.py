from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.web_routes import read_root_html


ROOT = Path(__file__).resolve().parents[1]
APP_SHELL_JS = ROOT / 'python' / 'eidolon' / 'web' / 'app-shell.js'
WORKSPACE_VIEWS_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-views-ui.js'
WORKSPACE_PROJECT_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-project-ui.js'
PROJECT_ENTITIES = ROOT / 'python' / 'eidolon' / 'workspaces' / 'project_entities.py'


class _RenderedIndexHtml:
    def read_text(self, encoding: str = 'utf-8') -> str:
        return read_root_html(ROOT)


def test_chat_is_default_entry_and_operate_is_not_a_landing_tab():
    html = _RenderedIndexHtml().read_text()
    shell = APP_SHELL_JS.read_text(encoding='utf-8')
    assert '<div id="panel-chat" class="tab-panel active">' in html
    assert 'id="panel-operate"' not in html
    assert "const LANDING_TAB = 'chat';" in shell
    assert "if (!raw || raw === 'operate' || !PAGES[raw]) return LANDING_TAB;" in shell
    assert "let currentTab = 'chat';" in shell
    assert 'chat: { title:' in shell
    assert 'operate: { title:' not in shell


def test_primary_nav_is_chat_work_and_essentials_not_tab_zoo():
    html = _RenderedIndexHtml().read_text()
    start = html.split('Start & Arbeit', 1)[1].split('Essentiell', 1)[0]
    assert 'data-tab="chat"' in start
    assert 'data-tab="workspaces"' in start
    assert 'data-tab="dashboard"' not in start
    assert 'data-tab="goals"' not in start
    assert 'data-tab="pods"' not in start
    assert 'Weitere Flächen' in html
    sidebar = html.split('<aside class="sidebar">', 1)[1].split('</aside>', 1)[0]
    assert sidebar.count('nav-group-title') == 2
    assert sidebar.count('class="nav-disclosure"') == 1
    mobile_bar = html.split('class="mobile-bar"', 1)[1].split('mobile-more-sheet', 1)[0]
    assert mobile_bar.count('data-tab-target=') == 2
    assert 'data-tab-target="chat"' in mobile_bar
    assert 'data-tab-target="workspaces"' in mobile_bar


def test_project_planning_board_is_default_and_wires_real_mutations():
    html = _RenderedIndexHtml().read_text()
    views = WORKSPACE_VIEWS_JS.read_text(encoding='utf-8')
    project_ui = WORKSPACE_PROJECT_JS.read_text(encoding='utf-8')
    entities = PROJECT_ENTITIES.read_text(encoding='utf-8')
    assert '<option value="board" selected>Planung</option>' in html
    assert "if (viewMode) viewMode.value = 'board';" in project_ui
    assert "label: 'Geplant'" in views
    assert "label: 'In Arbeit'" in views
    assert "label: 'Erledigt'" in views
    assert 'Verwandt' in views
    assert "api('PUT', '/projects/' + state.currentProjectId + '/elements/' + elementId, payload)" in views
    assert "api('PUT', '/projects/' + state.currentProjectId + '/elements/' + current.id, { sort_order: swapIdx })" in views
    assert "api('DELETE', '/projects/' + state.currentProjectId + '/elements/' + elementId)" in views
    assert "data-plan-action=\"toggle-done\"" in views
    assert "data-plan-field=\"title\"" in views
    assert "data-plan-field=\"priority\"" in views
    assert 'sort_order: int = 0' in entities


def test_situation_card_slots_are_scaffolding_only():
    html = _RenderedIndexHtml().read_text()
    assert 'id="ws-situation-slots"' in html
    assert 'id="chat-situation-slots"' in html
    assert 'data-slot-kind="generic"' in html
    assert 'keine Trainings-, Posting- oder Reise-Demodaten' in html
    assert 'instagram' not in html.lower()
    assert 'booking' not in html.lower()


def test_project_element_mutations_persist_sort_order_title_priority_and_status():
    client = TestClient(agent_server.app)
    created = client.post('/projects', json={
        'title': 'Planungsbrett-Vertrag',
        'description': 'Echte Mutationsprüfung',
        'domain': 'general',
    })
    assert created.status_code == 200
    project_id = created.json()['project']['id']
    try:
        first = client.post(f'/projects/{project_id}/elements', json={
            'title': 'Erste Karte',
            'status': 'planned',
            'priority': 2,
            'element_type': 'task',
        })
        second = client.post(f'/projects/{project_id}/elements', json={
            'title': 'Zweite Karte',
            'status': 'planned',
            'priority': 1,
            'element_type': 'task',
        })
        assert first.status_code == 200
        assert second.status_code == 200
        first_id = first.json()['element']['id']
        second_id = second.json()['element']['id']
        assert first.json()['element']['sort_order'] == 0
        assert second.json()['element']['sort_order'] == 1

        renamed = client.put(f'/projects/{project_id}/elements/{first_id}', json={'title': 'Umbenannt'})
        prioritized = client.put(f'/projects/{project_id}/elements/{first_id}', json={'priority': 5})
        reordered = client.put(f'/projects/{project_id}/elements/{first_id}', json={'sort_order': 1})
        completed = client.put(f'/projects/{project_id}/elements/{second_id}', json={'status': 'done', 'sort_order': 0})
        assert renamed.json()['element']['title'] == 'Umbenannt'
        assert prioritized.json()['element']['priority'] == 5
        assert reordered.json()['element']['sort_order'] == 1
        assert completed.json()['element']['status'] == 'done'

        loaded = client.get(f'/projects/{project_id}').json()['project']
        by_id = {item['id']: item for item in loaded['elements']}
        assert by_id[first_id]['title'] == 'Umbenannt'
        assert by_id[first_id]['priority'] == 5
        assert by_id[first_id]['sort_order'] == 1
        assert by_id[second_id]['status'] == 'done'
        assert by_id[second_id]['sort_order'] == 0

        deleted = client.delete(f'/projects/{project_id}/elements/{second_id}')
        assert deleted.status_code == 200
        remaining = client.get(f'/projects/{project_id}').json()['project']['elements']
        assert [item['id'] for item in remaining] == [first_id]
    finally:
        client.delete(f'/projects/{project_id}')
