// 3D 体素版《谁才是最强AI？》——每帧由 renderAt(T) 确定性地画出来。
// 小橙 = Claude 的橙色小宠物；小蓝 = ChatGPT（Codex）的蓝色机器人宠物。
import * as THREE from './node_modules/three/build/three.module.js';

const W = 1280, H = 720;
const glCanvas = document.getElementById('gl');
const ov = document.getElementById('ov');
const ctx = ov.getContext('2d');

const renderer = new THREE.WebGLRenderer({ canvas: glCanvas, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(38, W / H, 0.1, 200);
scene.fog = new THREE.Fog(0xcfe8ff, 26, 60);

// ------------------------------------------------------------------ utils
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const ease = x => x * x * (3 - 2 * x);
const lerp = (a, b, x) => a + (b - a) * x;
const hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return ((s >>> 0) % 100000) / 100000; }; }
const X = lx => (lx - 160) / 35;   // old 2D x coordinate → world x
const col = c => new THREE.Color(c);
const lerpCol = (a, b, k) => col(a).lerp(col(b), k);

const INK = '#281c2c';
const ORANGE = 0xd97757, ORANGE_D = 0xb0543a, ORANGE_L = 0xf09e7c;
const BLUE = 0x3b82f6, BLUE_L = 0x6aa6ff, BLUE_D = 0x1e4fb8, NAVY = 0x14203a;

const geoCache = {}, matCache = {};
function geo(w, h, d) { const k = `${w}|${h}|${d}`; return geoCache[k] || (geoCache[k] = new THREE.BoxGeometry(w, h, d)); }
function mat(c, emissive = 0) {
  const k = `${c}|${emissive}`;
  if (!matCache[k]) matCache[k] = new THREE.MeshLambertMaterial({ color: c, emissive: emissive ? c : 0, emissiveIntensity: emissive });
  return matCache[k];
}
function box(parent, w, h, d, c, x, y, z, m) {
  const mesh = new THREE.Mesh(geo(w, h, d), m || mat(c));
  mesh.position.set(x, y, z);
  mesh.castShadow = true; mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}
function canvasTex(w, h) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const t = new THREE.CanvasTexture(c);
  t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.colorSpace = THREE.SRGBColorSpace;
  return { c, g: c.getContext('2d'), t };
}
function facePlane(parent, w, h, pw, ph, x, y, z, opaque = false) {
  const ct = canvasTex(pw, ph);
  const m = opaque ? new THREE.MeshBasicMaterial({ map: ct.t }) : new THREE.MeshLambertMaterial({ map: ct.t, transparent: true, alphaTest: 0.5 });
  const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), m);
  p.position.set(x, y, z);
  parent.add(p);
  return ct;
}

// ------------------------------------------------------------------ pixel faces
function drawEyes(g, xs, ey, expr, color, w = 2, h = 3, hl = false) {
  const R = (x, y, ww, hh, c = color) => { g.fillStyle = c; g.fillRect(x, y, ww, hh); };
  xs.forEach((x, i) => {
    if (expr === 'blink' || expr === 'sleep') R(x, ey + h - 1, w, 1);
    else if (expr === 'happy' || expr === 'laugh') { R(x - 1, ey + 1, 1, 2); R(x, ey, w, 1); R(x + w, ey + 1, 1, 2); }
    else if (expr === 'dizzy') { for (const [dx, dy] of [[0, 0], [2, 0], [1, 1], [0, 2], [2, 2]]) R(x - (w === 2 ? 1 : 0) + dx, ey + dy, 1, 1); }
    else if (expr === 'smug') { R(x, ey + 1, w + 1, 1); R(x, ey + 2, w, 1); }
    else if (expr === 'surprised') { R(x - 1, ey - 1, w + 2, h + 1, '#ffffff'); R(x, ey, w, h - 1, color === '#ffffff' ? INK : color); }
    else { R(x, ey, w, h); if (hl) R(x, ey, 1, 1, '#ffffff'); }
    if (expr === 'angry' || expr === 'flush') {
      const ox = i === 0 ? x - 1 : x + w, ix = i === 0 ? x + w : x - 1;
      R(ox, ey - 3, 1, 1); R(Math.round((ox + ix) / 2), ey - 2, 1, 1); R(ix, ey - 1, 1, 1);
    }
    if (expr === 'sad') {
      const ox = i === 0 ? x - 1 : x + w, ix = i === 0 ? x + w : x - 1;
      R(ox, ey - 1, 1, 1); R(Math.round((ox + ix) / 2), ey - 2, 1, 1); R(ix, ey - 3, 1, 1);
    }
  });
}

// ------------------------------------------------------------------ characters
function makeClawd() {
  const root = new THREE.Group();
  const bodyG = new THREE.Group(); root.add(bodyG);
  box(bodyG, 1.8, 1.2, 1.1, ORANGE, 0, 1.1, 0);
  box(bodyG, 1.6, 0.06, 0.9, ORANGE_L, 0, 1.72, 0);
  const face = facePlane(bodyG, 1.8, 1.2, 18, 12, 0, 1.1, 0.556);
  const armL = box(bodyG, 0.32, 0.32, 0.36, ORANGE, -1.06, 0.95, 0);
  const armR = box(bodyG, 0.32, 0.32, 0.36, ORANGE, 1.06, 0.95, 0);
  const band = new THREE.Group(); bodyG.add(band);
  box(band, 0.34, 0.11, 0.03, 0xfff6e6, -0.72, 1.56, 0.57).rotation.z = 0.7;
  box(band, 0.34, 0.11, 0.03, 0xfff6e6, -0.72, 1.56, 0.575).rotation.z = -0.7;
  const legs = [-0.72, -0.4, 0.4, 0.72].map((x, k) => box(root, 0.2, 0.5, 0.26, k % 2 ? ORANGE_D : ORANGE, x, 0.25, 0));
  let lastKey = '';
  function set(st) {
    const { expr = 'normal', walk = 0, arms = 'down', sit = false, bandage = false, tear = -1, flush = false } = st;
    legs.forEach((l, k) => {
      const lift = walk && (k % 2 === walk - 1) ? 0.12 : 0;
      l.scale.y = sit ? 0.25 : 1; l.position.y = sit ? 0.06 : 0.25 + lift;
    });
    bodyG.position.y = sit ? -0.38 : (walk ? 0.04 : 0);
    if (arms === 'up') { armL.position.set(-1.06, 1.55, 0); armR.position.set(1.06, 1.55, 0); armL.scale.y = armR.scale.y = 2; }
    else if (arms === 'fwd') { armL.position.set(-1.06, 0.95, 0); armR.position.set(1.0, 1.0, 0.45); armL.scale.y = armR.scale.y = 1; }
    else { armL.position.set(-1.06, 0.95, 0); armR.position.set(1.06, 0.95, 0); armL.scale.y = armR.scale.y = 1; }
    band.visible = bandage;
    const key = `${expr}|${tear}|${flush}`;
    if (key !== lastKey) {
      lastKey = key;
      const g = face.g; g.clearRect(0, 0, 18, 12);
      if (flush || expr === 'flush') { g.fillStyle = '#f04646'; g.fillRect(1, 7, 3, 1); g.fillRect(14, 7, 3, 1); }
      else if (['happy', 'laugh', 'shy', 'sleep', 'normal', 'blink'].includes(expr)) { g.fillStyle = '#ff8caa'; g.fillRect(1, 7, 2, 1); g.fillRect(15, 7, 2, 1); }
      drawEyes(g, [4, 12], 3, expr === 'shy' ? 'normal' : expr, INK);
      if (expr === 'laugh') { g.fillStyle = '#781e28'; g.fillRect(7, 7, 4, 2); }
      if (tear >= 0) { g.fillStyle = '#5aa0ff'; g.fillRect(4, 6 + tear, 1, 2); g.fillRect(13, 6 + ((tear + 1) % 3), 1, 2); }
      face.t.needsUpdate = true;
    }
  }
  return { root, set, head: 2.0 };
}

