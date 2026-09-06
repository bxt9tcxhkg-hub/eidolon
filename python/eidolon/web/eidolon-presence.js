const PRESENCE_PHASES = {
    idle: { warp: 0.055, pulse: 0.42, mote: 0.62, gaze: 0.55 },
    denkt: { warp: 0.16, pulse: 0.86, mote: 0.88, gaze: 0.85 },
    arbeitet: { warp: 0.22, pulse: 1.05, mote: 0.96, gaze: 0.8 },
    antwortet: { warp: 0.07, pulse: 0.34, mote: 0.74, gaze: 1 },
};

const PRESENCE_VERT = [
    'attribute vec2 aPos;',
    'varying vec2 vUv;',
    'void main() {',
    '  vUv = aPos * 0.5 + 0.5;',
    '  gl_Position = vec4(aPos, 0.0, 1.0);',
    '}',
].join('\n');

const PRESENCE_FRAG = [
    'precision mediump float;',
    'varying vec2 vUv;',
    'uniform sampler2D uStill;',
    'uniform float uTime;',
    'uniform float uWarp;',
    'uniform float uPulse;',
    'uniform float uMote;',
    'uniform vec2 uGaze;',
    'float hash(vec2 p) {',
    '  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);',
    '}',
    'float noise(vec2 p) {',
    '  vec2 i = floor(p);',
    '  vec2 f = fract(p);',
    '  float a = hash(i);',
    '  float b = hash(i + vec2(1.0, 0.0));',
    '  float c = hash(i + vec2(0.0, 1.0));',
    '  float d = hash(i + vec2(1.0, 1.0));',
    '  vec2 u = f * f * (3.0 - 2.0 * f);',
    '  return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;',
    '}',
    'float fbm(vec2 p) {',
    '  float v = 0.0;',
    '  float a = 0.5;',
    '  for (int i = 0; i < 4; i++) {',
    '    v += a * noise(p);',
    '    p = p * 2.03 + vec2(1.7, 9.2);',
    '    a *= 0.5;',
    '  }',
    '  return v;',
    '}',
    'vec2 curl(vec2 p, float t) {',
    '  float e = 0.11;',
    '  vec2 d = vec2(e, 0.0);',
    '  float n1 = fbm(p + d.yx + t);',
    '  float n2 = fbm(p - d.yx + t);',
    '  float n3 = fbm(p + d.xy + t);',
    '  float n4 = fbm(p - d.xy + t);',
    '  return vec2(n1 - n2, n4 - n3);',
    '}',
    'void main() {',
    '  vec2 uv = vUv;',
    '  float dens = max(texture2D(uStill, uv).r, texture2D(uStill, uv).g * 0.72);',
    '  vec2 flow = curl(uv * 3.15, uTime * uWarp);',
    '  vec2 billow = curl(uv * 1.28 + vec2(2.2, 0.35), uTime * uWarp * 0.34);',
    '  float move = smoothstep(0.02, 0.38, dens);',
    '  vec2 warped = uv + flow * (0.010 + move * 0.036) + billow * move * 0.018;',
    '  vec4 ink = texture2D(uStill, clamp(warped, 0.0, 1.0));',
    '  vec2 mote = vec2(0.56, 0.58) + uGaze * 0.11;',
    '  vec2 md = (uv - mote) * vec2(1.0, 1.06);',
    '  float d2 = dot(md, md);',
    '  float core = exp(-d2 * 38.0);',
    '  float halo = exp(-d2 * 8.5);',
    '  vec3 gold = vec3(1.0, 0.88, 0.62);',
    '  ink.rgb += gold * (core * 0.78 + halo * 0.32) * uMote * uPulse;',
    '  gl_FragColor = ink;',
    '}',
].join('\n');

const presenceMarks = [];
let presenceRaf = 0;
let presenceListening = false;
let presenceFocusComposer = false;

function presenceMotionAllowed() {
    if (document.documentElement.getAttribute('data-animations') === 'off') return false;
    try {
        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return false;
        }
    } catch (_) { /* ignore */ }
    return true;
}

function presencePhaseName(root) {
    const phase = root && root.dataset ? root.dataset.turnPhase : 'idle';
    return PRESENCE_PHASES[phase] ? phase : 'idle';
}

