(function () {
    const operate = window.EidolonOperate = window.EidolonOperate || {};
    operate.state = operate.state || {
        selectedPodId: null,
    };

    operate.pickSelectedPod = function pickSelectedPod(items) {
        const pods = Array.isArray(items) ? items : [];
        if (!pods.length) {
            operate.state.selectedPodId = null;
            return null;
        }
        const selected = pods.find((item) => item.id === operate.state.selectedPodId);
        if (selected) return selected;
        operate.state.selectedPodId = pods[0].id;
        return pods[0];
    };

    operate.selectPod = function selectPod(podId) {
        operate.state.selectedPodId = podId || null;
    };

    operate.row = function row(label, value) {
        return '<div class="comp-row"><span class="comp-name">' + escapeHtml(label) + '</span><span class="comp-detail">' + escapeHtml(value) + '</span></div>';
    };

    operate.renderEmpty = function renderEmpty(id, message) {
        const el = document.getElementById(id);
        if (!el) return;
        el.innerHTML = '<div class="empty">' + escapeHtml(message) + '</div>';
    };
})();
