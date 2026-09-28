#!/usr/bin/env python3
"""《用 Opus 5.5 看世界》背景音乐：纯 numpy 合成，无采样、无外部素材。

96 BPM，4/4 拍，36 小节 = 90 秒。调性 D 大调 / B 小调，和弦循环 Bm - G - D - A。
段落（与画面分镜对齐，1 小节 = 2.5 秒）：
  0-3   前奏：柔和铺底 + 打字声 + 铃音             （0-10s   苏醒）
  4-9   + 琶音                                     （10-25s  字符构成的风景）
  10-15 + 贝斯、轻鼓、踩镲                          （25-40s  语义空间）
  16-21 + 轻柔主旋律、拍手                          （40-55s  注意力）
  22-23 上升音效，鼓退出                            （55-60s  坍缩成一点）
  24-31 高潮：完整鼓组 + 主旋律                     （60-80s  语言连接的地球）
  32-35 尾声：铺底 + 琶音渐隐，结束在 D 和弦        （80-90s  结语）

用法：python3 make_music.py [out.wav]
"""
import os
import sys
import wave

import numpy as np

SR = 44100
BPM = 96.0
BEAT = 60.0 / BPM          # 0.625 s
BAR = BEAT * 4             # 2.5 s
NBARS = 36
DUR = NBARS * BAR          # 90 s
N = int(DUR * SR) + SR * 4  # 留出混响尾巴，最后再裁剪

rng = np.random.default_rng(55)

# 打字时间表（与 scene.js 中的 TYPE_TIMES 保持一致）
TYPE_START, TYPE_STEP, TYPE_TEXT = 1.2, 0.14, "Hello, world."
END_TYPE_START, END_TYPE_STEP, END_TEXT = 87.8, 0.1, "世界，是一场对话。"


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


# ---- 和弦 ---------------------------------------------------------------
# 名称: (贝斯根音, 铺底音列, 琶音音列)
CHORDS = {
    "Bm": (35, [47, 54, 57, 61, 62], [59, 62, 66, 69, 73, 71, 66, 62]),
    "G":  (31, [43, 50, 54, 57, 59], [55, 59, 62, 66, 69, 66, 62, 59]),
    "D":  (38, [45, 50, 54, 57, 64], [57, 62, 66, 69, 74, 69, 66, 64]),
    "A":  (33, [45, 52, 57, 59, 61], [57, 61, 64, 69, 71, 69, 64, 61]),
}
PROG = ["Bm", "G", "D", "A"]


def chord_at(bar):
    if bar >= 35:
        return "D"
    return PROG[bar % 4]


# ---- 旋律（每 4 小节一句，共两句 = 8 小节）----------------------------------
# (小节内拍位, 时值(拍), MIDI)
MELODY = [
    [(0, 1.5, 78), (1.5, .5, 76), (2, 1, 74), (3, 1, 76)],          # Bm
    [(0, 3, 71), (3, 1, 74)],                                        # G
    [(0, 1.5, 81), (1.5, .5, 78), (2, 1, 76), (3, 1, 74)],          # D
    [(0, 2, 73), (2, 1, 76), (3, 1, 69)],                            # A
    [(0, 1.5, 78), (1.5, .5, 81), (2, 1, 83), (3, 1, 81)],          # Bm
    [(0, 2, 78), (2, 1, 76), (3, 1, 74)],                            # G
    [(0, 1.5, 76), (1.5, .5, 78), (2, 2, 81)],                       # D
    [(0, 4, 76)],                                                    # A
]


# ---- 基础工具 -------------------------------------------------------------
def add(buf, start_s, sig, gain=1.0, pan=0.0):
    """把单声道信号按声像写入立体声缓冲区。"""
    i = int(start_s * SR)
    if i >= buf.shape[1]:
        return
    sig = sig[: buf.shape[1] - i]
    lg = np.cos((pan + 1) * np.pi / 4) * gain
    rg = np.sin((pan + 1) * np.pi / 4) * gain
    buf[0, i:i + len(sig)] += sig * lg
    buf[1, i:i + len(sig)] += sig * rg


