# -*- coding: utf-8 -*-
"""storyboard.json 生成与体检。

  python scripts/storyboard.py --init            # 生成一份可改的模板（纯 figure，无需图片即可渲染）
  python scripts/storyboard.py --check           # 体检：字数、时长、画面类型、图片是否齐
  python scripts/storyboard.py --check --strict  # 有提示也返回非零
  python scripts/storyboard.py --types           # 列出可用的画风与画面类型
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _schema import (FIGURE_TYPES, RATIOS, STYLES, VISUAL_TYPES,  # noqa: E402
                     check_visual, image_path, norm_visual)

CHARS_PER_SEC = 4.6  # 中文口播舒适语速

TEMPLATE = {
    "title": "为什么飞机舷窗是圆的",
    "ratio": "9:16",
    "fps": 30,
    "style": "editorial",
    "voice": "zh-CN-YunxiNeural",
    "rate": "+4%",
    "hook": {"kicker": "30 秒科普", "line": "飞机舷窗，\n为什么是圆的？"},
    "scenes": [
        {
            "id": "s1",
            "narration": "坐飞机时，人人都摸过那片小小的舷窗。",
            "caption": "人人都摸过那片小舷窗",
            "visual": {"type": "keywords", "words": ["舷窗", "为什么是圆的"], "note": "看着理所当然"},
            "gap": 0.35,
        },
        {
            "id": "s2",
            "narration": "可最早的客机，窗户是方的，还出过大事。",
            "caption": "最早的窗户，是方的",
            "visual": {
                "type": "compare",
                "left": {"title": "方窗", "points": ["五十年代的喷气客机", "两次空中解体"]},
                "right": {"title": "圆窗", "points": ["应力沿弧线分散", "再没出过同类事故"]},
            },
            "gap": 0.35,
        },
        {
            "id": "s3",
            "narration": "机身像被反复弯折的铁丝，方角就是那道折痕。",
            "caption": "方角，就是那道折痕",
            "visual": {
                "type": "steps",
                "title": "裂纹是这么来的",
                "items": ["机身增压鼓胀", "方角处应力集中", "反复起降后开裂"],
            },
            "gap": 0.35,
        },
        {
            "id": "s4",
            "narration": "方角上的应力，比别处高出好几倍。",
            "caption": "应力高出好几倍",
            "visual": {"type": "bars", "unit": "倍", "items": [
                {"label": "圆窗边缘", "value": 1}, {"label": "方窗四角", "value": 3}]},
            "gap": 0.35,
        },
        {
            "id": "s5",
            "narration": "改成圆角，力顺着弧线走开，裂纹就起不来。",
            "caption": "弧线把力带走",
            "visual": {"type": "quote", "text": "圆不是好看，是把力散开的最短路径。"},
            "gap": 0.0,
        },
    ],
    "end": {"line1": "一条小知识，\n一个大原理", "line2": "关注 · 科普"},
}


def load(project, path=None):
    p = path or os.path.join(project, "storyboard.json")
    if not os.path.exists(p):
        raise SystemExit("找不到 %s，先跑 python scripts/storyboard.py --init" % p)
    with open(p, encoding="utf-8") as f:
        return json.load(f), p


def caption_max(sb):
    return int(sb.get("caption_max") or (14 if sb.get("ratio", "9:16") == "9:16" else 20))


def estimate(sb):
    intro = float(sb.get("intro_sec", 2.2))
    end = float(sb.get("end_sec", 3.0))
    total = intro + end
    for s in sb.get("scenes", []):
        total += len(s.get("narration", "")) / CHARS_PER_SEC + float(s.get("gap", 0.3))
    return total


def check(sb, project):
    warns, errs = [], []
    if not sb.get("title"):
        errs.append("缺 title")
    ratio = sb.get("ratio", "9:16")
    if ratio not in RATIOS:
        errs.append("ratio 必须是 %s 之一" % "/".join(RATIOS))
    style = sb.get("style", "editorial")
    if style not in STYLES:
        errs.append("style=%s 不支持（可用：%s）" % (style, "、".join(STYLES)))

    scenes = sb.get("scenes") or []
    if not (3 <= len(scenes) <= 8):
        warns.append("场景数 %d，建议 3–8 场（30–90 秒）" % len(scenes))

    cmax = caption_max(sb)
    rows, kinds = [], []
    for i, s in enumerate(scenes, 1):
        sid = s.get("id") or "s%d" % i
        nar = (s.get("narration") or "").strip()
        cap = (s.get("caption") or "").strip()
        if not nar:
            errs.append("%s 缺 narration" % sid)
        if not cap:
            errs.append("%s 缺 caption" % sid)
        if len(nar) > 60:
            warns.append("%s 口播 %d 字，超过 60 字一句容易赶，建议拆两场" % (sid, len(nar)))
        if len(cap) > cmax + 6:
            warns.append("%s 字幕 %d 字（建议 ≤%d），竖屏会挤成三行" % (sid, len(cap), cmax))
        try:
            v = norm_visual(s, sid)
        except SystemExit as e:
            errs.append(str(e))
            continue
        errs.extend(check_visual(v, sid))
        kinds.append(v["type"])
        if v["type"] == "image":
            if not os.path.exists(image_path(project, v["src"])):
                warns.append("%s 图片还没生成：public/%s" % (sid, v["src"]))
        elif v["type"] == "blank":
            warns.append("%s 是空卡，除非故意做停顿，建议换成 figure" % sid)
        rows.append((sid, v["type"], len(nar), round(len(nar) / CHARS_PER_SEC, 1), len(cap)))

    for a, b in zip(kinds, kinds[1:]):
        if a == b and a in FIGURE_TYPES:
            warns.append("连续两场都是 %s，画面会显得重复，建议穿插别的类型" % a)
    if kinds and all(k in FIGURE_TYPES for k in kinds):
        warns.append("全部是原生图形（无图），信息密度够但缺少实感；可加 1–2 场 image")

    if not (sb.get("hook") or {}).get("line"):
        warns.append("缺 hook.line，片头只能是空白卡")
    if not (sb.get("end") or {}).get("line1"):
        warns.append("缺 end.line1，片尾会是空白卡")

    print("场次  画面类型      口播字数  预计秒数  字幕字数")
    for r in rows:
        print("%-5s %-13s %8d %9.1f %9d" % r)
    print("\n画风：%s（%s）" % (style, STYLES.get(style, "?")))
    print("预计总时长：%.1f 秒（按 %.1f 字/秒估算，实际以配音为准）" % (estimate(sb), CHARS_PER_SEC))
    if warns:
        print("\n提示：")
        for w in warns:
            print("  - " + w)
    if errs:
        print("\n必须修：")
        for e in errs:
            print("  - " + e)
    return errs, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".")
    ap.add_argument("--file", help="storyboard.json 路径（默认 <project>/storyboard.json）")
    ap.add_argument("--init", action="store_true", help="写一份模板")
    ap.add_argument("--check", action="store_true", help="体检")
    ap.add_argument("--types", action="store_true", help="列出画风与画面类型")
    ap.add_argument("--strict", action="store_true", help="有提示也返回非零")
    ap.add_argument("--force", action="store_true", help="--init 时覆盖已存在文件")
    args = ap.parse_args()

    if args.types:
        print("画风（storyboard.style）：")
        for k, v in STYLES.items():
            print("  %-12s %s" % (k, v))
        print("\n画面类型（scene.visual.type）：")
        for k, v in VISUAL_TYPES.items():
            print("  %-12s %s" % (k, v))
        return 0

    project = os.path.abspath(args.project)
    target = args.file or os.path.join(project, "storyboard.json")

    if args.init:
        if os.path.exists(target) and not args.force:
            raise SystemExit("%s 已存在，加 --force 覆盖" % target)
        os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(TEMPLATE, f, ensure_ascii=False, indent=2)
        print("已生成模板：%s" % target)
        print("模板全部用原生图形，不需要图片就能直接渲染。")
        print("接着改 title / hook / 每场 narration 与 caption，再跑 --check")
        return 0

    sb, p = load(project, args.file)
    print("体检：%s\n" % p)
    errs, warns = check(sb, project)
    if errs:
        return 1
    if warns and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
