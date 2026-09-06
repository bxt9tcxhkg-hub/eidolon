const PAGES = {
    chat: { title: 'Eidolon', subtitle: 'Starte ein Gespräch oder setze reale Arbeit fort.' },
    operate: { title: 'Arbeit', subtitle: 'Freigaben und nächster Schritt, sobald etwas läuft' },
    pods: { title: 'Helfer', subtitle: 'Aktive Hilfsläufe und ihr realer Zustand', group: 'advanced' },
    dashboard: { title: 'Systemstatus', subtitle: 'Backend, Laufzeit, Speicher und verfügbare Fähigkeiten', group: 'advanced' },
    workspaces: { title: 'Projektfläche', subtitle: 'Board zum Planen — oder ein neues Projekt anlegen' },
    execution: { title: 'Laufzeit', subtitle: 'Geräte, Laufzeitfähigkeiten und aktuelle Ausführungssignale', group: 'advanced' },
    mesh: { title: 'Geräte', subtitle: 'Handy, Browser und weitere Geräte mit Eidolon koppeln', group: 'advanced' },
    goals: { title: 'Ziele', subtitle: 'Welche Ziele Eidolon verfolgt', group: 'advanced' },
    identity: { title: 'Identität', subtitle: 'Rollenmodell und Produkt-Selbstbeschreibung', group: 'config' },
    code: { title: 'Code-Reparatur', subtitle: 'Gezielte Analyse und Reparatur von lokalen Eidolon-Dateien', group: 'advanced' },
    healing: { title: 'Stabilität', subtitle: 'Reale Health-Checks und Wiederherstellungsstatus', group: 'advanced' },
    skills: { title: 'Fähigkeiten', subtitle: 'Aktivierte Werkzeuge und ausführbare Runtime-Fähigkeiten', group: 'advanced' },
    backups: { title: 'Sicherungen', subtitle: 'Echte Wiederherstellungspunkte und Speicherzustand', group: 'advanced' },
    settings: { title: 'Einstellungen', subtitle: 'Konfiguration mit speicherbaren Werten und Herkunftsanzeige' }
};

const TAB_SETTINGS_MAP = {
    operate: 'autonomy',
    chat: 'llm',
    pods: 'autonomy',
    dashboard: 'network',
    workspaces: 'ui',
    execution: 'network',
    goals: 'autonomy',
    identity: 'ui',
    code: 'privacy',
    healing: 'privacy',
    skills: 'llm',
    mesh: 'network',
    backups: 'privacy',
    settings: 'ui'
};

// Tabs
let currentTab = 'chat';
let currentGoalId = null;
let goalComposerVisible = false;
let armedUnpairPeerId = null;
let lastPresenceSnapshot = { state: 'idle', title: 'Bereit für neue Arbeit', detail: 'Starte ein Gespräch oder setze bestehende Arbeit fort.' };
let lastOperateSnapshot = {};

function closeMobileMore() {
    document.getElementById('mobile-more-sheet')?.classList.remove('open');
}

function syncNavHighlight(tabId) {
    const activeId = tabId || currentTab || 'chat';
    document.querySelectorAll('.nav-item').forEach((n) => {
        const on = n.dataset.tab === activeId;
        n.classList.toggle('active', on);
        if (on) n.setAttribute('aria-current', 'page');
        else n.removeAttribute('aria-current');
    });
    const moreOpen = Boolean(document.getElementById('mobile-more-sheet')?.classList.contains('open'));
    const primary = ['chat', 'workspaces', 'operate'];
    document.querySelectorAll('.mitem').forEach((m) => {
        if (m.dataset.tab === 'more') {
            m.classList.toggle('active', moreOpen || !primary.includes(activeId));
            return;
        }
        m.classList.toggle('active', !moreOpen && m.dataset.tab === activeId);
    });
    const disclosure = document.querySelector('.nav-disclosure');
    if (disclosure && disclosure.querySelector('.nav-item.active')) disclosure.open = true;
}

function toggleMobileMore() {
    const sheet = document.getElementById('mobile-more-sheet');
    if (!sheet) return;
    const next = !sheet.classList.contains('open');
    sheet.classList.toggle('open', next);
    syncNavHighlight(currentTab);
}

