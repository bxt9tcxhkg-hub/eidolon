function chatHasUserMessage() {
    return (chatMessages || []).some((m) => m && m.role === 'user' && String(m.content || '').trim());
}

function syncChatIdleLayout(runtimeContext) {
    const panel = document.getElementById('panel-chat');
    if (!panel) return;
    const idle = !chatHasUserMessage();
    panel.classList.toggle('chat-is-idle', idle);
    const prompt = document.getElementById('chat-idle-prompt');
    if (prompt) {
        prompt.textContent = idle
            ? 'Woran sollen wir arbeiten?'
            : 'Sag mir, was du erreichen willst oder woran ich weiterarbeiten soll.';
    }
}

function chatAuxHasWork(el) {
    return Boolean(el && el.querySelector('.chat-operate-item'));
}

function hideEmptyChatAux(el) {
    if (!el) return;
    el.hidden = !chatAuxHasWork(el);
}

function activeProjectDoorTitle(runtimeContext, overview) {
    const project = (runtimeContext && runtimeContext.project_context) || {};
    const operate = (runtimeContext && runtimeContext.operate_context) || {};
    const objective = (overview && overview.objective) || {};
    const raw = project.active_project_title || operate.objective_title || objective.title || '';
    const title = String(raw || '').trim();
    if (!title || /operate workspace bridge/i.test(title) || title === 'Kein Fokus') return '';
    const state = ((runtimeContext && runtimeContext.workflow_state) || {}).current_context_state;
    const hasRun = Boolean(operate.run_id || (overview && overview.run && overview.run.id));
    if (state !== 'active_project' && !project.active_project_id && !hasRun) return '';
    return title;
}

function renderChatProjectDoor(runtimeContext, overview) {
    const el = document.getElementById('chat-project-door');
    if (!el) return;
    const title = activeProjectDoorTitle(runtimeContext, overview);
    if (!title) {
        el.hidden = true;
        el.innerHTML = '';
        return;
    }
    el.hidden = false;
    el.innerHTML = '<button type="button" class="chat-project-door-link" data-tab-target="workspaces">'
        + escapeHtml(title) + ' · öffnen</button>';
}

function renderChatRuntimeContext(runtimeContext) {
    lastChatRuntimeContext = runtimeContext || null;
    syncChatIdleLayout(runtimeContext);
    const idle = !chatHasUserMessage();
    if (!runtimeContext) {
        if (typeof setEidolonPresence === 'function') {
            setEidolonPresence('idle', 'Bereit für neue Arbeit', 'Starte ein Gespräch oder setze bestehende Arbeit fort.');
        }
        renderChatFormation(null);
        renderChatOperateActionsFromContext(null);
        if (typeof loadChatLandingSummary === 'function') loadChatLandingSummary();
        syncChatIdleLayout(null);
        return;
    }
    const workflow = runtimeContext.workflow_state || {};
    const project = runtimeContext.project_context || {};
    const intent = runtimeContext.user_intent || {};
    const focus = project.active_project_title || project.candidate_project_title || (project.topic_labels || [])[0] || '';
    const readableFocus = focus && /operate workspace bridge/i.test(focus) ? '' : focus;
    const phase = workflow.current_phase || 'await_input';
    const classification = intent.classification || 'unknown';
    const workOriented = Boolean(intent.is_work_oriented);
    const social = !workOriented || classification === 'casual_chat' || classification === 'general_chat' || classification === 'general_chat_with_work_context';

    if (!idle) {
        renderChatFormation((runtimeContext && runtimeContext.formation) || null);
    } else {
        renderChatFormation(null);
    }
    if (social) {
        if (typeof setEidolonPresence === 'function') {
            setEidolonPresence('idle', 'Bereit für Gespräch', readableFocus ? (readableFocus + ' ist verfügbar, aber nicht erzwungen.') : 'Normale Unterhaltung ohne aktiven Arbeitslauf.');
        }
        if (!idle) renderChatOperateActionsFromContext(null);
    } else {
        if (typeof setEidolonPresence === 'function') {
            const waiting = ['await_input', 'await_user', 'approval', 'await_approval'].includes(String(phase || '').toLowerCase());
            setEidolonPresence(waiting ? 'waiting' : 'thinking', waiting ? 'Wartet auf dich' : 'Strukturiert Arbeit', workflow.next_step || readableFocus || '');
        }
        if (!idle) renderChatOperateActionsFromContext(runtimeContext);
    }
    if (typeof loadChatLandingSummary === 'function') loadChatLandingSummary();
    syncChatIdleLayout(runtimeContext);
}

