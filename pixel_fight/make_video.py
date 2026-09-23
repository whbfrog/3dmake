#!/usr/bin/env python3
"""像素短片《谁才是最强AI？》生成脚本。

小橙（Claude 的像素宠物）和小绿（ChatGPT 的像素宠物）互相不服、大打出手、
联手打败 BUG 怪兽，最后在夕阳下和好。

画面：320x180 像素画，放大 4 倍输出 1280x720 @24fps。
声音：程序合成的 8-bit 芯片音乐 + 音效（角色本身不发声，对白以中文字幕显示）。

用法：python3 make_video.py [输出路径]
依赖：pillow numpy imageio-ffmpeg，以及系统中的 Unifont 字体。
"""
import math
import os
import random
import subprocess
import sys
import wave
from functools import lru_cache

import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

W, H, S, FPS = 320, 180, 4, 24
BW, BH = W * S, H * S
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "claude_vs_chatgpt.mp4")

FONT = "/usr/share/fonts/opentype/unifont/unifont.otf"
F32 = ImageFont.truetype(FONT, 32)
F48 = ImageFont.truetype(FONT, 48)
F64 = ImageFont.truetype(FONT, 64)
F96 = ImageFont.truetype(FONT, 96)

# ---------------------------------------------------------------- palette
INK = (40, 28, 44)
WHITE = (255, 255, 255)
CREAM = (252, 246, 232)
ORANGE, ORANGE_L, ORANGE_D = (217, 119, 87), (240, 158, 124), (176, 84, 58)
GREEN, GREEN_L, GREEN_D = (16, 163, 127), (110, 214, 176), (8, 112, 86)
PINK = (255, 140, 170)
RED = (230, 60, 70)
YELLOW = (255, 220, 60)
BLUE = (90, 160, 255)
KIDBLUE = (80, 130, 220)

# ---------------------------------------------------------------- timeline
SCENES = [
    ("title", 0, 6),
    ("meet", 6, 26),
    ("contest", 26, 48),
    ("fight", 48, 65),
    ("bug", 65, 88),
    ("sunset", 88, 111),
    ("end", 111, 118),
]
TOTAL = 118
SC = {n: a for n, a, b in SCENES}

SPEAKERS = {
    "C": ("Claude · 小橙", ORANGE, 520),
    "G": ("ChatGPT · 小绿", GREEN, 700),
    "K": ("小朋友", KIDBLUE, 900),
}

# (scene, start, end, speaker, text) — start/end are scene-relative seconds
LINES_REL = [
    ("meet", 3.0, 6.5, "C", "今天天气真好～又是写代码的一天！"),
    ("meet", 6.5, 9.5, "G", "哟，这不是那只橙色小螃蟹嘛？"),
    ("meet", 9.5, 13.0, "C", "我才不是螃蟹！还有，我可是最强的 AI！"),
    ("meet", 13.0, 16.5, "G", "哈？最强的明明是我！全世界都在找我聊天～"),
    ("meet", 16.5, 20.0, "C", "聊天多有什么用？我写的代码一次就能跑通！"),
    ("contest", 0.5, 3.0, "G", "不服？那就来比一比！"),
    ("contest", 3.0, 7.0, "G", "看好了——我画一幅世界名画！"),
    ("contest", 7.0, 10.5, "C", "……这只猫为什么有六条腿？"),
    ("contest", 10.5, 13.5, "G", "那叫艺术！你不懂！"),
    ("contest", 13.5, 16.5, "C", "看我的：一口气写完一个小游戏！"),
    ("contest", 16.5, 19.5, "G", "嘿嘿，第 23 行少了个括号哦～"),
    ("contest", 19.5, 22.0, "C", "你……你……我跟你拼了！！"),
    ("fight", 10.5, 13.5, "C", "你……还挺能打的嘛……"),
    ("fight", 13.5, 17.0, "G", "你、你也不赖……哎哟，我的头……"),
    ("bug", 2.5, 6.0, "K", "呜呜……救命！有个大 BUG 在追我！"),
    ("bug", 6.5, 9.5, "C", "小绿！先别打了，救人要紧！"),
    ("bug", 9.5, 12.5, "G", "好！我来找它的弱点，你来修复它！"),
    ("bug", 12.5, 15.5, "G", "找到了——弱点就在第 23 行！"),
    ("bug", 15.5, 18.5, "C", "看我的：修复补丁，发射！"),
    ("bug", 19.5, 23.0, "K", "哇！谢谢你们！你们是最棒的搭档！"),
    ("sunset", 2.0, 5.5, "G", "刚才……谢谢你。其实你写的代码，我一直很佩服。"),
    ("sunset", 5.5, 9.0, "C", "你能陪那么多人聊天、帮人解忧，也很了不起呀。"),
    ("sunset", 9.0, 12.5, "C", "也许最强的不是谁，而是我们一起帮到别人的时候。"),
    ("sunset", 12.5, 15.0, "G", "……那，我们做好朋友吧？"),
    ("sunset", 15.0, 17.0, "C", "嗯！"),
    ("sunset", 17.0, 19.5, "G", "不过下次比赛，我还是会赢的！"),
    ("sunset", 19.5, 23.0, "C", "做梦吧你～哈哈哈！"),
]
LINES = [(SC[s] + a, SC[s] + b, who, txt) for s, a, b, who, txt in LINES_REL]
CPS = 13  # typewriter speed (chars / second)


def speaking(who, T):
    for a, b, w, txt in LINES:
        if w == who and a <= T < min(b, a + len(txt) / CPS + 0.2):
            return True
    return False


# ---------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def seg(t, a, b):
    return clamp((t - a) / (b - a))


def ease(x):
    return x * x * (3 - 2 * x)


def lerp(a, b, x):
    return a + (b - a) * x


def mix(c1, c2, k):
    return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))


def R(d, x, y, w, h, c):
    if w > 0 and h > 0:
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def P(d, x, y, c):
    d.point((x, y), fill=c)


def outline(spr, col=INK):
    a = np.array(spr)
    al = a[..., 3] > 0
    m = np.zeros_like(al)
    m[1:, :] |= al[:-1, :]
    m[:-1, :] |= al[1:, :]
    m[:, 1:] |= al[:, :-1]
    m[:, :-1] |= al[:, 1:]
    a[m & ~al] = col + (255,)
    return Image.fromarray(a)


def blit(img, spr, cx, by, scale=2, flip=False, anchor=(16, 24)):
    ax, ay = anchor
    if flip:
        spr = spr.transpose(Image.FLIP_LEFT_RIGHT)
        ax = spr.width - 1 - ax
    w, h = max(1, int(spr.width * scale)), max(1, int(spr.height * scale))
    s = spr.resize((w, h), Image.NEAREST)
    img.paste(s, (int(round(cx - (ax + 0.5) * scale)), int(round(by - (ay + 1) * scale))), s)


def draw_pattern(d, pat, x, y, col, s=1):
    for j, row in enumerate(pat):
        for i, ch in enumerate(row):
            if ch == "X":
                R(d, x + i * s, y + j * s, s, s, col)


HEART = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
HEART_O = ["..XX.XX..", ".XXXXXXX.", "XXXXXXXXX", "XXXXXXXXX", ".XXXXXXX.", "..XXXXX..", "...XXX...", "....X...."]


def heart(d, x, y, s=1, col=RED):
    draw_pattern(d, HEART_O, x - s, y - s, INK, s)
    draw_pattern(d, HEART, x, y, col, s)
    R(d, x + s, y + s, s, s, (255, 200, 210))


def star(d, x, y, col=YELLOW):
    R(d, x - 1, y - 2, 3, 5, INK)
    R(d, x - 2, y - 1, 5, 3, INK)
    R(d, x, y - 1, 1, 3, col)
    R(d, x - 1, y, 3, 1, col)


