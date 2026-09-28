// 用无头 Chromium 逐帧渲染 scene.html，并与 make_music.py 合成的配乐一起编码成 MP4。
// 用法：
//   node render.mjs                      → 输出 opus_eyes.mp4（1920x1080, 30fps, 90s）
//   node render.mjs --preview 5,15,35    → 只导出这些时间点的 PNG 预览（目录由 PREVIEW_DIR 指定）
import { spawn, execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const require_ = (await import('node:module')).createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require_('playwright')); } catch { ({ chromium } = await import('/opt/node22/lib/node_modules/playwright/index.mjs')); }

const FPS = 30;
const TOTAL = 90;
const args = process.argv.slice(2);
const previewIdx = args.indexOf('--preview');
const outDir = process.env.PREVIEW_DIR || HERE;
const OUT = path.join(HERE, 'opus_eyes.mp4');

async function openPage() {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('console', m => { if (m.type() === 'error') console.error('[page]', m.text()); });
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  await page.goto('file://' + path.join(HERE, 'scene.html'));
  await page.waitForFunction(() => window.ready === true);
  return { browser, page };
}

if (previewIdx >= 0) {
  const times = args[previewIdx + 1].split(',').map(Number);
  const { browser, page } = await openPage();
  for (const t of times) {
    await page.evaluate(tt => window.renderAt(tt), t);
    await page.screenshot({ path: path.join(outDir, `f_${t.toFixed(2).padStart(6, '0')}.png`) });
  }
  await browser.close();
  process.exit(0);
}

// ---- 完整渲染：分成多个并行进程，每个进程编码一段
const ffmpeg = execFileSync('python3', ['-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())']).toString().trim();
const total = TOTAL * FPS;
const WORKERS = Number(process.env.WORKERS || 4);
const tmp = fs.mkdtempSync(path.join(process.env.TMPDIR || '/tmp', 'opus-'));
const chunk = Math.ceil(total / WORKERS);
let done = 0;
const t0 = Date.now();

await Promise.all(Array.from({ length: WORKERS }, async (_, w) => {
  const from = w * chunk, to = Math.min(total, from + chunk);
  const seg = path.join(tmp, `seg${w}.mp4`);
  const ff = spawn(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'mjpeg', '-r', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', seg], { stdio: ['pipe', 'inherit', 'inherit'] });
  const { browser, page } = await openPage();
  for (let i = from; i < to; i++) {
    await page.evaluate(t => window.renderAt(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    done++;
    if (done % 150 === 0) console.log(`  ${done}/${total} frames  (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
}));

const wav = path.join(tmp, 'music.wav');
execFileSync('python3', [path.join(HERE, 'make_music.py'), wav], { stdio: 'inherit' });
const list = path.join(tmp, 'list.txt');
fs.writeFileSync(list, Array.from({ length: WORKERS }, (_, w) => `file '${path.join(tmp, `seg${w}.mp4`)}'`).join('\n'));
execFileSync(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-i', wav,
  '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT], { stdio: 'inherit' });
fs.rmSync(tmp, { recursive: true, force: true });
console.log('done:', OUT, `(${((Date.now() - t0) / 1000).toFixed(0)}s)`);
