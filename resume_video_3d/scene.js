// 3D 线稿履历动画：每个物件先在纸面上画出正立面线稿，再像立体书一样从纸里翻起、跃出。
// 页面暴露 window.build() 与 window.renderAt(t)，由 render.mjs 逐帧截图。
import * as THREE from 'three';
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

const W = 1920, H = 1080;
const PAPER = 0xf5efe2, INK = 0x2a2723, INK_CSS = '#2a2723';
const SP = 58;                       // 相邻场景的间距（世界单位）
const CAM_OFF = new THREE.Vector3(0, 14, 34);
const ELEV = Math.atan2(CAM_OFF.y, CAM_OFF.z);
const PI = Math.PI;
const V = (x, y, z) => new THREE.Vector3(x, y, z);

// ---------------------------------------------------------------- 分镜（与手绘版一致）
const SCENES = [
  { id: 'intro', dur: 8.5, draw: sIntro, zh: '我的职业历程', en: 'My Career Journey', sub: '1995 — 至今  ·  Thirty Years on the Road', big: true },
  { id: 'stage1', dur: 5, draw: sStage1, kind: 'stage', zh: '第一阶段 · 工程建设', en: 'Stage I · Engineering Construction', sub: '1995.07 — 2010.10' },
  { id: 'subgrade', dur: 8.5, draw: sSubgrade, zh: '路基路面专业工程师', en: 'Subgrade & Pavement Engineer', sub: '某高速公路  ·  Expressway Project' },
  { id: 'bridge', dur: 8.5, draw: sBridge, zh: '桥梁工程师', en: 'Bridge Engineer', sub: '某钢管拱特大桥  ·  Steel-Tube Arch Super Bridge' },
  { id: 'asphalt', dur: 8.5, draw: sAsphalt, zh: '沥青路面项目经理', en: 'Project Manager, Asphalt Pavement', sub: '某高速公路  ·  Expressway Project' },
  { id: 'tunnel', dur: 8.5, draw: sTunnel, zh: '特长隧道项目总工', en: 'Chief Engineer, Extra-Long Tunnel', sub: '某高速公路  ·  Expressway Project' },
  { id: 'stage2', dur: 5, draw: sStage2, kind: 'stage', zh: '第二阶段 · 运营管理', en: 'Stage II · Operations Management', sub: '2010.10 — 2021.09' },
  { id: 'office', dur: 8, draw: sOffice, zh: '办公室主任', en: 'Director of General Office', sub: '某高速公路运营公司  ·  Expressway Operations' },
  { id: 'gm', dur: 8.5, draw: sGM, zh: '公司总经理', en: 'General Manager', sub: '某高速公路运营公司  ·  Expressway Operations' },
  { id: 'maint', dur: 8.5, draw: sMaint, zh: '工程部经理', en: 'Manager, Engineering Department', sub: '某高速公路运营公司  ·  Expressway Operations' },
  { id: 'stage3', dur: 5, draw: sStage3, kind: 'stage', zh: '第三阶段 · 安全管理', en: 'Stage III · Safety Management', sub: '2021.09 — 至今 Present' },
  { id: 'safety', dur: 11, draw: sSafety, zh: '安全部负责人', en: 'Head of Safety Department', sub: '某上市集团  ·  A Listed Group' },
  { id: 'outro', dur: 12, draw: sOutro },
];

// ---------------------------------------------------------------- 渲染器
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('gl'), antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
const scene = new THREE.Scene();
scene.background = new THREE.Color(PAPER);
const camera = new THREE.PerspectiveCamera(30, W / H, 0.5, 500);

const MATS = {
  n: new LineMaterial({ color: INK, linewidth: 2.4 }),
  b: new LineMaterial({ color: INK, linewidth: 3.4 }),
  t: new LineMaterial({ color: INK, linewidth: 1.4 }),
};
const MATS_TOP = {}; // 不做深度测试（隧道内部等）
for (const k in MATS) {
  MATS[k].resolution.set(W, H);
  MATS_TOP[k] = MATS[k].clone(); MATS_TOP[k].depthTest = false; MATS_TOP[k].resolution.set(W, H);
}
const FILL = new THREE.MeshBasicMaterial({ color: PAPER, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: 2, polygonOffsetUnits: 2 });

// 纸张
function paperTexture() {
  const c = document.createElement('canvas'); c.width = c.height = 1024;
  const g = c.getContext('2d');
  g.fillStyle = '#f5efe2'; g.fillRect(0, 0, 1024, 1024);
  const img = g.getImageData(0, 0, 1024, 1024), d = img.data;
  let s = 12345; const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < d.length; i += 4) { const n = (rnd() - 0.5) * 14; d[i] += n; d[i + 1] += n * 0.95; d[i + 2] += n * 0.8; }
  g.putImageData(img, 0, 0);
  g.globalAlpha = 0.05; g.strokeStyle = '#6b5a3e';
  for (let i = 0; i < 260; i++) { g.lineWidth = rnd() * 1.4; g.beginPath(); const y = rnd() * 1024; g.moveTo(0, y); g.bezierCurveTo(300, y + rnd() * 20 - 10, 700, y + rnd() * 20 - 10, 1024, y); g.stroke(); }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(60, 4); t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
const paper = new THREE.Mesh(new THREE.PlaneGeometry(SP * 16, 240), new THREE.MeshBasicMaterial({ map: paperTexture() }));
paper.rotation.x = -PI / 2; paper.position.set(SP * 6, 0, -60);
scene.add(paper);

// ---------------------------------------------------------------- 物件构建器
let seedV = 7;
const rnd = () => ((seedV = (seedV * 16807) % 2147483647) / 2147483647);
const tmpM = new THREE.Matrix4();
function mat(pos = [0, 0, 0], rot = [0, 0, 0], scl = [1, 1, 1]) {
  return new THREE.Matrix4().compose(V(...pos), new THREE.Quaternion().setFromEuler(new THREE.Euler(...rot)), V(...scl));
}

