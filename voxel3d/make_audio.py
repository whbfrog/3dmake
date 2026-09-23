#!/usr/bin/env python3
"""为 3D 版生成音轨：复用 2D 版的芯片音乐/音效合成器，对白打字音按 story.json 的台词生成。"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pixel_fight"))
import make_video as mv  # noqa: E402

story = json.load(open(os.path.join(HERE, "story.json"), encoding="utf-8"))
sc = {n: a for n, a, b in story["scenes"]}
mv.LINES = [(sc[s] + a, sc[s] + b, who, txt) for s, a, b, who, txt in story["lines"]]
mv.write_wav(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "audio.wav"), mv.build_audio())