function presenceClamp(value, lo, hi) {
    return Math.max(lo, Math.min(hi, value));
}

function presenceGaze(root, phase) {
    const rect = root.getBoundingClientRect();
    if (!rect.width || !rect.height) return { x: 0, y: 0 };
    const cx = rect.left + rect.width * 0.5;
    const cy = rect.top + rect.height * 0.5;
    let target = null;
    if (phase === 'antwortet') {
        target = document.getElementById('chat-messages');
    } else if (phase === 'denkt' || phase === 'arbeitet') {
        target = document.getElementById('chat-input') || document.getElementById('chat-agent-status');
    } else if (presenceFocusComposer) {
        target = document.getElementById('chat-input');
    }
    if (!target) return { x: 0, y: 0 };
    const box = target.getBoundingClientRect();
    if (!box.width && !box.height) return { x: 0, y: 0 };
    const tx = box.left + box.width * 0.5;
    const ty = box.top + Math.min(box.height * 0.28, 36);
    const knobs = PRESENCE_PHASES[phase] || PRESENCE_PHASES.idle;
    return {
        x: presenceClamp(((tx - cx) / Math.max(window.innerWidth, 1)) * 2.6 * knobs.gaze, -1, 1),
        y: presenceClamp(((cy - ty) / Math.max(window.innerHeight, 1)) * 2.6 * knobs.gaze, -1, 1),
    };
}

function compilePresenceShader(gl, type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        gl.deleteShader(shader);
        return null;
    }
    return shader;
}

function createPresenceProgram(gl) {
    const vert = compilePresenceShader(gl, gl.VERTEX_SHADER, PRESENCE_VERT);
    const frag = compilePresenceShader(gl, gl.FRAGMENT_SHADER, PRESENCE_FRAG);
    if (!vert || !frag) return null;
    const program = gl.createProgram();
    gl.attachShader(program, vert);
    gl.attachShader(program, frag);
    gl.bindAttribLocation(program, 0, 'aPos');
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        gl.deleteProgram(program);
        return null;
    }
    return program;
}

function uploadPresenceTexture(gl, image) {
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 1);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
    return texture;
}

function createPresenceWebGL(canvas, image) {
    const gl = canvas.getContext('webgl', {
        alpha: false,
        antialias: false,
        depth: false,
        stencil: false,
        premultipliedAlpha: true,
        preserveDrawingBuffer: false,
        powerPreference: 'low-power',
    });
    if (!gl) return null;
    const program = createPresenceProgram(gl);
    if (!program) return null;
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const texture = uploadPresenceTexture(gl, image);
    const loc = {
        time: gl.getUniformLocation(program, 'uTime'),
        warp: gl.getUniformLocation(program, 'uWarp'),
        pulse: gl.getUniformLocation(program, 'uPulse'),
        mote: gl.getUniformLocation(program, 'uMote'),
        gaze: gl.getUniformLocation(program, 'uGaze'),
        still: gl.getUniformLocation(program, 'uStill'),
    };
    return {
        kind: 'webgl',
        draw: function (width, height, time, knobs, gaze) {
            if (canvas.width !== width || canvas.height !== height) {
                canvas.width = width;
                canvas.height = height;
                gl.viewport(0, 0, width, height);
            }
            gl.viewport(0, 0, canvas.width, canvas.height);
            gl.useProgram(program);
            gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
            gl.enableVertexAttribArray(0);
            gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
            gl.activeTexture(gl.TEXTURE0);
            gl.bindTexture(gl.TEXTURE_2D, texture);
            gl.uniform1i(loc.still, 0);
            gl.uniform1f(loc.time, time);
            gl.uniform1f(loc.warp, knobs.warp);
            gl.uniform1f(loc.pulse, knobs.pulse);
            gl.uniform1f(loc.mote, knobs.mote);
            gl.uniform2f(loc.gaze, gaze.x, gaze.y);
            gl.drawArrays(gl.TRIANGLES, 0, 3);
        },
    };
}

function buildPresenceLuma(image) {
    const size = 48;
    const map = document.createElement('canvas');
    map.width = size;
    map.height = size;
    const ctx = map.getContext('2d', { willReadFrequently: true });
    if (!ctx) return null;
    ctx.drawImage(image, 0, 0, size, size);
    return ctx.getImageData(0, 0, size, size);
}