class Obj {
  constructor(o = {}) {
    this.pivot = new THREE.Group();
    this.inner = new THREE.Group();
    this.pivot.add(this.inner);
    this.segs = { n: [], b: [], t: [] };
    this.ord = 0;
    this.fills = [];
    this.labels = [];
    this.o = o;
  }
  // 线段按 0.35 单位细分，便于“生长”
  seg(a, b, w = 'n') {
    const n = Math.max(1, Math.ceil(a.distanceTo(b) / 0.35));
    for (let i = 0; i < n; i++) this.segs[w].push([a.clone().lerp(b, i / n), a.clone().lerp(b, (i + 1) / n), this.ord++]);
  }
  line(pts, w = 'n', closed = false) {
    for (let i = 0; i < pts.length - 1; i++) this.seg(pts[i], pts[i + 1], w);
    if (closed) this.seg(pts[pts.length - 1], pts[0], w);
  }
  arc(c, r, plane = 'xy', a0 = 0, a1 = 2 * PI, w = 'n', n = 36, ry = r) {
    const pts = [];
    for (let i = 0; i <= n; i++) {
      const a = a0 + (a1 - a0) * i / n, u = Math.cos(a) * r, v = Math.sin(a) * ry;
      pts.push(plane === 'xy' ? V(c.x + u, c.y + v, c.z) : plane === 'xz' ? V(c.x + u, c.y, c.z + v) : V(c.x, c.y + v, c.z + u));
    }
    this.line(pts, w);
  }
  // 由几何体生成：填充（遮挡背后线条）+ 轮廓边
  geom(g, m, o = {}) {
    g.applyMatrix4(m);
    if (o.fill !== false) { const mesh = new THREE.Mesh(g, FILL); this.inner.add(mesh); this.fills.push(mesh); }
    const e = new THREE.EdgesGeometry(g, o.th ?? 20).attributes.position.array;
    const list = [];
    for (let i = 0; i < e.length; i += 6) list.push([V(e[i], e[i + 1], e[i + 2]), V(e[i + 3], e[i + 4], e[i + 5])]);
    list.sort((p, q) => Math.min(p[0].y, p[1].y) - Math.min(q[0].y, q[1].y) || p[0].x - q[0].x);
    for (const [a, b] of list) this.seg(a, b, o.w ?? 'n');
    return g;
  }
  box(w, h, d, pos, rot, o) { return this.geom(new THREE.BoxGeometry(w, h, d), mat(pos, rot), o); }
  // 以底面为基准的盒子
  blk(x0, y0, z0, w, h, d, o) { return this.box(w, h, d, [x0 + w / 2, y0 + h / 2, z0 + d / 2], [0, 0, 0], o); }
  cyl(rt, rb, h, pos, rot, seg = 18, o = {}) {
    const g = this.geom(new THREE.CylinderGeometry(rt, rb, h, seg, 1), mat(pos, rot), { th: 25, ...o });
    if (o.gen) { // 手动补几条母线
      const m = mat(pos, rot);
      for (let i = 0; i < o.gen; i++) { const a = i / o.gen * 2 * PI + (o.genOff ?? 0.4); this.seg(V(Math.cos(a) * rb, -h / 2, Math.sin(a) * rb).applyMatrix4(m), V(Math.cos(a) * rt, h / 2, Math.sin(a) * rt).applyMatrix4(m), 't'); }
    }
    return g;
  }
  wheel(x, y, z, r, wdt) { this.cyl(r, r, wdt, [x, y, z], [PI / 2, 0, 0], 20); this.arc(V(x, y, z + wdt / 2 + 0.01), r * 0.4, 'xy', 0, 2 * PI, 't', 16); }
  sphere(r, c, o = {}) {
    const g = new THREE.SphereGeometry(r, 16, 12); g.translate(c.x, c.y, c.z);
    const mesh = new THREE.Mesh(g, FILL); this.inner.add(mesh); this.fills.push(mesh);
    this.arc(c, r, 'xy', 0, 2 * PI, o.w ?? 'n', 28);
    this.arc(c, r, 'xz', 0, 2 * PI, 't', 28);
    if (o.meridian !== false) this.arc(c, r, 'zy', 0, 2 * PI, 't', 28);
  }
  beam(a, b, t = 0.2, o) {
    const d = b.clone().sub(a), len = d.length();
    const q = new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), d.normalize());
    const m = new THREE.Matrix4().compose(a.clone().add(b).multiplyScalar(0.5), q, V(1, 1, 1));
    return this.geom(new THREE.BoxGeometry(t, len, t), m, o);
  }
  // 2D 轮廓（xy 平面）沿 z 拉伸
  extrude(pts, depth, pos = [0, 0, 0], rot = [0, 0, 0], o = {}) {
    const sh = new THREE.Shape(pts.map(p => new THREE.Vector2(p[0], p[1])));
    for (const hole of o.holes ?? []) sh.holes.push(new THREE.Path(hole.map(p => new THREE.Vector2(p[0], p[1]))));
    const g = new THREE.ExtrudeGeometry(sh, { depth, bevelEnabled: false, curveSegments: o.cs ?? 12 });
    g.translate(0, 0, -depth / 2);
    return this.geom(g, mat(pos, rot), { th: o.th ?? 30, ...o });
  }
  tube(pts, r, o = {}) {
    const curve = new THREE.CatmullRomCurve3(pts);
    const g = new THREE.TubeGeometry(curve, 64, r, 8, false);
    const mesh = new THREE.Mesh(g, FILL); this.inner.add(mesh); this.fills.push(mesh);
    const P = curve.getSpacedPoints(80);
    for (const s of [-1, 1]) this.line(P.map(p => p.clone().add(V(0, 0, s * r))), o.w ?? 'n');
    this.line(P.map(p => p.clone().add(V(0, r, 0))), 't');
    return curve;
  }
  // 物件上的文字牌（随物件出现）
  label(text, font, px, hWorld, pos, rot = [0, 0, 0], o = {}) {
    const m = textMesh(text, font, px, hWorld, o);
    m.position.set(...pos); m.rotation.set(...rot);
    if (o.center !== false) m.children[0].position.x = -m.userData.w / 2;
    this.inner.add(m); this.labels.push(m);
  }
  finish() {
    this.lines = [];
    for (const k of ['n', 'b', 't']) {
      const arr = this.segs[k];
      if (!arr.length) continue;
      const pos = new Float32Array(arr.length * 6), ords = new Int32Array(arr.length);
      arr.sort((a, b) => a[2] - b[2]);
      arr.forEach(([a, b, o], i) => { pos.set([a.x, a.y, a.z, b.x, b.y, b.z], i * 6); ords[i] = o; });
      const g = new LineSegmentsGeometry(); g.setPositions(pos);
      const ls = new LineSegments2(g, (this.o.top ? MATS_TOP : MATS)[k]);
      ls.frustumCulled = false;
      if (this.o.top) ls.renderOrder = 10;
      this.inner.add(ls);
      this.lines.push({ g, ords, n: arr.length });
    }
    this.total = this.ord;
    // 以正面底边为铰链：翻平时整个物件藏在纸面下方，只露出正立面线稿
    const bb = new THREE.Box3();
    for (const f of this.fills) { f.geometry.computeBoundingBox(); bb.union(f.geometry.boundingBox); }
    for (const k in this.segs) for (const [a, b] of this.segs[k]) { bb.expandByPoint(a); bb.expandByPoint(b); }
    this.front = bb.max.z;
    this.inner.position.z = -this.front;
    this.pivot.position.z += this.front;
    this.pivot.position.y = (this.o.base ?? 0) + 0.02;
    return this;
  }
  reveal(k) {
    for (const L of this.lines) {
      let lo = 0, hi = L.n;
      while (lo < hi) { const m = (lo + hi) >> 1; if (L.ords[m] < k) lo = m + 1; else hi = m; }
      L.g.instanceCount = lo;
    }
  }
}

// 文字：画在 canvas 上的贴图平面，左对齐，底部基线 y=0
function textMesh(text, font, px, hWorld, o = {}) {
  const c = document.createElement('canvas'), g = c.getContext('2d');
  const fontStr = `${o.bold ? '700 ' : ''}${px}px ${font === 'Hand' ? 'Hand, XingShu' : font}`;
  g.font = fontStr;
  const tw = Math.ceil(g.measureText(text).width) + px * 0.4;
  c.width = tw; c.height = Math.ceil(px * 1.5);
  g.font = fontStr; g.fillStyle = INK_CSS; g.textBaseline = 'alphabetic';
  g.fillText(text, px * 0.2, px * 1.1);
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const s = hWorld / c.height, w = c.width * s;
  const geo = new THREE.PlaneGeometry(w, hWorld); geo.translate(w / 2, hWorld / 2 - px * 0.4 * s, 0);
  const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, side: THREE.DoubleSide }));
  const grp = new THREE.Group(); grp.add(m);
  grp.userData = { w, tex, mesh: m };
  return grp;
}