function makeRobot() {
  // 小蓝：Codex 风格的蓝色小机器人（屏幕脸 + 天线 + 小短腿）
  const root = new THREE.Group();
  const legs = [-0.24, 0.24].map(x => box(root, 0.28, 0.3, 0.32, BLUE_D, x, 0.15, 0));
  const bodyG = new THREE.Group(); root.add(bodyG);
  box(bodyG, 0.95, 0.6, 0.72, BLUE, 0, 0.6, 0);
  const chest = box(bodyG, 0.3, 0.16, 0.03, 0x7ff6ff, 0, 0.62, 0.37, mat(0x7ff6ff, 0.8));
  const mkArm = s => { const p = new THREE.Group(); p.position.set(s * 0.58, 0.82, 0); bodyG.add(p); box(p, 0.2, 0.46, 0.22, BLUE, 0, -0.2, 0); box(p, 0.24, 0.16, 0.26, BLUE_L, 0, -0.44, 0); return p; };
  const armL = mkArm(-1), armR = mkArm(1);
  const head = new THREE.Group(); head.position.y = 0.9; bodyG.add(head);
  box(head, 1.4, 1.0, 1.0, BLUE_L, 0, 0.5, 0);
  box(head, 1.2, 0.82, 0.04, 0x2b5fc9, 0, 0.5, 0.5);
  const face = facePlane(head, 1.12, 0.74, 24, 16, 0, 0.5, 0.525, true);
  box(head, 0.14, 0.4, 0.4, BLUE_D, -0.77, 0.5, 0);
  box(head, 0.14, 0.4, 0.4, BLUE_D, 0.77, 0.5, 0);
  box(head, 0.07, 0.34, 0.07, 0x9aa4b8, 0, 1.17, 0);
  const bulbMat = new THREE.MeshLambertMaterial({ color: 0xffe066, emissive: 0xffe066, emissiveIntensity: 0.9 });
  const bulb = box(head, 0.22, 0.22, 0.22, 0, 0, 1.42, 0, bulbMat);
  const bump = box(head, 0.3, 0.16, 0.3, 0xff7890, -0.38, 1.08, 0.1);
  let lastKey = '';
  function set(st) {
    const { expr = 'normal', walk = 0, arms = 'down', sit = false, talk = false, bumped = false, tear = -1, T = 0, flush = false } = st;
    legs.forEach((l, k) => { l.visible = !sit; l.position.y = 0.15 + (walk === k + 1 ? 0.1 : 0); });
    bodyG.position.y = sit ? -0.3 : (walk ? 0.04 : 0);
    const setArm = (p, s) => {
      if (arms === 'up') { p.rotation.set(0, 0, s * 2.6); }
      else if (arms === 'fwd' && s > 0) { p.rotation.set(-1.4, 0, 0.3); }
      else { p.rotation.set(0, 0, s * 0.15); }
    };
    setArm(armL, -1); setArm(armR, 1);
    bump.visible = bumped;
    bulbMat.emissiveIntensity = 0.5 + 0.5 * Math.abs(Math.sin(T * 3));
    const key = `${expr}|${talk}|${tear}|${flush}`;
    if (key !== lastKey) {
      lastKey = key;
      const g = face.g;
      g.fillStyle = '#101a33'; g.fillRect(0, 0, 24, 16);
      g.fillStyle = '#16244a'; for (let y = 1; y < 16; y += 3) g.fillRect(0, y, 24, 1);
      const cy = '#6ff4ff';
      if (flush || expr === 'flush') { g.fillStyle = '#ff5a6a'; g.fillRect(2, 10, 3, 1); g.fillRect(19, 10, 3, 1); }
      else if (['happy', 'laugh', 'shy', 'normal', 'blink', 'sleep'].includes(expr)) { g.fillStyle = '#ff8cc8'; g.fillRect(2, 10, 2, 1); g.fillRect(20, 10, 2, 1); }
      drawEyes(g, [6, 15], 4, expr === 'shy' ? 'normal' : expr, cy, 3, 4, false);
      g.fillStyle = cy;
      const m = (x, y, w, h) => g.fillRect(x, y, w, h);
      if (expr === 'laugh' || talk) { m(10, 11, 4, 2); }
      else if (['happy', 'shy'].includes(expr)) { m(9, 11, 1, 1); m(10, 12, 4, 1); m(14, 11, 1, 1); }
      else if (expr === 'smug') { m(10, 12, 4, 1); m(14, 11, 1, 1); }
      else if (['angry', 'flush', 'sad'].includes(expr)) { m(10, 12, 4, 1); }
      else if (expr === 'surprised') { m(11, 11, 2, 2); }
      else if (expr === 'dizzy') { m(9, 12, 1, 1); m(10, 11, 1, 1); m(11, 12, 1, 1); m(12, 11, 1, 1); m(13, 12, 1, 1); m(14, 11, 1, 1); }
      else if (expr === 'sleep') { m(11, 12, 2, 1); }
      else { m(10, 12, 1, 1); m(11, 12, 2, 1); g.fillStyle = cy; m(13, 12, 1, 1); } // ">_" feel
      if (tear >= 0) { g.fillStyle = '#9fd0ff'; g.fillRect(7, 8 + tear, 1, 2); g.fillRect(16, 8 + ((tear + 1) % 3), 1, 2); }
      face.t.needsUpdate = true;
    }
  }
  root.scale.setScalar(0.92);
  return { root, set, head: 2.45 * 0.92 };
}

function makeKid() {
  const root = new THREE.Group();
  const skin = 0xffd6b0, hair = 0x6e4628;
  const legL = box(root, 0.22, 0.55, 0.24, skin, -0.17, 0.3, 0), legR = box(root, 0.22, 0.55, 0.24, skin, 0.17, 0.3, 0);
  box(root, 0.26, 0.1, 0.34, 0x503228, -0.17, 0.05, 0.04); box(root, 0.26, 0.1, 0.34, 0x503228, 0.17, 0.05, 0.04);
  box(root, 0.7, 0.3, 0.42, 0x3c5ac8, 0, 0.66, 0);
  box(root, 0.72, 0.62, 0.44, 0xeb5050, 0, 1.08, 0);
  box(root, 0.3, 0.08, 0.03, 0xffffff, 0, 1.36, 0.225);
  const mkArm = s => { const p = new THREE.Group(); p.position.set(s * 0.47, 1.34, 0); root.add(p); box(p, 0.2, 0.55, 0.22, skin, 0, -0.26, 0); return p; };
  const armL = mkArm(-1), armR = mkArm(1);
  const headG = new THREE.Group(); headG.position.y = 1.4; root.add(headG);
  box(headG, 0.95, 0.88, 0.84, skin, 0, 0.46, 0);
  const face = facePlane(headG, 0.95, 0.88, 19, 17, 0, 0.46, 0.425);
  box(headG, 1.02, 0.28, 0.92, hair, 0, 0.92, -0.02);
  box(headG, 1.02, 0.7, 0.2, hair, 0, 0.6, -0.36);
  box(headG, 0.12, 0.4, 0.5, hair, -0.52, 0.66, -0.1); box(headG, 0.12, 0.4, 0.5, hair, 0.52, 0.66, -0.1);
  box(headG, 0.22, 0.44, 0.22, hair, -0.68, 0.5, -0.1); box(headG, 0.22, 0.44, 0.22, hair, 0.68, 0.5, -0.1);
  box(headG, 0.26, 0.1, 0.26, 0xff6490, -0.68, 0.74, -0.1); box(headG, 0.26, 0.1, 0.26, 0xff6490, 0.68, 0.74, -0.1);
  let lastKey = '';
  function set(st) {
    const { expr = 'cry', walk = 0, tear = 0 } = st;
    legL.position.y = 0.3 + (walk === 1 ? 0.1 : 0); legR.position.y = 0.3 + (walk === 2 ? 0.1 : 0);
    if (expr === 'happy') { armL.rotation.z = -2.6; armR.rotation.z = 2.6; }
    else { armL.rotation.z = -0.4; armR.rotation.z = 0.4; armL.rotation.x = armR.rotation.x = -0.5; }
    if (expr === 'happy') armL.rotation.x = armR.rotation.x = 0;
    const key = `${expr}|${tear}`;
    if (key !== lastKey) {
      lastKey = key;
      const g = face.g; g.clearRect(0, 0, 19, 17);
      const R = (x, y, w, h, c) => { g.fillStyle = c; g.fillRect(x, y, w, h); };
      if (expr === 'cry') {
        R(4, 7, 3, 1, INK); R(12, 7, 3, 1, INK); R(4, 6, 1, 1, INK); R(14, 6, 1, 1, INK);
        R(7, 11, 5, 3, '#822832');
        R(5, 8 + tear, 1, 3, '#5aa0ff'); R(13, 8 + ((tear + 1) % 3), 1, 3, '#5aa0ff');
      } else {
        R(4, 7, 1, 1, INK); R(5, 6, 2, 1, INK); R(7, 7, 1, 1, INK);
        R(11, 7, 1, 1, INK); R(12, 6, 2, 1, INK); R(14, 7, 1, 1, INK);
        R(7, 11, 5, 1, '#822832'); R(6, 10, 1, 1, '#822832'); R(12, 10, 1, 1, '#822832');
        R(2, 9, 2, 1, '#ff8caa'); R(15, 9, 2, 1, '#ff8caa');
      }
      face.t.needsUpdate = true;
    }
  }
  return { root, set, head: 2.55 };
}

