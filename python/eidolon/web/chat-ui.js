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

function renderChatRuntimeContext(runtimeContext) {
    lastChatRuntimeContext = runtimeContext || null;
    syncChatIdleLayout(runtimeContext);
    const stateEl = document.getElementById('chat-context-state');
    const intentEl = document.getElementById('chat-intent-mode');
    const nextEl = document.getElementById('chat-next-step');
    if (!stateEl || !intentEl || !nextEl) return;
    if (!runtimeContext) {
        stateEl.textContent = 'Noch kein belastbarer Arbeitskontext.';
        intentEl.textContent = 'Warte auf Arbeitssignal';
        nextEl.textContent = 'Sobald ein echter Kontext da ist, erscheint hier der nächste sinnvolle Schritt.';
        if (typeof setEidolonPresence === 'function') {
            setEidolonPresence('idle', 'Bereit für neue Arbeit', 'Starte ein Gespräch oder setze bestehende Arbeit fort.');
        }
        if (typeof loadChatLandingSummary === 'function') loadChatLandingSummary();
        syncChatIdleLayout(null);
        return;
    }
    const workflow = runtimeContext.workflow_state || {};
    const project = runtimeContext.project_context || {};
    const intent = runtimeContext.user_intent || {};
    const focus = project.active_project_title || project.candidate_project_title || (project.topic_labels || [])[0] || 'Kein Fokus';
    const readableFocus = focus && /operate workspace bridge/i.test(focus) ? 'Vorhandener Arbeitskontext' : focus;
    const contextState = workflow.current_context_state || 'no_live_context';
    const phase = workflow.current_phase || 'await_input';
    const classification = intent.classification || 'unknown';
    const workOriented = Boolean(intent.is_work_oriented);

    if (!workOriented || classification === 'casual_chat' || classification === 'general_chat' || classification === 'general_chat_with_work_context') {
        stateEl.textContent = (readableFocus && readableFocus !== 'Kein Fokus')
            ? (readableFocus + ' • Arbeitskontext verfügbar, aber für dieses Gespräch nicht erzwungen')
            : 'Normales Gespräch ohne erzwungenen Arbeitsmodus';
        intentEl.textContent = classification === 'casual_chat' ? 'normales Gespräch' : 'allgemeiner Chat';
        nextEl.textContent = 'Normale Unterhaltung aktiv — Arbeitskontext nur dann, wenn du ihn wirklich willst.';
        if (typeof setEidolonPresence === 'function') {
            setEidolonPresence('idle', 'Bereit für Gespräch', readableFocus && readableFocus !== 'Kein Fokus' ? (readableFocus + ' ist verfügbar, aber nicht erzwungen.') : 'Normale Unterhaltung ohne aktiven Arbeitslauf.');
        }
        if (typeof loadChatLandingSummary === 'function') loadChatLandingSummary();
        syncChatIdleLayout(runtimeContext);
        return;
    }

    stateEl.textContent = readableFocus + ' • Kontext: ' + contextState + ' • Phase: ' + phase;
    intentEl.textContent = classification + (intent.is_open_work_prompt ? ' • offene Arbeitsanfrage' : '');
    nextEl.textContent = workflow.next_step || 'Noch kein belastbarer nächster Schritt vorhanden.';
    if (typeof setEidolonPresence === 'function') {
        const waiting = ['await_input', 'await_user', 'approval', 'await_approval'].includes(String(phase || '').toLowerCase());
        setEidolonPresence(waiting ? 'waiting' : 'thinking', waiting ? 'Wartet auf dich' : 'Strukturiert Arbeit', workflow.next_step || (readableFocus + ' • ' + contextState));
    }
    if (typeof loadChatLandingSummary === 'function') loadChatLandingSummary();
    renderChatOperateActionsFromContext(runtimeContext);
    renderChatFormation((runtimeContext && runtimeContext.formation) || null);
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
    if (runId && nextAction.kind === 'next_step' && nextAction.action_enabled && !approvals.length && !blockers.length) {
        parts.push('<div class="chat-operate-item">'
            + '<div class="summary-headline">' + escapeHtml(nextAction.title || 'Nächster Schritt') + '</div>'
            + '<div class="summary-copy">' + escapeHtml(nextAction.summary || 'Die Arbeit kann fortgesetzt werden.') + '</div>'
            + '<div class="chat-operate-buttons">'
            + operateActionButton(nextAction.action_label || 'Weiter', 'advanceOperateRun', [runId], true)
            + '</div>'
            + '</div>');
    }
    if (!parts.length) {
        targetEl.innerHTML = '<div class="empty">Keine offenen Freigaben, Blocker oder fortsetzbaren Schritte.</div>';
        return;
    }
    targetEl.innerHTML = parts.join('');
}