// ---------------------------------------------------------------- 组件库（局部坐标：x 右，y 上，z 朝向镜头）
function person(o = {}) {
  return b => {
    const f = o.face ?? 0;
    const g = new THREE.Group(); // 占位，便于旋转：用矩阵作用在点上
    const R = new THREE.Matrix4().makeRotationY(f);
    const P = (x, y, z) => V(x, y, z).applyMatrix4(R);
    const bm = (a, c, t) => b.beam(a, c, t);
    if (o.pose === 'sit') {
      for (const s of [-1, 1]) { bm(P(s * 0.17, 1.0, 0), P(s * 0.17, 1.0, 0.75), 0.22); bm(P(s * 0.17, 1.0, 0.75), P(s * 0.17, 0, 0.8), 0.2); }
    } else {
      const st = o.pose === 'walk' ? 0.38 : 0.04;
      bm(P(-0.17, 1.02, 0), P(-0.19, 0, st), 0.22); bm(P(0.17, 1.02, 0), P(0.19, 0, -st), 0.22);
    }
    b.geom(new THREE.BoxGeometry(0.72, 0.95, 0.42), mat([0, 1.5, 0], [0, f, 0]));
    if (o.vest) { for (const s of [-1, 1]) b.seg(P(s * 0.16, 1.95, 0.22), P(s * 0.16, 1.08, 0.22), 't'); b.seg(P(-0.36, 1.45, 0.22), P(0.36, 1.45, 0.22), 't'); }
    if (o.tie) b.line([P(0, 1.95, 0.22), P(-0.06, 1.6, 0.22), P(0, 1.48, 0.22), P(0.06, 1.6, 0.22), P(0, 1.95, 0.22)], 't');
    // 手臂
    const sh = s => P(s * 0.44, 1.9, 0);
    const hand = {
      down: [P(-0.5, 1.1, 0.05), P(0.5, 1.1, 0.05)],
      point: [P(-0.5, 1.1, 0.05), P(1.15, 2.35, 0.45)],
      raise: [P(-0.5, 1.1, 0.05), P(0.62, 2.95, 0.1)],
      hold: [P(-0.18, 1.5, 0.55), P(0.18, 1.5, 0.55)],
      sit: [P(-0.3, 1.45, 0.75), P(0.3, 1.45, 0.75)],
      walk: [P(-0.48, 1.15, -0.3), P(0.48, 1.15, 0.3)],
    }[o.pose ?? 'down'];
    bm(sh(-1), hand[0], 0.17); bm(sh(1), hand[1], 0.17);
    if (o.pose === 'hold') b.geom(new THREE.BoxGeometry(0.55, 0.7, 0.05), mat(P(0, 1.62, 0.6).toArray(), [-0.5, f, 0]));
    // 头 + 安全帽
    b.sphere(0.25, V(0, 2.25, 0).applyMatrix4(R), { meridian: false });
    if (o.hat !== false) {
      const c = V(0, 2.33, 0);
      const g2 = new THREE.SphereGeometry(0.3, 14, 7, 0, 2 * PI, 0, PI / 2); g2.translate(c.x, c.y, c.z);
      const mesh = new THREE.Mesh(g2, FILL); b.inner.add(mesh); b.fills.push(mesh);
      b.arc(c, 0.4, 'xz', 0, 2 * PI, 'n', 24);
      b.arc(c, 0.3, 'xy', 0, PI, 'n', 14); b.arc(c, 0.3, 'zy', 0, PI, 't', 14);
    }
  };
}
function car(o = {}) {
  return b => {
    const prof = [[-2, 0.35], [-2, 0.95], [-1.1, 1.05], [-0.55, 1.6], [0.85, 1.6], [1.45, 1.05], [2.1, 0.9], [2.1, 0.35]];
    b.extrude(prof, 1.8, [0, 0, 0], [0, 0, 0], { th: 20 });
    for (const z of [0.91, -0.91]) b.line([V(-0.9, 1.05, z), V(-0.45, 1.5, z), V(0.8, 1.5, z), V(1.25, 1.05, z)], 't', true);
    for (const x of [-1.2, 1.25]) for (const z of [0.95, -0.95]) b.wheel(x, 0.42, z, 0.42, 0.3);
  };
}
function truck(o = {}) {
  return b => {
    b.blk(1.6, 0.45, -1, 1.6, 1.8, 2);
    b.line([V(1.8, 1.4, 1.01), V(2.9, 1.4, 1.01), V(3.1, 2.0, 1.01), V(1.8, 2.0, 1.01)], 't', true);
    b.blk(-2.6, 0.45, -1, 4.1, 0.7, 2);
    for (const x of [-1.8, 2.3]) for (const z of [1.02, -1.02]) b.wheel(x, 0.45, z, 0.45, 0.3);
    if (o.arrow) {
      b.beam(V(-1.8, 1.15, 0), V(-1.8, 2.3, 0), 0.15);
      b.blk(-3.0, 2.3, -0.1, 2.4, 1.2, 0.2);
      b.line([V(-2.7, 2.9, 0.12), V(-1.0, 2.9, 0.12)], 'b');
      b.line([V(-1.4, 3.2, 0.12), V(-0.95, 2.9, 0.12), V(-1.4, 2.6, 0.12)], 'b');
    }
    if (o.drill) {
      b.beam(V(-0.5, 1.2, 0.4), V(3.8, 3.2, 0.4), 0.18); b.beam(V(-0.5, 1.2, -0.4), V(4.2, 2.4, -0.4), 0.18);
      b.beam(V(3.8, 3.2, 0.4), V(5.0, 3.0, 0.4), 0.1); b.beam(V(4.2, 2.4, -0.4), V(5.3, 2.3, -0.4), 0.1);
    }
  };
}
function roller() {
  return b => {
    b.cyl(0.85, 0.85, 2.1, [1.7, 0.85, 0], [PI / 2, 0, 0], 22); b.arc(V(1.7, 0.85, 1.06), 0.35, 'xy', 0, 2 * PI, 't', 16);
    for (const z of [0.85, -0.85]) b.wheel(-1.5, 0.62, z, 0.62, 0.4);
    b.blk(-2.3, 0.7, -0.75, 3.2, 0.75, 1.5);
    b.blk(0.9, 1.1, -0.5, 1.2, 0.5, 1.0);
    for (const x of [-2.0, -0.6]) for (const z of [0.6, -0.6]) b.beam(V(x, 1.45, z), V(x, 2.85, z), 0.1);
    b.blk(-2.25, 2.85, -0.8, 1.9, 0.15, 1.6);
    b.blk(-1.6, 1.45, -0.3, 0.6, 0.5, 0.6);
  };
}
function excavator() {
  return b => {
    for (const z of [0.85, -0.85]) { b.blk(-2, 0, z - 0.35, 4, 0.7, 0.7); b.wheel(-1.7, 0.35, z, 0.33, 0.72); b.wheel(1.7, 0.35, z, 0.33, 0.72); }
    b.blk(-1.6, 0.75, -1, 2.8, 1.1, 2);
    b.blk(0.3, 1.85, 0.05, 0.9, 1.1, 0.9);
    b.line([V(0.4, 2.1, 0.96), V(1.1, 2.1, 0.96), V(1.1, 2.8, 0.96), V(0.4, 2.8, 0.96)], 't', true);
    b.beam(V(1.0, 1.6, -0.3), V(2.8, 4.3, -0.3), 0.36);
    b.beam(V(2.8, 4.3, -0.3), V(4.2, 1.9, -0.3), 0.28);
    b.extrude([[0, 0], [0.9, 0.3], [0.8, -0.7], [0.1, -0.9]], 0.9, [3.8, 1.8, -0.3]);
  };
}
function paver() {
  return b => {
    b.blk(-1.6, 0.5, -1.3, 3.2, 1.2, 2.6);
    b.extrude([[0, 0], [1.6, 0.8], [1.6, 1.6], [0, 1.3]], 2.6, [1.6, 0.4, 0]);
    b.blk(-2.4, 0.2, -1.6, 0.8, 0.5, 3.2);
    for (const x of [-0.9, 0.9]) for (const z of [1.35, -1.35]) b.wheel(x, 0.45, z, 0.45, 0.3);
    for (const x of [-1.4, 0.8]) for (const z of [1.1, -1.1]) b.beam(V(x, 1.7, z), V(x, 3.0, z), 0.1);
    b.blk(-1.6, 3.0, -1.3, 2.6, 0.14, 2.6);
    for (let i = 0; i < 3; i++) { const pts = []; for (let k = 0; k <= 10; k++) pts.push(V(-2.2 + i * 0.3 + Math.sin(k * 0.9 + i) * 0.12, 0.8 + k * 0.18, 0)); b.line(pts, 't'); }
  };
}
function tripod() {
  return b => {
    for (const a of [0.3, 2.4, 4.5]) b.beam(V(0, 1.45, 0), V(Math.cos(a) * 0.55, 0, Math.sin(a) * 0.55), 0.06);
    b.blk(-0.3, 1.45, -0.18, 0.6, 0.3, 0.36);
    b.cyl(0.1, 0.1, 0.5, [0.45, 1.6, 0], [0, 0, PI / 2], 12);
  };
}
function cone() {
  return b => {
    b.cyl(0.07, 0.3, 0.85, [0, 0.47, 0], [0, 0, 0], 10, { gen: 2, genOff: 1.3 });
    b.blk(-0.36, 0, -0.36, 0.72, 0.06, 0.72);
    b.arc(V(0, 0.35, 0), 0.23, 'xz', 0, 2 * PI, 't', 14); b.arc(V(0, 0.6, 0), 0.16, 'xz', 0, 2 * PI, 't', 14);
  };
}
function pine(s = 1) {
  return b => {
    b.cyl(0.12 * s, 0.14 * s, 0.6 * s, [0, 0.3 * s, 0], [0, 0, 0], 6);
    b.cyl(0, 0.9 * s, 1.6 * s, [0, 1.3 * s, 0], [0, 0, 0], 7);
    b.cyl(0, 0.7 * s, 1.3 * s, [0, 2.1 * s, 0], [0, 0.3, 0], 7);
  };
}
function mountain(r, h, seed, sz = 1) {
  return b => {
    const g = new THREE.ConeGeometry(r, h, 9, 3); g.translate(0, h / 2, 0);
    const p = g.attributes.position;
    const hash = (x, z) => { const s = Math.sin(x * 12.9898 + z * 78.233 + seed) * 43758.5453; return s - Math.floor(s); };
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
      if (y > 0.01 && y < h - 0.01) { const k = 0.25 * r; p.setXYZ(i, x + (hash(x, z) - 0.5) * k, y + (hash(z, x) - 0.5) * h * 0.25, z + (hash(x + 1, z) - 0.5) * k); }
    }
    g.scale(1, 1, sz);
    b.geom(g, new THREE.Matrix4(), { th: 8, w: 'n' });
  };
}
function building(w, h, d, cols, rows) {
  return b => {
    b.blk(-w / 2, 0, -d / 2, w, h, d);
    const cw = w / cols, rh = Math.min((h - 1) / rows, 1.3);
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const x = -w / 2 + c * cw + cw * 0.25, y = h - 0.8 - r * rh;
      b.line([V(x, y, d / 2 + 0.01), V(x + cw * 0.5, y, d / 2 + 0.01), V(x + cw * 0.5, y - rh * 0.55, d / 2 + 0.01), V(x, y - rh * 0.55, d / 2 + 0.01)], 't', true);
    }
    const dc = Math.max(2, Math.round(cols * d / w)), dw = d / dc;
    for (let r = 0; r < rows; r++) for (let c = 0; c < dc; c++) {
      const z = d / 2 - c * dw - dw * 0.25, y = h - 0.8 - r * rh;
      b.line([V(w / 2 + 0.01, y, z), V(w / 2 + 0.01, y, z - dw * 0.5), V(w / 2 + 0.01, y - rh * 0.55, z - dw * 0.5), V(w / 2 + 0.01, y - rh * 0.55, z)], 't', true);
    }
  };
}
function shield(s = 1) {
  return b => {
    const sp = [[0, 4.4 * s], [1.2 * s, 4.0 * s], [2.3 * s, 4.05 * s], [2.3 * s, 2.3 * s], [1.8 * s, 1.1 * s], [0, 0], [-1.8 * s, 1.1 * s], [-2.3 * s, 2.3 * s], [-2.3 * s, 4.05 * s], [-1.2 * s, 4.0 * s]];
    b.extrude(sp, 0.7 * s, [0, 0, 0], [0, 0, 0], { th: 20 });
    b.beam(V(-0.9 * s, 2.3 * s, 0.45 * s), V(-0.2 * s, 1.5 * s, 0.45 * s), 0.25 * s);
    b.beam(V(-0.2 * s, 1.5 * s, 0.45 * s), V(1.1 * s, 3.2 * s, 0.45 * s), 0.25 * s);
  };
}
function helmetBig(s = 1) {
  return b => {
    const c = V(0, 0.25 * s, 0), r = 2.1 * s;
    const g = new THREE.SphereGeometry(r, 20, 10, 0, 2 * PI, 0, PI / 2); g.translate(c.x, c.y, c.z);
    const mesh = new THREE.Mesh(g, FILL); b.inner.add(mesh); b.fills.push(mesh);
    b.cyl(2.9 * s, 2.9 * s, 0.25 * s, [0, 0.13 * s, 0.2 * s], [0, 0, 0], 32);
    for (const a of [0, PI / 4, PI / 2, 3 * PI / 4]) {
      const pts = []; for (let i = 0; i <= 18; i++) { const u = PI * i / 18; pts.push(V(Math.cos(u) * r * Math.cos(a), c.y + Math.sin(u) * r, Math.cos(u) * r * Math.sin(a))); }
      b.line(pts, a === 0 ? 'b' : 't');
    }
    b.arc(V(0, c.y + r * 0.5, 0), r * 0.866, 'xz', 0, 2 * PI, 't', 30);
    b.box(0.5 * s, 0.35 * s, 4.3 * s, [0, c.y + r + 0.05, 0], [0, 0, 0]);
  };
}
function flag(label) {
  return b => {
    b.cyl(0.05, 0.05, 2.6, [0, 1.3, 0], [0, 0, 0], 6);
    b.extrude([[0, 0], [1.2, -0.35], [0, -0.7]], 0.05, [0, 2.6, 0]);
    b.label(label, 'Hand', 90, 0.8, [0.2, 0.2, 0.3], [0, 0, 0], { bold: true, center: false });
  };
}

