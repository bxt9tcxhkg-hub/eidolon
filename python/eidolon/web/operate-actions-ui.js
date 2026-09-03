(function () {
    async function advanceOperateRun(runId) {
        await api('POST', '/api/v1/runs/' + runId + '/advance', { reason: 'Advance triggered from operate UI' });
        await loadOperateView();
    }

    async function requestOperateApproval(runId) {
        await api('POST', '/api/v1/runs/' + runId + '/request-approval', {
            title: 'Benutzerfreigabe aus Operate-UI',
            summary: 'Die aktuelle Operate-Aktion wurde in der UI zur Freigabe markiert',
            action_type: 'ui_review',
        });
        await loadOperateView();
    }

    async function resolveOperateApproval(runId, approvalId, decision) {
        await api('POST', '/api/v1/runs/' + runId + '/approval/' + approvalId, { decision, resolved_by: 'user' });
        await loadOperateView();
    }

    async function resolveOperateBlocker(runId, blockerId) {
        await api('POST', '/api/v1/runs/' + runId + '/blockers/' + blockerId + '/resolve', {
            resume_state: 'planning',
            state_reason: 'Blocker in Operate-UI als gelöst markiert',
        });
        await loadOperateView();
    }

    async function syncOperateFromWorkspace() {
        return api('POST', '/api/v1/session/sync-from-workspaces');
    }

    Object.assign(window, { advanceOperateRun, requestOperateApproval, resolveOperateApproval, resolveOperateBlocker, syncOperateFromWorkspace });
})();
