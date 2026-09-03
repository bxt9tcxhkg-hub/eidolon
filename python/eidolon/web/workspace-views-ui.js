(function () {
    const ws = window.EidolonWorkspace;
    const state = ws.state;

    function switchView() {
        const view = document.getElementById('ws-view-mode')?.value || 'canvas';
        document.getElementById('ws-canvas-card').style.display = view === 'canvas' ? 'block' : 'none';
        document.getElementById('ws-elements-card').style.display = view !== 'canvas' ? 'block' : 'none';
        const title = document.getElementById('ws-elements-title');
        if (title) title.textContent = view === 'board' ? 'Board' : view === 'timeline' ? 'Timeline' : 'Liste';
        if (view === 'canvas') renderCanvas();
        else if (view === 'board') renderBoardView();
        else if (view === 'timeline') renderTimelineView();
        else renderListView();
        const filter = document.getElementById('ws-element-filter');
        if (filter && !filter.dataset.bound) {
            filter.dataset.bound = '1';
            filter.addEventListener('input', () => {
                const currentView = document.getElementById('ws-view-mode')?.value || 'canvas';
                if (currentView === 'board') renderBoardView();
                else if (currentView === 'timeline') renderTimelineView();
                else if (currentView === 'list') renderListView();
            });
        }
    }

    function elementCard(item) {
        return '<div class="goal-card" data-status="' + escapeHtml(item.status || 'idea') + '" style="margin-bottom:8px;cursor:pointer;">' +
            '<div class="goal-stripe"></div><div class="goal-body"><div class="goal-title">' + escapeHtml(item.title) + '</div><div class="comp-detail" style="margin-top:6px;">' + escapeHtml(ws.elementTypeLabel(item.element_type)) + (item.priority > 0 ? ' · ' + escapeHtml(ws.priorityLabel(item.priority)) : '') + '</div></div></div>';
    }

    function bindOpenElementTargets(root) {
        root.querySelectorAll('[data-open-element-id]').forEach((node) => {
            node.addEventListener('click', () => openElementForm(node.dataset.openElementId, Number(node.dataset.x || 0), Number(node.dataset.y || 0)));
        });
    }

    function renderBoardView() {
        if (!state.currentProject) return;
        const elements = state.currentProject.elements || [];
        const el = document.getElementById('ws-elements-view');
        const filterInput = document.getElementById('ws-element-filter');
        const filterText = filterInput ? filterInput.value.toLowerCase().trim() : '';

        if (!elements.length) {
            el.innerHTML = '<div class="empty">Keine Elemente für das Board vorhanden</div>';
            document.getElementById('ws-elements-count').textContent = '0';
            return;
        }

        const filteredElements = filterText
            ? elements.filter(item => item.title.toLowerCase().includes(filterText) || (item.description || '').toLowerCase().includes(filterText))
            : elements;

        const columns = [['idea', 'Ideen'], ['planned', 'Geplant'], ['in_progress', 'In Arbeit'], ['blocked', 'Blockiert'], ['done', 'Erledigt']];
        el.innerHTML = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;">' + columns.map(([status, label]) => {
            const items = filteredElements.filter((item) => item.status === status);
            const body = items.length
                ? items.map((item) => '<div data-open-element-id="' + escapeHtml(item.id) + '" data-x="' + Number(item.position?.x || 0) + '" data-y="' + Number(item.position?.y || 0) + '">' + elementCard(item) + '</div>').join('')
                : '<div class="empty">Leer</div>';
            return '<div class="card" style="padding:10px;"><div class="card-header" style="margin-bottom:8px;"><h3 style="font-size:0.9rem;">' + escapeHtml(label) + '</h3><span class="tag info">' + items.length + '</span></div>' + body + '</div>';
        }).join('') + '</div>';
        bindOpenElementTargets(el);
        document.getElementById('ws-elements-count').textContent = String(filteredElements.length);
    }

    function renderTimelineView() {
        if (!state.currentProject) return;
        const elements = state.currentProject.elements || [];
        const el = document.getElementById('ws-elements-view');
        const scheduled = elements.filter((item) => item.due_at).sort((a, b) => String(a.due_at).localeCompare(String(b.due_at)));
        const unscheduled = elements.filter((item) => !item.due_at);
        if (!elements.length) {
            el.innerHTML = '<div class="empty">Keine Elemente für die Timeline vorhanden</div>';
            document.getElementById('ws-elements-count').textContent = '0';
            return;
        }
        let html = '';
        html += '<div class="card" style="padding:10px;margin-bottom:12px;"><div class="card-header"><h3 style="font-size:0.9rem;">Terminierte Schritte</h3><span class="tag info">' + scheduled.length + '</span></div>';
        html += scheduled.length ? scheduled.map((item) => '<div class="comp-row" data-open-element-id="' + escapeHtml(item.id) + '" data-x="' + Number(item.position?.x || 0) + '" data-y="' + Number(item.position?.y || 0) + '" style="cursor:pointer;"><span class="comp-name">' + escapeHtml(item.due_at) + '</span><span class="comp-detail">' + escapeHtml(item.title + ' · ' + ws.statusLabel(item.status)) + '</span></div>').join('') : '<div class="empty">Keine Termine gesetzt</div>';
        html += '</div>';
        html += '<div class="card" style="padding:10px;"><div class="card-header"><h3 style="font-size:0.9rem;">Ohne Termin</h3><span class="tag info">' + unscheduled.length + '</span></div>';
        html += unscheduled.length ? unscheduled.map((item) => '<div class="comp-row" data-open-element-id="' + escapeHtml(item.id) + '" data-x="' + Number(item.position?.x || 0) + '" data-y="' + Number(item.position?.y || 0) + '" style="cursor:pointer;"><span class="comp-name">' + escapeHtml(item.title) + '</span><span class="comp-detail">' + escapeHtml(ws.statusLabel(item.status) + ' · ' + ws.elementTypeLabel(item.element_type)) + '</span></div>').join('') : '<div class="empty">Alle Elemente sind terminiert</div>';
        html += '</div>';
        el.innerHTML = html;
        bindOpenElementTargets(el);
        document.getElementById('ws-elements-count').textContent = String(elements.length);
    }

    function renderListView() {
        if (!state.currentProject) return;
        const elements = state.currentProject.elements || [];
        const el = document.getElementById('ws-elements-view');
        if (!elements.length) {
            el.innerHTML = '<div class="empty">Keine Elemente in der Liste vorhanden</div>';
            document.getElementById('ws-elements-count').textContent = '0';
            return;
        }
        const rows = elements.map((item) => '<tr data-open-element-id="' + escapeHtml(item.id) + '" data-x="' + Number(item.position?.x || 0) + '" data-y="' + Number(item.position?.y || 0) + '" style="cursor:pointer;"><td style="padding:8px;border-bottom:1px solid var(--border-subtle);">' + escapeHtml(item.title) + '</td><td style="padding:8px;border-bottom:1px solid var(--border-subtle);">' + escapeHtml(ws.elementTypeLabel(item.element_type)) + '</td><td style="padding:8px;border-bottom:1px solid var(--border-subtle);">' + escapeHtml(ws.statusLabel(item.status)) + '</td><td style="padding:8px;border-bottom:1px solid var(--border-subtle);">' + escapeHtml(ws.priorityLabel(item.priority)) + '</td><td style="padding:8px;border-bottom:1px solid var(--border-subtle);">' + escapeHtml(item.assigned_to || '—') + '</td></tr>').join('');
        el.innerHTML = '<div style="overflow:auto;"><table style="width:100%;border-collapse:collapse;font-size:0.84rem;"><thead><tr><th style="text-align:left;padding:8px;border-bottom:1px solid var(--border);">Titel</th><th style="text-align:left;padding:8px;border-bottom:1px solid var(--border);">Typ</th><th style="text-align:left;padding:8px;border-bottom:1px solid var(--border);">Status</th><th style="text-align:left;padding:8px;border-bottom:1px solid var(--border);">Priorität</th><th style="text-align:left;padding:8px;border-bottom:1px solid var(--border);">Zuständig</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
        bindOpenElementTargets(el);
        document.getElementById('ws-elements-count').textContent = String(elements.length);
    }
})();
