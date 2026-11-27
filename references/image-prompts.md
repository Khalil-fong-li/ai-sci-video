# AI 配图 prompt 模板

只有 `image` 场次需要配图。其余场次（数字、流程、对比、关键词、金句）全部由 Remotion 原生绘制，**不要用 AI 画**——AI 画图表一定出错。

## 铁律

1. **画面里不要出现文字**。中文尤其不行，AI 会画成鬼画符。所有文字交给字幕层。
2. **主体撑满画幅**。图片卡在竖屏上方占 73.5%、宽度满屏，按 `object-fit: cover` 裁切——两侧会被切掉一点，所以主体要占画面 60% 以上，别把主体画在大片空白中间（空处被放大后更空）。
3. **一张图一个主体**。多主体会让画面在 2 秒的停留里读不出来。
4. **同一支视频内保持同一套 prompt 前缀**，只改主体描述，风格才统一。
5. **比例按画幅**：竖屏用 2:3 或 9:16，横屏用 16:9，方图用 1:1。

## 通用结构

```
[画风前缀] + [主体描述] + [构图] + [光线/氛围] + [负面约束]
```

---

## flat-kids（扁平贴纸）

```
Flat vector cartoon illustration for a children's science video, thick black
outlines, bold flat colors, creamy off-white background, simple geometric
shapes, no gradients, playful and friendly, centered composition with generous
negative space. Subject: {主体}. No text, no letters, no watermark, no frames.
```

## editorial（杂志信息图）

```
Minimal editorial illustration for a magazine explainer, muted palette of warm
off-white, brick red and deep teal, thin precise line work, subtle paper grain,
flat infographic style with geometric abstraction, generous white space,
centered subject. Subject: {主体}. No text, no letters, no charts, no watermark.
```

## dark-tech（深色科技）

```
Dark futuristic tech illustration, near-black background, glowing cyan and
indigo accents, fine grid texture, volumetric light, isometric or schematic
feel, high contrast, cinematic depth, centered subject. Subject: {主体}.
No text, no letters, no UI labels, no watermark.
```

## paper（手账笔记）

```
Soft hand-drawn notebook illustration, warm cream paper with faint ruled lines,
gentle watercolor and colored-pencil texture, kai-style organic lines, muted
terracotta and olive tones, cozy and calm, centered subject with white space.
Subject: {主体}. No text, no letters, no handwriting, no watermark.
```

---

## 主体怎么写

把"要看到什么"写具体，而不是写名词。

| 差 | 好 |
|---|---|
| 飞机窗户 | a close-up of a single oval airplane window on a white fuselage, seen from inside the cabin |
| 应力集中 | a metal sheet bending at a sharp square corner, cracks radiating from the corner |
| 肠道菌群 | tiny friendly bacteria shapes floating inside a translucent human intestine, cross-section view |
| 芯片 | a silicon wafer with a glowing circuit pattern, macro shot, shallow depth of field |

## 常用构图词

- `centered composition with generous negative space` — 主体居中留白（最适合配字幕）
- `top-heavy composition, empty lower third` — 主体偏上，下方留空（竖屏专用）
- `flat lay, top-down view` — 俯视平铺
- `cross-section view` — 剖面（讲结构必备）
- `macro shot, shallow depth of field` — 微距浅景深
- `isometric view` — 等轴测（讲装置、系统）

## 常见失败与补救

| 现象 | 原因 | 改法 |
|---|---|---|
| 画面里出现乱码文字 | 模型自动补字 | 负面词加 `no text, no letters, no typography`，并把主体描述里的"标签""说明"删掉 |
| 主体偏下被字幕压住 | 构图未指定 | 加 `top-heavy composition, empty lower third` |
| 图片下半部一大片空白 | 主体画小了 | prompt 加 `subject fills the frame, tight crop, no large empty area` |
| 四张图风格不统一 | 前缀每次都不一样 | 固定前缀，只替换 `Subject:` 后面 |
| 出现明显的水印/边框 | 模型默认装饰 | 负面词加 `no watermark, no border, no frame` |
| 颜色跟画风打架 | 没有限定色板 | 前缀里写死 2–3 个色名（brick red, deep teal, off-white） |

## 落地

生成后放到 `public/images/s1.png`（文件名与 `visual.src` 一致），再跑：

```bash
python scripts/storyboard.py --check --project .   # 会提示哪张还缺
```

图片尺寸建议短边 ≥1080（竖屏 1080×1620 左右），PNG/JPG 都可。模板用 `object-fit: cover` 裁切，不需要精确比例。
