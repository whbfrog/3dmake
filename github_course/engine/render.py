"""Render one episode of the GitHub course to MP4.

usage: python3 engine/render.py episodes/ep01.py [--preview]

An episode module defines NUM, TITLE and SCENES. Each scene is
    dict(html="...", steps=[dict(say=[...], js="..."), ...])
At step k (1-based) every element with data-s="k" is revealed and the step's
optional `js` runs. `say` holds narration sentences; an item may be a
(subtitle, spoken) tuple when the TTS needs different wording.
"""
import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
import soundfile as sf
from playwright.sync_api import sync_playwright

ENGINE = Path(__file__).resolve().parent
ROOT = ENGINE.parent
CACHE = ROOT / "cache"
OUT = ROOT / "out"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
CHROMIUM = "/opt/pw-browsers/chromium"
MODEL_DIR = Path("/opt/tts")

FPS = 30
SR = 24000
VOICE = "zf_001"
SPEED = 1.05
GAP = 0.3        # pause between sentences
STEP_LEAD = 0.2  # silence before a step's first sentence
STEP_TAIL = 0.3
SCENE_TAIL = 0.5


# English words the G2P gets wrong, spelled in IPA.
LEXICON = {
    "GitHub": "ɡˈɪthʌb",
    "README": "ɹˈid mˌi",
}


class TTS:
    def __init__(self):
        self._k = None

    def _load(self):
        from kokoro_onnx import Kokoro
        from misaki import en, zh
        e = en.G2P(trf=False, british=False, fallback=None)
        self.g2p = zh.ZHG2P(version="1.1", en_callable=lambda t: LEXICON.get(t) or e(t)[0])
        self._k = Kokoro(str(MODEL_DIR / "kokoro-v1.1-zh.onnx"), str(MODEL_DIR / "voices-v1.1-zh.bin"))

    def __call__(self, text):
        text = text.replace("……", "，").replace("《", "").replace("》", "")
        lex = sorted(v for k, v in LEXICON.items() if k in text)
        key = hashlib.sha1(f"{VOICE}|{SPEED}|{lex}|{text}".encode()).hexdigest()[:16]
        path = CACHE / "tts" / f"{key}.wav"
        if not path.exists():
            if self._k is None:
                self._load()
            ph, _ = self.g2p(text)
            audio, sr = self._k.create(ph, voice=VOICE, speed=SPEED, is_phonemes=True)
            assert sr == SR
            path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(path, audio, SR)
        audio, _ = sf.read(path, dtype="float32")
        return trim(audio)


def trim(a, thr=0.004):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    return a[max(0, idx[0] - 600): idx[-1] + 1200]


def sub_text(s):
    return re.sub(r"[。，；、]$", "", s.strip())


