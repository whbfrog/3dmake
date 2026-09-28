// 手绘线条履历动画：所有画面都是 rough.js 生成的素描线条，按时间逐笔“长”出来。
// 页面暴露 window.build() 与 window.renderAt(t)，由 render.mjs 逐帧截图。
'use strict';

const NS = 'http://www.w3.org/2000/svg';
const W = 1920, H = 1080;
const INK = '#2a2723';
const PI = Math.PI;
const gen = rough.generator();
let seed = 1;

// ---------------------------------------------------------------- 分镜
// dur：本段时长（秒）；kind：stage 为阶段标题页，role 为岗位页
const SCENES = [
  { id: 'intro', dur: 8.5, draw: sIntro,
    zh: '我的职业历程', en: 'My Career Journey', sub: '1995 — 至今  ·  Thirty Years on the Road', big: true },
  { id: 'stage1', dur: 5, draw: sStage1, kind: 'stage',
    zh: '第一阶段 · 工程建设', en: 'Stage I · Engineering Construction', sub: '1995.07 — 2010.10' },
  { id: 'subgrade', dur: 8.5, draw: sSubgrade,
    zh: '路基路面专业工程师', en: 'Subgrade & Pavement Engineer', sub: '某高速公路  ·  Expressway Project' },
  { id: 'bridge', dur: 8.5, draw: sBridge,
    zh: '桥梁工程师', en: 'Bridge Engineer', sub: '某钢管拱特大桥  ·  Steel-Tube Arch Super Bridge' },
  { id: 'asphalt', dur: 8.5, draw: sAsphalt,
    zh: '沥青路面项目经理', en: 'Project Manager, Asphalt Pavement', sub: '某高速公路  ·  Expressway Project' },
  { id: 'tunnel', dur: 8.5, draw: sTunnel,
    zh: '特长隧道项目总工', en: 'Chief Engineer, Extra-Long Tunnel', sub: '某高速公路  ·  Expressway Project' },
  { id: 'stage2', dur: 5, draw: sStage2, kind: 'stage',
    zh: '第二阶段 · 运营管理', en: 'Stage II · Operations Management', sub: '2010.10 — 2021.09' },
  { id: 'office', dur: 8, draw: sOffice,
    zh: '办公室主任', en: 'Director of General Office', sub: '某高速公路运营公司  ·  Expressway Operations' },
  { id: 'gm', dur: 8.5, draw: sGM,
    zh: '公司总经理', en: 'General Manager', sub: '某高速公路运营公司  ·  Expressway Operations' },
  { id: 'maint', dur: 8.5, draw: sMaint,
    zh: '工程部经理', en: 'Manager, Engineering Department', sub: '某高速公路运营公司  ·  Expressway Operations' },
  { id: 'stage3', dur: 5, draw: sStage3, kind: 'stage',
    zh: '第三阶段 · 安全管理', en: 'Stage III · Safety Management', sub: '2021.09 — 至今 Present' },
  { id: 'safety', dur: 11, draw: sSafety,
    zh: '安全部负责人', en: 'Head of Safety Department', sub: '某上市集团  ·  A Listed Group' },
  { id: 'outro', dur: 12, draw: sOutro },
];

// ---------------------------------------------------------------- 基础笔触
// 每个 shape 由若干 path 组成；按加入顺序依次绘制
let cur = null; // 当前场景收集器
function opts(o = {}) {
  return {
    seed: seed++, stroke: INK, strokeWidth: o.w ?? 2.4, roughness: o.r ?? 1.1, bowing: o.b ?? 1,
    fill: o.hach ? INK : undefined, fillStyle: o.fs ?? 'hachure', fillWeight: o.fw ?? 1,
    hachureGap: o.gap ?? 9, hachureAngle: o.ang ?? -41, disableMultiStroke: o.single ?? false,
    curveStepCount: 12, preserveVertices: false,
  };
}
function add(drawable, o = {}) {
  for (const p of gen.toPaths(drawable)) {
    cur.shapes.push({ d: p.d, w: p.strokeWidth, weight: o.weight ?? 1, alpha: o.alpha ?? 1, fill: p.fill && p.fill !== 'none' });
  }
}
const L = (x1, y1, x2, y2, o) => add(gen.line(x1, y1, x2, y2, opts(o)), o);
const P = (pts, o) => add(gen.linearPath(pts, opts(o)), o);
const G = (pts, o) => add(gen.polygon(pts, opts(o)), o);
const R = (x, y, w, h, o) => add(gen.rectangle(x, y, w, h, opts(o)), o);
const C = (cx, cy, d, o) => add(gen.circle(cx, cy, d, opts(o)), o);
const E = (cx, cy, w, h, o) => add(gen.ellipse(cx, cy, w, h, opts(o)), o);
const A = (cx, cy, w, h, a0, a1, o) => add(gen.arc(cx, cy, w, h, a0, a1, false, opts(o)), o);
const Q = (pts, o) => add(gen.curve(pts, opts(o)), o);
const D = (d, o) => add(gen.path(d, opts(o)), o);
// 纯手写细节（不经 rough，适合短小笔画）
const S = (d, o = {}) => cur.shapes.push({ d, w: o.w ?? 2, weight: o.weight ?? 1, alpha: o.alpha ?? 1 });
function T(x, y, text, o = {}) { // 场景内的小字
  cur.shapes.push({ text, x, y, size: o.size ?? 30, font: o.font ?? 'Hand', anchor: o.anchor ?? 'start', weight: o.weight ?? 1, bold: o.bold });
}