function makeBug() {
  const root = new THREE.Group();
  const mats = [];
  const m = (c, e = 0) => { const mm = new THREE.MeshLambertMaterial({ color: c, emissive: e ? c : 0, emissiveIntensity: e }); mats.push([mm, c, e]); return mm; };
  const shell = m(0x7a3296), shell2 = m(0x9a55b8), dark = m(0x46194f), spot = m(0xe63c5a), eye = m(0xff3232, 1), white = m(0xffffff);
  const legs = [];
  for (const x of [-0.8, 0.1, 1.0]) for (const z of [-1, 1]) {
    const p = new THREE.Group(); p.position.set(x, 0.75, z * 0.9); root.add(p);
    box(p, 0.18, 0.18, 0.7, 0, 0, 0, z * 0.35, dark);
    box(p, 0.16, 0.7, 0.16, 0, 0, -0.35, z * 0.7, dark);
    legs.push([p, z]);
  }
  box(root, 3.0, 0.8, 2.0, 0, 0.3, 1.2, 0, shell);
  box(root, 2.6, 0.5, 1.7, 0, 0.3, 1.8, 0, shell);
  box(root, 1.9, 0.35, 1.2, 0, 0.3, 2.2, 0, shell2);
  box(root, 0.08, 1.2, 2.05, 0, 0.3, 1.5, 0, dark);
  for (const [x, y, z] of [[0.9, 2.06, 0.5], [-0.3, 2.06, -0.5], [1.2, 1.6, 0.86], [-0.2, 1.3, 1.01], [0.8, 1.1, 1.01]]) box(root, 0.36, 0.1, 0.36, 0, x, y, z, spot).rotation.x = z > 0.9 ? Math.PI / 2 : 0;
  const bugTex = facePlane(root, 1.5, 0.5, 15, 5, 0.35, 1.25, 1.02);
  const L = { B: ['XX.', 'X.X', 'XX.', 'X.X', 'XX.'], U: ['X.X', 'X.X', 'X.X', 'X.X', 'XXX'], G: ['.XX', 'X..', 'X.X', 'X.X', '.XX'] };
  bugTex.g.fillStyle = '#ffdc3c';
  [...'BUG'].forEach((ch, i) => L[ch].forEach((row, y) => [...row].forEach((c, x) => { if (c === 'X') bugTex.g.fillRect(i * 5 + 1 + x, y, 1, 1); })));
  bugTex.t.needsUpdate = true;
  const head = new THREE.Group(); head.position.set(-1.6, 1.15, 0); root.add(head);
  box(head, 1.1, 1.0, 1.2, 0, 0, 0, 0, dark);
  box(head, 0.1, 0.24, 0.24, 0, -0.56, 0.18, 0.28, eye); box(head, 0.1, 0.24, 0.24, 0, -0.56, 0.18, -0.28, eye);
  box(head, 0.3, 0.3, 0.12, 0, -0.35, 0.18, 0.61, eye);
  box(head, 0.4, 0.14, 0.14, 0, -0.7, -0.4, 0.3, white).rotation.z = 0.4; box(head, 0.4, 0.14, 0.14, 0, -0.7, -0.4, -0.3, white).rotation.z = 0.4;
  box(head, 0.08, 0.6, 0.08, 0, -0.2, 0.7, 0.3, dark).rotation.z = 0.5; box(head, 0.08, 0.6, 0.08, 0, -0.2, 0.7, -0.3, dark).rotation.z = 0.5;
  function set(st) {
    const { T = 0, white: wh = false } = st;
    legs.forEach(([p, z], i) => { p.rotation.x = z * 0.15 * Math.sin(T * 16 + i); p.rotation.z = 0.2 * Math.sin(T * 16 + i * 1.7); });
    for (const [mm, c, e] of mats) { mm.emissive.set(wh ? 0xffffff : (e ? c : 0)); mm.emissiveIntensity = wh ? 1 : e; }
    head.rotation.z = 0.08 * Math.sin(T * 5);
  }
  return { root, set, head: 3.0 };
}

function makeLadybug() {
  const g = new THREE.Group();
  box(g, 0.5, 0.26, 0.5, 0xe63c46, 0, 0, 0);
  box(g, 0.2, 0.2, 0.3, 0x28201e, -0.32, 0, 0);
  box(g, 0.06, 0.27, 0.52, 0x28201e, 0, 0.01, 0);
  box(g, 0.1, 0.05, 0.1, 0x28201e, 0.12, 0.14, 0.12); box(g, 0.1, 0.05, 0.1, 0x28201e, -0.1, 0.14, -0.14);
  const w1 = box(g, 0.3, 0.02, 0.18, 0xdcf0ff, 0, 0.2, 0.2), w2 = box(g, 0.3, 0.02, 0.18, 0xdcf0ff, 0, 0.2, -0.2);
  return { root: g, set: T => { const a = Math.sin(T * 40) * 0.6; w1.rotation.x = a; w2.rotation.x = -a; } };
}

const HEART = ['.XX.XX.', 'XXXXXXX', 'XXXXXXX', '.XXXXX.', '..XXX..', '...X...'];
function makeHeart(c = 0xe63c46, s = 0.12) {
  const g = new THREE.Group();
  HEART.forEach((row, y) => [...row].forEach((ch, x) => { if (ch === 'X') box(g, s, s, s * 1.4, 0, (x - 3) * s, (5 - y) * s, 0, mat(c, 0.35)); }));
  box(g, s, s, s * 0.2, 0, -2 * s, 4 * s, s * 0.75, mat(0xffd0dc, 0.6));
  return g;
}

// ------------------------------------------------------------------ world
const world = new THREE.Group(); scene.add(world);
const hemi = new THREE.HemisphereLight(0xdff0ff, 0x6a8f4a, 1.6); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 2.4);
sun.position.set(6, 12, 8); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -12, right: 12, top: 10, bottom: -6, near: 1, far: 40 });
sun.shadow.bias = -0.0008;
scene.add(sun);

// ground: instanced grass blocks
const GR = rng(42);
const groundBlocks = [];
for (let x = -22; x <= 22; x++) for (let z = -12; z <= 8; z++) groundBlocks.push([x, z]);
const groundMesh = new THREE.InstancedMesh(geo(1, 1, 1), new THREE.MeshLambertMaterial({ color: 0xffffff }), groundBlocks.length);
groundMesh.receiveShadow = true;
{
  const m4 = new THREE.Matrix4(); const c = new THREE.Color();
  groundBlocks.forEach(([x, z], i) => {
    const h = (Math.abs(x) > 7 || z < -4) ? Math.floor(hash(x * 13 + z * 7) * 2) * 0.25 : 0;
    m4.makeTranslation(x, -0.5 + h, z); groundMesh.setMatrixAt(i, m4);
    const k = hash(x * 3.1 + z * 5.7);
    c.setRGB(0.36 + k * 0.08, 0.68 + k * 0.1, 0.3 + k * 0.05); groundMesh.setColorAt(i, c);
  });
}
world.add(groundMesh);

// back hills
const hillBlocks = [];
for (let x = -30; x <= 30; x++) for (let z = -26; z <= -14; z++) {
  const h = Math.max(0, Math.round(2 + 2.2 * Math.sin(x * 0.23 + 1) + 1.6 * Math.sin(x * 0.11 + z * 0.3) + (z + 20) * -0.25));
  for (let y = 0; y < h; y++) hillBlocks.push([x, y, z, y === h - 1]);
}
const hillMesh = new THREE.InstancedMesh(geo(1, 1, 1), new THREE.MeshLambertMaterial({ color: 0xffffff }), hillBlocks.length);
{
  const m4 = new THREE.Matrix4(); const c = new THREE.Color();
  hillBlocks.forEach(([x, y, z, top], i) => {
    m4.makeTranslation(x, y + 0.5, z); hillMesh.setMatrixAt(i, m4);
    const k = hash(x * 1.7 + y * 3.3 + z);
    if (top) c.setRGB(0.42 + k * 0.08, 0.72 + k * 0.08, 0.36); else c.setRGB(0.55 + k * 0.05, 0.4 + k * 0.05, 0.28);
    hillMesh.setColorAt(i, c);
  });
}
world.add(hillMesh);

// trees
function tree(x, z, s = 1) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.scale.setScalar(s);
  box(g, 0.5, 1.6, 0.5, 0x8a5a36, 0, 0.8, 0);
  box(g, 2.0, 1.2, 2.0, 0x3f9a4a, 0, 2.1, 0);
  box(g, 1.4, 0.8, 1.4, 0x56b35a, 0, 3.0, 0);
  box(g, 0.4, 0.3, 0.4, 0xe63c46, 0.8, 2.3, 0.9);
  world.add(g);
}
tree(-8.5, -5, 1.1); tree(-11, -2, 0.9); tree(9, -6, 1.2); tree(11.5, -1.5, 0.95); tree(-5.5, -9, 1.0); tree(6, -10, 1.0);

// flowers & tufts
const deco = new THREE.Group(); world.add(deco);
const fr = rng(7);
for (let i = 0; i < 90; i++) {
  const x = fr() * 30 - 15, z = fr() * 14 - 9;
  if (Math.abs(x) < 6 && z > -2.5 && z < 2.5) continue;
  const f = fr();
  if (f < 0.5) { box(deco, 0.06, 0.25, 0.06, 0x3e8e3e, x, 0.12, z); box(deco, 0.18, 0.12, 0.18, [0xffffff, 0xffdc3c, 0xff8caa, 0x9fc6ff][i % 4], x, 0.28, z); }
  else box(deco, 0.25, 0.14, 0.12, 0x3f8f45, x, 0.07, z);
}

// clouds
const clouds = [];
const cr = rng(3);
for (let i = 0; i < 8; i++) {
  const g = new THREE.Group();
  const n = 3 + Math.floor(cr() * 3);
  for (let k = 0; k < n; k++) box(g, 1.4 + cr() * 1.4, 0.8 + cr() * 0.6, 1.2 + cr(), 0xffffff, k * 1.1 - n * 0.5, cr() * 0.4, cr() * 0.6);
  g.traverse(o => { if (o.isMesh) { o.castShadow = false; o.material = mat(0xffffff, 0.25); } });
  g.position.set(cr() * 50 - 25, 7 + cr() * 3, -12 - cr() * 8);
  clouds.push([g, g.position.x]); scene.add(g);
}

// sunset mound (only for the last two scenes)
const mound = new THREE.Group(); scene.add(mound);
{
  const layers = [[9, 6, 0.4], [6.5, 4.4, 0.4], [4.2, 3.0, 0.4]];
  let y = 0;
  layers.forEach(([w, d, h], i) => { box(mound, w, h, d, i === 2 ? 0x7cc46a : 0x68b058, 0, y + h / 2, 0); y += h; });
}
const MOUND_TOP = 1.2;