// ---------------------------------------------------------------- 场景
let S = null; // 当前场景：{ cx, objs: [] }
function place(x, z, build, o = {}) {
  const ob = new Obj(o);
  build(ob);
  ob.finish();
  ob.pivot.position.x = S.cx + x;
  ob.pivot.position.z += z;
  if (o.ry) ob.pivot.rotation.y = o.ry;
  scene.add(ob.pivot);
  S.objs.push(ob);
  return ob;
}
const flat = { anim: 'flat' };

function roadAlongZ(b, x0, x1, z0, z1, dash = true) {
  b.line([V(x0, 0, z0), V(x0, 0, z1)], 'b'); b.line([V(x1, 0, z0), V(x1, 0, z1)], 'b');
  if (dash) for (let z = z0; z > z1; z -= 3) b.line([V((x0 + x1) / 2, 0, z), V((x0 + x1) / 2, 0, z - 1.5)], 'b');
}
function sIntro() {
  place(8, 0, b => roadAlongZ(b, 4, 10, 9, -40), flat);
  place(0, -30, mountain(9, 5, 1, 0.5));
  place(14, -32, mountain(11, 7, 2, 0.5));
  place(27, -30, mountain(8, 5, 3, 0.5));
  place(20, -24, b => { b.arc(V(0, 5, 0), 1.8, 'xy', 0, 2 * PI, 'b', 40); for (let i = 0; i < 12; i++) { const a = i / 12 * 2 * PI; b.seg(V(Math.cos(a) * 2.4, 5 + Math.sin(a) * 2.4, 0), V(Math.cos(a) * 3.1, 5 + Math.sin(a) * 3.1, 0), 'n'); } }, { anim: 'rise' });
  for (const [x, z, s] of [[1, -4, 1.1], [-1, 2, 1.3], [15, -6, 1], [17, 0, 1.3], [0.5, -12, 0.9], [14.5, -14, 0.9]]) place(x, z, pine(s));
  place(-6.5, 5, flag('1995'));
}
function sStage1() {
  place(8, -3, helmetBig(1.1));
  place(8, 4, b => { b.cyl(0.5, 0.5, 8, [0, 0.5, 0], [0, 0, PI / 2], 20, { gen: 4 }); b.arc(V(-4.01, 0.5, 0), 0.25, 'zy', 0, 2 * PI, 't', 12); });
  place(-6.5, 5, flag('1995.07'));
}
function sSubgrade() {
  // 路堤：梯形断面沿 z 拉伸，顶面叠铺结构层
  place(7, -1, b => {
    b.extrude([[-8, 0], [8, 0], [4.5, 2.4], [-4.5, 2.4]], 9, [0, 0, 0], [0, 0, 0], { th: 20 });
    for (const y of [0.8, 1.6]) { const hw = 8 - y * 3.5 / 2.4; b.line([V(-hw, y, 4.51), V(hw, y, 4.51)], 't'); }
    b.blk(-4.4, 2.4, -4.5, 8.8, 0.35, 9); b.blk(-4.1, 2.75, -4.5, 8.2, 0.3, 9); b.blk(-3.8, 3.05, -4.5, 7.6, 0.2, 9);
    for (let x = -3.6; x < 3.8; x += 0.35) b.seg(V(x, 3.05, 4.52), V(x + 0.2, 3.25, 4.52), 't');
    b.label('面层 surface', 'Hand', 90, 0.8, [4.3, 2.95, 4.6], [0, 0, 0], { center: false, bold: true });
    b.label('基层 base', 'Hand', 90, 0.8, [4.8, 2.3, 4.6], [0, 0, 0], { center: false, bold: true });
    b.label('路基 subgrade', 'Hand', 90, 0.8, [6.4, 0.9, 4.6], [0, 0, 0], { center: false, bold: true });
  });
  place(6, -2, roller(), { anim: 'drop', base: 3.25, ry: 0.35 });
  place(9.5, 1.5, person({ vest: true, pose: 'point', face: -0.6 }), { anim: 'drop', base: 3.25 });
  place(17, -7, excavator(), { ry: PI + 0.5 });
  place(-4, 5, tripod());
  place(-2.6, 5.2, person({ pose: 'hold', face: -0.9 }));
}
function sBridge() {
  place(8, 3, b => {
    for (let x = -12; x < 26; x += 4.2) for (const z of [0, 2.4, 4.8]) { const xx = x + (z % 4.8 ? 1.8 : 0); b.line([0, 1, 2, 3, 4, 5, 6].map(k => V(xx + k * 0.3 - 8, 0, z - 3 + Math.sin(k * 1.4) * 0.15)), 't'); }
  }, flat);
  place(9, -3, b => {
    b.blk(-12, 3, -1.6, 24, 0.45, 3.2);
    for (const z of [1.6, -1.6]) b.line([V(-12, 3.9, z), V(12, 3.9, z)], 't');
    for (const x of [-9, 9]) b.blk(x - 0.7, 0, -1.2, 1.4, 3, 2.4);
    for (const z of [-1.3, 1.3]) {
      const pts = [], pts2 = [];
      for (let i = 0; i <= 24; i++) { const t = i / 24, x = -9 + 18 * t, y = 3.1 + Math.sin(t * PI) * 5.8; pts.push(V(x, y, z)); pts2.push(V(x, y - 0.55 - Math.sin(t * PI) * 0.1, z)); }
      b.tube(pts, 0.16); b.tube(pts2, 0.12, { w: 't' });
      for (let i = 1; i < 24; i += 2) b.seg(pts[i], pts2[i + 1], 't');
      for (let i = 2; i < 23; i += 2) { const p = pts2[i]; if (p.y > 3.8) b.seg(p, V(p.x, 3.45, z), 't'); }
    }
    for (let i = 3; i < 22; i += 3) { const t = i / 24; b.seg(V(-9 + 18 * t, 3.1 + Math.sin(t * PI) * 5.8, -1.3), V(-9 + 18 * t, 3.1 + Math.sin(t * PI) * 5.8, 1.3), 't'); }
  });
  place(-1, 4.5, person({ pose: 'point', face: 0.6 }));
  place(13, 3.2, b => { b.extrude([[-1.5, 0.4], [1.5, 0.4], [1.1, 0], [-1.1, 0]], 1.0); b.beam(V(0, 0.4, 0), V(0, 1.9, 0), 0.06); b.extrude([[0, 1.9], [0.9, 1.2], [0, 1.2]], 0.04); });
  place(22, -9, b => {
    for (const [x, z] of [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]]) b.beam(V(x, 0, z), V(x, 13, z), 0.12);
    for (let y = 1; y < 13; y += 1.6) { b.seg(V(-0.5, y, 0.5), V(0.5, y + 1.6, 0.5), 't'); b.seg(V(-0.5, y, 0.5), V(0.5, y, 0.5), 't'); }
    b.blk(-4, 13, -0.4, 14, 0.5, 0.8); b.blk(-4, 13.5, -0.3, 1.6, 0.8, 0.6);
    b.line([V(-3.5, 13.5, 0), V(0, 15.5, 0), V(9.5, 13.5, 0)], 't');
    b.seg(V(-8.5 + 15, 13, 0), V(6.5, 9, 0), 't');
  });
}
function sAsphalt() {
  place(6, 1, b => {
    b.line([V(-18, 0, -2), V(26, 0, -2)], 'b'); b.line([V(-18, 0, 4), V(26, 0, 4)], 'b');
    for (let x = -17.5; x < 2; x += 0.5) b.seg(V(x, 0, 3.9), V(x + 1.2, 0, -1.9), 't');
  }, flat);
  place(4, -24, mountain(10, 6, 21, 0.5));
  place(20, -26, mountain(12, 8, 22, 0.5));
  place(8, 1, paver(), { ry: PI });
  place(1, 1, roller(), { ry: PI });
  place(-5.5, 1, roller(), { ry: PI });
  for (let i = 0; i < 26; i++) place(12 + (i * 3.7) % 12, -1.5 + (i * 1.9) % 5, b => b.arc(V(0, 0, 0), 0.12, 'xz', 0, 2 * PI, 't', 6), flat);
  place(15, 5.5, person({ pose: 'hold', face: -0.5 }));
  place(18.5, 5, b => { person({ vest: true, pose: 'raise', face: -0.5 })(b); b.beam(V(0.45, 2.9, -0.2), V(0.55, 4.8, -0.25), 0.06); b.extrude([[0, 0], [1.1, -0.3], [0, -0.6]], 0.04, [0.55, 4.8, -0.25]); });
  place(21, 3, cone()); place(22.5, 2, cone()); place(23.5, 0.8, cone());
}
function sTunnel() {
  place(8, -11, mountain(14, 11, 7, 0.4));
  place(24, -16, mountain(8, 6, 9, 0.6));
  place(8, -2.5, b => {
    const hole = []; for (let i = 0; i <= 20; i++) { const a = PI * i / 20; hole.push([Math.cos(a) * 3.4, 3.0 + Math.sin(a) * 3.4]); }
    b.extrude([[-6.5, 0], [6.5, 0], [6.5, 8], [-6.5, 8]], 1.2, [0, 0, 0], [0, 0, 0], { holes: [[[3.4, 0.01], ...hole, [-3.4, 0.01]]], cs: 20, th: 25 });
    b.blk(-7, 8, -0.9, 14, 0.7, 1.8);
    b.label('隧道  TUNNEL', 'XingShu', 110, 0.95, [0, 7.0, 0.62]);
  });
  place(8, -3.1, b => {
    for (const z of [-1.5, -3.5, -5.5, -8]) { const k = 1 - (-z) * 0.03; b.arc(V(0, 3 * k, z), 3.4 * k, 'xy', 0, PI, 't', 20); b.seg(V(3.4 * k, 0, z), V(3.4 * k, 3 * k, z), 't'); b.seg(V(-3.4 * k, 0, z), V(-3.4 * k, 3 * k, z), 't'); }
    for (let i = 0; i < 5; i++) b.arc(V(-1.6 + i * 0.8, 5.6, -1.6), 0.12, 'xy', 0, 2 * PI, 't', 8);
  }, { anim: 'plain', top: true });
  place(8, 0, b => { b.line([V(-3, 0, 0), V(-3, 0, 9)], 'b'); b.line([V(3, 0, 0), V(3, 0, 9)], 'b'); for (let z = 1; z < 9; z += 2.5) b.seg(V(0, 0, z), V(0, 0, z + 1.2), 'b'); }, flat);
  place(-2, 2.5, truck({ drill: true }), { ry: 0.25 });
  place(13, 4.5, person({ pose: 'hold', face: -0.5 }));
  place(15.8, 3.5, person({ vest: true, pose: 'point', face: -1.2 }));
}
function sStage2() {
  place(8, -2, b => {
    for (const x of [-4, 4]) b.cyl(0.2, 0.2, 5, [x, 2.5, 0], [0, 0, 0], 8);
    b.blk(-6, 5, -0.25, 12, 3.4, 0.5);
    b.label('高速公路', 'XingShu', 160, 1.6, [0, 6.35, 0.27]);
    b.label('EXPRESSWAY', 'Hand', 110, 0.9, [0, 5.35, 0.27], [0, 0, 0], { bold: true });
    b.line([V(3.4, 7.7, 0.27), V(5.2, 7.7, 0.27)], 'b'); b.line([V(4.7, 8.0, 0.27), V(5.25, 7.7, 0.27), V(4.7, 7.4, 0.27)], 'b');
  });
  place(8, 5, b => { b.line([V(-26, 0, -2.2), V(26, 0, -2.2)], 'b'); b.line([V(-26, 0, 2.2), V(26, 0, 2.2)], 'b'); for (let x = -25; x < 26; x += 3) b.seg(V(x, 0, 0), V(x + 1.5, 0, 0), 'b'); }, flat);
  place(1, 6, car());
  place(17, 4, car(), { ry: PI });
  place(-6.5, 5, flag('2010.10'));
}
function sOffice() {
  place(9, -8, b => {
    b.blk(-5, 1.2, -0.2, 10, 0.25, 0.4); b.blk(-5, 7.2, -0.2, 10, 0.25, 0.4);
    b.blk(-5.2, 1.2, -0.2, 0.25, 6.25, 0.4); b.blk(4.95, 1.2, -0.2, 0.25, 6.25, 0.4); b.blk(-0.1, 1.2, -0.15, 0.2, 6.2, 0.3);
    b.line([V(-4.8, 2.6, 0), V(-2, 3.4, 0), V(1, 3.0, 0), V(4.8, 3.8, 0)], 't');
    b.line([V(-4.8, 2.0, 0), V(-2, 2.8, 0), V(1, 2.4, 0), V(4.8, 3.2, 0)], 't');
    for (const [x, y] of [[-3, 4.2], [2.5, 5.8], [3.5, 4.5]]) { b.line([V(x - 0.4, y, 0), V(x, y + 1.1, 0), V(x + 0.4, y, 0)], 't', true); }
  });
  place(-1, -7.5, b => { b.cyl(1, 1, 0.2, [0, 5.5, 0], [PI / 2, 0, 0], 28); b.seg(V(0, 5.5, 0.12), V(0, 6.2, 0.12), 'n'); b.seg(V(0, 5.5, 0.12), V(0.45, 5.3, 0.12), 'n'); });
  // 办公桌 + 显示器 + 文件
  place(8, -1, b => {
    b.blk(-5, 1.35, -1.6, 10, 0.2, 3.2);
    for (const x of [-4.8, 4.5]) b.blk(x, 0, -1.4, 0.3, 1.35, 2.8);
    b.blk(1.5, 0.2, -1.4, 3.0, 1.15, 2.8); b.seg(V(1.5, 0.78, 1.41), V(4.5, 0.78, 1.41), 't');
    b.blk(-3.4, 1.55, -0.4, 0.2, 0.7, 0.2); b.box(2.6, 1.6, 0.15, [-3.3, 3.05, -0.4], [0, 0.35, 0]);
    b.blk(-0.9, 1.55, 0.5, 1.8, 0.08, 0.6);
    for (let i = 0; i < 6; i++) b.blk(1.4 + (i % 2) * 0.08, 1.55 + i * 0.22, -0.5, 1.6, 0.2, 1.3);
    for (let i = 0; i < 4; i++) b.blk(3.2 + (i % 2) * 0.06, 1.55 + i * 0.2, -0.4, 1.4, 0.18, 1.1);
  });
  place(8, -3.6, b => { person({ hat: false, tie: true, pose: 'sit' })(b); b.blk(-0.5, 0.95, -0.5, 1.0, 0.12, 1.0); b.blk(-0.5, 1.05, -0.6, 1.0, 1.3, 0.12); b.cyl(0.08, 0.08, 0.95, [0, 0.47, 0], [0, 0, 0], 6); }, { anim: 'drop' });
  place(15, 3, person({ hat: false, pose: 'hold', face: -1.1 }));
  place(-3, 4, b => { b.cyl(0.55, 0.42, 1.0, [0, 0.5, 0], [0, 0, 0], 12, { gen: 3 }); for (const a of [0, 1.2, 2.4, 3.6, 4.8]) b.line([V(0, 1, 0), V(Math.cos(a) * 0.6, 2.2, Math.sin(a) * 0.6), V(Math.cos(a) * 1.1, 2.8, Math.sin(a) * 1.1)], 'n'); });
}
function sGM() {
  place(7, -2, b => {
    b.blk(-12, 5.5, -2.5, 24, 1.2, 5);
    b.label('收费站  TOLL STATION', 'XingShu', 120, 1.0, [0, 5.75, 2.52]);
    for (let i = 0; i < 6; i++) { const x = -10 + i * 4; b.cyl(0.2, 0.2, 5.5, [x, 2.75, 0], [0, 0, 0], 8); b.blk(x - 0.55, 0, -1.3, 1.1, 2.2, 2.6); b.line([V(x - 0.35, 1.3, 1.31), V(x + 0.35, 1.3, 1.31), V(x + 0.35, 1.9, 1.31), V(x - 0.35, 1.9, 1.31)], 't', true); if (i < 5) b.beam(V(x + 0.6, 1.1, 1.4), V(x + 2.6, 1.1, 1.4), 0.08); }
  });
  place(7, 2, b => { for (let i = 0; i < 7; i++) b.line([V(-12 + i * 4, 0, -4), V(-12 + i * 4, 0, 8)], i === 0 || i === 6 ? 'b' : 't'); }, flat);
  place(-1, 3, car(), { ry: -PI / 2 });
  place(7, 5, car(), { ry: -PI / 2 });
  place(15, 1, truck(), { ry: -PI / 2 });
  place(23, -8, building(4, 11, 4, 3, 8));
  place(-5, 5.5, b => { b.blk(-1.6, 1.6, -0.1, 3.2, 2.4, 0.2); for (const x of [-1.2, 1.2]) b.beam(V(x, 0, 0), V(x, 1.6, 0), 0.08); b.line([V(-1.3, 2.0, 0.12), V(-0.6, 2.6, 0.12), V(0, 2.4, 0.12), V(0.7, 3.2, 0.12), V(1.3, 3.7, 0.12)], 'b'); b.line([V(1.0, 3.7, 0.12), V(1.35, 3.72, 0.12), V(1.3, 3.4, 0.12)], 'n'); });
  place(-2.3, 6, person({ hat: false, tie: true, pose: 'point', face: -0.9 }));
}
function sMaint() {
  place(8, -16, b => {
    b.blk(-24, 3.5, -1.5, 48, 0.5, 3);
    for (let x = -21; x < 24; x += 6) { b.cyl(0.3, 0.3, 3.5, [x, 1.75, 0], [0, 0, 0], 8); b.blk(x - 1.2, 3.2, -1.2, 2.4, 0.3, 2.4); }
  });
  place(8, 2, b => { b.line([V(-26, 0, -3), V(26, 0, -3)], 'b'); b.line([V(-26, 0, 3.5), V(26, 0, 3.5)], 'b'); for (let x = -25; x < 26; x += 3.5) b.seg(V(x, 0, 0.3), V(x + 1.6, 0, 0.3), 'b'); }, flat);
  place(0, 1.5, truck({ arrow: true }));
  for (let i = 0; i < 6; i++) place(5 + i * 1.6, 0.8 + i * 0.05, cone());
  place(15, 1.8, b => { b.arc(V(0, 0, 0), 2.0, 'xz', 0, 2 * PI, 'n', 24, 0.9); for (let x = -1.6; x < 1.6; x += 0.3) b.seg(V(x, 0, 0.5), V(x + 0.4, 0, -0.5), 't'); }, flat);
  place(13.5, 1.5, person({ vest: true, pose: 'hold', face: 0.8 }));
  place(16.5, 1.0, person({ vest: true, pose: 'raise', face: -0.8 }));
  place(20, 5, person({ pose: 'hold', face: -0.7 }));
}
function sStage3() {
  place(8, -2, shield(1.6));
  place(8, -2.5, b => { for (let i = 0; i < 9; i++) { const a = PI * 0.15 + i * PI * 0.7 / 8; b.seg(V(Math.cos(a) * 5.4, 3.6 + Math.sin(a) * 5.4, 0), V(Math.cos(a) * 6.4, 3.6 + Math.sin(a) * 6.4, 0), 'n'); } }, { anim: 'rise' });
  place(-6.5, 5, flag('2021.09'));
}
function sSafety() {
  place(17, -9, building(4, 12, 4, 3, 9));
  place(22, -7, building(4.5, 16, 4.5, 4, 12));
  place(27, -10, building(3.5, 9, 3.5, 3, 6));
  place(22, -7, b => { b.cyl(0.05, 0.05, 2, [0, 17, 0], [0, 0, 0], 6); b.extrude([[0, 0], [1, -0.3], [0, -0.6]], 0.04, [0, 18, 0]); }, { anim: 'drop', base: 0 });
  place(5, -3, b => {
    for (const x of [-3.2, 3.2]) b.beam(V(x, 0, 0), V(x, 1.8, 0), 0.12);
    b.blk(-4, 1.8, -0.15, 8, 4.2, 0.3);
    b.label('安全第一', 'XingShu', 200, 1.9, [0, 4.1, 0.17]);
    b.label('SAFETY FIRST', 'Hand', 120, 0.95, [0, 2.95, 0.17], [0, 0, 0], { bold: true });
  });
  place(10.5, 0.5, person({ pose: 'point', face: -1.0 }));
  for (let i = 0; i < 4; i++) place(-1 + i * 2.1, 4 + (i % 2) * 0.6, person({ vest: true, face: PI + 0.1 * (i - 1.5) }));
  place(13.5, 3.5, b => { b.cyl(0.35, 0.35, 1.3, [0, 0.65, 0], [0, 0, 0], 12, { gen: 2 }); b.cyl(0.12, 0.12, 0.3, [0, 1.45, 0], [0, 0, 0], 8); b.line([V(0, 1.6, 0), V(0.4, 1.7, 0), V(0.7, 1.2, 0.1)], 'n'); });
  place(15.5, 3.5, b => { b.box(1.8, 2.4, 0.12, [0, 1.3, 0], [-0.25, 0, 0]); for (let i = 0; i < 3; i++) { const y = 2.0 - i * 0.55; b.line([V(-0.6, y, 0.25), V(-0.45, y - 0.15, 0.25), V(-0.2, y + 0.2, 0.25)], 'b'); b.seg(V(0, y, 0.25), V(0.7, y, 0.25), 't'); } });
}
function sOutro() {
  place(10, 0, b => roadAlongZ(b, -3, 3, 9, -44), flat);
  place(10, -38, b => { b.arc(V(0, 0, 0), 7, 'xy', 0, PI, 'b', 40); for (let i = 0; i < 11; i++) { const a = PI * (i + 0.5) / 11; b.seg(V(Math.cos(a) * 8.5, Math.sin(a) * 8.5, 0), V(Math.cos(a) * 10.5, Math.sin(a) * 10.5, 0), 'n'); } }, { anim: 'rise' });
  place(-6, -30, mountain(12, 8, 11, 0.5));
  place(28, -32, mountain(14, 10, 12, 0.5));
  for (const [x, z, s] of [[4, -6, 1], [16, -4, 1.2], [3, -16, 0.9], [17.5, -18, 0.9]]) place(x, z, pine(s));
  place(11.2, 3, person({ pose: 'walk', face: PI }));
  place(-6.5, 5, flag('至今 Now'));
}