// ---------------------------------------------------------------- 组件
function person(x, y, s = 1, o = {}) {
  const f = o.face ?? 1;
  const hy = y - 150 * s, sh = y - 122 * s, hip = y - 72 * s;
  C(x, hy, 27 * s, { w: 2.2 });
  if (o.hat !== false) {
    A(x, hy - 3 * s, 34 * s, 32 * s, PI, 2 * PI, { w: 2.2 });
    L(x - 21 * s, hy - 3 * s, x + 22 * s, hy - 3 * s, { w: 2.2 });
    L(x, hy - 19 * s, x, hy - 8 * s, { w: 1.6, single: true });
  } else {
    A(x, hy - 2 * s, 29 * s, 26 * s, PI * 1.05, PI * 1.95, { w: 2 }); // 发际
  }
  // 躯干（外套）
  G([[x - 17 * s, sh], [x + 17 * s, sh], [x + 14 * s, hip + 4 * s], [x - 14 * s, hip + 4 * s]], { w: 2.2 });
  if (o.vest) { L(x - 7 * s, sh + 2 * s, x - 7 * s, hip, { w: 1.5, single: true }); L(x + 7 * s, sh + 2 * s, x + 7 * s, hip, { w: 1.5, single: true }); L(x - 14 * s, sh + 30 * s, x + 14 * s, sh + 30 * s, { w: 1.5, single: true }); }
  if (o.tie) { P([[x - 4 * s, sh], [x, sh + 6 * s], [x + 4 * s, sh]], { w: 1.6 }); P([[x, sh + 6 * s], [x - 3 * s, sh + 30 * s], [x, sh + 36 * s], [x + 3 * s, sh + 30 * s], [x, sh + 6 * s]], { w: 1.5, single: true }); }
  // 腿
  if (o.pose === 'sit') {
    P([[x - 8 * s, hip + 4 * s], [x + 38 * f * s, hip + 6 * s], [x + 40 * f * s, y]], { w: 2.6 });
    P([[x + 6 * s, hip + 4 * s], [x + 48 * f * s, hip + 8 * s], [x + 52 * f * s, y]], { w: 2.6 });
  } else {
    const sp = o.pose === 'walk' ? 24 : 11;
    P([[x - 7 * s, hip + 4 * s], [x - sp * s, y - 2 * s], [x - (sp + 10 * f) * s, y]], { w: 2.6 });
    P([[x + 7 * s, hip + 4 * s], [x + sp * s, y - 2 * s], [x + (sp + 10 * f) * s, y]], { w: 2.6 });
  }
  // 手臂
  const back = [[x - 15 * f * s, sh + 4 * s], [x - 22 * f * s, sh + 30 * s], [x - 20 * f * s, sh + 54 * s]];
  if (o.pose === 'point') {
    P(back, { w: 2.4 });
    P([[x + 15 * f * s, sh + 4 * s], [x + 42 * f * s, sh - 6 * s], [x + 70 * f * s, sh - 22 * s]], { w: 2.4 });
  } else if (o.pose === 'hold' || o.pose === 'sit') {
    P([[x - 12 * f * s, sh + 4 * s], [x + 2 * f * s, sh + 34 * s], [x + 30 * f * s, sh + 40 * s]], { w: 2.4 });
    P([[x + 15 * f * s, sh + 4 * s], [x + 24 * f * s, sh + 30 * s], [x + 40 * f * s, sh + 36 * s]], { w: 2.4 });
    if (o.pose === 'hold') G([[x + 26 * f * s, sh + 18 * s], [x + 56 * f * s, sh + 10 * s], [x + 60 * f * s, sh + 50 * s], [x + 30 * f * s, sh + 58 * s]], { w: 1.8 });
  } else if (o.pose === 'raise') {
    P(back, { w: 2.4 });
    P([[x + 15 * f * s, sh + 4 * s], [x + 30 * f * s, sh - 20 * s], [x + 36 * f * s, sh - 50 * s]], { w: 2.4 });
  } else {
    P(back, { w: 2.4 });
    P([[x + 15 * f * s, sh + 4 * s], [x + 22 * f * s, sh + 30 * s], [x + 20 * f * s, sh + 54 * s]], { w: 2.4 });
  }
}
function wheel(x, y, d) { C(x, y, d, { w: 2.2 }); C(x, y, d * 0.38, { w: 1.6 }); }
function roller(x, y, s = 1, f = 1) {
  const X = v => x + v * s * f;
  wheel(X(80), y - 38 * s, 76 * s);
  wheel(X(-70), y - 30 * s, 60 * s);
  G([[X(-100), y - 50 * s], [X(40), y - 50 * s], [X(60), y - 78 * s], [X(115), y - 78 * s], [X(118), y - 40 * s], [X(40), y - 30 * s], [X(-100), y - 30 * s]], { w: 2.2 });
  R(Math.min(X(-80), X(-10)), y - 140 * s, 70 * s, 90 * s, { w: 2.2 });
  R(Math.min(X(-72), X(-18)), y - 132 * s, 54 * s, 40 * s, { w: 1.6 });
  L(X(-90), y - 142 * s, X(0), y - 142 * s, { w: 2.4 });
}
function excavator(x, y, s = 1, f = 1) {
  const X = v => x + v * s * f;
  D(`M ${X(-90)} ${y - 10 * s} Q ${X(-100)} ${y - 36 * s} ${X(-78)} ${y - 40 * s} L ${X(60)} ${y - 40 * s} Q ${X(80)} ${y - 36 * s} ${X(70)} ${y - 8 * s} Z`, { w: 2.3 });
  for (let i = 0; i < 5; i++) C(X(-70 + i * 34), y - 22 * s, 20 * s, { w: 1.5, single: true });
  G([[X(-80), y - 40 * s], [X(-80), y - 92 * s], [X(10), y - 92 * s], [X(30), y - 60 * s], [X(30), y - 40 * s]], { w: 2.3 });
  R(Math.min(X(-30), X(8)), y - 134 * s, 38 * s, 42 * s, { w: 2 });
  P([[X(10), y - 84 * s], [X(95), y - 190 * s], [X(170), y - 120 * s]], { w: 3 });
  P([[X(22), y - 72 * s], [X(100), y - 172 * s], [X(158), y - 112 * s]], { w: 2 });
  G([[X(160), y - 125 * s], [X(195), y - 110 * s], [X(185), y - 70 * s], [X(150), y - 80 * s]], { w: 2.2 });
  for (let i = 0; i < 3; i++) L(X(162 + i * 10), y - 72 * s, X(158 + i * 10), y - 62 * s, { w: 1.6, single: true });
}
function paver(x, y, s = 1, f = 1) {
  const X = v => x + v * s * f;
  G([[X(90), y - 70 * s], [X(150), y - 100 * s], [X(150), y - 40 * s], [X(90), y - 30 * s]], { w: 2.2 }); // 料斗
  R(Math.min(X(-60), X(90)), y - 90 * s, 150 * s, 62 * s, { w: 2.3 });
  wheel(X(60), y - 20 * s, 40 * s); wheel(X(-20), y - 20 * s, 40 * s);
  R(Math.min(X(-120), X(-60)), y - 40 * s, 60 * s, 26 * s, { w: 2 }); // 熨平板
  L(X(-50), y - 90 * s, X(-50), y - 160 * s, { w: 2 }); L(X(40), y - 90 * s, X(40), y - 160 * s, { w: 2 });
  L(X(-70), y - 160 * s, X(60), y - 164 * s, { w: 2.6 });
  C(X(-5), y - 118 * s, 24 * s, { w: 1.8 }); // 司机头
  for (let i = 0; i < 3; i++) Q([[X(-90 + i * 26), y - 50 * s], [X(-96 + i * 26), y - 80 * s], [X(-84 + i * 26), y - 110 * s], [X(-92 + i * 26), y - 136 * s]], { w: 1.4, single: true, r: 0.6 });
}
function car(x, y, s = 1, f = 1) {
  const X = v => x + v * s * f;
  D(`M ${X(-80)} ${y - 20 * s} L ${X(-80)} ${y - 42 * s} Q ${X(-70)} ${y - 50 * s} ${X(-44)} ${y - 52 * s} L ${X(-24)} ${y - 76 * s} L ${X(30)} ${y - 76 * s} L ${X(56)} ${y - 50 * s} Q ${X(82)} ${y - 46 * s} ${X(84)} ${y - 30 * s} L ${X(84)} ${y - 20 * s} Z`, { w: 2.2 });
  L(X(2), y - 74 * s, X(2), y - 52 * s, { w: 1.6, single: true });
  wheel(X(-48), y - 18 * s, 34 * s); wheel(X(52), y - 18 * s, 34 * s);
}
function truck(x, y, s = 1, f = 1, arrow = false) {
  const X = v => x + v * s * f;
  G([[X(60), y - 30 * s], [X(60), y - 110 * s], [X(100), y - 110 * s], [X(128), y - 70 * s], [X(128), y - 30 * s]], { w: 2.3 });
  G([[X(70), y - 100 * s], [X(96), y - 100 * s], [X(116), y - 72 * s], [X(70), y - 72 * s]], { w: 1.6 });
  R(Math.min(X(-130), X(55)), y - 70 * s, 185 * s, 40 * s, { w: 2.3 });
  wheel(X(-90), y - 22 * s, 38 * s); wheel(X(90), y - 22 * s, 38 * s);
  if (arrow) {
    L(X(-60), y - 70 * s, X(-60), y - 110 * s, { w: 2 });
    R(Math.min(X(-120), X(0)), y - 170 * s, 120 * s, 60 * s, { w: 2.3 });
    P([[X(-100), y - 140 * s], [X(-30), y - 140 * s]], { w: 3 });
    P([[X(-48), y - 156 * s], [X(-26), y - 140 * s], [X(-48), y - 124 * s]], { w: 3 });
    for (let i = 0; i < 3; i++) C(X(-108 + i * 44), y - 162 * s, 6 * s, { w: 1.4, single: true });
  }
}
function cone(x, y, s = 1) {
  G([[x - 16 * s, y], [x + 16 * s, y], [x + 4 * s, y - 50 * s], [x - 4 * s, y - 50 * s]], { w: 2 });
  L(x - 11 * s, y - 16 * s, x + 11 * s, y - 16 * s, { w: 1.6, single: true });
  L(x - 8 * s, y - 30 * s, x + 8 * s, y - 30 * s, { w: 1.6, single: true });
  L(x - 22 * s, y, x + 22 * s, y, { w: 2 });
}
function tree(x, y, s = 1) {
  L(x, y, x, y - 60 * s, { w: 2.2 });
  Q([[x - 6 * s, y - 50 * s], [x - 38 * s, y - 70 * s], [x - 30 * s, y - 110 * s], [x - 8 * s, y - 132 * s], [x + 22 * s, y - 120 * s], [x + 36 * s, y - 88 * s], [x + 24 * s, y - 60 * s], [x + 4 * s, y - 56 * s]], { w: 2, r: 1.4 });
}
function pine(x, y, s = 1) {
  L(x, y, x, y - 22 * s, { w: 2 });
  P([[x - 30 * s, y - 22 * s], [x, y - 80 * s], [x + 30 * s, y - 22 * s]], { w: 2 });
  P([[x - 22 * s, y - 50 * s], [x, y - 100 * s], [x + 22 * s, y - 50 * s]], { w: 2 });
}
function cloud(x, y, s = 1) {
  D(`M ${x - 60 * s} ${y} Q ${x - 70 * s} ${y - 26 * s} ${x - 38 * s} ${y - 28 * s} Q ${x - 30 * s} ${y - 56 * s} ${x} ${y - 48 * s} Q ${x + 24 * s} ${y - 66 * s} ${x + 44 * s} ${y - 36 * s} Q ${x + 76 * s} ${y - 32 * s} ${x + 66 * s} ${y} Z`, { w: 1.8, r: 0.8 });
}
function sun(x, y, r) {
  C(x, y, r * 2, { w: 2 });
  for (let i = 0; i < 10; i++) {
    const a = i / 10 * 2 * PI;
    L(x + Math.cos(a) * r * 1.3, y + Math.sin(a) * r * 1.3, x + Math.cos(a) * r * 1.65, y + Math.sin(a) * r * 1.65, { w: 1.6, single: true });
  }
}
function birds(x, y, n = 3) {
  for (let i = 0; i < n; i++) {
    const bx = x + i * 46, by = y + (i % 2) * 18;
    S(`M ${bx - 14} ${by} Q ${bx - 7} ${by - 9} ${bx} ${by} Q ${bx + 7} ${by - 9} ${bx + 14} ${by}`, { w: 1.8 });
  }
}
function tripod(x, y, s = 1) { // 水准仪 / 全站仪
  L(x, y - 90 * s, x - 26 * s, y, { w: 2 }); L(x, y - 90 * s, x + 26 * s, y, { w: 2 }); L(x, y - 90 * s, x + 4 * s, y, { w: 2 });
  R(x - 22 * s, y - 112 * s, 44 * s, 20 * s, { w: 2 });
  C(x + 26 * s, y - 102 * s, 10 * s, { w: 1.6 });
  L(x - 22 * s, y - 102 * s, x - 34 * s, y - 102 * s, { w: 2 });
}
function towerCrane(x, y, h, s = 1) {
  L(x - 14 * s, y, x - 14 * s, y - h, { w: 2.2 }); L(x + 14 * s, y, x + 14 * s, y - h, { w: 2.2 });
  const n = Math.floor(h / (40 * s));
  const pts = [];
  for (let i = 0; i <= n; i++) pts.push([i % 2 ? x + 14 * s : x - 14 * s, y - i * h / n]);
  P(pts, { w: 1.4, single: true });
  L(x - 90 * s, y - h, x + 260 * s, y - h, { w: 2.4 });
  L(x - 90 * s, y - h + 16 * s, x + 260 * s, y - h + 10 * s, { w: 1.6 });
  P([[x - 80 * s, y - h], [x, y - h - 50 * s], [x + 250 * s, y - h]], { w: 1.6 });
  R(x - 90 * s, y - h + 12 * s, 36 * s, 26 * s, { w: 2 });
  L(x + 200 * s, y - h + 10 * s, x + 200 * s, y - h + 120 * s, { w: 1.4, single: true });
  P([[x + 192 * s, y - h + 120 * s], [x + 200 * s, y - h + 132 * s], [x + 208 * s, y - h + 120 * s]], { w: 1.8 });
}
function building(x, y, w, h, cols, rows) {
  R(x, y - h, w, h, { w: 2.3 });
  const cw = w / cols, rh = Math.min(h / rows, 60);
  for (let r = 0; r < rows && (r + 1) * rh < h - 20; r++)
    for (let c = 0; c < cols; c++) R(x + c * cw + cw * 0.25, y - h + 20 + r * rh, cw * 0.5, rh * 0.55, { w: 1.3, single: true, r: 0.6 });
}
function shield(x, y, s = 1, check = true) {
  D(`M ${x} ${y - 90 * s} Q ${x + 40 * s} ${y - 70 * s} ${x + 70 * s} ${y - 72 * s} Q ${x + 74 * s} ${y + 10 * s} ${x} ${y + 60 * s} Q ${x - 74 * s} ${y + 10 * s} ${x - 70 * s} ${y - 72 * s} Q ${x - 40 * s} ${y - 70 * s} ${x} ${y - 90 * s} Z`, { w: 3 });
  D(`M ${x} ${y - 72 * s} Q ${x + 32 * s} ${y - 56 * s} ${x + 54 * s} ${y - 58 * s} Q ${x + 56 * s} ${y + 2 * s} ${x} ${y + 42 * s} Q ${x - 56 * s} ${y + 2 * s} ${x - 54 * s} ${y - 58 * s} Q ${x - 32 * s} ${y - 56 * s} ${x} ${y - 72 * s} Z`, { w: 1.6 });
  if (check) P([[x - 26 * s, y - 12 * s], [x - 6 * s, y + 10 * s], [x + 30 * s, y - 34 * s]], { w: 5, r: 0.8 });
}
function helmet(x, y, s = 1) { // 大号安全帽
  D(`M ${x - 110 * s} ${y} Q ${x - 110 * s} ${y - 120 * s} ${x} ${y - 124 * s} Q ${x + 110 * s} ${y - 120 * s} ${x + 110 * s} ${y} Z`, { w: 3 });
  D(`M ${x - 150 * s} ${y + 4 * s} Q ${x} ${y - 16 * s} ${x + 160 * s} ${y + 6 * s} Q ${x + 170 * s} ${y + 22 * s} ${x + 140 * s} ${y + 24 * s} L ${x - 140 * s} ${y + 22 * s} Q ${x - 160 * s} ${y + 20 * s} ${x - 150 * s} ${y + 4 * s} Z`, { w: 3 });
  D(`M ${x - 22 * s} ${y - 2 * s} L ${x - 20 * s} ${y - 118 * s} Q ${x} ${y - 128 * s} ${x + 20 * s} ${y - 118 * s} L ${x + 22 * s} ${y - 2 * s}`, { w: 2 });
  A(x, y - 4 * s, 170 * s, 190 * s, PI * 1.12, PI * 1.36, { w: 1.4, single: true });
}
function clipboard(x, y, s = 1, ticks = 4) {
  R(x, y, 150 * s, 200 * s, { w: 2.4 });
  R(x + 45 * s, y - 12 * s, 60 * s, 26 * s, { w: 2 });
  for (let i = 0; i < ticks; i++) {
    const yy = y + 50 * s + i * 38 * s;
    R(x + 18 * s, yy - 12 * s, 20 * s, 20 * s, { w: 1.6 });
    L(x + 50 * s, yy, x + 130 * s, yy, { w: 1.6 });
    P([[x + 20 * s, yy - 4 * s], [x + 28 * s, yy + 6 * s], [x + 42 * s, yy - 18 * s]], { w: 2.6 });
  }
}
function timelineTick(x, label, big) {
  L(x, 985 - (big ? 26 : 12), x, 985 + (big ? 26 : 12), { w: big ? 3 : 2 });
  if (big) C(x, 985, 22, { w: 2.2 });
  if (label) T(x, 1045, label, { size: 36, anchor: 'middle', font: 'Hand', bold: true });
}

