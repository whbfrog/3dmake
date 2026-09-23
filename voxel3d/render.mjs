// 用无头 Chromium 渲染 scene.html 的每一帧，并与合成音轨一起编码成 MP4。
// 用法：
//   node render.mjs                     → 输出 claude_vs_chatgpt_3d.mp4
//   node render.mjs --preview 10,30,50  → 只导出这些时间点的 PNG 预览
import { spawn, execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const require_ = (await import('node:module')).createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require_('playwright')); } catch { ({ chromium } = await import('/opt/node22/lib/node_modules/playwright/index.mjs')); }

const FPS = 24;
const story = JSON.parse(fs.readFileSync(path.join(HERE, 'story.json'), 'utf8'));
const args = process.argv.slice(2);
const previewIdx = args.indexOf('--preview');
const outDir = process.env.PREVIEW_DIR || HERE;
const OUT = path.join(HERE, 'claude_vs_chatgpt_3d.mp4');

const exe = fs.existsSync('/opt/pw-browsers/chromium') ? undefined : undefined;
async function openPage() {
  const browser = await chromium.launch({
    executablePath: exe,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--allow-file-access-from-files', '--disable-web-security'],
  });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  page.on('console', m => { if (m.type() === 'error') console.error('[page]', m.text()); });
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  await page.goto('file://' + path.join(HERE, 'scene.html'));
  await page.waitForFunction(() => window.ready === true);
  await page.evaluate(s => window.init(s), story);
  return { browser, page };
}

async function renderRange(page, from, to, onFrame) {
  for (let i = from; i < to; i++) {
    await page.evaluate(t => window.renderAt(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
    await onFrame(i, buf);
  }
}

if (previewIdx >= 0) {
  const times = args[previewIdx + 1].split(',').map(Number);
  const { browser, page } = await openPage();
  for (const t of times) {
    await page.evaluate(tt => window.renderAt(tt), t);
    await page.screenshot({ path: path.join(outDir, `f3d_${t.toFixed(2).padStart(6, '0')}.png`) });
  }
  await browser.close();
  process.exit(0);
}

// ---- full render: split into parallel workers, each encodes a segment
const ffmpeg = execFileSync('python3', ['-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())']).toString().trim();
const total = Math.round(story.total * FPS);
const WORKERS = Number(process.env.WORKERS || 3);
const tmp = fs.mkdtempSync(path.join(process.env.TMPDIR || '/tmp', 'vox-'));
const chunk = Math.ceil(total / WORKERS);
let done = 0;
const t0 = Date.now();

await Promise.all(Array.from({ length: WORKERS }, async (_, w) => {
  const from = w * chunk, to = Math.min(total, from + chunk);
  const seg = path.join(tmp, `seg${w}.mp4`);
  const ff = spawn(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-r', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', seg], { stdio: ['pipe', 'inherit', 'inherit'] });
  const { browser, page } = await openPage();
  await renderRange(page, from, to, async (i, buf) => {
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    done++;
    if (done % 120 === 0) console.log(`  ${done}/${total} frames  (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  });
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
}));

// audio (shared chiptune generator from the 2D version, with this story's lines)
const wav = path.join(tmp, 'audio.wav');
execFileSync('python3', [path.join(HERE, 'make_audio.py'), wav], { stdio: 'inherit' });
const list = path.join(tmp, 'list.txt');
fs.writeFileSync(list, Array.from({ length: WORKERS }, (_, w) => `file '${path.join(tmp, `seg${w}.mp4`)}'`).join('\n'));
execFileSync(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-i', wav,
  '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', OUT], { stdio: 'inherit' });
fs.rmSync(tmp, { recursive: true, force: true });
console.log('done:', OUT, `(${((Date.now() - t0) / 1000).toFixed(0)}s)`);
