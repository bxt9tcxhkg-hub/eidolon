from pathlib import Path
import re
import sys
import textwrap

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import eidolon.core.llm_backend as llm_backend_mod
import agent_server
from eidolon.web_routes import ALLOWED_ASSETS, read_root_html
from eidolon.core.mesh_service import MeshService
from eidolon.workspaces.registry import WorkspaceRegistry


ROOT = Path(__file__).resolve().parents[1]


class _RenderedIndexHtml:
    def read_text(self, encoding: str = 'utf-8') -> str:
        return read_root_html(ROOT)


INDEX_HTML = _RenderedIndexHtml()
WORKSPACE_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-ui.js'
WORKSPACE_PROJECT_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-project-ui.js'
WORKSPACE_CANVAS_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-canvas-ui.js'
WORKSPACE_VIEWS_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-views-ui.js'
WORKSPACE_ELEMENT_COMPOSER_JS = ROOT / 'python' / 'eidolon' / 'web' / 'workspace-element-composer-ui.js'
APP_SHELL_JS = ROOT / 'python' / 'eidolon' / 'web' / 'app-shell.js'
CHAT_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
DASHBOARD_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'dashboard-ui.js'
GOALS_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'goals-ui.js'
ADMIN_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'admin-ui.js'
CODE_REPAIR_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'code-repair-ui.js'
HEALING_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'healing-ui.js'
SKILLS_BACKUPS_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'skills-backups-ui.js'
SETTINGS_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'settings-ui.js'
APP_SHELL_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'app-shell.css'
APP_COMPONENTS_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'app-components.css'
APP_CANVAS_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'app-canvas.css'
APP_MOBILE_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'app-mobile.css'
APP_WEB_JS = '\n'.join([p.read_text(encoding='utf-8') for p in [APP_SHELL_JS, CHAT_UI_JS, DASHBOARD_UI_JS, GOALS_UI_JS, ADMIN_UI_JS, CODE_REPAIR_UI_JS, HEALING_UI_JS, SKILLS_BACKUPS_UI_JS, SETTINGS_UI_JS]])
APP_WEB_CSS = '\n'.join([p.read_text(encoding='utf-8') for p in [APP_SHELL_CSS, APP_COMPONENTS_CSS, APP_CANVAS_CSS, APP_MOBILE_CSS]])
WORKSPACE_WEB_JS = '\n'.join([p.read_text(encoding='utf-8') for p in [WORKSPACE_JS, WORKSPACE_PROJECT_JS, WORKSPACE_CANVAS_JS, WORKSPACE_VIEWS_JS, WORKSPACE_ELEMENT_COMPOSER_JS]])
AGENT_SERVER = ROOT / 'python' / 'agent_server.py'
PROJECT_ROUTES = ROOT / 'python' / 'eidolon' / 'project_routes.py'


def test_referenced_web_assets_are_allowlisted_and_served():
    client = TestClient(agent_server.app)
    web_root = ROOT / 'python' / 'eidolon' / 'web'
    referenced_assets = set(re.findall(r'(?:src|href)="/assets/([^"]+)"', INDEX_HTML.read_text()))
    for css_path in web_root.rglob('*.css'):
        css_text = css_path.read_text(encoding='utf-8')
        for rel in re.findall(r"@import url\('./([^']+)'\)", css_text):
            referenced_assets.add((css_path.parent / rel).resolve().relative_to(web_root.resolve()).as_posix())

    missing = sorted(referenced_assets - set(ALLOWED_ASSETS))
    assert missing == []

    for asset in sorted(referenced_assets):
        response = client.get(f'/assets/{asset}')
        assert response.status_code == 200, asset
        assert response.text.strip(), asset


def test_identity_endpoint_matches_ui_contract():
    client = TestClient(agent_server.app)
    response = client.get('/identity')
    assert response.status_code == 200
    payload = response.json()
    assert payload['name'] == 'Eidolon'
    assert payload['identity']
    assert payload['product_role']
    assert payload['model']
    assert payload['provider']
    assert payload['role_count'] >= 4
    assert payload['active_role_count'] >= 1
    assert payload['defined_role_count'] >= 3
    assert {'operational', 'project', 'task', 'meta'}.issubset(set(payload['role_kinds']))


def test_bot_roles_endpoint_exposes_templates_without_claiming_they_are_active():
    client = TestClient(agent_server.app)
    response = client.get('/bots/roles')
    assert response.status_code == 200
    payload = response.json()
    summary = payload['summary']
    roles = {role['role_id']: role for role in payload['roles']}
    assert summary['total'] >= 4
    assert summary['active'] >= 1
    assert summary['defined'] >= 3
    assert roles['eidolon-core']['status'] == 'active'
    assert roles['eidolon-core']['visibility'] == 'direct'
    assert roles['eidolon-core']['instantiation_policy'] == 'always_on'
    assert roles['project-bot-template']['status'] == 'defined'
    assert roles['task-bot-template']['instantiation_policy'] == 'ephemeral_only'
    assert roles['meta-bot-template']['requires_user_approval'] is True


def test_healing_status_is_wired_and_exposes_real_check_state():
    client = TestClient(agent_server.app)
    response = client.get('/healing/status')
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] in {'running', 'stopped'}
    assert 'checks_registered' in payload
    assert 'total_checks' in payload
    assert 'nicht verdrahtet' not in payload['detail']


def test_capabilities_endpoint_uses_registry_shape():
    client = TestClient(agent_server.app)
    response = client.get('/capabilities')
    assert response.status_code == 200
    payload = response.json()
    capability_ids = {item['id'] for item in payload['capabilities']}
    assert 'browser.control' in capability_ids
    assert 'mesh.quic' in capability_ids


def test_health_does_not_claim_quic_listener_when_not_wired():
    client = TestClient(agent_server.app)
    response = client.get('/health')
    assert response.status_code == 200
    payload = response.json()
    quic = payload['components']['quic_port']
    assert quic['listening'] is False
    assert quic['status'] == 'not_wired'


def test_settings_endpoint_exposes_default_vs_stored_sources():
    client = TestClient(agent_server.app)
    original = agent_server.settings_store.get_area('ui')
    try:
        agent_server.settings_store.reset_area('ui')
        agent_server.settings_store.set('ui', 'theme', 'light')
        response = client.get('/settings')
        assert response.status_code == 200
        payload = response.json()
        assert payload['settings']['ui']['theme'] == 'light'
        assert payload['settings_meta']['ui']['theme']['source'] == 'stored'
        assert payload['settings_meta']['ui']['density']['source'] == 'default'
        assert payload['source_counts']['stored'] >= 1
    finally:
        agent_server.settings_store.set_area('ui', original)