// sky, sun disc, moon, stars
const skyTex = canvasTex(2, 256); skyTex.t.magFilter = THREE.LinearFilter; skyTex.t.minFilter = THREE.LinearFilter;
scene.background = skyTex.t;
let skyKey = '';
function setSky(stops) {
  const key = JSON.stringify(stops); if (key === skyKey) return; skyKey = key;
  const gr = skyTex.g.createLinearGradient(0, 0, 0, 256);
  stops.forEach(([p, c]) => gr.addColorStop(p, c));
  skyTex.g.fillStyle = gr; skyTex.g.fillRect(0, 0, 2, 256); skyTex.t.needsUpdate = true;
}
const sunTex = canvasTex(64, 64);
{
  const g = sunTex.g; g.fillStyle = '#ffeca0'; g.beginPath(); g.arc(32, 32, 31, 0, Math.PI * 2); g.fill();
  g.globalCompositeOperation = 'destination-out'; for (let y = 38; y < 64; y += 7) g.fillRect(0, y, 64, 2 + (y - 38) / 8); sunTex.t.needsUpdate = true;
}
const sunDisc = new THREE.Mesh(new THREE.PlaneGeometry(12, 12), new THREE.MeshBasicMaterial({ map: sunTex.t, transparent: true, fog: false }));
scene.add(sunDisc);
const moonTex = canvasTex(32, 32);
{
  const g = moonTex.g; g.fillStyle = '#fff4c8'; g.beginPath(); g.arc(16, 16, 14, 0, 7); g.fill();
  g.globalCompositeOperation = 'destination-out'; g.beginPath(); g.arc(22, 12, 12, 0, 7); g.fill(); moonTex.t.needsUpdate = true;
}
const moon = new THREE.Mesh(new THREE.PlaneGeometry(5, 5), new THREE.MeshBasicMaterial({ map: moonTex.t, transparent: true, fog: false }));
scene.add(moon);
const starGeo = new THREE.BufferGeometry();
{
  const sr = rng(11); const p = [];
  for (let i = 0; i < 500; i++) { const a = sr() * Math.PI * 1.4 - Math.PI * 0.7, e = 0.08 + sr() * 0.9; p.push(Math.sin(a) * 80 * Math.cos(e), 80 * Math.sin(e), -Math.cos(a) * 80 * Math.cos(e)); }
  starGeo.setAttribute('position', new THREE.Float32BufferAttribute(p, 3));
}
const starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 2.2, sizeAttenuation: false, transparent: true, fog: false });
const stars = new THREE.Points(starGeo, starMat); scene.add(stars);

// ------------------------------------------------------------------ actors & props
const clawd = makeClawd(), robot = makeRobot(), kid = makeKid(), bug = makeBug(), lady = makeLadybug();
for (const a of [clawd, robot, kid, bug, lady]) scene.add(a.root);
const bigHeart = makeHeart(); scene.add(bigHeart);
const smallHearts = [0, 1, 2, 3].map(() => { const h = makeHeart(0xff8caa, 0.07); scene.add(h); return h; });
const ladyHeart = makeHeart(0xe63c46, 0.06); scene.add(ladyHeart);
const endHeart = makeHeart(0xe63c46, 0.07); scene.add(endHeart);

const puffGeo = new THREE.IcosahedronGeometry(1, 0);
const puffMat = new THREE.MeshLambertMaterial({ color: 0xf2f2f8, flatShading: true });
const puffs = Array.from({ length: 14 }, () => { const m = new THREE.Mesh(puffGeo, puffMat); m.castShadow = true; scene.add(m); return m; });
const starMatY = mat(0xffdc3c, 0.8);
const starCubes = Array.from({ length: 12 }, () => { const m = new THREE.Mesh(geo(0.18, 0.18, 0.18), starMatY); scene.add(m); return m; });
const limbs = Array.from({ length: 5 }, (_, i) => { const m = new THREE.Mesh(geo(0.45, 0.3, 0.3), mat(i % 2 ? BLUE : ORANGE)); m.castShadow = true; scene.add(m); return m; });
const beam = Array.from({ length: 16 }, (_, i) => { const m = new THREE.Mesh(geo(0.14, 0.14, 0.14), mat(i % 2 ? 0x7ff6ff : 0xffffff, 1)); scene.add(m); return m; });
const steamCubes = Array.from({ length: 6 }, () => { const m = new THREE.Mesh(geo(0.3, 0.3, 0.3), mat(0xffffff, 0.3)); scene.add(m); return m; });
const flies = Array.from({ length: 14 }, () => { const m = new THREE.Mesh(geo(0.07, 0.07, 0.07), mat(0xfffaa0, 1)); scene.add(m); return m; });

// painting (the six-legged cat) and code panel
function board(w, h, pw, ph, frameCol) {
  const g = new THREE.Group();
  box(g, w + 0.2, h + 0.2, 0.12, frameCol, 0, 0, 0);
  const ct = facePlane(g, w, h, pw, ph, 0, 0, 0.065, true);
  scene.add(g); return { g, ct };
}
const painting = board(2.2, 1.7, 44, 34, 0x8a5a36);
{
  const g = painting.ct.g, R = (x, y, w, h, c) => { g.fillStyle = c; g.fillRect(x, y, w, h); };
  R(0, 0, 44, 34, '#fcf6e8');
  const c = '#f0a050';
  g.fillStyle = c; g.beginPath(); g.ellipse(18, 21, 11, 6, 0, 0, 7); g.fill();
  g.beginPath(); g.ellipse(31, 13, 6, 6, 0, 0, 7); g.fill();
  R(26, 5, 3, 4, c); R(34, 4, 3, 5, c);
  R(29, 12, 1, 1, INK); R(32, 11, 2, 2, INK); R(30, 16, 3, 1, INK);
  for (let i = 0; i < 6; i++) R(9 + i * 3 + (i % 2), 26, 1, 3 + (i % 3), c);
  g.strokeStyle = c; g.lineWidth = 1; g.beginPath(); g.moveTo(8, 20); g.lineTo(4, 15); g.lineTo(6, 11); g.lineTo(3, 8); g.stroke();
  R(17, 19, 3, 2, '#ff7878');
  painting.ct.t.needsUpdate = true;
}
const panel = board(3.0, 2.06, 64, 44, 0x3c4054);
const codeLines = (() => { const r = rng(3); const cols = ['#78c8ff', '#ffaa5a', '#be96ff', '#c8c8c8', '#8ce68c']; return Array.from({ length: 80 }, () => [Math.floor(r() * 4), Array.from({ length: 1 + Math.floor(r() * 3) }, () => [4 + Math.floor(r() * 10), cols[Math.floor(r() * 5)]])]); })();
function drawPanel(lt, error) {
  const g = panel.ct.g, R = (x, y, w, h, c) => { g.fillStyle = c; g.fillRect(x, y, w, h); };
  R(0, 0, 64, 44, '#1e2230'); R(0, 0, 64, 5, '#3c4054');
  ['#e63c46', '#ffdc3c', '#5adc6e'].forEach((c, i) => R(3 + i * 4, 1, 2, 2, c));
  const n = Math.floor(lt * 7), first = Math.max(0, n - 12);
  for (let idx = first, row = 0; idx < n; idx++, row++) {
    const [ind, parts] = codeLines[idx % 80]; let xx = 3 + ind * 3; const yy = 7 + row * 3;
    for (const [ln, c] of parts) { if (xx + ln > 62) break; R(xx, yy, ln, 1, c); xx += ln + 2; }
  }
  if (error && Math.floor(lt * 5) % 2 === 0) R(1, 7 + 6 * 3 - 1, 62, 3, '#c82832');
  panel.ct.t.needsUpdate = true;
}

// ------------------------------------------------------------------ story data
let STORY = null, LINES = [], SC = {};
function speaking(who, T) {
  for (const [a, b, w, txt] of LINES) if (w === who && T >= a && T < Math.min(b, a + [...txt].length / STORY.cps + 0.2)) return true;
  return false;
}
const bounce = (who, T) => (speaking(who, T) && Math.floor(T * 8) % 2) ? 0.08 : 0;
const talking = (who, T) => speaking(who, T) && Math.floor(T * 8) % 2 === 0;
const blink = (e, T, off = 0) => (e === 'normal' && (T + off) % 3.4 < 0.12) ? 'blink' : e;
const FACE_R = 0.55;  // body yaw when facing right (toward +x)

