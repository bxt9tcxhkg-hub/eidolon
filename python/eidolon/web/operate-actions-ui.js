(function () {
    async function refreshOperateSurfaces() {
        if (typeof loadOperateView === 'function') await loadOperateView();
        if (typeof loadChatLandingSummary === 'function') await loadChatLandingSummary();
        if (typeof loadChatRuntimeContext === 'function' && typeof currentChatSessionId === 'string' && currentChatSessionId) {
            await loadChatRuntimeContext(currentChatSessionId);
        }
        if (typeof loadWorkspaces === 'function') await loadWorkspaces();
    }

    async function advanceOperateRun(runId) {
        await api('POST', '/api/v1/runs/' + runId + '/advance', { reason: 'Advance triggered from chat or operate UI' });
        await refreshOperateSurfaces();
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
        await api('POST', '/api/v1/runs/' + runId + '/approval/' + approvalId, { decision, resolved_by: 'user' });
        await refreshOperateSurfaces();
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

    Object.assign(window, { advanceOperateRun, requestOperateApproval, resolveOperateApproval, resolveOperateBlocker, syncOperateFromWorkspace, refreshOperateSurfaces });
})();
