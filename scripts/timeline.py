# -*- coding: utf-8 -*-
"""把 storyboard + 配音时长 合成为 Remotion 读的时间轴。

  python scripts/timeline.py --project .
  python scripts/timeline.py --project . --out src/data/timeline.json

输出（帧为单位，绝对位置）：片头 / 各场 / 片尾 / 每条字幕的 from+dur / 画风
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _schema import RATIOS, STYLES, norm_visual  # noqa: E402

PUNCT = "。！？；…，、,.!?;:："
PALETTE_KEYS = ("bg", "paper", "ink", "muted", "accent", "accent2", "pop", "line")


def split_caption(text, max_len=14):
    """按标点切句，再按长度装箱；超长片段硬切。"""
    text = (text or "").strip()
    if not text:
        return []
    segs, cur = [], ""
    for ch in text:
        cur += ch
        if ch in PUNCT:
            segs.append(cur)
            cur = ""
    if cur:
        segs.append(cur)

    chunks, buf = [], ""
    for s in segs:
        if len(s) > max_len:
            if buf:
                chunks.append(buf)
                buf = ""
            while len(s) > max_len:
                chunks.append(s[:max_len])
                s = s[max_len:]
            buf = s
        elif len(buf) + len(s) <= max_len:
            buf += s
        else:
            if buf:
                chunks.append(buf)
            buf = s
    if buf:
        chunks.append(buf)
    return [c.strip() for c in chunks if c.strip()]


def build(sb, timing, fps):
    ratio = sb.get("ratio", "9:16")
    if ratio not in RATIOS:
        raise SystemExit("ratio 只支持 %s" % "/".join(RATIOS))
    W, H = RATIOS[ratio]

    style = sb.get("style", "editorial")
    if style not in STYLES:
        raise SystemExit("style=%s 不支持（可用：%s）" % (style, "、".join(STYLES)))

    intro_sec = float(timing.get("intro_sec", 2.2))
    end_sec = float(timing.get("end_sec", 3.0))
    total_sec = float(timing["total"])
    total = int(round(total_sec * fps))
    intro = int(round(intro_sec * fps))
    end_dur = total - int(round((total_sec - end_sec) * fps))

    cmax = int(sb.get("caption_max") or (14 if ratio == "9:16" else 20))
    by_id = {s["id"]: s for s in timing.get("scenes", [])}
    scenes_out = []
    for i, s in enumerate(sb.get("scenes") or [], 1):
        sid = s.get("id") or "s%d" % i
        t = by_id.get(sid)
        if not t:
            raise SystemExit("timing.json 里没有 %s，先跑 tts.py" % sid)
        audio_f = int(round(t["audio"] * fps))
        from_f = int(round(t["start"] * fps))
        dur = int(round((t["audio"] + t["gap"]) * fps))

        chunks = split_caption(s.get("caption"), cmax)
        total_chars = sum(len(c) for c in chunks) or 1
        chunks_out, acc = [], 0
        for c in chunks:
            d = max(int(round(audio_f * len(c) / total_chars)), int(0.8 * fps))
            chunks_out.append({"from": from_f + acc, "dur": d, "text": c})
            acc += d
        if chunks_out:
            last = chunks_out[-1]
            last["dur"] = max(audio_f - (last["from"] - from_f), int(0.6 * fps))

        scenes_out.append({
            "id": sid, "index": i, "from": from_f, "dur": dur,
            "visual": norm_visual(s, sid),
            "chunks": chunks_out,
        })

    # 色板微调：v1 的 theme 也认，统一成 themeOverride
    override = {}
    for src in (sb.get("theme") or {}, sb.get("themeOverride") or {}):
        for k, v in src.items():
            if k in PALETTE_KEYS and isinstance(v, str) and v.startswith("#"):
                override[k] = v

    end = sb.get("end") or {}
    qr = str(end.get("qr") or "").replace("\\", "/")
    if qr.startswith("public/"):
        qr = qr[len("public/"):]

    return {
        "fps": fps, "width": W, "height": H, "total": total,
        "ratio": ratio, "style": style, "themeOverride": override,
        "intro": {"from": 0, "dur": intro,
                  "kicker": (sb.get("hook") or {}).get("kicker", "科普"),
                  "line": (sb.get("hook") or {}).get("line", sb.get("title", ""))},
        "scenes": scenes_out,
        "end": {"from": total - end_dur, "dur": end_dur,
                "line1": end.get("line1", ""), "line2": end.get("line2", ""),
                **({"qr": qr} if qr else {})},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".")
    ap.add_argument("--out", help="默认 <project>/src/data/timeline.json")
    args = ap.parse_args()

    project = os.path.abspath(args.project)
    sb_p = os.path.join(project, "storyboard.json")
    tg_p = os.path.join(project, "public", "audio", "timing.json")
    for p in (sb_p, tg_p):
        if not os.path.exists(p):
            raise SystemExit("缺 %s（先跑 storyboard.py / tts.py）" % p)

    with open(sb_p, encoding="utf-8") as f:
        sb = json.load(f)
    with open(tg_p, encoding="utf-8") as f:
        timing = json.load(f)

    fps = int(sb.get("fps", 30))
    tl = build(sb, timing, fps)

    out = args.out or os.path.join(project, "src", "data", "timeline.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(tl, f, ensure_ascii=False, indent=2)

    n_chunks = sum(len(s["chunks"]) for s in tl["scenes"])
    kinds = {}
    for s in tl["scenes"]:
        kinds[s["visual"]["type"]] = kinds.get(s["visual"]["type"], 0) + 1
    print("时间轴：%s" % out)
    print("  %dx%d @%dfps  共 %d 帧 = %.2f 秒  画风 %s"
          % (tl["width"], tl["height"], fps, tl["total"], tl["total"] / fps, tl["style"]))
    print("  片头 %d 帧 / 正片 %d 场（%s）/ 片尾 %d 帧 / 字幕 %d 条"
          % (tl["intro"]["dur"], len(tl["scenes"]),
             "、".join("%s×%d" % (k, v) for k, v in kinds.items()),
             tl["end"]["dur"], n_chunks))
    long_lines = [c["text"] for s in tl["scenes"] for c in s["chunks"] if len(c["text"]) > 22]
    if long_lines:
        print("  注意：有 %d 条字幕超过 22 字，竖屏可能换行过多" % len(long_lines))
    print("下一步：npx remotion render SciVideo out/video.mp4 ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
