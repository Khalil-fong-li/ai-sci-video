# -*- coding: utf-8 -*-
"""成片校验 + 混音。

  python scripts/verify.py --video out/video.mp4 --mux out/final.mp4
  python scripts/verify.py --video out/video.mp4 --shots out/shots     # 每场抽一帧人工看

检查项：解码错误 / 时长与时间轴一致 / 分辨率 / 配音电平与异常静音 / 字幕长度 /
       每场画面素材是否齐（image 查文件，figure 查类型合法）。
退出码：0 全通过，1 有必须修的问题。
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _schema import VISUAL_TYPES, image_path  # noqa: E402
from _env import find_ffmpeg  # noqa: E402


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, errors="ignore")


def probe(ff, path):
    r = run([ff, "-i", path])
    out = r.stderr or ""
    d = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", out)
    dur = (int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3))) if d else None
    v = re.search(r"Stream #\d+:\d+.*?Video:.*?(\d{2,5})x(\d{2,5})", out, re.S)
    w, h = (int(v.group(1)), int(v.group(2))) if v else (None, None)
    fps = re.search(r"([\d.]+)\s*fps", out)
    has_audio = "Audio:" in out
    return {"dur": dur, "w": w, "h": h,
            "fps": float(fps.group(1)) if fps else None, "audio": has_audio}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".")
    ap.add_argument("--video", required=True)
    ap.add_argument("--timeline", help="默认 <project>/src/data/timeline.json")
    ap.add_argument("--audio", help="默认 <project>/public/audio/vo.wav")
    ap.add_argument("--mux", help="混音输出路径（-c:v copy，无损）")
    ap.add_argument("--shots", help="每场抽一帧的目录")
    ap.add_argument("--ffmpeg")
    args = ap.parse_args()

    project = os.path.abspath(args.project)
    tl_p = args.timeline or os.path.join(project, "src", "data", "timeline.json")
    au_p = args.audio or os.path.join(project, "public", "audio", "vo.wav")
    ff = find_ffmpeg(args.ffmpeg)

    problems, notes = [], []

    if not os.path.exists(tl_p):
        raise SystemExit("缺时间轴 %s" % tl_p)
    with open(tl_p, encoding="utf-8") as f:
        tl = json.load(f)
    expect = tl["total"] / float(tl["fps"])

    # 1. 解码
    r = run([ff, "-v", "error", "-i", args.video, "-f", "null", "-"])
    err = (r.stderr or "").strip()
    if err:
        problems.append("解码报错：\n" + "\n".join(err.splitlines()[:5]))
    else:
        notes.append("解码：零错误")

    # 2. 时长/分辨率
    info = probe(ff, args.video)
    if info["dur"] is None:
        problems.append("读不到时长，文件可能损坏")
    else:
        diff = abs(info["dur"] - expect)
        msg = "时长：%.2fs（时间轴 %.2fs，差 %.2fs）" % (info["dur"], expect, diff)
        (problems if diff > 0.35 else notes).append(msg)
    if info["w"] and (info["w"], info["h"]) != (tl["width"], tl["height"]):
        problems.append("分辨率 %dx%d 与时间轴 %dx%d 不一致"
                        % (info["w"], info["h"], tl["width"], tl["height"]))

    # 3. 音频
    if os.path.exists(au_p):
        if not info["audio"]:
            notes.append("视频暂无音轨（渲染默认静音，混音后才有）")
        r = run([ff, "-v", "info", "-i", au_p, "-af", "volumedetect", "-f", "null", "-"])
        m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", r.stderr or "")
        mx = re.search(r"max_volume:\s*(-?[\d.]+) dB", r.stderr or "")
        if m:
            mean = float(m.group(1))
            if mean < -34:
                problems.append("配音整体过轻（mean %.1f dB），检查配音是否为空" % mean)
            else:
                notes.append("配音电平：mean %.1f dB / max %s dB"
                             % (mean, mx.group(1) if mx else "?"))
        r = run([ff, "-v", "info", "-i", au_p, "-af", "silencedetect=n=-40dB:d=1.6", "-f", "null", "-"])
        sil = re.findall(r"silence_start:\s*([\d.]+)", r.stderr or "")
        if sil:
            notes.append("有声轨里 %.1f 秒以上的静音 %d 处：%s"
                         % (1.6, len(sil), ", ".join("%.1fs" % float(x) for x in sil[:6])))
    else:
        problems.append("缺配音文件 %s（先跑 tts.py）" % au_p)

    # 4. 字幕长度 + 每场画面
    long_lines = [(s["id"], c["text"]) for s in tl["scenes"] for c in s["chunks"] if len(c["text"]) > 24]
    if long_lines:
        problems.append("字幕超过 24 字（竖屏会挤）：" + "; ".join("%s「%s」" % x for x in long_lines[:4]))

    bad_types, missing_img, n_fig = [], [], 0
    for s in tl["scenes"]:
        v = s.get("visual") or {}
        t = v.get("type")
        if t not in VISUAL_TYPES:
            bad_types.append("%s:%s" % (s["id"], t))
        elif t == "image":
            if not os.path.exists(image_path(project, v.get("src", ""))):
                missing_img.append(v.get("src", "?"))
        else:
            n_fig += 1
    if bad_types:
        problems.append("画面类型非法：" + ", ".join(bad_types))
    if missing_img:
        problems.append("缺图片：" + ", ".join(missing_img))
    if not bad_types and not missing_img:
        notes.append("画面：%d 场（原生图形 %d 场，图片 %d 张齐）"
                     % (len(tl["scenes"]), n_fig, len(tl["scenes"]) - n_fig))

    # 5. 抽帧
    if args.shots:
        os.makedirs(args.shots, exist_ok=True)
        for s in tl["scenes"]:
            t = (s["from"] + s["dur"] * 0.45) / float(tl["fps"])
            out = os.path.join(args.shots, "%s.png" % s["id"])
            run([ff, "-v", "error", "-y", "-ss", "%.3f" % t, "-i", args.video,
                 "-frames:v", "1", "-vf", "scale=540:-1", out])
        notes.append("抽帧：%s（每场 1 张，人工看版式）" % os.path.abspath(args.shots))

    # 6. 混音：配音始终覆盖音轨
    if args.mux:
        r = run([ff, "-v", "error", "-y", "-i", args.video, "-i", au_p,
                 "-map", "0:v:0", "-map", "1:a:0",
                 "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                 "-movflags", "+faststart", args.mux])
        if r.returncode != 0:
            problems.append("混音失败：" + (r.stderr or "")[-300:])
        else:
            notes.append("混音输出：%s（%.1f MB）"
                         % (os.path.abspath(args.mux), os.path.getsize(args.mux) / 1e6))

    print("校验结果")
    for n in notes:
        print("  [OK] " + n)
    if problems:
        for p in problems:
            print("  [!!] " + p)
        return 1
    print("\n全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
