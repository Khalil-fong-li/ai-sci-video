把 image 场次的配图放这里，文件名与 storyboard.json 里 visual.src 一致（如 s1.png）。

要求：
- 尺寸比例与成片一致（竖屏 2:3 或 9:16，横屏 3:2 / 16:9），短边至少 1080px
- 画面里不要出现文字/字母/数字——AI 画出来的字一定是乱码，所有文字交给字幕层
- 同一支视频的所有配图沿用同一段风格前缀，保证画风统一（见 references/image-prompts.md）
- 主体放中上部：竖屏时下方约 40% 会被字幕和留白占用

只有 visual.type = "image" 的场次需要图。keywords / stat / bars / steps / compare / quote 六种画面由
Remotion 原生绘制，不需要任何素材。