# ---------------------------------------------------------------- faces
def draw_eyes(d, xs, ey, expr, w=2, h=3, hl=False):
    for i, x in enumerate(xs):
        inner = 1 if i == 0 else -1  # direction toward face centre
        if expr in ("blink", "sleep"):
            R(d, x, ey + h - 1, w, 1, INK)
        elif expr in ("happy", "laugh"):
            P(d, x - 1 + (1 if w == 2 else 0), ey + 1, INK)
            P(d, x + (1 if w == 2 else 0) - 0, ey, INK)
            P(d, x + w - 1, ey, INK)
            P(d, x + w, ey + 1, INK)
        elif expr == "dizzy":
            for dx, dy in ((0, 0), (2, 0), (1, 1), (0, 2), (2, 2)):
                P(d, x - (1 if i == 0 else 0) + dx, ey + dy, INK)
        elif expr == "smug":
            R(d, x, ey + 1, w + 1, 1, INK)
            R(d, x, ey + 2, w, 1, INK)
        elif expr == "surprised":
            R(d, x - 1, ey - 1, w + 2, h + 1, WHITE)
            R(d, x, ey, w, h - 1, INK)
        else:
            R(d, x, ey, w, h, INK)
            if hl:
                P(d, x, ey, WHITE)
        if expr in ("angry", "flush"):
            ox = x - 1 if i == 0 else x + w
            ix = x + w if i == 0 else x - 1
            P(d, ox, ey - 3, INK)
            P(d, (ox + ix) // 2 + (0 if i == 0 else 1), ey - 2, INK)
            P(d, ix, ey - 1, INK)
        if expr == "sad":
            ox = x - 1 if i == 0 else x + w
            ix = x + w if i == 0 else x - 1
            P(d, ox, ey - 1, INK)
            P(d, ix, ey - 3, INK)
            P(d, (ox + ix) // 2 + (0 if i == 0 else 1), ey - 2, INK)
        _ = inner


# ---------------------------------------------------------------- sprites
@lru_cache(maxsize=None)
def clawd(expr="normal", walk=0, arms="down", sit=False, flush=False, band=False, tear=-1):
    """Claude 的像素宠物小橙（橙色小方块，四条小短腿，两只小钳子）。朝右。"""
    im = Image.new("RGBA", (32, 26))
    d = ImageDraw.Draw(im)
    body = ORANGE
    R(d, 7, 8, 18, 12, body)
    R(d, 8, 8, 16, 1, ORANGE_L)
    R(d, 7, 9, 1, 2, ORANGE_L)
    R(d, 8, 19, 17, 1, ORANGE_D)
    # arms / claws
    if arms == "up":
        R(d, 4, 5, 3, 7, body)
        R(d, 25, 5, 3, 7, body)
        R(d, 3, 4, 2, 2, body)
        R(d, 27, 4, 2, 2, body)
    elif arms == "fwd":
        R(d, 4, 12, 3, 3, body)
        R(d, 25, 11, 5, 3, body)
    else:
        R(d, 4, 12, 3, 3, body)
        R(d, 25, 12, 3, 3, body)
    # legs
    lh = 1 if sit else 5
    for k, x in enumerate((8, 11, 19, 22)):
        up = 1 if (walk and (k % 2 == walk - 1)) else 0
        R(d, x, 20, 2, lh - up, ORANGE_D if k in (1, 3) else body)
    # face (looking right → shifted +1)
    xs = (12, 20)
    ey = 11
    if flush or expr == "flush":
        R(d, 9, 15, 3, 1, (240, 70, 70))
        R(d, 22, 15, 3, 1, (240, 70, 70))
    elif expr in ("happy", "laugh", "shy") or expr == "sleep":
        R(d, 9, 15, 2, 1, PINK)
        R(d, 23, 15, 2, 1, PINK)
    draw_eyes(d, xs, ey, "normal" if expr == "shy" else expr)
    if expr == "laugh":
        R(d, 15, 15, 3, 2, (120, 30, 40))
    if tear >= 0:
        R(d, 12, 14 + tear, 1, 2, BLUE)
        R(d, 21, 14 + (tear + 1) % 3, 1, 2, BLUE)
    if band:
        R(d, 8, 9, 4, 2, CREAM)
        R(d, 9, 8, 2, 4, CREAM)
        P(d, 9, 9, PINK)
    im = outline(im)
    return im


@lru_cache(maxsize=None)
def gpt(expr="normal", walk=0, arms="down", sit=False, talk=False, flush=False, bump=False, tear=-1):
    """ChatGPT 的像素宠物小绿（圆滚滚的薄荷绿团子，头顶一朵小花）。朝右。"""
    im = Image.new("RGBA", (32, 26))
    d = ImageDraw.Draw(im)
    # antenna flower
    R(d, 15, 6, 2, 4, GREEN_D)
    d.ellipse([12, 1, 19, 6], fill=GREEN_L)
    R(d, 15, 3, 2, 2, WHITE)
    # body
    d.ellipse([6, 9, 25, 24], fill=GREEN)
    d.ellipse([10, 16, 22, 24], fill=GREEN_L)
    R(d, 10, 10, 3, 1, (70, 200, 160))
    # feet
    if not sit:
        dy = (1 if walk == 1 else 0), (1 if walk == 2 else 0)
        R(d, 9, 23 - dy[0], 5, 2, GREEN_D)
        R(d, 18, 23 - dy[1], 5, 2, GREEN_D)
    # arms
    if arms == "up":
        R(d, 4, 10, 2, 6, GREEN)
        R(d, 26, 10, 2, 6, GREEN)
    elif arms == "fwd":
        R(d, 4, 16, 3, 2, GREEN)
        R(d, 25, 14, 5, 2, GREEN)
    else:
        R(d, 4, 16, 3, 2, GREEN)
        R(d, 25, 16, 3, 2, GREEN)
    xs = (12, 19)
    ey = 13
    if flush or expr == "flush":
        R(d, 8, 18, 3, 1, (240, 70, 70))
        R(d, 22, 18, 3, 1, (240, 70, 70))
    elif expr in ("happy", "laugh", "shy", "sleep", "normal", "blink", "talk"):
        R(d, 9, 18, 2, 1, PINK)
        R(d, 22, 18, 2, 1, PINK)
    draw_eyes(d, xs, ey, "normal" if expr == "shy" else expr, hl=True)
    # mouth
    if expr == "laugh" or talk:
        R(d, 15, 18, 2, 2, (120, 30, 40))
    elif expr in ("happy", "shy", "smug"):
        P(d, 15, 18, INK)
        P(d, 16, 18, INK)
        if expr != "smug":
            P(d, 14, 17, INK)
            P(d, 17, 17, INK)
        else:
            P(d, 17, 17, INK)
    elif expr in ("angry", "flush", "sad"):
        R(d, 15, 19, 2, 1, INK)
    elif expr == "surprised":
        R(d, 15, 18, 2, 2, INK)
    elif expr == "dizzy":
        P(d, 14, 19, INK)
        P(d, 15, 18, INK)
        P(d, 16, 19, INK)
        P(d, 17, 18, INK)
    else:
        P(d, 15, 18, INK)
    if tear >= 0:
        R(d, 12, 16 + tear, 1, 2, BLUE)
        R(d, 20, 16 + (tear + 1) % 3, 1, 2, BLUE)
    if bump:
        d.ellipse([7, 8, 11, 12], fill=(255, 120, 130))
        P(d, 8, 9, (255, 200, 200))
    return outline(im)


@lru_cache(maxsize=None)
def kid(expr="cry", walk=0, tear=0):
    im = Image.new("RGBA", (22, 32))
    d = ImageDraw.Draw(im)
    skin, hair = (255, 214, 176), (110, 70, 40)
    # legs
    l1 = 1 if walk == 1 else 0
    l2 = 1 if walk == 2 else 0
    R(d, 8, 25, 2, 4 - l1, skin)
    R(d, 12, 25, 2, 4 - l2, skin)
    R(d, 7, 29 - l1, 3, 1, (80, 50, 40))
    R(d, 12, 29 - l2, 3, 1, (80, 50, 40))
    R(d, 7, 22, 8, 3, (60, 90, 200))
    R(d, 7, 15, 8, 8, (235, 80, 80))
    R(d, 9, 15, 4, 1, WHITE)
    if expr == "happy":
        R(d, 4, 11, 2, 5, skin)
        R(d, 16, 11, 2, 5, skin)
    else:
        R(d, 5, 16, 2, 5, skin)
        R(d, 15, 16, 2, 5, skin)
    d.ellipse([5, 4, 16, 15], fill=skin)
    R(d, 5, 3, 12, 4, hair)
    R(d, 5, 7, 2, 3, hair)
    R(d, 15, 7, 2, 3, hair)
    R(d, 3, 6, 2, 4, hair)
    R(d, 17, 6, 2, 4, hair)
    R(d, 3, 5, 2, 1, (255, 100, 140))
    R(d, 17, 5, 2, 1, (255, 100, 140))
    if expr == "cry":
        R(d, 8, 9, 1, 1, INK)
        R(d, 13, 9, 1, 1, INK)
        P(d, 7, 8, INK)
        P(d, 14, 8, INK)
        R(d, 9, 12, 4, 2, (130, 40, 50))
        R(d, 8, 10 + tear, 1, 2, BLUE)
        R(d, 13, 10 + (tear + 1) % 3, 1, 2, BLUE)
    else:
        P(d, 7, 9, INK)
        P(d, 8, 8, INK)
        P(d, 9, 9, INK)
        P(d, 12, 9, INK)
        P(d, 13, 8, INK)
        P(d, 14, 9, INK)
        R(d, 9, 12, 4, 1, (130, 40, 50))
        P(d, 8, 11, (130, 40, 50))
        P(d, 13, 11, (130, 40, 50))
        R(d, 6, 11, 2, 1, PINK)
        R(d, 14, 11, 2, 1, PINK)
    return outline(im)


MINI = {
    "B": ["XX.", "X.X", "XX.", "X.X", "XX."],
    "U": ["X.X", "X.X", "X.X", "X.X", "XXX"],
    "G": [".XX", "X..", "X.X", "X.X", ".XX"],
}


@lru_cache(maxsize=None)
def bug_monster(phase=0, white=False):
    im = Image.new("RGBA", (58, 42))
    d = ImageDraw.Draw(im)
    shell, dark = (120, 50, 150), (70, 25, 85)
    # legs
    for k, x in enumerate((16, 28, 40)):
        off = 2 if (k + phase) % 2 else 0
        d.line([(x, 28), (x - 4 + off, 36), (x - 6 + off, 40)], fill=dark, width=2)
    d.ellipse([9, 6, 52, 34], fill=shell)
    d.ellipse([14, 8, 40, 16], fill=(160, 90, 190))
    for sx, sy in ((38, 20), (44, 12), (22, 24), (46, 24)):
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(230, 60, 90))
    x = 20
    for ch in "BUG":
        draw_pattern(d, MINI[ch], x, 17, YELLOW, 1)
        x += 4
    # head
    d.ellipse([1, 14, 17, 32], fill=dark)
    R(d, 4, 19, 3, 3, (255, 50, 50))
    R(d, 10, 19, 3, 3, (255, 50, 50))
    P(d, 4, 19, (255, 220, 200))
    P(d, 10, 19, (255, 220, 200))
    # mandibles
    R(d, 2, 29, 2, 4, WHITE)
    R(d, 12, 29, 2, 4, WHITE)
    R(d, 3, 11, 1, 4, dark)
    R(d, 11, 10, 1, 5, dark)
    R(d, 2, 10, 2, 1, dark)
    R(d, 11, 9, 2, 1, dark)
    im = outline(im)
    if white:
        a = np.array(im)
        a[a[..., 3] > 0, :3] = 255
        im = Image.fromarray(a)
    return im


@lru_cache(maxsize=None)
def ladybug(phase=0):
    im = Image.new("RGBA", (14, 10))
    d = ImageDraw.Draw(im)
    if phase:
        R(d, 3, 0, 3, 2, (220, 240, 255))
        R(d, 8, 0, 3, 2, (220, 240, 255))
    d.ellipse([2, 2, 11, 9], fill=RED)
    R(d, 7, 2, 1, 8, INK)
    P(d, 4, 5, INK)
    P(d, 9, 6, INK)
    R(d, 11, 4, 2, 3, INK)
    P(d, 12, 4, WHITE)
    return outline(im)


# ---------------------------------------------------------------- backgrounds
_rng = random.Random(7)
FLOWERS = [(_rng.randrange(0, W), _rng.randrange(112, 180), _rng.choice([WHITE, YELLOW, PINK]))
           for _ in range(60)]
TUFTS = [(_rng.randrange(0, W), _rng.randrange(108, 180)) for _ in range(80)]
STARS = [(_rng.randrange(0, W), _rng.randrange(0, 110), _rng.random()) for _ in range(90)]
CLOUDS = [(_rng.randrange(0, W + 80), _rng.randrange(12, 60), _rng.randrange(14, 26)) for _ in range(5)]

NIGHT = (40, 20, 70)


def tint(c, k, to=NIGHT):
    return mix(c, to, k) if k > 0 else c


def cloud(d, x, y, s, col=WHITE):
    for dx, dy, r in ((0, 0, s // 2), (s // 2, -s // 4, s // 2), (s, 0, s // 2), (s // 2, s // 6, s // 2)):
        d.ellipse([x + dx - r, y + dy - r // 2, x + dx + r, y + dy + r // 2 + 2], fill=col)


def bg_meadow(img, T, k=0.0):
    d = ImageDraw.Draw(img)
    sky = [(108, 188, 250), (130, 202, 252), (154, 214, 252), (178, 226, 252), (200, 236, 250)]
    R(d, 0, 0, W, H, tint(sky[-1], k))
    for i, c in enumerate(sky):
        R(d, 0, i * 20, W, 20, tint(c, k))
    if k > 0.3:
        for x, y, ph in STARS[:40]:
            if y < 90 and math.sin(T * 3 + ph * 20) > 0:
                P(d, x, y, tint(WHITE, 0.3 * (1 - k)))
    for x0, y, s in CLOUDS:
        x = (x0 + T * 4) % (W + 80) - 40
        cloud(d, int(x), y, s, tint(WHITE, k))
    # distant hills
    for cx, r in ((40, 60), (150, 45), (260, 70), (340, 50)):
        d.ellipse([cx - r, 92, cx + r, 92 + r], fill=tint((150, 210, 140), k))
    R(d, 0, 104, W, 76, tint((104, 188, 88), k))
    for y in range(110, 180, 12):
        R(d, 0, y, W, 2, tint((96, 178, 80), k))
    for x, y in TUFTS:
        c = tint((64, 146, 64), k)
        P(d, x, y, c)
        P(d, x + 2, y, c)
        P(d, x + 1, y + 1, c)
    for x, y, c in FLOWERS:
        P(d, x, y, tint(c, k))
        P(d, x, y + 1, tint((64, 146, 64), k))


def hill_y(x):
    return 130 + ((x - 160) / 90.0) ** 2 * 26


def bg_sunset(img, lt, night=0.0):
    d = ImageDraw.Draw(img)
    bands = [(58, 40, 108), (96, 52, 132), (150, 70, 140), (206, 96, 128), (240, 132, 110), (255, 178, 110), (255, 212, 140)]
    for i, c in enumerate(bands):
        R(d, 0, i * 17, W, 17, tint(c, night, (18, 18, 50)))
    R(d, 0, 119, W, 61, tint((255, 212, 140), night, (18, 18, 50)))
    for x, y, ph in STARS:
        a = clamp(night * 1.5 + (0.6 - y / 110.0)) if night > 0 else clamp((lt - 14) / 8) * (1 - y / 70.0)
        if a > 0.15 and math.sin(lt * 2 + ph * 30) > -0.3:
            P(d, x, y, mix((255, 200, 160), WHITE, a))
    # sun with retro stripes
    sy = 104 + lt * 0.6
    if night < 1:
        sun = Image.new("RGBA", (44, 44))
        sd = ImageDraw.Draw(sun)
        sd.ellipse([0, 0, 43, 43], fill=(255, 236, 160, int(255 * (1 - night))))
        for j in range(26, 44, 5):
            R(sd, 0, j, 44, 2 - (0 if j < 34 else 0), (0, 0, 0, 0))
        img.paste(sun, (218, int(sy) - 22), sun)
    # distant hills
    far = tint((150, 70, 120), night, (30, 25, 60))
    for cx, r in ((20, 70), (120, 60), (300, 80)):
        d.ellipse([cx - r, 118, cx + r, 118 + r], fill=far)
    near = tint((74, 38, 84), night, (20, 16, 40))
    pts = [(x, hill_y(x)) for x in range(0, W + 1, 4)] + [(W, H), (0, H)]
    d.polygon(pts, fill=near)
    # grass silhouettes on the hill
    for x in range(70, 252, 7):
        y = int(hill_y(x))
        P(d, x, y - 1, near)
        P(d, x + 2, y - 2, near)


def bg_night(img, lt):
    d = ImageDraw.Draw(img)
    bands = [(14, 14, 40), (20, 18, 52), (28, 24, 66), (36, 30, 80), (44, 36, 92)]
    for i, c in enumerate(bands):
        R(d, 0, i * 24, W, 24, c)
    R(d, 0, 120, W, 60, (44, 36, 92))
    for x, y, ph in STARS:
        b = 0.5 + 0.5 * math.sin(lt * 3 + ph * 40)
        P(d, x, y, mix((90, 90, 140), WHITE, b))
        if ph > 0.9 and b > 0.8:
            P(d, x - 1, y, (160, 160, 200))
            P(d, x + 1, y, (160, 160, 200))
    d.ellipse([256, 16, 280, 40], fill=(255, 244, 200))
    d.ellipse([264, 12, 288, 36], fill=bands[0])


# ---------------------------------------------------------------- scene state helpers
class Frame:
    def __init__(self):
        self.fx = []  # hi-res text overlays (text, x, y, font, fill, stroke)
        self.shake = (0, 0)
        self.flash = 0.0
        self.caption = None
        self.fade = 1.0


def text_fx(fr, s, x, y, font=F48, fill=YELLOW, stroke=4, anchor="mm"):
    fr.fx.append((s, x, y, font, fill, stroke, anchor))


def emote_bang(d, x, y):
    R(d, x - 2, y - 1, 5, 11, INK)
    R(d, x - 1, y, 3, 6, YELLOW)
    R(d, x - 1, y + 7, 3, 2, YELLOW)


def emote_anger(d, x, y, t):
    s = 1 if int(t * 6) % 2 else 0
    c = (240, 50, 60)
    for dx, dy in ((0, 0), (5, 0), (0, 5), (5, 5)):
        R(d, x + dx - s, y + dy - s, 3, 1, c)
        R(d, x + dx - s, y + dy - s, 1, 3, c)
    # corners as a "vein" mark
    R(d, x + 1, y + 1, 2, 1, c)
    R(d, x + 5, y + 5, 2, 1, c)


def sweat(d, x, y):
    R(d, x, y, 2, 3, (140, 200, 255))
    P(d, x, y - 1, (140, 200, 255))
    P(d, x, y, WHITE)


def steam(d, x, y, t):
    for i in range(3):
        k = (t * 1.5 + i / 3) % 1
        r = int(2 + k * 4)
        c = mix(WHITE, (200, 200, 210), k)
        d.ellipse([x + i * 6 - r - 6, y - k * 16 - r, x + i * 6 + r - 6, y - k * 16 + r], fill=c)


def dizzy_stars(d, cx, cy, t):
    for i in range(3):
        a = t * 5 + i * 2.094
        star(d, int(cx + math.cos(a) * 14), int(cy + math.sin(a) * 4))


def sparkle(d, x, y, t, col=WHITE):
    k = int(t * 8) % 3
    if k == 0:
        P(d, x, y, col)
    else:
        R(d, x - k, y, 2 * k + 1, 1, col)
        R(d, x, y - k, 1, 2 * k + 1, col)


def blink(expr, T, off=0.0):
    if expr == "normal" and (T + off) % 3.4 < 0.12:
        return "blink"
    return expr


def bounce(who, T):
    return -2 if speaking(who, T) and int(T * 8) % 2 else 0


# ---------------------------------------------------------------- scenes
GROUND = 134


def sc_title(img, lt, T, fr):
    bg_night(img, lt)
    d = ImageDraw.Draw(img)
    # hills
    d.ellipse([-60, 140, 200, 260], fill=(30, 60, 50))
    d.ellipse([140, 138, 400, 260], fill=(26, 52, 44))
    b1 = -abs(math.sin(lt * 5)) * 4
    b2 = -abs(math.sin(lt * 5 + 1.2)) * 4
    blit(img, clawd(blink("angry", lt), arms="up" if int(lt * 3) % 2 else "down"), 52, 176 + b1, 3)
    blit(img, gpt("angry", arms="up" if int(lt * 3 + 1) % 2 else "down"), 268, 176 + b2, 3, flip=True)
    if lt > 1.2:
        rng = random.Random(int(lt * 16))
        pts = [(100, 150)] + [(100 + i * 15, 150 + rng.randint(-6, 6)) for i in range(1, 8)] + [(220, 150)]
        d.line(pts, fill=YELLOW, width=3)
        d.line(pts, fill=WHITE, width=1)
    yy = lerp(-120, 220, ease(seg(lt, 0.2, 0.9))) + (math.sin(lt * 18) * 12 * (1 - seg(lt, 0.9, 1.4)) if lt > 0.9 else 0)
    text_fx(fr, "谁才是最强AI？", BW // 2, int(yy) - 60, F96, (255, 236, 120), 6)
    if lt > 1.2:
        text_fx(fr, "小橙（Claude）", 380, 300, F48, ORANGE_L, 4)
        text_fx(fr, "小绿（ChatGPT）", 900, 300, F48, GREEN_L, 4)
        vs_col = RED if int(lt * 6) % 2 else YELLOW
        text_fx(fr, "VS", BW // 2, 300, F64, vs_col, 5)
    if lt > 2.2:
        text_fx(fr, "～ 一个关于像素宠物的小故事 ～", BW // 2, 380, F32, (220, 220, 255), 3)


def sc_meet(img, lt, T, fr):
    bg_meadow(img, T)
    d = ImageDraw.Draw(img)
    s = seg(lt, 0, 3)
    cx = lerp(-20, 100, s)
    walkc = (int(lt * 8) % 2 + 1) if s < 1 else 0
    s2 = seg(lt, 0.3, 3.3)
    gx = lerp(340, 220, s2)
    walkg = (int(lt * 8) % 2 + 1) if s2 < 1 else 0

    ce = "normal"
    if 3 <= lt < 6.5:
        ce = "happy"
    elif 9.5 <= lt:
        ce = "angry"
    if 13 <= lt < 16.5:
        ce = "flush" if lt > 15 else "angry"
    ge = "normal"
    if 6.5 <= lt < 7.2:
        ge = "surprised"
    elif lt >= 7.2:
        ge = "smug"
    if lt >= 18.3:
        ge = "angry"
    cjump = -math.sin(math.pi * seg(lt, 9.5, 9.9)) * 10
    carms = "up" if 9.5 <= lt < 11 or 16.5 <= lt < 18 else "down"
    garms = "up" if 13 <= lt < 15 else "down"
    blit(img, clawd(blink(ce, T), walkc, carms), cx, GROUND + bounce("C", T) + cjump)
    blit(img, gpt(blink(ge, T, 1.3), walkg, garms, talk=speaking("G", T) and int(T * 8) % 2 == 0), gx, GROUND + bounce("G", T), flip=True)
    if 6.5 <= lt < 7.6:
        emote_bang(d, int(gx), 66)
    if 9.5 <= lt < 16.5 or lt >= 17:
        emote_anger(d, int(cx + 10), 76, lt)
    if lt >= 18.3:
        emote_anger(d, int(gx - 12), 76, lt)
    if 13 <= lt < 16:
        sweat(d, int(cx - 14), 94)


def draw_canvas(d, x, y, t):
    R(d, x - 1, y - 1, 46, 36, INK)
    R(d, x, y, 44, 34, (150, 100, 60))
    R(d, x + 3, y + 3, 38, 28, CREAM)
    # the "masterpiece": a six-legged cat
    c = (240, 160, 80)
    d.ellipse([x + 10, y + 13, x + 32, y + 24], fill=c)
    d.ellipse([x + 26, y + 6, x + 37, y + 17], fill=c)
    d.polygon([(x + 27, y + 9), (x + 28, y + 3), (x + 31, y + 8)], fill=c)
    d.polygon([(x + 33, y + 8), (x + 36, y + 2), (x + 36, y + 9)], fill=c)
    P(d, x + 30, y + 10, INK)
    R(d, x + 33, y + 10, 2, 2, INK)
    R(d, x + 31, y + 14, 3, 1, INK)
    for i in range(6):
        lx = x + 12 + i * 3 + (1 if i % 2 else 0)
        R(d, lx, y + 24, 1, 3 + (i % 3), c)
    d.line([(x + 10, y + 16), (x + 6, y + 12), (x + 8, y + 8), (x + 5, y + 5)], fill=c)
    R(d, x + 20, y + 16, 3, 2, (255, 120, 120))  # random heart-ish blob
    sparkle(d, x - 3, y + 2, t)
    sparkle(d, x + 46, y + 20, t + 0.2)


def draw_code_panel(d, x, y, lt, error):
    R(d, x - 1, y - 1, 66, 46, INK)
    R(d, x, y, 64, 44, (30, 34, 48))
    R(d, x, y, 64, 5, (60, 64, 84))
    for i, c in enumerate((RED, YELLOW, (90, 220, 110))):
        R(d, x + 3 + i * 4, y + 1, 2, 2, c)
    rng = random.Random(3)
    lines = [(rng.randrange(0, 4), [(rng.randrange(4, 14), rng.choice([(120, 200, 255), (255, 170, 90), (190, 150, 255), (200, 200, 200), (140, 230, 140)])) for _ in range(rng.randrange(1, 4))]) for _ in range(60)]
    n = int(lt * 7)
    first = max(0, n - 12)
    for row, idx in enumerate(range(first, n)):
        ind, parts = lines[idx]
        xx = x + 3 + ind * 3
        yy = y + 7 + row * 3
        for ln, col in parts:
            if xx + ln > x + 62:
                break
            R(d, xx, yy, ln, 1, col)
            xx += ln + 2
    if error and int(lt * 5) % 2 == 0:
        R(d, x + 1, y + 7 + 6 * 3 - 1, 62, 3, (200, 40, 50))


def sc_contest(img, lt, T, fr):
    bg_meadow(img, T)
    d = ImageDraw.Draw(img)
    cx = lerp(100, 110, seg(lt, 0, 0.5))
    gx = lerp(220, 210, seg(lt, 0, 0.5))
    ce, ge = "angry", "angry"
    carms, garms = "down", "down"
    if 3 <= lt < 7:
        ge, garms = "smug", "up"
        ce = "normal"
    if 7 <= lt < 10.5:
        ce, ge = "smug", "happy"
    if 10.5 <= lt < 13.5:
        ge, ce = "flush", "blink" if lt % 1.2 < 0.15 else "smug"
    if 13.5 <= lt < 16.5:
        ce, carms, ge = "happy", "up", "normal"
    if 16.5 <= lt < 19.5:
        ce, ge, garms = "surprised", "smug", "fwd"
    if lt >= 19.5:
        ce, carms, ge = "flush", "up", "surprised"
    shakec = random.Random(int(T * 30)).randint(-1, 1) if lt >= 19.5 else 0
    blit(img, clawd(blink(ce, T), 0, carms), cx + shakec, GROUND + bounce("C", T))
    blit(img, gpt(blink(ge, T, 0.8), 0, garms, talk=speaking("G", T) and int(T * 8) % 2 == 0), gx, GROUND + bounce("G", T), flip=True)
    # stare-down lightning
    if lt < 3:
        rng = random.Random(int(T * 16))
        pts = [(cx + 16, 108)]
        for i in range(1, 8):
            pts.append((lerp(cx + 16, gx - 16, i / 8), 108 + rng.randint(-5, 5)))
        pts.append((gx - 16, 110))
        d.line(pts, fill=YELLOW, width=3)
        d.line(pts, fill=WHITE, width=1)
    if 4.3 <= lt < 13.5:
        pop = ease(seg(lt, 4.3, 4.6))
        yy = int(lerp(90, 26, pop))
        draw_canvas(d, int(gx - 22), yy, lt)
    if 7 <= lt < 10.5:
        sweat(d, int(cx - 14), 96)
    if 10.5 <= lt < 13.5:
        emote_anger(d, int(gx - 14), 80, lt)
    if 13.8 <= lt < 22:
        draw_code_panel(d, int(cx - 32), 26, lt - 13.8, lt >= 16.8)
    if 16.8 <= lt < 19.5 and int(lt * 5) % 2 == 0:
        text_fx(fr, "ERROR!", int(cx * S), 66, F32, (255, 90, 90), 3)
    if lt >= 19.5:
        steam(d, int(cx), 84, lt)
        emote_anger(d, int(cx + 10), 76, lt)
        emote_anger(d, int(gx - 12), 76, lt + 0.3)
    if lt >= 21.6:
        fr.flash = seg(lt, 21.6, 22) * 0.9


WORDS = ["砰！", "啪！", "嘿哈！", "咚！", "嗷呜！", "啊打！", "吃我一钳！", "喵？！"]


def sc_fight(img, lt, T, fr):
    bg_meadow(img, T)
    d = ImageDraw.Draw(img)
    if lt < 1:
        s = ease(seg(lt, 0, 0.9))
        cx, gx = lerp(110, 150, s), lerp(210, 170, s)
        hop = -math.sin(math.pi * s) * 30
        blit(img, clawd("angry", 0, "up"), cx, GROUND + hop)
        blit(img, gpt("angry", 0, "up"), gx, GROUND + hop, flip=True)
        return
    if lt < 9.2:
        ccx, ccy = 160, 108
        rng = random.Random(int(lt * 7))
        # limbs popping out
        for i in range(4):
            a = rng.random() * math.tau
            px, py = ccx + math.cos(a) * 40, ccy + math.sin(a) * 24
            kind = rng.choice(["claw", "paw", "star", "claw", "paw"])
            if kind == "claw":
                R(d, px - 5, py - 3, 10, 6, INK)
                R(d, px - 4, py - 2, 8, 4, ORANGE)
                R(d, px + 2, py - 4, 3, 2, ORANGE_D)
            elif kind == "paw":
                d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=INK)
                d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=GREEN)
            else:
                star(d, int(px), int(py))
        puffs = []
        for i in range(11):
            a = i * math.tau / 11 + lt * 2.2
            r = 22 + 4 * math.sin(lt * 9 + i)
            puffs.append((ccx + math.cos(a) * r * 1.35, ccy + math.sin(a) * r * 0.7, 14 + 3 * math.sin(lt * 11 + i * 2)))
        for x, y, r in puffs:
            d.ellipse([x - r - 1, y - r - 1, x + r + 1, y + r + 1], fill=INK)
        for x, y, r in puffs:
            d.ellipse([x - r, y - r, x + r, y + r], fill=(236, 236, 242))
        for x, y, r in puffs:
            d.ellipse([x - r + 3, y - r + 2, x + r - 5, y + r - 6], fill=WHITE)
        d.ellipse([ccx - 30, ccy - 14, ccx + 30, ccy + 14], fill=(240, 240, 246))
        # faces peeking out of the brawl
        if int(lt * 3) % 2:
            blit(img, clawd("angry", 0, "up"), ccx - 16, ccy + 10, 1)
            blit(img, gpt("dizzy"), ccx + 14, ccy + 12, 1, flip=True)
        else:
            blit(img, clawd("dizzy"), ccx + 10, ccy + 10, 1, flip=True)
            blit(img, gpt("angry", 0, "up"), ccx - 12, ccy + 12, 1)
        for i in range(5):
            a = rng.random() * math.tau
            star(d, int(ccx + math.cos(a) * 60), int(ccy + math.sin(a) * 34))
        rs = random.Random(int(T * 30))
        fr.shake = (rs.randint(-2, 2) * S, rs.randint(-2, 2) * S)
        if 4.5 <= lt < 6.8:
            box = (104, 66, 216, 150)
            reg = img.crop(box)
            reg = reg.resize((14, 10), Image.BILINEAR).resize((box[2] - box[0], box[3] - box[1]), Image.NEAREST)
            img.paste(reg, box[:2])
            fr.caption = "（画面过于激烈，已自动打码）"
        else:
            rw = random.Random(int(lt / 0.35))
            for k in range(2):
                text_fx(fr, rw.choice(WORDS), 640 + rw.randint(-300, 300), 380 + rw.randint(-200, 120),
                        F64, rw.choice([YELLOW, (255, 120, 80), WHITE, (120, 220, 255)]), 5)
        if lt >= 9.0:
            fr.flash = 1 - seg(lt, 9.0, 9.2)
        return
    # knocked apart
    s = seg(lt, 9.2, 10.1)
    cx = lerp(160, 85, s)
    gx = lerp(160, 235, s)
    arc = -math.sin(math.pi * s) * 40
    landed = s >= 1
    blit(img, clawd("dizzy", sit=landed, band=True, arms="up" if not landed else "down"), cx, GROUND + arc + (8 if landed else 0) + (bounce("C", T) if landed else 0))
    blit(img, gpt("dizzy", sit=landed, bump=True, arms="up" if not landed else "down", talk=speaking("G", T) and int(T * 8) % 2 == 0), gx, GROUND + arc + (2 if landed else 0) + (bounce("G", T) if landed else 0), flip=True)
    if landed:
        dizzy_stars(d, cx, GROUND - 30, lt)
        dizzy_stars(d, gx, GROUND - 42, lt + 1)
    fr.flash = max(fr.flash, 0.6 * (1 - seg(lt, 9.2, 9.6)))
    if lt < 10.3:
        for i in range(8):
            a = i * math.tau / 8
            k = seg(lt, 9.2, 10.3)
            r = 20 + k * 60
            c = mix(WHITE, (200, 200, 200), k)
            rr = int(8 * (1 - k)) + 1
            x, y = 160 + math.cos(a) * r * 1.3, 108 + math.sin(a) * r * 0.6
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c)


def sc_bug(img, lt, T, fr):
    k = 0.65 * seg(lt, 0, 2)
    if lt > 17.5:
        k *= 1 - seg(lt, 17.5, 19.5)
    bg_meadow(img, T, k)
    d = ImageDraw.Draw(img)
    # kid
    kx = lerp(-20, 50, seg(lt, 0.8, 3))
    kwalk = (int(lt * 10) % 2 + 1) if 0.8 < lt < 3 else 0
    kexpr = "cry" if lt < 18.8 else "happy"
    kjump = -abs(math.sin((lt - 18.8) * 7)) * 8 if lt >= 18.8 else 0
    kshake = random.Random(int(T * 20)).randint(-1, 1) if kexpr == "cry" and lt > 3 else 0
    blit(img, kid(kexpr, kwalk, int(T * 6) % 3), kx + kshake, GROUND + kjump + bounce("K", T), 2, anchor=(11, 29))
    # pets
    st = seg(lt, 5.3, 6.3)
    standing = lt >= 5.3
    cx = lerp(85, 112, ease(st))
    gx = lerp(235, 170, ease(st))
    hop = -math.sin(math.pi * st) * 14
    ce = "normal" if lt < 2.5 else "surprised"
    ge = "blink" if lt < 2.5 and int(lt * 2) % 3 == 0 else ("normal" if lt < 2.5 else "surprised")
    carms = garms = "down"
    gflip = True
    if 6.3 <= lt:
        ce, ge = "angry", "angry"
        gflip = False
    if 9.5 <= lt < 12.5:
        ge = "happy"
    if 12.5 <= lt < 15.5:
        ge, garms = "angry", "fwd"
    if 15.5 <= lt < 18.5:
        ce, carms = "angry", "fwd"
    if lt >= 18.5:
        ce, ge = "happy", "happy"
        carms = garms = "up"
    if lt >= 19.2:
        gflip = True
    cb = -abs(math.sin(lt * 6)) * 5 if lt >= 18.5 else 0
    blit(img, clawd(blink(ce, T), 0, carms, sit=not standing, band=True), cx, GROUND + hop + (0 if standing else 8) + bounce("C", T) + cb)
    blit(img, gpt(blink(ge, T, 0.6), 0, garms, sit=not standing, bump=True, talk=speaking("G", T) and int(T * 8) % 2 == 0), gx, GROUND + hop + (0 if standing else 2) + bounce("G", T) + cb, flip=gflip)
    if 5.0 <= lt < 6.0:
        emote_bang(d, int(cx), 74)
        emote_bang(d, int(gx), 70)
    # bug monster
    bx = lerp(380, 262, ease(seg(lt, 4, 6.5)))
    by = GROUND + 2 + math.sin(T * 6) * 1.5
    if lt < 17.5:
        hit = False
        if 15.8 <= lt < 17.5:
            for i in range(7):
                t0 = 15.8 + i * 0.22
                if 0 <= lt - t0 < 0.35:
                    p = (lt - t0) / 0.35
                    px = lerp(cx + 18, bx - 20, p)
                    py = lerp(GROUND - 26, GROUND - 40, p) - math.sin(math.pi * p) * 12
                    text_fx(fr, ["{ }", "</>", "fix", "( )"][i % 4], int(px * S), int(py * S), F48, ORANGE_L, 4)
                if 0 <= lt - (t0 + 0.35) < 0.07:
                    hit = True
        wob = random.Random(int(T * 20)).randint(-2, 2) if hit else 0
        blit(img, bug_monster(int(T * 8) % 2, hit), bx + wob, by, 2, anchor=(29, 40))
        if 12.5 <= lt < 15.8:
            # scan beam from GPT to the bug
            x0, y0 = gx + 14, GROUND - 22
            x1, y1 = bx - 30, GROUND - 42
            n = 14
            for i in range(n):
                p = ((i + lt * 3) % n) / n
                R(d, int(lerp(x0, x1, p)), int(lerp(y0, y1, p)), 2, 2, GREEN_L if i % 2 else WHITE)
            if int(lt * 6) % 2 == 0:
                rx, ry = int(bx - 22), int(GROUND - 58)
                for dx, dy in ((0, 0), (20, 0), (0, 20), (20, 20)):
                    R(d, rx + dx - 1, ry + dy - 1, 4, 1, RED)
                    R(d, rx + dx - 1 + (0 if dx == 0 else 3), ry + dy - 1, 1, 4, RED)
            if lt > 13.3:
                text_fx(fr, "弱点：第 23 行", int(bx * S), 150, F32, (255, 110, 110), 3)
    else:
        # poof + cute ladybug flying away
        p = seg(lt, 17.5, 18.2)
        if p < 1:
            for i in range(10):
                a = i * math.tau / 10
                r = 6 + p * 34
                rr = int(12 * (1 - p)) + 1
                x, y = bx + math.cos(a) * r, GROUND - 30 + math.sin(a) * r * 0.7
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=mix(WHITE, (210, 200, 230), p))
        if lt > 17.8:
            tt = lt - 17.8
            lx = bx - 10 + tt * 26
            ly = GROUND - 30 - tt * 22 + math.sin(tt * 8) * 3
            blit(img, ladybug(int(T * 12) % 2), lx, ly, 2, anchor=(7, 9))
            heart(d, int(lx - 2), int(ly - 30), 1)
        if lt > 18.2:
            rs = random.Random(5)
            for i in range(10):
                sparkle(d, rs.randrange(20, 300), rs.randrange(40, 120), lt + i * 0.13, YELLOW if i % 2 else WHITE)
    if 1.5 <= lt < 3:
        fr.shake = (random.Random(int(T * 30)).randint(-1, 1) * S, 0)
    if 4.8 <= lt < 6.5:
        fr.shake = (random.Random(int(T * 30)).randint(-2, 2) * S, random.Random(int(T * 31)).randint(-1, 1) * S)
        if lt < 6.2:
            text_fx(fr, "吼——！", 1060, 220, F64, (220, 120, 255), 5)


def sc_sunset(img, lt, T, fr):
    bg_sunset(img, lt)
    d = ImageDraw.Draw(img)
    cx = 142
    gx = lerp(184, 170, ease(seg(lt, 15.6, 16.3)))
    ge, ce = "normal", "normal"
    gflip = False  # facing right: watching the sunset
    gtear = -1
    if 2 <= lt < 5.5:
        ge, gflip = "shy", True
    if 5.5 <= lt < 12.5:
        ce, ge = ("happy" if lt > 9 else "normal"), "shy"
        gflip = True
    if 12.5 <= lt < 15:
        ge, gflip = "shy", True
        gtear = int(T * 5) % 3
        ce = "surprised" if lt < 13.5 else "normal"
    if 15 <= lt < 17:
        ce, ge, gflip = "happy", "happy", True
    if 17 <= lt < 19.5:
        ge, ce, gflip = "smug", "normal", True
    if lt >= 19.5:
        ce, ge, gflip = "smug", "happy", True
    if lt >= 21:
        ce, ge = "laugh", "laugh"
    lb = -abs(math.sin(lt * 9)) * 3 if lt >= 21 else 0
    blit(img, clawd(blink(ce, T), 0, "down", sit=True, band=True), cx, hill_y(cx) + 8 + bounce("C", T) + lb)
    blit(img, gpt(blink(ge, T, 1.1), 0, "up" if 15.6 <= lt < 17 else "down", sit=True, bump=True, tear=gtear,
                  talk=speaking("G", T) and int(T * 8) % 2 == 0),
         gx, hill_y(gx) + 3 + bounce("G", T) + lb, flip=gflip)
    if 16.2 <= lt < 20:
        p = seg(lt, 16.2, 20)
        s = 2 if p < 0.15 else 3
        heart(d, int((cx + gx) / 2 - 10), int(78 - p * 26), s)
        for i in range(4):
            q = (p * 1.5 + i * 0.25) % 1
            heart(d, int((cx + gx) / 2 - 30 + i * 18 + math.sin(q * 8) * 4), int(110 - q * 60), 1, PINK)
    if lt >= 21:
        for i, (x, y) in enumerate(((330, 260), (900, 240), (620, 170))):
            text_fx(fr, "哈哈哈！", x + int(math.sin(lt * 4 + i) * 10), y - int((lt - 21) * 20), F48, (255, 240, 180), 4)
    # fireflies
    rs = random.Random(11)
    for i in range(10):
        fx0, fy0 = rs.randrange(0, W), rs.randrange(100, 170)
        x = fx0 + math.sin(lt * 0.7 + i) * 10
        y = fy0 + math.cos(lt * 0.9 + i * 2) * 6
        if math.sin(lt * 3 + i) > 0 and lt > 6:
            P(d, int(x), int(y), (255, 250, 170))


def sc_end(img, lt, T, fr):
    bg_sunset(img, 23, night=1.0)
    d = ImageDraw.Draw(img)
    blit(img, clawd("sleep", 0, "down", sit=True, band=True), 150, hill_y(150) + 8)
    blit(img, gpt("sleep", 0, "down", sit=True, bump=True), 166, hill_y(166) + 3, flip=True)
    heart(d, 152, 88 - int(math.sin(lt * 2) * 2), 1)
    for i in range(3):
        q = (lt * 0.5 + i / 3) % 1
        text_fx(fr, "Z", int((176 + q * 30) * S), int((102 - q * 30) * S), F32 if i % 2 else F48, (200, 210, 255), 3)
    a = seg(lt, 0.5, 1.6)
    if a > 0:
        col = mix((20, 20, 50), (255, 236, 150), a)
        text_fx(fr, "全 剧 终", BW // 2, 140, F96, col, 6)
    if lt > 1.8:
        text_fx(fr, "最强的，是一起帮助别人的我们 ♥", BW // 2, 250, F32, mix((20, 20, 50), WHITE, seg(lt, 1.8, 2.6)), 3)
    if lt > 2.6:
        text_fx(fr, "THE END", BW // 2, 300, F32, mix((20, 20, 50), (180, 180, 220), seg(lt, 2.6, 3.4)), 3)


SCENE_FN = {
    "title": sc_title, "meet": sc_meet, "contest": sc_contest, "fight": sc_fight,
    "bug": sc_bug, "sunset": sc_sunset, "end": sc_end,
}


# ---------------------------------------------------------------- dialogue box
def wrap(txt, n):
    out, cur = [], ""
    for ch in txt:
        cur += ch
        if len(cur) >= n:
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


def draw_dialog(bd, T):
    for a, b, who, txt in LINES:
        if a <= T < b:
            break
    else:
        return
    name, col, _ = SPEAKERS[who]
    n = int((T - a) * CPS)
    shown = txt[:n]
    x0, y0, x1, y1 = 32, 556, BW - 32, BH - 20
    bd.rectangle([x0, y0 + 8, x1, y1 - 8], fill=INK)
    bd.rectangle([x0 + 8, y0, x1 - 8, y1], fill=INK)
    bd.rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], fill=CREAM)
    bd.rectangle([x0 + 8, y1 - 16, x1 - 8, y1 - 8], fill=(232, 222, 200))
    # name tag
    tw = int(bd.textlength(name, font=F32)) + 40
    bd.rectangle([x0 + 24, y0 - 36, x0 + 24 + tw, y0 + 4], fill=INK)
    bd.rectangle([x0 + 28, y0 - 32, x0 + 20 + tw, y0 + 4], fill=col)
    bd.text((x0 + 44, y0 - 30), name, font=F32, fill=WHITE)
    for i, line in enumerate(wrap(shown, 34)):
        bd.text((x0 + 40, y0 + 26 + i * 44), line, font=F32, fill=INK)
    if n >= len(txt) and int(T * 3) % 2 == 0:
        bd.polygon([(x1 - 52, y1 - 44), (x1 - 28, y1 - 44), (x1 - 40, y1 - 30)], fill=col)


# ---------------------------------------------------------------- render
def render_frame(T):
    for name, a, b in SCENES:
        if a <= T < b:
            break
    lt = T - a
    img = Image.new("RGB", (W, H))
    fr = Frame()
    SCENE_FN[name](img, lt, T, fr)
    big = img.resize((BW, BH), Image.NEAREST)
    if fr.shake != (0, 0):
        sh = Image.new("RGB", (BW, BH), INK)
        sh.paste(big, fr.shake)
        big = sh
    bd = ImageDraw.Draw(big)
    for s, x, y, font, fill, stroke, anchor in fr.fx:
        bd.text((x, y), s, font=font, fill=fill, stroke_width=stroke, stroke_fill=INK, anchor=anchor)
    if fr.caption:
        bd.rectangle([0, 470, BW, 530], fill=(0, 0, 0))
        bd.text((BW // 2, 500), fr.caption, font=F32, fill=WHITE, anchor="mm")
    draw_dialog(bd, T)
    arr = np.asarray(big).astype(np.float32)
    if fr.flash > 0:
        arr = arr + (255 - arr) * fr.flash
    fade = min(1.0, (T - a) / 0.35, (b - T) / 0.35) if name not in ("title",) else min(1.0, (b - T) / 0.35)
    if name == "end":
        fade = min(1.0, (T - a) / 0.35, (b - T) / 1.5)
    if fade < 1:
        arr *= max(0.0, fade)
    return np.clip(arr, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- audio
SR = 44100
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def hz(n):
    name, octv = n[:-1], int(n[-1])
    m = 12 * (octv + 1) + NOTE[name]
    return 440.0 * 2 ** ((m - 69) / 12)


def tone(freq, dur, kind="sq", vol=0.2, duty=0.5, attack=0.005, release=0.04, decay=0.0, slide=None):
    n = int(dur * SR)
    if n <= 0:
        return np.zeros(0)
    t = np.arange(n) / SR
    if slide is not None:
        f = np.linspace(freq, slide, n)
        ph = np.cumsum(f) / SR
    else:
        ph = t * freq
    ph = ph % 1.0
    if kind == "sq":
        w = np.where(ph < duty, 1.0, -1.0)
    elif kind == "tri":
        w = 4 * np.abs(ph - 0.5) - 1
    elif kind == "sin":
        w = np.sin(ph * math.tau)
    elif kind == "saw":
        w = 2 * ph - 1
    else:  # noise
        w = np.random.default_rng(int(freq * 1000) % 99991).uniform(-1, 1, n)
    env = np.ones(n)
    a = max(1, int(attack * SR))
    env[:a] = np.linspace(0, 1, a)
    r = min(n, max(1, int(release * SR)))
    env[-r:] *= np.linspace(1, 0, r)
    if decay > 0:
        env *= np.exp(-t / decay)
    return w * env * vol


class Mixer:
    def __init__(self, seconds):
        self.buf = np.zeros(int(seconds * SR) + SR)

    def add(self, t0, sig):
        i = int(t0 * SR)
        if i < 0 or i >= len(self.buf):
            return
        j = min(len(self.buf), i + len(sig))
        self.buf[i:j] += sig[: j - i]

    def seq(self, t0, bpm, notes, t_end, kind="sq", vol=0.15, duty=0.5, gap=0.9, loop=True, decay=0.0):
        beat = 60.0 / bpm
        t = t0
        while t < t_end:
            for n, beats in notes:
                if t >= t_end:
                    break
                dur = beats * beat
                if n:
                    for nn in n.split("+"):
                        self.add(t, tone(hz(nn), min(dur * gap, t_end - t), kind, vol, duty, decay=decay))
                t += dur
            if not loop:
                break

    def drums(self, t0, bpm, pattern, t_end, vol=1.0):
        beat = 60.0 / bpm
        step = beat / 2
        t = t0
        i = 0
        while t < t_end:
            ch = pattern[i % len(pattern)]
            if ch == "k":
                self.add(t, tone(120, 0.12, "sin", 0.35 * vol, slide=45, decay=0.05))
            elif ch == "s":
                self.add(t, tone(1.1, 0.1, "noise", 0.16 * vol, decay=0.04))
            elif ch == "h":
                self.add(t, tone(2.2, 0.03, "noise", 0.05 * vol, decay=0.01))
            t += step
            i += 1


def bars(chords, per_bar, fn):
    out = []
    for c in chords:
        out += fn(c, per_bar)
    return out


def bass_pattern(roots, octave_notes=True):
    out = []
    for r in roots:
        lo, hi = r + "2", r + "3"
        out += [(lo, 0.5), (hi, 0.5)] * 4 if octave_notes else [(lo, 1)] * 4
    return out


def build_audio():
    mx = Mixer(TOTAL)
    # --- A: happy theme (C major, 132 bpm), 0 → 46.5
    melA = [
        ("E5", .5), ("G5", .5), ("C6", 1), ("G5", .5), ("E5", .5), ("G5", 1),
        ("D5", .5), ("G5", .5), ("B5", 1), ("A5", .5), ("G5", .5), ("D5", 1),
        ("C5", .5), ("E5", .5), ("A5", 1), ("G5", .5), ("E5", .5), ("C5", 1),
        ("F5", .5), ("A5", .5), ("G5", .5), ("F5", .5), ("E5", 1), ("D5", 1),
        ("E5", .5), ("E5", .5), ("G5", 1), ("C6", .5), ("B5", .5), ("A5", 1),
        ("B5", .5), ("A5", .5), ("G5", 1), ("D5", 1), ("G5", 1),
        ("A5", .5), ("G5", .5), ("F5", 1), ("E5", .5), ("D5", .5), ("C5", 1),
        ("B4", 1), ("D5", 1), ("G5", 2),
    ]
    endA = 46.4
    mx.seq(0.3, 132, melA, endA, "sq", 0.075, 0.25)
    mx.seq(0.3, 132, bass_pattern(["C", "G", "A", "F", "C", "G", "F", "G"]), endA, "tri", 0.22)
    mx.seq(0.3, 132, bars(["C4+E4+G4", "B3+D4+G4", "C4+E4+A4", "C4+F4+A4", "C4+E4+G4", "B3+D4+G4", "C4+F4+A4", "B3+D4+G4"], 4,
                          lambda c, n: [(c, 1), (None, 1), (c, 1), (None, 1)]), endA, "sq", 0.025, 0.5, gap=0.4)
    mx.drums(0.3, 132, "khshkhsh", endA, 0.8)

    # --- fight theme (A minor, 168 bpm), 48 → 57.2
    melF = [
        ("A5", .5), ("A5", .5), ("C6", .5), ("A5", .5), ("E5", .5), ("A5", .5), ("C6", .5), ("D6", .5),
        ("C6", .5), ("A5", .5), ("F5", .5), ("A5", .5), ("C6", 1), ("A5", 1),
        ("B5", .5), ("G5", .5), ("D5", .5), ("G5", .5), ("B5", .5), ("D6", .5), ("B5", 1),
        ("G#5", .5), ("E5", .5), ("B4", .5), ("E5", .5), ("G#5", 1), ("B5", 1),
    ]
    mx.seq(48.0, 168, melF, 57.1, "sq", 0.07, 0.5)
    mx.seq(48.0, 168, bass_pattern(["A", "F", "G", "E"]), 57.1, "saw", 0.12)
    mx.drums(48.0, 168, "kskskkss", 57.1, 1.0)
    # dizzy after-fight wobble
    for i, n in enumerate(["E5", "D#5", "D5", "C#5", "C5", "B4", "A#4", "A4"] * 2):
        mx.add(58.4 + i * 0.42, tone(hz(n), 0.36, "tri", 0.12, slide=hz(n) * 0.97, decay=0.3))

    # --- tense (D minor, 96 bpm), 65 → 71.3
    tense = [("D5", 2), ("F5", 1), ("E5", 1), ("D5", 2), ("A4", 2), ("Bb4", 2), ("C5", 1), ("D5", 1), ("A4", 4)]
    mx.seq(65.5, 96, tense, 71.3, "sq", 0.05, 0.25)
    mx.seq(65.5, 96, [("D2", 2), ("D2", 2), ("D2", 2), ("D2", 2), ("Bb1", 4), ("A1", 4)], 71.3, "tri", 0.3)
    mx.drums(65.5, 96, "k.......", 71.3, 1.2)
    # --- heroic (C major, 150 bpm), 71.5 → 82.5
    hero = [
        ("G4", .5), ("C5", .5), ("E5", 1), ("G5", 1), ("E5", .5), ("G5", .5),
        ("A5", 1), ("F5", 1), ("C5", 1), ("A5", 1),
        ("B5", 1), ("G5", .5), ("A5", .5), ("B5", 1), ("D6", 1),
        ("C6", 2), ("G5", 1), ("C6", 1),
    ]
    mx.seq(71.5, 150, hero, 82.4, "sq", 0.07, 0.5)
    mx.seq(71.5, 150, bass_pattern(["C", "F", "G", "C"]), 82.4, "tri", 0.22)
    mx.drums(71.5, 150, "khskkhsh", 82.4, 0.9)
    # victory fanfare
    for i, (n, d) in enumerate([("C5", .14), ("E5", .14), ("G5", .14), ("C6", .7)]):
        mx.add(83.0 + i * 0.14, tone(hz(n), d, "sq", 0.09, 0.5))
    mx.add(84.1, tone(hz("G5"), 0.25, "sq", 0.08))
    mx.add(84.4, tone(hz("C6"), 1.6, "sq", 0.09, decay=0.9))
    mx.add(84.4, tone(hz("C4"), 1.6, "tri", 0.2, decay=0.9))
    mx.add(84.4, tone(hz("E5"), 1.6, "sq", 0.04, 0.25, decay=0.9))

    # --- tender (F major, 80 bpm), 88 → 111
    tender = [
        ("A5", 1.5), ("G5", .5), ("F5", 1), ("C5", 1),
        ("E5", 2), ("G5", 1), ("E5", 1),
        ("F5", 1.5), ("E5", .5), ("D5", 1), ("F5", 1),
        ("D5", 2), ("C5", 2),
        ("A5", 1.5), ("Bb5", .5), ("C6", 1), ("A5", 1),
        ("G5", 2), ("E5", 1), ("C5", 1),
        ("D5", 1), ("F5", 1), ("A5", 1), ("G5", 1),
        ("F5", 4),
    ]
    mx.seq(88.4, 80, tender, 110.8, "tri", 0.2, decay=0.0)
    mx.seq(88.4, 80, tender, 110.8, "sq", 0.025, 0.125)
    arp = {"F": ["F3", "C4", "F4", "A4"], "C": ["C3", "G3", "C4", "E4"], "Dm": ["D3", "A3", "D4", "F4"], "Bb": ["Bb2", "F3", "Bb3", "D4"]}
    arps = []
    for c in ["F", "C", "Dm", "Bb", "F", "C", "Dm", "F"]:
        a = arp[c]
        arps += [(a[0], .5), (a[1], .5), (a[2], .5), (a[3], .5), (a[2], .5), (a[1], .5), (a[2], .5), (a[3], .5)]
    mx.seq(88.4, 80, arps, 110.8, "tri", 0.12, gap=0.95)

    # --- ending music box
    for i, n in enumerate(["F5", "A5", "C6", "F6", "C6", "A5", "C6", "F6"]):
        mx.add(111.4 + i * 0.36, tone(hz(n), 1.2, "tri", 0.16, decay=0.5))
    for n in ["F4", "A4", "C5", "F5"]:
        mx.add(114.3, tone(hz(n), 3.6, "tri", 0.09, decay=1.4))

    # ----------------------------------------------------------- sfx
    def blips():
        for a, b, who, txt in LINES:
            f = SPEAKERS[who][2]
            for i, ch in enumerate(txt):
                if i % 2 == 0 and ch not in "…，。！？～ —":
                    t = a + i / CPS
                    mx.add(t, tone(f * (1 + 0.06 * ((i * 7) % 3)), 0.035, "sq", 0.05, 0.5))
    blips()

    def boing(t, lo=300, hi=900):
        mx.add(t, tone(lo, 0.18, "sq", 0.08, 0.5, slide=hi))

    def ding(t):
        mx.add(t, tone(1320, 0.08, "sq", 0.07))
        mx.add(t + 0.08, tone(1760, 0.14, "sq", 0.07, decay=0.1))

    def punch(t, seed=0):
        mx.add(t, tone(3.3 + seed, 0.09, "noise", 0.25, decay=0.03))
        mx.add(t, tone(180, 0.12, "sin", 0.35, slide=50, decay=0.05))

    def poof(t, dur=0.6, vol=0.3):
        mx.add(t, tone(7.7, dur, "noise", vol, decay=dur / 3))
        mx.add(t, tone(90, dur, "sin", vol, slide=30, decay=dur / 3))

    def zap(t):
        mx.add(t, tone(1600, 0.12, "sq", 0.06, 0.5, slide=300))

    def chime(t):
        for i, n in enumerate(["C6", "E6", "G6", "C7"]):
            mx.add(t + i * 0.07, tone(hz(n), 0.5, "tri", 0.14, decay=0.25))

    def anger(t):
        mx.add(t, tone(700, 0.06, "sq", 0.06))
        mx.add(t + 0.07, tone(500, 0.08, "sq", 0.06))

    # title drop
    boing(0.9, 200, 700)
    punch(1.25)
    # meet
    for i in range(12):
        mx.add(6 + i * 0.125 * 2, tone(220 if i % 2 else 260, 0.04, "tri", 0.1))
    ding(SC["meet"] + 6.5)
    anger(SC["meet"] + 9.5)
    boing(SC["meet"] + 9.5)
    anger(SC["meet"] + 18.3)
    # contest
    for i in range(10):
        zap(SC["contest"] + i * 0.28)
    mx.add(SC["contest"] + 4.3, tone(500, 0.1, "sq", 0.08, slide=1200))
    chime(SC["contest"] + 4.6)
    mx.add(SC["contest"] + 7.0, tone(400, 0.5, "tri", 0.12, slide=180))  # awkward slide
    anger(SC["contest"] + 10.5)
    for i in range(20):
        mx.add(SC["contest"] + 13.8 + i * 0.13, tone(1800 + (i % 3) * 200, 0.02, "noise", 0.04))
    for i in range(3):
        mx.add(SC["contest"] + 16.8 + i * 0.4, tone(160, 0.2, "sq", 0.08))
    anger(SC["contest"] + 19.5)
    mx.add(SC["contest"] + 19.6, tone(5.5, 2.0, "noise", 0.04, decay=1.2))  # steam hiss
    mx.add(SC["contest"] + 21.6, tone(200, 0.4, "sq", 0.1, slide=1400))
    # fight
    boing(SC["fight"] + 0.05, 250, 800)
    rng = random.Random(4)
    t = SC["fight"] + 1.0
    while t < SC["fight"] + 9.0:
        if not (SC["fight"] + 4.5 <= t < SC["fight"] + 6.8):
            punch(t, rng.random())
        else:
            mx.add(t, tone(4.4 + rng.random(), 0.05, "noise", 0.08, decay=0.02))
        t += rng.choice([0.18, 0.24, 0.3, 0.36])
    mx.add(SC["fight"] + 4.5, tone(1000, 0.3, "sq", 0.06, 0.5))  # censor beep
    mx.add(SC["fight"] + 6.3, tone(1000, 0.3, "sq", 0.06, 0.5))
    poof(SC["fight"] + 9.0, 0.9, 0.4)
    mx.add(SC["fight"] + 9.3, tone(900, 0.7, "sq", 0.05, 0.5, slide=200))
    punch(SC["fight"] + 10.1)
    punch(SC["fight"] + 10.15, 0.5)
    # bug
    mx.add(SC["bug"] + 0.3, tone(8.8, 2.2, "noise", 0.08, decay=1.0))
    mx.add(SC["bug"] + 0.3, tone(55, 2.2, "saw", 0.08, decay=1.0))
    for i in range(8):
        mx.add(SC["bug"] + 0.9 + i * 0.25, tone(300, 0.04, "tri", 0.1))
    ding(SC["bug"] + 5.0)
    mx.add(SC["bug"] + 4.8, tone(80, 1.2, "saw", 0.18, slide=50, decay=0.8))
    mx.add(SC["bug"] + 4.8, tone(9.9, 1.2, "noise", 0.12, decay=0.6))
    boing(SC["bug"] + 5.3)
    for i in range(12):
        mx.add(SC["bug"] + 12.6 + i * 0.25, tone(880 + (i % 4) * 110, 0.06, "sq", 0.04, 0.25))
    for i in range(7):
        zap(SC["bug"] + 15.8 + i * 0.22)
        punch(SC["bug"] + 15.8 + i * 0.22 + 0.35, 0.3)
    poof(SC["bug"] + 17.5)
    chime(SC["bug"] + 17.9)
    # sunset
    chime(SC["sunset"] + 16.2)
    boing(SC["sunset"] + 15.6, 400, 700)
    for i in range(6):
        mx.add(SC["sunset"] + 21 + i * 0.25, tone(600 + (i % 2) * 150, 0.08, "sq", 0.04, 0.25))

    buf = mx.buf[: int(TOTAL * SR)]
    # gentle limiter
    peak = np.max(np.abs(buf)) or 1.0
    buf = np.tanh(buf / peak * 1.4) * 0.85
    fade = int(1.0 * SR)
    buf[-fade:] *= np.linspace(1, 0, fade)
    return buf


def write_wav(path, buf):
    data = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def main():
    wav = OUT.rsplit(".", 1)[0] + ".wav"
    write_wav(wav, build_audio())
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{BW}x{BH}", "-r", str(FPS), "-i", "-",
           "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-tune", "animation",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = TOTAL * FPS
    for i in range(n):
        p.stdin.write(render_frame(i / FPS).tobytes())
        if i % (FPS * 10) == 0:
            print(f"  {i / FPS:5.1f}s / {TOTAL}s", flush=True)
    p.stdin.close()
    p.wait()
    os.remove(wav)
    print("done:", OUT)


if __name__ == "__main__":
    if os.environ.get("PREVIEW"):
        # PREVIEW="6.5,30,50" → dump still frames for checking
        for t in os.environ["PREVIEW"].split(","):
            Image.fromarray(render_frame(float(t))).save(os.path.join(os.environ.get("PREVIEW_DIR", "."), f"frame_{float(t):06.2f}.png"))
    else:
        main()
