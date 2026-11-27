# 踩坑清单

按"现象 → 原因 → 处理"查。

## 时序

**字幕整体早/晚几秒**
原因：`storyboard.json` 改了文案，但没重跑 `tts.py`，`timing.json` 还是旧的。
处理：`tts.py` → `timeline.py` → 重新渲染。三步缺一不可。

**字幕逐条越走越偏**
原因：字幕时长按字数比例分配，但口播里有长停顿（逗号处换气）。
处理：把 `caption` 拆得更碎（多打标点），或直接接纳 0.3–0.5 秒的偏差——这是句内均分的固有限制。

**最后一句字幕没显示完就切片尾**
原因：`gap` 给了负值或 0 且配音末尾被 VAD 裁短。
处理：最后一场 `gap` 设 0，并把 `end_sec` 提到 3.2。

**片头空白没声音**
正常。片头 `intro_sec` 就是静音钩子卡，配音从正片开始。

## 渲染

**`Failed to launch browser` / 渲染卡在 0%**
原因：Remotion 自带的 headless 壳起不来。
处理：必带 `--browser-executable="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"`（Chrome 同理）。

**`Cannot find module './data/timeline.json'`**
原因：还没生成时间轴就跑了 `tsc` 或渲染。
处理：先 `python scripts/timeline.py --project .`。

**渲染到某一帧反复失败（其他帧正常）**
原因：图片/视频资源在该帧加载超时。
处理：把该帧前后拆段渲染再 `-c copy` 拼接：
```bash
npx remotion render SciVideo out/a.mp4 --frames=0-699 ...
npx remotion render SciVideo out/b.mp4 --frames=700-837 ...
printf "file 'a.mp4'\nfile 'b.mp4'\n" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy out/video.mp4
```

**成片没有声音**
正常。Remotion 渲染默认静音，配音靠 `verify.py --mux` 混入。

**改了 `style` 但画面没变**
原因：`timeline.json` 里存的是上次的 style。
处理：重跑 `timeline.py`。

**分辨率还是老的**
原因：改 `ratio` 后没重跑 `timeline.py`；Composition 的宽高读的是 timeline。
处理：重跑 `timeline.py` 后**必须重新渲染**（不是混音）。

## 字体与文字

**中文显示成方框/豆腐块**
原因：字体栈里一个中文字体都没命中（多见于 Linux 容器）。
处理：装 `fonts-noto-cjk`，或在 `style.ts` 的字体栈最前面加已安装字体名。

**标题不够粗**
原因：`Microsoft YaHei` 没有 900 字重，浏览器用合成加粗，视觉上偏细。
处理：`editorial` / `paper` 本来就用 700；要更粗就换 `Noto Sans SC`（有 900）。

**字幕换行成三行**
原因：单条超过 `caption_max`。
处理：把 `caption` 改短，或 `storyboard.py --check` 看哪几条超了。

**数字没滚动**
原因：`value` 里没有阿拉伯数字（如写成"三倍"）。
处理：写成 `"3"` + `unit: "倍"`。

## 音频

**配音整体很轻**
原因：edge-tts 输出音量偏低且 `loudnorm` 单遍处理。
处理：`verify.py` 会报 mean < -34dB；确认 `vo.wav` 不是空文件。必要时 `--bgm-gain` 调低，让 `loudnorm` 有更多余量。

**BGM 盖过人声**
处理：`--bgm-gain 0.10`～`0.14`（默认 0.16 偏大）。

**`ModuleNotFoundError: edge_tts`**
原因：装在了另一个 Python 里。
处理：`python scripts/env_check.py` 会打印哪个解释器有，用那个跑 `tts.py`。

## 画面

**图片主体被裁掉**
原因：`cover` 会居中裁切，主体不在中心就被切。
处理：改 prompt 让主体居中（`centered composition`），或临时设 `"fit": "contain"` 看全图。

**竖屏图注压到字幕**
原因：图注在图片正下方，字幕在底部；图太高时两者接近。
处理：图注只在需要时加，且内容要短（≤14 字）。

**`compare` 两栏高度不一致很难看**
原因：左右要点数量差太多。
处理：两栏要点数保持相等或差 1。

**深色风格在手机上看不清**
原因：`dark-tech` 对比度在强光下衰减。
处理：字幕压到 ≤12 字、`themeOverride` 把 `accent` 调亮（如 `#4BF0D0`）。

## 工程

**`npx remotion` 提示找不到命令**
原因：`node_modules` 没装。
处理：工程内 `npm install`；或从已有工程做 junction（Windows：`mklink /J node_modules <目标>`）。

**装到别的智能体后脚本跑不起来**
原因：`install.py` 会排除 `node_modules`（正确，太大了），每个新工程需自己装依赖或软链。
处理：见 `install.py` 输出里的依赖自检提示。