// ---------------------------------------------------------------- 各场景
function sIntro() {
  // 远山 + 太阳 + 伸向远方的公路
  Q([[860, 640], [1000, 520], [1100, 560], [1230, 450], [1360, 540], [1480, 480], [1640, 600], [1820, 580]], { w: 2 });
  Q([[980, 640], [1120, 600], [1260, 620], [1400, 590], [1540, 640]], { w: 1.6 });
  sun(1500, 330, 52);
  cloud(1180, 300, 1.1); cloud(1720, 220, 0.8);
  birds(1260, 380);
  // 公路：透视
  L(1260, 640, 760, 960, { w: 2.8 }); L(1300, 640, 1860, 960, { w: 2.8 });
  L(700, 640, 1860, 640, { w: 1.8, r: 0.6 });
  for (let i = 0; i < 6; i++) { const t = i / 6, t2 = t + 0.07; const y1 = 650 + Math.pow(t, 1.6) * 300, y2 = 650 + Math.pow(t2, 1.6) * 300; L(1280 + (1310 - 1280) * t, y1, 1280 + (1310 - 1280) * t2, y2, { w: 2 + t * 4, single: true }); }
  tree(820, 700, 0.9); tree(700, 760, 1.2); pine(1760, 700, 0.8); pine(1840, 740, 1);
  timelineTick(160, '', true);
}
function stageCard(icon, tickLabel) {
  icon();
  timelineTick(200, tickLabel, true);
}
function sStage1() {
  stageCard(() => {
    helmet(1320, 640, 1.5);
    // 图纸卷 + 丁字尺
    R(900, 760, 520, 80, { w: 2.2, r: 0.8 }); E(900, 800, 40, 80, { w: 2 }); E(1420, 800, 40, 80, { w: 2 });
    for (let i = 0; i < 4; i++) L(960 + i * 110, 780, 1040 + i * 110, 780 + (i % 2) * 40, { w: 1.2, single: true });
    L(1480, 860, 1860, 700, { w: 2.6 }); L(1840, 680, 1880, 740, { w: 2.6 });
  }, '1995.07');
}
function sSubgrade() {
  // 路基横断面：分层的梯形路堤
  const gy = 900;
  L(40, gy, 1880, gy, { w: 2.4 });
  G([[440, gy], [760, 620], [1360, 620], [1680, gy]], { w: 2.8 });
  P([[554, gy - 100], [1566, gy - 100]], { w: 1.2, single: true, r: 0.6, alpha: 0.7 });
  P([[657, gy - 190], [1463, gy - 190]], { w: 1.2, single: true, r: 0.6, alpha: 0.7 });
  // 路面结构层
  R(760, 580, 600, 40, { w: 2.2 }); R(780, 552, 560, 28, { w: 2 }); R(800, 530, 520, 22, { w: 2.4, hach: true, gap: 6, fw: 0.9 });
  T(1380, 548, '面层 surface', { size: 26, font: 'Hand' });
  T(1380, 598, '基层 base', { size: 26, font: 'Hand' });
  T(1470, 740, '路基 subgrade', { size: 26, font: 'Hand' });
  // 挖掘机、压路机、测量工程师
  excavator(220, gy, 1.15, 1);
  roller(1080, 530, 0.9, -1);
  tripod(1730, gy, 1.1);
  person(1830, gy, 1.1, { pose: 'hold', face: -1 });
  person(1290, 530, 0.85, { vest: true, pose: 'point', face: -1 });
  cloud(1500, 250, 0.9); birds(1700, 330);
  timelineTick(300, '', false);
}
function sBridge() {
  const deck = 650, water = 820;
  // 两岸
  Q([[40, 690], [100, 770], [150, 930]], { w: 2.4 });
  Q([[1880, 690], [1820, 770], [1770, 930]], { w: 2.4 });
  // 水面波纹
  for (let i = 0; i < 9; i++) { const x = 380 + (i % 3) * 400 + (i > 2 ? 120 : 0) + (i > 5 ? -60 : 0), y = water + Math.floor(i / 3) * 44; S(`M ${x} ${y} q 20 -10 40 0 t 40 0 t 40 0`, { w: 1.6 }); }
  // 主拱：双钢管
  Q([[260, deck + 40], [560, 410], [960, 310], [1360, 410], [1660, deck + 40]], { w: 3.4, r: 0.7 });
  Q([[260, deck + 64], [560, 436], [960, 338], [1360, 436], [1660, deck + 64]], { w: 2.6, r: 0.7 });
  // 桥面
  L(40, deck, 1880, deck, { w: 3 }); L(40, deck + 22, 1880, deck + 22, { w: 2.4 });
  // 吊杆
  for (let i = 1; i < 14; i++) {
    const x = 260 + i * 100; const t = (x - 260) / 1400; const y = deck + 52 - Math.sin(t * PI) * 332;
    if (y < deck - 10) L(x, y, x, deck, { w: 1.4, single: true });
  }
  // 桥墩
  for (const x of [240, 1680]) { G([[x - 40, deck + 22], [x + 40, deck + 22], [x + 50, 930], [x - 50, 930]], { w: 2.4 }); }
  // 缆索吊 + 小船 + 工程师
  towerCrane(1500, deck, 440, 0.8);
  D('M 1040 880 L 1200 880 L 1170 910 L 1070 910 Z', { w: 2 }); L(1120, 880, 1120, 830, { w: 1.6 });
  G([[1120, 832], [1160, 862], [1120, 862]], { w: 1.6 });
  person(1780, deck, 0.9, { pose: 'point', face: -1 });
  birds(1450, 170);
  timelineTick(300, '', false);
}
function sAsphalt() {
  const gy = 880;
  // 透视路面
  L(40, gy, 1880, gy, { w: 2.2 });
  L(40, 640, 1880, 640, { w: 1.6, r: 0.5 });
  Q([[40, 630], [300, 540], [520, 580], [760, 500], [980, 560], [1260, 520], [1500, 570], [1880, 540]], { w: 1.8 });
  // 已摊铺的沥青（排线阴影）
  R(40, 820, 900, 60, { w: 2.2, hach: true, gap: 7, ang: -60, fw: 1 });
  // 摊铺机 → 压路机 → 压路机 列队
  paver(1100, gy, 1.25, -1);
  roller(620, gy - 58, 1.05, -1);
  roller(250, gy - 58, 0.9, -1);
  // 未铺的碎石基层点点
  for (let i = 0; i < 16; i++) { const x = 1330 + (i * 37) % 520, y = 838 + (i * 17) % 34; C(x, y, 7, { w: 1.2, single: true }); }
  // 项目经理手持图纸 + 施工旗
  person(1500, gy, 1.15, { pose: 'hold', face: -1 });
  person(1690, gy, 1, { vest: true, pose: 'raise', face: -1 });
  L(1654, 740, 1654, 560, { w: 2 }); G([[1654, 560], [1714, 580], [1654, 602]], { w: 2 });
  cone(1840, gy, 0.9); cone(1780, gy, 0.8);
  sun(1650, 330, 36); cloud(1300, 380, 0.8);
  timelineTick(300, '', false);
}
function sTunnel() {
  // 大山
  Q([[40, 700], [220, 540], [420, 480], [640, 400], [900, 350], [1160, 300], [1420, 250], [1660, 420], [1880, 520]], { w: 2.6 });
   Q([[1240, 420], [1380, 380], [1500, 440]], { w: 1.4, single: true });
  for (const [x, y, s] of [[300, 610, 0.8], [380, 580, 0.7], [1580, 540, 0.8], [1680, 600, 0.9], [220, 660, 0.9]]) pine(x, y, s);
  // 隧道洞门（端墙式）
  R(620, 470, 680, 60, { w: 2.6 });
  G([[560, 900], [620, 530], [1300, 530], [1360, 900]], { w: 2.4 });
  D('M 700 900 L 700 700 Q 700 560 960 560 Q 1220 560 1220 700 L 1220 900', { w: 3.2 });
  D('M 760 900 L 760 720 Q 760 610 960 610 Q 1160 610 1160 720 L 1160 900', { w: 1.8, hach: true, gap: 10, ang: 60, fw: 0.8 });
  D('M 850 900 L 850 780 Q 850 700 960 700 Q 1070 700 1070 780 L 1070 900', { w: 1.6 });
  for (let i = 0; i < 5; i++) C(960 + (i - 2) * 50, 640 + Math.abs(i - 2) * 12, 8, { w: 1.6, single: true });
  // 道路延伸
  L(40, 900, 1880, 900, { w: 2.4 });
  L(960, 900, 960, 960, { w: 3, single: true });
  // 凿岩台车 + 总工
  truck(390, 900, 1.05, 1);
  P([[420, 820], [560, 740], [640, 760]], { w: 2.6 }); P([[430, 800], [580, 700], [660, 700]], { w: 2.6 });
  person(1480, 900, 1.2, { pose: 'hold', face: -1 });
  person(1640, 900, 1, { vest: true, pose: 'point', face: -1 });
  T(960, 500, '隧道  TUNNEL', { size: 34, anchor: 'middle', font: 'XingShu' });
  timelineTick(300, '', false);
}
function sStage2() {
  stageCard(() => {
    // 高速公路指示牌 + 行驶的汽车
    L(1200, 900, 1200, 520, { w: 3 }); L(1560, 900, 1560, 520, { w: 3 });
    R(1100, 380, 560, 180, { w: 3 });
    T(1380, 470, '高速公路', { size: 72, anchor: 'middle', font: 'XingShu' });
    T(1380, 530, 'EXPRESSWAY', { size: 40, anchor: 'middle', font: 'Hand', bold: true });
    P([[1540, 410], [1600, 410]], { w: 2.4 }); P([[1586, 398], [1604, 410], [1586, 422]], { w: 2.4 });
    L(700, 900, 1880, 900, { w: 2.2 });
    car(900, 900, 1.2, 1); car(1760, 900, 0.9, -1);
  }, '2010.10');
}
function sOffice() {
  // 窗户（窗外高速）
  R(1150, 180, 520, 330, { w: 2.6 });
  L(1410, 180, 1410, 510, { w: 2 }); L(1150, 345, 1670, 345, { w: 1.6 });
  Q([[1160, 470], [1300, 430], [1420, 440], [1560, 400], [1660, 410]], { w: 1.4, single: true });
  Q([[1160, 500], [1300, 460], [1420, 470], [1560, 430], [1660, 440]], { w: 1.4, single: true });
  pine(1250, 320, 0.6); cloud(1560, 260, 0.6);
  // 墙钟 + 日历
  C(960, 260, 90, { w: 2.2 }); L(960, 260, 960, 228, { w: 2 }); L(960, 260, 984, 272, { w: 2 });
  R(1760, 240, 110, 130, { w: 2 }); L(1760, 272, 1870, 272, { w: 1.6 });
  for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) S(`M ${1776 + c * 24} ${292 + r * 26} l 10 0`, { w: 2 });
  // 办公桌
  G([[520, 800], [1560, 800], [1640, 860], [440, 860]], { w: 2.6 });
  L(460, 860, 460, 960, { w: 2.6 }); L(1620, 860, 1620, 960, { w: 2.6 }); L(1300, 860, 1300, 960, { w: 2 });
  R(1320, 876, 280, 34, { w: 1.8 }); R(1320, 916, 280, 34, { w: 1.8 });
  // 显示器
  R(760, 600, 300, 190, { w: 2.4 }); L(910, 790, 910, 806, { w: 2.4 }); L(860, 808, 960, 808, { w: 2.4 });
  for (let i = 0; i < 4; i++) L(790, 640 + i * 30, 790 + 180 - i * 30, 640 + i * 30, { w: 1.2, single: true });
  // 文件堆
  for (let i = 0; i < 6; i++) R(1150 + (i % 2) * 6, 782 - i * 18, 150, 16, { w: 1.6 });
  for (let i = 0; i < 4; i++) R(1380 + (i % 2) * 5, 784 - i * 16, 130, 14, { w: 1.6 });
  // 电话 + 笔筒
  D('M 560 790 L 660 790 L 650 760 L 570 760 Z', { w: 2 }); D('M 560 755 Q 610 730 660 755', { w: 2.4 });
  R(690, 740, 40, 50, { w: 1.8 }); L(700, 740, 694, 704, { w: 1.6 }); L(716, 740, 724, 700, { w: 1.6 });
  // 坐着的主任 + 来访同事
  R(200, 838, 130, 16, { w: 2 }); L(200, 690, 200, 960, { w: 2.4 }); L(320, 854, 320, 960, { w: 2 });
  person(280, 960, 1.7, { hat: false, pose: 'sit', tie: true, face: 1 });
  person(1760, 960, 1.5, { hat: false, pose: 'hold', face: -1 });
  // 绿植
  G([[60, 960], [140, 960], [130, 880], [70, 880]], { w: 2 });
  for (const a of [-0.9, -0.4, 0.1, 0.6, 1.0]) Q([[100, 880], [100 + a * 30, 810], [100 + a * 60, 760]], { w: 1.6, single: true });
  timelineTick(300, '', false);
}
function sGM() {
  // 收费站
  R(260, 360, 1400, 70, { w: 2.8 });
  T(960, 412, '收费站  TOLL STATION', { size: 44, anchor: 'middle', font: 'XingShu' });
  for (let i = 0; i < 6; i++) { const x = 330 + i * 250; L(x, 430, x, 900, { w: 2.4 }); R(x - 30, 740, 60, 110, { w: 2 }); R(x - 18, 760, 36, 30, { w: 1.4 }); }
  L(40, 900, 1880, 900, { w: 2.4 });
  // 车辆
  car(460, 900, 1, 1); car(960, 900, 1.05, 1); truck(1460, 900, 0.9, 1);
  // 栏杆
  L(560, 850, 700, 830, { w: 2 }); L(1060, 850, 1210, 820, { w: 2 });
  // 管理楼
  building(1720, 900, 170, 460, 3, 7);
  // 总经理 + 趋势图板
  person(170, 900, 1.2, { hat: false, tie: true, pose: 'point', face: 1 });
  R(80, 490, 250, 200, { w: 2.4 }); L(205, 690, 205, 760, { w: 2 });
  P([[100, 670], [100, 510]], { w: 1.4 }); P([[100, 670], [310, 670]], { w: 1.4 });
  P([[112, 650], [160, 620], [200, 634], [250, 574], [300, 530]], { w: 2.6 });
  P([[284, 528], [302, 528], [300, 546]], { w: 2.2 });
  cloud(1500, 230, 0.8); sun(1200, 230, 30);
  timelineTick(300, '', false);
}
function sMaint() {
  // 远景：高架桥 + 山
  Q([[40, 560], [300, 470], [600, 520], [900, 430], [1200, 500], [1500, 450], [1880, 520]], { w: 1.8 });
  L(40, 600, 1880, 600, { w: 2 }); L(40, 620, 1880, 620, { w: 1.6 });
  for (let i = 0; i < 8; i++) { const x = 140 + i * 240; L(x - 10, 620, x - 14, 700, { w: 1.6 }); L(x + 10, 620, x + 14, 700, { w: 1.6 }); }
  L(40, 700, 1880, 700, { w: 1.4, r: 0.4 });
  // 近景路面 + 车道线
  L(40, 900, 1880, 900, { w: 2.4 });
  for (let i = 0; i < 7; i++) L(80 + i * 280, 800, 200 + i * 280, 800, { w: 3, single: true });
  // 养护车（箭头板）+ 锥桶
  truck(420, 900, 1.2, 1, true);
  for (let i = 0; i < 6; i++) cone(760 + i * 110, 900 - i * 3, 0.9);
  // 路面修补：工人 + 开挖区域
  E(1180, 880, 220, 40, { w: 2, hach: true, gap: 8, ang: 30 });
  person(1110, 880, 0.95, { vest: true, pose: 'hold', face: 1 });
  person(1270, 880, 0.95, { vest: true, pose: 'raise', face: -1 });
  // 工程部经理：看剪贴板
  person(1560, 900, 1.15, { pose: 'hold', face: -1 });
  birds(1500, 300); cloud(700, 260, 0.9);
  timelineTick(300, '', false);
}
function sStage3() {
  stageCard(() => {
    shield(1340, 620, 2.6, true);
    for (let i = 0; i < 8; i++) { const a = -PI * 0.9 + i * PI * 0.8 / 7; L(1340 + Math.cos(a) * 330, 600 + Math.sin(a) * 330, 1340 + Math.cos(a) * 380, 600 + Math.sin(a) * 380, { w: 1.8, single: true }); }
  }, '2021.09');
}
function sSafety() {
  // 集团总部楼群
  building(1260, 900, 180, 560, 3, 9);
  building(1450, 900, 220, 690, 4, 11);
  building(1680, 900, 160, 470, 3, 7);
  L(1540, 210, 1540, 150, { w: 2 }); G([[1540, 150], [1600, 168], [1540, 186]], { w: 1.8 });
  // 安全宣讲：白板 + 讲解人 + 听讲员工
  R(460, 400, 520, 280, { w: 2.8 });
  T(720, 505, '安全第一', { size: 88, anchor: 'middle', font: 'XingShu' });
  T(720, 570, 'SAFETY FIRST', { size: 46, anchor: 'middle', font: 'Hand', bold: true });
  shield(720, 630, 0.34, true);
  L(520, 680, 500, 900, { w: 2 }); L(920, 680, 940, 900, { w: 2 });
  person(1060, 900, 1.2, { pose: 'point', face: -1 });
  for (let i = 0; i < 4; i++) person(110 + i * 105, 900, 1.02 + (i % 2) * 0.06, { vest: true, face: 1 });
  // 检查表 + 灭火器
  clipboard(1040, 170, 0.75, 3);
  R(1860, 790, 40, 110, { w: 2 }); P([[1870, 790], [1870, 766], [1900, 760]], { w: 2 }); L(1880, 766, 1880, 790, { w: 2 });
  L(40, 900, 1880, 900, { w: 2.4 });
  timelineTick(300, '', false);
}
function sOutro() {
  // 与开篇呼应：一条路伸向远方，人物戴安全帽前行，朝阳升起
  Q([[40, 620], [300, 540], [520, 580], [760, 470], [1000, 540], [1260, 500], [1520, 560], [1880, 520]], { w: 2 });
  D('M 1100 620 A 120 120 0 0 1 1340 620', { w: 2.4 });
  for (let i = 0; i < 9; i++) { const a = PI + (i + 0.5) * PI / 9; L(1220 + Math.cos(a) * 150, 620 + Math.sin(a) * 150, 1220 + Math.cos(a) * 200, 620 + Math.sin(a) * 200, { w: 1.6, single: true }); }
  L(40, 620, 1880, 620, { w: 1.8, r: 0.5 });
  D('M 1180 620 Q 1060 760 700 1000', { w: 2.8 }); D('M 1260 620 Q 1400 760 1860 1000', { w: 2.8 });
  for (let i = 0; i < 5; i++) { const t = i / 5; const y = 640 + t * t * 320; L(1220 + t * 20, y, 1220 + t * 24, y + 20 + t * 30, { w: 2 + t * 3, single: true }); }
  person(1340, 900, 1.3, { pose: 'walk', face: -1 });
  birds(1380, 400, 4);
  L(40, 1040, 600, 1040, { w: 1.6 });
  T(60, 1020, '1995 — 2010 — 2021 — 至今 Now', { size: 34, font: 'Hand', bold: true });
}

