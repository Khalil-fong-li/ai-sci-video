# -*- coding: utf-8 -*-
"""逐句配音 → 量时长 → 拼成整轨，产出 public/audio/timing.json + vo.wav

  python scripts/tts.py --project .
  python scripts/tts.py --project . --voice zh-CN-YunjianNeural --rate +8%
  python scripts/tts.py --project . --bgm music/bgm.mp3 --bgm-gain 0.16

依赖 edge-tts（python -m pip install edge-tts）。若当前解释器没有，
用 python scripts/env_check.py 查哪个 Python 装了，再用它跑本脚本。

产出的 vo.wav 已按片头/片尾留白对齐到视频第 0 帧，渲染后可直接 -c copy 混入。
"""
import argparse
import asyncio
import json
import os
import subprocess
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _env import find_ffmpeg  # noqa: E402

SR = 24000  # 采样率：edge-tts 原生 24k，整轨统一，避免重采样误差


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
    if r.returncode != 0:
        raise SystemExit("ffmpeg 失败：%s\n%s" % (" ".join(cmd[:6]), (r.stderr or "")[-600:]))
    return r


def wav_dur(path):
    with wave.open(path, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def silence(path, sec, ff):
    run([ff, "-v", "error", "-y", "-f", "lavfi", "-i",
         "anullsrc=r=%d:cl=mono" % SR, "-t", "%.3f" % max(sec, 0.001),
         "-c:a", "pcm_s16le", path])


async def synth(text, voice, rate, out_mp3, retries=3):
    import edge_tts
    last = None
    for i in range(retries):
        try:
            c = edge_tts.Communicate(text, voice, rate=rate)
            await c.save(out_mp3)
            if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 800:
                return
            last = "文件过小，可能没合成成功"
        except Exception as e:  # 网络抖动重试
            last = str(e)
            await asyncio.sleep(1.2 * (i + 1))
    raise SystemExit("配音失败（%s）：%s\n检查网络，或换 --voice" % (text[:12] + "…", last))


async def main_async(args):
    project = os.path.abspath(args.project)
    sb_path = args.file or os.path.join(project, "storyboard.json")
    if not os.path.exists(sb_path):
        raise SystemExit("找不到 %s" % sb_path)
    with open(sb_path, encoding="utf-8") as f:
        sb = json.load(f)

    voice = args.voice or sb.get("voice") or "zh-CN-YunxiNeural"
    rate = args.rate or sb.get("rate") or "+0%"
    intro_sec = float(sb.get("intro_sec", 2.2))
    end_sec = float(sb.get("end_sec", 3.0))
    scenes = sb.get("scenes") or []
    if not scenes:
        raise SystemExit("storyboard 里没有 scenes")

    ff = find_ffmpeg(args.ffmpeg)
    audio_dir = os.path.join(project, "public", "audio")
    os.makedirs(audio_dir, exist_ok=True)

    parts = []          # 依次排队的 wav 路径
    timing_scenes = []
    t = intro_sec
    silence(os.path.join(audio_dir, "_sil_intro.wav"), intro_sec, ff)
    parts.append(os.path.join(audio_dir, "_sil_intro.wav"))

    for i, s in enumerate(scenes, 1):
        sid = s.get("id") or "s%d" % i
        text = (s.get("narration") or "").strip()
        if not text:
            raise SystemExit("%s 没有 narration" % sid)
        mp3 = os.path.join(audio_dir, "vo_%s.mp3" % sid)
        wav = os.path.join(audio_dir, "vo_%s.wav" % sid)
        print("[%d/%d] %s  %s" % (i, len(scenes), sid, text[:24] + ("…" if len(text) > 24 else "")))
        if not (os.path.exists(wav) and os.path.getsize(wav) > 1000):
            await synth(text, voice, rate, mp3)
            run([ff, "-v", "error", "-y", "-i", mp3, "-ar", str(SR), "-ac", "1",
                 "-c:a", "pcm_s16le", wav])
        dur = wav_dur(wav)
        gap = float(s.get("gap", 0.3))
        timing_scenes.append({"id": sid, "audio": round(dur, 3), "gap": round(gap, 3),
                              "start": round(t, 3), "end": round(t + dur, 3)})
        parts.append(wav)
        t += dur
        if gap > 0:
            sp = os.path.join(audio_dir, "_sil_%s.wav" % sid)
            silence(sp, gap, ff)
            parts.append(sp)
            t += gap

    silence(os.path.join(audio_dir, "_sil_end.wav"), end_sec, ff)
    parts.append(os.path.join(audio_dir, "_sil_end.wav"))
    t += end_sec

    # 拼接
    lst = os.path.join(audio_dir, "_concat.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in parts:
            f.write("file '%s'\n" % p.replace("\\", "/").replace("'", "'\\''"))
    raw = os.path.join(audio_dir, "_vo_raw.wav")
    run([ff, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c:a", "pcm_s16le", "-ar", str(SR), "-ac", "1", raw])

    out = os.path.join(audio_dir, "vo.wav")
    if args.bgm:
        bgm = os.path.abspath(args.bgm)
        if not os.path.exists(bgm):
            raise SystemExit("找不到 BGM：%s" % bgm)
        run([ff, "-v", "error", "-y", "-i", raw, "-stream_loop", "-1", "-i", bgm,
             "-filter_complex",
             "[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[v];"
             "[1:a]volume=%.3f,afade=t=out:st=%.2f:d=1.2[m];"
             "[v][m]amix=inputs=2:duration=first:dropout_transition=0[a]"
             % (args.bgm_gain, max(t - 1.2, 0)),
             "-map", "[a]", "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", out])
    else:
        run([ff, "-v", "error", "-y", "-i", raw, "-af",
             "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "1",
             "-c:a", "pcm_s16le", out])

    timing = {"fps": sb.get("fps", 30), "voice": voice, "rate": rate,
              "intro_sec": intro_sec, "end_sec": end_sec,
              "total": round(t, 3), "scenes": timing_scenes}
    tp = os.path.join(audio_dir, "timing.json")
    with open(tp, "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)

    print("\n整轨：%s（%.2f 秒）" % (out, t))
    print("时间轴：%s" % tp)
    print("下一步：python scripts/timeline.py --project .")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".")
    ap.add_argument("--file", help="storyboard.json 路径")
    ap.add_argument("--voice", help="edge-tts 音色，默认读 storyboard.voice")
    ap.add_argument("--rate", help="语速，如 +8%% / -4%%")
    ap.add_argument("--bgm", help="背景音乐路径（循环铺底 + 结尾淡出）")
    ap.add_argument("--bgm-gain", type=float, default=0.16, help="BGM 音量系数，默认 0.16")
    ap.add_argument("--ffmpeg", help="ffmpeg 路径（默认自动探测）")
    args = ap.parse_args()
    try:
        import edge_tts  # noqa: F401
    except ImportError:
        raise SystemExit(
            "当前 Python 没有 edge-tts：%s\n"
            "装：python -m pip install edge-tts\n"
            "或用已装好的解释器跑：python scripts/env_check.py 会告诉你哪个 Python 有。" % sys.executable)
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
