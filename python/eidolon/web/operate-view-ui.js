(function () {
    const renderEmpty = window.EidolonOperate.renderEmpty;

    async function loadOperateDeepData(runId) {
        if (!runId) {
            return { history: [], work_graph: { nodes: [], edges: [] }, transitions: [], evidence: [], subagents: [] };
        }
        const [historyRes, workGraphRes, transitionsRes, evidenceRes, subagentsRes] = await Promise.all([
            api('GET', '/api/v1/runs/' + encodeURIComponent(runId) + '/history'),
            api('GET', '/api/v1/runs/' + encodeURIComponent(runId) + '/work-graph'),
            api('GET', '/api/v1/runs/' + encodeURIComponent(runId) + '/transitions'),
            api('GET', '/api/v1/runs/' + encodeURIComponent(runId) + '/evidence'),
            api('GET', '/api/v1/runs/' + encodeURIComponent(runId) + '/subagents'),
        ]);
        return {
            history: historyRes?.data?.history || [],
            work_graph: workGraphRes?.data || { nodes: [], edges: [] },
            transitions: transitionsRes?.data?.transitions || [],
            evidence: evidenceRes?.data?.evidence || [],
            subagents: subagentsRes?.data?.subagents || [],
        };
    }

    async function loadOperateView() {
        try {
            let overview = await api('GET', '/api/v1/operate/overview');
            let data = overview?.data || {};
            if (!data.run || !data.session) {
                const synced = await syncOperateFromWorkspace();
                data = synced?.data || {};
            }
            const run = data.run || null;
            const session = data.session || null;
            const objective = data.objective || null;
            const blockers = data.blockers || [];
            const approvals = data.approvals || [];
            const nextAction = data.next_action || { kind: 'none' };
            if (typeof setEidolonPresence === 'function' && typeof describeOperatePresence === 'function') {
                const presence = describeOperatePresence(data);
                setEidolonPresence(presence.state, presence.title, presence.detail);
            }
            if (!run || !session) {
                renderState(null, null, [], []);
                renderObjective(null);
                renderApprovals(null, []);
                renderBlockers(null, []);
                renderSubagents([]);
                renderEvidence([]);
                renderNextAction(null, { kind: 'none' });
                renderHistory([]);
                renderWorkGraph({ nodes: [], edges: [] });
                renderTransitions([]);
                return;
            }
            const deep = await loadOperateDeepData(run.id);
            const subagents = deep.subagents || data.subagents || [];
            const activePods = (subagents.filter((item) => item && item.is_active)) || data.active_pods || [];
            const evidence = deep.evidence || data.evidence || [];
            const transitions = deep.transitions || [];
            const history = deep.history || [];
            const workGraph = deep.work_graph || { nodes: [], edges: [] };
            renderState(run, objective, blockers, approvals);
            renderObjective(objective);
            renderApprovals(run.id, approvals);
            renderBlockers(run.id, blockers);
            renderSubagents(activePods);
            renderEvidence(evidence);
            renderNextAction(run.id, nextAction);
            renderHistory(history);
            renderWorkGraph(workGraph);
            renderTransitions(transitions);
            if (typeof renderPodsOverview === 'function') {
                renderPodsOverview(activePods);
                renderPodDetail(window.EidolonOperate.pickSelectedPod(activePods));
            }
            if (typeof loadChatLandingSummary === 'function') loadChatLandingSummary();
        } catch (e) {
            renderEmpty('operate-state-bar', e.message || 'Operate konnte nicht geladen werden');
            renderEmpty('operate-objective-card', 'Operate-Ziel konnte nicht geladen werden');
            renderEmpty('operate-approvals', 'Operate-Freigaben konnten nicht geladen werden');
            renderEmpty('operate-blockers', 'Operate-Blocker konnten nicht geladen werden');
            renderEmpty('operate-subagents', 'Operate-Subagenten konnten nicht geladen werden');
            renderEmpty('operate-evidence', 'Operate-Evidenz konnte nicht geladen werden');
            renderEmpty('operate-next-action', 'Operate-Nächste-Aktion konnte nicht geladen werden');
            renderEmpty('operate-history', 'Operate-Historie konnte nicht geladen werden');
            renderEmpty('operate-workgraph', 'Operate-Work-Graph konnte nicht geladen werden');
            renderEmpty('operate-transitions', 'Operate-Übergänge konnten nicht geladen werden');
        }
    }

    window.loadOperateView = loadOperateView;
})();
