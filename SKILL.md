---
name: ai-sci-video
description: 用 Remotion 渲染 AI 科普视频（知识短视频/讲解视频/科普动画）。当用户要做科普视频、知识短视频、讲解视频、原理动画、数据解读视频，或要把一篇文章/一个概念做成 30-90 秒可发布的视频时使用。支持 4 种画风（扁平贴纸、杂志信息图、深色科技、手账笔记）与 8 种画面类型（AI 配图、关键词、大数字、条形对比、流程、左右对比、金句、空卡），自动配音、字幕、进度条，输出竖屏/横屏 MP4。
---

# AI 科普视频（Remotion）

把「一个知识点」变成 30–90 秒、可直接发布的科普视频：脚本 → 分镜 → 配音 → 渲染 → 校验。

**核心思路**：视频的骨架是**配音时长**，不是估算。先出配音，时间轴由声音决定，画面跟着时间轴长——所以永远不会出现「字幕快了」「画面多停了 3 秒」。画面不依赖素材：能画出来的（数字、流程、对比、关键词）全部用 Remotion 原生渲染，只有「需要实感」的地方才用 AI 配图。

## 什么时候用

- 用户要「科普视频 / 知识短视频 / 讲解视频 / 原理动画 / 数据解读视频」
- 用户给了一篇文章、一段资料、一个概念，要「做成 1 分钟视频」
- 用户已有口播稿，要配画面、字幕、片头片尾
- 需要批量出同款视频（换文案不换版式）

**不适用**：长视频剪辑/切片（用 `video-clip-cut`）、纯动效 Logo、真人出镜。

## 五步流程

```
1 选题与脚本  →  2 分镜 storyboard.json  →  3 配音 tts.py
                                              ↓
                5 校验交付  ←  4 渲染 render  ←  timeline.py
```

### 第 1 步：把知识点写成口播

先明确三件事，缺一件就先问用户：

| 要素 | 说明 | 默认 |
|---|---|---|
| 受众 | 决定画风与用词深度 | 泛知识人群 |
| 时长 | 30s / 60s / 90s | 30–45s |
| 画幅 | 竖屏（抖音/视频号）或横屏（B站/YouTube） | 9:16 |

口播写法（这决定成片质量，别跳过）：

1. **第一句必须是钩子**，用提问或反常识，2 秒内说完
2. **一句一个信息点**，每句 15–30 字，超过 40 字就拆
3. **说人话**：把「应力集中」说成「力都挤在一个角上」
4. **给一个可记住的锚点**：一个数字、一个比喻、一句结论
5. **最后一句收束**，一句话把原理说透（这句直接做片尾金句）

### 第 2 步：写分镜

```bash
python scripts/storyboard.py --init --project <工程目录>
python scripts/storyboard.py --check --project <工程目录>    # 体检
python scripts/storyboard.py --types                          # 查画风/画面类型
```

`storyboard.json` 每场一个 `visual`，8 种类型：

| type | 用途 | 关键参数 |
|---|---|---|
| `image` | 需要实感/场景感（实物、人物、场景） | `src` `motion` |
| `keywords` | 抛概念、拆关键词 | `words`(1–5) `note` |
| `stat` | 一个数字最有说服力时 | `value` `unit` `label` |
| `bars` | 比大小、排名 | `items[{label,value}]` `unit` |
| `steps` | 讲机制、讲因果链 | `items`(2–5) `title` |
| `compare` | 前后/正误/方案对比 | `left/right{title,points}` |
| `quote` | 金句、结论、反转 | `text` `by` |
| `blank` | 停顿、呼吸 | — |

**排布原则**：不要连续三场同一类型；`image` 与 figure 交替；全片至少一个 `stat` 或 `bars`（数字比形容词可信）。

### 第 3 步：配音

```bash
python scripts/tts.py --project <工程目录>
python scripts/tts.py --project <工程目录> --voice zh-CN-YunjianNeural --rate +8%
python scripts/tts.py --project <工程目录> --bgm music/bgm.mp3 --bgm-gain 0.12
```