function hashPresenceNoise(x, y) {
    const s = Math.sin(x * 127.1 + y * 311.7) * 43758.5453;
    return s - Math.floor(s);
}

function fadePresenceNoise(t) {
    return t * t * (3 - 2 * t);
}

function valuePresenceNoise(x, y) {
    const x0 = Math.floor(x);
    const y0 = Math.floor(y);
    const fx = fadePresenceNoise(x - x0);
    const fy = fadePresenceNoise(y - y0);
    const a = hashPresenceNoise(x0, y0);
    const b = hashPresenceNoise(x0 + 1, y0);
    const c = hashPresenceNoise(x0, y0 + 1);
    const d = hashPresenceNoise(x0 + 1, y0 + 1);
    return a + (b - a) * fx + (c - a) * fy * (1 - fx) + (d - b) * fx * fy;
}

function createPresenceCanvas2D(canvas, image) {
    const luma = buildPresenceLuma(image);
    return {
        kind: 'canvas2d',
        draw: function (width, height, time, knobs, gaze) {
            if (canvas.width !== width || canvas.height !== height) {
                canvas.width = width;
                canvas.height = height;
            }
            const ctx = canvas.getContext('2d', { alpha: false });
            if (!ctx) return;
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, width, height);
            const cells = 14;
            const srcW = image.naturalWidth || image.width;
            const srcH = image.naturalHeight || image.height;
            const cellW = width / cells;
            const cellH = height / cells;
            const srcCellW = srcW / cells;
            const srcCellH = srcH / cells;
            const lumW = luma ? luma.width : 1;
            const lumH = luma ? luma.height : 1;
            const data = luma ? luma.data : null;
            for (let y = 0; y < cells; y += 1) {
                for (let x = 0; x < cells; x += 1) {
                    const u = (x + 0.5) / cells;
                    const v = (y + 0.5) / cells;
                    let dens = 0.35;
                    if (data) {
                        const lx = Math.min(lumW - 1, Math.floor(u * lumW));
                        const ly = Math.min(lumH - 1, Math.floor(v * lumH));
                        const i = (ly * lumW + lx) * 4;
                        dens = Math.max(data[i] / 255, data[i + 1] / 255 * 0.72);
                    }
                    const n1 = valuePresenceNoise(u * 3.2 + time * knobs.warp, v * 3.2);
                    const n2 = valuePresenceNoise(u * 1.3 + 2.1, v * 1.3 - time * knobs.warp * 0.34);
                    const move = Math.max(0, (dens - 0.04) / 0.36);
                    const ox = (n1 - 0.5) * srcCellW * (0.18 + move * 0.72);
                    const oy = (n2 - 0.5) * srcCellH * (0.16 + move * 0.64);
                    const sx = Math.min(Math.max(0, x * srcCellW + ox), Math.max(0, srcW - srcCellW));
                    const sy = Math.min(Math.max(0, y * srcCellH + oy), Math.max(0, srcH - srcCellH));
                    ctx.drawImage(
                        image,
                        sx,
                        sy,
                        srcCellW,
                        srcCellH,
                        x * cellW,
                        y * cellH,
                        cellW + 0.6,
                        cellH + 0.6
                    );
                }
            }
            const mx = (0.56 + gaze.x * 0.11) * width;
            const my = (1 - (0.58 + gaze.y * 0.11)) * height;
            const radius = Math.max(width, height) * 0.52;
            const glow = ctx.createRadialGradient(mx, my, 0, mx, my, radius);
            const pulse = knobs.mote * knobs.pulse;
            glow.addColorStop(0, 'rgba(255, 240, 196,' + (0.52 * pulse).toFixed(3) + ')');
            glow.addColorStop(0.28, 'rgba(217, 161, 92,' + (0.22 * pulse).toFixed(3) + ')');
            glow.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.globalCompositeOperation = 'screen';
            ctx.fillStyle = glow;
            ctx.fillRect(0, 0, width, height);
            ctx.globalCompositeOperation = 'source-over';
        },
    };
}

function presenceBackingSize(root) {
    const css = Math.max(root.clientWidth || 48, root.clientHeight || 48);
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    return Math.max(64, Math.round(css * dpr));
}

