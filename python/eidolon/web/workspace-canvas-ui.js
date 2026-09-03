(function () {
    const ws = window.EidolonWorkspace;
    const state = ws.state;

    function renderCanvas() {
        if (!state.currentProject) return;
        const elements = state.currentProject.elements || [];
        const world = document.getElementById('canvas-world');
        const svg = document.getElementById('canvas-edges');
        const nodesLayer = document.getElementById('canvas-nodes');
        const canvas = state.canvas;
        if (!world || !svg || !nodesLayer) return;
        world.style.transform = 'translate(' + canvas.panX + 'px, ' + canvas.panY + 'px) scale(' + canvas.zoom + ')';
        nodesLayer.innerHTML = '';
        for (const item of elements) {
            const node = document.createElement('div');
            node.className = 'canvas-node' + (canvas.selected.has(item.id) ? ' selected' : '');
            node.style.left = (item.position?.x || 0) + 'px';
            node.style.top = (item.position?.y || 0) + 'px';
            node.dataset.elementId = item.id;
            node.innerHTML = '<span class="node-status ' + (item.status || 'idea') + '"></span><span class="node-title">' + escapeHtml(item.title) + '</span><div class="node-meta">' + (item.priority > 0 ? '<span class="cat-badge">P' + item.priority + '</span>' : '') + (item.dependencies?.length ? '<span class="cat-badge">↳' + item.dependencies.length + '</span>' : '') + '</div>';
            node.onmousedown = (ev) => canvasNodeMouseDown(ev, item.id);
            node.ondblclick = (ev) => { ev.stopPropagation(); openElementForm(item.id, item.position?.x || 0, item.position?.y || 0); };
            nodesLayer.appendChild(node);
        }
        requestAnimationFrame(() => {
            svg.innerHTML = '<defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="var(--accent)"/></marker></defs>';
            const worldRect = world.getBoundingClientRect();
            for (const item of elements) {
                if (item.parent_id) {
                    const child = nodesLayer.querySelector('[data-element-id="' + item.id + '"]');
                    const parent = nodesLayer.querySelector('[data-element-id="' + item.parent_id + '"]');
                    if (child && parent) {
                        const c = child.getBoundingClientRect();
                        const p = parent.getBoundingClientRect();
                        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                        line.setAttribute('x1', (c.left + c.width / 2 - worldRect.left) / canvas.zoom);
                        line.setAttribute('y1', (c.top + c.height / 2 - worldRect.top) / canvas.zoom);
                        line.setAttribute('x2', (p.left + p.width / 2 - worldRect.left) / canvas.zoom);
                        line.setAttribute('y2', (p.top + p.height / 2 - worldRect.top) / canvas.zoom);
                        line.setAttribute('stroke', 'var(--success)');
                        line.setAttribute('stroke-dasharray', '6 4');
                        line.setAttribute('stroke-width', '2');
                        svg.appendChild(line);
                    }
                }
                for (const depId of item.dependencies || []) {
                    const src = nodesLayer.querySelector('[data-element-id="' + item.id + '"]');
                    const tgt = nodesLayer.querySelector('[data-element-id="' + depId + '"]');
                    if (!src || !tgt) continue;
                    const s = src.getBoundingClientRect();
                    const t = tgt.getBoundingClientRect();
                    const x1 = (s.left + s.width / 2 - worldRect.left) / canvas.zoom;
                    const y1 = (s.top + s.height / 2 - worldRect.top) / canvas.zoom;
                    const x2 = (t.left + t.width / 2 - worldRect.left) / canvas.zoom;
                    const y2 = (t.top + t.height / 2 - worldRect.top) / canvas.zoom;
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', x1); line.setAttribute('y1', y1); line.setAttribute('x2', x2); line.setAttribute('y2', y2); line.setAttribute('marker-end', 'url(#arrowhead)');
                    svg.appendChild(line);
                }
            }
        });
        document.getElementById('canvas-zoom-level').textContent = Math.round(canvas.zoom * 100) + '%';
        document.getElementById('canvas-statusbar').textContent = elements.length + ' Elemente';
    }

    function canvasNodeMouseDown(event, elementId) {
        const canvas = state.canvas;
        event.stopPropagation();
        if (canvas.mode === 'move') {
            canvas.selected.clear();
            canvas.selected.add(elementId);
            canvas.dragging = true;
            canvas.dragStart = { x: event.clientX, y: event.clientY };
        } else if (canvas.mode === 'link') {
            if (!canvas.linkSource) { canvas.linkSource = elementId; canvas.selected.add(elementId); }
            else { addDependency(canvas.linkSource, elementId); canvas.linkSource = null; canvas.selected.clear(); }
            renderCanvas();
        } else if (canvas.mode === 'hierarchy') {
            if (!canvas.linkSource) { canvas.linkSource = elementId; canvas.selected.clear(); canvas.selected.add(elementId); }
            else { assignHierarchy(elementId, canvas.linkSource); canvas.linkSource = null; canvas.selected.clear(); }
            renderCanvas();
        }
    }

    function canvasMouseDown(event) {
        const canvas = state.canvas;
        if (canvas.mode !== 'move') return;
        canvas.selected.clear();
        canvas.dragging = true;
        canvas.panStart = { x: event.clientX - canvas.panX, y: event.clientY - canvas.panY };
    }

    function canvasMouseMove(event) {
        const canvas = state.canvas;
        if (!canvas.dragging) return;
        if (canvas.selected.size === 0) {
            canvas.panX = event.clientX - canvas.panStart.x;
            canvas.panY = event.clientY - canvas.panStart.y;
            renderCanvas();
            return;
        }
        if (canvas.selected.size === 1) {
            const elId = [...canvas.selected][0];
            const item = state.currentProject?.elements?.find((entry) => entry.id === elId);
            if (!item) return;
            item.position = item.position || { x: 0, y: 0 };
            item.position.x += (event.clientX - canvas.dragStart.x) / canvas.zoom;
            item.position.y += (event.clientY - canvas.dragStart.y) / canvas.zoom;
            canvas.dragStart = { x: event.clientX, y: event.clientY };
            renderCanvas();
        }
    }

    function canvasMouseUp() {
        const canvas = state.canvas;
        if (canvas.dragging && canvas.selected.size === 1) {
            const elId = [...canvas.selected][0];
            const item = state.currentProject?.elements?.find((entry) => entry.id === elId);
            if (item) api('PUT', '/projects/' + state.currentProjectId + '/elements/' + elId, { position: item.position });
        }
        canvas.dragging = false;
    }

    function canvasWheel(event) { event.preventDefault(); state.canvas.zoom = Math.max(0.3, Math.min(3, state.canvas.zoom * (event.deltaY > 0 ? 0.9 : 1.1))); renderCanvas(); }
    function canvasZoomIn() { state.canvas.zoom = Math.min(3, state.canvas.zoom * 1.2); renderCanvas(); }
    function canvasZoomOut() { state.canvas.zoom = Math.max(0.3, state.canvas.zoom * 0.8); renderCanvas(); }
    function canvasResetView() { state.canvas.zoom = 1; state.canvas.panX = 0; state.canvas.panY = 0; renderCanvas(); }
    function canvasDoubleClick(event) {
        const rect = document.getElementById('canvas-container').getBoundingClientRect();
        openElementForm(null, (event.clientX - rect.left - state.canvas.panX) / state.canvas.zoom, (event.clientY - rect.top - state.canvas.panY) / state.canvas.zoom);
    }
    function setCanvasMode(mode) {
        state.canvas.mode = mode;
        state.canvas.linkSource = null;
        state.canvas.selected.clear();
        [['move', 'btn-mode-move'], ['link', 'btn-mode-link'], ['hierarchy', 'btn-mode-hierarchy']].forEach(([candidate, id]) => {
            const btn = document.getElementById(id);
            if (!btn) return;
            btn.classList.toggle('btn-primary', candidate === mode);
        });
        renderCanvas();
    }
})();
