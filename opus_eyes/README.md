# 用 Opus 5.5 看世界

90 秒短片，画面和配乐全部由代码生成：没有图片、没有采样、没有旁白。

- `scene.js` / `scene.html`：Canvas 2D 逐帧绘制（`renderAt(t)` 是纯函数）
- `make_music.py`：numpy 合成的配乐（96 BPM，D 大调，Bm–G–D–A，36 小节 = 90 秒）
- `render.mjs`：无头 Chromium 渲染每一帧，ffmpeg 编码并混入配乐

| 时间 | 段落 |
| --- | --- |
| 0–10s | 苏醒：光标敲出 "Hello, world."，切分成 token，散作星辰，标题 |
| 10–25s | 文字构成的世界：用汉字拼成的日出山水，并被逐一识别 |
| 25–40s | 意义空间：词语的三维分布，king − man + woman ≈ queen |
| 40–55s | 注意力：词与词互相注视，预测下一个词，多层网络随鼓点脉动 |
| 55–60s | 凝聚：一切旋入一点，白光 |
| 60–77.5s | 一个世界：点阵地球上，各种语言的问候彼此相连 |
| 77.5–90s | 看见：地球化作眼睛的虹膜，眨眼，"世界，是一场对话。" |

重新生成：`pip install numpy imageio-ffmpeg`，然后 `node render.mjs`（约 3 分钟）。