def onepole_lp(x, cutoff):
    """一阶低通（向量化：用 FFT 频响近似，适合整轨处理）。"""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    H = 1 / np.sqrt(1 + (f / cutoff) ** 2)
    return np.fft.irfft(X * H, len(x))


def fft_convolve(x, h):
    n = len(x) + len(h) - 1
    nfft = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(h, nfft), nfft)[: len(x)]


# ---- 音色 -----------------------------------------------------------------
def pad_note(m, dur, bright=0.55):
    """双声部失谐锯齿（加法合成）+ 慢起慢收。"""
    n = int((dur + 1.6) * SR)
    t = np.arange(n) / SR
    f0 = mtof(m)
    sig = np.zeros(n)
    for det in (-0.09, 0.09):
        f = f0 * 2 ** (det / 12)
        ph = rng.uniform(0, 2 * np.pi)
        for h in range(1, 9):
            if f * h > 9000:
                break
            sig += np.sin(2 * np.pi * f * h * t + ph * h) * (bright ** (h - 1)) / h
    e = np.clip(t / 0.7, 0, 1) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.5))
    return sig * e * 0.12


def pluck(m, decay=0.35, bright=0.6):
    """琶音拨弦：衰减的谐波 + 轻微 FM 闪光。"""
    n = int((decay * 4 + 0.05) * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    sig = np.zeros(n)
    for h in range(1, 7):
        sig += np.sin(2 * np.pi * f * h * t) * (bright ** (h - 1)) * np.exp(-t * h * 1.2 / decay)
    sig += 0.25 * np.sin(2 * np.pi * f * 2 * t + 2.0 * np.sin(2 * np.pi * f * 3 * t) * np.exp(-t * 18))
    return sig * np.minimum(t / 0.003, 1) * 0.22


def bell(m, dur=2.8):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    mod = 3.5 * np.exp(-t * 2.5) * np.sin(2 * np.pi * f * 3.5 * t)
    sig = np.sin(2 * np.pi * f * t + mod) * np.exp(-t * 1.6)
    sig += 0.3 * np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t * 3)
    return sig * np.minimum(t / 0.002, 1) * 0.18


def lead(m, dur, soft=False):
    """圆润主旋律：三角波 + 延迟颤音。"""
    n = int((dur + 0.5) * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.25) / 0.3, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    sig = np.zeros(n)
    for h in (1, 3, 5, 7):
        sig += ((-1) ** ((h - 1) // 2)) * np.sin(h * ph) / (h * h)
    sig += 0.35 * np.sin(2 * ph) * (0.3 if soft else 0.5)
    e = np.clip(t / 0.04, 0, 1) * np.where(t < dur, 1 - 0.25 * np.clip(t / dur, 0, 1), 0.75 * np.exp(-(t - dur) / 0.12))
    return sig * e * (0.10 if soft else 0.16)


def bass(m, dur):
    n = int((dur + 0.2) * SR)
    t = np.arange(n) / SR
    f = mtof(m)
    sig = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t * 3) + 0.12 * np.sin(6 * np.pi * f * t)
    e = np.clip(t / 0.01, 0, 1) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.05))
    return sig * e * 0.30


def kick(strength=1.0):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 45 + 85 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) * np.exp(-t * 7) + 0.3 * rng.standard_normal(n) * np.exp(-t * 180)
    return np.tanh(sig * 1.4) * 0.55 * strength


def clap(strength=1.0):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    nz = np.diff(nz, prepend=0)  # 粗略高通
    e = np.zeros(n)
    for off in (0, 0.011, 0.022):
        e += np.where(t >= off, np.exp(-(t - off) * 60), 0) * 0.5
    e += np.exp(-t * 14) * 0.5
    return nz * e * 0.16 * strength


def hat(open_=False, strength=1.0):
    n = int((0.35 if open_ else 0.08) * SR)
    t = np.arange(n) / SR
    nz = np.diff(np.diff(rng.standard_normal(n + 2)))
    return nz * np.exp(-t * (9 if open_ else 55)) * 0.05 * strength


def key_click():
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    nz = np.convolve(rng.standard_normal(n), np.ones(4) / 4, mode="same")  # 柔化，去掉刺耳的高频
    return (nz * np.exp(-t * 220) * 0.12 + np.sin(2 * np.pi * 1400 * t) * np.exp(-t * 140) * 0.06)