function operateActionButton(label, action, args, primary) {
    return '<button class="btn btn-sm' + (primary ? ' btn-primary' : '') + '" data-ui-action="' + escapeHtml(action) + '" data-ui-args="' + escapeHtml(JSON.stringify(args)) + '">' + escapeHtml(label) + '</button>';
}

function pendingOperateApprovals(items) {
    return (Array.isArray(items) ? items : []).filter((item) => item && item.id && (item.status === 'pending' || item.is_pending || !item.status));
}

function openOperateBlockers(items) {
    return (Array.isArray(items) ? items : []).filter((item) => item && item.id && (item.status === 'open' || item.is_open || !item.status));
}

function renderChatOperateDoor(targetEl, data) {
    if (!targetEl) return;
    const run = data.run || {};
    const runId = run.id || data.run_id || '';
    const nextAction = data.next_action || {};
    const approvals = pendingOperateApprovals(data.pending_approvals || data.approvals);
    const blockers = openOperateBlockers(data.open_blockers || data.blockers);
    const parts = [];
    approvals.forEach((item) => {
        parts.push('<div class="chat-operate-item">'
            + '<div class="summary-headline">' + escapeHtml(item.title || 'Freigabe') + '</div>'
            + '<div class="summary-copy">' + escapeHtml(item.summary || 'Diese Aktion wartet auf deine Entscheidung.') + '</div>'
            + '<div class="summary-copy">Freigabe speichert die Entscheidung. Buchung, Mail oder externe Aktion folgen nicht — kein Executor.</div>'
            + (runId ? '<div class="chat-operate-buttons">'
                + operateActionButton('Freigeben', 'resolveOperateApproval', [runId, item.id, 'approved'], true)
                + operateActionButton('Ablehnen', 'resolveOperateApproval', [runId, item.id, 'rejected'], false)
                + '</div>' : '')
            + '</div>');
    });
    blockers.forEach((item) => {
        parts.push('<div class="chat-operate-item">'
            + '<div class="summary-headline">' + escapeHtml(item.title || 'Blocker') + '</div>'
            + '<div class="summary-copy">' + escapeHtml(item.summary || item.resolution_hint || 'Dieser Blocker hält die Arbeit an.') + '</div>'
            + (runId ? '<div class="chat-operate-buttons">'
                + operateActionButton('Weiter / lösen', 'resolveOperateBlocker', [runId, item.id], true)
                + '</div>' : '')
            + '</div>');
    });
    if (runId && nextAction.kind === 'approval_request' && !approvals.length) {
        parts.push('<div class="chat-operate-item">'
            + '<div class="summary-headline">' + escapeHtml(nextAction.title || 'Freigabe') + '</div>'
            + '<div class="summary-copy">' + escapeHtml(nextAction.summary || 'Freigabe erneut anfordern — Ausführung ist nicht angebunden.') + '</div>'
            + '<div class="chat-operate-buttons">'
            + operateActionButton('Freigabe erneut anfordern', 'requestOperateApproval', [runId], false)
            + '</div>'
            + '</div>');
    }
    if (runId && nextAction.kind === 'next_step' && nextAction.action_enabled && !approvals.length && !blockers.length) {
        parts.push('<div class="chat-operate-item">'
            + '<div class="summary-headline">' + escapeHtml(nextAction.title || 'Nächster Schritt') + '</div>'
            + '<div class="summary-copy">' + escapeHtml(nextAction.summary || 'Schreibt nur die Phase weiter — keine Ausführung.') + '</div>'
            + '<div class="chat-operate-buttons">'
            + operateActionButton(nextAction.action_label || 'Phase fortschreiben', 'advanceOperateRun', [runId], true)
            + '</div>'
            + '</div>');
    }
    if (!parts.length) {
        targetEl.innerHTML = '';
        targetEl.hidden = true;
        return;
    }
    targetEl.hidden = false;
    targetEl.innerHTML = parts.join('');
}