function renderChatOperateActionsFromContext(runtimeContext) {
    const el = document.getElementById('chat-operate-actions');
    if (!el) return;
    const operate = (runtimeContext && runtimeContext.operate_context) || {};
    if (!operate.run_id && !pendingOperateApprovals(operate.pending_approvals).length && !openOperateBlockers(operate.open_blockers).length) {
        el.innerHTML = '<div class="empty">Keine ausführbare Operate-Aktion im aktuellen Kontext.</div>';
        return;
    }
    renderChatOperateDoor(el, {
        run: { id: operate.run_id, state: operate.run_state },
        run_id: operate.run_id,
        next_action: operate.next_action || {},
        pending_approvals: operate.pending_approvals || [],
        open_blockers: operate.open_blockers || [],
    });
}

function renderChatFormation(formation) {
    const el = document.getElementById('chat-formation');
    if (!el) return;
    const data = formation || {};
    if (!data.visible || !data.workspace_id || !data.to_state) {
        el.innerHTML = '<div class="empty">Keine sichtbare Projektbildung.</div>';
        return;
    }
    const label = data.label || 'Aktueller Kontext';
    const confirmNeeded = Boolean(data.requires_confirmation);
    const copy = confirmNeeded
        ? ('"' + label + '" ist ein Projektkandidat. Erst mit deiner Bestätigung wird daraus ein dauerhaftes Projekt — kein stiller Projekt-Bot.')
        : ('"' + label + '" kann vom Gesprächsthema zum Projektkandidaten werden. Der Übergang bleibt sichtbar.');
    const args = [data.workspace_id, data.to_state, confirmNeeded];
    el.innerHTML = '<div class="chat-operate-item">'
        + '<div class="summary-headline">' + escapeHtml(data.action_label || 'Projektbildung') + '</div>'
        + '<div class="summary-copy">' + escapeHtml(copy) + '</div>'
        + '<div class="summary-meta"><span class="summary-chip">' + escapeHtml(data.from_state || data.current_state || '') + '</span><span class="summary-chip">→ ' + escapeHtml(data.to_state) + '</span></div>'
        + (data.action_enabled ? '<div class="chat-operate-buttons">' + operateActionButton(data.action_label || 'Bestätigen', 'applyChatFormation', args, true) + '</div>' : '')
        + '</div>';
}

async function applyChatFormation(workspaceId, toState, confirmed) {
    const response = await api('POST', '/workspaces/formation', {
        workspace_id: workspaceId,
        to_state: toState,
        confirmed: Boolean(confirmed),
        reason: confirmed ? 'user_confirmed_promotion' : 'visible_proactive_formation',
    });
    if (response?.ok === false) {
        showNotice(response.error || 'Projektbildung fehlgeschlagen', 'error');
        return;
    }
    showNotice(confirmed ? 'Projekt übernommen' : 'Kandidat sichtbar gesetzt', 'success');
    if (typeof refreshOperateSurfaces === 'function') await refreshOperateSurfaces();
    else if (typeof loadChatLandingSummary === 'function') await loadChatLandingSummary();
    if (typeof loadWorkspaces === 'function') await loadWorkspaces();
}

