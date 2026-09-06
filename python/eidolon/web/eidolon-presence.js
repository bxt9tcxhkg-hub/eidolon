const PRESENCE_ASSET_VERSION = '20260906-phases';
const PRESENCE_STILL_PNG = '/assets/media/eidolon-presence.png';

const PRESENCE_ARIA = {
    idle: 'Eidolon ist bereit',
    schreibt: 'Eidolon achtet auf die Eingabe',
    denkt: 'Eidolon denkt',
    arbeitet: 'Eidolon arbeitet',
    antwortet: 'Eidolon antwortet',
};

// Distinct motion signatures, readable at 36–42px within ~1s.
// schreibt = slow horizontal drift + soft glow; denkt = filament churn + quick pulse;
// antwortet = speaking rhythm + gaze toward transcript; idle quieter than all three.
const PRESENCE_PHASES = {
    idle: { warp: 0.38, pulse: 0.82, mote: 0.86, gaze: 0.28, drift: 0.18, churn: 0.22, rhythm: 1.35, mode: 0 },
    schreibt: { warp: 0.22, pulse: 0.9, mote: 0.96, gaze: 1.2, drift: 1.0, churn: 0.06, rhythm: 1.2, mode: 1 },
    denkt: { warp: 1.18, pulse: 1.42, mote: 1.38, gaze: 0.45, drift: 0.05, churn: 1.15, rhythm: 6.8, mode: 2 },
    arbeitet: { warp: 1.36, pulse: 1.52, mote: 1.44, gaze: 0.42, drift: 0.06, churn: 1.32, rhythm: 7.4, mode: 3 },
    antwortet: { warp: 0.26, pulse: 1.22, mote: 1.2, gaze: 1.28, drift: 0.04, churn: 0.12, rhythm: 3.05, mode: 4 },
};

const PRESENCE_PHASE_CLASSES = ['is-schreibt', 'is-denkt', 'is-antwortet'];

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
    'uniform float uDrift;',
    'uniform float uChurn;',
    'uniform float uRhythm;',
    'uniform float uMode;',
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
    '  float move = smoothstep(0.02, 0.38, dens);',
    '  float isWrite = step(0.5, uMode) * (1.0 - step(1.5, uMode));',
    '  float isThink = step(1.5, uMode) * (1.0 - step(3.5, uMode));',
    '  float isSpeak = step(3.5, uMode);',
    '  vec2 flow = curl(uv * 3.15, uTime * uWarp);',
    '  vec2 filament = curl(uv * 7.4 + vec2(0.4, 1.1), uTime * (uWarp + uChurn) * 1.85);',
    '  vec2 billow = curl(uv * 1.18 + vec2(2.2, 0.35), uTime * uWarp * 0.42);',
    '  float horiz = sin(uTime * 0.82 + uv.y * 3.1) * 0.12 * uDrift;',
    '  vec2 drift = vec2(horiz, sin(uTime * 0.31) * 0.014 * uDrift);',
    '  vec2 churn = filament * (0.05 + move * 0.22) * uChurn;',
    '  vec2 speak = vec2(0.0, sin(uTime * uRhythm) * 0.05) * isSpeak;',
    '  vec2 warped = uv + flow * (0.018 + move * 0.07) + drift * move + churn + billow * move * 0.035 + speak * move;',
    '  vec4 ink = texture2D(uStill, clamp(warped, 0.0, 1.0));',
    '  float moteSpeed = mix(0.7, 3.4, clamp(uChurn, 0.0, 1.0));',
    '  vec2 moteWalk = vec2(sin(uTime * moteSpeed), cos(uTime * moteSpeed * 0.78));',
    '  moteWalk.x += sin(uTime * 0.88) * 0.09 * uDrift;',
    '  moteWalk.y *= mix(1.0, 0.2, clamp(uDrift, 0.0, 1.0));',
    '  vec2 mote = vec2(0.56, 0.58) + uGaze * mix(0.12, 0.24, isSpeak) + moteWalk * mix(0.028, 0.075, clamp(uChurn, 0.0, 1.0));',
    '  mote += vec2(-0.08, 0.1) * isSpeak;',
    '  mote += vec2(0.0, -0.08) * isWrite;',
    '  float beat = 0.62 + 0.38 * sin(uTime * uRhythm);',
    '  float speakBeat = 0.36 + 0.64 * pow(0.5 + 0.5 * sin(uTime * uRhythm), 2.0);',
    '  float thinkBeat = 0.42 + 0.58 * sin(uTime * uRhythm);',
    '  beat = mix(beat, thinkBeat, isThink);',
    '  beat = mix(beat, speakBeat, isSpeak);',
    '  float coreTight = mix(20.0, 50.0, clamp(uChurn + isThink * 0.35, 0.0, 1.0));',
    '  float haloWide = mix(8.4, 3.1, clamp(uDrift + isWrite * 0.4, 0.0, 1.0));',
    '  vec2 md = (uv - mote) * vec2(1.0, 1.06);',
    '  float d2 = dot(md, md);',
    '  float core = exp(-d2 * coreTight);',
    '  float halo = exp(-d2 * haloWide);',
    '  vec3 gold = vec3(1.0, 0.88, 0.62);',
    '  ink.rgb += gold * (core * 1.08 + halo * 0.58) * uMote * uPulse * beat;',
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