// ---------------------------------------------------------------- 构建
const world = document.getElementById('world');
const penG = document.getElementById('pen');
let strokes = [], texts = [], sceneStart = [], total = 0;
const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent && parent.appendChild(e); return e; };

function makeText(g, x, y, str, size, font, anchor, bold) {
  const t = el('text', { x, y, 'font-size': size, 'font-family': font === 'Hand' ? 'Hand, XingShu' : font, 'text-anchor': anchor, fill: INK }, g);
  if (bold) t.setAttribute('font-weight', 700);
  t.textContent = str;
  return t;
}
function addTextItem(g, x, y, str, size, font, anchor, start, dur, bold) {
  const clipId = 'c' + texts.length;
  const cp = el('clipPath', { id: clipId }, g);
  const t = makeText(g, x, y, str, size, font, anchor, bold);
  const bb = t.getBBox();
  const rect = el('rect', { x: bb.x - 10, y: bb.y - 20, width: 0, height: bb.height + 40 }, cp);
  t.setAttribute('clip-path', `url(#${clipId})`);
  texts.push({ rect, w: bb.width + 20, start, dur, gx: bb.x - 10, gy: bb.y + bb.height * 0.62, g });
}

window.build = async function () {
  await document.fonts.load('72px XingShu', '我的职业历程');
  await document.fonts.load('bold 40px Hand', 'Career');
  await document.fonts.ready;
  let t0 = 0;
  // 跨全片的时间轴基线
  const axisG = el('g', {}, world);
  SCENES.forEach((sc, i) => {
    sceneStart.push(t0);
    const g = el('g', { transform: `translate(${i * W},0)` }, world);
    cur = { shapes: [] };
    if (sc.id !== 'outro') L(0, 985, W, 985, { w: 2, r: 0.4, b: 0.3 });
    sc.draw();
    // 文字：标题行书 + 英文手写 + 副标题
    const isStage = sc.kind === 'stage';
    const tx = isStage ? 160 : 150, ty = isStage ? 330 : 190;
    let textEnd = t0 + 0.5;
    if (sc.zh) {
      const zsize = sc.big ? 150 : isStage ? 108 : 92;
      const zy = sc.big ? 330 : ty;
      const zd = Math.min(2.0, 0.5 + sc.zh.length * 0.13), es = t0 + 0.5 + zd * 0.85;
      addTextItem(g, tx, zy, sc.zh, zsize, 'XingShu', 'start', t0 + 0.5, zd);
      addTextItem(g, tx + 6, zy + (sc.big ? 90 : 72), sc.en, sc.big ? 68 : 54, 'Hand', 'start', es, 1.0, true);
      addTextItem(g, tx + 6, zy + (sc.big ? 160 : 128), sc.sub, isStage ? 50 : 38, 'Hand', 'start', es + 0.9, 0.9, isStage);
      L(tx, zy + (sc.big ? 190 : 150), tx + (sc.big ? 560 : 420), zy + (sc.big ? 190 : 150), { w: 1.6, r: 1.6 });
    }
    // 线条：按长度分配到绘制窗口内
    const drawStart = t0 + (i === 0 ? 0.3 : 0.6);
    const drawWin = sc.dur * (sc.id === 'outro' ? 0.45 : 0.72);
    const items = [];
    for (const sh of cur.shapes) {
      if (sh.text) {
        items.push({ text: sh, len: sh.text.length * sh.size * 0.9 });
        continue;
      }
      const p = el('path', { d: sh.d, fill: 'none', stroke: INK, 'stroke-width': sh.w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: sh.alpha }, g);
      const len = p.getTotalLength();
      items.push({ p, len, sceneIdx: i });
    }
    const totLen = items.reduce((a, b) => a + Math.sqrt(b.len) , 0) || 1;
    let tt = drawStart;
    for (const it of items) {
      const dur = Math.max(0.04, Math.sqrt(it.len) / totLen * drawWin);
      if (it.text) {
        const s = it.text;
        addTextItem(g, s.x, s.y, s.text, s.size, s.font === 'XingShu' ? 'XingShu' : 'Hand', s.anchor, tt, dur, s.bold ?? s.font !== 'XingShu');
      } else {
        it.p.style.strokeDasharray = `${it.len + 1} ${it.len + 1}`;
        strokes.push({ p: it.p, len: it.len, start: tt, dur, ox: i * W });
      }
      tt += dur;
    }
    t0 += sc.dur;
  });
  total = t0;
  addOutroText();
  return { total, scenes: SCENES.map((s, i) => ({ id: s.id, start: sceneStart[i], dur: s.dur })) };
};