产出 `public/audio/vo.wav`（已按片头/片尾留白对齐到第 0 帧）+ `timing.json`（每句真实时长）。

音色选择：

| 音色 | 听感 | 适合 |
|---|---|---|
| `zh-CN-YunxiNeural` | 年轻男声，轻快 | 泛科普、科技 |
| `zh-CN-YunjianNeural` | 沉稳男声 | 硬核原理、数据 |
| `zh-CN-XiaoxiaoNeural` | 温和女声 | 生活、健康、亲子 |
| `zh-CN-XiaoyiNeural` | 活泼女声 | 趣味冷知识 |

### 第 4 步：渲染

```bash
python scripts/timeline.py --project <工程目录>     # 生成 src/data/timeline.json
npx remotion render SciVideo out/video.mp4 \
  --browser-executable="<Chrome/Edge 路径>" --gl=angle --concurrency=6 --crf=14 --codec=h264
```

改画风只改 `storyboard.json` 的 `style` 再跑一次 `timeline.py` + 渲染，**内容和时间轴完全不变**。

### 第 5 步：校验与交付

```bash
python scripts/verify.py --project <工程目录> --video out/video.mp4 \
  --mux out/final.mp4 --shots out/shots
```

必须全绿才算完成：解码零错误、时长与时间轴差 <0.35s、分辨率一致、配音电平正常、字幕不超长、每场画面齐。`--shots` 会每场抽一帧，**必须人眼看一遍版式**再交付。

## 画风怎么选

| style | 观感 | 适合题材 |
|---|---|---|
| `flat-kids` | 贴纸、粗描边、高饱和 | 儿童科普、生活常识、趣味冷知识 |
| `editorial` | 米白纸感、衬线标题、细线 | 机构解读、政策说明、科研进展、严肃科普 |
| `dark-tech` | 深色、网格、发光强调 | AI、芯片、数据、前沿科技 |
| `paper` | 手账、胶带、马克笔 | 人文、生物、医学、心理 |

判断依据是**受众期待**，不是个人喜好：给机构/专业读者看，`editorial` 比卡通稳；给短视频信息流，`dark-tech` 和 `flat-kids` 更抓眼。

## 目录结构

```
<工程目录>/
  storyboard.json             # 你写的：内容 + 画面意图 + 画风
  public/images/s1.png        # AI 配图（image 场次）
  public/audio/vo.wav         # tts.py 产出
  public/audio/timing.json    # 每句真实时长
  src/data/timeline.json      # timeline.py 产出，渲染只读它
  out/final.mp4               # 交付物
```

模板目录在 `assets/remotion-template/`，新工程直接整体复制，再把 `node_modules` 指过去（`mklink /J` 或软链）就不必重装依赖。

## 硬性约束（踩过的坑）

1. **字幕对齐不要用计算，用数据**。字幕 `from/dur` 全部来自 `timing.json` 的真实配音时长，任何「按字数估算」都会漂。
2. **`OffthreadVideo` / 音频组件必须加 `muted`**，否则 Remotion 抽音会失败。
3. **中文不要用宋体做正文**（投影/手机看不清），标题可以；正文一律黑体或楷体。
4. **字幕竖屏 ≤14 字，横屏 ≤20 字**，超了必换行成三行。
5. **单场时长不要低于 2.5 秒**，否则观众来不及看；也不要超过 8 秒，否则画面呆滞（拆成两场）。
6. **渲染必带 `--browser-executable`**，否则 Remotion 自带的 headless 壳在部分 Windows 机器上起不来。
7. **改完 `storyboard.json` 必须重跑 `timeline.py`**，否则渲染的还是旧时间轴。
8. **数字必须有来源**。`stat` / `bars` 里的数字如果没有可靠出处，改成定性表述（「高出好几倍」）而不是编一个精确值。

## 参考文档

- `references/storyboard-schema.md` — storyboard 全字段
- `references/visuals.md` — 8 种画面类型的版式与参数
- `references/styles.md` — 4 种画风的色板、字体、动效
- `references/image-prompts.md` — AI 配图 prompt 模板（按画风）
- `references/pitfalls.md` — 踩坑清单与排查顺序
