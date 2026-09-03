// Code Repair
function codePathValue() {
    return document.getElementById('code-file-path')?.value.trim() || 'python/agent_server.py';
}

function renderCodeBlock(id, payload) {
    const el = document.getElementById(id);
    if (!el) return;
    el.style.display = 'block';
    el.textContent = typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2);
}

async function loadCodeRepair() {
    try {
        const d = await api('GET', '/code/files');
        const el = document.getElementById('code-analysis');
        const files = d.files || [];
        if (el) el.style.display = 'block';
        if (!files.length) { el.innerHTML = '<div class="empty">Keine Dateien</div>'; return; }
        el.innerHTML = files.map(f => '<div class="comp-row"><span class="comp-dot ok"></span><span class="comp-name">' + escapeHtml(f) + '</span><button class="btn btn-sm" onclick="document.getElementById(\'code-file-path\').value=' + escapeHtml(JSON.stringify(f)) + '">Übernehmen</button></div>').join('');
    } catch (e) { const el = document.getElementById('code-analysis'); if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>'; }
}
async function analyzeCode() {
    var file = codePathValue();
    if (!file) return;
    try {
        var d = await api('POST', '/code/analyze', { file_path: file });
        if (d?.ok === false) { renderCodeBlock('code-analysis', d); showNotice(d.error || 'Analyse fehlgeschlagen', 'error'); return; }
        renderCodeBlock('code-analysis', d);
        showNotice('Analyse OK', 'success');
    } catch (e) { showNotice(e.message, 'error'); }
}
async function fixCode() {
    var file = codePathValue();
    var issue = document.getElementById('code-issue')?.value.trim() || '';
    if (!issue) { showNotice('Keine Issue-Beschreibung', 'error'); return; }
    try {
        var d = await api('POST', '/code/fix', { file_path: file, issue });
        renderCodeBlock('code-fix', d);
        if (d?.change_type === 'proposal_only' || d?.applied === false || d?.supported === false) {
            showNotice(d.rationale || d.error || 'Vorschlag erstellt, nicht angewendet', 'warn');
            return;
        }
        if (d?.ok === false) { showNotice(d.error || 'Reparatur fehlgeschlagen', 'error'); return; }
        showNotice('Fix angewendet', 'success');
    } catch (e) { showNotice(e.message, 'error'); }
}
