async function loadHealth() {
    try {
        const d = await api('GET', '/health');
        const badge = document.getElementById('health-badge');
        badge.className = d.status === 'ok' ? 'tag ok' : 'tag warn';
        badge.textContent = d.status === 'ok' ? 'OK' : 'Eingeschränkt';
        const wsStatus = document.getElementById('ws-status');
        if (wsStatus) applyLocalRuntimeStatus(wsStatus, d);
        const comps = d.components || {};
        const componentRows = [];
        let html = '<div class="comp-row"><span class="comp-dot ok"></span><span class="comp-name">Laufzeit</span><span class="comp-detail">' + (d.uptime_human || '-') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-dot ok"></span><span class="comp-name">Status</span><span class="comp-detail">' + (d.status || '-') + '</span></div>';
        if (comps.skills) html += '<div class="comp-row"><span class="comp-dot ok"></span><span class="comp-name">Skills</span><span class="comp-detail">' + comps.skills.count + '/' + comps.skills.enabled + '</span></div>';
        if (comps.capabilities) html += '<div class="comp-row"><span class="comp-dot ok"></span><span class="comp-name">Capabilities</span><span class="comp-detail">' + comps.capabilities.available + '/' + comps.capabilities.total + '</span></div>';
        if (comps.certificates) html += '<div class="comp-row"><span class="comp-dot ' + (comps.certificates.complete ? 'ok' : 'warn') + '"></span><span class="comp-name">Zertifikate</span><span class="comp-detail">' + (comps.certificates.complete ? comps.certificates.days_left + ' Tage' : 'Unvollständig') + '</span></div>';
        if (comps.mesh_metrics) html += '<div class="comp-row"><span class="comp-dot ' + (comps.mesh_metrics.peer_count > 0 ? 'ok' : '') + '"></span><span class="comp-name">Mesh-Peers</span><span class="comp-detail">' + comps.mesh_metrics.peer_count + ' verbunden</span></div>';
        if (comps.knowledge_graph) componentRows.push('<div class="comp-row"><span class="comp-dot ' + (comps.knowledge_graph.available ? 'ok' : 'warn') + '"></span><span class="comp-name">Knowledge Graph</span><span class="comp-detail">' + (comps.knowledge_graph.available ? ((comps.knowledge_graph.stats?.entities ?? 0) + ' Entitäten') : 'Nicht verfügbar') + '</span></div>');
        if (comps.quic_port) componentRows.push('<div class="comp-row"><span class="comp-dot ' + (comps.quic_port.listening ? 'ok' : 'warn') + '"></span><span class="comp-name">QUIC-Transport</span><span class="comp-detail">' + escapeHtml(comps.quic_port.status || (comps.quic_port.listening ? 'listening' : 'not_wired')) + '</span></div>');
        if (comps.self_healing) componentRows.push('<div class="comp-row"><span class="comp-dot ' + (comps.self_healing.available ? 'ok' : 'warn') + '"></span><span class="comp-name">Self-Healing</span><span class="comp-detail">' + escapeHtml(comps.self_healing.status || (comps.self_healing.available ? 'available' : 'unavailable')) + '</span></div>');
        if (comps.evidence) componentRows.push('<div class="comp-row"><span class="comp-dot ' + (comps.evidence.available ? 'ok' : 'warn') + '"></span><span class="comp-name">Evidence Store</span><span class="comp-detail">' + ((comps.evidence.verified ?? 0) + ' verifiziert / ' + (comps.evidence.blocked ?? 0) + ' blockiert') + '</span></div>');
        if (comps.goals) componentRows.push('<div class="comp-row"><span class="comp-dot ' + ((comps.goals.active ?? 0) > 0 ? 'ok' : 'warn') + '"></span><span class="comp-name">Ausführungsziele</span><span class="comp-detail">' + ((comps.goals.active ?? 0) + ' aktiv / ' + (comps.goals.done ?? 0) + ' erledigt') + '</span></div>');
        if (comps.backups) componentRows.push('<div class="comp-row"><span class="comp-dot ok"></span><span class="comp-name">Sicherungen</span><span class="comp-detail">' + ((comps.backups.count ?? 0) + ' vorhanden') + '</span></div>');
        const hc = document.getElementById('health-summary');
        if (hc) hc.innerHTML = html;
        const dc = document.getElementById('dash-components');
        if (dc) dc.innerHTML = componentRows.length ? componentRows.join('') : '<div class="empty">Keine Komponenteninformationen</div>';
    } catch (e) {
        const hc = document.getElementById('health-summary');
        if (hc) hc.innerHTML = '<span class="tag err">' + e.message + '</span>';
        const dc = document.getElementById('dash-components');
        if (dc) dc.innerHTML = '<span class="tag err">' + e.message + '</span>';
        const wsStatus = document.getElementById('ws-status');
        if (wsStatus) applyLocalRuntimeStatus(wsStatus, null, e.message);
    }
}

