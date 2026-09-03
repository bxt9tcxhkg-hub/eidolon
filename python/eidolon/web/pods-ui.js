(function () {
    function podCard(item, selectedPodId) {
        const selected = item.id === selectedPodId;
        return [
            '<div class="goal-card" data-status="' + escapeHtml(item.state || 'queued') + '"' + (selected ? ' style="border-color:var(--accent);box-shadow:0 0 0 1px var(--accent-subtle) inset;"' : '') + '>',
            '<div class="goal-body">',
            '<div class="goal-head"><div class="goal-headline"><span class="status-chip">' + escapeHtml(item.state || 'queued') + '</span><div class="goal-title">' + escapeHtml(item.display_name || item.id || 'Pod') + '</div></div></div>',
            '<div class="comp-detail" style="margin:6px 0 10px 0;">' + escapeHtml(item.mission || 'Keine Mission') + '</div>',
            '<div class="goal-actions">',
            '<button class="btn btn-sm ' + (selected ? 'btn-primary' : '') + '" data-ui-action="openPodDetail" data-ui-args=' + JSON.stringify([item.id]) + '>Details</button>',
            '</div>',
            '</div>',
            '</div>',
        ].join('');
    }

    function renderPodsOverview(items) {
        const root = document.getElementById('pods-list');
        if (!root) return;
        const pods = Array.isArray(items) ? items : [];
        const selected = window.EidolonOperate.pickSelectedPod(pods);
        if (!pods.length) {
            root.innerHTML = '<div class="empty">Keine aktiven Pod-Runs.</div>';
            return;
        }
        root.innerHTML = pods.map((item) => podCard(item, selected?.id)).join('');
    }

    function renderPodDetail(item) {
        const root = document.getElementById('pod-detail');
        if (!root) return;
        if (!item) {
            root.innerHTML = '<div class="empty">Kein aktiver Pod gewählt.</div>';
            return;
        }
        const rows = [
            ['Name', item.display_name || '—'],
            ['Pod-ID', item.id || '—'],
            ['Funktion', item.function_family || item.function_type || '—'],
            ['Mission', item.mission || '—'],
            ['Zustand', item.state || '—'],
            ['Aktiv', item.is_active ? 'ja' : 'nein'],
            ['Terminal', item.is_terminal ? 'ja' : 'nein'],
            ['Grund', item.state_reason || '—'],
            ['Ergebnis', item.result_status || '—'],
            ['Evidenz', String(item.evidence_count ?? 0)],
        ];
        root.innerHTML = rows.map(([label, value]) => window.EidolonOperate.row(label, value)).join('');
    }

    async function loadPodsView() {
        try {
            const overview = await api('GET', '/api/v1/operate/overview');
            const data = overview?.data || {};
            const pods = data.active_pods || data.subagents || [];
            renderPodsOverview(pods);
            renderPodDetail(window.EidolonOperate.pickSelectedPod(pods));
        } catch (e) {
            window.EidolonOperate.renderEmpty('pods-list', e.message || 'Pods konnten nicht geladen werden');
            window.EidolonOperate.renderEmpty('pod-detail', 'Pod-Detail konnte nicht geladen werden');
        }
    }

    function openPodDetail(podId) {
        window.EidolonOperate.selectPod(podId);
        loadPodsView();
        showTab('pods');
    }

    Object.assign(window, { loadPodsView, openPodDetail, renderPodsOverview, renderPodDetail });
})();
