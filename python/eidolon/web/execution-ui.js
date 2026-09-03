(function () {
    function row(label, value) {
        return '<div class="comp-row"><span class="comp-name">' + escapeHtml(label) + '</span><span class="comp-detail">' + escapeHtml(value) + '</span></div>';
    }

    function renderExecutionSummary(runtime, health, capabilities, mesh, workspaceOverview) {
        const root = document.getElementById('execution-summary');
        if (!root) return;
        const operate = workspaceOverview?.operate || {};
        const run = operate.run || {};
        const activeWorkspace = (workspaceOverview?.workspaces || []).find((item) => item.state === 'active');
        const orchestration = (activeWorkspace?.state_data || {}).orchestration || {};
        const nextBest = orchestration.next_best_action || {};
        const paired = mesh?.paired || [];
        const availableCaps = (capabilities?.capabilities || []).filter((item) => item.available);
        const rows = [
            ['Run', run.id || 'kein aktiver Run'],
            ['Run-Zustand', run.state || '—'],
            ['Aktive Pods', String((operate.active_pods || operate.subagents || []).length)],
            ['Aktiver Workspace', activeWorkspace?.topic_label || 'keiner'],
            ['Nächste Workspace-Aktion', nextBest.label || nextBest.action || 'keine ausführbare Aktion'],
            ['Browser-Control', availableCaps.some((item) => item.id === 'browser.control') ? 'verfügbar' : 'nicht verfügbar'],
            ['QUIC / Mesh', health?.components?.quic_port?.status || 'unbekannt'],
            ['Gekoppelte Geräte', String(paired.length)],
            ['Python', runtime?.python_version || '—'],
            ['Plattform', runtime?.platform || '—'],
            ['Prozess', runtime?.process?.available ? ('PID ' + runtime.process.pid + ' · ' + runtime.process.memory_mb + ' MB') : (runtime?.process?.reason || 'nicht verfügbar')],
        ];
        root.innerHTML = rows.map(([label, value]) => row(label, value)).join('');
    }

    function renderExecutionCapabilities(capabilities) {
        const root = document.getElementById('execution-capabilities');
        if (!root) return;
        const caps = capabilities?.capabilities || [];
        if (!caps.length) {
            root.innerHTML = '<div class="empty">Keine Capabilities-Daten.</div>';
            return;
        }
        root.innerHTML = caps.map((item) => '<div class="comp-row"><span class="comp-dot ' + (item.available ? 'ok' : 'warn') + '"></span><span class="comp-name">' + escapeHtml(item.name || item.id) + '</span><span class="comp-detail">' + escapeHtml(item.detail || '') + '</span></div>').join('');
    }

    function renderExecutionDevices(mesh) {
        const root = document.getElementById('execution-devices');
        if (!root) return;
        const paired = mesh?.paired || [];
        if (!paired.length) {
            root.innerHTML = '<div class="empty">Keine gekoppelten Geräte.</div>';
            return;
        }
        root.innerHTML = paired.map((item) => '<div class="comp-row"><span class="comp-name">' + escapeHtml(item.name || item.peer_id || 'Gerät') + '</span><span class="comp-detail">' + escapeHtml((item.peer_id || '—') + ' · ' + (item.status || 'paired')) + '</span></div>').join('');
    }

    async function loadExecutionView() {
        try {
            const [runtime, health, capabilities, mesh, workspaceOverview] = await Promise.all([
                api('GET', '/system/metrics'),
                api('GET', '/health'),
                api('GET', '/capabilities'),
                api('GET', '/mesh/pairing/paired'),
                api('GET', '/workspaces'),
            ]);
            renderExecutionSummary(runtime, health, capabilities, mesh, workspaceOverview);
            renderExecutionCapabilities(capabilities);
            renderExecutionDevices(mesh);
        } catch (e) {
            const msg = e.message || 'Execution Surface konnte nicht geladen werden';
            document.getElementById('execution-summary').innerHTML = '<div class="empty">' + escapeHtml(msg) + '</div>';
            document.getElementById('execution-capabilities').innerHTML = '<div class="empty">Capabilities konnten nicht geladen werden.</div>';
            document.getElementById('execution-devices').innerHTML = '<div class="empty">Geräte konnten nicht geladen werden.</div>';
        }
    }

    window.loadExecutionView = loadExecutionView;
})();
