(function () {
    const ws = window.EidolonWorkspace;
    const state = ws.state;

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

    const PLANNING_COLUMNS = [
        ['idea', 'Zusammengehörig'],
        ['planned', 'Geplant'],
        ['in_progress', 'In Arbeit'],
        ['blocked', 'Blockiert'],
        ['done', 'Fertig'],
        ['archived', 'Archiv'],
    ];
    const PLANNING_STATUS_OPTIONS = [
        ['idea', 'Zusammengehörig'],
        ['planned', 'Geplant'],
        ['in_progress', 'In Arbeit'],
        ['blocked', 'Blockiert'],
        ['done', 'Fertig'],
        ['archived', 'Archiviert'],
    ];

    function planningColumnFor(status) {
        if (status === 'ready') return 'planned';
        if (PLANNING_COLUMNS.some(([key]) => key === status)) return status;
        return 'idea';
    }

    function statusOptions(selected) {
        return PLANNING_STATUS_OPTIONS.map(([value, label]) =>
            '<option value="' + value + '"' + (value === selected ? ' selected' : '') + '>' + escapeHtml(label) + '</option>'
        ).join('');
    }

    function priorityOptions(selected) {
        return [0, 1, 2, 3, 4, 5].map((value) =>
            '<option value="' + value + '"' + (Number(selected || 0) === value ? ' selected' : '') + '>' + escapeHtml(ws.priorityLabel(value)) + '</option>'
        ).join('');
    }

    function relatedLabel(item, elements) {
        if (!item.parent_id) return '';
        const parent = (elements || []).find((entry) => entry.id === item.parent_id);
        return parent ? ('Gehört zu: ' + parent.title) : ('Gehört zu: ' + item.parent_id);
    }

    function relatedOptions(item, elements) {
        const choices = [['', 'Keine Gruppe']].concat(
            (elements || [])
                .filter((entry) => entry.id !== item.id)
                .map((entry) => [entry.id, entry.title || entry.id])
        );
        return choices.map(([value, label]) =>
            '<option value="' + escapeHtml(value) + '"' + (String(item.parent_id || '') === String(value) ? ' selected' : '') + '>' + escapeHtml(label) + '</option>'
        ).join('');
    }

    function elementCard(item) {
        const elements = state.currentProject?.elements || [];
        const related = relatedLabel(item, elements);
        return '<div class="goal-card plan-card" data-status="' + escapeHtml(item.status || 'idea') + '" data-element-id="' + escapeHtml(item.id) + '" draggable="true">' +
            '<div class="goal-stripe"></div><div class="goal-body">' +
            '<div class="comp-detail">' + escapeHtml(ws.elementTypeLabel(item.element_type)) + (related ? ' · ' + escapeHtml(related) : '') + '</div>' +
            '<input class="plan-card-title" data-plan-field="title" data-element-id="' + escapeHtml(item.id) + '" value="' + escapeHtml(item.title || '') + '">' +
            '<select class="plan-card-status" data-plan-field="status" data-element-id="' + escapeHtml(item.id) + '">' + statusOptions(item.status || 'idea') + '</select>' +
            '<select class="plan-card-related" data-plan-field="parent_id" data-element-id="' + escapeHtml(item.id) + '">' + relatedOptions(item, elements) + '</select>' +
            '<select class="plan-card-priority" data-plan-field="priority" data-element-id="' + escapeHtml(item.id) + '">' + priorityOptions(item.priority) + '</select>' +
            '<div class="plan-card-actions">' +
            '<button class="btn btn-sm" data-open-element-id="' + escapeHtml(item.id) + '" data-x="' + Number(item.position?.x || 0) + '" data-y="' + Number(item.position?.y || 0) + '">Details</button>' +
            '<button class="btn btn-sm" data-plan-archive="' + escapeHtml(item.id) + '">Ablegen</button>' +
            '<button class="btn btn-sm" data-plan-drop="' + escapeHtml(item.id) + '">' + (state.armedDropElementId === item.id ? 'Nochmal streichen' : 'Streichen') + '</button>' +
            '</div>' +
            '</div></div>';
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
        if (!el) return;
        const filterInput = document.getElementById('ws-element-filter');
        const filterText = filterInput ? filterInput.value.toLowerCase().trim() : '';
        const filteredElements = filterText
            ? elements.filter(item => item.title.toLowerCase().includes(filterText) || (item.description || '').toLowerCase().includes(filterText))
            : elements;

        const columns = PLANNING_COLUMNS;
        el.innerHTML = '<div class="planning-board">' + columns.map(([status, label]) => {
            const items = filteredElements.filter((item) => planningColumnFor(item.status) === status);
            const body = items.length
                ? items.map((item) => elementCard(item)).join('')
                : '<div class="empty">Leer</div>';
            return '<div class="card planning-column" data-plan-column="' + status + '"><div class="card-header" style="margin-bottom:8px;"><h3 style="font-size:0.9rem;">' + escapeHtml(label) + '</h3><span class="tag info">' + items.length + '</span></div>' + body + '</div>';
        }).join('') + '</div>';
        bindOpenElementTargets(el);
        bindPlanningBoard(el);
        document.getElementById('ws-elements-count').textContent = String(filteredElements.length);
    }

    async function persistPlanElement(elementId, patch) {
        if (!state.currentProjectId || !elementId) return false;
        const response = await api('PUT', '/projects/' + state.currentProjectId + '/elements/' + elementId, patch);
        if (response?.ok === false) { showNotice(response.error || 'Element speichern fehlgeschlagen', 'error'); return false; }
        return true;
    }

    async function persistPlanOrder(elementIds) {
        if (!state.currentProjectId || !Array.isArray(elementIds)) return false;
        const response = await api('POST', '/projects/' + state.currentProjectId + '/elements/reorder', { element_ids: elementIds });
        if (response?.ok === false) { showNotice(response.error || 'Reihenfolge speichern fehlgeschlagen', 'error'); return false; }
        return true;
    }

    async function updatePlanElement(elementId, patch) {
        try {
            const nextPatch = { ...patch };
            if (Object.prototype.hasOwnProperty.call(nextPatch, 'parent_id') && !nextPatch.parent_id) {
                nextPatch.parent_id = null;
            }
            if (await persistPlanElement(elementId, nextPatch)) await openProject(state.currentProjectId);
        } catch (e) { showNotice(e.message, 'error'); }
    }

    async function reorderPlanElements(elementIds) {
        try {
            if (await persistPlanOrder(elementIds)) await openProject(state.currentProjectId);
        } catch (e) { showNotice(e.message, 'error'); }
    }

    async function archivePlanElement(elementId) {
        await updatePlanElement(elementId, { status: 'archived' });
    }

    async function dropPlanElement(elementId) {
        if (!state.currentProjectId || !elementId) return;
        if (state.armedDropElementId !== elementId) {
            state.armedDropElementId = elementId;
            renderBoardView();
            showNotice('Streichen ist scharf gestellt — zweiter Klick löscht dauerhaft.', 'warning', 2200);
            setTimeout(() => {
                if (state.armedDropElementId === elementId) {
                    state.armedDropElementId = null;
                    if (document.getElementById('ws-view-mode')?.value === 'board') renderBoardView();
                }
            }, 2200);
            return;
        }
        state.armedDropElementId = null;
        try {
            const response = await api('DELETE', '/projects/' + state.currentProjectId + '/elements/' + elementId);
            if (response?.ok === false) { showNotice(response.error || 'Element streichen fehlgeschlagen', 'error'); return; }
            showNotice('Element gestrichen', 'success');
            await openProject(state.currentProjectId);
        } catch (e) { showNotice(e.message, 'error'); }
    }

    function collectBoardOrder() {
        const ids = [];
        document.querySelectorAll('.planning-column .plan-card').forEach((card) => {
            if (card.dataset.elementId) ids.push(card.dataset.elementId);
        });
        (state.currentProject?.elements || []).forEach((item) => {
            if (!ids.includes(item.id)) ids.push(item.id);
        });
        return ids;
    }

    function bindPlanningBoard(root) {
        root.querySelectorAll('[data-plan-field]').forEach((field) => {
            field.addEventListener('change', () => {
                const key = field.dataset.planField;
                let value = field.value;
                if (key === 'priority') value = parseInt(value, 10) || 0;
                if (key === 'parent_id') value = value || null;
                updatePlanElement(field.dataset.elementId, { [key]: value });
            });
        });
        root.querySelectorAll('[data-plan-archive]').forEach((btn) => {
            btn.addEventListener('click', (event) => {
                event.stopPropagation();
                archivePlanElement(btn.dataset.planArchive);
            });
        });
        root.querySelectorAll('[data-plan-drop]').forEach((btn) => {
            btn.addEventListener('click', (event) => {
                event.stopPropagation();
                dropPlanElement(btn.dataset.planDrop);
            });
        });
        root.querySelectorAll('.plan-card').forEach((card) => {
            card.addEventListener('dragstart', (event) => {
                event.dataTransfer.setData('text/plain', card.dataset.elementId || '');
                event.dataTransfer.effectAllowed = 'move';
            });
        });
        root.querySelectorAll('.planning-column').forEach((column) => {
            column.addEventListener('dragover', (event) => {
                event.preventDefault();
                column.classList.add('drop-target');
            });
            column.addEventListener('dragleave', () => column.classList.remove('drop-target'));
            column.addEventListener('drop', async (event) => {
                event.preventDefault();
                column.classList.remove('drop-target');
                const elementId = event.dataTransfer.getData('text/plain');
                const nextStatus = column.dataset.planColumn;
                const card = root.querySelector('.plan-card[data-element-id="' + elementId + '"]');
                if (card) column.appendChild(card);
                try {
                    if (elementId && nextStatus) await persistPlanElement(elementId, { status: nextStatus });
                    await persistPlanOrder(collectBoardOrder());
                    await openProject(state.currentProjectId);
                } catch (e) { showNotice(e.message, 'error'); }
            });
        });
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

    Object.assign(window, { switchView, renderBoardView, renderTimelineView, renderListView, updatePlanElement, reorderPlanElements, archivePlanElement, dropPlanElement });
})();