def load_episode(path):
    spec = importlib.util.spec_from_file_location("ep", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def page_html(ep):
    css = (ENGINE / "base.css").read_text() + (ENGINE / "gh.css").read_text()
    css += getattr(ep, "CSS", "")
    js = (ENGINE / "runtime.js").read_text()
    cursor = ('<svg id="cursor" viewBox="0 0 24 24"><path d="M3 2l7.5 19 2.6-7.9L21 10.5z" '
              'fill="#fff" stroke="#1f2328" stroke-width="1.6" stroke-linejoin="round"/></svg>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>
<body><div id="brand"><div class="logo">G</div>GitHub 零基础入门
<span class="ep">· 第 {ep.NUM} 集 {ep.TITLE}</span></div>
<div id="stage"></div>{cursor}<div id="sub"></div><script>{js}</script></body></html>"""


def build_timeline(ep, tts):
    """Synthesize narration; return per-step plans with audio and sentence offsets."""
    plans = []
    for si, scene in enumerate(ep.SCENES):
        for k, step in enumerate(scene["steps"], 1):
            sents, t = [], STEP_LEAD
            for item in step.get("say", []):
                shown, spoken = item if isinstance(item, tuple) else (item, item)
                audio = tts(spoken)
                sents.append(dict(text=sub_text(shown), audio=audio, start=t))
                t += len(audio) / SR + GAP
            t += STEP_TAIL - (GAP if sents else 0)
            if k == len(scene["steps"]):
                t += SCENE_TAIL
            plans.append(dict(scene=si, k=k, step=step, sents=sents, last=k == len(scene["steps"]),
                              dur=max(t, step.get("min", 0)), html=scene["html"] if k == 1 else None))
    return plans


def render(ep_path, preview=False):
    ep = load_episode(ep_path)
    tts = TTS()
    plans = build_timeline(ep, tts)
    name = f"ep{ep.NUM:02d}"
    OUT.mkdir(exist_ok=True)
    tmp_video = CACHE / f"{name}_video.mp4"
    tmp_video.parent.mkdir(exist_ok=True)

    enc = None if preview else subprocess.Popen(
        [FFMPEG, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png",
         "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-r", str(FPS), str(tmp_video)], stdin=subprocess.PIPE)

    total_frames = 0
    srt, audio_track = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.set_content(page_html(ep))
        page.evaluate("document.fonts.ready")
        for n, plan in enumerate(plans):
            if plan["html"] is not None:
                page.evaluate("h => setScene(h)", plan["html"])
            page.evaluate(f"reveal({plan['k']})")
            if plan["step"].get("js"):
                page.evaluate(plan["step"]["js"])
            page.evaluate("document.fonts.ready")
            anim_end = page.evaluate("prepare()") / 1000.0
            if preview:
                page.evaluate(f"seek({anim_end * 1000 + 1})")
                s = plan["sents"][0]["text"] if plan["sents"] else ""
                page.evaluate("t => setSub(t)", s)
                if plan["last"]:
                    page.evaluate("dropLeaving()")
                    page.screenshot(path=str(OUT / f"{name}_s{plan['scene'] + 1:02d}.png"))
                continue

            dur = max(plan["dur"], anim_end + 0.3)
            nframes = int(round(dur * FPS))
            sub_at = {int(round(s["start"] * FPS)): s["text"] for s in plan["sents"]}
            png, cur_sub = None, None
            for f in range(nframes):
                t = f / FPS
                dirty = png is None
                if t <= anim_end + 1 / FPS:
                    page.evaluate(f"seek({t * 1000})")
                    dirty = True
                if f in sub_at and sub_at[f] != cur_sub:
                    cur_sub = sub_at[f]
                    page.evaluate("t => setSub(t)", cur_sub)
                    dirty = True
                if dirty:
                    png = page.screenshot(type="png")
                enc.stdin.write(png)
            page.evaluate("dropLeaving()")

            base = total_frames / FPS
            for i, s in enumerate(plan["sents"]):
                end = plan["sents"][i + 1]["start"] if i + 1 < len(plan["sents"]) else s["start"] + len(s["audio"]) / SR + 0.2
                srt.append((base + s["start"], base + min(end, dur), s["text"]))
                audio_track.append((base + s["start"], s["audio"]))
            total_frames += nframes
            print(f"  step {n + 1}/{len(plans)}  {base:6.1f}s  {plan['sents'][0]['text'][:24] if plan['sents'] else ''}", flush=True)
        browser.close()
    if preview:
        print("preview stills in", OUT)
        return

    enc.stdin.close()
    enc.wait()
    length = total_frames / FPS
    mix = np.zeros(int(length * SR) + SR, dtype=np.float32)
    for start, a in audio_track:
        i = int(start * SR)
        mix[i:i + len(a)] += a[: len(mix) - i]
    peak = np.abs(mix).max() or 1.0
    mix = mix / peak * 0.89
    wav = CACHE / f"{name}.wav"
    sf.write(wav, mix[: int(length * SR)], SR)

    final = OUT / f"{name}.mp4"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(tmp_video), "-i", str(wav),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
                    str(final)], check=True)
    (OUT / f"{name}.srt").write_text("".join(
        f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(srt, 1)), encoding="utf-8")
    print(f"done: {final}  {length / 60:.1f} min")


def ts(x):
    ms = int(round(x * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


if __name__ == "__main__":
    render(sys.argv[1], preview="--preview" in sys.argv)
