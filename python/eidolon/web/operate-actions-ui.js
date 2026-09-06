(function () {
    async function refreshOperateSurfaces() {
        if (typeof loadOperateView === 'function') await loadOperateView();
        if (typeof loadChatRuntimeContext === 'function') {
            await loadChatRuntimeContext(typeof currentChatSessionId === 'string' ? currentChatSessionId : '');
        } else if (typeof loadChatLandingSummary === 'function') {
            await loadChatLandingSummary();
        }
        if (typeof loadWorkspaces === 'function') await loadWorkspaces();
    }

    async function advanceOperateRun(runId) {
        await api('POST', '/api/v1/runs/' + runId + '/advance', { reason: 'Advance triggered from chat or operate UI' });
        await refreshOperateSurfaces();
        if (typeof showNotice === 'function') showNotice('Phase fortgeschrieben. Es wurde keine Aktion ausgeführt.', 'info', 5000);
        if (typeof confirmAction === 'function') confirmAction(document.getElementById('operate-next-action') || document.getElementById('panel-operate'), 'continued');
    }

    async function requestOperateApproval(runId) {
        await api('POST', '/api/v1/runs/' + runId + '/request-approval', {
            title: 'Benutzerfreigabe aus Chat/Operate',
            summary: 'Die aktuelle Operate-Aktion wurde zur Freigabe markiert',
            action_type: 'ui_review',
        });
        await refreshOperateSurfaces();
    }

    async function resolveOperateApproval(runId, approvalId, decision) {
        const result = await api('POST', '/api/v1/runs/' + runId + '/approval/' + approvalId, { decision, resolved_by: 'user' });
        await refreshOperateSurfaces();
        const execution = result && result.data && result.data.execution;
        if (decision === 'approved') {
            if (typeof showNotice === 'function') {
                showNotice((execution && execution.detail) || 'Freigabe notiert. Ausführung (Buchung, Mail, externe Aktion) ist nicht angebunden.', 'info', 6000);
            }
        } else if (typeof showNotice === 'function') {
            showNotice('Ablehnung notiert. Es wurde keine Gegenaktion ausgeführt.', 'info', 5000);
        }
        if (typeof confirmAction === 'function') confirmAction(document.getElementById('operate-approvals') || document.getElementById('panel-operate'), decision === 'rejected' ? 'rejected' : 'approved');
    }

    async function resolveOperateBlocker(runId, blockerId) {
        await api('POST', '/api/v1/runs/' + runId + '/blockers/' + blockerId + '/resolve', {
            resume_state: 'planning',
            state_reason: 'Blocker aus Chat/Operate als gelöst markiert',
        });
        await refreshOperateSurfaces();
    }

    async function syncOperateFromWorkspace() {
        return api('POST', '/api/v1/session/sync-from-workspaces');
    }

    async function takeOverFromProject() {
        const synced = await syncOperateFromWorkspace();
        await loadOperateView();
        const run = synced && synced.data && synced.data.run;
        if (run && typeof confirmAction === 'function') {
            confirmAction(document.getElementById('panel-operate'), 'synced');
            return;
        }
        if (!run) showNotice('Keine übernehmbare Arbeit in der Projektfläche', 'info');
    }

    Object.assign(window, { advanceOperateRun, requestOperateApproval, resolveOperateApproval, resolveOperateBlocker, syncOperateFromWorkspace, refreshOperateSurfaces, takeOverFromProject });
})();
