// Self-Healing
async function loadHealing() {
    try {
        const d = await api('GET', '/healing/status');
        const el = document.getElementById('healing-status');
        if (!el) return;
        const running = d.available === true && d.status === 'running';
        let html = '<div class="comp-row"><span class="comp-dot ' + (running ? 'ok' : 'warn') + '"></span><span class="comp-name">Status</span><span class="comp-detail">' + (d.status || 'unbekannt') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-dot ok"></span><span class="comp-name">Registrierte Checks</span><span class="comp-detail">' + ((d.checks_registered || []).join(', ') || 'Keine') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-dot ok"></span><span class="comp-name">Ausgeführte Checks</span><span class="comp-detail">' + (d.total_checks || 0) + '</span></div>';
        html += '<div class="comp-row"><span class="comp-dot ' + (Object.keys(d.error_counts || {}).length ? 'warn' : 'ok') + '"></span><span class="comp-name">Fehlerzähler</span><span class="comp-detail">' + (Object.keys(d.error_counts || {}).length ? escapeHtml(JSON.stringify(d.error_counts)) : 'Keine') + '</span></div>';
        html += '<div class="small muted" style="margin-top:10px;">' + escapeHtml(d.detail || '') + '</div>';
        if (d.last_event) html += '<pre style="margin-top:10px;max-height:180px;overflow:auto;">' + escapeHtml(JSON.stringify(d.last_event, null, 2)) + '</pre>';
        el.innerHTML = html;
    } catch (e) { const el = document.getElementById('healing-status'); if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>'; }
}

async function runHealingCheck() {
    try {
        const d = await api('POST', '/healing/check', {});
        if (d?.ok === false) { showNotice(d.error || 'Healing-Check fehlgeschlagen', 'error'); return; }
        showNotice('Healing-Check ausgeführt', 'success');
        await loadHealing();
    } catch (e) { showNotice(e.message, 'error'); }
}
