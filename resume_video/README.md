# 手绘线条履历短片 · Career Story

`career_story.mp4`：1920×1080，30fps，时长 1分45秒。素描线条逐笔从纸面“长”出来，按时间轴讲述三个阶段：
工程建设（1995.07—2010.10）→ 运营管理（2010.10—2021.09）→ 安全管理（2021.09—至今）。

- `scene.js`：全部分镜与线稿（rough.js 手绘笔触），修改文字/岗位就在顶部的 `SCENES` 列表里
- `make_audio.py`：用 numpy 合成的钢琴 + 弦乐背景音乐（D 大调，随阶段逐层加厚）及铅笔沙沙声
- `render.mjs`：无头 Chromium 逐帧渲染并用 ffmpeg 合成

重新生成：`npm i && pip install numpy imageio-ffmpeg && node render.mjs`（预览：`node render.mjs --preview 5,20,60`）

字体：中文行书 Zhi Mang Xing（智莽行），英文手写 Caveat，均为 SIL Open Font License（见 `fonts/OFL.txt`）。