// ---------------------------------------------------------------- 标题文字卡：纸面上书写，同时像立体书一样翻起
const cards = [];
function titleCard(cx, sc, t0, o = {}) {
  const pivot = new THREE.Group();
  pivot.position.set(cx + (o.x ?? -14.5), 0.03, o.z ?? -6);
  scene.add(pivot);
  const k = sc.big ? 1.35 : sc.kind === 'stage' ? 1.15 : 1;
  const lines = o.lines ?? [
    { text: sc.zh, font: 'XingShu', px: 170, h: 2.3 * k, y: 3.2 * k, dur: Math.min(2.0, 0.5 + sc.zh.length * 0.13) },
    { text: sc.en, font: 'Hand', px: 120, h: 1.25 * k, y: 1.95 * k, bold: true, dur: 1.0 },
    { text: sc.sub, font: 'Hand', px: 90, h: 0.9 * k, y: 1.0 * k, bold: sc.kind === 'stage', dur: 0.9 },
  ];
  const items = [];
  let t = t0 + 0.5;
  for (const L of lines) {
    const m = textMesh(L.text, L.font, L.px, L.h, { bold: L.bold });
    m.position.y = L.y; pivot.add(m);
    items.push({ m, start: L.at ?? t, dur: L.dur });
    t = (L.at ?? t) + L.dur * 0.85;
  }
  // 立体书式的纸卡：挡住身后的线条，带一圈细边框
  const cw = Math.max(...items.map(it => it.m.userData.w), o.ul ?? 0) + 1.2;
  const ch = Math.max(...lines.map(L => L.y + L.h * 0.75)) + 0.5;
  const back = new THREE.Mesh(new THREE.PlaneGeometry(cw, ch), new THREE.MeshBasicMaterial({ color: 0xf8f4ea, side: THREE.DoubleSide }));
  back.position.set(cw / 2 - 0.6, ch / 2, -0.03); pivot.add(back);
  const ul = new Obj();
  ul.line([V(-0.6, 0, 0), V(cw - 0.6, 0, 0), V(cw - 0.6, ch, 0), V(-0.6, ch, 0)], 't', true);
  ul.seg(V(0, 0.5 * k, 0.01), V(o.ul ?? 9 * k, 0.5 * k, 0.01), 'n'); ul.finish();
  ul.pivot.position.set(0, 0, 0); ul.inner.position.set(0, 0, 0); pivot.add(ul.pivot);
  cards.push({ pivot, items, t0: t0 + 0.4, ul, ulStart: t, });
}

