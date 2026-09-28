#!/usr/bin/env python3
"""合成背景音乐：温暖的钢琴 + 弦乐铺底，D 大调，四个乐句随履历阶段逐层加厚；
另按画面里铅笔是否在绘制，叠加很轻的“沙沙”笔触声。
用法：python3 make_audio.py pen.json out.wav"""
import json
import sys
import wave

import numpy as np

SR = 44100
info = json.load(open(sys.argv[1]))
TOTAL = info["total"]
N = int((TOTAL + 0.5) * SR)
rng = np.random.default_rng(7)
BAR = TOTAL / 32  # 32 小节铺满全片
BEAT = BAR / 4

mid = lambda m: 440.0 * 2 ** ((m - 69) / 12)
L = np.zeros(N)
Rt = np.zeros(N)


def put(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    Rt[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def piano(m, dur, vel=0.5):
    f = mid(m)
    n = int((dur + 1.8) * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k in range(1, 8):
        if f * k > 9000:
            break
        det = 1 + (rng.random() - 0.5) * 0.0008
        s += (1 / k ** 1.6) * np.sin(2 * np.pi * f * k * det * t) * np.exp(-t * (0.9 + 0.55 * k) * (f / 400) ** 0.3)
    att = np.minimum(1, t / 0.004)
    rel = np.clip(1 - (t - dur) / 0.35, 0, 1) ** 2
    rel[t < dur] = 1
    return s * att * rel * vel


def pad(ms, dur, vel=0.12):
    n = int((dur + 1.0) * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for m in ms:
        f = mid(m)
        for d in (-0.12, 0.0, 0.12):
            ff = f * 2 ** (d / 12)
            s += np.sin(2 * np.pi * ff * t + rng.random() * 6) + 0.25 * np.sin(4 * np.pi * ff * t)
    env = np.minimum(1, t / 0.9) * np.clip((dur + 1.0 - t) / 1.0, 0, 1)
    return s * env * vel / len(ms) / 3


# 和弦进行（D 大调）：D  A/C#  Bm  F#m  G  D  G  A
CH = [(50, [62, 66, 69]), (49, [61, 64, 69]), (47, [59, 62, 66]), (42, [61, 66, 69]),
      (43, [59, 62, 67]), (50, [62, 66, 69]), (43, [59, 62, 67]), (45, [61, 64, 69])]
MEL = [[(78, 0, 1.5), (76, 1.5, .5), (74, 2, 2)],
       [(76, 0, 1), (73, 1, 1), (69, 2, 2)],
       [(71, 0, 1), (74, 1, 1), (78, 2, 1.5), (76, 3.5, .5)],
       [(73, 0, 3), (69, 3, 1)],
       [(71, 0, 1.5), (74, 1.5, .5), (79, 2, 2)],
       [(78, 0, 1), (76, 1, 1), (74, 2, 2)],
       [(71, 0, 1), (74, 1, 1), (76, 2, 1), (79, 3, 1)],
       [(76, 0, 3), (73, 3, 1)]]
END = [(78, 0, 1.5), (76, 1.5, .5), (74, 2, 4)]

for bar in range(32):
    phrase, k = divmod(bar, 8)
    t0 = bar * BAR
    last = bar == 31
    bass, tones = (50, [62, 66, 69]) if last else CH[k]
    # 分解和弦（左手）
    arp = [bass, tones[0] - 12 + 12, tones[1], tones[2], tones[1], tones[0]]
    steps = 8 if phrase >= 1 else 4
    for j in range(1 if last else steps):
        m = arp[j % len(arp)] if j else bass
        put(piano(m, BEAT * (4 if last else 4 / steps * 1.6), 0.22 if j else 0.3), t0 + j * BEAT * 4 / steps, pan=-0.2 + 0.1 * (j % 3))
    # 弦乐铺底
    if bar >= 2:
        put(pad([bass + 12] + tones, BAR * (2.2 if last else 1.0), 0.10 + 0.03 * min(phrase, 2)), t0, pan=0.0)
    # 低音
    if phrase >= 1:
        put(piano(bass - 12, BAR * (2 if last else 0.9), 0.25), t0, pan=-0.1)
    # 旋律（右手）
    mel = END if last else MEL[k]
    vel = [0.26, 0.3, 0.32, 0.34][phrase]
    for m, b, d in mel:
        put(piano(m, d * BEAT, vel), t0 + b * BEAT + 0.012, pan=0.18)
        if phrase == 3 and not last:
            put(piano(m - 12, d * BEAT, vel * 0.45), t0 + b * BEAT + 0.012, pan=0.1)
    # 第三乐句：高音八音盒式点缀
    if phrase == 2:
        for j, m in enumerate([tones[2] + 12, tones[1] + 12, tones[0] + 24, tones[1] + 12]):
            put(piano(m, BEAT * 0.5, 0.08), t0 + (j * 2 + 1) * BEAT / 2, pan=0.45)
    if last:
        put(piano(86, BAR * 1.5, 0.12), t0 + 2 * BEAT, pan=0.4)

# 混响：衰减噪声脉冲响应卷积
def reverb(x, seed):
    r = np.random.default_rng(seed)
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t / 0.55)
    ir[: int(0.02 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    size = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    return y

L, Rt = 0.78 * L + 0.32 * reverb(L, 1), 0.78 * Rt + 0.32 * reverb(Rt, 2)

# 铅笔沙沙声
fps = info["fps"]
pen = np.array(info["pen"], dtype=float)
env = np.interp(np.arange(N) / SR, np.arange(len(pen)) / fps, pen)
k = int(0.04 * SR)
env = np.convolve(env, np.ones(k) / k, mode="same")
noise = rng.standard_normal(N)
spec = np.fft.rfft(noise)
fr = np.fft.rfftfreq(N, 1 / SR)
spec *= np.exp(-((np.log(fr + 1) - np.log(3800)) ** 2) / 0.35)
scratch = np.fft.irfft(spec, N)
scratch /= np.max(np.abs(scratch)) + 1e-9
grain = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * np.cumsum(7 + 5 * rng.random(N) ) / SR))
scratch *= env * grain * 0.045 * info.get("scratch", 1.0)
L += scratch
Rt += scratch * 0.9

# 3D 版：物件从纸上跃起时的轻柔“呼”声（低通噪声，先强后弱）
for tp in info.get("pops", []):
    n = int(0.55 * SR)
    tt = np.arange(n) / SR
    w = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * np.exp(-np.fft.rfftfreq(n, 1 / SR) / 900), n)
    w = w / (np.max(np.abs(w)) + 1e-9) * np.sin(np.pi * np.minimum(1, tt / 0.55)) ** 2 * 0.05
    put(w, tp, pan=0.0)
    put(w * 0.8, tp + 0.01, pan=0.3)

# 首尾淡入淡出 + 归一化
t = np.arange(N) / SR
fade = np.minimum(1, t / 1.0) * np.clip((TOTAL + 0.5 - t) / 2.5, 0, 1)
L *= fade
Rt *= fade
peak = max(np.max(np.abs(L)), np.max(np.abs(Rt)))
L, Rt = L / peak * 0.85, Rt / peak * 0.85
data = (np.stack([L, Rt], 1) * 32767).astype(np.int16)
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(data.tobytes())
print("audio →", sys.argv[2], f"{N / SR:.1f}s")
