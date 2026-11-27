# storyboard.json 字段表

只写这一份文件，就能决定内容、画面、画风。像素级版式由 Remotion 模板负责。

```json
{
  "title": "为什么飞机舷窗是圆的",
  "ratio": "9:16",
  "fps": 30,
  "style": "editorial",
  "voice": "zh-CN-YunxiNeural",
  "rate": "+4%",
  "caption_max": 14,
  "intro_sec": 2.2,
  "end_sec": 3.0,
  "themeOverride": {"accent": "#B8452D"},
  "hook": {"kicker": "30 秒科普", "line": "飞机舷窗，为什么是圆的？"},
  "scenes": [
    {
      "id": "s1",
      "narration": "坐飞机时，人人都摸过那片小小的舷窗。",
      "caption": "人人都摸过那片小舷窗",
      "visual": {"type": "keywords", "words": ["舷窗", "为什么是圆的"], "note": "看着理所当然"},
      "gap": 0.35
    }
  ],
  "end": {"line1": "一条小知识，一个大原理", "line2": "关注 · 科普"}
}
```

## 顶层字段

| 字段 | 必填 | 默认 | 说明 |
|---|---|---|---|
| `title` | ✔ | — | 项目标题，也做片头兜底文案 |
| `ratio` | | `9:16` | `9:16`(1080×1920) / `16:9`(1920×1080) / `1:1`(1080×1080) |
| `fps` | | `30` | 30 足够科普；60 只在大幅运动时需要 |
| `style` | | `editorial` | 画风，见 `styles.md` |
| `voice` | | `zh-CN-YunxiNeural` | edge-tts 音色 |
| `rate` | | `+0%` | 语速，科普常用 `+4%`～`+8%` |
| `caption_max` | | 竖屏 14 / 横屏 20 | 单条字幕上限字数 |
| `intro_sec` | | `2.2` | 片头时长（秒），片头不念口播 |
| `end_sec` | | `3.0` | 片尾时长（秒） |
| `themeOverride` | | `{}` | 只覆盖色板，键：`bg paper ink muted accent accent2 pop line`，值必须 `#RRGGBB` |
| `hook` | 建议 | — | 片头：`kicker` 小标签 + `line` 主标题 |
| `scenes` | ✔ | — | 正片场次，3–8 场 |
| `end` | 建议 | — | 片尾：`line1` 主句 + `line2` 小字 + 可选 `qr`（二维码图片，相对 `public/`） |

## 场次字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | 建议 | 唯一 id（`s1`…），`timing.json` 靠它对应；缺省按顺序 `s1..sn` |
| `narration` | ✔ | 口播原文，建议 15–40 字 |
| `caption` | ✔ | 屏幕字幕，比口播更短；会被 `timeline.py` 按标点再切成多条 |
| `visual` | ✔ | 画面，8 种类型见 `visuals.md` |
| `gap` | | 本场结束后留白秒数，默认 0.3；最后一场建议 0 |

## 兼容写法

老版本把图片写在顶层，仍然支持：

```json
{"id": "s1", "image": "images/s1.png", "motion": "push-in"}
```

等价于 `"visual": {"type": "image", "src": "images/s1.png", "motion": "push-in"}`。新工程建议统一用 `visual`。

## 字幕切分规则

`caption` → 按标点（`。！？；…，、,.!?;:`）切句 → 按 `caption_max` 装箱 → 按字数比例分配该句配音的时长。

所以：
- `caption` 写短句、多标点，字幕节奏会更细
- 不要写超长无标点的句子，会被硬切

## 时长是怎么定的

```
总时长 = intro_sec + Σ(该场配音真实时长 + gap) + end_sec
```

配音时长来自 `tts.py` 实测（`timing.json`），不是估算。改了文案就要重跑 `tts.py` 和 `timeline.py`。