// ------------------------------------------------------------------ overlay (2D) helpers
function proj(x, y, z) { const v = new THREE.Vector3(x, y, z).project(camera); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H]; }
function headPos(a, extra = 0) { const v = new THREE.Vector3(0, a.head + extra, 0); a.root.localToWorld(v); return proj(v.x, v.y, v.z); }
function text(s, x, y, size, fill, stroke = 4, align = 'center') {
  ctx.font = `${size}px Pix`; ctx.textAlign = align; ctx.textBaseline = 'middle';
  if (stroke) { ctx.lineWidth = stroke * 2; ctx.strokeStyle = INK; ctx.lineJoin = 'round'; ctx.strokeText(s, x, y); }
  ctx.fillStyle = fill; ctx.fillText(s, x, y);
}
function pix(pattern, x, y, s, color) {
  pattern.forEach((row, j) => [...row].forEach((c, i) => {
    if (c === 'X') { ctx.fillStyle = color; ctx.fillRect(x + i * s, y + j * s, s, s); }
    if (c === 'o') { ctx.fillStyle = INK; ctx.fillRect(x + i * s, y + j * s, s, s); }
  }));
}
const BANG = ['ooo', 'oXo', 'oXo', 'oXo', 'oXo', 'ooo', 'oXo', 'ooo'];
const ANGER = ['.XX.XX.', 'X.X.X.X', 'XX...XX', '.......', 'XX...XX', 'X.X.X.X', '.XX.XX.'];
const SWEAT = ['.X.', 'XXX', 'XXX', '.X.'];
function emoteBang(a) { const [x, y] = headPos(a, 0.35); pix(BANG, x - 9, y - 60, 6, '#ffdc3c'); }
function emoteAnger(a, T, dx = 30) { const [x, y] = headPos(a, 0.1); const s = Math.floor(T * 6) % 2 ? 6 : 5; pix(ANGER, x + dx, y - 40, s, '#f03246'); }
function emoteSweat(a, dx = -50) { const [x, y] = headPos(a, -0.2); pix(SWEAT, x + dx, y, 6, '#8cc8ff'); }
function sparkle(x, y, T, c = '#fff') {
  const k = Math.floor(T * 8) % 3; ctx.fillStyle = c;
  if (k === 0) ctx.fillRect(x - 3, y - 3, 6, 6); else { ctx.fillRect(x - k * 6 - 3, y - 3, k * 12 + 6, 6); ctx.fillRect(x - 3, y - k * 6 - 3, 6, k * 12 + 6); }
}
function lightning(p1, p2, T) {
  const r = rng(Math.floor(T * 16) + 1); const pts = [p1];
  for (let i = 1; i < 9; i++) pts.push([lerp(p1[0], p2[0], i / 9), lerp(p1[1], p2[1], i / 9) + (r() - 0.5) * 36]);
  pts.push(p2);
  for (const [w, c] of [[14, INK], [8, '#ffdc3c'], [3, '#fff']]) {
    ctx.lineWidth = w; ctx.strokeStyle = c; ctx.lineJoin = 'miter'; ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.stroke();
  }
}

// speech bubble above the speaker
const SPEAKER_ACTOR = { C: () => clawd, G: () => robot, K: () => kid };
const NO_START = '，。！？、：；…—～）」』!?,.';
function wrapText(s, maxW = 420) {
  ctx.font = '32px Pix';
  const out = []; let cur = '';
  for (const ch of s) {
    if (cur && ctx.measureText(cur + ch).width > maxW && !NO_START.includes(ch)) { out.push(cur); cur = ''; }
    cur += ch;
  }
  if (cur) out.push(cur);
  return out;
}
function wrapShown(full, n) { const out = []; let left = n; for (const l of full) { const c = [...l]; if (left <= 0) break; out.push(c.slice(0, left).join('')); left -= c.length; } return out; }
function drawBubble(T) {
  let line = null;
  for (const l of LINES) if (T >= l[0] && T < l[1]) { line = l; break; }
  if (!line) return;
  const [a, , who, txt] = line;
  const sp = STORY.speakers[who];
  const chars = [...txt];
  const n = Math.floor((T - a) * STORY.cps);
  const full = wrapText(txt);
  const shown = wrapShown(full, n);
  ctx.font = '32px Pix';
  const tw = Math.max(...full.map(s => ctx.measureText(s).width));
  const bw = Math.round(tw + 48), bh = full.length * 42 + 30;
  const [hx, hy] = headPos(SPEAKER_ACTOR[who](), 0.2);
  const pop = ease(seg(T, a, a + 0.15));
  let bx = Math.round(hx - bw / 2), by = Math.round(hy - 30 - bh);
  bx = Math.max(16, Math.min(W - 16 - bw, bx)); by = Math.max(52, by);
  const tailX = Math.max(bx + 30, Math.min(bx + bw - 30, hx));
  ctx.save();
  ctx.translate(tailX, by + bh); ctx.scale(0.6 + 0.4 * pop, 0.6 + 0.4 * pop); ctx.translate(-tailX, -(by + bh));
  // shadow
  ctx.fillStyle = 'rgba(0,0,0,0.25)'; ctx.fillRect(bx + 8, by + 8, bw, bh);
  // body with chunky pixel corners
  ctx.fillStyle = INK; ctx.fillRect(bx + 6, by, bw - 12, bh); ctx.fillRect(bx, by + 6, bw, bh - 12);
  ctx.fillStyle = '#fffaf0'; ctx.fillRect(bx + 6, by + 6, bw - 12, bh - 12);
  ctx.fillStyle = '#efe4cc'; ctx.fillRect(bx + 6, by + bh - 12, bw - 12, 6);
  // tail
  ctx.fillStyle = INK; ctx.beginPath(); ctx.moveTo(tailX - 16, by + bh - 6); ctx.lineTo(tailX + 16, by + bh - 6); ctx.lineTo(tailX, by + bh + 24); ctx.fill();
  ctx.fillStyle = '#fffaf0'; ctx.beginPath(); ctx.moveTo(tailX - 9, by + bh - 7); ctx.lineTo(tailX + 9, by + bh - 7); ctx.lineTo(tailX, by + bh + 12); ctx.fill();
  // name tag
  ctx.font = 'bold 22px "WenQuanYi Zen Hei"';
  const nw = ctx.measureText(sp.name).width + 20;
  ctx.fillStyle = INK; ctx.fillRect(bx + 12, by - 30, nw + 6, 36);
  ctx.fillStyle = sp.color; ctx.fillRect(bx + 15, by - 27, nw, 30);
  ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(sp.name, bx + 25, by - 11);
  // text
  ctx.font = '32px Pix'; ctx.fillStyle = INK;
  shown.forEach((s, i) => ctx.fillText(s, bx + 24, by + 34 + i * 42));
  if (n >= chars.length && Math.floor(T * 3) % 2 === 0) {
    ctx.fillStyle = sp.color; ctx.beginPath(); ctx.moveTo(bx + bw - 30, by + bh - 26); ctx.lineTo(bx + bw - 14, by + bh - 26); ctx.lineTo(bx + bw - 22, by + bh - 16); ctx.fill();
  }
  ctx.restore();
}

// ------------------------------------------------------------------ lighting presets
const LIGHT = {
  day: { sky: [[0, '#5aa8f5'], [0.55, '#9fd2fb'], [1, '#e2f3ff']], fog: 0xd4ecff, hemi: [0xdff0ff, 0x6a8f4a, 1.35], sun: [0xfff4e0, 2.8], sunPos: [6, 12, 8] },
  dark: { sky: [[0, '#1d1238'], [0.6, '#4b2d6e'], [1, '#7a4a8a']], fog: 0x4b2d6e, hemi: [0x9a80d0, 0x302040, 0.8], sun: [0xb090ff, 1.1], sunPos: [6, 12, 8] },
  sunset: { sky: [[0, '#3a2868'], [0.35, '#9a4a8c'], [0.62, '#f08a6e'], [0.8, '#ffc27a'], [1, '#ffe2a0']], fog: 0xf0a080, hemi: [0xffc8b0, 0x604060, 1.4], sun: [0xffb070, 2.4], sunPos: [6, 6, 9] },
  night: { sky: [[0, '#0b0c26'], [0.6, '#1c1c4a'], [1, '#2e2a62']], fog: 0x1c1c4a, hemi: [0x8fa0f0, 0x303060, 1.5], sun: [0xc0ccff, 1.9], sunPos: [4, 10, 9] },
};
function applyLight(a, b = null, k = 0) {
  const A = LIGHT[a], B = b ? LIGHT[b] : A;
  const mixHex = (x, y) => lerpCol(x, y, k);
  setSky(k < 0.5 || !b ? A.sky : B.sky);
  if (b && k > 0 && k < 1) {
    // blend sky gradient stops by drawing both
    const key = `${a}>${b}:${k.toFixed(2)}`; if (key !== skyKey) {
      skyKey = key; const g = skyTex.g;
      for (const [L, al] of [[A, 1], [B, k]]) { const gr = g.createLinearGradient(0, 0, 0, 256); L.sky.forEach(([p, c]) => gr.addColorStop(p, c)); g.globalAlpha = al; g.fillStyle = gr; g.fillRect(0, 0, 2, 256); }
      g.globalAlpha = 1; skyTex.t.needsUpdate = true;
    }
  }
  scene.fog.color.copy(mixHex(A.fog, B.fog));
  hemi.color.copy(mixHex(A.hemi[0], B.hemi[0])); hemi.groundColor.copy(mixHex(A.hemi[1], B.hemi[1]));
  hemi.intensity = lerp(A.hemi[2], B.hemi[2], k);
  sun.color.copy(mixHex(A.sun[0], B.sun[0])); sun.intensity = lerp(A.sun[1], B.sun[1], k);
  sun.position.set(...A.sunPos.map((v, i) => lerp(v, B.sunPos[i], k)));
}

function setCam(px, py, pz, lx, ly, lz, shake = [0, 0]) {
  camera.position.set(px + shake[0], py + shake[1], pz); camera.lookAt(lx + shake[0] * 0.5, ly + shake[1] * 0.5, lz);
}
function place(a, x, y, z, yaw = 0) { a.root.visible = true; a.root.position.set(x, y, z); a.root.rotation.set(0, yaw, 0); }

// ------------------------------------------------------------------ scenes
const FX = { flash: 0, caption: null, mosaic: null, overlays: [] };
const later = f => FX.overlays.push(f);