# ---- 编曲 -----------------------------------------------------------------
def build():
    pad = np.zeros((2, N))
    arp = np.zeros((2, N))
    drums = np.zeros((2, N))
    mel = np.zeros((2, N))
    fx = np.zeros((2, N))
    bs = np.zeros((2, N))

    def bt(bar, beat=0.0):
        return bar * BAR + beat * BEAT

    # 铺底
    for b in range(NBARS):
        _, notes, _ = CHORDS[chord_at(b)]
        bright = 0.35 if b < 10 else (0.5 if b < 24 else 0.62)
        if b >= 32:
            bright = 0.4
        g = 1.0
        if b < 2:
            g = 0.55 + 0.45 * b / 2
        dur = BAR * (2.0 if b == 35 else 1.0) + 0.1
        for k, m in enumerate(notes):
            add(pad, bt(b), pad_note(m, dur, bright), g, pan=(k - 2) * 0.3)

    # 打字音
    for i, _ in enumerate(TYPE_TEXT):
        add(fx, TYPE_START + i * TYPE_STEP + rng.uniform(-0.01, 0.01), key_click(), 0.9, pan=rng.uniform(-0.3, 0.3))
    for i, _ in enumerate(END_TEXT):
        add(fx, END_TYPE_START + i * END_TYPE_STEP, key_click(), 0.7, pan=rng.uniform(-0.3, 0.3))

    # 铃音：开场、各段落转场
    for tsec, m in [(0.2, 86), (4.0, 81), (4.6, 85), (5.2, 88), (10.0, 90), (25.0, 86), (40.0, 90),
                    (60.0, 93), (77.5, 86), (80.0, 90), (85.0, 86), (86.25, 90), (87.5, 93)]:
        add(fx, tsec, bell(m), 0.8, pan=rng.uniform(-0.5, 0.5))

    # 琶音（16 分音符）
    delay_s = BEAT * 0.75
    for b in range(4, 34):
        if 22 <= b <= 23:
            continue
        pat = CHORDS[chord_at(b)][2]
        g = min(1.0, 0.35 + (b - 4) * 0.12)
        if b >= 32:
            g = 0.8 - (b - 32) * 0.3
        step = 0.5 if b < 10 else 0.25
        k = 0
        s = 0.0
        while s < 4 - 1e-6:
            m = pat[k % len(pat)]
            acc = 1.0 if abs(s - round(s)) < 1e-6 else 0.7
            add(arp, bt(b, s), pluck(m, 0.28 if step == 0.25 else 0.45), g * acc, pan=0.35 * np.sin(k * 1.3))
            k += 1
            s += step
    # 乒乓延迟
    d = int(delay_s * SR)
    wet = np.zeros_like(arp)
    wet[1, d:] += arp[0, :-d] * 0.45
    wet[0, 2 * d:] += arp[1, :-2 * d] * 0.3
    arp += wet

    # 贝斯
    for b in range(10, 32):
        if 22 <= b <= 23:
            continue
        root = CHORDS[chord_at(b)][0]
        if b < 16:
            add(bs, bt(b), bass(root, BAR * 0.95), 0.9)
        else:
            for s, dur, oc in [(0, 1.5, 0), (1.5, 0.5, 12), (2, 1.5, 0), (3.5, 0.5, 7)]:
                add(bs, bt(b, s), bass(root + oc, dur * BEAT * 0.95), 0.95)

    # 鼓
    kicks = []
    for b in range(12, 32):
        if 22 <= b <= 23:
            continue
        climax = b >= 24
        for s in (range(4) if climax or b >= 16 else (0, 2)):
            kicks.append(bt(b, s))
            add(drums, bt(b, s), kick(1.0 if climax else 0.75))
        if b >= 14:
            for s in np.arange(0, 4, 0.25 if climax else 0.5):
                off = abs(s - round(s) - 0.5) < 1e-6 or (climax and abs(s % 1 - 0.5) < 1e-6)
                if not climax and not off:
                    continue
                strength = 1.0 if off else 0.45
                add(drums, bt(b, s), hat(open_=(climax and off and int(s) == 3), strength=strength),
                    1.0, pan=0.25)
        if b >= 16:
            for s in ((1, 3) if climax else (3,)):
                add(drums, bt(b, s), clap(1.0 if climax else 0.7), 1.0, pan=-0.1)
    # 小节 21 末尾的过门
    for s in (3.0, 3.25, 3.5, 3.75):
        add(drums, bt(21, s), clap(0.5 + 0.15 * (s - 3) * 4), 1.0)

    # 旋律
    for b in range(16, 22):
        for s, dur, m in MELODY[(b - 16) % 8]:
            add(mel, bt(b, s), lead(m - 12, dur * BEAT, soft=True), 1.0, pan=0.1)
    for b in range(24, 32):
        for s, dur, m in MELODY[(b - 24) % 8]:
            add(mel, bt(b, s), lead(m, dur * BEAT), 1.0, pan=0.12)
            add(mel, bt(b, s), lead(m - 12, dur * BEAT, soft=True), 0.6, pan=-0.2)

    # 上升音效 55-60s + 高潮冲击
    rs, re_ = bt(22), bt(24)
    n = int((re_ - rs) * SR)
    t = np.arange(n) / SR
    x = t / (re_ - rs)
    nz = rng.standard_normal(n)
    hp = np.diff(nz, prepend=0)
    riser = (nz * (1 - x) * 0.3 + hp * x) * (x ** 2.2) * 0.12
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1400 * x ** 2) / SR) * x ** 3 * 0.05
    add(fx, rs, riser + sweep, 1.0)
    # 上升期间的 "吸入" 和弦（反向包络）
    for m in (62, 66, 69, 73):
        s = pad_note(m, BAR * 2, 0.7)[: n]
        add(fx, rs, s * (x ** 1.5)[: len(s)] * 0.9, 1.0, pan=0.2 * (m - 67) / 6)
    # 冲击
    n2 = int(3.5 * SR)
    t2 = np.arange(n2) / SR
    boom = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t2 * 6)) / SR) * np.exp(-t2 * 1.4) * 0.5
    crash = np.diff(rng.standard_normal(n2 + 1)) * np.exp(-t2 * 1.3) * 0.07
    add(fx, re_, boom + crash, 1.0)

    # 侧链压缩：鼓点处压低铺底和琶音
    duck = np.ones(N)
    L = int(0.4 * SR)
    shape = 1 - 0.55 * np.exp(-np.arange(L) / SR * 9)
    for k in kicks:
        i = int(k * SR)
        j = min(N, i + L)
        duck[i:j] = np.minimum(duck[i:j], shape[: j - i])
    pad *= duck
    arp *= 0.6 + 0.4 * duck

    # 混响（合成的指数衰减噪声脉冲响应）
    irn = int(3.2 * SR)
    ti = np.arange(irn) / SR
    ir = [rng.standard_normal(irn) * np.exp(-ti * 2.2) for _ in range(2)]
    for c in range(2):
        ir[c][: int(0.012 * SR)] = 0
        ir[c] = onepole_lp(ir[c], 5000)
        ir[c] /= np.sqrt(np.sum(ir[c] ** 2))
    send = pad * 0.5 + arp * 0.6 + mel * 0.55 + fx * 0.45 + drums * 0.12
    rev = np.stack([fft_convolve(send[c], ir[c]) for c in range(2)]) * 0.55

    mix = pad * 0.9 + arp * 0.8 + mel + fx + drums + bs * 0.9 + rev
    # 主总线：轻微低切（去直流）+ 软削波 + 淡入淡出
    mix -= mix.mean(axis=1, keepdims=True)
    mix = mix[:, : int(DUR * SR)]
    tt = np.arange(mix.shape[1]) / SR
    mix *= np.clip(tt / 0.8, 0, 1) * np.clip((DUR - tt) / 3.0, 0, 1)
    peak = np.max(np.abs(mix))
    mix = np.tanh(mix / peak * 1.25) / np.tanh(1.25) * 0.89
    return mix


def write_wav(path, mix):
    data = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "music.wav")
    write_wav(out, build())
    print("wrote", out)