// ---------------------------------------------------------------- 时间轴
let timeline;
function buildTimeline() {
  timeline = new Obj();
  timeline.seg(V(-22, 0, 0), V(SP * (SCENES.length - 1) - 22, 0, 0), 't');
  for (let i = 0; i < SCENES.length - 1; i++) timeline.arc(V(SP * i - 16, 0, 0), 0.25, 'xz', 0, 2 * PI, 't', 10);
  timeline.finish();
  timeline.pivot.position.set(0, 0.02, 7 + 0.0);
  timeline.inner.position.z = 0; timeline.pivot.position.z = 7;
  scene.add(timeline.pivot);
}

// ---------------------------------------------------------------- 构建 + 时间编排
let sceneStart = [], total = 0, objs = [], pops = [];
window.build = async function () {
  await document.fonts.load('72px XingShu', '我的职业历程');
  await document.fonts.load('bold 40px Hand', 'Career');
  await document.fonts.ready;
  let t0 = 0;
  buildTimeline();
  SCENES.forEach((sc, i) => {
    sceneStart.push(t0);
    S = { cx: i * SP, objs: [] };
    sc.draw();
    if (sc.zh) titleCard(S.cx, sc, t0);
    const drawStart = t0 + (i === 0 ? 0.5 : 0.8);
    const win = sc.dur * (sc.id === 'outro' ? 0.4 : 0.62);
    const wsum = S.objs.reduce((a, o) => a + Math.sqrt(o.total), 0);
    let tt = drawStart;
    for (const o of S.objs) {
      const dur = Math.max(0.3, Math.sqrt(o.total) / wsum * win);
      o.start = tt; o.dur = dur;
      o.popStart = tt + dur * 0.45; o.popDur = 0.95;
      if (!['flat', 'plain'].includes(o.o.anim)) pops.push(+o.popStart.toFixed(3));
      tt += dur * 0.8;
      objs.push(o);
    }
    t0 += sc.dur;
  });
  const oi = SCENES.length - 1;
  titleCard(oi * SP, {}, sceneStart[oi], {
    x: -15, z: -5, ul: 15, lines: [
      { text: '筑路 · 管路 · 守平安', font: 'XingShu', px: 170, h: 2.8, y: 5.6, dur: 2.2, at: sceneStart[oi] + 0.6 },
      { text: 'Building roads · Running roads · Safeguarding lives', font: 'Hand', px: 110, h: 1.2, y: 4.4, bold: true, dur: 1.8, at: sceneStart[oi] + 2.8 },
      { text: '路在脚下，未完待续', font: 'XingShu', px: 150, h: 1.9, y: 2.4, dur: 1.6, at: sceneStart[oi] + 5.0 },
      { text: 'The road goes on — to be continued.', font: 'Hand', px: 100, h: 1.05, y: 1.2, bold: true, dur: 1.4, at: sceneStart[oi] + 6.6 },
    ],
  });
  total = t0;
  return { total, scenes: SCENES.map((s, i) => ({ id: s.id, start: sceneStart[i], dur: s.dur })) };
};