function setPresenceEngineAttr(root, kind) {
    if (!root) return;
    root.setAttribute('data-presence-engine', kind);
}

function presenceTurnPhase(root) {
    const phase = root && root.dataset ? root.dataset.turnPhase : 'idle';
    return PRESENCE_PHASES[phase] && phase !== 'schreibt' ? phase : 'idle';
}

function presenceVisualPhase(root) {
    const turn = presenceTurnPhase(root);
    if (turn === 'idle' && presenceFocusComposer) return 'schreibt';
    return turn;
}

function presencePhaseName(root) {
    return presenceVisualPhase(root);
}

function applyPresencePhaseAttrs() {
    document.querySelectorAll('[data-eidolon-presence]').forEach(function (el) {
        const visual = presenceVisualPhase(el);
        el.setAttribute('data-presence-phase', visual);
        PRESENCE_PHASE_CLASSES.forEach(function (cls) {
            el.classList.toggle(cls, cls === 'is-' + visual);
        });
        if (el.getAttribute('role') === 'img') {
            el.setAttribute('aria-label', PRESENCE_ARIA[visual] || PRESENCE_ARIA.idle);
        }
    });
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
    } else if (phase === 'schreibt' || presenceFocusComposer) {
        target = document.getElementById('chat-input');
    }
    if (!target) return { x: 0, y: 0 };
    const box = target.getBoundingClientRect();
    if (!box.width && !box.height) return { x: 0, y: 0 };
    const tx = box.left + box.width * 0.5;
    const ty = box.top + Math.min(box.height * 0.28, 36);
    const knobs = PRESENCE_PHASES[phase] || PRESENCE_PHASES.idle;
    let x = presenceClamp(((tx - cx) / Math.max(window.innerWidth, 1)) * 2.6 * knobs.gaze, -1, 1);
    let y = presenceClamp(((cy - ty) / Math.max(window.innerHeight, 1)) * 2.6 * knobs.gaze, -1, 1);
    if (phase === 'antwortet') {
        x = presenceClamp(x - 0.22, -1, 1);
        y = presenceClamp(y + 0.34, -1, 1);
    }
    return { x: x, y: y };
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

function getPresenceGL(canvas) {
    const opts = {
        alpha: false,
        antialias: false,
        depth: false,
        stencil: false,
        premultipliedAlpha: true,
        preserveDrawingBuffer: false,
        powerPreference: 'low-power',
    };
    try {
        return canvas.getContext('webgl', opts) || canvas.getContext('experimental-webgl', opts);
    } catch (_) {
        return null;
    }
}

function uploadPresenceTexture(gl, image) {
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, 1);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    try {
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
        if (gl.getError() !== gl.NO_ERROR) {
            gl.deleteTexture(texture);
            return null;
        }
    } catch (_) {
        gl.deleteTexture(texture);
        return null;
    }
    return texture;
}

