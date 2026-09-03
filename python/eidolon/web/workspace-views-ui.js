(function () {
    const ws = window.EidolonWorkspace;
    const state = ws.state;
    const PLAN_BUCKETS = [
        { id: 'planned', label: 'Geplant', match: (item) => item.status === 'idea' || item.status === 'planned' },
        { id: 'in_progress', label: 'In Arbeit', match: (item) => item.status === 'in_progress' },
        { id: 'blocked', label: 'Blockiert', match: (item) => item.status === 'blocked' },
        { id: 'done', label: 'Erledigt', match: (item) => item.status === 'done' || item.status === 'archived' },
    ];

    function switchView() {
        const view = document.getElementById('ws-view-mode')?.value || 'board';
        document.getElementById('ws-canvas-card').style.display = view === 'canvas' ? 'block' : 'none';
        document.getElementById('ws-elements-card').style.display = view !== 'canvas' ? 'block' : 'none';
        const title = document.getElementById('ws-elements-title');
        if (title) title.textContent = view === 'board' ? 'Planung' : view === 'timeline' ? 'Timeline' : 'Liste';
        if (view === 'canvas') renderCanvas();
        else if (view === 'board') renderBoardView();
        else if (view === 'timeline') renderTimelineView();
        else renderListView();
        const filter = document.getElementById('ws-element-filter');
        if (filter && !filter.dataset.bound) {
            filter.dataset.bound = '1';
            filter.addEventListener('input', () => {
                const currentView = document.getElementById('ws-view-mode')?.value || 'board';
                if (currentView === 'board') renderBoardView();
                else if (currentView === 'timeline') renderTimelineView();
                else if (currentView === 'list') renderListView();
            });
        }
    }

    function elementTitleMap(elements) {
        const map = {};
        (elements || []).forEach((item) => { map[item.id] = item.title || item.id; });
        return map;
    }

    function relatedLabels(item, titles) {
        const labels = [];
        (item.dependencies || []).forEach((id) => labels.push(titles[id] || id));
        if (item.parent_id) labels.push(titles[item.parent_id] || item.parent_id);
        return labels;
    }

    function relatedPairs(elements) {
        const titles = elementTitleMap(elements);
        const pairs = [];
        (elements || []).forEach((item) => {
            (item.dependencies || []).forEach((id) => {
                pairs.push((titles[id] || id) + ' → ' + (item.title || item.id));
            });
            if (item.parent_id) {
                pairs.push((item.title || item.id) + ' unter ' + (titles[item.parent_id] || item.parent_id));
            }
        });
        return pairs;
    }

    function planBucketFor(item) {
        return PLAN_BUCKETS.find((bucket) => bucket.match(item)) || PLAN_BUCKETS[0];
    }

    function sortedBucketItems(elements, bucket) {
        return elements
            .filter(bucket.match)
            .map((item, index) => ({ item, index }))
            .sort((a, b) => {
                const orderA = Number.isFinite(Number(a.item.sort_order)) ? Number(a.item.sort_order) : a.index;
                const orderB = Number.isFinite(Number(b.item.sort_order)) ? Number(b.item.sort_order) : b.index;
                if (orderA !== orderB) return orderA - orderB;
                return (b.item.priority || 0) - (a.item.priority || 0);
            })
            .map((entry) => entry.item);
    }

    function priorityOptions(current) {
        return [0, 1, 2, 3, 4, 5].map((value) => {
            const selected = Number(current || 0) === value ? ' selected' : '';
            return '<option value="' + value + '"' + selected + '>' + escapeHtml(ws.priorityLabel(value)) + '</option>';
        }).join('');
    }

    function planCard(item, titles, siblings) {
        const related = relatedLabels(item, titles);
        const idx = siblings.findIndex((entry) => entry.id === item.id);
        const canUp = idx > 0;
        const canDown = idx >= 0 && idx < siblings.length - 1;
        const done = item.status === 'done' || item.status === 'archived';
        const deleteArmed = state.armedDeleteElementId === item.id;
        return '<article class="plan-card' + (done ? ' is-done' : '') + '" data-status="' + escapeHtml(item.status || 'idea') + '" data-element-id="' + escapeHtml(item.id) + '">' +
            '<div class="plan-card-head">' +
                '<input class="plan-title-input" data-plan-field="title" value="' + escapeHtml(item.title || '') + '" aria-label="Titel">' +
                '<span class="tag info">' + escapeHtml(ws.elementTypeLabel(item.element_type)) + '</span>' +
            '</div>' +
            (related.length
                ? '<div class="plan-related">Verwandt: ' + related.map((label) => '<span class="summary-chip">' + escapeHtml(label) + '</span>').join(' ') + '</div>'
                : '<div class="plan-related muted">Keine Verknüpfung</div>') +
            '<div class="plan-card-actions">' +
                '<select class="plan-priority" data-plan-field="priority" aria-label="Priorität">' + priorityOptions(item.priority) + '</select>' +
                '<button class="btn btn-sm" data-plan-action="reorder" data-direction="up"' + (canUp ? '' : ' disabled') + ' title="Nach oben">↑</button>' +
                '<button class="btn btn-sm" data-plan-action="reorder" data-direction="down"' + (canDown ? '' : ' disabled') + ' title="Nach unten">↓</button>' +
                '<button class="btn btn-sm" data-plan-action="toggle-done">' + (done ? 'Wieder öffnen' : 'Erledigt') + '</button>' +
                '<button class="btn btn-sm" data-plan-action="delete">' + (deleteArmed ? 'Nochmal löschen' : 'Löschen') + '</button>' +
                '<button class="btn btn-sm" data-plan-action="details">Details</button>' +
            '</div>' +
        '</article>';
    }

    function bindPlanBoard(root) {
        root.querySelectorAll('[data-plan-field="title"]').forEach((input) => {
            input.addEventListener('keydown', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    input.blur();
                }
            });
            input.addEventListener('blur', () => {
                const card = input.closest('[data-element-id]');
                if (!card) return;
                patchPlanElement(card.dataset.elementId, { title: input.value.trim() });
            });
        });
        root.querySelectorAll('[data-plan-field="priority"]').forEach((select) => {
            select.addEventListener('change', () => {
                const card = select.closest('[data-element-id]');
                if (!card) return;
                patchPlanElement(card.dataset.elementId, { priority: parseInt(select.value, 10) || 0 });
            });
        });
        root.querySelectorAll('[data-plan-action]').forEach((btn) => {
            btn.addEventListener('click', (event) => {
                event.preventDefault();
                event.stopPropagation();
                const card = btn.closest('[data-element-id]');
                if (!card) return;
                const elementId = card.dataset.elementId;
                const action = btn.dataset.planAction;
                if (action === 'reorder') reorderPlanElement(elementId, btn.dataset.direction);
                else if (action === 'toggle-done') togglePlanDone(elementId);
                else if (action === 'delete') deletePlanElement(elementId);
                else if (action === 'details') {
                    const item = state.currentProject?.elements?.find((entry) => entry.id === elementId);
                    openElementForm(elementId, Number(item?.position?.x || 0), Number(item?.position?.y || 0));
                }
            });
        });
    }

    async function patchPlanElement(elementId, payload) {
        if (!state.currentProjectId || !elementId) return;
        const current = state.currentProject?.elements?.find((entry) => entry.id === elementId);
        if (!current) return;
        if (payload.title !== undefined) {
            if (!payload.title) { showNotice('Titel erforderlich', 'warning'); renderBoardView(); return; }
            if (payload.title === current.title) return;
        }
        if (payload.priority !== undefined && Number(payload.priority) === Number(current.priority || 0)) return;
        try {
            const response = await api('PUT', '/projects/' + state.currentProjectId + '/elements/' + elementId, payload);
            if (response?.ok === false) { showNotice(response.error || 'Element speichern fehlgeschlagen', 'error'); return; }
            showNotice('Element aktualisiert', 'success', 1400);
            await openProject(state.currentProjectId);
        } catch (e) { showNotice(e.message, 'error'); }
    }

    async function togglePlanDone(elementId) {
        const current = state.currentProject?.elements?.find((entry) => entry.id === elementId);
        if (!current) return;
        const next = (current.status === 'done' || current.status === 'archived') ? 'planned' : 'done';
        await patchPlanElement(elementId, { status: next });
    }

    async function reorderPlanElement(elementId, direction) {
        const elements = state.currentProject?.elements || [];
        const current = elements.find((entry) => entry.id === elementId);
        if (!current) return;
        const siblings = sortedBucketItems(elements, planBucketFor(current));
        const idx = siblings.findIndex((entry) => entry.id === elementId);
        const swapIdx = direction === 'up' ? idx - 1 : idx + 1;
        if (idx < 0 || swapIdx < 0 || swapIdx >= siblings.length) return;
        const other = siblings[swapIdx];
        try {
            const first = await api('PUT', '/projects/' + state.currentProjectId + '/elements/' + current.id, { sort_order: swapIdx });
            if (first?.ok === false) { showNotice(first.error || 'Reihenfolge speichern fehlgeschlagen', 'error'); return; }
            const second = await api('PUT', '/projects/' + state.currentProjectId + '/elements/' + other.id, { sort_order: idx });
            if (second?.ok === false) { showNotice(second.error || 'Reihenfolge speichern fehlgeschlagen', 'error'); return; }
            showNotice('Reihenfolge gespeichert', 'success', 1400);
            await openProject(state.currentProjectId);
        } catch (e) { showNotice(e.message, 'error'); }
    }

    async function deletePlanElement(elementId) {
        if (!state.currentProjectId || !elementId) return;
        if (state.armedDeleteElementId !== elementId) {
            state.armedDeleteElementId = elementId;
            renderBoardView();
            showNotice('Löschen ist scharf gestellt', 'warning', 2200);
            setTimeout(() => {
                if (state.armedDeleteElementId === elementId) {
                    state.armedDeleteElementId = null;
                    const view = document.getElementById('ws-view-mode')?.value || 'board';
                    if (view === 'board') renderBoardView();
                }
            }, 2200);
            return;
        }
        state.armedDeleteElementId = null;
        try {
            const response = await api('DELETE', '/projects/' + state.currentProjectId + '/elements/' + elementId);
            if (response?.ok === false) { showNotice(response.error || 'Element löschen fehlgeschlagen', 'error'); return; }
            showNotice('Element gelöscht', 'success');
            await openProject(state.currentProjectId);
        } catch (e) { showNotice(e.message, 'error'); }
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
        const titles = elementTitleMap(elements);
        const filteredElements = filterText
            ? elements.filter((item) => item.title.toLowerCase().includes(filterText) || (item.description || '').toLowerCase().includes(filterText) || relatedLabels(item, titles).some((label) => label.toLowerCase().includes(filterText)))
            : elements;
        const pairs = relatedPairs(filteredElements);
        const relatedHtml = '<div class="plan-related-strip"><div class="card-header" style="margin-bottom:8px;"><h3 style="font-size:0.9rem;">Verwandt</h3><span class="tag info">' + pairs.length + '</span></div>' +
            (pairs.length ? pairs.map((pair) => '<div class="comp-row"><span class="comp-detail">' + escapeHtml(pair) + '</span></div>').join('') : '<div class="empty">Keine Abhängigkeiten oder Hierarchie im Kernel</div>') +
            '</div>';

        if (!elements.length) {
            el.innerHTML = relatedHtml + '<div class="empty">Keine Elemente für die Planung vorhanden</div>';
            document.getElementById('ws-elements-count').textContent = '0';
            return;
        }

        const columns = PLAN_BUCKETS.map((bucket) => {
            const items = sortedBucketItems(filteredElements, bucket);
            const body = items.length
                ? items.map((item) => planCard(item, titles, items)).join('')
                : '<div class="empty">Leer</div>';
            return '<div class="plan-column" data-plan-bucket="' + bucket.id + '"><div class="card-header" style="margin-bottom:8px;"><h3 style="font-size:0.9rem;">' + escapeHtml(bucket.label) + '</h3><span class="tag info">' + items.length + '</span></div>' + body + '</div>';
        }).join('');
        el.innerHTML = relatedHtml + '<div class="plan-board">' + columns + '</div>';
        bindPlanBoard(el);
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

    Object.assign(window, {
        switchView,
        renderBoardView,
        renderTimelineView,
        renderListView,
        patchPlanElement,
        reorderPlanElement,
        togglePlanDone,
        deletePlanElement,
    });
})();