function showTab(tabId) {
    if (tabId !== 'more') closeMobileMore();
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.getElementById('panel-' + tabId)?.classList.add('active');
    currentTab = tabId;
    syncNavHighlight(tabId);
    const page = PAGES[tabId] || PAGES.chat;
    document.getElementById('page-title').textContent = page.title;
    document.getElementById('page-subtitle').textContent = page.subtitle;
    if (window.location.hash !== '#' + tabId) history.replaceState(null, '', '#' + tabId);
    const loaders = {
        operate: () => loadOperateView(),
        chat: () => {
            renderChat();
            if (typeof loadChatLandingSummary === 'function') loadChatLandingSummary().catch(() => {});
        },
        pods: () => loadPodsView(),
        dashboard: () => loadDashboard(),
        workspaces: () => loadWorkspaces(),
        execution: () => loadExecutionView(),
        goals: () => { loadGoals(); loadGoalLog(); },
        mesh: () => { loadMesh(); loadMeshPending(); },
        healing: () => loadHealing(),
        skills: () => loadSkills(),
        backups: () => loadBackups(),
        settings: () => loadSettings(),
        identity: () => loadIdentity(),
        code: () => loadCodeRepair(),
    };
    loaders[tabId]?.();
}

function focusSettingsArea(area) {
    const el = document.getElementById('settings-' + area);
    if (!el) return;
    el.closest('.card')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    el.closest('.card')?.classList.add('settings-anchor-highlight');
    setTimeout(() => el.closest('.card')?.classList.remove('settings-anchor-highlight'), 1800);
}

function openTabSettings() {
    const area = TAB_SETTINGS_MAP[currentTab];
    showTab('settings');
    loadSettings().then(() => {
        if (area) focusSettingsArea(area);
    });
}

function escapeHtml(str) {
    return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

async function api(method, path, body) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const r = await fetch(path, opts);
    if (!r.ok) throw new Error(r.status + ': ' + r.statusText);
    return r.json();
}

function getStoredMobileDevice() {
    try {
        const device = JSON.parse(localStorage.getItem('eidolon-paired-device') || 'null');
        return device && device.peer_id ? device : null;
    } catch (_) { return null; }
}

async function loadMobileDeviceState() {
    const banner = document.getElementById('mobile-device-banner');
    if (!banner) return;
    const device = getStoredMobileDevice();
    if (!device) { banner.classList.remove('visible'); banner.textContent = ''; return; }
    try {
        const data = await api('GET', '/mesh/pairing/paired');
        const paired = (data.paired || []).find(p => p.peer_id === device.peer_id);
        if (!paired) { banner.classList.remove('visible'); banner.textContent = ''; return; }
        banner.classList.add('visible');
        banner.innerHTML = '<strong>Dieses Handy ist gekoppelt.</strong> Du nutzt jetzt die mobile Eidolon-Oberfläche; Nachrichten, Projekte, Ziele, Status und Einstellungen laufen gegen denselben Eidolon-Server.';
    } catch (e) {
        banner.classList.add('visible');
        banner.textContent = 'Gekoppeltes Gerät erkannt, aber Mesh-Status konnte nicht geladen werden: ' + e.message;
    }
}

function showNotice(message, type = 'info', duration = 3000) {
    let container = document.getElementById('notice-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notice-container';
        container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:1000;display:flex;flex-direction:column;gap:8px;';
        document.body.appendChild(container);
    }
    const colors = { ok: '#22c55e', success: '#22c55e', warning: '#f59e0b', error: '#ef4444', info: '#3b82f6' };
    const el = document.createElement('div');
    el.style.cssText = 'padding:10px 16px;border-radius:6px;color:#fff;font-size:0.85rem;box-shadow:0 4px 12px rgba(0,0,0,0.3);min-width:200px;';
    el.style.background = colors[type] || colors.info;
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => el.remove(), duration);
}

const CHAT_TURN_ARIA = {
    idle: 'Eidolon ist bereit',
    denkt: 'Eidolon denkt',
    arbeitet: 'Eidolon arbeitet',
    antwortet: 'Eidolon antwortet',
};