function describeLocalRuntimeStatus(health, errorMessage) {
    if (!health) {
        return {
            label: 'Offline',
            tone: 'offline',
            title: 'Backend nicht erreichbar. Die lokale Runtime antwortet nicht' + (errorMessage ? (': ' + errorMessage) : '.'),
        };
    }
    const status = health.status || '';
    const problems = Array.isArray(health.problems) ? health.problems.filter(Boolean) : [];
    const unavailable = health.components?.capabilities?.unavailable_ids || [];
    if (status === 'ok') {
        return {
            label: 'Lokal',
            tone: 'quiet',
            title: 'Lokal verbunden. Die Runtime ist erreichbar — das ist kein voller Mesh-/QUIC-Status.',
        };
    }
    if (status === 'ok_with_limits') {
        const extra = unavailable.length ? (' Nicht verdrahtet: ' + unavailable.join(', ') + '.') : '';
        return {
            label: 'Lokal',
            tone: 'quiet',
            title: 'Lokal verbunden, mit bekannten Grenzen.' + extra + ' Kein erfundener Vollstatus.',
        };
    }
    const reason = problems.length
        ? problems.join('; ')
        : 'Bekannte lokale Grenzen (z. B. fehlendes Backup oder unvollständige Zertifikate).';
    return {
        label: 'Lokal · Grenzen',
        tone: 'limited',
        title: 'Lokal eingeschränkt: ' + reason + ' Die Arbeitsfläche selbst läuft weiter — das ist kein Ausfall.',
    };
}

function applyLocalRuntimeStatus(el, health, errorMessage) {
    const info = describeLocalRuntimeStatus(health, errorMessage);
    el.className = 'ws-status ' + info.tone;
    el.title = info.title;
    el.setAttribute('aria-label', info.title);
    el.innerHTML = '<span class="dot"></span> ' + escapeHtml(info.label);
}
async function loadCapabilities() {
    try {
        const d = await api('GET', '/capabilities');
        const el = document.getElementById('capabilities-summary');
        const caps = d.capabilities || [];
        if (!caps.length) { el.innerHTML = '<div class="empty">Keine</div>'; return; }
        el.innerHTML = caps.map(c => '<div class="comp-row"><span class="comp-dot ' + (c.available ? 'ok' : 'warn') + '"></span><span class="comp-name">' + escapeHtml(c.name || c.id) + '</span><span class="comp-detail">' + escapeHtml(c.detail || '') + '</span></div>').join('');
        const cc = document.getElementById('cap-count');
        if (cc) cc.textContent = caps.filter(c => c.available).length + '/' + caps.length;
    } catch (e) {
        const el = document.getElementById('capabilities-summary');
        if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>';
    }
}
async function loadSystemMetrics() {
    try {
        const d = await api('GET', '/system/metrics');
        const el = document.getElementById('dash-metrics');
        if (!el) return;
        const runtime = d.process || {};
        const system = d.system || {};
        let html = '<div class="comp-row"><span class="comp-name">Prozessspeicher</span><span class="comp-detail">' + ((runtime.memory_mb ?? '—') + ' MB') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-name">Threads</span><span class="comp-detail">' + (runtime.threads ?? '—') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-name">System-CPU</span><span class="comp-detail">' + ((system.cpu_percent ?? '—') + '%') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-name">RAM gesamt</span><span class="comp-detail">' + ((system.ram_used_gb ?? '—') + ' / ' + (system.ram_total_gb ?? '—') + ' GB') + '</span></div>';
        html += '<div class="comp-row"><span class="comp-name">Freier Speicher</span><span class="comp-detail">' + ((system.disk_free_gb ?? '—') + ' GB') + '</span></div>';
        el.innerHTML = html;
    } catch (e) {
        const el = document.getElementById('dash-metrics');
        if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>';
    }
}
async function loadSystemStorage() {
    try {
        const d = await api('GET', '/system/storage');
        const el = document.getElementById('dash-storage');
        if (!el) return;
        const areas = d.areas || {};
        const entries = Object.entries(areas);
        let html = entries.length
            ? entries.map(([name, area]) => '<div class="comp-row"><span class="comp-name">' + escapeHtml(name) + '</span><span class="comp-detail">' + ((area.size_mb ?? '—') + ' MB · ' + (area.files ?? 0) + ' Dateien') + '</span></div>').join('')
            : '<div class="empty">Keine Datenablageinformationen</div>';
        el.innerHTML = html;
    } catch (e) {
        const el = document.getElementById('dash-storage');
        if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>';
    }
}
async function loadDashboard() {
    loadHealth();
    loadCapabilities();
    loadSystemMetrics();
    loadSystemStorage();
}

