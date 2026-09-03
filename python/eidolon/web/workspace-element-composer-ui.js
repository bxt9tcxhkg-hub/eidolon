(function () {
    const ws = window.EidolonWorkspace;
    const state = ws.state;

    async function addDependency(fromId, toId) {
        const from = state.currentProject?.elements?.find((entry) => entry.id === fromId);
        if (!from) return;
        from.dependencies = from.dependencies || [];
        const previous = [...from.dependencies];
        if (from.dependencies.includes(toId)) from.dependencies = from.dependencies.filter((id) => id !== toId);
        else from.dependencies.push(toId);
        try {
            const response = await api('PUT', '/projects/' + state.currentProjectId + '/elements/' + fromId, { dependencies: from.dependencies });
            if (response?.ok === false) { from.dependencies = previous; showNotice(response.error || 'Verknüpfung speichern fehlgeschlagen', 'error'); renderCanvas(); return; }
            await openProject(state.currentProjectId);
        } catch (e) { from.dependencies = previous; showNotice(e.message, 'error'); renderCanvas(); }
    }

    async function assignHierarchy(childId, parentId) {
        if (!childId || !parentId || childId === parentId) return;
        const child = state.currentProject?.elements?.find((entry) => entry.id === childId);
        if (!child) return;
        const previous = child.parent_id || null;
        child.parent_id = child.parent_id === parentId ? null : parentId;
        try {
            const response = await api('PUT', '/projects/' + state.currentProjectId + '/elements/' + childId, { parent_id: child.parent_id });
            if (response?.ok === false) { child.parent_id = previous; showNotice(response.error || 'Hierarchie speichern fehlgeschlagen', 'error'); renderCanvas(); return; }
            showNotice(child.parent_id ? 'Hierarchie verknüpft' : 'Hierarchie gelöst', 'success', 1800);
            await openProject(state.currentProjectId);
        } catch (e) { child.parent_id = previous; showNotice(e.message, 'error'); renderCanvas(); }
    }

    function openElementForm(elementId, x, y) {
        const panel = ws.elementComposerEl();
        if (!panel) return;
        const existing = elementId ? state.currentProject?.elements?.find((entry) => entry.id === elementId) : null;
        document.getElementById('ws-element-composer-title').textContent = existing ? 'Element direkt bearbeiten' : 'Element direkt anlegen';
        document.getElementById('task-id').value = existing?.id || '';
        document.getElementById('task-title').value = existing?.title || '';
        document.getElementById('task-description').value = existing?.description || '';
        document.getElementById('task-priority').value = String(existing?.priority || 0);
        document.getElementById('task-domain').value = existing?.element_type || 'idea';
        document.getElementById('task-status').value = existing?.status || 'idea';
        document.getElementById('task-assigned-to').value = existing?.assigned_to || '';
        document.getElementById('task-due-at').value = existing?.due_at || '';
        ws.resetElementComposerPosition(existing?.position?.x ?? x ?? 0, existing?.position?.y ?? y ?? 0);
        const deleteBtn = document.getElementById('task-delete-btn');
        if (deleteBtn) { deleteBtn.style.display = existing ? 'inline-flex' : 'none'; deleteBtn.textContent = 'Löschen'; }
        state.armedDeleteElementId = null;
        panel.style.display = 'block';
        document.getElementById('task-title')?.focus();
    }

    async function submitTaskForm() {
        const id = document.getElementById('task-id').value;
        const payload = {
            title: document.getElementById('task-title').value.trim(),
            description: document.getElementById('task-description').value.trim(),
            priority: parseInt(document.getElementById('task-priority').value, 10) || 0,
            element_type: document.getElementById('task-domain').value || 'idea',
            status: document.getElementById('task-status').value || 'idea',
            assigned_to: document.getElementById('task-assigned-to').value.trim(),
            due_at: document.getElementById('task-due-at').value || '',
            position: { x: parseFloat(document.getElementById('task-x').value) || 0, y: parseFloat(document.getElementById('task-y').value) || 0 },
        };
        if (!payload.title) { showNotice('Titel erforderlich', 'warning'); return; }
        const route = id ? '/projects/' + state.currentProjectId + '/elements/' + id : '/projects/' + state.currentProjectId + '/elements';
        const method = id ? 'PUT' : 'POST';
        try {
            const response = await api(method, route, payload);
            if (response?.ok === false) { showNotice(response.error || 'Element speichern fehlgeschlagen', 'error'); return; }
            showNotice(id ? 'Element aktualisiert' : 'Element angelegt', 'success');
            ws.closeElementComposer();
            await openProject(state.currentProjectId);
        } catch (e) { showNotice(e.message, 'error'); }
    }

    async function deleteElement(elementId) {
        openElementForm(elementId);
        const deleteBtn = document.getElementById('task-delete-btn');
        if (deleteBtn) deleteBtn.textContent = 'Nochmal klicken zum Löschen';
        state.armedDeleteElementId = elementId;
        showNotice('Element im Direkteditor geöffnet — zweiter Klick löscht.', 'warning', 2200);
    }

    async function deleteCurrentComposerElement() {
        const elementId = document.getElementById('task-id').value;
        const deleteBtn = document.getElementById('task-delete-btn');
        if (!elementId) return;
        if (state.armedDeleteElementId !== elementId) {
            state.armedDeleteElementId = elementId;
            if (deleteBtn) deleteBtn.textContent = 'Nochmal klicken zum Löschen';
            showNotice('Löschen ist scharf gestellt', 'warning', 2200);
            setTimeout(() => {
                if (state.armedDeleteElementId === elementId) {
                    state.armedDeleteElementId = null;
                    if (deleteBtn) deleteBtn.textContent = 'Löschen';
                }
            }, 2200);
            return;
        }
        state.armedDeleteElementId = null;
        if (deleteBtn) deleteBtn.textContent = 'Löschen';
        try {
            const response = await api('DELETE', '/projects/' + state.currentProjectId + '/elements/' + elementId);
            if (response?.ok === false) { showNotice(response.error || 'Element löschen fehlgeschlagen', 'error'); return; }
            showNotice('Element gelöscht', 'success');
            ws.closeElementComposer();
            await openProject(state.currentProjectId);
        } catch (e) { showNotice(e.message, 'error'); }
    }

    Object.assign(window, { switchView, renderBoardView, renderTimelineView, renderListView, renderCanvas, canvasMouseDown, canvasMouseMove, canvasMouseUp, canvasWheel, canvasZoomIn, canvasZoomOut, canvasResetView, canvasDoubleClick, setCanvasMode, openElementForm, submitTaskForm, deleteElement, deleteCurrentComposerElement, assignHierarchy });
})();
})();