function setEidolonTurnPhase(phase) {
    const next = (phase === 'denkt' || phase === 'arbeitet' || phase === 'antwortet') ? phase : 'idle';
    document.querySelectorAll('[data-eidolon-presence]').forEach((el) => {
        el.dataset.turnPhase = next;
        if (el.getAttribute('role') === 'img') {
            el.setAttribute('aria-label', CHAT_TURN_ARIA[next] || CHAT_TURN_ARIA.idle);
        }
    });
}

function setEidolonPresence(state, title, detail) {
    const next = {
        state: state || 'idle',
        title: title || 'Bereit für neue Arbeit',
        detail: detail || 'Starte ein Gespräch oder setze bestehende Arbeit fort.',
    };
    lastPresenceSnapshot = next;
    document.querySelectorAll('.eidolon-signature').forEach(el => {
        el.dataset.presenceState = next.state;
    });
    const copyEl = document.getElementById('eidolon-presence-copy');
    if (copyEl) copyEl.textContent = next.title;
    const metaEl = document.getElementById('eidolon-presence-meta');
    if (metaEl) metaEl.textContent = next.detail;
    const badgeEl = document.getElementById('chat-presence-badge');
    if (badgeEl) {
        badgeEl.dataset.presenceState = next.state;
        badgeEl.textContent = next.title;
    }
    const noteEl = document.getElementById('chat-presence-note');
    if (noteEl) noteEl.textContent = next.detail;
    refreshWorkTraces();
}

function describeOperatePresence(data) {
    const run = data?.run || {};
    const objective = data?.objective || {};
    const blockers = (Array.isArray(data?.blockers) ? data.blockers : []).filter((item) => !item.status || item.status === 'open' || item.is_open);
    const approvals = (Array.isArray(data?.approvals) ? data.approvals : []).filter((item) => !item.status || item.status === 'pending' || item.is_pending);
    const nextAction = data?.next_action || {};
    const focus = objective.title || objective.normalized_title || run.goal || 'Aktive Arbeit';
    const phase = String(run.phase || run.current_phase || '').toLowerCase();
    const status = String(run.status || run.state || '').toLowerCase();
    if (blockers.length) {
        return { state: 'blocked', title: 'Blockiert', detail: focus + ' • ' + blockers.length + ' Blocker offen' };
    }
    if (approvals.length || ['approval', 'await_approval', 'user_input', 'await_input'].includes(String(nextAction.kind || '').toLowerCase())) {
        return { state: 'waiting', title: 'Wartet auf dich', detail: focus + ' • ' + Math.max(approvals.length, 1) + ' Entscheidung offen' };
    }
    if (['completed', 'done', 'verified'].includes(status) || phase === 'finalize') {
        return { state: 'done', title: 'Verifiziert', detail: focus + ' • letzte Arbeit abgeschlossen' };
    }
    if (['execute', 'executing', 'verify', 'verifying', 'sync', 'finalize'].some(token => phase.includes(token)) || ['active', 'running', 'in_progress'].includes(status)) {
        return { state: 'acting', title: 'Arbeitet gerade', detail: focus + (phase ? ' • Phase: ' + phase : '') };
    }
    if (focus && focus !== 'Aktive Arbeit') {
        return { state: 'thinking', title: 'Strukturiert Arbeit', detail: focus + (phase ? ' • Phase: ' + phase : '') };
    }
    return { state: 'idle', title: 'Bereit für neue Arbeit', detail: 'Starte ein Gespräch oder setze bestehende Arbeit fort.' };
}

function pickRecentLocalWork(sessions) {
    const list = Array.isArray(sessions) ? sessions : [];
    const withSignal = list.filter((session) => {
        const preview = String(session.last_message_preview || '').trim();
        const count = Number(session.message_count || 0);
        const title = String(session.title || '').trim();
        return Boolean(preview) || count > 0 || (title && title !== 'Neue Unterhaltung');
    });
    if (!withSignal.length) return null;
    return withSignal.slice().sort((a, b) => {
        const ta = Date.parse(a.updated_at || a.created_at || 0) || 0;
        const tb = Date.parse(b.updated_at || b.created_at || 0) || 0;
        return tb - ta;
    })[0];
}