function scTitle(lt, T) {
  applyLight('night');
  stars.visible = true; starMat.opacity = 1; moon.visible = true; moon.position.set(14, 16, -40); moon.lookAt(0, 2, 10);
  mound.visible = false; sunDisc.visible = false; clouds.forEach(([g]) => g.visible = false);
  const b1 = Math.abs(Math.sin(lt * 5)) * 0.25, b2 = Math.abs(Math.sin(lt * 5 + 1.2)) * 0.25;
  place(clawd, -2.4, b1, 0.5, 0.7); clawd.set({ expr: blink('angry', lt), arms: Math.floor(lt * 3) % 2 ? 'up' : 'down' });
  place(robot, 2.4, b2, 0.5, -0.7); robot.set({ expr: 'angry', arms: Math.floor(lt * 3 + 1) % 2 ? 'up' : 'down', T });
  const z = lerp(8.4, 7.2, ease(seg(lt, 0, 6)));
  setCam(Math.sin(lt * 0.4) * 0.6, 2.4, z, 0, 2.3, 0);
  later(() => {
    if (lt > 1.2) lightning(headPos(clawd, -0.6), headPos(robot, -0.9), T);
    let yy = lerp(-120, 150, ease(seg(lt, 0.2, 0.9)));
    if (lt > 0.9) yy += Math.sin(lt * 18) * 12 * (1 - seg(lt, 0.9, 1.4));
    text('谁才是最强AI？', W / 2, yy, 96, '#ffec78', 6);
    if (lt > 1.2) {
      text('小橙（Claude）', 330, 262, 48, '#f09e7c', 4);
      text('VS', W / 2, 262, 64, Math.floor(lt * 6) % 2 ? '#e63c46' : '#ffdc3c', 5);
      text('小蓝（ChatGPT）', 950, 262, 48, '#8cbcff', 4);
    }
    if (lt > 2.2) text('～ 一个关于体素宠物的小故事 ～', W / 2, 330, 32, '#dcdcff', 3);
  });
}

function dayWorld(T, k = 0) {
  stars.visible = k > 0.3; starMat.opacity = clamp((k - 0.3) * 2);
  moon.visible = false; mound.visible = false; sunDisc.visible = false;
  clouds.forEach(([g, x0]) => { g.visible = true; g.position.x = ((x0 + T * 0.35 + 30) % 60) - 30; });
}

function scMeet(lt, T) {
  applyLight('day'); dayWorld(T);
  const s = seg(lt, 0, 3), s2 = seg(lt, 0.3, 3.3);
  const cx = lerp(X(-20), X(100), s), gx = lerp(X(340), X(220), s2);
  const walkc = s < 1 ? Math.floor(lt * 8) % 2 + 1 : 0, walkg = s2 < 1 ? Math.floor(lt * 8) % 2 + 1 : 0;
  let ce = 'normal'; if (lt >= 3 && lt < 6.5) ce = 'happy'; else if (lt >= 9.5) ce = 'angry';
  if (lt >= 13 && lt < 16.5) ce = lt > 15 ? 'flush' : 'angry';
  let ge = 'normal'; if (lt >= 6.5 && lt < 7.2) ge = 'surprised'; else if (lt >= 7.2) ge = 'smug'; if (lt >= 18.3) ge = 'angry';
  const jump = Math.sin(Math.PI * seg(lt, 9.5, 9.9)) * 0.6;
  const carms = (lt >= 9.5 && lt < 11) || (lt >= 16.5 && lt < 18) ? 'up' : 'down';
  const garms = lt >= 13 && lt < 15 ? 'up' : 'down';
  place(clawd, cx, bounce('C', T) + jump, 0, lt < 3 ? Math.PI / 2 * 0.8 : FACE_R);
  clawd.set({ expr: blink(ce, T), walk: walkc, arms: carms });
  place(robot, gx, bounce('G', T), 0, lt < 3.3 ? -Math.PI / 2 * 0.8 : -FACE_R);
  robot.set({ expr: blink(ge, T, 1.3), walk: walkg, arms: garms, talk: talking('G', T), T });
  const camX = lerp(-2, 0, ease(seg(lt, 0, 4)));
  setCam(camX + Math.sin(lt * 0.3) * 0.3, 3.2, lerp(12, 10, ease(seg(lt, 0, 20))), camX * 0.5, 1.4, 0);
  later(() => {
    if (lt >= 6.5 && lt < 7.6) emoteBang(robot);
    if ((lt >= 9.5 && lt < 16.5) || lt >= 17) emoteAnger(clawd, lt);
    if (lt >= 18.3) emoteAnger(robot, lt, -80);
    if (lt >= 13 && lt < 16) emoteSweat(clawd);
  });
}

function scContest(lt, T) {
  applyLight('day'); dayWorld(T);
  const cx = lerp(X(100), X(110), seg(lt, 0, 0.5)), gx = lerp(X(220), X(210), seg(lt, 0, 0.5));
  let ce = 'angry', ge = 'angry', carms = 'down', garms = 'down';
  if (lt >= 3 && lt < 7) { ge = 'smug'; garms = 'up'; ce = 'normal'; }
  if (lt >= 7 && lt < 10.5) { ce = 'smug'; ge = 'happy'; }
  if (lt >= 10.5 && lt < 13.5) { ge = 'flush'; ce = lt % 1.2 < 0.15 ? 'blink' : 'smug'; }
  if (lt >= 13.5 && lt < 16.5) { ce = 'happy'; carms = 'up'; ge = 'normal'; }
  if (lt >= 16.5 && lt < 19.5) { ce = 'surprised'; ge = 'smug'; garms = 'fwd'; }
  if (lt >= 19.5) { ce = 'flush'; carms = 'up'; ge = 'surprised'; }
  const sh = lt >= 19.5 ? (hash(Math.floor(T * 30)) - 0.5) * 0.12 : 0;
  place(clawd, cx + sh, bounce('C', T), 0, FACE_R); clawd.set({ expr: blink(ce, T), arms: carms });
  place(robot, gx, bounce('G', T), 0, -FACE_R); robot.set({ expr: blink(ge, T, 0.8), arms: garms, talk: talking('G', T), T });
  // painting pops next to the robot
  painting.g.visible = lt >= 4.3 && lt < 13.5;
  if (painting.g.visible) { const p = ease(seg(lt, 4.3, 4.7)); painting.g.position.set(gx + 2.3, lerp(0.5, 2.3, p), -0.3); painting.g.scale.setScalar(Math.max(0.01, p)); painting.g.rotation.set(0, -0.35 + Math.sin(lt * 2) * 0.05, 0); }
  panel.g.visible = lt >= 13.8;
  if (panel.g.visible) { const p = ease(seg(lt, 13.8, 14.2)); panel.g.position.set(cx - 2.5, lerp(0.5, 2.3, p), -0.3); panel.g.scale.setScalar(Math.max(0.01, p)); panel.g.rotation.set(0, 0.35, 0); drawPanel(lt - 13.8, lt >= 16.8); }
  // steam
  steamCubes.forEach((m, i) => {
    m.visible = lt >= 19.5; if (!m.visible) return;
    const k = (lt * 1.2 + i / 6) % 1; m.position.set(cx + (i % 3 - 1) * 0.35, 2.0 + k * 1.6, 0); m.scale.setScalar(0.5 + k * 1.2); m.rotation.set(k * 3, k * 2, 0);
  });
  const focus = lt < 3 ? 0 : (speaking('C', T) ? cx : speaking('G', T) ? gx : 0) * 0.25;
  setCam(focus + Math.sin(lt * 0.35) * 0.3, 2.9, 9.4, focus * 0.6, 1.5, 0);
  if (lt >= 21.6) FX.flash = seg(lt, 21.6, 22) * 0.9;
  later(() => {
    if (lt < 3) lightning(headPos(clawd, -0.7), headPos(robot, -1.0), T);
    if (lt >= 7 && lt < 10.5) emoteSweat(clawd);
    if (lt >= 10.5 && lt < 13.5) emoteAnger(robot, lt, -80);
    if (lt >= 16.8 && lt < 19.5 && Math.floor(lt * 5) % 2 === 0) { const [x, y] = proj(cx - 2.5, 3.6, -0.3); text('ERROR!', x, y, 32, '#ff5a5a', 3); }
    if (lt >= 19.5) { emoteAnger(clawd, lt); emoteAnger(robot, lt + 0.3, -80); }
  });
}