function renderChatOperateActionsFromContext(runtimeContext) {
    const el = document.getElementById('chat-operate-actions');
    if (!el) return;
    const operate = (runtimeContext && runtimeContext.operate_context) || {};
    if (!operate.run_id && !pendingOperateApprovals(operate.pending_approvals).length && !openOperateBlockers(operate.open_blockers).length) {
        el.innerHTML = '';
        el.hidden = true;
        return;
    }
    renderChatOperateDoor(el, {
        run: { id: operate.run_id, state: operate.run_state },
        run_id: operate.run_id,
        next_action: operate.next_action || {},
        pending_approvals: operate.pending_approvals || [],
        open_blockers: operate.open_blockers || [],
    });
    hideEmptyChatAux(el);
}

function renderChatFormation(formation) {
    const el = document.getElementById('chat-formation');
    if (!el) return;
    const data = formation || {};
    if (!data.visible || !data.workspace_id || !data.to_state) {
        el.innerHTML = '';
        el.hidden = true;
        return;
    }
    const label = data.label || 'Aktueller Kontext';
    const confirmNeeded = Boolean(data.requires_confirmation);
    const why = data.why || (confirmNeeded
        ? 'Erst mit deiner Bestätigung wird daraus ein dauerhaftes Projekt.'
        : 'Der Übergang bleibt sichtbar und legt noch kein dauerhaftes Projekt an.');
    const summary = data.summary ? String(data.summary) : '';
    const copy = confirmNeeded
        ? ('Projekt: ' + label + '. ' + why)
        : ('Thema: ' + label + '. ' + why);
    const confirmArgs = [data.workspace_id, data.to_state, confirmNeeded, Boolean(data.seed_board)];
    const buttons = [];
    if (data.action_enabled) {
        buttons.push(operateActionButton(data.action_label || (confirmNeeded ? 'Ja, übernehmen' : 'Als Kandidat merken'), 'applyChatFormation', confirmArgs, true));
        if (data.decline_to_state) {
            buttons.push(operateActionButton(data.decline_label || 'Nein, nur im Chat', 'applyChatFormation', [data.workspace_id, data.decline_to_state, false, false], false));
        }
    }
    el.innerHTML = '<div class="chat-operate-item chat-formation-card">'
        + '<div class="summary-headline">' + escapeHtml(confirmNeeded ? 'Daraus ein Projekt machen?' : (data.action_label || 'Projektbildung')) + '</div>'
        + '<div class="summary-copy">' + escapeHtml(copy) + '</div>'
        + (summary ? '<div class="summary-copy">' + escapeHtml(summary) + '</div>' : '')
        + '<div class="summary-meta"><span class="summary-chip">' + escapeHtml(data.from_state || data.current_state || '') + '</span><span class="summary-chip">→ ' + escapeHtml(data.to_state) + '</span></div>'
        + (buttons.length ? '<div class="chat-operate-buttons">' + buttons.join('') + '</div>' : '')
        + '</div>';
    el.hidden = false;
}

async function applyChatFormation(workspaceId, toState, confirmed, seedBoard) {
    const response = await api('POST', '/workspaces/formation', {
        workspace_id: workspaceId,
        to_state: toState,
        confirmed: Boolean(confirmed),
        seed_board: Boolean(seedBoard || (confirmed && toState === 'active_project')),
        reason: confirmed ? 'user_confirmed_promotion' : (toState === 'chat_topic' ? 'user_declined_promotion' : 'visible_proactive_formation'),
    });
    if (response?.ok === false) {
        showNotice(response.error || response.detail || 'Projektbildung fehlgeschlagen', 'error');
        return;
    }
    const seeded = (response && response.seeded_elements) || [];
    if (confirmed && toState === 'active_project') {
        showNotice(seeded.length ? ('Projekt übernommen, ' + seeded.length + ' Karten auf dem Board') : 'Projekt übernommen', 'success');
    } else if (toState === 'chat_topic') {
        showNotice('Bleibt im Chat, kein Projekt angelegt', 'info');
    } else {
        showNotice('Kandidat sichtbar gesetzt', 'success');
    }
    if (typeof refreshOperateSurfaces === 'function') await refreshOperateSurfaces();
    else if (typeof loadChatLandingSummary === 'function') await loadChatLandingSummary();
    if (typeof loadWorkspaces === 'function') await loadWorkspaces();
}