function createPresenceWebGL(canvas, image) {
    const gl = getPresenceGL(canvas);
    if (!gl) return null;
    const program = createPresenceProgram(gl);
    if (!program) return null;
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const texture = uploadPresenceTexture(gl, image);
    if (!texture) return null;
    const loc = {
        time: gl.getUniformLocation(program, 'uTime'),
        warp: gl.getUniformLocation(program, 'uWarp'),
        pulse: gl.getUniformLocation(program, 'uPulse'),
        mote: gl.getUniformLocation(program, 'uMote'),
        gaze: gl.getUniformLocation(program, 'uGaze'),
        drift: gl.getUniformLocation(program, 'uDrift'),
        churn: gl.getUniformLocation(program, 'uChurn'),
        rhythm: gl.getUniformLocation(program, 'uRhythm'),
        mode: gl.getUniformLocation(program, 'uMode'),
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
            gl.uniform1f(loc.drift, knobs.drift);
            gl.uniform1f(loc.churn, knobs.churn);
            gl.uniform1f(loc.rhythm, knobs.rhythm);
            gl.uniform1f(loc.mode, knobs.mode);
            gl.drawArrays(gl.TRIANGLES, 0, 3);
        },
    };
}

function presenceWebGLUsable(image) {
    const probe = document.createElement('canvas');
    probe.width = 8;
    probe.height = 8;
    try {
        return !!createPresenceWebGL(probe, image);
    } catch (_) {
        return false;
    }
}

function replacePresenceCanvas(oldCanvas) {
    const next = oldCanvas.cloneNode(false);
    if (oldCanvas.parentNode) oldCanvas.parentNode.replaceChild(next, oldCanvas);
    return next;
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
            const cells = 16;
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
                    const move = Math.max(0, (dens - 0.04) / 0.36);
                    const mode = knobs.mode || 0;
                    let ox = 0;
                    let oy = 0;
                    if (mode === 1) {
                        ox = Math.sin(time * 0.82 + v * 3.1) * srcCellW * (1.2 + move * 0.55) * knobs.drift;
                        oy = Math.sin(time * 0.31) * srcCellH * 0.14 * knobs.drift;
                    } else if (mode === 2 || mode === 3) {
                        const n1 = valuePresenceNoise(u * 6.4 + time * knobs.churn * 4.2, v * 6.4 + time * knobs.churn * 3.1);
                        const n2 = valuePresenceNoise(u * 5.1 - time * knobs.churn * 3.6, v * 5.1 + time * knobs.churn * 2.4);
                        const n3 = valuePresenceNoise(u * 9.2 + time * knobs.churn * 5.0, v * 9.2);
                        ox = (n1 - 0.5) * srcCellW * (1.45 + move * 1.85) * knobs.churn;
                        oy = (n2 - 0.5) * srcCellH * (1.4 + move * 1.7) * knobs.churn + (n3 - 0.5) * srcCellH * move * 0.85;
                    } else if (mode === 4) {
                        const n1 = valuePresenceNoise(u * 2.1 + time * 0.35, v * 2.1);
                        ox = (n1 - 0.5) * srcCellW * 0.28;
                        oy = Math.sin(time * knobs.rhythm) * srcCellH * (0.62 + move * 0.32);
                    } else {
                        const n1 = valuePresenceNoise(u * 3.2 + time * knobs.warp * 1.8, v * 3.2 + time * knobs.warp * 0.45);
                        const n2 = valuePresenceNoise(u * 1.3 + 2.1 - time * knobs.warp * 0.75, v * 1.3 - time * knobs.warp * 0.95);
                        const n3 = valuePresenceNoise(u * 6.1 + time * knobs.warp * 2.1, v * 6.1);
                        ox = (n1 - 0.5) * srcCellW * (0.4 + move * 0.85) + (n3 - 0.5) * srcCellW * move * 0.35;
                        oy = (n2 - 0.5) * srcCellH * (0.36 + move * 0.75) + (n3 - 0.5) * srcCellH * move * 0.28;
                    }
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
                        cellW + 0.8,
                        cellH + 0.8
                    );
                }
            }
            const mode = knobs.mode || 0;
            let mx;
            let my;
            let pulse;
            let radius = Math.max(width, height) * 0.68;
            if (mode === 1) {
                mx = (0.56 + gaze.x * 0.16 + Math.sin(time * 0.88) * 0.1) * width;
                my = (1 - (0.44 + gaze.y * 0.1)) * height;
                pulse = knobs.mote * knobs.pulse * (0.86 + 0.14 * Math.sin(time * knobs.rhythm));
                radius = Math.max(width, height) * 0.86;
            } else if (mode === 2 || mode === 3) {
                mx = (0.56 + gaze.x * 0.1 + Math.sin(time * 3.4) * 0.075) * width;
                my = (1 - (0.58 + gaze.y * 0.1 + Math.cos(time * 2.9) * 0.065)) * height;
                pulse = knobs.mote * knobs.pulse * (0.48 + 0.52 * Math.sin(time * knobs.rhythm));
                radius = Math.max(width, height) * 0.52;
            } else if (mode === 4) {
                const beat = Math.pow(0.5 + 0.5 * Math.sin(time * knobs.rhythm), 2);
                mx = (0.4 + gaze.x * 0.22) * width;
                my = (1 - (0.7 + gaze.y * 0.16)) * height;
                pulse = knobs.mote * knobs.pulse * (0.4 + 0.6 * beat);
                radius = Math.max(width, height) * 0.62;
            } else {
                const driftX = Math.sin(time * 0.9) * 0.04;
                const driftY = Math.cos(time * 0.73) * 0.035;
                mx = (0.56 + gaze.x * 0.1 + driftX) * width;
                my = (1 - (0.58 + gaze.y * 0.1 + driftY)) * height;
                pulse = knobs.mote * knobs.pulse * (0.82 + 0.18 * Math.sin(time * knobs.rhythm));
            }
            const glow = ctx.createRadialGradient(mx, my, 0, mx, my, radius);
            glow.addColorStop(0, 'rgba(255, 240, 196,' + (0.78 * pulse).toFixed(3) + ')');
            glow.addColorStop(0.22, 'rgba(217, 161, 92,' + (0.38 * pulse).toFixed(3) + ')');
            glow.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.globalCompositeOperation = 'screen';
            ctx.fillStyle = glow;
            ctx.fillRect(0, 0, width, height);
            ctx.globalCompositeOperation = 'source-over';
        },
    };
}

