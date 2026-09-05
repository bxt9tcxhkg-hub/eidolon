// Settings
const LLM_FIELD_LABELS = {
    provider: 'Anbieter',
    preset: 'Vorlage',
    base_url: 'Basis-URL',
    model: 'Modell',
    ollama_url: 'Ollama-URL',
    fallback_chain: 'Ersatzkette',
    temperature: 'Temperatur',
    max_tokens: 'Max. Tokens',
    offline_mode: 'Offline-Modus',
    response_style: 'Antwortstil',
    auth_method: 'Anmeldung'
};
const SETTING_FIELD_LABELS = {
    llm: LLM_FIELD_LABELS,
    network: { http_port: 'HTTP-Port', quic_port: 'QUIC-Port', mesh_discovery_port: 'Mesh-Port', auto_discovery: 'Auto-Discovery' },
    autonomy: { level: 'Stufe', cycle_interval_s: 'Zyklus (s)', self_improvement_allowed: 'Selbstverbesserung', self_improvement_max_risk: 'Max. Risiko' },
    privacy: { analytics_enabled: 'Analysen', log_level: 'Log-Level', retention_days: 'Aufbewahrung (Tage)', auto_cleanup: 'Automatisch bereinigen' },
    ui: { language: 'Sprache', theme: 'Thema', density: 'Dichte', animations: 'Animationen', advanced_views: 'Erweiterte Ansichten' }
};

