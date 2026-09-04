(function () {
    const operate = window.EidolonOperate;
    const row = operate.row;

    function sectionHasVisibleData(el) {
        if (!el) return false;
        const text = String(el.textContent || '').trim();
        if (!text) return false;
        const emptyOnly = el.querySelector('.empty') && !el.querySelector('.comp-row, .goal-card, .chat-operate-item, button');
        return !emptyOnly;
    }

    function syncOperateEmptyLayout(flags) {
        const hasRun = Boolean(flags && flags.hasRun);
        const panel = document.getElementById('panel-operate');
        if (panel) panel.classList.toggle('operate-is-idle', !hasRun);
        const idle = document.getElementById('operate-idle-empty');
        if (idle) idle.hidden = hasRun;
        const stateBar = document.getElementById('operate-state-bar');
        if (stateBar) stateBar.hidden = !hasRun;
        const nextAction = document.getElementById('operate-next-action');
        const hasNext = Boolean(flags && flags.next);
        if (nextAction) nextAction.hidden = !hasRun || !hasNext;
        const populated = {
            objective: Boolean(flags && flags.objective),
            approvals: Boolean(flags && flags.approvals),
            blockers: Boolean(flags && flags.blockers),
            subagents: Boolean(flags && flags.subagents),
            evidence: Boolean(flags && flags.evidence),
            history: Boolean(flags && flags.history),
            workgraph: Boolean(flags && flags.workgraph),
            transitions: Boolean(flags && flags.transitions),
        };
        const emptyLabels = [];
        const labelMap = {
            objective: 'Ziel',
            approvals: 'Freigaben',
            blockers: 'Blocker',
            subagents: 'Helfer',
            evidence: 'Evidenz',
            history: 'Verlauf',
            workgraph: 'Work-Graph',
            transitions: 'Übergänge',
        };
        document.querySelectorAll('#panel-operate [data-operate-section]').forEach((card) => {
            const key = card.dataset.operateSection;
            const show = hasRun && Boolean(populated[key]);
            card.hidden = !show;
            card.classList.toggle('operate-section-empty', !populated[key]);
            if (hasRun && !populated[key] && labelMap[key]) emptyLabels.push(labelMap[key]);
        });
        const details = document.getElementById('operate-empty-details');
        const detailsBody = document.getElementById('operate-empty-details-body');
        if (details) {
            details.hidden = !hasRun || emptyLabels.length === 0;
            if (detailsBody) {
                detailsBody.textContent = emptyLabels.length
                    ? ('Ohne Daten: ' + emptyLabels.join(', ') + '.')
                    : 'Keine leeren Kernel-Bereiche.';
            }
        }
    }

    function renderState(run, objective, blockers, approvals) {
        const el = document.getElementById('operate-state-bar');
        if (!el) return;
        if (!run) {
            el.innerHTML = '<div class="empty">Kein aktiver Operate-Run.</div>';
            return;
        }
        const blocker = Array.isArray(blockers) && blockers.find((item) => item.status === 'open');
        const approval = Array.isArray(approvals) && approvals.find((item) => item.status === 'pending');
        const mode = run.state === 'acting' || run.state === 'spawning_work' ? 'Handelt' : run.state === 'verifying' ? 'Verifiziert' : run.state === 'blocked' ? 'Blockiert' : run.state === 'waiting' ? 'Wartet' : run.state === 'completed' ? 'Fertig' : 'Denkt';
        el.innerHTML = [row('Modus', mode), row('Zustand', run.state || '—'), row('Grund', run.state_reason || '—'), row('Phase', run.canonical_phase || run.current_phase || '—'), row('Nächster Übergang', run.canonical_next_transition || run.next_transition || '—'), row('Ziel', (objective && objective.title) || run.objective_title || '—'), row('Freigabe offen', approval ? approval.title : 'nein'), row('Blocker', blocker ? blocker.title : 'keiner'), row('Interrupts', String(run.pending_interrupt_count ?? 0))].join('');
    }

    function renderObjective(objective) {
        const el = document.getElementById('operate-objective-card');
        if (!el) return;
        if (!objective) { el.innerHTML = '<div class="empty">Noch kein aktives Ziel im Operate-Kernel.</div>'; return; }
        el.innerHTML = [row('Titel', objective.title || '—'), row('Normalisiert', objective.normalized_goal || '—'), row('Scope', objective.scope_summary || '—'), row('Decomposition', objective.decomposition_mode || '—'), row('Status', objective.status || '—')].join('');
    }

    function renderSubagents(items) {
        const el = document.getElementById('operate-subagents');
        if (!el) return;
        if (!Array.isArray(items) || !items.length) { el.innerHTML = '<div class="empty">Keine aktiven Pod-Runs.</div>'; return; }
        el.innerHTML = items.map((item) => ['<div class="goal-card" data-status="' + escapeHtml(item.state || 'queued') + '">', '<div class="goal-body">', row('Name', item.display_name || '—'), row('Funktion', item.function_family || item.function_type || '—'), row('Mission', item.mission || '—'), row('Zustand', item.state || '—'), row('Aktiv', item.is_active ? 'ja' : 'nein'), row('Grund', item.state_reason || '—'), row('Ergebnis', item.result_status || '—'), row('Evidenz', String(item.evidence_count ?? 0)), '<div style="margin-top:10px;"><button class="btn btn-sm btn-primary" data-ui-action="openPodDetail" data-ui-args=' + JSON.stringify([item.id]) + '>Pod-Detail</button></div>', '</div>', '</div>'].join('')).join('');
    }

    function renderEvidence(items) {
        const el = document.getElementById('operate-evidence');
        if (!el) return;
        if (!Array.isArray(items) || !items.length) { el.innerHTML = '<div class="empty">Noch keine kernel-gebundene Evidenz.</div>'; return; }
        el.innerHTML = items.map((item) => '<div class="comp-row"><span class="comp-name">' + escapeHtml(item.title || item.kind || 'Evidenz') + '</span><span class="comp-detail">' + escapeHtml((item.evidence_status || 'unknown') + ' · ' + (item.summary || '—')) + '</span></div>').join('');
    }

    function renderNextAction(runId, nextAction) {
        const el = document.getElementById('operate-next-action');
        if (!el) return;
        if (!nextAction || nextAction.kind === 'none') { el.innerHTML = '<div class="empty">Noch keine nächste Aktion im Operate-Kernel.</div>'; return; }
        const advanceButton = runId && nextAction.kind === 'next_step' && nextAction.action_enabled ? '<div style="margin-top:12px;"><button class="btn btn-primary" onclick="advanceOperateRun(' + JSON.stringify(runId) + ')">' + escapeHtml(nextAction.action_label || 'Weiter') + '</button></div>' : '';
        const approvalButton = runId && nextAction.kind === 'approval_request' ? '<div style="margin-top:12px;"><button class="btn btn-sm" onclick="requestOperateApproval(' + JSON.stringify(runId) + ')">Freigabe erneut anfordern</button></div>' : '';
        el.innerHTML = [row('Typ', nextAction.kind || '—'), row('Titel', nextAction.title || '—'), row('Zusammenfassung', nextAction.summary || '—'), row('Aktion', nextAction.action_label || '—'), row('Ausführbar', nextAction.action_enabled ? 'ja' : 'nein'), advanceButton, approvalButton].join('');
    }

    function renderApprovals(runId, items) {
        const el = document.getElementById('operate-approvals');
        if (!el) return;
        if (!Array.isArray(items) || !items.length) { el.innerHTML = '<div class="empty">Keine offenen Freigaben.</div>'; return; }
        el.innerHTML = items.map((item) => {
            const actions = item.status === 'pending' ? '<div style="display:flex;gap:8px;margin-top:10px;"><button class="btn btn-sm btn-primary" onclick="resolveOperateApproval(' + JSON.stringify(runId) + ', ' + JSON.stringify(item.id) + ', ' + JSON.stringify('approved') + ')">Freigeben</button><button class="btn btn-sm" onclick="resolveOperateApproval(' + JSON.stringify(runId) + ', ' + JSON.stringify(item.id) + ', ' + JSON.stringify('rejected') + ')">Ablehnen</button></div>' : '';
            return '<div class="goal-card" data-status="' + escapeHtml(item.status || 'pending') + '"><div class="goal-body">' + row('Titel', item.title || '—') + row('Status', item.status || '—') + row('Entscheidung nötig', item.requires_decision ? 'ja' : 'nein') + row('Aktion', item.action_type || '—') + row('Zusammenfassung', item.summary || '—') + actions + '</div></div>';
        }).join('');
    }

    function renderBlockers(runId, items) {
        const el = document.getElementById('operate-blockers');
        if (!el) return;
        if (!Array.isArray(items) || !items.length) { el.innerHTML = '<div class="empty">Keine offenen Blocker.</div>'; return; }
        el.innerHTML = items.map((item) => {
            const actions = item.status === 'open' ? '<div style="display:flex;gap:8px;margin-top:10px;"><button class="btn btn-sm btn-primary" onclick="resolveOperateBlocker(' + JSON.stringify(runId) + ', ' + JSON.stringify(item.id) + ')">Als gelöst markieren</button></div>' : '';
            return '<div class="goal-card" data-status="' + escapeHtml(item.status || 'open') + '"><div class="goal-body">' + row('Titel', item.title || '—') + row('Status', item.status || '—') + row('Offen', item.is_open ? 'ja' : 'nein') + row('Kategorie', item.category || '—') + row('Zusammenfassung', item.summary || '—') + row('Lösungshinweis', item.resolution_hint || '—') + actions + '</div></div>';
        }).join('');
    }

    function renderHistory(items) {
        const el = document.getElementById('operate-history');
        if (!el) return;
        if (!Array.isArray(items) || !items.length) { el.innerHTML = '<div class="empty">Noch keine Historie im Operate-Kernel.</div>'; return; }
        el.innerHTML = items.slice(-20).reverse().map((item) => ['<div class="comp-row"><span class="comp-name">' + escapeHtml(item.timestamp || '—') + '</span>', '<span class="comp-detail">' + escapeHtml((item.kind || 'event') + ' · ' + (item.title || '—')) + '</span></div>', '<div style="margin:-4px 0 8px 0;color:var(--text-dim);font-size:0.78rem;line-height:1.4;">' + escapeHtml(item.summary || '') + '</div>'].join('')).join('');
    }

    function renderWorkGraph(graph) {
        const el = document.getElementById('operate-workgraph');
        if (!el) return;
        const nodes = graph?.nodes || [];
        const edges = graph?.edges || [];
        if (!nodes.length) { el.innerHTML = '<div class="empty">Noch kein Work Graph im Operate-Kernel.</div>'; return; }
        const nodeHtml = nodes.map((node) => '<div class="comp-row"><span class="comp-name">' + escapeHtml(node.kind + ': ' + (node.label || node.id)) + '</span><span class="comp-detail">' + escapeHtml(node.state || node.title || '—') + '</span></div>').join('');
        const edgeHtml = edges.length ? '<div style="margin-top:12px;">' + edges.map((edge) => '<div class="comp-row"><span class="comp-name">' + escapeHtml(edge.type || 'link') + '</span><span class="comp-detail">' + escapeHtml((edge.from || '—') + ' → ' + (edge.to || '—')) + '</span></div>').join('') + '</div>' : '<div class="empty">Keine Kanten</div>';
        el.innerHTML = nodeHtml + edgeHtml;
    }

    function renderTransitions(items) {
        const el = document.getElementById('operate-transitions');
        if (!el) return;
        if (!Array.isArray(items) || !items.length) { el.innerHTML = '<div class="empty">Noch keine Übergänge im Operate-Kernel.</div>'; return; }
        el.innerHTML = items.map((item) => ['<div class="comp-row"><span class="comp-name">' + escapeHtml(item.transition_type || 'state_change') + '</span>', '<span class="comp-detail">' + escapeHtml((item.from_state || '—') + ' → ' + (item.to_state || '—')) + '</span></div>', '<div style="margin:-4px 0 8px 0;color:var(--text-dim);font-size:0.78rem;line-height:1.4;">' + escapeHtml(item.summary || '') + '</div>'].join('')).join('');
    }

    Object.assign(window, { renderState, renderObjective, renderSubagents, renderEvidence, renderNextAction, renderApprovals, renderBlockers, renderHistory, renderWorkGraph, renderTransitions, syncOperateEmptyLayout, sectionHasVisibleData });
})();
