# -*- coding: utf-8 -*-
"""storyboard / timeline / verify 共用的 schema 常量与校验。

storyboard.json 只描述内容与画面意图，具体像素由 Remotion 模板决定。
"""
import os

RATIOS = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}

# 4 套视觉体系，与 src/style.ts 的 PRESETS 一一对应
STYLES = {
    "flat-kids": "扁平贴纸（活泼，适合儿童/生活科普）",
    "editorial": "杂志信息图（克制，适合机构解读/科研说明）",
    "dark-tech": "深色科技（屏幕感强，适合 AI/芯片/数据）",
    "paper": "手账笔记（温和，适合人文/生物/医学）",
}

MOTIONS = {"push-in", "pull-out", "pan-left", "pan-right", "tilt-up", "tilt-down", "still"}

# 画面类型：image 用图，其余全部由 Remotion 原生绘制，不需要素材
VISUAL_TYPES = {
    "image": "一张图（AI 生成或实拍）+ 运镜",
    "keywords": "1–5 个大词逐条砸下（words）",
    "stat": "一个大数字 + 单位 + 说明（value/unit/label）",
    "bars": "横向条形对比（items[{label,value}]，可给 max/unit）",
    "steps": "编号流程（items 2–5 条，可给 title）",
    "compare": "左右对比（left/right 各含 title+points）",
    "quote": "金句大字（text，可给 by）",
    "blank": "纯色过渡卡（慎用）",
}
FIGURE_TYPES = set(VISUAL_TYPES) - {"image", "blank"}


def _num(x, default=0.3):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def norm_visual(scene, where=""):
    """把 v1（顶层 image/motion）与 v2（visual 对象）统一成 v2。"""
    v = scene.get("visual")
    if isinstance(v, dict) and v.get("type"):
        out = dict(v)
    elif scene.get("image"):
        out = {"type": "image", "src": scene["image"], "motion": scene.get("motion", "push-in")}
        if scene.get("label"):
            out["label"] = scene["label"]
    else:
        raise SystemExit("%s 没有 visual，也没有 image（可用类型：%s）"
                         % (where or "某场", "、".join(VISUAL_TYPES)))

    t = out["type"]
    if t not in VISUAL_TYPES:
        raise SystemExit("%s visual.type=%s 不支持（可用：%s）"
                         % (where, t, "、".join(VISUAL_TYPES)))

    if t == "image":
        src = str(out.get("src") or "").replace("\\", "/")
        if src.startswith("public/"):
            src = src[len("public/"):]
        out["src"] = src.lstrip("/")
        out["motion"] = out.get("motion") if out.get("motion") in MOTIONS else "push-in"
        out["fit"] = "contain" if out.get("fit") == "contain" else "cover"
    elif t == "keywords":
        out["words"] = [str(w) for w in (out.get("words") or []) if str(w).strip()]
    elif t == "stat":
        out["value"] = str(out.get("value") or "")
        out["unit"] = str(out.get("unit") or "")
        out["label"] = str(out.get("label") or "")
    elif t == "bars":
        items = []
        for it in out.get("items") or []:
            if isinstance(it, dict) and "value" in it:
                items.append({"label": str(it.get("label") or ""), "value": _num(it.get("value"), 0)})
        out["items"] = items
        if out.get("max") is not None:
            out["max"] = _num(out.get("max"), 0) or None
        out["unit"] = str(out.get("unit") or "")
    elif t == "steps":
        out["items"] = [str(x) for x in (out.get("items") or []) if str(x).strip()]
        out["title"] = str(out.get("title") or "")
    elif t == "compare":
        for side in ("left", "right"):
            sd = out.get(side) or {}
            out[side] = {"title": str(sd.get("title") or ""),
                         "points": [str(x) for x in (sd.get("points") or []) if str(x).strip()]}
    elif t == "quote":
        out["text"] = str(out.get("text") or "")
        out["by"] = str(out.get("by") or "")
    return out


def check_visual(v, where=""):
    """返回错误列表（空 = 通过）。"""
    errs = []
    t = v.get("type")
    if t == "image":
        if not v.get("src"):
            errs.append("%s image 缺 src" % where)
    elif t == "keywords":
        n = len(v.get("words") or [])
        if n == 0:
            errs.append("%s keywords 缺 words" % where)
        elif n > 5:
            errs.append("%s keywords %d 个词，最多 5 个" % (where, n))
        elif any(len(w) > 12 for w in v["words"]):
            errs.append("%s keywords 有超过 12 字的词，画面会挤" % where)
    elif t == "stat":
        if not v.get("value"):
            errs.append("%s stat 缺 value" % where)
    elif t == "bars":
        n = len(v.get("items") or [])
        if n < 2:
            errs.append("%s bars 至少 2 条数据" % where)
        elif n > 6:
            errs.append("%s bars %d 条数据，最多 6 条" % (where, n))
    elif t == "steps":
        n = len(v.get("items") or [])
        if n < 2:
            errs.append("%s steps 至少 2 步" % where)
        elif n > 5:
            errs.append("%s steps %d 步，最多 5 步" % (where, n))
    elif t == "compare":
        for side, cn in (("left", "左"), ("right", "右")):
            sd = v.get(side) or {}
            if not sd.get("title"):
                errs.append("%s compare %s栏缺 title" % (where, cn))
            if not (1 <= len(sd.get("points") or []) <= 4):
                errs.append("%s compare %s栏要点需 1–4 条" % (where, cn))
    elif t == "quote":
        if not v.get("text"):
            errs.append("%s quote 缺 text" % where)
        elif len(v["text"]) > 60:
            errs.append("%s quote %d 字，建议 40 字内" % (where, len(v["text"])))
    return errs


def image_path(project, src):
    return os.path.join(project, "public", src.replace("/", os.sep))
