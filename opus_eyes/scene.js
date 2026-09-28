// 《用 Opus 5.5 看世界》—— 全部画面由 Canvas 2D 代码实时绘制，无图片、无外部素材。
// window.renderAt(t) 是纯函数：给定时间（秒）画出这一帧，便于逐帧离线渲染。
//
// 分镜（与 make_music.py 的小节对齐，96 BPM，1 小节 = 2.5 秒）
//   0-10     苏醒：光标、"Hello, world."、切分成 token、散作星辰、标题
//   10-25    文字构成的世界：由汉字拼成的日出山水，逐一识别
//   25-40    意义空间：词语在三维空间中的分布，king − man + woman ≈ queen
//   40-55    注意力：词与词之间的注视，预测下一个词，多层网络脉动
//   55-60    凝聚：一切旋入一点，白光
//   60-77.5  一个世界：点阵地球，各种语言的问候彼此相连
//   77.5-90  看见：地球化作眼睛的虹膜，眨眼，结语

const W = 1920, H = 1080, CX = W / 2, CY = H / 2;
const BEAT = 60 / 96;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');

const SANS = '"DejaVu Sans","WenQuanYi Zen Hei","FreeSerif","Loma",sans-serif';
const CJK = '"WenQuanYi Zen Hei","DejaVu Sans",sans-serif';
const MONO = '"DejaVu Sans Mono","WenQuanYi Zen Hei Mono",monospace';

const BG = '#06070c';
const CREAM = [242, 236, 226];
const CLAY = [232, 128, 90];
const AMBER = [246, 192, 112];
const TEAL = [104, 204, 210];
const VIOLET = [158, 138, 236];
const LEAF = [140, 206, 130];

// 与 make_music.py 保持一致
const TYPE_START = 1.2, TYPE_STEP = 0.14, TYPE_TEXT = 'Hello, world.';
const END_TYPE_START = 87.8, END_TYPE_STEP = 0.1, END_TEXT = '世界，是一场对话。';