async function loadSettings() {
    try {
        const d = await api('GET', '/settings');
        const areas = ['network', 'llm', 'autonomy', 'privacy', 'ui'];
        const settings = d.settings || {};
        window.__lastSettings = settings;
        if (typeof applyUiMotionPreference === 'function') applyUiMotionPreference(settings);
        const meta = d.settings_meta || {};
        areas.forEach(a => { const el = document.getElementById('settings-' + a); if (el) el.innerHTML = renderSettingsArea(a, settings, meta[a] || {}); });
        const provider = (settings.llm && settings.llm.provider) || 'ollama';
        await loadModelList(provider);
        await updateLLMActions(provider);
        await loadLLMConnection();
        syncLlmFieldVisibility(provider);
    } catch (e) { ['network', 'llm', 'autonomy', 'privacy', 'ui'].forEach(a => { const el = document.getElementById('settings-' + a); if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>'; }); }
}
function settingLabel(area, key) {
    return (SETTING_FIELD_LABELS[area] && SETTING_FIELD_LABELS[area][key]) || key;
}
function settingField(area, key, value, meta) {
    const source = meta.source === 'stored' ? 'gesetzt' : 'standard';
    const badgeClass = meta.source === 'stored' ? 'ok' : 'info';
    const id = 'setting-' + area + '-' + key;
    const boolValue = value === true || value === false;
    const numberValue = typeof value === 'number';
    const displayValue = Array.isArray(value) ? value.join(', ') : value;
    let input = '';
    if (key === 'provider') {
        input = '<select id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '" onchange="onProviderChange(this)">' +
            '<option value="ollama"' + (value === 'ollama' ? ' selected' : '') + '>Ollama lokal</option>' +
            '<option value="openai"' + (value === 'openai' ? ' selected' : '') + '>OpenAI-kompatibel (API-Key)</option>' +
            '<option value="openai_oauth"' + (value === 'openai_oauth' ? ' selected' : '') + '>OpenAI (ChatGPT-Login)</option></select>';
    } else if (key === 'preset') {
        input = '<select id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '" onchange="onPresetChange(this)">' +
            '<option value="custom"' + (value === 'custom' ? ' selected' : '') + '>Benutzerdefiniert</option>' +
            '<option value="openai"' + (value === 'openai' ? ' selected' : '') + '>OpenAI</option>' +
            '<option value="groq"' + (value === 'groq' ? ' selected' : '') + '>Groq</option>' +
            '<option value="openrouter"' + (value === 'openrouter' ? ' selected' : '') + '>OpenRouter</option>' +
            '<option value="mistral"' + (value === 'mistral' ? ' selected' : '') + '>Mistral</option>' +
            '<option value="gemini"' + (value === 'gemini' ? ' selected' : '') + '>Gemini (OpenAI-kompatibel)</option>' +
            '<option value="local"' + (value === 'local' ? ' selected' : '') + '>Lokales Gateway</option></select>';
    } else if (key === 'model') {
        input = '<input id="' + id + '" list="llm-model-suggestions" data-setting-area="' + area + '" data-setting-key="' + key + '" type="text" value="' + escapeHtml(String(displayValue ?? '')) + '"><datalist id="llm-model-suggestions"></datalist>';
    } else if (key === 'level') {
        input = '<select id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '"><option value="passive"' + (value === 'passive' ? ' selected' : '') + '>passiv</option><option value="proactive"' + (value === 'proactive' ? ' selected' : '') + '>proaktiv</option><option value="full"' + (value === 'full' ? ' selected' : '') + '>voll</option></select>';
    } else if (key === 'theme') {
        input = '<select id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '"><option value="dark"' + (value === 'dark' ? ' selected' : '') + '>dark</option><option value="light"' + (value === 'light' ? ' selected' : '') + '>light</option><option value="system"' + (value === 'system' ? ' selected' : '') + '>system</option></select>';
    } else if (boolValue) {
        input = '<select id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '"><option value="true"' + (value ? ' selected' : '') + '>an</option><option value="false"' + (!value ? ' selected' : '') + '>aus</option></select>';
    } else {
        input = '<input id="' + id + '" data-setting-area="' + area + '" data-setting-key="' + key + '" type="' + (numberValue ? 'number' : 'text') + '" value="' + escapeHtml(String(displayValue ?? '')) + '">';
    }
    return '<div class="form-group" data-llm-field="' + escapeHtml(key) + '"><label for="' + id + '">' + escapeHtml(settingLabel(area, key)) + ' <span class="tag ' + badgeClass + '">' + source + '</span></label>' + input + '</div>';
}
function renderSettingsArea(area, settingsByArea, metaByArea) {
    const fields = {
        network: ['http_port', 'quic_port', 'mesh_discovery_port', 'auto_discovery'],
        llm: ['provider', 'preset', 'base_url', 'model', 'ollama_url', 'fallback_chain', 'temperature', 'max_tokens', 'offline_mode', 'response_style'],
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
    if (Array.isArray(currentValue)) return String(raw || '').split(',').map(item => item.trim()).filter(Boolean);
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
function connectionStatusLabel(connection) {
    const status = (connection && connection.status) || '';
    if (status === 'connected') return 'verbunden';
    if (status === 'error') return 'Fehler';
    return 'fehlt';
}
async function loadLLMConnection() {
    const el = document.getElementById('llm-connection-status');
    if (!el) return;
    try {
        const d = await api('GET', '/llm/connection');
        const connection = d.connection || {};
        const openai = d.openai || {};
        const rows = [];
        rows.push('<div class="comp-row"><span class="comp-name">Aktiver Anbieter</span><span class="comp-detail">' + escapeHtml(d.provider || '-') + ' / ' + escapeHtml(d.model || '-') + '</span></div>');
        rows.push('<div class="comp-row"><span class="comp-name">Verbindung</span><span class="comp-detail">' + escapeHtml(connectionStatusLabel(connection)) + ' — ' + escapeHtml(connection.detail || '') + '</span></div>');
        rows.push('<div class="comp-row"><span class="comp-name">Anmeldung</span><span class="comp-detail">' + escapeHtml(d.auth_method || connection.auth_method || '-') + (connection.oauth_supported ? ' (OAuth verfügbar)' : ' (kein OAuth)') + '</span></div>');
        if (d.provider === 'openai') {
            rows.push('<div class="comp-row"><span class="comp-name">API-Schlüssel</span><span class="comp-detail">' + (d.key_present ? escapeHtml(d.key_masked || 'hinterlegt') : 'fehlt') + '</span></div>');
        }
        if (d.provider === 'openai_oauth') {
            const oauthText = openai.configured ? 'ChatGPT-Login aktiv' : (openai.oauth_supported ? 'ChatGPT-Login nicht aktiv — bitte anmelden' : 'Codex-CLI fehlt, OAuth nicht startbar');
            rows.push('<div class="comp-row"><span class="comp-name">OpenAI Login</span><span class="comp-detail">' + oauthText + '</span></div>');
        }
        if (Array.isArray(d.fallback_chain) && d.fallback_chain.length) {
            rows.push('<div class="comp-row"><span class="comp-name">Ersatzkette</span><span class="comp-detail">' + escapeHtml(d.fallback_chain.join(' → ')) + '</span></div>');
        }
        el.innerHTML = rows.join('');
    } catch (e) { el.textContent = e.message; }
}
function syncLlmFieldVisibility(provider) {
    document.querySelectorAll('#settings-llm [data-llm-field]').forEach(row => {
        const key = row.getAttribute('data-llm-field');
        let show = true;
        if (key === 'ollama_url') show = provider === 'ollama';
        if (key === 'preset' || key === 'base_url') show = provider === 'openai';
        row.style.display = show ? '' : 'none';
    });
}
async function onProviderChange(sel) {
    const provider = sel.value;
    const area = sel.dataset.settingArea;
    if (area !== 'llm') return;
    syncLlmFieldVisibility(provider);
    await loadModelList(provider);
    await updateLLMActions(provider);
}
async function onPresetChange(sel) {
    try {
        const d = await api('GET', '/llm/providers');
        const preset = (d.presets || []).find(item => item.id === sel.value);
        const urlInput = document.querySelector('[data-setting-area="llm"][data-setting-key="base_url"]');
        if (preset && preset.base_url && urlInput) urlInput.value = preset.base_url;
        await loadModelList('openai');
    } catch (e) { console.error('Preset error:', e); }
}
async function loadModelList(provider) {
    try {
        const d = await api('GET', '/llm/models');
        const byProvider = d.by_provider || {};
        const models = byProvider[provider] || (provider === 'openai_oauth' ? (d.openai || []) : (provider === 'openai' ? (d.openai || []) : (d.ollama || [])));
        const list = document.getElementById('llm-model-suggestions');
        if (list) {
            list.innerHTML = models.map(m => '<option value="' + escapeHtml(m) + '"></option>').join('');
        }
    } catch (e) { console.error('Model list error:', e); }
}
async function updateLLMActions(provider) {
    const container = document.getElementById('llm-actions');
    if (!container) return;
    if (provider === 'openai') {
        const d = await api('GET', '/llm/connection');
        const masked = d.key_present ? ('Aktuell: ' + (d.key_masked || 'hinterlegt')) : 'Kein Schlüssel hinterlegt.';
        container.innerHTML = '<div class="muted" style="margin-bottom:8px;">OpenAI-kompatibler Stecker: Basis-URL + API-Schlüssel + Modell. OAuth gibt es für diesen Anbieter nicht.</div>' +
            '<div class="form-group"><label for="openai-api-key">API-Schlüssel</label><input id="openai-api-key" type="password" autocomplete="off" placeholder="wird nie in Antworten zurückgegeben"></div>' +
            '<div class="muted" style="margin-bottom:8px;">' + escapeHtml(masked) + '</div>' +
            '<button class="btn btn-sm btn-primary" onclick="saveOpenAIKey(this)">Schlüssel speichern</button> <button class="btn btn-sm" onclick="testOpenAIChat(this)">Test-Chat</button>';
        return;
    }
    if (provider === 'openai_oauth') {
        const d = await api('GET', '/llm/connection');
        const openai = d.openai || {};
        const oauthSupported = openai.oauth_supported === true;
        if (!oauthSupported) {
            container.innerHTML = '<div class="muted">OAuth ist nur über die Codex-CLI verfügbar. Die CLI fehlt — es gibt keinen Fake-Login für diesen Pfad.</div>';
            return;
        }
        if (openai.configured) {
            container.innerHTML = '<div class="muted" style="margin-bottom:8px;">OpenAI ist über ChatGPT-Login verbunden.</div><button class="btn btn-sm" onclick="checkOpenAIAuth(this)">Status prüfen</button> <button class="btn btn-sm" onclick="testOpenAIChat(this)">Test-Chat</button>';
        } else {
            container.innerHTML = '<div class="muted" style="margin-bottom:8px;">Starte einen echten Gerätecode-Login. Das funktioniert auch auf dem Handy: Link öffnen, Code eingeben, danach Status prüfen.</div><button class="btn btn-sm btn-primary" onclick="triggerOpenAILogin(this)">OpenAI Login starten</button><div id="openai-login-session" class="muted" style="margin-top:10px;"></div>';
        }
        return;
    }
    container.innerHTML = '<div class="muted">Ollama braucht keine Schlüssel. OAuth wird hier nicht angeboten.</div>';
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
    if (!key) { showNotice('API-Schlüssel fehlt', 'warning'); return; }
    btn && (btn.disabled = true);
    try {
        const result = await api('POST', '/llm/openai/api-key', { api_key: key });
        if (result.ok === false) throw new Error(result.error || 'API-Schlüssel konnte nicht gespeichert werden');
        if (result.api_key || (key && JSON.stringify(result).includes(key))) throw new Error('Server hat den Schlüssel zurückgegeben — Speichern abgebrochen.');
        input.value = '';
        showNotice('API-Schlüssel gespeichert', 'success');
        await loadLLMConnection();
        await updateLLMActions('openai');
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
            showNotice('Chat-Antwort: ' + (result.reply || result.response || '').slice(0, 50), 'success');
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
