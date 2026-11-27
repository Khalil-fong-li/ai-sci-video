# ai-sci-video

用 Remotion 渲染 AI 科普视频的技能包。给一个知识点，产出 30–90 秒可直接发布的 MP4：口播配音、字幕、片头片尾、进度条、运镜，全部自动。

**和"AI 生成视频"的区别**：画面不是模型随机的产物，而是**代码排出来的版式**——文字、数字、图表永远清晰、位置永远对齐、改一个字不用重新"生成"。

## 它能做什么

- 4 种画风：扁平贴纸、杂志信息图、深色科技、手账笔记（换一个字段就换整套视觉）
- 8 种画面：AI 配图、关键词、大数字、条形对比、流程步骤、左右对比、金句、空卡
- 自动配音（edge-tts，中英多音色）+ 逐句字幕（时间轴由真实音频时长决定）
- 竖屏 9:16 / 横屏 16:9 / 方图 1:1

## 快速开始

```bash
# 0. 依赖自检（缺什么会直接告诉你装什么）
python scripts/env_check.py

# 1. 建工程：复制模板
cp -r assets/remotion-template ~/my-video
cd ~/my-video
npm install          # 或在已有 Remotion 工程里做 node_modules 软链

# 2. 写分镜（生成一份可直接跑的模板）
python <skill>/scripts/storyboard.py --init --project .
python <skill>/scripts/storyboard.py --check --project .

# 3. 配音（时长由它决定，必须先生成）
python <skill>/scripts/tts.py --project .

# 4. 出时间轴
python <skill>/scripts/timeline.py --project .

# 5. 渲染
npx remotion render SciVideo out/video.mp4 \
  --browser-executable="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --gl=angle --concurrency=6 --crf=14 --codec=h264

# 6. 校验 + 混音 + 抽帧
python <skill>/scripts/verify.py --project . --video out/video.mp4 \
  --mux out/final.mp4 --shots out/shots
```

`out/final.mp4` 就是成品。`out/shots/` 里每场一张截图，交付前看一眼版式。

## 触发方式

对智能体说这些就会用上它：

> 做一个 30 秒科普视频，讲讲为什么飞机舷窗是圆的
> 把这篇文章做成 1 分钟的知识短视频，竖屏
> 用深色科技风出一条讲 AI 推理原理的视频

更精确的用法见 `PROMPT.md`（可直接粘贴的指令模板）。

## 依赖

| 依赖 | 用途 | 安装 |
|---|---|---|
| Node ≥18 + npm | Remotion | https://nodejs.org |
| Chrome 或 Edge | Remotion 渲染内核 | 系统已有 |
| ffmpeg | 音频拼接、混音、校验 | `pip install imageio-ffmpeg` |
| Python 3.9+ | 流水线脚本 | — |
| edge-tts | 配音 | `python -m pip install edge-tts` |

`scripts/env_check.py` 会逐项检查并给出安装命令。

## 目录

```
ai-sci-video/
├── SKILL.md                  # 技能主文档（工作流、规范、约束）
├── PROMPT.md                 # 可直接粘贴给智能体的指令模板
├── scripts/
│   ├── _env.py               # ffmpeg / 浏览器探测
│   ├── _schema.py            # storyboard 校验（画风、画面类型）
│   ├── env_check.py          # 环境自检
│   ├── storyboard.py         # 分镜模板 + 体检
│   ├── tts.py                # 配音 → timing.json + vo.wav
│   ├── timeline.py           # 合并成分镜时间轴 timeline.json
│   └── verify.py             # 成片校验 + 混音 + 抽帧
├── assets/remotion-template/ # Remotion 工程模板
│   └── src/
│       ├── style.ts          # 4 套画风预设
│       ├── Figure.tsx        # 6 种原生图形
│       ├── SceneCard.tsx     # 场景卡与转场
│       ├── Captions.tsx      # 4 种字幕样式
│       ├── Intro.tsx / EndCard.tsx / Chrome.tsx
│       └── Video.tsx         # 主合成（id: SciVideo）
└── references/
    ├── storyboard-schema.md  # 字段全表
    ├── visuals.md            # 8 种画面类型
    ├── styles.md             # 4 种画风详解
    ├── image-prompts.md      # AI 配图 prompt 模板
    └── pitfalls.md           # 踩坑清单
```

## 安装到其他智能体

```bash
python install.py            # 自动装到本机检测到的所有智能体技能目录
python install.py --list     # 只探测
python install.py --only codex
```

Windows 双击 `install.bat`，macOS/Linux 用 `bash install.sh`。

也可以直接从 GitHub 拷进技能目录：

```bash
git clone https://github.com/Khalil-fong-li/ai-sci-video.git \
  ~/.workbuddy/skills/ai-sci-video          # Codex 改成 ~/.codex/skills/
```

## 设计取舍

- **先声音后画面**：配音时长是唯一时钟，字幕、画面、进度条全部由它推导，所以永远不会"声画不同步"。
- **能画就不生图**：数字、流程、对比、关键词全部代码绘制——清晰、可改、零成本，也避免 AI 图里的乱码文字。
- **一份 JSON 两个维度**：`style`（画风）× `visual.type`（画面类型），组合出 32 种版式，不需要为每个视频写组件。
- **中文字体不打包**：直接用系统字体栈（雅黑/宋体/楷体/苹方），跨机器不掉字。
