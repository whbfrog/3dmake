# GitHub 零基础入门（教学视频）

面向第一次使用 GitHub 的初学者，共 10 集。画面为动画幻灯片 + 仿真 GitHub 界面，女声解说（离线 ZipVoice TTS，参考音色由 Kokoro 合成，不克隆真人声音；每句配音经语音识别核对，不准确会自动重新生成），1080p，字幕内嵌。

| 集 | 标题 | 时长 |
|---|---|---|
| 1 | GitHub 到底是什么？ | 4:31 |
| 2 | 注册账号与界面导览 | 4:56 |
| 3 | 创建第一个仓库 | 4:15 |
| 4 | 提交 Commit 与历史记录 | 4:02 |
| 5 | 把仓库搬到电脑上（GitHub Desktop、clone） | 4:32 |
| 6 | 本地修改与同步（commit / push / pull） | 3:53 |
| 7 | 分支 Branch | 3:57 |
| 8 | Pull Request 协作与冲突 | 4:18 |
| 9 | 参与开源（Star、Fork、Issue） | 4:31 |
| 10 | 实用技巧与总结（Markdown、GitHub Pages、安全） | 3:40 |

合计约 42 分钟。

成片在 `out/epNN.mp4`，同名 `.srt` 为字幕文件。

## 渲染

```
python3 engine/render.py episodes/ep01.py            # 完整视频
python3 engine/render.py episodes/ep01.py --preview  # 每个场景一张预览图
```

依赖：`sherpa-onnx`、`kokoro-onnx`、`misaki[zh,en]`、`soundfile`、`scipy`、`playwright`、`imageio-ffmpeg`；
模型放在 `/opt/tts`：`kokoro-v1.1-zh.onnx`、`voices-v1.1-zh.bin`（thewh1teagle/kokoro-onnx release `model-files-v1.1`），
`sherpa-onnx-zipvoice-distill-int8-zh-en-emilia/`、`vocos_24khz.onnx`、`sherpa-onnx-paraformer-zh-small-2024-03-09/`（k2-fsa/sherpa-onnx releases）；
字体：思源黑体 SC、JetBrains Mono。

多音字等读音问题在 `engine/render.py` 的 `SPOKEN_FIX` 里用同音字替换（只影响配音，不影响字幕）。

每集是 `episodes/` 下的一个 Python 文件：`SCENES` 列出场景 HTML 和分步讲稿，第 k 步会显示 `data-s="k"` 的元素并执行该步的 `js`（如 `hl()` 高亮、`cursor()` 鼠标演示）。
