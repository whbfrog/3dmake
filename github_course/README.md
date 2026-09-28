# GitHub 零基础入门（教学视频）

面向第一次使用 GitHub 的初学者，共 10 集。画面为动画幻灯片 + 仿真 GitHub 界面，女声解说（离线 Kokoro 中文 TTS），1080p，字幕内嵌。

| 集 | 标题 |
|---|---|
| 1 | GitHub 到底是什么？ |
| 2 | 注册账号与界面导览 |
| 3 | 创建第一个仓库 |
| 4 | 提交 Commit 与历史记录 |
| 5 | 把仓库搬到电脑上（Git / GitHub Desktop、clone） |
| 6 | 本地修改与同步（commit / push / pull） |
| 7 | 分支 Branch |
| 8 | Pull Request 协作与冲突 |
| 9 | 参与开源（Star、Fork、Issue） |
| 10 | 实用技巧与总结（Markdown、GitHub Pages、安全） |

成片在 `out/epNN.mp4`，同名 `.srt` 为字幕文件。

## 渲染

```
python3 engine/render.py episodes/ep01.py            # 完整视频
python3 engine/render.py episodes/ep01.py --preview  # 每个场景一张预览图
```

依赖：`kokoro-onnx`、`misaki[zh,en]`、`soundfile`、`playwright`、`imageio-ffmpeg`；
模型 `kokoro-v1.1-zh.onnx`、`voices-v1.1-zh.bin` 放在 `/opt/tts`（来自 thewh1teagle/kokoro-onnx 的 release `model-files-v1.1`）；
字体：思源黑体 SC、JetBrains Mono。

每集是 `episodes/` 下的一个 Python 文件：`SCENES` 列出场景 HTML 和分步讲稿，第 k 步会显示 `data-s="k"` 的元素并执行该步的 `js`（如 `hl()` 高亮、`cursor()` 鼠标演示）。