async function loadChatLandingSummary() {
    try {
        const overview = await api('GET', '/api/v1/operate/overview');
        const data = overview?.data || {};
        const kernel = data.work_kernel || lastChatRuntimeContext || {};
        if (typeof refreshWorkTraces === 'function') refreshWorkTraces(data);
        const presence = typeof describeOperatePresence === 'function'
            ? describeOperatePresence(data)
            : { state: 'idle', title: 'Bereit für neue Arbeit', detail: 'Starte ein Gespräch oder setze bestehende Arbeit fort.' };
        if (typeof setEidolonPresence === 'function') {
            setEidolonPresence(presence.state, presence.title, presence.detail);
        }
        renderChatProjectDoor(lastChatRuntimeContext || kernel, data);
        if (!chatHasUserMessage()) {
            renderChatFormation(null);
            const actionsEl = document.getElementById('chat-operate-actions');
            if (actionsEl) {
                actionsEl.innerHTML = '';
                actionsEl.hidden = true;
            }
        } else {
            renderChatFormation(kernel.formation || data.formation);
            renderChatOperateActionsFromContext(lastChatRuntimeContext || kernel);
        }
        syncChatIdleLayout(lastChatRuntimeContext);
    } catch (_) {
        renderChatProjectDoor(lastChatRuntimeContext, null);
        syncChatIdleLayout(lastChatRuntimeContext);
    }
}
window.loadChatLandingSummary = loadChatLandingSummary;
window.renderChatFormation = renderChatFormation;
window.applyChatFormation = applyChatFormation;

async function loadChatRuntimeContext(sessionId) {
    if (!sessionId) {
        renderChatRuntimeContext(null);
        return null;
    }
    try {
        const result = await api('GET', '/chat/context?session_id=' + encodeURIComponent(sessionId));
        renderChatRuntimeContext(result.runtime_context || null);
        return result.runtime_context || null;
    } catch (_) {
        renderChatRuntimeContext(null);
        return null;
    }
}

