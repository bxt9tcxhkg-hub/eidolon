async function loadGoals() {
    try {
        const d = await api('GET', '/api/v1/operate/goals');
        const payload = d.data || {};
        allGoals = payload.goals || [];
        renderGoalsList();
        renderGoalStats(payload.stats);
    } catch (e) { const el = document.getElementById('goals-list'); if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>'; }
}
function renderGoalsList() {
    const el = document.getElementById('goals-list');
    if (!allGoals.length) { el.innerHTML = '<div class="empty">Keine Ziele</div>'; return; }
    el.innerHTML = allGoals.map(g => {
        const allowed = Array.isArray(g.allowed_transitions) ? g.allowed_transitions : [];
        const actions = [];
        actions.push('<button class="btn btn-sm" onclick="toggleGoalComposer(true, ' + escapeHtml(JSON.stringify(g)) + ')">Bearbeiten</button>');
        if (allowed.includes('active')) actions.push('<button class="btn btn-sm" onclick="transitionGoal(\'' + g.id + '\', \'active\')">Starten</button>');
        if (allowed.includes('paused')) actions.push('<button class="btn btn-sm" onclick="transitionGoal(\'' + g.id + '\', \'paused\')">Pausieren</button>');
        if (allowed.includes('done')) actions.push('<button class="btn btn-sm" onclick="transitionGoal(\'' + g.id + '\', \'done\')">Erledigt</button>');
        if (allowed.includes('failed')) actions.push('<button class="btn btn-sm" onclick="transitionGoal(\'' + g.id + '\', \'failed\')">Fehlgeschlagen</button>');
        if (!['done', 'cancelled'].includes(g.status)) actions.push('<button class="btn btn-sm" onclick="deleteGoal(\'' + g.id + '\')">' + (armedGoalDeleteId === g.id ? 'Nochmal löschen' : 'Löschen') + '</button>');
        const actionHtml = actions.length ? actions.join('') : '<span class="tag info">Keine Aktionen</span>';
        const detail = [g.problem_key, g.verify_state ? 'verify: ' + g.verify_state : '', g.evidence || ''].filter(Boolean).join(' · ');
        return '<div class="goal-card" data-status="' + escapeHtml(g.status) + '"><div class="goal-stripe"></div><div class="goal-body"><div class="goal-head"><div class="goal-headline"><span class="status-chip">' + escapeHtml(g.status) + '</span><div class="goal-title">' + escapeHtml(g.title) + '</div></div></div><div class="comp-detail" style="margin:6px 0 10px 0;">' + escapeHtml(detail) + '</div><div class="goal-actions">' + actionHtml + '</div></div></div>';
    }).join('');
}

function renderGoalActionResult(title, data) {
    const el = document.getElementById('goals-action-result');
    if (!el) return;
    el.innerHTML = '<div class="card" style="padding:10px;margin-top:8px;"><div style="font-size:0.78rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">' + escapeHtml(title) + '</div><pre class="code-block" style="display:block;white-space:pre-wrap;max-height:260px;overflow:auto;">' + escapeHtml(JSON.stringify(data, null, 2)) + '</pre></div>';
}
function renderGoalStats(stats) {
    const el = document.getElementById('goals-stats');
    if (!stats) return;
    const activeCount = stats.active_count ?? stats.active ?? 0;
    const doneCount = stats.done_count ?? stats.done ?? 0;
    el.innerHTML = '<div class="status-tiles"><div class="status-tile"><div class="num">' + (stats.total || 0) + '</div><div class="lbl">Gesamt</div></div><div class="status-tile" data-t="active"><div class="num">' + activeCount + '</div><div class="lbl">Aktiv</div></div><div class="status-tile" data-t="done"><div class="num">' + doneCount + '</div><div class="lbl">Erledigt</div></div></div>';
}
function populateGoalComposer(goal) {
    currentGoalId = goal?.id || null;
    document.getElementById('goal-composer-title').textContent = currentGoalId ? 'Ziel bearbeiten' : 'Neues Ziel';
    document.getElementById('goal-inline-title').value = goal?.title || '';
    document.getElementById('goal-inline-description').value = goal?.description || '';
    document.getElementById('goal-inline-category').value = goal?.category || 'system';
    document.getElementById('goal-inline-priority').value = String(goal?.priority || 3);
    document.getElementById('goal-inline-steps').value = Array.isArray(goal?.steps) ? goal.steps.map(s => s.title || '').join('\n') : '';
}
function toggleGoalComposer(forceVisible, goal) {
    const card = document.getElementById('goal-composer-card');
    if (!card) return;
    const nextVisible = typeof forceVisible === 'boolean' ? forceVisible : !goalComposerVisible;
    goalComposerVisible = nextVisible;
    card.style.display = nextVisible ? 'block' : 'none';
    if (nextVisible) {
        populateGoalComposer(goal || null);
        document.getElementById('goal-inline-title')?.focus();
    } else {
        currentGoalId = null;
        populateGoalComposer(null);
    }
}
async function submitGoalForm() {
    const title = document.getElementById('goal-inline-title').value.trim();
    if (!title) {
        showNotice('Titel erforderlich', 'warning');
        return;
    }
    const payload = {
        title,
        description: document.getElementById('goal-inline-description').value.trim(),
        category: document.getElementById('goal-inline-category').value,
        priority: parseInt(document.getElementById('goal-inline-priority').value, 10) || 3,
        steps: document.getElementById('goal-inline-steps').value,
    };
    try {
        const editing = Boolean(currentGoalId);
        const d = currentGoalId ? await api('PUT', '/api/v1/operate/goals/' + currentGoalId, payload) : await api('POST', '/api/v1/operate/goals', payload);
        renderGoalActionResult(editing ? 'Ziel aktualisieren' : 'Ziel anlegen', d.data || d);
        if (d?.ok === false) { showNotice((d.error && d.error.message) || d.error || 'Ziel speichern fehlgeschlagen', 'error'); return; }
        toggleGoalComposer(false);
        loadGoals();
        loadGoalLog();
        showNotice(editing ? 'Ziel aktualisiert' : 'Ziel angelegt', 'success');
    } catch (e) {
        showNotice(e.message, 'error');
    }
}
async function transitionGoal(id, status) {
    try {
        const d = await api('POST', '/api/v1/operate/goals/' + id + '/transition', { status });
        renderGoalActionResult('Statuswechsel', d.data || d);
        if (d?.ok === false) { showNotice((d.error && d.error.message) || d.error || 'Statuswechsel fehlgeschlagen', 'error'); return; }
        loadGoals();
        loadGoalLog();
        showNotice('Status geändert: ' + status, 'success');
    } catch (e) { showNotice(e.message, 'error'); }
}
async function deleteGoal(id) {
    if (armedGoalDeleteId !== id) {
        armedGoalDeleteId = id;
        renderGoalsList();
        showNotice('Löschen ist scharf gestellt', 'warning', 2200);
        setTimeout(() => {
            if (armedGoalDeleteId === id) {
                armedGoalDeleteId = null;
                renderGoalsList();
            }
        }, 2200);
        return;
    }
    armedGoalDeleteId = null;
    try {
        const d = await api('DELETE', '/api/v1/operate/goals/' + id);
        renderGoalActionResult('Ziel löschen', d.data || d);
        if (d?.ok === false) { showNotice((d.error && d.error.message) || d.error || 'Löschen fehlgeschlagen', 'error'); return; }
        loadGoals();
        loadGoalLog();
        showNotice('Ziel gelöscht', 'success');
    } catch (e) { showNotice(e.message, 'error'); }
}
async function deriveGoals() {
    try {
        const d = await api('GET', '/api/v1/operate/derive');
        const payload = d.data || {};
        renderGoalActionResult('Abgeleitete Vorschläge', payload);
        if (d?.ok === false) { showNotice((d.error && d.error.message) || d.error || 'Ableitung fehlgeschlagen', 'error'); return; }
        showNotice((payload.proposals?.length || 0) + ' Vorschläge', 'info');
    } catch (e) { showNotice(e.message, 'error'); }
}
async function runAutonomyCycle() {
    try {
        const d = await api('POST', '/api/v1/operate/cycle', {});
        renderGoalActionResult('Autonomie-Zyklus', d.data || d);
        if (d?.ok === false) { showNotice((d.error && d.error.message) || d.error || 'Zyklus fehlgeschlagen', 'error'); return; }
        loadGoals();
        loadGoalLog();
        showNotice('Zyklus ausgeführt', 'success');
    } catch (e) { showNotice(e.message, 'error'); }
}
async function revalidateGoals() {
    try {
        const d = await api('POST', '/api/v1/operate/revalidate', {});
        renderGoalActionResult('Revalidierung', d.data || d);
        if (d?.ok === false) { showNotice((d.error && d.error.message) || d.error || 'Revalidierung fehlgeschlagen', 'error'); return; }
        loadGoals();
        loadGoalLog();
        showNotice('Geprüft', 'success');
    } catch (e) { showNotice(e.message, 'error'); }
}
async function loadGoalLog() {
    try {
        const d = await api('GET', '/api/v1/operate/overview');
        const el = document.getElementById('goals-log');
        const rows = (d.data && d.data.history) || [];
        if (!rows.length) { el.innerHTML = '<div class="empty">Kein Verlauf</div>'; return; }
        el.innerHTML = rows.slice(-20).reverse().map(entry => '<div class="comp-row"><span class="comp-name">' + escapeHtml(entry.timestamp || entry.created_at || '—') + '</span><span class="comp-detail">' + escapeHtml((entry.kind || 'event') + ' · ' + (entry.title || entry.message || entry.event || '—')) + '</span></div><div style="margin:-4px 0 8px 0;color:var(--text-dim);font-size:0.78rem;line-height:1.4;">' + escapeHtml(entry.summary || entry.message || '') + '</div>').join('');
    } catch (e) {
        const el = document.getElementById('goals-log');
        if (el) el.innerHTML = '<span class="tag err">' + e.message + '</span>';
    }
}

// Identity