function presenceTextureUrl(image) {
    const src = image && image.getAttribute ? String(image.getAttribute('src') || '') : '';
    if (/\.png(\?|#|$)/i.test(src) && src.toLowerCase().indexOf('.webp') === -1) {
        return src;
    }
    return PRESENCE_STILL_PNG;
}

function loadPresenceTextureImage(displayImage) {
    return new Promise(function (resolve, reject) {
        const url = presenceTextureUrl(displayImage);
        const tex = new Image();
        tex.decoding = 'async';
        const finish = function () {
            if (!tex.naturalWidth) {
                reject(new Error('presence png empty'));
                return;
            }
            if (typeof tex.decode === 'function') {
                tex.decode().then(function () { resolve(tex); }).catch(function () { resolve(tex); });
                return;
            }
            resolve(tex);
        };
        tex.onload = finish;
        tex.onerror = function () { reject(new Error('presence png failed')); };
        tex.src = url;
        if (tex.complete && tex.naturalWidth) finish();
    });
}

function resolvePresenceTexture(displayImage) {
    return loadPresenceTextureImage(displayImage).catch(function () {
        if (displayImage && displayImage.naturalWidth) return displayImage;
        throw new Error('presence texture unavailable');
    });
}

function createPresenceEngine(canvas, image) {
    if (presenceWebGLUsable(image)) {
        try {
            const engine = createPresenceWebGL(canvas, image);
            if (engine) return { canvas: canvas, engine: engine };
        } catch (_) { /* canvas may now be WebGL-locked */ }
        canvas = replacePresenceCanvas(canvas);
    }
    try {
        return { canvas: canvas, engine: createPresenceCanvas2D(canvas, image) };
    } catch (_) {
        return { canvas: canvas, engine: null };
    }
}

function presenceBackingSize(root) {
    const css = Math.max(root.clientWidth || 48, root.clientHeight || 48);
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    return Math.max(72, Math.round(css * dpr));
}

function showPresenceStill(mark) {
    mark.root.classList.remove('is-live');
    mark.canvas.hidden = true;
    setPresenceEngineAttr(mark.root, 'still');
}

function showPresenceLive(mark) {
    mark.root.classList.add('is-live');
    mark.canvas.hidden = false;
    setPresenceEngineAttr(mark.root, mark.engine ? mark.engine.kind : 'still');
}

function bindPresenceMark(root) {
    const displayImage = root.querySelector('.eidolon-presence-still');
    const canvas = root.querySelector('.eidolon-presence-live');
    if (!displayImage || !canvas) return null;
    if (root._eidolonPresenceBound) return null;
    root._eidolonPresenceBound = true;
    setPresenceEngineAttr(root, 'still');
    resolvePresenceTexture(displayImage).then(function (image) {
        const created = createPresenceEngine(canvas, image);
        const mark = {
            root: root,
            canvas: created.canvas,
            engine: created.engine,
            image: image,
            visible: true,
        };
        if (created.engine && created.engine.kind === 'webgl') {
            created.canvas.addEventListener('webglcontextlost', function (event) {
                event.preventDefault();
                const fresh = replacePresenceCanvas(mark.canvas);
                mark.canvas = fresh;
                try {
                    mark.engine = createPresenceCanvas2D(fresh, image);
                } catch (_) {
                    mark.engine = null;
                }
                setPresenceEngineAttr(root, mark.engine ? mark.engine.kind : 'still');
                if (!mark.engine) showPresenceStill(mark);
            }, false);
        }
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
    }).catch(function () {
        root._eidolonPresenceBound = false;
        setPresenceEngineAttr(root, 'still');
    });
    return root;
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
    presenceMarks.forEach(function (mark) {
        if (!mark.visible || !mark.engine) {
            showPresenceStill(mark);
            return;
        }
        const phase = presenceVisualPhase(mark.root);
        const knobs = Object.assign({}, PRESENCE_PHASES[phase]);
        knobs.pulse = presencePulseAmount(time, phase, knobs);
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

function presencePulseAmount(time, phase, knobs) {
    if (phase === 'schreibt') return knobs.pulse * (0.88 + 0.12 * Math.sin(time * knobs.rhythm));
    if (phase === 'denkt' || phase === 'arbeitet') return knobs.pulse * (0.5 + 0.5 * Math.sin(time * knobs.rhythm));
    if (phase === 'antwortet') {
        const beat = Math.sin(time * knobs.rhythm);
        return knobs.pulse * (0.42 + 0.58 * (beat * beat));
    }
    return knobs.pulse * (0.84 + 0.16 * Math.sin(time * knobs.rhythm));
}

function setPresenceComposerFocus(next) {
    const focused = !!next;
    if (presenceFocusComposer === focused) return;
    presenceFocusComposer = focused;
    applyPresencePhaseAttrs();
}

function bindPresenceChrome() {
    if (presenceListening) return;
    presenceListening = true;
    const input = document.getElementById('chat-input');
    if (input) {
        input.addEventListener('focus', function () { setPresenceComposerFocus(true); });
        input.addEventListener('blur', function () { setPresenceComposerFocus(false); });
        input.addEventListener('input', function () { setPresenceComposerFocus(true); });
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
    new MutationObserver(function () { applyPresencePhaseAttrs(); })
        .observe(document.documentElement, { subtree: true, attributes: true, attributeFilter: ['data-turn-phase'] });
    applyPresencePhaseAttrs();
}

function pruneDetachedPresenceMarks() {
    for (let i = presenceMarks.length - 1; i >= 0; i -= 1) {
        const mark = presenceMarks[i];
        if (!mark.root || !document.documentElement.contains(mark.root)) {
            if (mark.io) mark.io.disconnect();
            presenceMarks.splice(i, 1);
        }
    }
}

function refreshEidolonPresenceMarks() {
    pruneDetachedPresenceMarks();
    document.querySelectorAll('[data-eidolon-presence]').forEach(bindPresenceMark);
    bindPresenceChrome();
    syncEidolonPresenceMotion();
}

function startEidolonPresence() {
    refreshEidolonPresenceMarks();
}

function syncEidolonPresenceMotion() {
    if (!presenceMotionAllowed()) {
        stopPresenceLoop();
        return;
    }
    startPresenceLoop();
}

window.startEidolonPresence = startEidolonPresence;
window.refreshEidolonPresenceMarks = refreshEidolonPresenceMarks;
window.syncEidolonPresenceMotion = syncEidolonPresenceMotion;
window.applyPresencePhaseAttrs = applyPresencePhaseAttrs;
window.PRESENCE_ARIA = PRESENCE_ARIA;
window.PRESENCE_ASSET_VERSION = PRESENCE_ASSET_VERSION;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startEidolonPresence);
} else {
    startEidolonPresence();
}