async function loadChatSelfReflection() {
    try {
        const result = await api('GET', '/api/v1/self-reflection/text');
        return result?.data?.text || null;
    } catch (_) {
        return null;
    }
}
function loadStoredChatMessages() {
    try {
        const raw = localStorage.getItem('eidolon-chat-messages');
        const parsed = JSON.parse(raw || '[]');
        if (!Array.isArray(parsed)) return [];
        return parsed.filter(m => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string').slice(-100);
    } catch (_) {
        return [];
    }
}
function persistChatMessages() {
    try {
        const serializable = (chatMessages || []).map((m) => ({ role: m.role, content: m.content }));
        localStorage.setItem('eidolon-chat-messages', JSON.stringify(serializable.slice(-100)));
    } catch (_) {}
}
function getStoredChatSessionId() {
    try { return localStorage.getItem('eidolon-chat-current-session') || ''; } catch (_) { return ''; }
}
function persistCurrentChatSessionId() {
    try {
        if (currentChatSessionId) localStorage.setItem('eidolon-chat-current-session', currentChatSessionId);
    } catch (_) {}
}
function clearCurrentChatSessionId() {
    try { localStorage.removeItem('eidolon-chat-current-session'); } catch (_) {}
}
function formatSessionTimestamp(value) {
    if (!value) return 'ohne Zeit';
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return 'ohne Zeit';
    return d.toLocaleString('de-DE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}
function describeSessionAge(value) {
    if (!value) return 'Unbekannt';
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return 'Unbekannt';
    const now = new Date();
    const startNow = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const startThen = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    const diffDays = Math.round((startNow - startThen) / 86400000);
    if (diffDays <= 0) return 'Heute';
    if (diffDays === 1) return 'Gestern';
    if (diffDays <= 7) return 'Diese Woche';
    return 'Älter';
}
function groupChatSessions(sessions) {
    const groups = new Map();
    for (const session of sessions || []) {
        const label = describeSessionAge(session.updated_at || session.created_at);
        if (!groups.has(label)) groups.set(label, []);
        groups.get(label).push(session);
    }
    return ['Heute', 'Gestern', 'Diese Woche', 'Älter']
        .filter(label => groups.has(label))
        .map(label => ({ label, items: groups.get(label) }));
}
async function ensureChatSession() {
    const stored = getStoredChatSessionId();
    if (stored) {
        const existing = await api('GET', '/chat/sessions/' + encodeURIComponent(stored));
        if (existing?.ok && existing.session) {
            currentChatSessionId = existing.session.session_id;
            chatMessages = (existing.session.messages || []).map(m => ({ role: m.role, content: m.content }));
            persistCurrentChatSessionId();
            renderChat();
            await loadChatRuntimeContext(currentChatSessionId);
            await loadChatSessions();
            return existing.session;
        }
        clearCurrentChatSessionId();
    }
    if (chatSessions.length) {
        return await selectChatSession(chatSessions[0].session_id, { skipListReload: true });
    }
    const listed = await api('GET', '/chat/sessions');
    const sessions = listed.sessions || [];
    if (sessions.length) {
        chatSessions = sessions;
        renderChatSessions(chatSessions);
        return await selectChatSession(sessions[0].session_id, { skipListReload: true });
    }
    return await createChatSession();
}
function renderChatSessions(sessions) {
    const el = document.getElementById('chat-sessions');
    const titleEl = document.getElementById('chat-session-title');
    const summaryEl = document.getElementById('chat-session-summary');
    if (!el) return;
    const query = (document.getElementById('chat-session-search')?.value || '').trim().toLowerCase();
    const filtered = (sessions || []).filter(s => {
        if (!query) return true;
        const haystack = [s.title, s.last_message_preview, s.source].filter(Boolean).join(' ').toLowerCase();
        return haystack.includes(query);
    });
    const groups = groupChatSessions(filtered);
    const rows = groups.map(group => {
        const items = group.items.map(s => {
            const active = s.session_id === currentChatSessionId;
            const title = escapeHtml(s.title || 'Neue Unterhaltung');
            const preview = escapeHtml((s.last_message_preview || 'Noch keine Nachrichten').slice(0, 140));
            const updated = escapeHtml(formatSessionTimestamp(s.updated_at || s.created_at));
            const count = Number(s.message_count || 0);
            return '<div class="chat-session-item' + (active ? ' active' : '') + '" onclick="openChatSession(\'' + s.session_id + '\')">'
                + '<div class="chat-session-main">'
                + '<div class="chat-session-name">' + title + '</div>'
                + '<div class="chat-session-preview">' + preview + '</div>'
                + '<div class="chat-session-subline"><span>' + updated + '</span><span>' + count + ' Nachrichten</span></div>'
                + '</div>'
                + '<div class="chat-session-actions">'
                + '<button class="chat-session-close" title="Session schließen" onclick="event.stopPropagation(); deleteChatSession(\'' + s.session_id + '\')">×</button>'
                + '</div>'
                + '</div>';
        }).join('');
        return '<div class="chat-session-group"><div class="chat-session-group-label"><span>' + escapeHtml(group.label) + '</span><span class="chat-session-count">' + group.items.length + '</span></div>' + items + '</div>';
    }).join('');
    el.innerHTML = rows || '<div class="empty">Keine passenden Sessions gefunden.</div>';
    const activeSession = (sessions || []).find(s => s.session_id === currentChatSessionId) || null;
    if (titleEl) titleEl.textContent = activeSession?.title || 'Neue Unterhaltung';
    if (summaryEl) summaryEl.textContent = filtered.length + ' von ' + ((sessions || []).length) + ' Sessions sichtbar';
    if (typeof refreshWorkTraces === 'function') refreshWorkTraces();
}
async function loadChatSessions() {
    const result = await api('GET', '/chat/sessions');
    chatSessions = result.sessions || [];
    renderChatSessions(chatSessions);
    loadChatLandingSummary().catch(() => {});
    return chatSessions;
}
async function openChatSession(sessionId) {
    if (typeof showTab === 'function' && currentTab !== 'chat') showTab('chat');
    return selectChatSession(sessionId);
}
async function selectChatSession(sessionId, options = {}) {
    const result = await api('GET', '/chat/sessions/' + encodeURIComponent(sessionId));
    if (result?.ok === false || !result.session) {
        showNotice(result.error || 'Chat-Session konnte nicht geladen werden', 'error');
        return null;
    }
    currentChatSessionId = result.session.session_id;
    persistCurrentChatSessionId();
    chatMessages = (result.session.messages || []).map(m => ({ role: m.role, content: m.content }));
    persistChatMessages();
    await loadChatRuntimeContext(result.session.session_id);
    chatSessions = chatSessions.map(s => s.session_id === result.session.session_id ? {
        ...s,
        title: result.session.title,
        updated_at: result.session.updated_at,
        message_count: result.session.message_count,
        last_message_preview: ((result.session.messages || []).slice(-1)[0] || {}).content || '',
    } : s);
    renderChat();
    loadChatLandingSummary().catch(() => {});
    if (!options.skipListReload) {
        await loadChatSessions();
    } else {
        renderChatSessions(chatSessions);
    }
    return result.session;
}
async function createChatSession() {
    const result = await api('POST', '/chat/sessions', { source: 'chat' });
    if (result?.ok === false || !result.session) {
        showNotice(result.error || 'Chat-Session konnte nicht erstellt werden', 'error');
        return null;
    }
    currentChatSessionId = result.session.session_id;
    persistCurrentChatSessionId();
    chatMessages = [];
    persistChatMessages();
    chatSessions = [
        {
            session_id: result.session.session_id,
            title: result.session.title,
            source: result.session.source,
            created_at: result.session.created_at,
            updated_at: result.session.updated_at,
            message_count: result.session.message_count,
            last_message_preview: '',
        },
        ...chatSessions.filter(s => s.session_id !== result.session.session_id),
    ];
    renderChat();
    renderChatRuntimeContext(null);
    renderChatSessions(chatSessions);
    loadChatLandingSummary().catch(() => {});
    return result.session;
}
async function deleteChatSession(sessionId) {
    const wasActive = currentChatSessionId === sessionId;
    const remainingSessions = chatSessions.filter(s => s.session_id !== sessionId);
    chatSessions = remainingSessions;
    const result = await api('DELETE', '/chat/sessions/' + encodeURIComponent(sessionId));
    if (result?.ok === false) {
        await loadChatSessions();
        showNotice(result.error || 'Chat-Session konnte nicht gelöscht werden', 'error');
        return;
    }
    if (wasActive) {
        if (remainingSessions.length) {
            currentChatSessionId = remainingSessions[0].session_id;
            persistCurrentChatSessionId();
            renderChatSessions(chatSessions);
            await selectChatSession(currentChatSessionId, { skipListReload: true });
        } else {
            currentChatSessionId = null;
            clearCurrentChatSessionId();
            chatMessages = [];
            persistChatMessages();
            renderChat();
            await createChatSession();
        }
        return;
    }
    renderChatSessions(chatSessions);
    loadChatLandingSummary().catch(() => {});
}
const CHAT_STATUS_LABELS = {
    denkt: 'denkt…',
    arbeitet: 'arbeitet…',
    antwortet: 'antwortet',
};
let chatAgentStatus = null;
let chatSendInFlight = false;
let chatStatusPollTimer = null;

function chatStatusLabel(phase) {
    return CHAT_STATUS_LABELS[phase] || '';
}

function setChatAgentStatus(phase, source) {
    const label = chatStatusLabel(phase);
    chatAgentStatus = label ? { phase, label, source: source || 'local' } : null;
    renderChatAgentStatus();
    const el = document.getElementById('chat-messages');
    if (el && chatMessages.length) renderChat();
}

function clearChatAgentStatus() {
    chatAgentStatus = null;
    renderChatAgentStatus();
}

function renderChatAgentStatus() {
    const el = document.getElementById('chat-agent-status');
    const labelEl = document.getElementById('chat-agent-status-label');
    if (!el) return;
    const phase = chatAgentStatus ? chatAgentStatus.phase : 'idle';
    el.hidden = !chatAgentStatus;
    el.classList.toggle('is-visible', Boolean(chatAgentStatus));
    el.dataset.phase = phase;
    if (labelEl) labelEl.textContent = chatAgentStatus ? chatAgentStatus.label : '';
    if (typeof setEidolonTurnPhase === 'function') {
        setEidolonTurnPhase(phase);
    }
    if (chatAgentStatus) {
        el.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }
}

function stopChatStatusPoll() {
    if (chatStatusPollTimer) {
        clearInterval(chatStatusPollTimer);
        chatStatusPollTimer = null;
    }
}

function startChatStatusPoll(sessionId) {
    stopChatStatusPoll();
    if (!sessionId) return;
    chatStatusPollTimer = setInterval(async () => {
        if (!chatSendInFlight) {
            stopChatStatusPoll();
            return;
        }
        try {
            const r = await api('GET', '/chat/turn-status?session_id=' + encodeURIComponent(sessionId));
            if (r && r.phase && chatStatusLabel(r.phase)) {
                setChatAgentStatus(r.phase, 'server');
            }
        } catch (_) {}
    }, 400);
}

function chatModelText(r) {
    if (!r || typeof r !== 'object') return '';
    const candidates = [r.response, r.data && r.data.response, r.reply, r.data && r.data.reply];
    for (const value of candidates) {
        if (typeof value === 'string' && value.trim()) return value;
    }
    return '';
}

function chatErrorText(r) {
    const err = r && r.error;
    if (typeof err === 'string' && err.trim()) return err;
    if (err && typeof err === 'object') {
        const message = err.message || err.detail || err.code;
        if (typeof message === 'string' && message.trim()) return message;
    }
    return 'Keine Modellantwort erhalten';
}

function applyChatEnvelope(r) {
    if (r?.session_id) {
        currentChatSessionId = r.session_id;
        persistCurrentChatSessionId();
    }
    if (r?.runtime_context) {
        renderChatRuntimeContext(r.runtime_context);
    }
}

function applyFinishedChatReply(r) {
    applyChatEnvelope(r);
    const reply = chatModelText(r);
    if (r?.ok === false) {
        chatMessages.push({ role: 'assistant', content: 'Fehler: ' + chatErrorText(r) });
    } else if (reply) {
        chatMessages.push({ role: 'assistant', content: reply });
    } else {
        chatMessages.push({ role: 'assistant', content: 'Fehler: Keine Modellantwort erhalten' });
    }
}

function chatStreamingDraft() {
    const last = chatMessages[chatMessages.length - 1];
    return last && last.role === 'assistant' && last.streaming ? last : null;
}

function updateStreamingAssistant(text) {
    const draft = chatStreamingDraft();
    if (draft) {
        draft.content = text;
    } else {
        chatMessages.push({ role: 'assistant', content: text, streaming: true });
    }
    renderChat();
}

function finishStreamingAssistant(text) {
    const draft = chatStreamingDraft();
    if (draft) {
        draft.content = text;
        delete draft.streaming;
    } else if (text) {
        chatMessages.push({ role: 'assistant', content: text });
    }
}

function parseSseBuffer(buffer) {
    const events = [];
    const parts = String(buffer || '').split('\n\n');
    const rest = parts.pop() || '';
    for (const block of parts) {
        const dataLines = block.split('\n').filter((line) => line.startsWith('data:')).map((line) => line.slice(5).trim());
        if (!dataLines.length) continue;
        try {
            const parsed = JSON.parse(dataLines.join('\n'));
            if (parsed && typeof parsed === 'object') events.push(parsed);
        } catch (_) {}
    }
    return { events, rest };
}

async function consumeChatStream(response) {
    const reader = response.body && response.body.getReader ? response.body.getReader() : null;
    if (!reader) {
        const fallback = await response.json();
        setChatAgentStatus('antwortet', 'response');
        applyFinishedChatReply(fallback);
        return fallback;
    }
    const decoder = new TextDecoder();
    let buffer = '';
    let acc = '';
    let sawDelta = false;
    let terminal = null;
    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const parsed = parseSseBuffer(buffer);
        buffer = parsed.rest;
        for (const event of parsed.events) {
            if (event.type === 'phase' && chatStatusLabel(event.phase)) {
                setChatAgentStatus(event.phase, 'stream');
            }
            if (event.type === 'delta' && typeof event.text === 'string' && event.text) {
                if (!sawDelta) setChatAgentStatus('antwortet', 'stream');
                sawDelta = true;
                acc += event.text;
                updateStreamingAssistant(acc);
            }
            if (event.type === 'replace' && typeof event.text === 'string') {
                acc = event.text;
                if (sawDelta) updateStreamingAssistant(acc);
            }
            if (event.type === 'done' || event.type === 'error') {
                terminal = event;
            }
        }
    }
    if (buffer.trim()) {
        const parsed = parseSseBuffer(buffer + '\n\n');
        for (const event of parsed.events) {
            if (event.type === 'done' || event.type === 'error') terminal = event;
            if (event.type === 'replace' && typeof event.text === 'string') acc = event.text;
        }
    }
    applyChatEnvelope(terminal || {});
    if (!terminal) {
        if (sawDelta) finishStreamingAssistant(acc);
        else chatMessages.push({ role: 'assistant', content: 'Fehler: Keine Modellantwort erhalten' });
        return { ok: false, error: 'Keine Modellantwort erhalten' };
    }
    if (terminal.type === 'error' || terminal.ok === false) {
        const errorText = 'Fehler: ' + chatErrorText(terminal);
        if (sawDelta) finishStreamingAssistant(errorText);
        else chatMessages.push({ role: 'assistant', content: errorText });
        return terminal;
    }
    const reply = chatModelText(terminal) || acc;
    if (sawDelta) {
        finishStreamingAssistant(reply || acc);
    } else {
        setChatAgentStatus('antwortet', 'response');
        if (reply) chatMessages.push({ role: 'assistant', content: reply });
        else chatMessages.push({ role: 'assistant', content: 'Fehler: Keine Modellantwort erhalten' });
    }
    return terminal;
}

async function sendChat() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text || chatSendInFlight) return;
    if (!currentChatSessionId) {
        await ensureChatSession();
    }
    chatSendInFlight = true;
    chatMessages.push({ role: 'user', content: text });
    persistChatMessages();
    setChatAgentStatus('denkt', 'local');
    renderChat();
    input.value = '';
    startChatStatusPoll(currentChatSessionId);
    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    try {
        const pairedDevice = getStoredMobileDevice();
        const isMetaQuestion = /selbstreflexion|analysiere dich|was würdest du verbessern|reflektiere|was ist deine schwäche|was ist deine stärke/i.test(text);
        const body = { message: text, source: pairedDevice ? ('mobile:' + pairedDevice.peer_id) : 'chat', session_id: currentChatSessionId };
        if (isMetaQuestion) {
            const r = await api('POST', '/api/v1/self-reflection/chat', body);
            if (!r?.runtime_context) await loadChatRuntimeContext(currentChatSessionId);
            setChatAgentStatus('antwortet', 'response');
            applyFinishedChatReply(r);
        } else {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
                body: JSON.stringify({ ...body, stream: true }),
            });
            const contentType = response.headers.get('content-type') || '';
            if (contentType.indexOf('text/event-stream') !== -1) {
                const terminal = await consumeChatStream(response);
                if (!terminal?.runtime_context) await loadChatRuntimeContext(currentChatSessionId);
            } else {
                if (!response.ok) throw new Error(response.status + ': ' + response.statusText);
                const r = await response.json();
                if (!r?.runtime_context) await loadChatRuntimeContext(currentChatSessionId);
                setChatAgentStatus('antwortet', 'response');
                applyFinishedChatReply(r);
            }
        }
    } catch (e) {
        await loadChatRuntimeContext(currentChatSessionId);
        const draft = chatStreamingDraft();
        if (draft) finishStreamingAssistant('Fehler: ' + e.message);
        else chatMessages.push({ role: 'assistant', content: 'Fehler: ' + e.message });
    }
    stopChatStatusPoll();
    chatSendInFlight = false;
    clearChatAgentStatus();
    persistChatMessages();
    renderChat();
    loadChatLandingSummary().catch(() => {});
}
function renderChatTurn(m) {
    const role = m.role === 'user' ? 'user' : 'assistant';
    const streaming = Boolean(m.streaming);
    return '<div class="chat-turn msg ' + role + (streaming ? ' is-streaming' : '') + '" data-role="' + role + '">'
        + '<div class="chat-turn-meta"><span class="chat-turn-sender sender">' + escapeHtml(m.role === 'user' ? 'Du' : 'Eidolon') + '</span></div>'
        + '<div class="chat-turn-body">' + escapeHtml(m.content) + '</div>'
        + '</div>';
}
function renderChatStatusTurn() {
    if (!chatAgentStatus) return '';
    if (chatStreamingDraft()) return '';
    return '<div class="chat-turn chat-turn-status msg assistant" data-role="status" data-phase="' + escapeHtml(chatAgentStatus.phase) + '">'
        + '<div class="chat-turn-meta">'
        + '<span class="chat-turn-sender sender">Eidolon</span>'
        + '<span class="chat-agent-status-label">' + escapeHtml(chatAgentStatus.label) + '</span>'
        + '</div>'
        + '</div>';
}
function renderChat() {
    const el = document.getElementById('chat-messages');
    if (!el) return;
    syncChatIdleLayout(lastChatRuntimeContext);
    renderChatAgentStatus();
    if (!chatMessages.length) {
        el.innerHTML = '<div class="empty chat-idle-hint">Bereit, wenn du es bist.</div>';
        return;
    }
    el.innerHTML = chatMessages.map(renderChatTurn).join('') + renderChatStatusTurn();
    el.scrollTop = el.scrollHeight;
}

// Dashboard