// ---------------------------------------------------------------- 渲染
const ease = x => x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const clamp = x => Math.max(0, Math.min(1, x));
function camera(t) {
  let k = 0;
  for (let i = 0; i < sceneStart.length; i++) if (t >= sceneStart[i]) k = i;
  const u = ease(clamp((t - sceneStart[k]) / 1.4));
  const x = k === 0 ? 0 : (k - 1 + u) * W;
  // 场景内缓慢推近，增加呼吸感
  const local = t - sceneStart[k];
  const z = 1 + 0.025 * clamp(local / SCENES[k].dur);
  return { x, z };
}
// 铅笔
function drawPen() {
  penG.innerHTML = '';
  const g = el('g', {}, penG);
  el('path', { d: 'M 0 0 L 10 -22 L 150 -170 L 172 -150 L 32 -2 Z', fill: '#f5efe2', stroke: INK, 'stroke-width': 2.4, 'stroke-linejoin': 'round' }, g);
  el('path', { d: 'M 10 -22 L 32 -2', fill: 'none', stroke: INK, 'stroke-width': 2 }, g);
  el('path', { d: 'M 0 0 L 4 -9 L 13 -3 Z', fill: INK }, g);
  el('path', { d: 'M 136 -155 L 158 -135', fill: 'none', stroke: INK, 'stroke-width': 2 }, g);
  el('path', { d: 'M 20 -12 L 160 -160', fill: 'none', stroke: INK, 'stroke-width': 1, opacity: 0.6 }, g);
}
drawPen();
let lastPen = null;

