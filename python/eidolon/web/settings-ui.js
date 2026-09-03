// Settings
async function loadSettings() {
    try {
        const d = await api('GET', '/settings');
        const areas = ['network', 'llm', 'autonomy', 'privacy', 'ui'];
        const settings = d.settings || {};
        window.__lastSettings = settings;
        const meta = d.settings_meta || {};
        areas.forEach(a => { const el = document.getElementById('settings-' + a); if (el) el.innerHTML = renderSettingsArea(a, settings, meta[a] || {}); });
        // LLM-Modelle und -Actions initialisieren
        const provider = (settings.llm && settings.llm.provider) || 'ollama';
        await loadModelList(provider);
        await updateLLMActions(provider);
        await loadLLMConnection();
    } catch (e) { ['network', 'llm', 'autonomy', 'privacy', 'ui'].forEach(a => { const el = document.getElementById('settings-' + a); if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>'; }); }
}
function settingField(area, key, value, meta) {
    const source = meta.source === 'stored' ? 'gesetzt' : 'standard';
    const badgeClass = meta.source === 'stored' ? 'ok' : 'info';
    const id = 'setting-' + area + '-' + key;
    const boolValue = value === true || value === false;
    const numberValue = typeof value === 'number';
    let input = '';
    if (key === 'provider') {
        input = '<select id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '" onchange="onProviderChange(this)"><option value="ollama"' + (value === 'ollama' ? ' selected' : '') + '>Ollama lokal</option><option value="openai_oauth"' + (value === 'openai_oauth' ? ' selected' : '') + '>OpenAI (Login)</option></select>';
    } else if (key === 'model') {
        // Modell-Dropdown wird dynamisch befüllt
        input = '<select id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '"><option value="' + escapeHtml(String(value)) + '">' + escapeHtml(String(value)) + '</option></select>';
    } else if (key === 'level') {
        input = '<select id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '"><option value="passive"' + (value === 'passive' ? ' selected' : '') + '>passiv</option><option value="proactive"' + (value === 'proactive' ? ' selected' : '') + '>proaktiv</option><option value="full"' + (value === 'full' ? ' selected' : '') + '>voll</option></select>';
    } else if (key === 'theme') {
        input = '<select id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '"><option value="dark"' + (value === 'dark' ? ' selected' : '') + '>dark</option><option value="light"' + (value === 'light' ? ' selected' : '') + '>light</option><option value="system"' + (value === 'system' ? ' selected' : '') + '>system</option></select>';
    } else if (boolValue) {
        input = '<select id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '"><option value="true"' + (value ? ' selected' : '') + '>an</option><option value="false"' + (!value ? ' selected' : '') + '>aus</option></select>';
    } else {
        input = '<input id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '" type="' + (numberValue ? 'number' : 'text') + '" value="' + escapeHtml(String(value ?? '')) + '">';
    }
    return '<div class="form-group"><label for="' + id + '">' + escapeHtml(key) + ' <span class="tag ' + badgeClass + '">' + source + '</span></label>' + input + '</div>';
}
function renderSettingsArea(area, settingsByArea, metaByArea) {
    const fields = {
        network: ['http_port', 'quic_port', 'mesh_discovery_port', 'auto_discovery'],
        llm: ['provider', 'model', 'ollama_url', 'temperature', 'max_tokens', 'offline_mode', 'response_style'],
        autonomy: ['level', 'cycle_interval_s', 'self_improvement_allowed', 'self_improvement_max_risk'],
        privacy: ['analytics_enabled', 'log_level', 'retention_days', 'auto_cleanup'],
        ui: ['language', 'theme', 'density', 'animations', 'advanced_views']
    };
    const settings = settingsByArea[area] || {};
    let html = '';
    for (const key of (fields[area] || Object.keys(settings))) {
        if (settings[key] === undefined) continue;
        html += settingField(area, key, settings[key], metaByArea[key] || {});
    }
    if (area === 'llm') {
        html += '<div id="llm-actions"></div>';
    }
    html += '<div class="form-actions"><button class="btn btn-primary btn-sm" onclick="saveSettingsArea(\'' + area + '\', this)">Änderungen speichern</button></div>';
    return html || '<div class="empty">Keine Einstellungen</div>';
}
function parseSettingValue(raw, currentValue) {
    if (typeof currentValue === 'boolean') return raw === 'true';
    if (typeof currentValue === 'number') return Number(raw);
    return raw;
}
async function saveSettingsArea(area, btn) {
    const controls = document.querySelectorAll('[data-setting-area="' + area + '"]');
    const current = (window.__lastSettings && window.__lastSettings[area]) || {};
    const payload = {};
    controls.forEach(ctrl => { const key = ctrl.dataset.settingKey; payload[key] = parseSettingValue(ctrl.value, current[key]); });
    btn && (btn.disabled = true);
    try {
        const result = await api('POST', '/settings/' + area, payload);
        if (result.ok === false) throw new Error(result.error || 'Speichern fehlgeschlagen');
        showNotice('Einstellungen gespeichert', 'success');
        await loadSettings();
    } catch (e) {
        showNotice(e.message, 'error');
    } finally {
        btn && (btn.disabled = false);
    }
}
async function loadLLMConnection() {
    const el = document.getElementById('llm-connection-status');
    if (!el) return;
    try {
        const d = await api('GET', '/llm/connection');
        const openai = d.openai || {};
        let statusText;
        if (openai.auth_method === 'chatgpt_login') {
            statusText = openai.configured ? 'ChatGPT-Login aktiv' : 'ChatGPT-Login nicht aktiv — Bitte anmelden';
        } else {
            statusText = openai.configured ? 'Verbunden' : 'Nicht verbunden';
        }
        el.innerHTML = '<div class="comp-row"><span class="comp-name">OpenAI</span><span class="comp-detail">' + statusText + '</span></div>';
    } catch (e) { el.textContent = e.message; }
}
async function onProviderChange(sel) {
    const provider = sel.value;
    const area = sel.dataset.settingArea;
    if (area !== 'llm') return;
    await loadModelList(provider);
    await updateLLMActions(provider);
}
async function loadModelList(provider) {
    try {
        const d = await api('GET', '/llm/models');
        const models = provider === 'openai_oauth' ? (d.openai || []) : (d.ollama || []);
        const select = document.querySelector('[data-setting-area="llm"][data-setting-key="model"]');
        if (select) {
            const current = select.value;
            select.innerHTML = models.map(m => '<option value="' + escapeHtml(m) + '"' + (m === current ? ' selected' : '') + '>' + escapeHtml(m) + '</option>').join('');
        }
    } catch (e) { console.error('Model list error:', e); }
}
async function updateLLMActions(provider) {
    const container = document.getElementById('llm-actions');
    if (!container) return;
    if (provider === 'openai_oauth') {
        const d = await api('GET', '/llm/connection');
        const openai = d.openai || {};
        if (openai.configured) {
            container.innerHTML = '<div class="muted" style="margin-bottom:8px;">OpenAI ist über ChatGPT-Login verbunden.</div><button class="btn btn-sm" onclick="checkOpenAIAuth(this)">Status prüfen</button> <button class="btn btn-sm" onclick="testOpenAIChat(this)">Test-Chat</button>';
        } else {
            container.innerHTML = '<div class="muted" style="margin-bottom:8px;">Starte einen echten Gerätecode-Login. Das funktioniert auch auf dem Handy: Link öffnen, Code eingeben, danach Status prüfen.</div><button class="btn btn-sm btn-primary" onclick="triggerOpenAILogin(this)">OpenAI Login starten</button><div id="openai-login-session" class="muted" style="margin-top:10px;"></div>';
        }
    } else {
        container.innerHTML = '';
    }
}
async function triggerOpenAILogin(btn) {
    btn && (btn.disabled = true);
    try {
        const result = await api('POST', '/integrations/openai/login', {});
        if (result.session_id) {
            window.eidolonOpenAILoginSessionId = result.session_id;
            const panel = document.getElementById('openai-login-session');
            if (panel) {
                panel.innerHTML = '<div><strong>1.</strong> Öffne: <a href="' + result.verification_url + '" target="_blank" rel="noopener noreferrer">' + result.verification_url + '</a></div>' +
                    '<div style="margin-top:6px;"><strong>2.</strong> Code: <code>' + result.user_code + '</code></div>' +
                    '<div style="margin-top:6px;"><strong>3.</strong> Danach unten auf <em>Status prüfen</em> klicken.</div>' +
                    '<div style="margin-top:10px;"><button class="btn btn-sm" onclick="checkOpenAIAuth(this)">Status prüfen</button></div>';
            }
            showNotice('OpenAI-Gerätecode erstellt. Öffne den Link und gib den Code ein.', 'warning');
        } else if (result.ok) {
            showNotice(result.detail || 'Login erfolgreich', 'success');
        } else {
            showNotice(result.error || 'Login fehlgeschlagen', 'error');
        }
        await loadLLMConnection();
        await updateLLMActions('openai_oauth');
    } catch (e) { showNotice(e.message, 'error'); }
    finally { btn && (btn.disabled = false); }
}
async function saveOpenAIKey(btn) {
    const input = document.getElementById('openai-api-key');
    const key = (input?.value || '').trim();
    if (!key) { showNotice('OpenAI API-Key fehlt', 'warning'); return; }
    btn && (btn.disabled = true);
    try {
        const result = await api('POST', '/llm/openai/api-key', { api_key: key });
        if (result.ok === false) throw new Error(result.error || 'OpenAI-Key konnte nicht gespeichert werden');
        input.value = '';
        showNotice('OpenAI-Key gespeichert', 'success');
        await loadLLMConnection();
    } catch (e) { showNotice(e.message, 'error'); }
    finally { btn && (btn.disabled = false); }
}
async function checkOpenAIAuth(btn) {
    btn && (btn.disabled = true);
    try {
        let result;
        if (window.eidolonOpenAILoginSessionId) {
            result = await api('GET', '/integrations/openai/login/' + window.eidolonOpenAILoginSessionId);
            if (result.logged_in) {
                window.eidolonOpenAILoginSessionId = null;
            }
        } else {
            result = await api('POST', '/integrations/openai/auth', {});
        }
        if (result.ok) {
            showNotice(result.detail || 'OpenAI verbunden', 'success');
        } else if (result.status === 'awaiting_browser') {
            showNotice('Login läuft noch. Öffne den Link, gib den Code ein und prüfe danach erneut den Status.', 'warning');
        } else {
            showNotice(result.error || 'OpenAI nicht verbunden', 'warning');
        }
        await loadLLMConnection();
        await updateLLMActions('openai_oauth');
    } catch (e) { showNotice(e.message, 'error'); }
    finally { btn && (btn.disabled = false); }
}
async function testOpenAIChat(btn) {
    btn && (btn.disabled = true);
    try {
        const result = await api('POST', '/chat', { message: 'Sag nur: EIDOLON_OK' });
        if (result.ok) {
            showNotice('Chat-Antwort: ' + (result.reply || '').slice(0, 50), 'success');
        } else {
            showNotice(result.error || 'Chat fehlgeschlagen', 'error');
        }
    } catch (e) { showNotice(e.message, 'error'); }
    finally { btn && (btn.disabled = false); }
}
async function resetSettingsArea(area) {
    try {
        await api('POST', '/settings/' + area + '/reset', {});
        showNotice('Bereich zurückgesetzt', 'success');
        await loadSettings();
        focusSettingsArea(area);
    } catch (e) {
        showNotice(e.message, 'error');
    }
}

// Theme