function renderChatLandingRecentSessions() {
    const el = document.getElementById('chat-recent-summary');
    if (!el) return;
    if (!chatSessions.length) {
        el.innerHTML = '<div class="empty">Noch keine Unterhaltungen gespeichert.</div>';
        return;
    }
    el.innerHTML = '<div class="summary-list">' + chatSessions.slice(0, 3).map(session => {
        const active = session.session_id === currentChatSessionId;
        const title = escapeHtml(session.title || 'Neue Unterhaltung');
        const preview = escapeHtml((session.last_message_preview || 'Noch keine Nachrichten').slice(0, 96));
        const updated = escapeHtml(formatSessionTimestamp(session.updated_at || session.created_at));
        return '<div class="summary-list-item">'
            + '<div class="summary-headline">' + title + (active ? ' <span class="summary-chip">Aktuell</span>' : '') + '</div>'
            + '<div class="summary-copy">' + preview + '</div>'
            + '<div class="summary-meta"><span class="summary-chip">' + updated + '</span><span class="summary-chip">' + Number(session.message_count || 0) + ' Nachrichten</span></div>'
            + '</div>';
    }).join('') + '</div>';
}

async function loadChatLandingSummary() {
    renderChatLandingRecentSessions();
    const activeEl = document.getElementById('chat-active-summary');
    const decisionEl = document.getElementById('chat-decision-summary');
    if (!activeEl || !decisionEl) return;
    try {
        const overview = await api('GET', '/api/v1/operate/overview');
        const data = overview?.data || {};
        const kernel = data.work_kernel || lastChatRuntimeContext || {};
        const operateCtx = kernel.operate_context || {};
        const run = data.run || (operateCtx.run_id ? { id: operateCtx.run_id, state: operateCtx.run_state } : null);
        const objective = data.objective || (operateCtx.objective_title ? { title: operateCtx.objective_title } : null);
        const blockers = openOperateBlockers(operateCtx.open_blockers || data.blockers);
        const approvals = pendingOperateApprovals(operateCtx.pending_approvals || data.approvals);
        const nextAction = operateCtx.next_action || data.next_action || {};
        const history = Array.isArray(data.history) ? data.history : [];
        const presence = typeof describeOperatePresence === 'function'
            ? describeOperatePresence(data)
            : { state: 'idle', title: 'Bereit für neue Arbeit', detail: 'Starte ein Gespräch oder setze bestehende Arbeit fort.' };
        if (typeof setEidolonPresence === 'function') {
            setEidolonPresence(presence.state, presence.title, presence.detail);
        }
        if (!run || !objective) {
            activeEl.innerHTML = '<div class="empty">Noch keine laufende Arbeit. Starte oben mit einer Nachricht oder öffne eine bestehende Unterhaltung.</div>';
        } else {
            const phase = escapeHtml(run.phase || run.current_phase || 'ohne Phase');
            const status = escapeHtml(run.status || run.state || 'ohne Status');
            const nextStepValue = (nextAction.summary || nextAction.label || '').trim()
                || (String(nextAction.kind || '').toLowerCase() === 'none' ? '' : String(nextAction.kind || '').trim())
                || (history.slice(-1)[0]?.summary || '')
                || 'Kein offener nächster Schritt — die letzte Arbeit ist abgeschlossen.';
            const nextStep = escapeHtml(nextStepValue);
            const continueButton = (run.id && nextAction.kind === 'next_step' && nextAction.action_enabled)
                ? '<div class="chat-operate-buttons">' + operateActionButton(nextAction.action_label || 'Weiter', 'advanceOperateRun', [run.id], true) + '</div>'
                : '';
            activeEl.innerHTML = '<div class="summary-headline">' + escapeHtml(objective.title || 'Aktive Arbeit') + '</div>'
                + '<div class="summary-copy">' + nextStep + '</div>'
                + '<div class="summary-meta"><span class="summary-chip">Status: ' + status + '</span><span class="summary-chip">Phase: ' + phase + '</span></div>'
                + continueButton;
        }
        renderChatOperateDoor(decisionEl, {
            run,
            next_action: nextAction,
            pending_approvals: approvals,
            open_blockers: blockers,
        });
        renderChatFormation(kernel.formation || data.formation);
        if (!blockers.length && !approvals.length && !(run && run.id && nextAction.kind === 'next_step' && nextAction.action_enabled)) {
            decisionEl.innerHTML = '<div class="empty">Keine offenen Freigaben oder Blocker. Du kannst direkt weiterarbeiten.</div>';
        }
        const actionsEl = document.getElementById('chat-operate-actions');
        if (actionsEl) {
            const hasActions = approvals.length || blockers.length || (run && run.id && nextAction.kind === 'next_step' && nextAction.action_enabled);
            actionsEl.innerHTML = hasActions
                ? '<div class="chat-panel-meta">Freigeben, Ablehnen und Weiter stehen oben in Gerade aktiv / Braucht deine Entscheidung.</div>'
                : '<div class="empty">Keine ausführbare Operate-Aktion im aktuellen Kontext.</div>';
        }
        syncChatIdleLayout(lastChatRuntimeContext);
    } catch (e) {
        activeEl.innerHTML = '<span class="tag err">' + escapeHtml(e.message || 'Aktive Arbeit konnte nicht geladen werden') + '</span>';
        decisionEl.innerHTML = '<span class="tag err">' + escapeHtml(e.message || 'Freigaben konnten nicht geladen werden') + '</span>';
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
        localStorage.setItem('eidolon-chat-messages', JSON.stringify(chatMessages.slice(-100)));
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
    renderChatLandingRecentSessions();
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
    const metaEl = document.getElementById('chat-session-meta');
    if (metaEl) metaEl.textContent = formatSessionTimestamp(result.session.updated_at || result.session.created_at) + ' • ' + (result.session.message_count || 0) + ' Nachrichten';
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
    const metaEl = document.getElementById('chat-session-meta');
    if (metaEl) metaEl.textContent = 'Gerade erstellt • 0 Nachrichten';
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
async function sendChat() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;
    if (!currentChatSessionId) {
        await ensureChatSession();
    }
    chatMessages.push({ role: 'user', content: text });
    persistChatMessages();
    renderChat();
    input.value = '';
    try {
        const pairedDevice = getStoredMobileDevice();
        const isMetaQuestion = /selbstreflexion|analysiere dich|was würdest du verbessern|reflektiere|was ist deine schwäche|was ist deine stärke/i.test(text);
        const endpoint = isMetaQuestion ? '/api/v1/self-reflection/chat' : '/chat';
        const r = await api('POST', endpoint, { message: text, source: pairedDevice ? ('mobile:' + pairedDevice.peer_id) : 'chat', session_id: currentChatSessionId });
        if (r?.session_id) {
            currentChatSessionId = r.session_id;
            persistCurrentChatSessionId();
        }
        if (r?.runtime_context) {
            renderChatRuntimeContext(r.runtime_context);
        } else {
            await loadChatRuntimeContext(currentChatSessionId);
        }
        if (r?.ok === false) {
            chatMessages.push({ role: 'assistant', content: 'Fehler: ' + (r.error || 'Keine Modellantwort erhalten') });
        } else if (typeof r?.response === 'string' && r.response.trim()) {
            chatMessages.push({ role: 'assistant', content: r.response });
        } else {
            chatMessages.push({ role: 'assistant', content: 'Fehler: Keine Modellantwort erhalten' });
        }
    } catch (e) {
        await loadChatRuntimeContext(currentChatSessionId);
        chatMessages.push({ role: 'assistant', content: 'Fehler: ' + e.message });
    }
    persistChatMessages();
    renderChat();
    loadChatLandingSummary().catch(() => {});
}
function renderChat() {
    const el = document.getElementById('chat-messages');
    if (!el) return;
    syncChatIdleLayout(lastChatRuntimeContext);
    if (!chatMessages.length) {
        el.innerHTML = '<div class="empty chat-idle-hint">Noch kein Gesprächskontext.</div>';
        return;
    }
    el.innerHTML = chatMessages.map(m => '<div class="msg ' + m.role + '"><div class="sender">' + escapeHtml(m.role === 'user' ? 'Du' : 'Eidolon') + '</div><div>' + escapeHtml(m.content) + '</div></div>').join('');
    el.scrollTop = el.scrollHeight;
}

// Dashboard
