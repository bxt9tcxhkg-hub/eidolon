(function () {
    const ws = window.EidolonWorkspace = window.EidolonWorkspace || {};
    ws.state = ws.state || {
        currentProjectId: null,
        currentProject: null,
        brainstormData: [],
        armedDeleteElementId: null,
        armedDeleteProjectId: null,
        armedDropElementId: null,
        canvas: {
            zoom: 1,
            panX: 0,
            panY: 0,
            mode: 'move',
            selected: new Set(),
            dragging: false,
            dragStart: { x: 0, y: 0 },
            panStart: { x: 0, y: 0 },
            linkSource: null,
        },
    };

    ws.projectListEl = () => document.getElementById('ws-projects-list');
    ws.projectDetailEl = () => document.getElementById('ws-project-detail');
    ws.projectComposerEl = () => document.getElementById('project-create-panel');
    ws.elementComposerEl = () => document.getElementById('ws-element-composer');

    ws.resetElementComposerPosition = function resetElementComposerPosition(x = 0, y = 0) {
        document.getElementById('task-x').value = Math.round(x || 0);
        document.getElementById('task-y').value = Math.round(y || 0);
    };

    ws.clearElementComposer = function clearElementComposer() {
        document.getElementById('task-id').value = '';
        document.getElementById('task-title').value = '';
        document.getElementById('task-description').value = '';
        document.getElementById('task-priority').value = '0';
        document.getElementById('task-domain').value = 'idea';
        document.getElementById('task-status').value = 'idea';
        const parentField = document.getElementById('task-parent-id');
        if (parentField) parentField.value = '';
        document.getElementById('task-assigned-to').value = '';
        document.getElementById('task-due-at').value = '';
        const deleteBtn = document.getElementById('task-delete-btn');
        if (deleteBtn) {
            deleteBtn.style.display = 'none';
            deleteBtn.textContent = 'Löschen';
        }
        ws.state.armedDeleteElementId = null;
        ws.resetElementComposerPosition(0, 0);
    };

    ws.closeElementComposer = function closeElementComposer() {
        const panel = ws.elementComposerEl();
        if (!panel) return;
        panel.style.display = 'none';
        ws.clearElementComposer();
    };

    function closeTaskForm() {
        ws.closeElementComposer();
    }

    function statusLabel(status) {
        const labels = { idea: 'Zusammengehörig', planned: 'Geplant', in_progress: 'In Arbeit', active: 'In Arbeit', blocked: 'Blockiert', done: 'Fertig', archived: 'Archiviert', ready: 'Geplant' };
        return labels[status] || status || 'Unklar';
    }

    function elementTypeLabel(type) {
        const labels = { idea: 'Idee', task: 'Aufgabe', note: 'Notiz', decision: 'Entscheidung', deliverable: 'Ergebnis', milestone: 'Meilenstein' };
        return labels[type] || type || 'Element';
    }

    function priorityLabel(priority) {
        const labels = { 0: 'Keine', 1: 'Niedrig', 2: 'Normal', 3: 'Erhöht', 4: 'Hoch', 5: 'Kritisch' };
        return labels[priority] || ('P' + String(priority || 0));
    }

    ws.statusLabel = statusLabel;
    ws.elementTypeLabel = elementTypeLabel;
    ws.priorityLabel = priorityLabel;
    ws.closeTaskForm = closeTaskForm;

    window.closeTaskForm = closeTaskForm;
})();