// ---------------------------------------------------------------- 工具函数
const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
const seg = (t, a, b) => clamp((t - a) / (b - a));
const sm = x => x * x * (3 - 2 * x);
const eio = x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const eout = x => 1 - Math.pow(1 - x, 3);
const lerp = (a, b, x) => a + (b - a) * x;
const fade = (t, a, b, f = 0.6) => sm(seg(t, a, a + f)) * (1 - sm(seg(t, b - f, b)));
const rgba = (c, a) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a})`;
const mix = (c1, c2, x) => [lerp(c1[0], c2[0], x), lerp(c1[1], c2[1], x), lerp(c1[2], c2[2], x)];
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function hash(i, j = 0) {
  let h = Math.imul(i | 0, 374761393) + Math.imul(j | 0, 668265263);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}
const rnd = mulberry32(20260928);
const gauss = () => { let u = 0; for (let i = 0; i < 4; i++) u += rnd(); return (u - 2) / 0.58; };

// 发光贴图（径向渐变），加色混合时使用
const glowCache = new Map();
function glow(c) {
  const key = c.join(',');
  if (glowCache.has(key)) return glowCache.get(key);
  const g = document.createElement('canvas'); g.width = g.height = 128;
  const x = g.getContext('2d');
  const gr = x.createRadialGradient(64, 64, 0, 64, 64, 64);
  gr.addColorStop(0, rgba(c, 1)); gr.addColorStop(0.18, rgba(c, 0.55));
  gr.addColorStop(0.45, rgba(c, 0.12)); gr.addColorStop(1, rgba(c, 0));
  x.fillStyle = gr; x.fillRect(0, 0, 128, 128);
  glowCache.set(key, g);
  return g;
}
function drawGlow(c, x, y, r, a = 1) {
  if (a <= 0) return;
  ctx.globalAlpha = a;
  ctx.drawImage(glow(c), x - r, y - r, 2 * r, 2 * r);
  ctx.globalAlpha = 1;
}

// ---------------------------------------------------------------- 星空（多场景共用）
const STARS = [];
for (let i = 0; i < 1500; i++) {
  STARS.push({ x: (rnd() * 2 - 1) * 1.7, y: (rnd() * 2 - 1) * 1.1, z: rnd() * 4 + 0.15, b: 0.3 + rnd() * 0.7, c: rnd() });
}
// 相机前进距离（积分形式，便于求速度）
function travel(t) {
  const warp = x => (x <= 0 ? 0 : x); // 在 8.3s 后加速
  let d = 0.06 * t;
  const w = warp(t - 8.3);
  d += w > 0 ? Math.min(w, 2.4) ** 3 * 0.35 + Math.max(0, w - 2.4) * 6 : 0;
  return d;
}
function drawStars(t, alpha, spin = 0, dist = travel(t)) {
  if (alpha <= 0) return;
  const v = (dist - travel(t - 1 / 30)) * 30;
  const cs = Math.cos(spin), sn = Math.sin(spin);
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < STARS.length; i++) {
    const s = STARS[i];
    const z = ((s.z - dist) % 4.15 + 4.15) % 4.15 + 0.05;
    const x = s.x * cs - s.y * sn, y = s.x * sn + s.y * cs;
    const k = 560 / z;
    const sx = CX + x * k, sy = CY + y * k;
    if (sx < -50 || sx > W + 50 || sy < -50 || sy > H + 50) continue;
    const a = alpha * s.b * clamp((4.1 - z) / 1.2) * clamp(z / 0.3);
    const col = s.c < 0.15 ? AMBER : s.c < 0.3 ? TEAL : CREAM;
    const len = Math.min(v * 0.06, 1.2);
    if (len > 0.02) {
      const z2 = z + len, k2 = 560 / z2;
      ctx.strokeStyle = rgba(col, a);
      ctx.lineWidth = Math.min(3, 1.6 / z + 0.4);
      ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(CX + x * k2, CY + y * k2); ctx.stroke();
    } else {
      const r = Math.min(2.6, 1.3 / z + 0.5);
      ctx.fillStyle = rgba(col, a);
      ctx.fillRect(sx - r / 2, sy - r / 2, r, r);
    }
  }
  ctx.globalCompositeOperation = 'source-over';
}

// ---------------------------------------------------------------- 1. 苏醒
const S1 = {};
function initS1() {
  const oc = document.createElement('canvas'); oc.width = W; oc.height = H;
  const o = oc.getContext('2d');
  o.font = `500 92px ${MONO}`;
  S1.cw = o.measureText('M').width;
  S1.x0 = CX - (S1.cw * TYPE_TEXT.length) / 2;
  S1.y = CY;
  o.textBaseline = 'middle'; o.fillStyle = '#fff';
  for (let i = 0; i < TYPE_TEXT.length; i++) o.fillText(TYPE_TEXT[i], S1.x0 + i * S1.cw, S1.y);
  const d = o.getImageData(0, 0, W, H).data;
  S1.parts = [];
  for (let y = S1.y - 70; y < S1.y + 70; y += 3) {
    for (let x = Math.floor(S1.x0 - 10); x < S1.x0 + S1.cw * TYPE_TEXT.length + 10; x += 3) {
      if (d[(y * W + x) * 4 + 3] > 120) {
        const ci = clamp(Math.floor((x - S1.x0) / S1.cw), 0, TYPE_TEXT.length - 1);
        let vx = (x - CX) / 500 + gauss() * 0.6, vy = (y - CY) / 200 + gauss() * 0.6;
        const n = Math.hypot(vx, vy) + 1e-6;
        S1.parts.push({ x, y, ci, vx: vx / n, vy: vy / n, sp: 0.4 + rnd() * 1.2, tw: rnd() * 6.28 });
      }
    }
  }
  S1.tokens = [
    { a: 0, b: 5, id: '9906', c: CLAY },
    { a: 5, b: 6, id: '11', c: TEAL },
    { a: 6, b: 12, id: '1917', c: AMBER },
    { a: 12, b: 13, id: '13', c: VIOLET },
  ];
}
function tokOf(ci) { return ci < 5 ? 0 : ci < 6 ? 1 : ci < 12 ? 2 : 3; }

function roundRect(x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}

function scene1(t) {
  const n = t < TYPE_START ? 0 : Math.min(TYPE_TEXT.length, Math.floor((t - TYPE_START) / TYPE_STEP) + 1);
  const cw = S1.cw;

  drawStars(t, 0.9 * sm(seg(t, 5.4, 7.2)) * (1 - sm(seg(t, 10.0, 10.7))));

  if (t < 5.2) {
    ctx.font = `500 92px ${MONO}`;
    ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
    for (let i = 0; i < n; i++) {
      const k = tokOf(i);
      const tint = sm(seg(t, 3.3 + k * 0.3, 3.7 + k * 0.3));
      ctx.fillStyle = rgba(mix(CREAM, S1.tokens[k].c, tint * 0.55), 1);
      ctx.fillText(TYPE_TEXT[i], S1.x0 + i * cw, S1.y);
    }
    // 光标
    const typing = t >= TYPE_START && t < TYPE_START + TYPE_STEP * TYPE_TEXT.length;
    if ((typing || t % 1.0 < 0.55) && t < 3.3) {
      ctx.fillStyle = rgba(AMBER, 1);
      ctx.fillRect(S1.x0 + n * cw + 6, S1.y - 50, 8, 100);
      drawGlow(AMBER, S1.x0 + n * cw + 10, S1.y, 90, 0.25);
    }
    // token 切分框与编号
    for (let k = 0; k < S1.tokens.length; k++) {
      const tk = S1.tokens[k];
      const a = sm(seg(t, 3.3 + k * 0.3, 3.7 + k * 0.3)) * (1 - sm(seg(t, 4.9, 5.25)));
      if (a <= 0) continue;
      const x = S1.x0 + tk.a * cw - 6 + (tk.a === 6 ? cw * 0.5 : 0);
      const w = (tk.b - tk.a) * cw + 12 - (tk.a === 6 ? cw * 0.5 : 0);
      ctx.globalAlpha = a;
      ctx.strokeStyle = rgba(tk.c, 0.9); ctx.lineWidth = 2.5;
      roundRect(x, S1.y - 66, w, 132, 12); ctx.stroke();
      ctx.fillStyle = rgba(tk.c, 0.1); ctx.fill();
      ctx.font = `20px ${MONO}`; ctx.textAlign = 'center'; ctx.fillStyle = rgba(tk.c, 1);
      ctx.fillText(tk.id, x + w / 2, S1.y + 100 + (1 - a) * 10);
      ctx.globalAlpha = 1;
    }
    ctx.textAlign = 'left';
  } else {
    // 散作星尘
    const e = seg(t, 5.2, 9.8);
    const D = 1300 * Math.pow(e, 1.7);
    const fa = 1 - sm(seg(t, 7.2, 9.6));
    ctx.globalCompositeOperation = 'lighter';
    for (const p of S1.parts) {
      const c = S1.tokens[tokOf(p.ci)].c;
      const col = mix(CREAM, c, 0.55 + 0.45 * sm(seg(t, 5.2, 6)));
      const x = p.x + p.vx * D * p.sp + Math.sin(p.tw + t * 2) * 3 * e;
      const y = p.y + p.vy * D * p.sp + Math.cos(p.tw + t * 1.7) * 3 * e;
      const a = fa * (0.55 + 0.45 * Math.sin(p.tw + t * 6));
      ctx.fillStyle = rgba(col, a);
      const r = 2.6 + e * 1.5;
      ctx.fillRect(x - r / 2, y - r / 2, r, r);
    }
    ctx.globalCompositeOperation = 'source-over';
  }

  // 标题
  const ta = sm(seg(t, 6.6, 7.6)) * (1 - sm(seg(t, 9.2, 9.9)));
  if (ta > 0) {
    const title = '用 Opus 5.5 看世界';
    ctx.save();
    ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    ctx.font = `600 104px ${CJK}`;
    ctx.letterSpacing = '10px';
    const full = ctx.measureText(title).width;
    let x = CX - full / 2;
    ctx.textAlign = 'left';
    for (let i = 0; i < title.length; i++) {
      const ch = title[i];
      const a = sm(seg(t, 6.6 + i * 0.06, 7.3 + i * 0.06)) * (1 - sm(seg(t, 9.2, 9.9)));
      const w = ctx.measureText(ch).width;
      ctx.fillStyle = rgba(ch === '5' || ch === '.' || /[Opus]/.test(ch) ? AMBER : CREAM, a);
      ctx.shadowColor = rgba(AMBER, 0.5 * a); ctx.shadowBlur = 30;
      ctx.fillText(ch, x, CY + 10 + (1 - a) * 24);
      x += w;
    }
    ctx.shadowBlur = 0;
    ctx.letterSpacing = '9px';
    ctx.textAlign = 'center';
    ctx.font = `300 24px ${SANS}`;
    ctx.fillStyle = rgba(CREAM, 0.7 * sm(seg(t, 7.4, 8.3)) * (1 - sm(seg(t, 9.2, 9.9))));
    ctx.fillText('SEEING THE WORLD THROUGH OPUS 5.5', CX, CY + 88);
    const lw = 520 * eout(seg(t, 7.2, 8.4));
    ctx.fillStyle = rgba(AMBER, 0.8 * ta);
    ctx.fillRect(CX - lw / 2, CY + 40, lw, 2);
    ctx.restore();
  }
}

// ---------------------------------------------------------------- 2. 文字构成的世界
const CS = 24, COLS = W / CS, ROWS = H / CS;
const HZ = 0.66;
const GLY = {
  sky1: '天空', sky2: '空气', sky3: '霞光暖', cloud: '云',
  sun: '日', far: '山', mid: '山岭峰', near: '林木树森', water: '水波流', shine: '光',
};
const SCRAMBLE = '01#%&*+=<>/ABCDEFGHXYZ∑∆λπ';
function sunPos(t) { const r = seg(t, 10, 25); return { x: 0.66, y: 0.42 - 0.07 * r }; }
function ridgeFar(u) { return 0.43 + 0.06 * Math.sin(u * 7 + 1) + 0.03 * Math.sin(u * 17 + 2) + 0.012 * Math.sin(u * 41); }
function ridgeMid(u) { return 0.5 + 0.055 * Math.sin(u * 5 + 3.4) + 0.025 * Math.sin(u * 13 + 1) + 0.01 * Math.sin(u * 43 + 2); }
function ridgeNear(u) { return 0.585 + 0.05 * Math.sin(u * 3.3 + 0.2) + 0.02 * Math.sin(u * 11) + 0.008 * Math.sin(u * 53); }
const SKY_TOP = [16, 18, 46], SKY_MID = [70, 52, 112], SKY_LOW = [236, 140, 92];

function above(u, v, t, col, ci, cj) {
  const sp = sunPos(t);
  const dx = (u - sp.x) * (W / H), dy = v - sp.y;
  const d = Math.hypot(dx, dy);
  const light = Math.exp(-d * 5);
  if (d < 0.062) {
    const k = 1 - d / 0.062;
    col.c = mix([255, 190, 110], [255, 246, 220], k); col.g = GLY.sun; col.kind = 1;
    return;
  }
  const rn = ridgeNear(u), rm = ridgeMid(u), rf = ridgeFar(u);
  if (v > rn) {
    const depth = seg(v, rn, HZ);
    col.c = mix(mix([60, 120, 92], [22, 52, 50], depth), [255, 170, 110], light * 0.45 * (1 - depth));
    if (v - rn < 0.018) col.c = mix(col.c, [255, 200, 140], 0.35 + light);
    col.g = GLY.near[Math.floor(hash(ci, cj) * 4)];
    col.kind = 4;
    return;
  }
  if (v > rm) {
    const depth = seg(v, rm, rm + 0.12);
    col.c = mix(mix([104, 80, 150], [48, 38, 86], depth), [255, 176, 120], light * 0.6 * (1 - depth * 0.7));
    if (v - rm < 0.018) col.c = mix(col.c, [255, 196, 150], 0.3 + light);
    col.g = GLY.mid[Math.floor(hash(ci, cj) * 3)];
    col.kind = 3;
    return;
  }
  if (v > rf) {
    const depth = seg(v, rf, rf + 0.1);
    const skyc = mix(SKY_MID, SKY_LOW, seg(v, 0.3, HZ));
    col.c = mix(mix([176, 160, 214], [130, 116, 176], depth), skyc, 0.3);
    col.c = mix(col.c, [255, 190, 130], light * 0.5);
    col.g = GLY.far; col.kind = 2;
    return;
  }
  // 天空与云
  let c = v < 0.3 ? mix(SKY_TOP, SKY_MID, v / 0.3) : mix(SKY_MID, SKY_LOW, seg(v, 0.3, HZ) ** 1.3);
  c = mix(c, [255, 214, 150], clamp(light * 0.9));
  const cl = Math.sin(u * 9 + t * 0.06 + Math.sin(v * 31) * 0.8) * Math.sin(u * 4.3 - t * 0.04 + 1.3 + v * 7);
  if (v > 0.12 && v < 0.36 && cl > 0.42) {
    col.c = mix(c, [255, 206, 196], clamp((cl - 0.42) * 2.2) * 0.6 + light * 0.3);
    col.g = GLY.cloud; col.kind = 5;
    return;
  }
  col.c = c;
  const set = v < 0.2 ? GLY.sky1 : v < 0.42 ? GLY.sky2 : GLY.sky3;
  col.g = set[Math.floor(hash(ci, cj) * set.length)];
  col.kind = 0;
}

function scene2(t) {
  const zoom = 1 + 0.07 * sm(seg(t, 13, 25));
  const scan = lerp(-0.06, 1.08, seg(t, 10.2, 13.4));
  const cell = { c: null, g: '', kind: 0 };
  ctx.save();
  ctx.translate(CX, CY); ctx.scale(zoom, zoom); ctx.translate(-CX, -CY);
  ctx.font = `20px ${CJK}`;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const lift = t > 22;
  for (let j = 0; j < ROWS; j++) {
    const v = (j + 0.5) / ROWS;
    for (let i = 0; i < COLS; i++) {
      const u = (i + 0.5) / COLS;
      let x = i * CS + CS / 2, y = j * CS + CS / 2;
      let a = 1;
      if (v > scan - 0.035 && v < scan + 0.02) {
        // 扫描线处：乱码
        const r = hash(i * 7 + Math.floor(t * 20), j);
        ctx.fillStyle = rgba(mix(TEAL, CREAM, r), 0.5 + 0.5 * r);
        ctx.fillText(SCRAMBLE[Math.floor(r * SCRAMBLE.length)], x, y);
        continue;
      }
      if (v >= scan) {
        if (hash(i, j + 99) < 0.08) { ctx.fillStyle = rgba(TEAL, 0.12); ctx.fillRect(x - 1, y - 1, 2, 2); }
        continue;
      }
      if (v < HZ) {
        above(u, v, t, cell, i, j);
      } else {
        const vv = 2 * HZ - v;
        const uu = u + 0.006 * Math.sin(v * 90 - t * 2.4 + u * 10);
        above(uu, vv, t, cell, i, 2 * Math.round(HZ * ROWS) - j);
        const sunCol = cell.kind === 1;
        const depth = seg(v, HZ, 1);
        cell.c = mix(mix(cell.c, [40, 70, 110], 0.35 + depth * 0.3), [0, 0, 0], 0.25 + depth * 0.35);
        if (sunCol) { cell.g = GLY.shine; cell.c = mix(cell.c, [255, 220, 160], 0.6); }
        else cell.g = GLY.water[Math.floor(hash(i, j + Math.floor(t * 1.2 + hash(i, j) * 3)) * 3)];
        // 水面波光
        const sp = sunPos(t);
        const glint = Math.abs(u - sp.x) < 0.05 + depth * 0.06 && Math.sin(u * 140 + v * 60 - t * 5) > 0.6;
        if (glint) cell.c = mix(cell.c, [255, 220, 160], 0.5);
      }
      if (lift) {
        const dl = hash(i + 311, j) * 1.3 + (1 - v) * 0.6;
        const lt = Math.max(0, t - 22 - dl);
        y -= lt * lt * 240;
        x += (u - 0.5) * lt * 160;
        a *= 1 - sm(seg(lt, 0.2, 1.3));
        if (a <= 0.01) continue;
      }
      // 淡淡的底色 + 字
      ctx.fillStyle = rgba(cell.c, 0.2 * a);
      ctx.fillRect(x - CS / 2, y - CS / 2, CS, CS);
      ctx.fillStyle = rgba(mix(cell.c, [255, 255, 255], 0.12), a);
      ctx.fillText(cell.g, x, y);
    }
  }
  // 扫描线
  if (scan > -0.05 && scan < 1.05) {
    const sy = scan * H;
    const gr = ctx.createLinearGradient(0, sy - 40, 0, sy + 4);
    gr.addColorStop(0, rgba(TEAL, 0)); gr.addColorStop(1, rgba(TEAL, 0.35));
    ctx.fillStyle = gr; ctx.fillRect(0, sy - 40, W, 44);
    ctx.fillStyle = rgba(TEAL, 0.9); ctx.fillRect(0, sy, W, 2);
  }
  // 飞鸟
  const ba = sm(seg(t, 12.5, 13.5)) * (1 - sm(seg(t, 22, 23)));
  if (ba > 0) {
    ctx.font = `22px ${CJK}`;
    for (let k = 0; k < 5; k++) {
      const bx = (0.12 + 0.035 * k + (t - 10) * 0.016) * W;
      const by = (0.26 + 0.025 * Math.sin(k * 2.1 + t * 1.6) - (k % 2) * 0.02 + k * 0.012) * H;
      ctx.fillStyle = rgba([30, 26, 50], ba);
      ctx.fillText('鸟', bx, by);
    }
  }
  ctx.restore();

  // 识别框
  const sp = sunPos(t);
  const boxes = [
    { t0: 15.0, x: sp.x * W, y: sp.y * H, w: 170, h: 170, zh: '日出', en: 'sunrise', p: '0.98', c: AMBER },
    { t0: 16.25, x: 0.3 * W, y: 0.46 * H, w: 320, h: 170, zh: '山', en: 'mountains', p: '0.96', c: VIOLET },
    { t0: 17.5, x: (0.14 + 0.07 + (t - 10) * 0.016) * W, y: 0.27 * H, w: 250, h: 110, zh: '飞鸟', en: 'birds', p: '0.89', c: CREAM },
    { t0: 18.75, x: 0.16 * W, y: 0.63 * H, w: 330, h: 120, zh: '森林', en: 'forest', p: '0.93', c: LEAF },
    { t0: 20.0, x: 0.68 * W, y: 0.82 * H, w: 420, h: 150, zh: '倒影', en: 'reflection', p: '0.91', c: TEAL },
  ];
  for (const b of boxes) {
    const a = sm(seg(t, b.t0, b.t0 + 0.35)) * (1 - sm(seg(t, 21.8, 22.4)));
    if (a <= 0) continue;
    const s = lerp(1.25, 1, eout(seg(t, b.t0, b.t0 + 0.45)));
    const hw = (b.w / 2) * s, hh = (b.h / 2) * s;
    const bx = CX + (b.x - CX) * zoom, by = CY + (b.y - CY) * zoom;
    brackets(bx - hw, by - hh, hw * 2, hh * 2, b.c, a);
    ctx.globalAlpha = a;
    const label = `${b.zh}  ${b.en}  ${b.p}`;
    ctx.font = `18px ${MONO}`;
    const lw = ctx.measureText(label).width + 22;
    ctx.fillStyle = rgba([8, 10, 18], 0.75);
    ctx.fillRect(bx - hw, by - hh - 34, lw, 28);
    ctx.fillStyle = rgba(b.c, 1);
    ctx.fillRect(bx - hw, by - hh - 34, 4, 28);
    ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    ctx.fillStyle = rgba(CREAM, 0.95);
    ctx.fillText(label, bx - hw + 12, by - hh - 20);
    ctx.globalAlpha = 1;
  }
}

function brackets(x, y, w, h, c, a, L = 22) {
  ctx.strokeStyle = rgba(c, a); ctx.lineWidth = 2.5;
  ctx.beginPath();
  ctx.moveTo(x, y + L); ctx.lineTo(x, y); ctx.lineTo(x + L, y);
  ctx.moveTo(x + w - L, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + L);
  ctx.moveTo(x + w, y + h - L); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w - L, y + h);
  ctx.moveTo(x + L, y + h); ctx.lineTo(x, y + h); ctx.lineTo(x, y + h - L);
  ctx.stroke();
}

// ---------------------------------------------------------------- 3. 意义空间
const CLUSTERS = [
  { zh: '动物', en: 'ANIMALS', c: TEAL, p: [-0.62, 0.28, 0.2] },
  { zh: '自然', en: 'NATURE', c: LEAF, p: [0.1, 0.62, -0.45] },
  { zh: '情感', en: 'FEELINGS', c: CLAY, p: [-0.05, -0.62, -0.35] },
  { zh: '音乐', en: 'MUSIC', c: VIOLET, p: [-0.55, -0.35, 0.55] },
  { zh: '人', en: 'PEOPLE', c: AMBER, p: [0.55, -0.05, 0.3] },
];
const MAN = [0.42, 0.14, 0.32], GEN = [0.0, -0.3, 0.06], ROY = [0.3, 0.0, -0.1];
const add3 = (a, b, k = 1) => [a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k];
const WORDS = [
  ['猫', 'cat', 0, [-0.7, 0.2, 0.25]], ['狗', 'dog', 0, [-0.58, 0.3, 0.1]], ['鸟', 'bird', 0, [-0.75, 0.45, 0.35]],
  ['鱼', 'fish', 0, [-0.45, 0.2, 0.42]], ['马', 'horse', 0, [-0.5, 0.42, 0.0]],
  ['山', 'mountain', 1, [0.2, 0.7, -0.4]], ['河', 'river', 1, [0.02, 0.55, -0.55]], ['雨', 'rain', 1, [-0.05, 0.72, -0.3]],
  ['太阳', 'sun', 1, [0.25, 0.52, -0.6]], ['海', 'sea', 1, [0.1, 0.5, -0.3]],
  ['爱', 'love', 2, [0.0, -0.7, -0.3]], ['希望', 'hope', 2, [0.15, -0.55, -0.45]], ['喜悦', 'joy', 2, [-0.15, -0.6, -0.2]],
  ['思念', 'longing', 2, [0.05, -0.75, -0.5]],
  ['旋律', 'melody', 3, [-0.6, -0.3, 0.6]], ['节奏', 'rhythm', 3, [-0.45, -0.42, 0.5]], ['歌', 'song', 3, [-0.62, -0.45, 0.45]],
  ['男人', 'man', 4, MAN], ['女人', 'woman', 4, add3(MAN, GEN)],
  ['国王', 'king', 4, add3(MAN, ROY)], ['女王', 'queen', 4, add3(add3(MAN, GEN), ROY)],
].map(([zh, en, cl, p]) => ({ zh, en, cl, p, d: rnd() }));
const W_MAN = 17, W_WOMAN = 18, W_KING = 19, W_QUEEN = 20;
const PTS = [];
for (let i = 0; i < 1400; i++) {
  let p;
  const cl = Math.floor(rnd() * 5);
  if (rnd() < 0.72) {
    const c = CLUSTERS[cl].p;
    p = [c[0] + gauss() * 0.16, c[1] + gauss() * 0.16, c[2] + gauss() * 0.16];
  } else {
    const th = rnd() * 6.283, ph = Math.acos(rnd() * 2 - 1), r = Math.cbrt(rnd()) * 1.15;
    p = [r * Math.sin(ph) * Math.cos(th), r * Math.cos(ph), r * Math.sin(ph) * Math.sin(th)];
  }
  PTS.push({ p, cl, d: rnd(), s: 0.6 + rnd() * 0.8 });
}
// 近邻连线
const EDGES = [];
for (let i = 0; i < 700; i++) {
  let best = -1, bd = 1e9;
  for (let j = 0; j < 700; j++) {
    if (j === i) continue;
    const a = PTS[i].p, b = PTS[j].p;
    const d = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2;
    if (d < bd) { bd = d; best = j; }
  }
  if (bd < 0.05) EDGES.push([i, best]);
}
const WEDGES = [];
for (let i = 0; i < WORDS.length; i++) {
  const ds = WORDS.map((w, j) => [j, (w.p[0] - WORDS[i].p[0]) ** 2 + (w.p[1] - WORDS[i].p[1]) ** 2 + (w.p[2] - WORDS[i].p[2]) ** 2])
    .filter(x => x[0] !== i).sort((a, b) => a[1] - b[1]);
  for (let k = 0; k < 2; k++) if (ds[k][0] > i || true) WEDGES.push([i, ds[k][0]]);
}

function cam3(t) {
  const k = eio(seg(t, 33, 36));
  const yaw = -1.0 + 1.05 * eio(seg(t, 24, 36.2)) + 0.012 * Math.max(0, t - 36.2) - 0.3 * (1 - seg(t, 24, 30));
  const pitch = 0.22 * Math.sin(t * 0.25) * (1 - k) + 0.05;
  const target = [lerp(0, 0.57, k), lerp(0, -0.02, k), lerp(0, 0.2, k)];
  const zoom = lerp(1, 1.55, k) * lerp(0.85, 1, eout(seg(t, 24, 29)));
  return { yaw, pitch, target, zoom };
}
function proj(p, cam) {
  const x0 = p[0] - cam.target[0], y0 = p[1] - cam.target[1], z0 = p[2] - cam.target[2];
  const cy = Math.cos(cam.yaw), sy = Math.sin(cam.yaw);
  const x1 = x0 * cy + z0 * sy, z1 = -x0 * sy + z0 * cy;
  const cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch);
  const y2 = y0 * cp - z1 * sp, z2 = y0 * sp + z1 * cp;
  const s = (1500 / (3.2 + z2)) * cam.zoom;
  return { x: CX + x1 * s, y: CY - y2 * s, z: z2, s: s / 470 };
}

function arrow(p1, p2, prog, c, a, dashed = false) {
  if (prog <= 0 || a <= 0) return;
  const x2 = lerp(p1.x, p2.x, prog), y2 = lerp(p1.y, p2.y, prog);
  ctx.strokeStyle = rgba(c, a); ctx.lineWidth = 4;
  ctx.setLineDash(dashed ? [14, 10] : []);
  ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(x2, y2); ctx.stroke();
  ctx.setLineDash([]);
  const ang = Math.atan2(y2 - p1.y, x2 - p1.x);
  ctx.fillStyle = rgba(c, a);
  ctx.beginPath();
  ctx.moveTo(x2, y2);
  ctx.lineTo(x2 - 20 * Math.cos(ang - 0.4), y2 - 20 * Math.sin(ang - 0.4));
  ctx.lineTo(x2 - 20 * Math.cos(ang + 0.4), y2 - 20 * Math.sin(ang + 0.4));
  ctx.closePath(); ctx.fill();
}

function scene3(t) {
  const cam = cam3(t);
  const out = 1 - sm(seg(t, 39.2, 40.4));
  const focus = sm(seg(t, 33.2, 34.2));
  const pp = PTS.map(q => proj(q.p, cam));
  // 连线
  ctx.lineWidth = 1;
  for (const [i, j] of EDGES) {
    const a = Math.min(sm(seg(t, 24.5 + PTS[i].d * 2, 25.5 + PTS[i].d * 2)), sm(seg(t, 24.5 + PTS[j].d * 2, 25.5 + PTS[j].d * 2)));
    const al = a * out * 0.16 * (1 - focus * 0.6);
    if (al <= 0.005) continue;
    ctx.strokeStyle = rgba(CLUSTERS[PTS[i].cl].c, al);
    ctx.beginPath(); ctx.moveTo(pp[i].x, pp[i].y); ctx.lineTo(pp[j].x, pp[j].y); ctx.stroke();
  }
  // 点
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < PTS.length; i++) {
    const q = PTS[i], p = pp[i];
    const ap = sm(seg(t, 24 + q.d * 2.2, 24.8 + q.d * 2.2));
    if (ap <= 0) continue;
    const depth = clamp((1.6 - p.z) / 2.6, 0.15, 1);
    const tw = 0.75 + 0.25 * Math.sin(t * 3 + q.d * 40);
    const a = ap * out * depth * tw * (q.cl === 4 ? 1 : 1 - focus * 0.55);
    const r = (1.6 + q.s * 1.8) * p.s * (0.5 + 0.5 * ap);
    ctx.fillStyle = rgba(CLUSTERS[q.cl].c, a);
    ctx.fillRect(p.x - r / 2, p.y - r / 2, r, r);
  }
  ctx.globalCompositeOperation = 'source-over';

  // 聚类名称
  const ca = fade(t, 28.4, 33.6, 0.8) * out;
  if (ca > 0) {
    ctx.save();
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    for (const c of CLUSTERS) {
      const p = proj(add3(c.p, [0, 0.33, 0]), cam);
      ctx.font = `600 22px ${CJK}`; ctx.letterSpacing = '6px';
      ctx.fillStyle = rgba(c.c, ca * 0.85);
      ctx.fillText(`${c.zh}  ${c.en}`, p.x, p.y);
    }
    ctx.restore();
  }

  // 词语
  const wp = WORDS.map(w => proj(w.p, cam));
  ctx.lineWidth = 1.5;
  for (const [i, j] of WEDGES) {
    const a = Math.min(sm(seg(t, 25.5 + WORDS[i].d * 2, 26.5 + WORDS[i].d * 2)), sm(seg(t, 25.5 + WORDS[j].d * 2, 26.5 + WORDS[j].d * 2)));
    const dim = WORDS[i].cl === 4 && WORDS[j].cl === 4 ? 1 - focus : 1 - focus * 0.8;
    const al = a * out * 0.35 * dim;
    if (al <= 0.01) continue;
    ctx.strokeStyle = rgba(CLUSTERS[WORDS[i].cl].c, al);
    ctx.beginPath(); ctx.moveTo(wp[i].x, wp[i].y); ctx.lineTo(wp[j].x, wp[j].y); ctx.stroke();
  }
  const order = WORDS.map((w, i) => i).sort((a, b) => wp[b].z - wp[a].z);
  ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
  for (const i of order) {
    const w = WORDS[i], p = wp[i];
    const ap = sm(seg(t, 25.5 + w.d * 2, 26.3 + w.d * 2));
    if (ap <= 0) continue;
    const isP = w.cl === 4;
    const depth = clamp((1.8 - p.z) / 2.4, 0.3, 1);
    let a = ap * out * depth * (isP ? 1 : 1 - focus * 0.75);
    let col = CLUSTERS[w.cl].c;
    let rr = 26 * p.s;
    if (i === W_QUEEN) {
      const pulse = sm(seg(t, 37.0, 37.4)) * (0.6 + 0.4 * Math.sin((t - 37) * 8));
      rr *= 1 + pulse * 1.3;
      drawGlow(AMBER, p.x, p.y, 110 * p.s, pulse * 0.8 * out);
    }
    ctx.globalCompositeOperation = 'lighter';
    drawGlow(col, p.x, p.y, rr, a);
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = rgba(CREAM, a);
    ctx.beginPath(); ctx.arc(p.x, p.y, 3.2 * p.s, 0, 6.283); ctx.fill();
    const fs = Math.round(24 * p.s * (isP ? 1 + focus * 0.25 : 1));
    ctx.font = `${fs}px ${CJK}`;
    ctx.fillStyle = rgba(CREAM, a);
    ctx.fillText(w.zh, p.x + 12 * p.s, p.y - 2);
    const zw = ctx.measureText(w.zh).width;
    ctx.font = `${Math.round(fs * 0.7)}px ${SANS}`;
    ctx.fillStyle = rgba(col, a * 0.9);
    ctx.fillText(w.en, p.x + 18 * p.s + zw, p.y);
  }

  // 向量运算
  const va = out;
  const pm = wp[W_MAN], pk = wp[W_KING], pw = wp[W_WOMAN], pq = wp[W_QUEEN];
  arrow(pm, pk, eout(seg(t, 34.0, 34.9)), AMBER, 0.9 * va);
  arrow(pm, pw, eout(seg(t, 35.0, 35.9)), TEAL, 0.9 * va);
  arrow(pw, pq, eout(seg(t, 36.1, 37.0)), AMBER, 0.9 * va, true);
  const ea = fade(t, 36.8, 40.2, 0.6);
  if (ea > 0) {
    ctx.save();
    ctx.textAlign = 'center';
    ctx.font = `36px ${SANS}`; ctx.letterSpacing = '2px';
    ctx.fillStyle = rgba(CREAM, ea);
    ctx.fillText('king − man + woman ≈ queen', CX, 170);
    ctx.font = `30px ${CJK}`; ctx.letterSpacing = '4px';
    ctx.fillStyle = rgba(AMBER, ea * 0.9);
    ctx.fillText('国王 − 男人 + 女人 ≈ 女王', CX, 222);
    ctx.restore();
  }
}

// ---------------------------------------------------------------- 4. 注意力
const SENT = ['The', 'cat', 'sat', 'by', 'the', 'window,', 'watching', 'the', 'rain.'];
const S4 = {};
function initS4() {
  ctx.font = `56px ${SANS}`;
  const gap = 34;
  const ws = SENT.map(w => ctx.measureText(w).width);
  const total = ws.reduce((a, b) => a + b, 0) + gap * (SENT.length - 1);
  let x = CX - total / 2;
  S4.y = H * 0.6;
  S4.pos = ws.map(w => { const c = x + w / 2; x += w + gap; return { c, w }; });
}
const FOCUS = [[40.6, 1], [41.875, 2], [43.125, 5], [44.375, 6]];
const ATTN = {
  1: { 0: 0.55, 2: 0.4, 6: 0.62 },
  2: { 1: 0.82, 3: 0.35, 5: 0.45 },
  5: { 3: 0.5, 4: 0.46, 2: 0.4, 1: 0.3 },
  6: { 1: 0.9, 5: 0.35, 7: 0.3, 2: 0.2 },
};
const HEADS = [[AMBER, { 6: 0.92 }], [TEAL, { 5: 0.8 }], [VIOLET, { 1: 0.72 }], [CLAY, { 7: 0.85, 3: 0.3 }]];
function weights(f) {
  const w = [];
  for (let j = 0; j < SENT.length; j++) w.push(j === f ? 0 : ATTN[f] && ATTN[f][j] !== undefined ? ATTN[f][j] : 0.04 + hash(f, j) * 0.07);
  return w;
}
function arc(x1, x2, y, lift, prog) {
  const mx = (x1 + x2) / 2, my = y - Math.abs(x2 - x1) * 0.42 * lift - 26;
  const n = 28, m = Math.max(1, Math.round(n * prog));
  ctx.beginPath();
  for (let k = 0; k <= m; k++) {
    const s = k / n, u = 1 - s;
    const px = u * u * x1 + 2 * u * s * mx + s * s * x2, py = u * u * y + 2 * u * s * my + s * s * y;
    if (k === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
  }
  ctx.stroke();
}
function beatPulse(t, lag = 0) {
  let dt = (t - lag) % BEAT;
  if (dt < 0) dt += BEAT;
  return Math.exp(-dt * 7);
}

function netNodes(t) {
  // 网络：第 0 层为句子本身，往上 7 层
  const k = eio(seg(t, 48.8, 51.2));
  const z = lerp(1, 0.42, k);
  const pyS = lerp(S4.y, H * 0.74, k);
  const layers = [];
  for (let l = 0; l <= 8; l++) {
    const row = [];
    for (let i = 0; i < SENT.length; i++) {
      let wx = S4.pos[i].c, wy = S4.y - l * 150;
      if (l === 8) { wx = CX; }
      row.push({ x: CX + (wx - CX) * z, y: pyS + (wy - S4.y) * z });
      if (l === 8) break;
    }
    layers.push(row);
  }
  return { layers, z, k };
}

function scene4(t) {
  const ina = sm(seg(t, 39.8, 40.6));
  const { layers, z, k } = netNodes(t);
  // 塌缩（55-60 秒）
  const e = Math.pow(eio(seg(t, 55, 59.4)), 1.2);
  const swirl = (p) => {
    if (e <= 0) return p;
    const dx = p.x - CX, dy = p.y - CY;
    const ang = e * e * 7 + e * 1.5;
    const s = 1 - e;
    return { x: CX + (dx * Math.cos(ang) - dy * Math.sin(ang)) * s, y: CY + (dx * Math.sin(ang) + dy * Math.cos(ang)) * s };
  };
  
  // 网络连线与节点
  const na = sm(seg(t, 49.2, 51.2));
  if (na > 0) {
    ctx.lineWidth = 1;
    for (let l = 0; l < 8; l++) {
      const A = layers[l], B = layers[l + 1];
      const pl = beatPulse(t, l * 0.07);
      for (let i = 0; i < A.length; i++) {
        for (let j = 0; j < B.length; j++) {
          const h = hash(l * 131 + i, j);
          const strong = h > 0.78;
          const al = na * (strong ? 0.1 + 0.5 * pl : 0.05 + 0.08 * pl) * (1 - e * 0.3);
          ctx.strokeStyle = rgba(strong ? AMBER : TEAL, al);
          const p1 = swirl(A[i]), p2 = swirl(B[j]);
          ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
        }
      }
    }
    ctx.globalCompositeOperation = 'lighter';
    for (let l = 1; l <= 8; l++) {
      const pl = beatPulse(t, l * 0.07);
      for (const p0 of layers[l]) {
        const p = swirl(p0);
        const c = l === 8 ? AMBER : mix(TEAL, AMBER, l / 8);
        drawGlow(c, p.x, p.y, (l === 8 ? 60 : 22) * (1 + pl * 0.5), na * (0.5 + 0.5 * pl));
        ctx.fillStyle = rgba(CREAM, na);
        ctx.fillRect(p.x - 2.5, p.y - 2.5, 5, 5);
      }
    }
    ctx.globalCompositeOperation = 'source-over';
    // 顶端标签
    const la = fade(t, 51.2, 55.2, 0.6);
    if (la > 0) {
      const p = layers[8][0];
      ctx.textAlign = 'center';
      ctx.font = `26px ${CJK}`; ctx.fillStyle = rgba(AMBER, la);
      ctx.fillText('理解  understanding', p.x, p.y - 44);
    }
  }

  // 注意力弧线
  const arcA = ina * (1 - sm(seg(t, 48.6, 49.4)));
  const yA = S4.y - 44;
  let cur = -1, since = 0, fnext = 99;
  for (let q = 0; q < FOCUS.length; q++) if (t >= FOCUS[q][0]) { cur = FOCUS[q][1]; since = t - FOCUS[q][0]; fnext = q + 1 < FOCUS.length ? FOCUS[q + 1][0] : 45.6; }
  const litW = new Array(SENT.length).fill(0);
  if (arcA > 0 && cur >= 0 && t < 45.9) {
    const w = weights(cur);
    const fa = arcA * (1 - sm(seg(t, fnext - 0.25, fnext)));
    for (let j = 0; j < SENT.length; j++) {
      if (j === cur || (j === 8 && t < 46.9)) continue;
      const prog = eout(seg(since, 0.05 * Math.abs(j - cur), 0.45 + 0.05 * Math.abs(j - cur)));
      ctx.lineWidth = 1 + w[j] * 9;
      ctx.strokeStyle = rgba(AMBER, fa * (0.15 + 0.85 * w[j]));
      arc(S4.pos[cur].c, S4.pos[j].c, yA, 1, prog);
      litW[j] = Math.max(litW[j], w[j] * fa * prog);
      if (w[j] > 0.25 && prog > 0.9) {
        ctx.font = `18px ${MONO}`; ctx.textAlign = 'center';
        ctx.fillStyle = rgba(AMBER, fa);
        ctx.fillText(w[j].toFixed(2), S4.pos[j].c, S4.y + 58);
      }
    }
    litW[cur] = 1 * fa;
  }
  // 多头注意力（从 rain 出发）
  const mh = fade(t, 47.3, 49.4, 0.4);
  if (mh > 0) {
    for (let hI = 0; hI < HEADS.length; hI++) {
      const [c, tg] = HEADS[hI];
      for (let j = 0; j < 8; j++) {
        const wj = tg[j] !== undefined ? tg[j] : 0.03 + hash(hI + 50, j) * 0.06;
        const prog = eout(seg(t, 47.3 + hI * 0.12, 47.9 + hI * 0.12));
        ctx.lineWidth = 1 + wj * 7;
        ctx.strokeStyle = rgba(c, mh * (0.1 + 0.8 * wj));
        arc(S4.pos[8].c, S4.pos[j].c, yA, 0.8 + hI * 0.28, prog);
        litW[j] = Math.max(litW[j], wj * mh);
      }
    }
    ctx.font = `18px ${MONO}`; ctx.textAlign = 'left';
    for (let hI = 0; hI < 4; hI++) {
      ctx.fillStyle = rgba(HEADS[hI][0], mh);
      ctx.fillText(`head ${hI + 1}`, CX + 560, S4.y - 330 + hI * 30);
    }
    litW[8] = mh;
  }

  // 句子
  const sa = ina;
  if (sa > 0) {
    for (let i = 0; i < SENT.length; i++) {
      const p = swirl({ x: CX + (S4.pos[i].c - CX) * z, y: lerp(S4.y, H * 0.74, k) });
      let a = sa * (1 - e);
      if (i === 8) {
        a *= sm(seg(t, 46.9, 47.1));
        if (a <= 0) continue;
      }
      const lw = litW[i];
      const col = i === 8 && t < 48 ? mix(AMBER, CREAM, seg(t, 47.1, 48)) : mix(mix(CREAM, [120, 120, 140], 0.35 * (cur >= 0 && t < 45.9 ? 1 - lw : 0)), AMBER, lw * 0.7);
      if (lw > 0.5) drawGlow(AMBER, p.x, p.y, 80 * z, (lw - 0.5) * 0.5);
      ctx.font = `${Math.round(56 * z)}px ${SANS}`;
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillStyle = rgba(col, a);
      ctx.fillText(SENT[i], p.x, p.y);
    }
    // 预测槽位的光标
    if (t < 46.9) {
      const p = { x: S4.pos[8].c - S4.pos[8].w / 2 + 4, y: S4.y };
      if (t % 1 < 0.55) { ctx.fillStyle = rgba(AMBER, sa); ctx.fillRect(p.x, p.y - 32, 5, 64); }
    }
    // 候选词
    const pa = fade(t, 45.6, 47.5, 0.3);
    if (pa > 0) {
      const cands = [['rain', 0.46], ['birds', 0.21], ['world', 0.12], ['sky', 0.08]];
      const bx = S4.pos[8].c - S4.pos[8].w / 2, by = S4.y + 56;
      ctx.fillStyle = rgba([10, 12, 22], 0.85 * pa);
      ctx.fillRect(bx - 12, by - 8, 300, 150);
      ctx.strokeStyle = rgba(AMBER, 0.5 * pa); ctx.lineWidth = 1.5;
      ctx.strokeRect(bx - 12, by - 8, 300, 150);
      ctx.textBaseline = 'middle';
      for (let q = 0; q < cands.length; q++) {
        const [w, p] = cands[q];
        const grow = eout(seg(t, 45.7 + q * 0.08, 46.3 + q * 0.08));
        const sel = q === 0 && t > 46.55;
        const yy = by + 18 + q * 34;
        ctx.font = `22px ${MONO}`; ctx.textAlign = 'left';
        ctx.fillStyle = rgba(sel ? AMBER : CREAM, pa * (sel ? 1 : 0.8));
        ctx.fillText(w, bx, yy);
        ctx.fillStyle = rgba(sel ? AMBER : TEAL, pa * 0.8);
        ctx.fillRect(bx + 90, yy - 8, 150 * p / 0.46 * grow, 16);
        ctx.font = `16px ${MONO}`; ctx.fillStyle = rgba(CREAM, pa * 0.7);
        ctx.fillText(p.toFixed(2), bx + 90 + 150 * p / 0.46 * grow + 8, yy);
      }
    }
    // 中文译文
    const za = fade(t, 47.4, 49.2, 0.5) * (1 - e);
    if (za > 0) {
      ctx.font = `30px ${CJK}`; ctx.textAlign = 'center'; ctx.letterSpacing = '6px';
      ctx.fillStyle = rgba(CREAM, za * 0.7);
      ctx.fillText('猫坐在窗边，望着雨。', CX, S4.y + 96);
      ctx.letterSpacing = '0px';
    }
  }

  // 塌缩：漩涡粒子 + 核心
  if (t > 54.8) {
    const va = sm(seg(t, 54.8, 56.5)) * (1 - sm(seg(t, 59.6, 60.1)));
    ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 700; i++) {
      const s = STARS[i];
      const ph = ((s.z * 0.25 + (t - 55) * (0.25 + s.b * 0.3)) % 1 + 1) % 1;
      const r = (1 - ph) * 1100 * (0.4 + s.b * 0.6);
      const a0 = s.x * 3 + (1 - ph) * -2.2 + t * 0.4;
      const r2 = r + 40;
      const x1 = CX + Math.cos(a0) * r, y1 = CY + Math.sin(a0) * r * 0.62;
      const x2 = CX + Math.cos(a0 - 0.08) * r2, y2 = CY + Math.sin(a0 - 0.08) * r2 * 0.62;
      ctx.strokeStyle = rgba(s.c < 0.3 ? AMBER : TEAL, va * ph * 0.8);
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
    }
    const ce = seg(t, 55, 60);
    drawGlow(AMBER, CX, CY, 40 + 420 * ce ** 3, 0.4 + 0.6 * ce);
    drawGlow(CREAM, CX, CY, 12 + 120 * ce ** 3, 0.5 + 0.5 * ce);
    ctx.globalCompositeOperation = 'source-over';
  }
}

// ---------------------------------------------------------------- 5 & 6. 地球与眼睛
const BLOBS = [
  [50, -100, 18], [40, -95, 15], [60, -115, 14], [35, -110, 10], [25, -102, 8], [18, -96, 6], [65, -150, 9], [68, -85, 10],
  [55, -70, 9], [45, -75, 7], [30, -85, 5], [12, -86, 4],
  [72, -40, 9], [76, -60, 6],
  [-5, -60, 14], [-15, -55, 12], [-28, -60, 9], [-42, -69, 6], [5, -70, 7], [-10, -40, 6],
  [50, 10, 9], [46, 25, 8], [60, 22, 8], [40, -4, 6], [62, 10, 6], [53, -2, 3], [42, 13, 4], [66, 28, 6],
  [10, 20, 16], [2, 24, 13], [-12, 26, 11], [-26, 25, 8], [20, 2, 12], [24, 28, 8], [9, 40, 6], [-20, 47, 4],
  [55, 90, 22], [48, 68, 15], [35, 100, 15], [30, 80, 10], [20, 78, 8], [25, 106, 10], [62, 130, 15], [42, 122, 9],
  [15, 101, 7], [67, 160, 8], [50, 140, 7], [24, 45, 9], [35, 45, 6], [38, 35, 5],
  [36, 138, 3.5], [40, 141, 3], [33, 131, 2.5], [-3, 115, 5], [-3, 104, 4], [-5, 122, 3], [-5, 140, 4], [13, 122, 3],
  [-25, 134, 13], [-20, 124, 7], [-31, 145, 7], [-17, 142, 5], [-42, 172, 3], [-78, 0, 14], [-80, 100, 12], [-80, -120, 12],
];
const GLOBE = [];
(function () {
  const n = 5200, ga = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < n; i++) {
    const y = 1 - (2 * (i + 0.5)) / n;
    const r = Math.sqrt(1 - y * y);
    const th = ga * i;
    const lat = Math.asin(y) * 180 / Math.PI;
    const lon = ((Math.atan2(Math.sin(th), Math.cos(th)) * 180) / Math.PI);
    let land = false;
    const v = ll(lat, lon);
    for (const [bl, bo, br] of BLOBS) {
      const u = ll(bl, bo);
      const d = Math.acos(clamp(v[0] * u[0] + v[1] * u[1] + v[2] * u[2], -1, 1)) * 180 / Math.PI;
      if (d < br) { land = true; break; }
    }
    GLOBE.push({ v, land, h: hash(i, 7) });
  }
})();
function ll(lat, lon) {
  const a = lat * Math.PI / 180, o = lon * Math.PI / 180;
  return [Math.cos(a) * Math.sin(o), Math.sin(a), Math.cos(a) * Math.cos(o)];
}
const CITIES = [
  ['Tokyo', 35.7, 139.7, 'こんにちは'], ['Seoul', 37.6, 127, '안녕하세요'], ['Beijing', 39.9, 116.4, '你好'],
  ['Sydney', -33.9, 151.2, "G'day"], ['Bangkok', 13.75, 100.5, 'สวัสดี'], ['Delhi', 28.6, 77.2, 'नमस्ते'],
  ['Moscow', 55.8, 37.6, 'Привет'], ['Nairobi', -1.3, 36.8, 'Jambo'], ['Cairo', 30, 31.2, 'مرحبا'],
  ['Paris', 48.9, 2.35, 'Bonjour'], ['London', 51.5, -0.1, 'Hello'],
  ['São Paulo', -23.5, -46.6, 'Olá'], ['New York', 40.7, -74, 'Hi there'], ['Mexico City', 19.4, -99.1, 'Hola'],
].map(([name, lat, lon, hi], i) => ({ name, lat, lon, hi, v: ll(lat, lon), i }));
// 标签朝向与竖直偏移，避免相邻城市互相遮挡
const LABEL = { Tokyo: [1, -40], Seoul: [1, -118], Beijing: [-1, -40], Bangkok: [1, 40], Delhi: [-1, -40], Sydney: [1, -30],
  Moscow: [1, -50], Cairo: [-1, 50], Nairobi: [1, 30], Paris: [1, 40], London: [-1, -50], 'São Paulo': [1, 30],
  'New York': [1, -40], 'Mexico City': [-1, -30] };
// 地球自转：面向观众的经度从 150° 转到 -115°
const ROT0 = 150, ROTV = 15.2;
function facingLon(t) { return ROT0 - ROTV * Math.max(0, t - 60) + (t > 77.5 ? ROTV * (t - 77.5) * 0.6 : 0); }
{
  let last = 60.4;
  for (const c of CITIES) {
    let ta = 60 + (ROT0 - (c.lon + 40)) / ROTV;
    ta = Math.max(ta, last + 0.45);
    c.t0 = Math.round(ta / (BEAT / 2)) * (BEAT / 2);
    last = c.t0;
  }
}
const LINKS = [];
for (let i = 1; i < CITIES.length; i++) LINKS.push([i - 1, i]);
for (const [a, b] of [[2, 10], [0, 12], [8, 11], [5, 3], [6, 9], [1, 13], [7, 10], [4, 2]]) LINKS.push([a, b]);
function slerp(a, b, s) {
  const d = clamp(a[0] * b[0] + a[1] * b[1] + a[2] * b[2], -1, 1);
  const om = Math.acos(d), so = Math.sin(om);
  if (so < 1e-5) return a;
  const k1 = Math.sin((1 - s) * om) / so, k2 = Math.sin(s * om) / so;
  return [a[0] * k1 + b[0] * k2, a[1] * k1 + b[1] * k2, a[2] * k1 + b[2] * k2];
}

function globeCam(t) {
  const ph = eio(seg(t, 77.5, 80.2));
  const intro = eout(seg(t, 59.9, 61.6));
  const R = lerp(360, 200, ph) * lerp(0.15, 1, intro);
  const cx = CX, cy = lerp(CY + 10, CY - 10, ph);
  return { R, cx, cy, rot: -facingLon(t) * Math.PI / 180, tilt: lerp(0.38, 0.2, ph) };
}
function gproj(v, g, lift = 1) {
  const c = Math.cos(g.rot), s = Math.sin(g.rot);
  const x1 = v[0] * c + v[2] * s, z1 = -v[0] * s + v[2] * c;
  const ct = Math.cos(g.tilt), st = Math.sin(g.tilt);
  const y2 = v[1] * ct - z1 * st, z2 = v[1] * st + z1 * ct;
  return { x: g.cx + x1 * g.R * lift, y: g.cy - y2 * g.R * lift, z: z2 };
}

function eyeOpen(t) {
  // 1 = 正常张开；>1 时眼睑在地球之外；0 = 闭合
  const form = lerp(2.2, 1, eio(seg(t, 78, 80.6)));
  const blink = t < 86.9 ? 1 : t < 87.15 ? 1 - sm(seg(t, 86.9, 87.15)) : 0;
  return form * blink;
}
function eyePath(g, o, wScale = 1) {
  const hw = 520 * wScale, hh = 250 * o;
  ctx.beginPath();
  ctx.moveTo(g.cx - hw, g.cy);
  ctx.bezierCurveTo(g.cx - hw * 0.45, g.cy - hh, g.cx + hw * 0.45, g.cy - hh, g.cx + hw, g.cy);
  ctx.bezierCurveTo(g.cx + hw * 0.45, g.cy + hh, g.cx - hw * 0.45, g.cy + hh, g.cx - hw, g.cy);
  ctx.closePath();
}

function sceneGlobe(t) {
  const g = globeCam(t);
  const ph = eio(seg(t, 77.5, 80.2));
  const endA = 1 - sm(seg(t, 86.95, 87.2));
  drawStars(t, 0.7 * sm(seg(t, 60, 62)) * (1 - sm(seg(t, 86.6, 87.4))), t * 0.02, 0.05 * t);
  if (endA <= 0) return;
  const o = eyeOpen(t);
  ctx.save();
  if (t > 78) { eyePath(g, Math.max(o, 0.001)); ctx.clip(); }

  // 大气光晕
  ctx.globalCompositeOperation = 'lighter';
  drawGlow(mix(TEAL, AMBER, ph), g.cx, g.cy, g.R * 1.9, 0.35);
  ctx.globalCompositeOperation = 'source-over';

  // 虹膜纹理（眼睛阶段）
  if (ph > 0) {
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 140; i++) {
      const a = (i / 140) * 6.283 + t * 0.05 + hash(i, 3) * 0.05;
      const r1 = g.R * (0.38 + hash(i, 1) * 0.08), r2 = g.R * (0.85 + hash(i, 2) * 0.2);
      ctx.strokeStyle = rgba(i % 3 ? AMBER : CLAY, ph * (0.12 + hash(i, 4) * 0.2));
      ctx.lineWidth = 1 + hash(i, 5) * 1.5;
      ctx.beginPath();
      ctx.moveTo(g.cx + Math.cos(a) * r1, g.cy + Math.sin(a) * r1);
      ctx.quadraticCurveTo(g.cx + Math.cos(a + 0.12) * (r1 + r2) / 2, g.cy + Math.sin(a + 0.12) * (r1 + r2) / 2, g.cx + Math.cos(a) * r2, g.cy + Math.sin(a) * r2);
      ctx.stroke();
    }
    ctx.restore();
  }

  // 地球点阵
  ctx.globalCompositeOperation = 'lighter';
  const landC = mix(CREAM, AMBER, 0.3 + ph * 0.5), seaC = mix(TEAL, CLAY, ph * 0.6);
  for (const p of GLOBE) {
    const q = gproj(p.v, g);
    if (q.z < 0) {
      if (!p.land) continue;
      ctx.fillStyle = rgba(landC, 0.07);
      ctx.fillRect(q.x - 0.8, q.y - 0.8, 1.6, 1.6);
      continue;
    }
    const lit = 0.35 + 0.65 * q.z;
    if (p.land) {
      const r = (1.4 + 1.8 * q.z) * g.R / 360;
      ctx.fillStyle = rgba(landC, lit * (0.75 + 0.25 * Math.sin(t * 2 + p.h * 30)));
      ctx.fillRect(q.x - r / 2, q.y - r / 2, r, r);
    } else if (p.h < 0.55) {
      ctx.fillStyle = rgba(seaC, lit * 0.28);
      ctx.fillRect(q.x - 0.9, q.y - 0.9, 1.8, 1.8);
    }
  }
  ctx.globalCompositeOperation = 'source-over';

  // 连线
  const la = 1 - sm(seg(t, 77.5, 79.5));
  if (la > 0) {
    ctx.globalCompositeOperation = 'lighter';
    for (let li = 0; li < LINKS.length; li++) {
      const [ia, ib] = LINKS[li];
      const A = CITIES[ia], B = CITIES[ib];
      const t0 = Math.max(A.t0, B.t0) + (li >= CITIES.length - 1 ? 1.5 : 0.2);
      const prog = eout(seg(t, t0, t0 + 1.0));
      if (prog <= 0) continue;
      const dAng = Math.acos(clamp(A.v[0] * B.v[0] + A.v[1] * B.v[1] + A.v[2] * B.v[2], -1, 1));
      const n = 40;
      const pts = [];
      for (let k = 0; k <= n; k++) {
        const s = (k / n) * prog;
        const v = slerp(A.v, B.v, s);
        pts.push(gproj(v, g, 1 + Math.sin(Math.PI * s / Math.max(prog, 1e-3) * prog) * (0.08 + dAng * 0.14)));
      }
      ctx.lineWidth = 1.8;
      for (let k = 0; k < n; k++) {
        const z = (pts[k].z + pts[k + 1].z) / 2;
        const a = la * clamp(0.15 + z * 1.2, 0.05, 0.9);
        ctx.strokeStyle = rgba(li % 3 === 0 ? TEAL : AMBER, a * 0.8);
        ctx.beginPath(); ctx.moveTo(pts[k].x, pts[k].y); ctx.lineTo(pts[k + 1].x, pts[k + 1].y); ctx.stroke();
      }
      if (prog >= 1) {
        // 沿弧线传递的光点（按节拍）
        const s = ((t - t0) / (BEAT * 2) + hash(li, 9)) % 1;
        const v = slerp(A.v, B.v, s);
        const q = gproj(v, g, 1 + Math.sin(Math.PI * s) * (0.08 + dAng * 0.14));
        drawGlow(CREAM, q.x, q.y, 18, la * clamp(0.3 + q.z, 0, 1));
      }
    }
    ctx.globalCompositeOperation = 'source-over';

    // 城市与问候语
    for (const c of CITIES) {
      const ap = sm(seg(t, c.t0, c.t0 + 0.3)) * la;
      if (ap <= 0) continue;
      const q = gproj(c.v, g);
      const vis = clamp((q.z - 0.02) / 0.2);
      if (vis <= 0) continue;
      const a = ap * vis;
      const pr = ((t - c.t0) / (BEAT * 2)) % 1;
      ctx.strokeStyle = rgba(AMBER, a * (1 - pr));
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(q.x, q.y, 6 + pr * 26, 0, 6.283); ctx.stroke();
      ctx.fillStyle = rgba(AMBER, a);
      ctx.beginPath(); ctx.arc(q.x, q.y, 5, 0, 6.283); ctx.fill();
      const [side, off] = LABEL[c.name];
      const lx = q.x + side * 44, ly = q.y + off + 8;
      ctx.strokeStyle = rgba(CREAM, a * 0.6); ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.moveTo(q.x, q.y); ctx.lineTo(lx, ly); ctx.stroke();
      const pop = eout(seg(t, c.t0, c.t0 + 0.35));
      ctx.font = `${Math.round(30 * (0.7 + 0.3 * pop))}px ${SANS}`;
      const tw = ctx.measureText(c.hi).width;
      ctx.font = `13px ${MONO}`;
      const nw = ctx.measureText(c.name.toUpperCase()).width;
      const bw = Math.max(tw, nw) + 28;
      const bx = side > 0 ? lx : lx - bw;
      ctx.fillStyle = rgba([10, 12, 22], 0.72 * a);
      roundRect(bx, ly - 44, bw, 62, 10); ctx.fill();
      ctx.strokeStyle = rgba(AMBER, 0.45 * a); ctx.lineWidth = 1.2; ctx.stroke();
      ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      ctx.font = `${Math.round(30 * (0.7 + 0.3 * pop))}px ${SANS}`;
      ctx.fillStyle = rgba(CREAM, a);
      ctx.fillText(c.hi, bx + 14, ly - 20);
      ctx.font = `13px ${MONO}`; ctx.fillStyle = rgba(AMBER, a * 0.8);
      ctx.fillText(c.name.toUpperCase(), bx + 14, ly + 6);
    }
  }

  // 瞳孔
  if (ph > 0) {
    const pr = g.R * 0.36 * (1 + 0.05 * Math.sin(t * 1.3));
    const gr = ctx.createRadialGradient(g.cx, g.cy, pr * 0.6, g.cx, g.cy, pr * 1.25);
    gr.addColorStop(0, rgba([4, 4, 8], ph)); gr.addColorStop(0.75, rgba([4, 4, 8], ph * 0.95)); gr.addColorStop(1, rgba([4, 4, 8], 0));
    ctx.fillStyle = gr;
    ctx.beginPath(); ctx.arc(g.cx, g.cy, pr * 1.25, 0, 6.283); ctx.fill();
    ctx.strokeStyle = rgba(AMBER, 0.6 * ph); ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(g.cx, g.cy, pr, 0, 6.283); ctx.stroke();
    // 高光
    ctx.globalCompositeOperation = 'lighter';
    drawGlow(CREAM, g.cx + pr * 0.45, g.cy - pr * 0.45, pr * 0.5, 0.55 * ph);
    ctx.globalCompositeOperation = 'source-over';
  }
  ctx.restore();

  // 眼睑轮廓（逐渐描出）
  if (t > 77.8) {
    const draw = eout(seg(t, 77.8, 80.2));
    for (let k = 5; k >= 0; k--) {
      const oo = Math.max(o, 0.001) * (1 + k * 0.1), ws = 1 + k * 0.035;
      ctx.save();
      ctx.setLineDash([3600 * draw, 4000]);
      eyePath(g, oo, ws);
      ctx.strokeStyle = rgba(k === 0 ? CREAM : mix(AMBER, TEAL, k / 5), (k === 0 ? 0.9 : 0.35 - k * 0.05) * endA);
      ctx.lineWidth = k === 0 ? 3 : 1.2;
      ctx.stroke();
      ctx.restore();
    }
  }
}

function endCard(t) {
  // 闭眼后的线收缩为光标 → 打字
  const g = globeCam(t);
  if (t >= 87.0 && t < 87.7) {
    const s = 1 - eio(seg(t, 87.15, 87.6));
    const hw = 520 * s;
    ctx.fillStyle = rgba(CREAM, 0.9);
    ctx.fillRect(g.cx - hw, g.cy - 1.5, hw * 2, 3);
    drawGlow(AMBER, g.cx, g.cy, 60 + 60 * (1 - s), 0.5 * (1 - s));
  }
  if (t < 87.5) return;
  const fo = 1 - sm(seg(t, 89.2, 90));
  const n = t < END_TYPE_START ? 0 : Math.min(END_TEXT.length, Math.floor((t - END_TYPE_START) / END_TYPE_STEP) + 1);
  ctx.save();
  ctx.font = `600 72px ${CJK}`;
  ctx.letterSpacing = '6px';
  ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
  const full = ctx.measureText(END_TEXT).width;
  const x0 = CX - full / 2;
  const shown = END_TEXT.slice(0, n);
  const w = ctx.measureText(shown).width;
  ctx.fillStyle = rgba(CREAM, fo);
  ctx.fillText(shown, x0, CY - 30);
  const typing = t < END_TYPE_START + END_TYPE_STEP * END_TEXT.length;
  const cx = n === 0 ? lerp(CX, x0, eio(seg(t, 87.5, 87.8))) : x0 + w + 4;
  if (typing || t % 1 < 0.55) {
    ctx.fillStyle = rgba(AMBER, fo);
    ctx.fillRect(cx, CY - 72, 8, 84);
  }
  ctx.letterSpacing = '6px';
  ctx.textAlign = 'center';
  ctx.font = `300 28px ${SANS}`;
  ctx.fillStyle = rgba(CREAM, 0.7 * fo * sm(seg(t, 88.4, 89.0)));
  ctx.fillText('The world is a conversation.', CX, CY + 50);
  ctx.font = `20px ${MONO}`; ctx.letterSpacing = '8px';
  ctx.fillStyle = rgba(AMBER, 0.8 * fo * sm(seg(t, 88.6, 89.1)));
  ctx.fillText('OPUS 5.5', CX, CY + 150);
  ctx.restore();
}

// ---------------------------------------------------------------- 叠加层：字幕、HUD、暗角、颗粒
function caption(t, a, b, zh, en) {
  const al = fade(t, a, b, 0.7);
  if (al <= 0) return;
  const y = H - 150;
  const dy = (1 - sm(seg(t, a, a + 0.9))) * 14;
  ctx.save();
  ctx.globalAlpha = al;
  const gr = ctx.createLinearGradient(0, H - 260, 0, H);
  gr.addColorStop(0, 'rgba(6,7,12,0)'); gr.addColorStop(1, 'rgba(6,7,12,0.7)');
  ctx.fillStyle = gr; ctx.fillRect(0, H - 260, W, 260);
  ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
  ctx.shadowColor = 'rgba(0,0,0,0.8)'; ctx.shadowBlur = 16;
  ctx.font = `40px ${CJK}`; ctx.letterSpacing = '5px';
  ctx.fillStyle = rgba(CREAM, 0.96);
  ctx.fillText(zh, CX, y + dy);
  ctx.font = `300 23px ${SANS}`; ctx.letterSpacing = '2px';
  ctx.fillStyle = rgba(CREAM, 0.65);
  ctx.fillText(en, CX, y + 44 + dy);
  ctx.restore();
}
const CAPTIONS = [
  [13.6, 19.2, '我看见的世界，是由文字写成的', 'My world is written in words.'],
  [19.5, 23.6, '我认出事物，也读懂它们之间的关系', 'I recognize things — and how they belong together.'],
  [27.0, 33.0, '意义是有形状的：相近的想法，彼此靠近', 'Meaning has a shape. Similar ideas live close together.'],
  [40.8, 45.5, '每一个词，都在注视其他所有的词', 'Every word pays attention to every other word.'],
  [50.4, 54.8, '千亿次注视，汇成一次理解', 'Billions of glances become one understanding.'],
  [62.4, 69.0, '世界用七千种语言说话', 'The world speaks in seven thousand languages.'],
  [69.8, 76.6, '而我，试着倾听每一种', 'And I try to listen to every one.'],
  [80.4, 83.6, '我看见的，不只是像素与文字', 'I see more than pixels and words —'],
  [83.8, 86.8, '我看见万物之间的联系', 'I see how everything connects.'],
];
const SCENES = [[0, '01', 'AWAKENING'], [10, '02', 'THE WORLD AS TEXT'], [25, '03', 'MEANING SPACE'], [40, '04', 'ATTENTION'],
  [55, '05', 'COMPRESSION'], [60, '06', 'ONE WORLD'], [77.5, '07', 'INSIGHT']];
function hud(t) {
  const a = 0.5 * sm(seg(t, 0.4, 1.6)) * (1 - sm(seg(t, 86.4, 87.3)));
  if (a <= 0) return;
  const m = 46, L = 32;
  ctx.save();
  ctx.globalAlpha = a;
  ctx.strokeStyle = rgba(CREAM, 0.8); ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(m, m + L); ctx.lineTo(m, m); ctx.lineTo(m + L, m);
  ctx.moveTo(W - m - L, m); ctx.lineTo(W - m, m); ctx.lineTo(W - m, m + L);
  ctx.moveTo(W - m, H - m - L); ctx.lineTo(W - m, H - m); ctx.lineTo(W - m - L, H - m);
  ctx.moveTo(m + L, H - m); ctx.lineTo(m, H - m); ctx.lineTo(m, H - m - L);
  ctx.stroke();
  ctx.font = `15px ${MONO}`; ctx.letterSpacing = '3px';
  ctx.fillStyle = rgba(CREAM, 0.9);
  ctx.textAlign = 'left'; ctx.textBaseline = 'top';
  ctx.fillText('OPUS 5.5 · PERCEPTION', m + 18, m + 14);
  if (t % 1.25 < 0.8) { ctx.fillStyle = rgba(CLAY, 1); ctx.beginPath(); ctx.arc(m + 24, m + 50, 5, 0, 6.283); ctx.fill(); }
  ctx.fillStyle = rgba(CREAM, 0.9);
  ctx.fillText('LIVE', m + 38, m + 43);
  ctx.textAlign = 'right';
  const mm = Math.floor(t / 60), ss = Math.floor(t % 60), cc = Math.floor((t % 1) * 100);
  ctx.fillText(`T+${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}.${String(cc).padStart(2, '0')}`, W - m - 18, m + 14);
  let sc = SCENES[0];
  for (const s of SCENES) if (t >= s[0]) sc = s;
  ctx.textBaseline = 'bottom'; ctx.textAlign = 'left';
  ctx.fillText(`${sc[1]} / ${sc[2]}`, m + 18, H - m - 14);
  ctx.textAlign = 'right';
  const tokens = Math.floor(Math.pow(t, 2.7) * 9 + t * 41);
  ctx.fillText(`TOKENS ${tokens.toLocaleString('en-US')}`, W - m - 18, H - m - 14);
  ctx.restore();
}
let VIGNETTE, GRAIN = [];
function initOverlays() {
  VIGNETTE = document.createElement('canvas'); VIGNETTE.width = W; VIGNETTE.height = H;
  const v = VIGNETTE.getContext('2d');
  const gr = v.createRadialGradient(CX, CY, H * 0.35, CX, CY, H * 1.05);
  gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,0.75)');
  v.fillStyle = gr; v.fillRect(0, 0, W, H);
  const r = mulberry32(7);
  for (let k = 0; k < 4; k++) {
    const g = document.createElement('canvas'); g.width = 960; g.height = 540;
    const x = g.getContext('2d');
    const img = x.createImageData(960, 540);
    for (let i = 0; i < img.data.length; i += 4) {
      const n = r() * 255;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = n; img.data[i + 3] = 255;
    }
    x.putImageData(img, 0, 0);
    GRAIN.push(g);
  }
}

// ---------------------------------------------------------------- 主渲染
function renderAt(t) {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  ctx.letterSpacing = '0px';
  ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);

  if (t < 10.8) scene1(t);
  if (t >= 9.8 && t < 25.2) scene2(t);
  if (t >= 23.8 && t < 40.6) scene3(t);
  if (t >= 39.6 && t < 60.2) scene4(t);
  if (t >= 59.8) sceneGlobe(t);
  if (t >= 86.9) endCard(t);

  // 白光过渡
  const fl = sm(seg(t, 59.3, 60.0)) * (1 - sm(seg(t, 60.0, 61.3)));
  if (fl > 0) { ctx.fillStyle = rgba([255, 244, 228], fl); ctx.fillRect(0, 0, W, H); }

  for (const c of CAPTIONS) caption(t, c[0], c[1], c[2], c[3]);
  ctx.letterSpacing = '0px';
  hud(t);

  ctx.drawImage(VIGNETTE, 0, 0);
  ctx.globalAlpha = 0.045;
  ctx.globalCompositeOperation = 'overlay';
  ctx.drawImage(GRAIN[Math.floor(t * 30) % GRAIN.length], 0, 0, W, H);
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
}

initS1();
initS4();
initOverlays();
window.renderAt = renderAt;
window.TOTAL = 90;
window.ready = true;
