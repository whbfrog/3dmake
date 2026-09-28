// 用无头 Chromium 逐帧渲染 scene.html，并与 make_audio.py 生成的配乐合成 MP4。
// 用法：
//   node render.mjs                    → 输出 career_story.mp4
//   node render.mjs --preview 3,20,50  → 只导出这些时间点的 PNG 预览
import { spawn, execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const { chromium } = await import('/opt/node22/lib/node_modules/playwright/index.mjs');
const FPS = 30;
const args = process.argv.slice(2);
const previewIdx = args.indexOf('--preview');
const OUT = path.join(HERE, 'career_story_3d.mp4');

async function openPage() {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('console', m => { if (m.type() === 'error') console.error('[page]', m.text()); });
  page.on('pageerror', e => console.error('[pageerror]', e.message));
  await page.goto('file://' + path.join(HERE, 'scene.html'));
  await page.waitForFunction(() => window.ready === true);
  const info = await page.evaluate(() => window.build());
  return { browser, page, info };
}

if (previewIdx >= 0) {
  const dir = process.env.PREVIEW_DIR || HERE;
  const times = args[previewIdx + 1].split(',').map(Number);
  const { browser, page, info } = await openPage();
  console.log(JSON.stringify(info));
  for (const t of times) {
    await page.evaluate(tt => window.renderAt(tt), t);
    await page.screenshot({ path: path.join(dir, `prev_${t.toFixed(1).padStart(5, '0')}.png`) });
  }
  await browser.close();
  process.exit(0);
}

const ffmpeg = execFileSync('python3', ['-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())']).toString().trim();
const tmp = fs.mkdtempSync(path.join(process.env.TMPDIR || '/tmp', 'career3d-'));
const probe = await openPage();
const total = Math.round(probe.info.total * FPS);
// 铅笔沙沙声的时间包络交给音频脚本
const pen = await probe.page.evaluate(n => Array.from({ length: n }, (_, i) => window.penActivity(i / 30)), total);
const pops = await probe.page.evaluate(() => window.pops());
await probe.browser.close();
fs.writeFileSync(path.join(tmp, 'pen.json'), JSON.stringify({ fps: FPS, total: probe.info.total, pen, pops, scratch: 0.5, scenes: probe.info.scenes }));
const audio = spawn('python3', [path.join(HERE, '..', 'resume_video', 'make_audio.py'), path.join(tmp, 'pen.json'), path.join(tmp, 'audio.wav')], { stdio: 'inherit' });
const audioDone = new Promise(r => audio.on('close', r));

const WORKERS = Number(process.env.WORKERS || 4);
const per = Math.ceil(total / WORKERS);
await Promise.all(Array.from({ length: WORKERS }, async (_, w) => {
  const from = w * per, to = Math.min(total, from + per);
  const { browser, page } = await openPage();
  const seg = path.join(tmp, `seg${w}.mp4`);
  const ff = spawn(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', seg], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = from; i < to; i++) {
    await page.evaluate(t => window.renderAt(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((i - from) % 150 === 0) console.log(`worker ${w}: ${i - from}/${to - from}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
}));
await audioDone;
fs.writeFileSync(path.join(tmp, 'list.txt'), Array.from({ length: WORKERS }, (_, w) => `file 'seg${w}.mp4'`).join('\n'));
execFileSync(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', path.join(tmp, 'list.txt'), '-i', path.join(tmp, 'audio.wav'),
  '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT]);
console.log('done →', OUT);