function showPresenceStill(mark) {
    mark.root.classList.remove('is-live');
    mark.canvas.hidden = true;
}

function showPresenceLive(mark) {
    mark.root.classList.add('is-live');
    mark.canvas.hidden = false;
}

function bindPresenceMark(root) {
    const image = root.querySelector('.eidolon-presence-still');
    const canvas = root.querySelector('.eidolon-presence-live');
    if (!image || !canvas) return null;
    const start = function () {
        if (root._eidolonPresenceBound) return;
        if (!image.naturalWidth) return;
        root._eidolonPresenceBound = true;
        const engine = createPresenceWebGL(canvas, image) || createPresenceCanvas2D(canvas, image);
        const mark = {
            root: root,
            canvas: canvas,
            engine: engine,
            visible: true,
        };
        if (typeof IntersectionObserver === 'function') {
            mark.io = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    mark.visible = entry.isIntersecting && entry.intersectionRatio > 0;
                });
            }, { threshold: 0.01 });
            mark.io.observe(root);
        }
        presenceMarks.push(mark);
        syncEidolonPresenceMotion();
    };
    if (image.complete && image.naturalWidth) start();
    else image.addEventListener('load', start, { once: true });
}

function presenceAnyVisible() {
    return presenceMarks.some(function (mark) { return mark.visible; });
}

function drawPresenceFrame(now) {
    presenceRaf = 0;
    if (!presenceMotionAllowed()) {
        presenceMarks.forEach(showPresenceStill);
        return;
    }
    if (!presenceAnyVisible()) {
        presenceRaf = window.requestAnimationFrame(drawPresenceFrame);
        return;
    }
    const time = now * 0.001;
    const pulseWave = 0.5 + 0.5 * Math.sin(time * 1.7);
    presenceMarks.forEach(function (mark) {
        if (!mark.visible || !mark.engine) {
            showPresenceStill(mark);
            return;
        }
        const phase = presencePhaseName(mark.root);
        const knobs = Object.assign({}, PRESENCE_PHASES[phase]);
        knobs.pulse = knobs.pulse * (0.82 + pulseWave * 0.18);
        const size = presenceBackingSize(mark.root);
        showPresenceLive(mark);
        mark.engine.draw(size, size, time, knobs, presenceGaze(mark.root, phase));
    });
    presenceRaf = window.requestAnimationFrame(drawPresenceFrame);
}

function stopPresenceLoop() {
    if (presenceRaf) {
        window.cancelAnimationFrame(presenceRaf);
        presenceRaf = 0;
    }
    presenceMarks.forEach(showPresenceStill);
}

function startPresenceLoop() {
    if (presenceRaf) return;
    presenceRaf = window.requestAnimationFrame(drawPresenceFrame);
}

function bindPresenceChrome() {
    if (presenceListening) return;
    presenceListening = true;
    const input = document.getElementById('chat-input');
    if (input) {
        input.addEventListener('focus', function () { presenceFocusComposer = true; });
        input.addEventListener('blur', function () { presenceFocusComposer = false; });
        presenceFocusComposer = document.activeElement === input;
    }
    try {
        const media = window.matchMedia('(prefers-reduced-motion: reduce)');
        const onChange = function () { syncEidolonPresenceMotion(); };
        if (media.addEventListener) media.addEventListener('change', onChange);
        else if (media.addListener) media.addListener(onChange);
    } catch (_) { /* ignore */ }
    new MutationObserver(function () { syncEidolonPresenceMotion(); })
        .observe(document.documentElement, { attributes: true, attributeFilter: ['data-animations'] });
}

function startEidolonPresence() {
    document.querySelectorAll('[data-eidolon-presence]').forEach(bindPresenceMark);
    bindPresenceChrome();
    syncEidolonPresenceMotion();
}

function syncEidolonPresenceMotion() {
    if (!presenceMotionAllowed()) {
        stopPresenceLoop();
        return;
    }
    startPresenceLoop();
}

window.startEidolonPresence = startEidolonPresence;
window.syncEidolonPresenceMotion = syncEidolonPresenceMotion;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startEidolonPresence);
} else {
    startEidolonPresence();
}