const WORDS = ['砰！', '啪！', '嘿哈！', '咚！', '嗷呜！', '啊打！', '吃我一钳！', '哔哔！'];
function scFight(lt, T) {
  applyLight('day'); dayWorld(T);
  let shake = [0, 0];
  if (lt < 1) {
    const s = ease(seg(lt, 0, 0.9)); const hop = Math.sin(Math.PI * s) * 1.6;
    place(clawd, lerp(X(110), -0.4, s), hop, 0, FACE_R); clawd.set({ expr: 'angry', arms: 'up' });
    place(robot, lerp(X(210), 0.4, s), hop, 0, -FACE_R); robot.set({ expr: 'angry', arms: 'up', T });
    setCam(0, 2.8, 9.4, 0, 1.5, 0);
    return;
  }
  if (lt < 9.2) {
    const r = rng(Math.floor(lt * 7) + 5);
    puffs.forEach((p, i) => {
      p.visible = true; const a = i * Math.PI * 2 / 14 + lt * 2.2, rr = 1.0 + 0.25 * Math.sin(lt * 9 + i);
      p.position.set(Math.cos(a) * rr * 1.3, 1.3 + Math.sin(a) * rr * 0.6, Math.sin(a * 2) * 0.5);
      p.scale.setScalar(0.85 + 0.2 * Math.sin(lt * 11 + i * 2)); p.rotation.set(lt * 2 + i, lt * 3, 0);
    });
    limbs.forEach((m, i) => {
      m.visible = true; const a = r() * Math.PI * 2;
      m.position.set(Math.cos(a) * 2.2, 1.3 + Math.sin(a) * 1.1, 0.4); m.rotation.set(0, 0, a);
    });
    starCubes.forEach((m, i) => { m.visible = i < 8; const a = r() * Math.PI * 2; m.position.set(Math.cos(a) * 2.9, 1.3 + Math.sin(a) * 1.6, 0.2); m.rotation.set(lt * 5, lt * 4, 0); });
    shake = [(hash(Math.floor(T * 30)) - 0.5) * 0.35, (hash(Math.floor(T * 30) + 7) - 0.5) * 0.25];
    const z = lerp(9.4, 7.4, ease(seg(lt, 1, 3)));
    setCam(0, 2.6, z, 0, 1.4, 0, shake);
    if (lt >= 4.5 && lt < 6.8) { FX.mosaic = [proj(-3, 3.2, 0), proj(3, -0.2, 0)]; FX.caption = '（画面过于激烈，已自动打码）'; }
    else later(() => {
      const rw = rng(Math.floor(lt / 0.35) + 9);
      for (let k = 0; k < 2; k++) text(WORDS[Math.floor(rw() * WORDS.length)], 640 + (rw() - 0.5) * 700, 360 + (rw() - 0.6) * 400, 64, ['#ffdc3c', '#ff7850', '#ffffff', '#78dcff'][Math.floor(rw() * 4)], 5);
    });
    if (lt >= 9.0) FX.flash = 1 - seg(lt, 9.0, 9.2);
    return;
  }
  const s = seg(lt, 9.2, 10.1), landed = s >= 1, arc = Math.sin(Math.PI * s) * 2.2;
  const cx = lerp(0, X(85), s), gx = lerp(0, X(235), s);
  place(clawd, cx, arc + (landed ? bounce('C', T) : 0), 0, landed ? 0.35 : s * 12);
  clawd.set({ expr: 'dizzy', sit: landed, bandage: true, arms: landed ? 'down' : 'up' });
  place(robot, gx, arc + (landed ? bounce('G', T) : 0), 0, landed ? -0.35 : -s * 12);
  robot.set({ expr: 'dizzy', sit: landed, bumped: true, arms: landed ? 'down' : 'up', talk: talking('G', T), T });
  if (landed) {
    starCubes.forEach((m, i) => {
      m.visible = i < 6; const who = i < 3 ? [cx, 1.9] : [gx, 2.5]; const a = lt * 5 + (i % 3) * 2.094;
      m.position.set(who[0] + Math.cos(a) * 0.7, who[1] + 0.2, Math.sin(a) * 0.7); m.rotation.set(lt * 4, lt * 3, 0);
    });
  }
  if (lt < 10.3) puffs.forEach((p, i) => {
    const k = seg(lt, 9.2, 10.3); p.visible = true; const a = i * Math.PI * 2 / 14;
    p.position.set(Math.cos(a) * (1 + k * 4), 1.3 + Math.sin(a) * (0.6 + k * 2), 0); p.scale.setScalar(0.9 * (1 - k) + 0.05);
  });
  FX.flash = Math.max(FX.flash, 0.6 * (1 - seg(lt, 9.2, 9.6)));
  setCam(0, 3.0, lerp(7.4, 9.6, ease(seg(lt, 9.2, 10.5))), 0, 1.2, 0);
}

function scBug(lt, T) {
  let k = seg(lt, 0, 2); if (lt > 17.5) k *= 1 - seg(lt, 17.5, 19.5);
  applyLight('day', 'dark', k); dayWorld(T, k);
  const kx = lerp(X(-20), X(50), seg(lt, 0.8, 3));
  const kwalk = lt > 0.8 && lt < 3 ? Math.floor(lt * 10) % 2 + 1 : 0;
  const kexpr = lt < 18.8 ? 'cry' : 'happy';
  const kj = lt >= 18.8 ? Math.abs(Math.sin((lt - 18.8) * 7)) * 0.5 : 0;
  const ksh = kexpr === 'cry' && lt > 3 ? (hash(Math.floor(T * 20)) - 0.5) * 0.08 : 0;
  place(kid, kx + ksh, kj + bounce('K', T), 0.3, lt < 3 ? 1.1 : 0.4); kid.set({ expr: kexpr, walk: kwalk, tear: Math.floor(T * 6) % 3 });
  const st = seg(lt, 5.3, 6.3), standing = lt >= 5.3;
  const cx = lerp(X(85), X(112), ease(st)), gx = lerp(X(235), X(170), ease(st));
  const hop = Math.sin(Math.PI * st) * 0.8;
  let ce = lt < 2.5 ? 'normal' : 'surprised', ge = lt < 2.5 ? 'normal' : 'surprised', carms = 'down', garms = 'down';
  let gyaw = -0.6;
  if (lt >= 6.3) { ce = 'angry'; ge = 'angry'; gyaw = 0.6; }
  if (lt >= 9.5 && lt < 12.5) ge = 'happy';
  if (lt >= 12.5 && lt < 15.5) { ge = 'angry'; garms = 'fwd'; }
  if (lt >= 15.5 && lt < 18.5) { ce = 'angry'; carms = 'fwd'; }
  if (lt >= 18.5) { ce = 'happy'; ge = 'happy'; carms = garms = 'up'; }
  if (lt >= 19.2) gyaw = -0.5;
  const cb = lt >= 18.5 ? Math.abs(Math.sin(lt * 6)) * 0.3 : 0;
  place(clawd, cx, hop + bounce('C', T) + cb, 0, lt < 6.3 ? -0.3 : FACE_R); clawd.set({ expr: blink(ce, T), arms: carms, sit: !standing, bandage: true });
  place(robot, gx, hop + bounce('G', T) + cb, 0, gyaw); robot.set({ expr: blink(ge, T, 0.6), arms: garms, sit: !standing, bumped: true, talk: talking('G', T), T });
  const bx = lerp(X(380), X(262) + 0.4, ease(seg(lt, 4, 6.5)));
  let shake = [0, 0];
  if (lt < 17.5) {
    let hit = false;
    const projs = [];
    if (lt >= 15.8) for (let i = 0; i < 7; i++) {
      const t0 = 15.8 + i * 0.22;
      if (lt - t0 >= 0 && lt - t0 < 0.35) { const p = (lt - t0) / 0.35; projs.push([lerp(cx + 0.8, bx - 1.8, p), lerp(1.2, 1.6, p) + Math.sin(Math.PI * p) * 0.8, ['{ }', '</>', 'fix', '( )'][i % 4]]); }
      if (lt - (t0 + 0.35) >= 0 && lt - (t0 + 0.35) < 0.07) hit = true;
    }
    place(bug, bx + (hit ? (hash(T * 99) - 0.5) * 0.3 : 0), Math.sin(T * 6) * 0.05, -0.2, 0.25); bug.set({ T, white: hit });
    beam.forEach((m, i) => {
      m.visible = lt >= 12.5 && lt < 15.8; if (!m.visible) return;
      const p = ((i + lt * 3) % 16) / 16; m.position.set(lerp(gx + 0.6, bx - 1.9, p), lerp(1.4, 1.9, p), lerp(0, -0.1, p)); m.rotation.set(lt * 5, lt * 5, 0);
    });
    later(() => {
      for (const [x, y, s] of projs) { const [px, py] = proj(x, y, 0.4); text(s, px, py, 48, '#f09e7c', 4); }
      if (lt >= 12.5 && lt < 15.8 && Math.floor(lt * 6) % 2 === 0) {
        const [x0, y0] = proj(bx - 1.9, 2.6, 0.4), [x1, y1] = proj(bx - 1.0, 0.6, 0.4);
        ctx.strokeStyle = '#ff3c3c'; ctx.lineWidth = 6; const L = 20;
        for (const [x, y, sx, sy] of [[x0, y0, 1, 1], [x1, y0, -1, 1], [x0, y1, 1, -1], [x1, y1, -1, -1]]) { ctx.beginPath(); ctx.moveTo(x + sx * L, y); ctx.lineTo(x, y); ctx.lineTo(x, y + sy * L); ctx.stroke(); }
      }
      if (lt > 13.3 && lt < 15.8) { const [x, y] = proj(bx, 3.6, 0); text('弱点：第 23 行', x, y, 32, '#ff6e6e', 3); }
      if (lt >= 4.8 && lt < 6.2) { const [x, y] = proj(bx, 3.5, 0); text('吼——！', x, y, 64, '#dc78ff', 5); }
    });
  } else {
    const p = seg(lt, 17.5, 18.2);
    if (p < 1) puffs.forEach((m, i) => { m.visible = true; const a = i * Math.PI * 2 / 14; m.position.set(bx + Math.cos(a) * (0.4 + p * 2.4), 1.4 + Math.sin(a) * (0.4 + p * 1.6), 0); m.scale.setScalar(1.1 * (1 - p) + 0.05); });
    if (lt > 17.8) {
      const tt = lt - 17.8;
      place(lady, bx - 0.5 + tt * 1.2, 1.2 + tt * 0.9 + Math.sin(tt * 8) * 0.15, 0.5, 0.4); lady.set(T);
      ladyHeart.visible = true; ladyHeart.position.set(lady.root.position.x, lady.root.position.y + 0.8, 0.5);
    }
    if (lt > 18.2) later(() => { const r = rng(5); for (let i = 0; i < 12; i++) sparkle(80 + r() * 1120, 120 + r() * 300, lt + i * 0.13, i % 2 ? '#ffdc3c' : '#fff'); });
  }
  if (lt >= 1.5 && lt < 3) shake = [(hash(Math.floor(T * 30)) - 0.5) * 0.12, 0];
  if (lt >= 4.8 && lt < 6.5) shake = [(hash(Math.floor(T * 30)) - 0.5) * 0.3, (hash(Math.floor(T * 31)) - 0.5) * 0.15];
  const zoom = lt >= 12.5 && lt < 17.5 ? ease(seg(lt, 12.5, 13.5)) : (lt >= 17.5 ? 1 - ease(seg(lt, 17.5, 19)) : 0);
  setCam(lerp(-0.4, 0.6, zoom), lerp(3.6, 3.0, zoom), lerp(13.2, 11.2, zoom), lerp(-0.2, 0.6, zoom), 1.5, 0, shake);
  later(() => { if (lt >= 5 && lt < 6) { emoteBang(clawd); emoteBang(robot); } });
}