function describeWorkTrace(data) {
    const presence = describeOperatePresence(data);
    const nextAction = data?.next_action || {};
    const nextKind = String(nextAction.kind || '').toLowerCase();
    const nextText = String(nextAction.title || nextAction.summary || nextAction.action_label || '').trim();
    const hasNext = nextKind && nextKind !== 'none' && Boolean(nextText);
    const recent = pickRecentLocalWork(typeof chatSessions !== 'undefined' ? chatSessions : []);

    if (presence.state === 'blocked') {
        return {
            state: 'waiting',
            ready: presence.title,
            waiting: presence.detail,
            next: hasNext ? nextText : 'Blocker in Arbeit sichtbar',
            nextLabel: 'als Nächstes',
        };
    }
    if (presence.state === 'waiting') {
        return {
            state: 'waiting',
            ready: presence.title,
            waiting: presence.detail,
            next: hasNext ? nextText : 'deine Entscheidung',
            nextLabel: 'als Nächstes',
        };
    }
    if (presence.state === 'acting' || presence.state === 'thinking') {
        return {
            state: 'active',
            ready: presence.title,
            waiting: presence.detail,
            next: hasNext ? nextText : presence.detail,
            nextLabel: 'als Nächstes',
        };
    }
    if (presence.state === 'done') {
        return {
            state: 'recent',
            ready: 'Zuletzt',
            waiting: 'nichts wartet',
            next: presence.detail,
            nextLabel: 'zuletzt',
        };
    }
    if (recent) {
        const title = String(recent.title || 'Unterhaltung').trim();
        const when = (typeof formatSessionTimestamp === 'function')
            ? formatSessionTimestamp(recent.updated_at || recent.created_at)
            : '';
        return {
            state: 'recent',
            ready: 'Bereit',
            waiting: 'nichts wartet',
            next: when ? (title + ' · ' + when) : title,
            nextLabel: 'zuletzt',
        };
    }
    return {
        state: 'ready',
        ready: 'Bereit',
        waiting: 'nichts wartet',
        next: 'dein Impuls',
        nextLabel: 'als Nächstes',
    };
}

function applyWorkTrace(el, trace) {
    if (!el || !trace) return;
    el.dataset.workTraceState = trace.state;
    const ready = el.querySelector('[data-work-trace-ready]');
    const waiting = el.querySelector('[data-work-trace-waiting]');
    const next = el.querySelector('[data-work-trace-next]');
    const nextLabel = el.querySelector('[data-work-trace-next-label]');
    if (ready) ready.textContent = trace.ready;
    if (waiting) waiting.textContent = trace.waiting;
    if (next) next.textContent = trace.next;
    if (nextLabel) nextLabel.textContent = trace.nextLabel;
}

function refreshWorkTraces(operateData) {
    if (operateData && typeof operateData === 'object') lastOperateSnapshot = operateData;
    const trace = describeWorkTrace(lastOperateSnapshot);
    document.querySelectorAll('[data-work-trace]').forEach((el) => applyWorkTrace(el, trace));
}

// Chat
let chatMessages = [];
let currentChatSessionId = null;
let chatSessions = [];
let lastChatRuntimeContext = null;
function loadTheme() { var saved = localStorage.getItem('eidolon-theme') || 'dark'; document.documentElement.setAttribute('data-theme', saved); var icon = document.getElementById('theme-icon'); if (icon) icon.textContent = saved === 'dark' ? '◐' : '◑'; }
function toggleTheme() { var c = document.documentElement.getAttribute('data-theme') || 'dark'; var n = c === 'dark' ? 'light' : 'dark'; document.documentElement.setAttribute('data-theme', n); document.getElementById('theme-icon').textContent = n === 'dark' ? '◐' : '◑'; localStorage.setItem('eidolon-theme', n); }


