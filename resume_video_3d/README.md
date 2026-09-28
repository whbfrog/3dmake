# 3D 线稿履历短片 · Career Story (3D line-art)

`career_story_3d.mp4`：1920×1080，30fps，时长 1分45秒。与 `../resume_video`（手绘版）内容、文字、配乐一致，
画面改为 three.js 渲染的 3D 线稿：每个物件先在纸面上画出正立面线稿，再像立体书一样从纸里翻起、跃出；
标题文字写在立起来的纸卡上。

- `scene.js`：分镜、3D 线稿模型（盒体/圆柱/拉伸体的轮廓边 + 纸色填充做消隐）与动画
- `render.mjs`：无头 Chromium（SwiftShader WebGL）逐帧渲染，配乐复用 `../resume_video/make_audio.py`（另加物件跃起的轻“呼”声）

重新生成：`npm i && pip install numpy imageio-ffmpeg && node render.mjs`（预览：`node render.mjs --preview 5,20,60`）
