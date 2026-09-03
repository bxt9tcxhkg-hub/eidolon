(function () {
    const ws = window.EidolonWorkspace;
    const state = ws.state;

    function renderWorkspaceContext(ctx) {
        const el = document.getElementById('ws-context-summary');
        if (!el) return;
        if (!ctx || Object.keys(ctx).length === 0) {
            el.innerHTML = '<div class="empty">Kein abgeleiteter Arbeitskontext verfügbar</div>';
            return;
        }
        const listOrDash = (items) => Array.isArray(items) && items.length ? items.join(', ') : '—';
        const operate = ctx.operate || {};
        const run = operate.run || {};
        const objective = operate.objective || {};
        const rows = [
            ['Workflow-Schleife', listOrDash(ctx.workflow_loop)],
            ['Operate-Zustand', run.state || '—'],
            ['Operate-Phase', run.canonical_phase || run.current_phase || ctx.current_phase || '—'],
            ['Operate-Ziel', objective.title || ctx.current_focus_label || '—'],
            ['Aktive Pods', String((operate.active_pods || operate.subagents || []).length)],
            ['Operate-Blocker', String((operate.blockers || []).filter(item => item.status === 'open').length)],
            ['Operate-Freigaben', String((operate.approvals || []).filter(item => item.status === 'pending').length)],
            ['Kontextzustand', ctx.current_context_state || '—'],
            ['Aktueller Fokus', ctx.current_focus_label || '—'],
            ['Aktiver Projektkontext', ctx.current_conversation_project || '—'],
            ['Aktive Projektfläche', ctx.active_surface_project || '—'],
            ['Projektkandidaten (Labels)', listOrDash(ctx.candidate_labels)],
            ['Chat-Themen (Labels)', listOrDash(ctx.topic_labels)],
            ['Projektkandidaten', String(ctx.project_candidate_count ?? 0)],
            ['Chat-Themen', String(ctx.chat_topic_count ?? 0)],
            ['Kontextwechsel', ctx.context_shift_state || 'same_project'],
            ['Nächster Übergang', ctx.next_transition || '—'],
            ['Nächster Schritt', ctx.next_step || '—'],
            ['Freigaberahmen', ctx.approval_state || '—'],
            ['Verantwortliche Rolle', ctx.responsible_role || 'eidolon-core'],
        ];
        el.innerHTML = rows.map(([label, value]) => '<div class="comp-row"><span class="comp-name">' + escapeHtml(label) + '</span><span class="comp-detail">' + escapeHtml(value) + '</span></div>').join('');
    }

    function renderProjectList(projects) {
        const el = ws.projectListEl();
        if (!el) return;
        renderProjectListFiltered(projects);
        const searchInput = document.getElementById('ws-project-search');
        if (searchInput && !searchInput.dataset.bound) {
            searchInput.dataset.bound = '1';
            searchInput.addEventListener('input', () => renderProjectListFiltered(projects));
        }
    }

    function renderProjectListFiltered(projects) {
        const el = ws.projectListEl();
        if (!el) return;
        const searchInput = document.getElementById('ws-project-search');
        const searchText = searchInput ? searchInput.value.toLowerCase().trim() : '';
        const filtered = searchText
            ? projects.filter(p => p.title.toLowerCase().includes(searchText) || (p.description || '').toLowerCase().includes(searchText))
            : projects;

        if (!filtered?.length) {
            el.innerHTML = '<div class="empty">Keine Projekte</div>';
            return;
        }
        window.__testProjectButtons = filtered.map((p) => p.id);
        el.innerHTML = filtered.map((p) =>
            '<div class="goal-card" data-status="' + (p.status || 'active') + '">' +
                '<div class="goal-stripe"></div>' +
                '<div class="goal-body">' +
                    '<div class="goal-head"><div class="goal-headline"><span class="status-chip">' + escapeHtml(p.status || 'Aktiv') + '</span><div class="goal-title">' + escapeHtml(p.title) + '</div></div></div>' +
                    '<div class="comp-detail" style="margin:8px 0 12px 0;">' + escapeHtml(p.description || 'Keine Beschreibung') + '</div>' +
                    '<div class="goal-actions">' +
                        '<button class="btn btn-sm btn-primary" data-action="open-project" data-id="' + escapeHtml(p.id) + '">Öffnen</button>' +
                        '<button class="btn btn-sm" data-action="delete-project" data-id="' + escapeHtml(p.id) + '">' + (state.armedDeleteProjectId === p.id ? 'Nochmal löschen' : 'Löschen') + '</button>' +
                    '</div>' +
                '</div>' +
            '</div>'
        ).join('');
        el.querySelectorAll('[data-action="open-project"]').forEach((btn) => btn.addEventListener('click', () => openProject(btn.dataset.id)));
        el.querySelectorAll('[data-action="delete-project"]').forEach((btn) => btn.addEventListener('click', () => deleteProject(btn.dataset.id)));
    }

    function renderProjectStats(project) {
        const el = document.getElementById('ws-project-stats');
        if (!el || !project) return;
        const elements = project.elements || [];
        const inboxOpen = (project.inbox || []).filter((item) => !item.processed).length;
        const rows = [
            ['Status', ws.statusLabel(project.status || 'active')],
            ['Domäne', project.domain || '—'],
            ['Elemente', String(elements.length)],
            ['Geplant', String(elements.filter((item) => item.status === 'idea' || item.status === 'planned').length)],
            ['In Arbeit', String(elements.filter((item) => item.status === 'in_progress').length)],
            ['Blockiert', String(elements.filter((item) => item.status === 'blocked').length)],
            ['Erledigt', String(elements.filter((item) => item.status === 'done').length)],
            ['Terminiert', String(elements.filter((item) => item.due_at).length)],
            ['Inbox offen', String(inboxOpen)],
        ];
        el.innerHTML = rows.map(([label, value]) => '<div class="comp-row"><span class="comp-name">' + escapeHtml(label) + '</span><span class="comp-detail">' + escapeHtml(value) + '</span></div>').join('');
    }

    async function loadWorkspaces() {
        const overview = await api('GET', '/workspaces');
        const contextData = overview.context_model || {};
        const operate = overview.operate || {};
        renderProjectList((overview.workspaces || []).filter((item) => item.workspace_type === 'project_workspace').map((item) => ({
            id: String(item.workspace_id || '').replace(/^project_/, ''),
            title: item.topic_label,
            description: item.metadata?.project_description || item.overview || '',
            status: item.metadata?.project_status || item.state || 'active',
        })));
        renderWorkspaceContext({ ...contextData, operate });
    }

    function toggleProjectComposer(forceVisible) {
        const panel = ws.projectComposerEl();
        if (!panel) return;
        const nextVisible = typeof forceVisible === 'boolean' ? forceVisible : panel.style.display === 'none';
        panel.style.display = nextVisible ? 'block' : 'none';
        if (nextVisible) document.getElementById('project-title')?.focus();
    }

    function resetProjectForm() {
        document.getElementById('project-title').value = '';
        document.getElementById('project-description').value = '';
        document.getElementById('project-domain').value = 'general';
        toggleProjectComposer(false);
    }

    async function submitProjectForm() {
        const title = document.getElementById('project-title').value.trim();
        const description = document.getElementById('project-description').value.trim();
        const domain = document.getElementById('project-domain').value.trim();
        if (!title) { showNotice('Projekttitel erforderlich', 'warning'); return; }
        try {
            const response = await api('POST', '/projects', { title, description, domain });
            if (response?.ok === false) { showNotice(response.error || 'Projekt anlegen fehlgeschlagen', 'error'); return; }
            showNotice('Projekt angelegt', 'success');
            resetProjectForm();
            await loadWorkspaces();
        } catch (e) { showNotice(e.message, 'error'); }
    }

    async function openProject(projectId) {
        try {
            if (ws.projectListEl()) ws.projectListEl().style.display = 'none';
            if (ws.projectDetailEl()) ws.projectDetailEl().style.display = 'block';
            const titleEl = document.getElementById('ws-detail-title');
            if (titleEl) titleEl.textContent = 'Lade Projekt…';
            const viewMode = document.getElementById('ws-view-mode');
            if (viewMode) viewMode.value = 'board';
            renderProjectStats({title: 'Lade…', elements: [], inbox: [], status: 'active', domain: '—'});
            ws.closeElementComposer();
            window.switchView();
            const response = await api('GET', '/projects/' + projectId);
            if (!response) { showNotice('Projekt konnte nicht geladen werden', 'error'); return; }
            if (response.ok === false) { showNotice(response.error || 'Projekt nicht geladen', 'error'); return; }
            const project = response.project || response;
            if (!project || !project.id) { showNotice('Unerwartetes Projektformat', 'error'); return; }
            state.currentProjectId = project.id;
            state.currentProject = project;
            if (titleEl) titleEl.textContent = project.title || 'Unbenannt';
            renderProjectStats(project);
            window.switchView();
        } catch (e) { showNotice(e.message || 'Projekt öffnen fehlgeschlagen', 'error'); }
    }

    function showProjectList() {
        state.currentProjectId = null;
        state.currentProject = null;
        if (ws.projectListEl()) ws.projectListEl().style.display = 'block';
        if (ws.projectDetailEl()) ws.projectDetailEl().style.display = 'none';
        ws.closeElementComposer();
        loadWorkspaces();
    }

    async function deleteProject(projectId) {
        if (state.armedDeleteProjectId !== projectId) {
            state.armedDeleteProjectId = projectId;
            await loadWorkspaces();
            showNotice('Projektlöschen ist scharf gestellt', 'warning', 2200);
            setTimeout(async () => {
                if (state.armedDeleteProjectId === projectId) {
                    state.armedDeleteProjectId = null;
                    await loadWorkspaces();
                }
            }, 2200);
            return;
        }
        state.armedDeleteProjectId = null;
        try {
            const response = await api('DELETE', '/projects/' + projectId);
            if (response?.ok === false) { showNotice(response.error || 'Projekt löschen fehlgeschlagen', 'error'); return; }
            showNotice('Projekt gelöscht', 'success');
            await loadWorkspaces();
        } catch (e) { showNotice(e.message, 'error'); }
    }

    async function generateBrainstorm() {
        const text = document.getElementById('brainstorm-text').value.trim();
        if (!text) { showNotice('Beschreibe zuerst dein Projekt', 'warning'); return; }
        try {
            const response = await api('POST', '/projects/' + state.currentProjectId + '/brainstorm', { text });
            if (response?.ok === false) { showNotice(response.error || 'Brainstorm fehlgeschlagen', 'error'); return; }
            state.brainstormData = response.suggestions || [];
            renderBrainstorm(state.brainstormData);
        } catch (e) { showNotice(e.message, 'error'); }
    }

    function renderBrainstorm(suggestions) {
        const el = document.getElementById('brainstorm-suggestions');
        if (!suggestions?.length) { el.innerHTML = '<div class="empty">Keine Vorschläge</div>'; return; }
        el.innerHTML = suggestions.map((item, index) => {
            const type = item.type || 'fehlt';
            const colors = { fehlt: 'var(--accent)', verbessern: 'var(--warning)', kontext: 'var(--success)' };
            const labels = { fehlt: 'Fehlt', verbessern: 'Verbessern', kontext: 'Kontext' };
            const bc = colors[type] || colors.fehlt;
            const label = labels[type] || '';
            return '<div class="comp-row" style="background:var(--bg);border-radius:6px;padding:10px 12px;border-left:3px solid ' + bc + ';">' +
                '<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">' +
                    '<span class="cat-badge" style="background:' + bc + '22;color:' + bc + ';border:1px solid ' + bc + '44;">' + label + '</span>' +
                    '<span class="comp-name" style="flex:1;">' + escapeHtml(item.title) + '</span>' +
                '</div>' +
                '<span class="comp-detail" style="display:block;margin-bottom:8px;">' + escapeHtml(item.reason || '') + '</span>' +
                '<div style="display:flex;gap:6px;">' +
                    '<button class="btn btn-sm btn-primary" data-suggestion-action="accept" data-index="' + index + '">Übernehmen</button>' +
                    '<button class="btn btn-sm" data-suggestion-action="reject" data-index="' + index + '">Ablehnen</button>' +
                '</div>' +
            '</div>';
        }).join('');
        el.querySelectorAll('[data-suggestion-action="accept"]').forEach((btn) => btn.addEventListener('click', () => acceptSuggestion(Number(btn.dataset.index))));
        el.querySelectorAll('[data-suggestion-action="reject"]').forEach((btn) => btn.addEventListener('click', () => rejectSuggestion(Number(btn.dataset.index))));
    }

    async function acceptSuggestion(index) {
        const item = state.brainstormData[index];
        if (!item || !state.currentProjectId) return;
        const payload = { title: item.title, description: item.reason, status: 'idea', priority: 1, element_type: 'idea', dependencies: item.connect_to ? [item.connect_to] : [] };
        try {
            const response = await api('POST', '/projects/' + state.currentProjectId + '/elements', payload);
            if (response?.ok === false) { showNotice(response.error || 'Vorschlag übernehmen fehlgeschlagen', 'error'); return; }
            showNotice('Element hinzugefügt' + (item.connect_to ? ' (verknüpft)' : ''), 'success');
            await openProject(state.currentProjectId);
        } catch (e) { showNotice(e.message, 'error'); }
    }

    function rejectSuggestion(index) {
        state.brainstormData.splice(index, 1);
        renderBrainstorm(state.brainstormData);
    }

    function clearBrainstorm() {
        document.getElementById('brainstorm-text').value = '';
        document.getElementById('brainstorm-suggestions').innerHTML = '<div class="empty" style="text-align:center;padding:20px;color:var(--text-muted);">Beschreibe dein Projekt und frage die KI nach fehlenden Bausteinen.</div>';
        state.brainstormData = [];
    }

    Object.assign(window, { loadWorkspaces, toggleProjectComposer, resetProjectForm, submitProjectForm, openProject, showProjectList, deleteProject, generateBrainstorm, acceptSuggestion, rejectSuggestion, clearBrainstorm });
})();