window.penActivity = t => strokes.some(s => t >= s.start && t < s.start + s.dur) ? 1 : 0;

window.renderAt = function (t) {
  const cam = camera(t);
  const cx = cam.x + W / 2, cy = H / 2;
  world.setAttribute('transform', `translate(${W / 2} ${cy}) scale(${cam.z}) translate(${-cx} ${-cy})`);
  let active = null;
  for (const s of strokes) {
    const p = clamp((t - s.start) / s.dur);
    if (p <= 0) { s.p.style.visibility = 'hidden'; continue; }
    s.p.style.visibility = 'visible';
    s.p.style.strokeDashoffset = s.len * (1 - p);
    if (p < 1 && (!active || s.start > active.s.start)) active = { s, p };
  }
  for (const tx of texts) {
    const p = clamp((t - tx.start) / tx.dur);
    tx.rect.setAttribute('width', tx.w * p);
  }
  // 铅笔跟随正在生长的笔画
  if (active) {
    const pt = active.s.p.getPointAtLength(active.s.len * active.p);
    const wx = pt.x + active.s.ox, wy = pt.y;
    const sx = W / 2 + (wx - cx) * cam.z, sy = cy + (wy - cy) * cam.z;
    lastPen = { x: sx, y: sy, t };
  }
  if (lastPen && t - lastPen.t < 0.25) {
    penG.style.visibility = 'visible';
    penG.setAttribute('transform', `translate(${lastPen.x} ${lastPen.y})`);
    penG.style.opacity = 1 - clamp((t - lastPen.t) / 0.25);
  } else penG.style.visibility = 'hidden';
  // 片尾淡出
  document.getElementById('fade').setAttribute('opacity', clamp((t - (total - 1.2)) / 1.2));
};

// 片尾文字（屏幕中央，叠加在最后一幕）
function addOutroText() {
  const i = SCENES.length - 1, g = world.children[i + 1];
  const t0 = sceneStart[i];
  addTextItem(g, 150, 210, '筑路 · 管路 · 守平安', 120, 'XingShu', 'start', t0 + 0.6, 2.4);
  addTextItem(g, 156, 290, 'Building roads · Running roads · Safeguarding lives', 54, 'Hand', 'start', t0 + 3.1, 1.8, true);
  addTextItem(g, 156, 380, '路在脚下，未完待续', 72, 'XingShu', 'start', t0 + 5.2, 1.6);
  addTextItem(g, 156, 440, 'The road goes on — to be continued.', 46, 'Hand', 'start', t0 + 6.8, 1.4, true);
};