// ---------------------------------------------------------------- 渲染
const clamp = x => Math.max(0, Math.min(1, x));
const ease = x => x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const outBack = x => { const c1 = 1.5, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };

function camAt(t) {
  let k = 0;
  for (let i = 0; i < sceneStart.length; i++) if (t >= sceneStart[i]) k = i;
  const u = ease(clamp((t - sceneStart[k]) / 1.6));
  const x = k === 0 ? 0 : (k - 1 + u) * SP;
  const yaw = 0.06 * Math.sin(t * 2 * PI / 17);
  const target = V(x + 3, 2.6, -4);
  const off = CAM_OFF.clone().applyAxisAngle(V(0, 1, 0), yaw);
  camera.position.copy(target).add(off);
  camera.lookAt(target);
  return x;
}

window.penActivity = t => objs.some(o => t >= o.start && t < o.start + o.dur) ? 1 : 0;
window.pops = () => pops;

window.renderAt = function (t) {
  const camX = camAt(t);
  // 时间轴随镜头推进
  timeline.reveal(Math.floor(timeline.total * clamp((camX + 21 + 22) / (SP * (SCENES.length - 1)))));
  for (const o of objs) {
    const p = clamp((t - o.start) / o.dur);
    o.pivot.visible = p > 0;
    if (p <= 0) continue;
    o.reveal(Math.ceil(o.total * p));
    const anim = o.o.anim;
    const q = clamp((t - o.popStart) / o.popDur);
    for (const l of o.labels) { l.userData.mesh.material.opacity = clamp((p - 0.5) * 3); }
    if (anim === 'flat' || anim === 'plain') { o.pivot.rotation.x = 0; continue; }
    if (anim === 'drop' || anim === 'rise') {
      // 从纸面上方落下 / 从纸下升起
      const e = outBack(clamp(q * 1.1));
      o.inner.position.y = anim === 'drop' ? (1 - e) * 4 : -(1 - e) * 6;
      o.pivot.rotation.x = 0;
      o.pivot.scale.setScalar(anim === 'drop' ? 0.6 + 0.4 * clamp(q * 2) : 1);
      continue;
    }
    // 铰链翻起 + 一跃
    const e = outBack(q);
    o.pivot.rotation.x = -PI / 2 * (1 - e);
    o.pivot.position.y = 0.02 + Math.sin(PI * clamp(q * 1.15)) * 0.9 + (o.o.base ?? 0);
  }
  for (const c of cards) {
    const q = clamp((t - c.t0) / 1.0);
    c.pivot.rotation.x = -PI / 2 + (PI / 2 - ELEV) * outBack(q);
    c.pivot.position.y = 0.03 + Math.sin(PI * q) * 0.6;
    for (const it of c.items) {
      const p = clamp((t - it.start) / it.dur), m = it.m.userData.mesh;
      m.visible = p > 0;
      m.scale.x = Math.max(p, 1e-4);
      m.material.map.repeat.x = Math.max(p, 1e-4);
    }
    c.ul.reveal(Math.ceil(c.ul.total * clamp((t - c.t0) / 1.2)));
  }
  document.getElementById('fade').style.opacity = clamp((t - (total - 1.2)) / 1.2);
  renderer.render(scene, camera);
};
window.ready = true;