function bindShellEvents() {
    document.getElementById('chat-session-search')?.addEventListener('input', function () {
        renderChatSessions(chatSessions);
    });
    document.getElementById('ws-view-mode')?.addEventListener('change', function () {
        switchView();
    });
    document.getElementById('goals-filter')?.addEventListener('change', function () {
        loadGoals();
    });
    const canvas = document.getElementById('canvas-container');
    if (canvas) {
        canvas.addEventListener('mousedown', function (event) { canvasMouseDown(event); });
        canvas.addEventListener('mousemove', function (event) { canvasMouseMove(event); });
        canvas.addEventListener('mouseup', function () { canvasMouseUp(); });
        canvas.addEventListener('wheel', function (event) { canvasWheel(event); });
        canvas.addEventListener('dblclick', function (event) { canvasDoubleClick(event); });
    }
}

// Init
document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    chatMessages = loadStoredChatMessages();
    const initialTab = (window.location.hash || '#chat').replace('#', '');
    if (PAGES[initialTab]) showTab(initialTab);
    else showTab('chat');
    setEidolonPresence(lastPresenceSnapshot.state, lastPresenceSnapshot.title, lastPresenceSnapshot.detail);
    ensureChatSession().catch(e => showNotice(e.message, 'error'));
    bindShellEvents();
    window.addEventListener('hashchange', function () {
        const tabId = (window.location.hash || '#chat').replace('#', '');
        if (PAGES[tabId] && tabId !== currentTab) showTab(tabId);
    });
    renderChat(); loadOperateView(); loadPodsView(); loadWorkspaces(); loadGoals(); loadGoalLog(); loadHealth(); loadCapabilities(); loadSystemMetrics(); loadSystemStorage(); loadExecutionView(); loadIdentity(); loadMesh(); loadMeshPending(); loadHealing(); loadSkills(); loadBackups(); loadSettings(); loadMobileDeviceState();
});


function invokeUiAction(name, args = []) {
    const fn = window[name];
    if (typeof fn !== 'function') {
        showNotice('UI-Aktion nicht verfügbar: ' + name, 'error');
        return;
    }
    return fn(...args);
}

document.addEventListener('click', function (event) {
    const nav = event.target.closest('[data-tab-target]');
    if (nav) {
        event.preventDefault();
        showTab(nav.dataset.tabTarget);
        return;
    }
    const actionEl = event.target.closest('[data-ui-action]');
    if (!actionEl) return;
    event.preventDefault();
    const action = actionEl.dataset.uiAction;
    const args = actionEl.dataset.uiArgs ? JSON.parse(actionEl.dataset.uiArgs) : [];
    if (actionEl.dataset.uiPass === 'element') args.push(actionEl);
    const mode = actionEl.dataset.uiMode || 'call';
    if (mode === 'syncOperateAndReload') {
        syncOperateFromWorkspace().then(() => loadOperateView());
        return;
    }
    invokeUiAction(action, args);
});

document.addEventListener('keydown', function (event) {
    const enterEl = event.target.closest('[data-enter-action]');
    if (!enterEl || event.key !== 'Enter') return;
    event.preventDefault();
    invokeUiAction(enterEl.dataset.enterAction);
});

function actionMotionEnabled() {
    if (document.documentElement.getAttribute('data-animations') === 'off') return false;
    try {
        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
    } catch (_) { /* ignore */ }
    return true;
}

function applyUiMotionPreference(settings) {
    const enabled = !(settings && settings.ui && settings.ui.animations === false);
    document.documentElement.setAttribute('data-animations', enabled ? 'on' : 'off');
}

function confirmAction(target, kind) {
    const el = typeof target === 'string' ? document.getElementById(target) : target;
    const node = el || document.getElementById('panel-' + (currentTab || 'chat'));
    if (!node) return false;
    node.dataset.actionConfirm = kind || 'settle';
    if (!actionMotionEnabled()) return false;
    node.classList.remove('action-confirm');
    void node.offsetWidth;
    node.classList.add('action-confirm');
    window.setTimeout(() => node.classList.remove('action-confirm'), 420);
    return true;
}

Object.assign(window, {
    setEidolonPresence,
    setEidolonTurnPhase,
    describeOperatePresence,
    describeWorkTrace,
    refreshWorkTraces,
    pickRecentLocalWork,
    syncNavHighlight,
    showTab,
    actionMotionEnabled,
    applyUiMotionPreference,
    confirmAction,
});