def test_settings_validation_rejects_invalid_network_port_without_mutating_state():
    client = TestClient(agent_server.app)
    original = agent_server.settings_store.get_area('network')
    try:
        response = client.post('/settings/network', json={'http_port': 70000})
        assert response.status_code == 200
        payload = response.json()
        assert payload['ok'] is False
        assert 'zwischen 1 und 65535' in payload['error']
        assert agent_server.settings_store.get_area('network')['http_port'] == original['http_port']
    finally:
        agent_server.settings_store.set_area('network', original)


def test_settings_validation_rejects_duplicate_network_ports():
    client = TestClient(agent_server.app)
    original = agent_server.settings_store.get_area('network')
    try:
        response = client.post('/settings/network', json={'http_port': original['quic_port']})
        assert response.status_code == 200
        payload = response.json()
        assert payload['ok'] is False
        assert 'Ports müssen eindeutig sein' in payload['error']
        assert agent_server.settings_store.get_area('network') == original
    finally:
        agent_server.settings_store.set_area('network', original)


def test_settings_validation_rejects_invalid_fallback_chain():
    client = TestClient(agent_server.app)
    original = agent_server.settings_store.get_area('llm')
    try:
        response = client.post('/settings/llm', json={'fallback_chain': ['ollama', 'ollama']})
        assert response.status_code == 200
        payload = response.json()
        assert payload['ok'] is False
        assert 'keine Duplikate' in payload['error']
        assert agent_server.settings_store.get_area('llm')['fallback_chain'] == original['fallback_chain']
    finally:
        agent_server.settings_store.set_area('llm', original)