function scSunset(lt, T) {
  applyLight('sunset');
  stars.visible = lt > 14; starMat.opacity = clamp((lt - 14) / 8) * 0.8;
  moon.visible = false; mound.visible = true; sunDisc.visible = true;
  sunDisc.position.set(7, 4.5 - lt * 0.08, -40); sunDisc.lookAt(0, 2, 10);
  clouds.forEach(([g, x0]) => { g.visible = true; g.position.x = ((x0 + T * 0.2 + 30) % 60) - 30; });
  const cx = -0.95, gx = lerp(1.0, 0.55, ease(seg(lt, 15.6, 16.3)));
  let ge = 'normal', ce = 'normal', gyaw = 0.25, gtear = -1;
  if (lt >= 2 && lt < 5.5) { ge = 'shy'; gyaw = -0.5; }
  if (lt >= 5.5 && lt < 12.5) { ce = lt > 9 ? 'happy' : 'normal'; ge = 'shy'; gyaw = -0.5; }
  if (lt >= 12.5 && lt < 15) { ge = 'shy'; gyaw = -0.5; gtear = Math.floor(T * 5) % 3; ce = lt < 13.5 ? 'surprised' : 'normal'; }
  if (lt >= 15 && lt < 17) { ce = 'happy'; ge = 'happy'; gyaw = -0.5; }
  if (lt >= 17 && lt < 19.5) { ge = 'smug'; ce = 'normal'; gyaw = -0.5; }
  if (lt >= 19.5) { ce = 'smug'; ge = 'happy'; gyaw = -0.5; }
  if (lt >= 21) { ce = 'laugh'; ge = 'laugh'; }
  const lb = lt >= 21 ? Math.abs(Math.sin(lt * 9)) * 0.15 : 0;
  place(clawd, cx, MOUND_TOP + bounce('C', T) + lb, 0.2, 0.45); clawd.set({ expr: blink(ce, T), sit: true, bandage: true });
  place(robot, gx, MOUND_TOP + bounce('G', T) + lb, 0.2, gyaw);
  robot.set({ expr: blink(ge, T, 1.1), arms: lt >= 15.6 && lt < 17 ? 'up' : 'down', sit: true, bumped: true, tear: gtear, talk: talking('G', T), T });
  bigHeart.visible = lt >= 16.2 && lt < 20;
  if (bigHeart.visible) {
    const p = seg(lt, 16.2, 20); bigHeart.position.set((cx + gx) / 2, 3.2 + p * 1.2, 0.3);
    bigHeart.scale.setScalar(ease(seg(lt, 16.2, 16.6)) * 1.4); bigHeart.rotation.y = Math.sin(lt * 2) * 0.4;
    smallHearts.forEach((h, i) => { h.visible = true; const q = (p * 1.5 + i * 0.25) % 1; h.position.set((cx + gx) / 2 - 1.5 + i + Math.sin(q * 8) * 0.2, 2.0 + q * 2.5, 0.3); h.rotation.y = lt * 2 + i; });
  }
  flies.forEach((m, i) => {
    m.visible = lt > 6 && Math.sin(lt * 3 + i) > 0; const a = hash(i * 3.3), b = hash(i * 7.1);
    m.position.set(a * 10 - 5 + Math.sin(lt * 0.7 + i) * 0.5, 0.5 + b * 2 + Math.cos(lt * 0.9 + i * 2) * 0.3, 1 + hash(i) * 2);
  });
  const ang = lerp(-0.35, 0.3, lt / 23);
  const rad = lerp(8.5, 7.2, ease(seg(lt, 0, 23)));
  setCam(Math.sin(ang) * rad, 2.8, Math.cos(ang) * rad, 0, 2.0, 0);
  later(() => {
    if (lt >= 21) [[380, 200], [900, 180], [640, 120]].forEach(([x, y], i) => text('哈哈哈！', x + Math.sin(lt * 4 + i) * 10, y - (lt - 21) * 20, 48, '#fff0b4', 4));
  });
}

function scEnd(lt, T) {
  applyLight('night');
  stars.visible = true; starMat.opacity = 1; moon.visible = true; moon.position.set(-10, 13, -40); moon.lookAt(0, 2, 10);
  mound.visible = true; sunDisc.visible = false;
  clouds.forEach(([g]) => g.visible = false);
  place(clawd, -0.42, MOUND_TOP, 0.2, 0.3); clawd.set({ expr: 'sleep', sit: true, bandage: true });
  place(robot, 0.42, MOUND_TOP - 0.05, 0.2, -0.3); robot.root.rotation.z = 0.12; robot.set({ expr: 'sleep', sit: true, bumped: true, T });
  endHeart.visible = true; endHeart.position.set(0, 3.0 + Math.sin(lt * 2) * 0.1, 0.3); endHeart.rotation.y = lt;
  flies.forEach((m, i) => { m.visible = Math.sin(lt * 3 + i) > 0; m.position.set(hash(i * 3.3) * 10 - 5, 0.5 + hash(i * 7.1) * 2.5, 1 + hash(i) * 2); });
  setCam(0, lerp(2.6, 3.4, lt / 7), lerp(6.5, 8.5, lt / 7), 0, 2.2, 0);
  later(() => {
    for (let i = 0; i < 3; i++) { const q = (lt * 0.5 + i / 3) % 1; const [x, y] = headPos(robot, 0.2); text('Z', x + 40 + q * 70, y + 20 - q * 50, i % 2 ? 32 : 48, '#c8d2ff', 3); }
    const a = seg(lt, 0.5, 1.6);
    if (a > 0) { ctx.globalAlpha = a; text('全 剧 终', W / 2, 110, 96, '#ffec96', 6); ctx.globalAlpha = 1; }
    if (lt > 1.8) { ctx.globalAlpha = seg(lt, 1.8, 2.6); text('最强的，是一起帮助别人的我们 ♥', W / 2, 210, 32, '#ffffff', 3); ctx.globalAlpha = 1; }
    if (lt > 2.6) { ctx.globalAlpha = seg(lt, 2.6, 3.4); text('THE END', W / 2, 256, 32, '#b4b4dc', 3); ctx.globalAlpha = 1; }
  });
}

const SCENE_FN = { title: scTitle, meet: scMeet, contest: scContest, fight: scFight, bug: scBug, sunset: scSunset, end: scEnd };
const dynamic = [clawd.root, robot.root, kid.root, bug.root, lady.root, bigHeart, ladyHeart, endHeart, painting.g, panel.g, ...smallHearts, ...puffs, ...starCubes, ...limbs, ...beam, ...steamCubes, ...flies];

function renderAt(T) {
  let name, a, b;
  for ([name, a, b] of STORY.scenes) if (T >= a && T < b) break;
  const lt = T - a;
  dynamic.forEach(o => { o.visible = false; });
  robot.root.rotation.z = 0;
  FX.flash = 0; FX.caption = null; FX.mosaic = null; FX.overlays = [];
  SCENE_FN[name](lt, T);
  renderer.render(scene, camera);
  ctx.clearRect(0, 0, W, H);
  ctx.imageSmoothingEnabled = false;
  if (FX.mosaic) {
    const [[x0, y0], [x1, y1]] = FX.mosaic; const w = x1 - x0, h = y1 - y0;
    const tmp = document.createElement('canvas'); tmp.width = 18; tmp.height = Math.max(1, Math.round(18 * h / w));
    const tg = tmp.getContext('2d'); tg.drawImage(glCanvas, x0, y0, w, h, 0, 0, tmp.width, tmp.height);
    ctx.drawImage(tmp, 0, 0, tmp.width, tmp.height, x0, y0, w, h);
  }
  FX.overlays.forEach(f => f());
  if (FX.caption) { ctx.fillStyle = '#000'; ctx.fillRect(0, 580, W, 60); text(FX.caption, W / 2, 610, 32, '#fff', 0); }
  drawBubble(T);
  if (FX.flash > 0) { ctx.fillStyle = `rgba(255,255,255,${FX.flash})`; ctx.fillRect(0, 0, W, H); }
  let fade = name === 'title' ? Math.min(1, (b - T) / 0.35) : Math.min(1, (T - a) / 0.35, (b - T) / 0.35);
  if (name === 'end') fade = Math.min(1, (T - a) / 0.35, (b - T) / 1.5);
  if (fade < 1) { ctx.fillStyle = `rgba(0,0,0,${1 - Math.max(0, fade)})`; ctx.fillRect(0, 0, W, H); }
}

window.init = async (story) => {
  STORY = story;
  SC = Object.fromEntries(story.scenes.map(([n, a]) => [n, a]));
  LINES = story.lines.map(([s, a, b, w, t]) => [SC[s] + a, SC[s] + b, w, t]);
  await document.fonts.load('32px Pix');
  await document.fonts.load('16px Pix');
  return true;
};
window.renderAt = renderAt;
window.ready = true;