// Workspaces moved to /assets/workspace-ui.js

// Mesh
async function loadMesh() {
    try {
        const [peerData, pairedData] = await Promise.all([api('GET', '/mesh/peers'), api('GET', '/mesh/pairing/paired')]);
        const el = document.getElementById('mesh-peers');
        const byId = new Map();
        (peerData.peers || []).forEach(p => byId.set(p.peer_id, p));
        (pairedData.paired || []).forEach(p => byId.set(p.peer_id, { ...(byId.get(p.peer_id) || {}), ...p, paired: true, status: (byId.get(p.peer_id)?.status || 'paired') }));
        const peers = Array.from(byId.values());
        if (!peers.length) { el.innerHTML = '<div class="empty">Keine gekoppelten Geräte oder erreichbaren Peers</div>'; return; }
        el.innerHTML = peers.map(p => {
            const dot = p.status === 'connected' ? 'ok' : p.paired ? 'warn' : '';
            const detail = [p.address || '', p.status || '', p.paired ? 'gepaart' : ''].filter(Boolean).join(' · ');
            const action = p.paired ? '<button class="btn btn-sm" data-unpair-peer="' + escapeHtml(p.peer_id) + '" onclick="unpairPeer(\'' + escapeHtml(p.peer_id) + '\', this)">' + (armedUnpairPeerId === p.peer_id ? 'Entkoppeln bestätigen' : 'Entkoppeln') + '</button>' : '';
            return '<div class="comp-row"><span class="comp-dot ' + dot + '"></span><span class="comp-name">' + escapeHtml(p.name || p.address || p.peer_id) + '</span><span class="comp-detail">' + escapeHtml(detail) + '</span>' + action + '</div>';
        }).join('');
    } catch (e) { const el = document.getElementById('mesh-peers'); if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>'; }
}
async function scanMeshPeers() { try { await api('POST', '/mesh/scan', {}); loadMesh(); } catch (e) {} }
async function unpairPeer(peerId, btn) {
    if (!peerId) { showNotice('Peer-ID fehlt', 'error'); return; }
    if (armedUnpairPeerId !== peerId) {
        armedUnpairPeerId = peerId;
        if (btn) btn.textContent = 'Entkoppeln bestätigen';
        showNotice('Noch einmal klicken, um die Kopplung aufzuheben.', 'warning');
        return;
    }
    btn && (btn.disabled = true);
    try {
        const result = await api('DELETE', '/mesh/pairing/paired/' + encodeURIComponent(peerId));
        if (result.ok === false) throw new Error(result.error || 'Entkoppeln fehlgeschlagen');
        const localDevice = getStoredMobileDevice();
        if (localDevice && localDevice.peer_id === peerId) localStorage.removeItem('eidolon-paired-device');
        armedUnpairPeerId = null;
        showNotice('Gerät entkoppelt', 'success');
        await loadMesh();
        await loadMobileDeviceState();
    } catch (e) {
        showNotice(e.message, 'error');
    } finally {
        btn && (btn.disabled = false);
    }
}
async function createPairing() {
    try {
        const d = await api('POST', '/mesh/pairing/create', {});
        document.getElementById('mesh-pairing-code').textContent = d.code || '';
        document.getElementById('mesh-qr').innerHTML = d.qr_png ? '<img src="' + d.qr_png + '" width="160">' : (d.qr_svg ? d.qr_svg : '');
    } catch (e) { showNotice(e.message, 'error'); }
}
async function acceptPairing() {
    const code = document.getElementById('mesh-input-code')?.value.trim();
    if (!code) { showNotice('Code eingeben', 'warning'); return; }
    try {
        const r = await api('POST', '/mesh/pairing/accept', { code });
        loadMesh();
        loadMeshPending();
        if (r?.ok === false) {
            showNotice(r.error || 'Pairing fehlgeschlagen', 'error');
            return;
        }
        showNotice('Verbunden!', 'success');
    } catch (e) { showNotice(e.message, 'error'); }
}
async function denyPairing() { try { await api('POST', '/mesh/pairing/reject', {}); loadMeshPending(); } catch (e) {} }
async function loadMeshPending() {
    try {
        const d = await api('GET', '/mesh/pairing/pending');
        const el = document.getElementById('mesh-pending');
        const pending = d.pending || [];
        if (!pending.length) { el.innerHTML = '<div class="empty">Keine Anfragen</div>'; return; }
        el.innerHTML = pending.map(p => '<div class="comp-row"><span class="comp-dot warn"></span><span class="comp-name">' + escapeHtml(p.name || p.address) + '</span><span class="comp-detail">' + (p.code || '') + '</span></div>').join('');
    } catch (e) { const el = document.getElementById('mesh-pending'); if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>'; }
}

// Goals
let allGoals = [];
let armedGoalDeleteId = null;