def test_code_fix_missing_target_is_honest_error_not_fake_success():
    client = TestClient(agent_server.app)
    response = client.post('/code/fix', json={'issue': 'syntax error', 'file_path': 'does-not-exist.py'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['ok'] is False
    assert payload['supported'] is False
    assert payload['applied'] is False
    assert 'Datei nicht gefunden' in payload['error']


def test_code_fix_proposal_only_is_not_reported_as_applied():
    client = TestClient(agent_server.app)
    async def fake_complete(system: str, user: str) -> str:
        return 'def noop():\n    return 1\n'
    original = agent_server.llm_backend.complete
    agent_server.llm_backend.complete = fake_complete
    response = client.post('/code/fix', json={'issue': 'improve naming', 'file_path': 'python/agent_server.py', 'dry_run': True})
    try:
        assert response.status_code == 200
        payload = response.json()
        assert payload['supported'] is True
        assert payload['applied'] is False
        assert payload['ok'] in {True, False}
        assert payload.get('validation') in {'dry_run_validated', 'no_change', None}
    finally:
        agent_server.llm_backend.complete = original


def test_code_analysis_get_compatibility_route_matches_post_contract():
    client = TestClient(agent_server.app)
    response = client.get('/code/analyze', params={'file_path': 'python/agent_server.py'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['ok'] is True
    assert payload['file'] == 'python/agent_server.py'
    assert 'analysis' in payload


def test_code_self_reflect_and_refactor_routes_are_honest_not_found_replacements():
    client = TestClient(agent_server.app)
    reflect = client.get('/code/self-reflect')
    assert reflect.status_code == 200
    reflect_payload = reflect.json()
    assert reflect_payload['ok'] is True
    assert reflect_payload['supported'] is True
    assert isinstance(reflect_payload['candidates'], list)
    assert reflect_payload['action'] == 'self_reflect'

    async def fake_complete(system: str, user: str) -> str:
        return 'def noop():\n    return 1\n'
    original = agent_server.llm_backend.complete
    agent_server.llm_backend.complete = fake_complete
    refactor = client.post('/code/refactor', json={'file_path': 'python/agent_server.py', 'dry_run': True})
    try:
        assert refactor.status_code == 200
        refactor_payload = refactor.json()
        assert refactor_payload['supported'] is True
        assert refactor_payload['action'] == 'refactor'
        assert refactor_payload['applied'] is False
    finally:
        agent_server.llm_backend.complete = original


def test_code_fix_ui_does_not_show_success_for_proposal_only_results():
    js = APP_WEB_JS
    assert "d?.change_type === 'proposal_only'" in js
    assert "showNotice(d.rationale || d.error || 'Vorschlag erstellt, nicht angewendet', 'warn')" in js
    assert "showNotice('Fix angewendet', 'success')" in js


def test_code_fix_applies_validated_python_mutation(monkeypatch):
    client = TestClient(agent_server.app)
    target = ROOT / 'python' / 'data' / 'code_fix_live_test.py'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('def greet():\n    return "hi"\n', encoding='utf-8')

    async def fake_complete(system: str, user: str) -> str:
        return textwrap.dedent('''
        ```python
        def greet():
            return "hello"
        ```
        ''').strip()

    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)
    try:
        response = client.post('/code/fix', json={
            'issue': 'Change greeting from hi to hello',
            'file_path': 'python/data/code_fix_live_test.py',
        })
        assert response.status_code == 200
        payload = response.json()
        assert payload['ok'] is True
        assert payload['supported'] is True
        assert payload['applied'] is True
        assert payload['validation'] == 'py_compile_ok'
        assert 'return "hello"' in target.read_text(encoding='utf-8')
    finally:
        if target.exists():
            target.unlink()


def test_code_self_reflect_post_apply_uses_real_mutation_pipeline(monkeypatch):
    client = TestClient(agent_server.app)
    target = ROOT / 'python' / 'data' / 'self_reflect_live_test.py'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('def value():\n    return 1\n', encoding='utf-8')

    async def fake_complete(system: str, user: str) -> str:
        return 'def value():\n    return 2\n'

    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)
    monkeypatch.setattr(agent_server, '_self_reflect_candidates', lambda limit=5: [
        {'file': 'python/data/self_reflect_live_test.py', 'maintainability': 10, 'complexity': 1, 'lines': 2, 'long_functions': []}
    ])
    try:
        response = client.post('/code/self-reflect', json={'apply': True, 'limit': 1})
        assert response.status_code == 200
        payload = response.json()
        assert payload['ok'] is True
        assert payload['applied'] is True
        assert payload['action'] == 'self_reflect'
        assert 'return 2' in target.read_text(encoding='utf-8')
    finally:
        if target.exists():
            target.unlink()


def test_settings_ui_renders_source_badges():
    html = INDEX_HTML.read_text(encoding='utf-8')
    js = APP_WEB_JS
    assert "const meta = d.settings_meta || {};" in js
    assert "source = meta.source === 'stored' ? 'gesetzt' : 'standard'" in js
    assert 'function saveSettingsArea(area, btn)' in js
    assert 'data-setting-area' in js
    assert "api('POST', '/settings/' + area" in js


def test_openai_connection_supports_oauth_via_codex_login():
    js = APP_WEB_JS
    assert 'OpenAI (ChatGPT-Login)' in js
    assert 'OpenAI-kompatibel (API-Key)' in js
    assert 'Ollama lokal' in js
    assert 'OAuth gibt es für diesen Anbieter nicht' in js
    client = TestClient(agent_server.app)
    status = client.get('/llm/connection').json()
    providers = {item['id']: item for item in status['providers']}
    assert providers['openai_oauth']['oauth_supported'] is True
    assert providers['openai']['oauth_supported'] is False
    assert providers['ollama']['oauth_supported'] is False
    assert status['openai']['auth_method'] == 'chatgpt_login'
    assert 'oauth_supported' in status['openai']
    if status['openai']['source'] == 'missing':
        assert status['openai']['oauth_supported'] is False
    else:
        assert status['openai']['oauth_supported'] is True


def test_llm_models_endpoint_returns_both_providers():
    client = TestClient(agent_server.app)
    resp = client.get('/llm/models')
    assert resp.status_code == 200
    data = resp.json()
    assert data['ok'] is True
    assert isinstance(data['ollama'], list)
    assert isinstance(data['openai'], list)
    assert len(data['openai']) > 0


def test_integrations_status_and_auth_routes_are_truthful_compatibility_paths():
    client = TestClient(agent_server.app)
    llm = client.get('/llm/connection').json()
    integrations = client.get('/integrations/status')
    assert integrations.status_code == 200
    payload = integrations.json()
    assert payload['ok'] is True
    assert payload['integrations']['openai']['auth_method'] == 'chatgpt_login'
    assert 'oauth_supported' in payload['integrations']['openai']
    assert payload['integrations']['openai_compat']['oauth_supported'] is False
    assert payload['integrations']['openai_compat']['auth_method'] == 'api_key'
    assert payload['integrations']['openai']['configured'] == llm['openai']['configured']
    assert payload['integrations']['openai']['current_provider'] == (llm['provider'] in ('openai', 'openai_oauth'))

    auth = client.post('/integrations/openai/auth')
    assert auth.status_code == 200
    auth_payload = auth.json()
    assert auth_payload['ok'] is True
    assert auth_payload['supported'] is True
    assert auth_payload['auth_method'] == 'chatgpt_login'


def test_openai_login_endpoint_can_return_real_device_flow_contract():
    client = TestClient(agent_server.app)
    original_available = llm_backend_mod._codex_available
    original_status = llm_backend_mod._codex_login_status
    original_spawn = agent_server._spawn_openai_device_login
    try:
        llm_backend_mod._codex_available = lambda: True
        llm_backend_mod._codex_login_status = lambda: {'logged_in': False, 'mode': 'none'}
        agent_server._spawn_openai_device_login = lambda: {
            'ok': True,
            'supported': True,
            'provider': 'openai',
            'auth_method': 'chatgpt_login',
            'session_id': 'sess123',
            'status': 'awaiting_browser',
            'verification_url': 'https://auth.openai.com/codex/device',
            'user_code': 'ABCD-EFGH',
            'detail': 'Öffne den Link und gib den Code ein.',
            'logged_in': False,
            'current_provider': 'ollama',
            'command': 'codex login --device-auth',
        }
        response = client.post('/integrations/openai/login')
        assert response.status_code == 200
        payload = response.json()
        assert payload['ok'] is True
        assert payload['status'] == 'awaiting_browser'
        assert payload['verification_url'] == 'https://auth.openai.com/codex/device'
        assert payload['user_code'] == 'ABCD-EFGH'
    finally:
        llm_backend_mod._codex_available = original_available
        llm_backend_mod._codex_login_status = original_status
        agent_server._spawn_openai_device_login = original_spawn


def test_llm_runtime_status_is_initialized_from_settings_store():
    configured = agent_server.settings_store.get_area('llm')
    status = agent_server.llm_backend.status()
    assert status['provider'] == configured['provider']
    assert status['model'] == configured['model']


def test_identity_ui_renders_role_truth_fields():
    js = APP_WEB_JS
    assert 'Aktive Rollen' in js
    assert 'Definierte Vorlagenrollen' in js
    assert 'Rollentypen' in js
    assert 'Aktiv wirksame Rollen' in js
    assert 'Definierte Vorlagen' in js
    assert 'active_roles' in js
    assert 'defined_roles' in js
    assert 'Lokal verbunden' in js
    assert 'Backend nicht erreichbar' in js


def test_role_registry_enforces_activation_truth():
    from eidolon.bots.role_registry import BotRoleRegistry
    registry = BotRoleRegistry(ROOT)
    payload = {
        'role_id': 'test-ephemeral-active',
        'name': 'Test Ephemeral',
        'purpose': 'Vertragstest',
        'responsibilities': ['testen'],
        'non_responsibilities': ['dauerhaft handeln'],
        'activation_triggers': ['test'],
        'autonomy_level': 'background_analysis',
        'direct_user_counterpart': False,
        'requires_user_approval': False,
        'context_sources': ['task_payload'],
        'success_metrics': ['keine Persistenz'],
        'status': 'active',
        'instantiation_policy': 'ephemeral_only',
    }
    try:
        registry.create_role(payload)
    except ValueError as exc:
        assert 'ephemeral_only' in str(exc)
    else:
        raise AssertionError('ephemeral_only role was persisted as active')


def test_skills_endpoints_mutate_real_runtime_state():
    client = TestClient(agent_server.app)
    disabled = client.post('/skills/chat/disable').json()
    assert disabled['ok'] is True
    assert disabled['enabled'] is False
    enabled_list = client.get('/skills/enabled').json()['skills']
    assert 'chat' not in {skill['name'] for skill in enabled_list}
    enabled = client.post('/skills/chat/enable').json()
    assert enabled['ok'] is True
    assert enabled['enabled'] is True
    missing = client.post('/skills/does-not-exist/enable').json()
    assert missing['ok'] is False


def test_workspace_ui_implements_distinct_views_and_hierarchy_mode():
    js = WORKSPACE_WEB_JS
    assert 'function renderBoardView()' in js
    assert 'function renderTimelineView()' in js
    assert 'function renderListView()' in js
    assert "else if (view === 'board') renderBoardView();" in js
    assert "else if (canvas.mode === 'hierarchy')" in js
    assert 'async function assignHierarchy(childId, parentId)' in js


def test_settings_ui_uses_real_area_reset_route_without_dead_modal_or_prompts():
    html = INDEX_HTML.read_text(encoding='utf-8')
    assert "data-ui-action=\"resetSettingsArea\" data-ui-args='[\"network\"]'" in html
    assert "data-ui-action=\"resetSettingsArea\" data-ui-args='[\"ui\"]'" in html
    assert 'id="settings-modal"' not in html
    assert 'saveModalSettings' not in html
    assert 'async function saveSettings()' not in html
    assert 'async function resetSettings()' not in html


def test_element_editor_supports_status_assignment_and_due_date():
    html = INDEX_HTML.read_text(encoding='utf-8')
    js = WORKSPACE_WEB_JS
    assert 'id="task-status"' in html
    assert 'id="task-assigned-to"' in html
    assert 'id="task-due-at"' in html
    assert 'value="deliverable"' in html
    assert 'value="milestone"' in html
    assert "document.getElementById('task-status').value" in js
    assert "assigned_to: document.getElementById('task-assigned-to').value.trim()" in js
    assert "due_at: document.getElementById('task-due-at').value || ''" in js


def test_mesh_service_does_not_invent_demo_peer(tmp_path):
    service = MeshService(tmp_path)
    service._discovery.broadcast_presence = lambda *args, **kwargs: None
    service._discovery.get_peers = lambda: []
    service._pairing.get_paired = lambda: {}
    peers = service.scan_peers()
    assert peers == []


def test_mesh_service_surfaces_real_paired_peer_without_claiming_connection(tmp_path):
    service = MeshService(tmp_path)
    service._discovery.broadcast_presence = lambda *args, **kwargs: None
    service._discovery.get_peers = lambda: []
    service._pairing.get_paired = lambda: {
        'peer-real': {
            'name': 'Telefon',
            'address': '192.168.0.55',
            'port': 8002,
            'public_key': 'abc',
        }
    }
    peers = service.scan_peers()
    assert len(peers) == 1
    assert peers[0].name == 'Telefon'
    assert peers[0].status == 'paired'
    assert peers[0].paired is True


def test_qr_pairing_registers_browser_device_instead_of_self_pairing(tmp_path):
    service = MeshService(tmp_path)
    result = service.create_pairing()
    self_result = service.accept_pairing(result['code'])
    assert self_result['ok'] is False
    assert 'sich selbst' in self_result['error']
    browser_result = service.accept_browser_device_pairing(
        result['code'],
        device_name='Telefon',
        peer_id='browser-device-1',
        public_key='browser-public-key',
        address='192.168.0.55',
        user_agent='dogfood',
    )
    assert browser_result['ok'] is True
    paired = service.get_paired_peers()
    assert paired[0]['peer_id'] == 'browser-device-1'
    assert paired[0]['kind'] == 'browser_device'


def test_mesh_service_filters_self_pairing_from_visible_peers(tmp_path):
    service = MeshService(tmp_path)
    service._discovery.broadcast_presence = lambda *args, **kwargs: None
    service._discovery.get_peers = lambda: []
    service._pairing.get_paired = lambda: {
        'peer-self': {
            'name': service.name,
            'address': service.get_local_ip(),
            'port': 8002,
            'public_key': service.public_key,
        }
    }
    assert service.scan_peers() == []
    assert service.get_paired_peers() == []


def test_accept_pairing_ui_does_not_show_success_on_error_payload():
    js = APP_WEB_JS
    assert "if (r?.ok === false)" in js
    assert "showNotice(r.error || 'Pairing fehlgeschlagen', 'error')" in js


def test_skills_ui_populates_both_summary_and_list_instead_of_staying_loading():
    js = APP_WEB_JS
    assert "const listEl = document.getElementById('skills-list');" in js
    assert 'if (listEl) listEl.innerHTML = rows;' in js
    assert 'if (listEl) listEl.innerHTML = err;' in js


def test_code_and_backup_buttons_are_bound_to_real_inline_flows_not_prompts():
    html = INDEX_HTML.read_text(encoding='utf-8')
    js = APP_WEB_JS
    assert 'prompt(' not in html
    assert 'confirm(' not in html
    assert 'id="code-file-path"' in html
    assert 'id="code-issue"' in html
    assert "if (d?.ok === false)" in js


def test_chat_ui_persists_messages_across_reload_in_local_storage():
    html = INDEX_HTML.read_text(encoding='utf-8')
    js = APP_WEB_JS
    assert "localStorage.getItem('eidolon-chat-messages')" in js
    assert "localStorage.setItem('eidolon-chat-messages'" in js
    assert 'function loadStoredChatMessages()' in js
    assert 'function persistChatMessages()' in js
    assert 'chatMessages = loadStoredChatMessages();' in js
    assert "localStorage.getItem('eidolon-chat-current-session')" in js
    assert "api('GET', '/chat/sessions')" in js
    assert "api('POST', '/chat/sessions'" in js
    assert "api('GET', '/chat/sessions/' + encodeURIComponent(sessionId))" in js
    assert 'class="chat-session-rail"' in html
    assert 'id="chat-session-summary"' in html
    assert 'Neue Unterhaltung' in html
    assert 'id="chat-sessions"' in html
    assert 'id="chat-session-search"' in html
    assert 'class="chat-shell"' in html
    assert '.theme-toggle { display: none; }' in APP_WEB_CSS
    assert '.nav-item .icon::before' in APP_WEB_CSS
    assert 'data-tab="chat" data-tab-target="chat"' in html
    assert 'data-tab="workspaces" data-tab-target="workspaces"><span class="icon"></span> Projektfläche' in html
    assert 'data-tab="dashboard" data-tab-target="dashboard"><span class="icon"></span> Systemstatus' in html
    assert 'data-tab="mesh" data-tab-target="mesh"><span class="icon"></span> Geräte' in html
    assert 'id="chat-active-summary"' in html
    assert 'id="chat-decision-summary"' in html
    assert 'id="chat-recent-summary"' in html
    assert 'id="eidolon-signature"' in html
    assert '<div class="theme-toggle"' not in html
    assert "document.addEventListener('click'" in js
    assert 'data-ui-action' in html
    assert 'function groupChatSessions(sessions)' in js
    assert "Keine passenden Sessions gefunden." in js
    assert "m.role === 'user' ? 'Du' : 'Eidolon'" in js
    assert 'restoreBackupById(' in js
    assert 'deleteBackupById(' in js
    assert 'armedBackupAction' in js


def test_goal_buttons_follow_allowed_transitions_and_render_real_results():
    html = INDEX_HTML.read_text(encoding='utf-8')
    js = APP_WEB_JS
    assert 'const allowed = Array.isArray(g.allowed_transitions)' in js
    assert "POST', '/api/v1/operate/goals/' + id + '/transition'" in js
    assert "renderGoalActionResult('Statuswechsel', d.data || d)" in js
    assert "renderGoalActionResult('Abgeleitete Vorschläge', payload)" in js
    assert "renderGoalActionResult('Autonomie-Zyklus', d.data || d)" in js
    assert "renderGoalActionResult('Revalidierung', d.data || d)" in js
    assert "if (d?.ok === false)" in js
    assert 'Keine Aktionen' in js
    assert 'stats.active_count ?? stats.active ?? 0' in js
    assert 'stats.done_count ?? stats.done ?? 0' in js
    assert 'goal-inline-title' in html
    assert 'toggleGoalComposer(' in js
    assert 'populateGoalComposer(' in js


def test_workspace_buttons_handle_api_errors_instead_of_silent_noops():
    js = WORKSPACE_WEB_JS
    assert "response?.ok === false" in js
    assert 'Projekt anlegen fehlgeschlagen' in js
    assert 'Element speichern fehlgeschlagen' in js
    assert 'Element löschen fehlgeschlagen' in js
    assert 'Projekt löschen fehlgeschlagen' in js
    assert 'Brainstorm fehlgeschlagen' in js
    assert 'Vorschlag übernehmen fehlgeschlagen' in js
    assert 'Verknüpfung speichern fehlgeschlagen' in js
    assert 'Hierarchie speichern fehlgeschlagen' in js
    assert 'const previous = [...from.dependencies];' in js
    assert 'const previous = child.parent_id || null;' in js


def test_project_element_create_route_persists_canvas_position_and_parent():
    source = PROJECT_ROUTES.read_text(encoding='utf-8')
    assert 'position=request.get("position", {"x": 0, "y": 0})' in source
    assert 'parent_id=request.get("parent_id")' in source


def test_backup_list_hides_test_and_dogfood_catalog_entries(tmp_path):
    service = agent_server.BackupService(tmp_path)
    service._entries = [
        {'id':'20260822_143050_test', 'timestamp':'t', 'reason':'test', 'source_dir':'src', 'backup_dir':'b1', 'size_bytes':10, 'file_count':1, 'created_by':'user', 'metadata':{}},
        {'id':'20260822_135523_test_manual', 'timestamp':'t', 'reason':'test_manual', 'source_dir':'src', 'backup_dir':'b2', 'size_bytes':10, 'file_count':1, 'created_by':'user', 'metadata':{}},
        {'id':'20260826_073350_dogfood', 'timestamp':'t', 'reason':'dogfood', 'source_dir':'src', 'backup_dir':'b3', 'size_bytes':10, 'file_count':1, 'created_by':'user', 'metadata':{}},
        {'id':'20260826_080000_manual', 'timestamp':'t', 'reason':'manual', 'source_dir':'src', 'backup_dir':'b4', 'size_bytes':20, 'file_count':2, 'created_by':'user', 'metadata':{}},
    ]
    visible = service.list_backups()
    assert [entry['id'] for entry in visible] == ['20260826_080000_manual']
    stats = service.get_stats()
    assert stats['count'] == 1
    assert stats['hidden_count'] == 3
    assert stats['total_size_bytes'] == 20


def test_workspace_context_model_exposes_agentic_workflow_fields(tmp_path):
    registry = WorkspaceRegistry(tmp_path)
    context = registry.build_context_model([
        {
            'workspace_id': 'ws_alpha',
            'topic_label': 'Eidolon Produktkern',
            'product_state': 'project_candidate',
        }
    ])
    assert context['current_context_state'] == 'project_candidate'
    assert context['current_phase'] == 'form_project'
    assert context['next_transition'] == 'promote_candidate_to_project'
    assert context['responsible_role'] == 'eidolon-core'
    assert 'verstehen' in context['workflow_loop']
    assert context['candidate_labels'] == ['Eidolon Produktkern']


def test_workspace_context_model_marks_true_empty_state_explicitly(tmp_path):
    registry = WorkspaceRegistry(tmp_path)
    context = registry.build_context_model([])
    assert context['chat_topic_count'] == 0
    assert context['project_candidate_count'] == 0
    assert context['active_project_count'] == 0
    assert context['current_context_state'] == 'no_live_context'
    assert context['current_phase'] == 'await_input'
    assert context['next_transition'] is None
    assert context['approval_state'] == 'awaiting_live_input'
    assert 'Kein aktiver Gesprächs- oder Projektkontext' in context['next_step']


def test_project_suggestions_do_not_invent_review_items_when_no_gap_exists():
    client = TestClient(agent_server.app)
    projects_file = ROOT / 'data' / 'user' / 'projects.json'
    original = projects_file.read_text(encoding='utf-8') if projects_file.exists() else None
    try:
        created = client.post('/projects', json={
            'title': 'Verifizierbares Projekt',
            'description': 'Ein klares Ergebnis ist definiert.',
            'domain': 'general',
        })
        assert created.status_code == 200
        project_id = created.json()['project']['id']
        add_deliverable = client.post(f'/projects/{project_id}/elements', json={
            'title': 'Abnahme',
            'description': 'Fertiges Ergebnis',
            'element_type': 'deliverable',
            'status': 'ready',
        })
        add_task = client.post(f'/projects/{project_id}/elements', json={
            'title': 'Implementierung läuft',
            'description': 'Aktive Arbeit',
            'element_type': 'task',
            'status': 'in_progress',
            'assigned_to': 'eidolon-core',
            'dependencies': [add_deliverable.json()['element']['id']],
        })
        assert add_deliverable.status_code == 200
        assert add_task.status_code == 200
        response = client.post(f'/projects/{project_id}/suggestions')
        assert response.status_code == 200
        suggestions = response.json()['suggestions']
        assert suggestions == []

        brainstorm = client.post(f'/projects/{project_id}/brainstorm', json={'text': ''})
        assert brainstorm.status_code == 200
        assert brainstorm.json()['suggestions'] == []
    finally:
        if original is None:
            if projects_file.exists():
                projects_file.unlink()
        else:
            projects_file.write_text(original, encoding='utf-8')


def test_pairing_connect_page_requires_manual_action():
    client = TestClient(agent_server.app)
    response = client.get('/pairing?code=TEST123&name=Phone')
    assert response.status_code == 200
    html = response.text
    assert 'Tippe auf den Button, um dieses Gerät mit Eidolon zu koppeln.' in html
    assert 'device_peer_id' in html
    assert 'device_public_key' in html
    assert 'eidolon-paired-device' in html
    assert "window.location.replace('/#chat')" in html
    assert 'Nach erfolgreicher Kopplung öffnet sich die echte mobile Eidolon-Oberfläche.' in html
    assert 'id="interaction"' not in html
    assert 'setTimeout(connect, 500);' not in html


def test_root_mobile_ui_marks_paired_device_and_uses_mobile_chat_source():
    html = INDEX_HTML.read_text(encoding='utf-8')
    js = APP_WEB_JS
    assert 'id="mobile-device-banner"' in html
    assert 'function loadMobileDeviceState()' in js
    assert "api('GET', '/mesh/pairing/paired')" in js
    assert 'Dieses Handy ist gekoppelt' in js
    assert "source: pairedDevice ? ('mobile:' + pairedDevice.peer_id) : 'chat'" in js


def test_mesh_ui_exposes_real_two_click_unpair_flow():
    html = INDEX_HTML.read_text(encoding='utf-8')
    server = (ROOT / 'python' / 'eidolon' / 'chat_and_code_routes.py').read_text(encoding='utf-8') + '\n' + AGENT_SERVER.read_text(encoding='utf-8') + '\n' + (ROOT / 'python' / 'eidolon' / 'mesh_pairing_routes.py').read_text(encoding='utf-8')
    service = (ROOT / 'python' / 'eidolon' / 'core' / 'mesh_service.py').read_text(encoding='utf-8') + '\n' + (ROOT / 'python' / 'eidolon' / 'core' / 'mesh_support.py').read_text(encoding='utf-8')
    assert '@app.delete("/mesh/pairing/paired/{peer_id}")' in server
    assert 'def unpair_peer(self, peer_id: str)' in service
    assert 'def unpair(self, peer_id: str)' in service
    js = APP_WEB_JS
    assert 'let armedUnpairPeerId = null' in js
    assert 'Entkoppeln bestätigen' in js
    assert "api('DELETE', '/mesh/pairing/paired/' + encodeURIComponent(peerId))" in js
    assert "localStorage.removeItem('eidolon-paired-device')" in js


def test_terminal_cli_exposes_pairing_and_unpair_commands_against_runtime_routes():
    cli = (ROOT / 'crates' / 'eidolon-cli' / 'src' / 'main.rs').read_text(encoding='utf-8')
    assert 'Paired {' in cli
    assert 'Pair {' in cli
    assert 'Unpair {' in cli
    assert '"/mesh/pairing/paired"' in cli
    assert '"/mesh/pairing/create"' in cli
    assert 'mesh/pairing/paired/{}' in cli


def test_terminal_cli_exposes_projects_goals_and_settings_commands_against_runtime_routes():
    cli = (ROOT / 'crates' / 'eidolon-cli' / 'src' / 'main.rs').read_text(encoding='utf-8')
    for marker in [
        'Projects {',
        'ProjectCreate {',
        'ProjectDelete {',
        'Goals {',
        'GoalCreate {',
        'GoalTransition {',
        'GoalDelete {',
        'Settings {',
        'SettingsSet {',
        'SettingsReset {',
        '"/projects"',
        '"/api/v1/operate/goals"',
        'api/v1/operate/goals/{}/transition',
        '"/settings"',
        '"/settings/{}',
        'settings/{}/reset',
    ]:
        assert marker in cli


def test_terminal_cli_exposes_real_repl_and_tui_modes():
    cli = (ROOT / 'crates' / 'eidolon-cli' / 'src' / 'main.rs').read_text(encoding='utf-8')
    cargo = (ROOT / 'crates' / 'eidolon-cli' / 'Cargo.toml').read_text(encoding='utf-8')
    for marker in [
        'Repl {',
        'Tui {',
        'fn run_repl(port: u16)',
        'fn run_tui(port: u16)',
        'prompt_line(',
        'EnterAlternateScreen',
        'LeaveAlternateScreen',
        'crossterm = "0.28"',
        'KeyCode::Char(\'c\') if tab == TuiTab::Chat',
        'KeyCode::Char(\'n\') if tab == TuiTab::Projects',
        'KeyCode::Char(\'e\') if tab == TuiTab::Settings',
    ]:
        assert marker in (cli + '\n' + cargo)


def test_terminal_cli_exposes_generic_api_command_for_runtime_parity():
    cli = (ROOT / 'crates' / 'eidolon-cli' / 'src' / 'main.rs').read_text(encoding='utf-8')
    for marker in [
        'Api {',
        'fn api(port: u16, method: &str, path: &str, body: Option<&str>)',
        'api <METHOD> <PATH> [JSON]',
    ]:
        assert marker in cli


def test_mesh_service_rejects_self_pairing_instead_of_claiming_success(tmp_path):
    service = MeshService(tmp_path)
    created = service.create_pairing()
    result = service.accept_pairing(created['code'])
    assert result['ok'] is False
    assert 'nicht mit sich selbst koppeln' in result['error']
    assert service.get_paired_peers() == []


def test_web_ui_has_mobile_navigation_markup():
    html = INDEX_HTML.read_text(encoding='utf-8')
    assert '<div class="mobile-bar">' in html
    assert 'id="mobile-more-sheet"' in html
    assert 'pointer-events: none;' in APP_WEB_CSS
    assert 'bottom: 72px;' in APP_WEB_CSS


def test_primary_inline_handlers_exist():
    html = INDEX_HTML.read_text(encoding='utf-8')
    js = WORKSPACE_WEB_JS
    shell = APP_WEB_JS
    all_code = html + '\n' + js + '\n' + shell
    expected = {
        'openTabSettings',
        'toggleGoalComposer',
        'submitGoalForm',
        'loadGoalLog',
        'toggleMobileMore',
        'openElementForm',
        'closeTaskForm',
        'submitTaskForm',
        'deleteCurrentComposerElement',
        'saveProjectTitle',
        'saveProjectStatus',
        'archiveCurrentProject',
        'updatePlanElement',
        'reorderPlanElements',
        'archivePlanElement',
        'dropPlanElement',
    }
    defined = set(re.findall(r'function\s+([A-Za-z0-9_]+)\s*\(', all_code))
    missing = sorted(expected - defined)
    assert not missing, f'Missing handlers: {missing}'


def test_dashboard_uses_real_health_components_and_runtime_shapes():
    js = APP_WEB_JS
    assert "document.getElementById('dash-components')" in js
    assert 'comps.quic_port.status' in js
    assert 'comps.self_healing.status' in js
    assert 'const runtime = d.process || {};' in js
    assert 'const system = d.system || {};' in js
    assert 'const areas = d.areas || {};' in js


def test_chat_ui_does_not_fall_back_to_fake_success_copy():
    html = INDEX_HTML.read_text(encoding='utf-8')
    js = APP_WEB_JS
    assert "'Antwort erhalten'" not in html
    assert "Fehler: Keine Modellantwort erhalten" in js
    assert 'Bereit, wenn du es bist.' in js
    assert 'renderChat(); loadOperateView(); loadPodsView(); loadWorkspaces();' in js


def test_chat_ui_renders_live_runtime_context_contract():
    html = INDEX_HTML.read_text(encoding='utf-8')
    js = APP_WEB_JS
    assert 'id="chat-context-state"' in html
    assert 'id="chat-intent-mode"' in html
    assert 'id="chat-next-step"' in html
    assert "async function loadChatRuntimeContext(sessionId)" in js
    assert "'/chat/context?session_id=' + encodeURIComponent(sessionId)" in js
    assert 'renderChatRuntimeContext(r.runtime_context);' in js


def test_chat_is_initial_active_surface_and_header():
    html = INDEX_HTML.read_text(encoding='utf-8')
    assert '<h2 id="page-title">Eidolon</h2>' in html
    assert 'Sprich den Kern an — oder setze reale Arbeit fort.' in html
    assert '<div id="panel-chat" class="tab-panel active chat-is-idle">' in html
    assert 'id="chat-idle-prompt"' in html
    assert 'id="operate-idle-empty"' in html
    assert '<div id="panel-operate" class="tab-panel operate-is-idle">' in html
    assert '<div id="panel-operate" class="tab-panel active">' not in html
    assert 'id="panel-workspaces"' in html
    assert 'class="tab-panel workspaces-is-idle"' in html
    assert '<div id="panel-dashboard" class="tab-panel">' in html
    assert '<div id="panel-mesh" class="tab-panel">' in html
    assert "let currentTab = 'chat';" in APP_SHELL_JS.read_text(encoding='utf-8')
    assert 'function syncNavHighlight(tabId)' in APP_SHELL_JS.read_text(encoding='utf-8')
    assert "window.addEventListener('hashchange'" in APP_SHELL_JS.read_text(encoding='utf-8')
    assert "const initialTab = (window.location.hash || '#chat').replace('#', '');" in APP_SHELL_JS.read_text(encoding='utf-8')
    assert "operate: { title: 'Arbeit'" in APP_SHELL_JS.read_text(encoding='utf-8')
    assert 'data-tab="operate" data-tab-target="operate">' in html
    assert 'data-tab-target="operate">Arbeit öffnen' in html


def test_project_planning_surface_is_generic_and_editable():
    html = INDEX_HTML.read_text(encoding='utf-8')
    js = WORKSPACE_WEB_JS
    assert '<option value="board" selected>Planung</option>' in html
    assert "if (viewMode) viewMode.value = 'board';" in js
    assert "['in_progress', 'In Arbeit']" in js
    assert "['planned', 'Geplant']" in js
    assert "['done', 'Fertig']" in js
    assert "['archived', 'Archiv']" in js
    assert 'class="plan-card-title"' in js
    assert 'data-plan-field="title"' not in js
    assert 'id="task-title"' in html
    assert 'data-plan-menu' in js
    assert 'data-plan-field="status"' in js
    assert 'data-plan-field="parent_id"' in js
    assert 'data-plan-archive' in js
    assert 'data-plan-drop' in js
    assert "/projects/' + state.currentProjectId + '/elements/reorder'" in js
    assert "status: 'archived'" in js
    assert 'id="ws-planning-scaffold"' in html
    assert 'id="ws-planning-scaffold-board"' in html
    assert 'data-plan-column="idea"' in html
    assert 'data-plan-column="archived"' in html
    assert 'overview.work_kernel' in js
    assert 'generic_slots' in js
    assert 'data-slot="context"' in html
    assert 'data-slot="next"' in html
    assert 'data-slot="inbox"' in html
    assert 'id="ws-project-title-edit"' in html
    assert 'id="ws-project-status-edit"' in html
    assert 'data-ui-action="saveProjectTitle"' in html
    assert 'data-ui-action="archiveCurrentProject"' in html
    assert 'id="task-parent-id"' in html
    assert 'Mehr Flächen' in html
    assert 'id="chat-operate-actions"' in html
    assert 'id="chat-formation"' in html
    assert 'Mehr Flächen' in html
    assert 'nav-group-title">Betrieb</div>' in html
    assert 'nav-group-title">Technik</div>' in html
    assert 'Slots, keine Domänen-Pakete' in html
    assert 'keine fest verdrahteten Training-, Instagram- oder Reise-Flächen' in html
    assert 'data-tab="training"' not in html
    assert 'data-tab="instagram"' not in html
    assert 'data-tab="reise"' not in html
    assert 'data-tab="travel"' not in html


def test_rust_runtime_is_quarantined_from_python_live_ports():
    runtime_config = (ROOT / 'crates' / 'eidolon-runtime' / 'src' / 'config' / 'mod.rs').read_text(encoding='utf-8')
    runtime_main = (ROOT / 'crates' / 'eidolon-runtime' / 'src' / 'main.rs').read_text(encoding='utf-8')
    runtime_lib = (ROOT / 'crates' / 'eidolon-runtime' / 'src' / 'lib.rs').read_text(encoding='utf-8')
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    architecture = (ROOT / 'ARCHITECTURE.md').read_text(encoding='utf-8')
    assert 'PYTHON_LIVE_HTTP_PORT: u16 = 8002' in runtime_config
    assert 'fn uses_python_live_port' in runtime_config
    assert 'http_port: 18002' in runtime_config
    assert 'http_port: 18002' in runtime_main
    assert 'uses_python_live_port()' in runtime_lib
    assert 'Einzige live Runtime' in architecture or 'einzige live Runtime' in architecture
    assert 'Python FastAPI ist der einzige live Produktserver' in readme
    cli = (ROOT / 'crates' / 'eidolon-cli' / 'src' / 'main.rs').read_text(encoding='utf-8')
    assert 'default_value = "8002"' in cli


def test_project_element_reorder_persists_list_order(tmp_path, monkeypatch):
    from eidolon.workspaces.project_service import ProjectService

    service = ProjectService(tmp_path)
    project = service.create_project('Reorder', 'List order is modeled', 'general')
    first = service.add_element(project.id, title='Alpha', status='planned')
    second = service.add_element(project.id, title='Beta', status='planned')
    third = service.add_element(project.id, title='Gamma', status='in_progress')
    monkeypatch.setattr(agent_server, 'project_service', service, raising=False)
    client = TestClient(agent_server.app)
    response = client.post(f'/projects/{project.id}/elements/reorder', json={'element_ids': [third.id, first.id, second.id]})
    assert response.status_code == 200
    payload = response.json()
    assert payload['ok'] is True
    titles = [item['title'] for item in payload['project']['elements']]
    assert titles == ['Gamma', 'Alpha', 'Beta']
    persisted = service.get_project(project.id)
    assert [item.title for item in persisted.elements] == ['Gamma', 'Alpha', 'Beta']


def test_project_status_and_element_archive_persist(tmp_path, monkeypatch):
    from eidolon.workspaces.project_service import ProjectService

    service = ProjectService(tmp_path)
    project = service.create_project('Status persist', 'Real project status', 'general')
    first = service.add_element(project.id, title='Alpha', status='planned')
    second = service.add_element(project.id, title='Related', status='idea')
    monkeypatch.setattr(agent_server, 'project_service', service, raising=False)
    client = TestClient(agent_server.app)

    renamed = client.put(f'/projects/{project.id}', json={'title': 'Status persist renamed', 'status': 'in_progress'})
    assert renamed.status_code == 200
    assert renamed.json()['project']['title'] == 'Status persist renamed'
    assert renamed.json()['project']['status'] == 'in_progress'

    archived_project = client.put(f'/projects/{project.id}', json={'status': 'archived'})
    assert archived_project.status_code == 200
    assert archived_project.json()['project']['status'] == 'archived'
    assert service.get_project(project.id).status == 'archived'

    grouped = client.put(f'/projects/{project.id}/elements/{first.id}', json={'parent_id': second.id, 'status': 'in_progress'})
    assert grouped.status_code == 200
    assert grouped.json()['element']['parent_id'] == second.id
    assert grouped.json()['element']['status'] == 'in_progress'

    archived = client.put(f'/projects/{project.id}/elements/{first.id}', json={'status': 'archived'})
    assert archived.status_code == 200
    assert archived.json()['element']['status'] == 'archived'
    assert service.get_project(project.id).elements[0].status == 'archived'

    dropped = client.delete(f'/projects/{project.id}/elements/{first.id}')
    assert dropped.status_code == 200
    remaining = service.get_project(project.id)
    assert [item.id for item in remaining.elements] == [second.id]


def test_chat_is_operate_execute_door():
    html = INDEX_HTML.read_text(encoding='utf-8')
    js = APP_WEB_JS
    operate_js = (ROOT / 'python' / 'eidolon' / 'web' / 'operate-actions-ui.js').read_text(encoding='utf-8')
    assert 'id="chat-operate-actions"' in html
    assert 'id="chat-decision-summary"' in html
    assert 'function renderChatOperateDoor' in js
    assert 'function renderChatFormation' in js
    assert "applyChatFormation" in js
    assert "'/workspaces/formation'" in js
    assert 'Daraus ein Projekt machen?' in js
    assert 'Ja, übernehmen' in js
    assert 'Nein, nur im Chat' in js
    assert 'seed_board' in js
    assert "resolveOperateApproval" in js
    assert "advanceOperateRun" in js
    assert "resolveOperateBlocker" in js
    assert "'/api/v1/runs/' + runId + '/approval/'" in operate_js
    assert "'/api/v1/runs/' + runId + '/advance'" in operate_js
    assert 'refreshOperateSurfaces' in operate_js
    assert 'loadChatLandingSummary' in operate_js
    assert 'Mehr Flächen' in html
    assert 'nav-group-title">System</div>' not in html


def test_doc_hierarchy_declares_spec_as_product_truth():
    agent = (ROOT / 'AGENT.md').read_text(encoding='utf-8')
    boundaries = (ROOT / 'docs' / 'repo-boundaries.md').read_text(encoding='utf-8')
    roadmap = (ROOT / 'ROADMAP.md').read_text(encoding='utf-8')
    mapping = (ROOT / 'docs' / 'eidolon-spec-to-system-mapping.md').read_text(encoding='utf-8')
    assert 'Sie ist nicht die Produktspezifikation' in agent
    assert 'Produkt-Soll' in agent
    assert 'Aktive Produktwahrheit' in boundaries
    assert 'Quellwahrheit für **heutigen Projektfortschritt**' in roadmap
    assert 'Fresh evidence basis' in mapping
    assert 'live `python -m pytest -q` → passes' in mapping
