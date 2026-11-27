# -*- coding: utf-8 -*-
"""环境自检：ffmpeg / Node / 浏览器 / 配音后端 / Python 依赖。

用法：
  python scripts/env_check.py           # 人类可读报告
  python scripts/env_check.py --json    # 机器可读（便于宿主程序解析）

退出码始终为 0（缺依赖不算失败，报告里给安装指引）。
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _env import find_browser, find_ffmpeg, render_cmd  # noqa: E402


def _run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           errors="ignore")
        return (r.stdout or r.stderr).strip()
    except Exception:
        return ""


def _python_candidates():
    """可能的 Python 解释器：当前、PATH、以及常见安装目录。"""
    seen, out = set(), []

    def add(p):
        if not p:
            return
        p = os.path.abspath(p)
        if p in seen or not os.path.exists(p):
            return
        seen.add(p)
        out.append(p)

    add(sys.executable)
    for name in ("python", "python3", "py"):
        add(shutil.which(name))
    for pat in (
        "~/AppData/Local/Programs/Python/Python*/python.exe",
        "C:/Python*/python.exe",
        "/usr/bin/python3*",
        "/opt/homebrew/bin/python3*",
        "/usr/local/bin/python3*",
    ):
        for p in sorted(glob.glob(os.path.expanduser(pat))):
            add(p)
    return out


def find_python_with(pkg):
    """返回第一个能 import 指定包的 Python 解释器路径。"""
    for py in _python_candidates():
        code = "import %s" % pkg
        try:
            r = subprocess.run([py, "-c", code], capture_output=True, timeout=20)
            if r.returncode == 0:
                return py
        except Exception:
            continue
    return None


def check():
    rep = {"ok": True, "hints": []}

    # ffmpeg
    try:
        ff = find_ffmpeg()
        rep["ffmpeg"] = ff
        rep["ffmpeg_version"] = _run([ff, "-version"]).splitlines()[0] if ff else None
    except SystemExit:
        rep["ffmpeg"] = None
        rep["hints"].append("缺 ffmpeg：pip install imageio-ffmpeg 或 winget install Gyan.FFmpeg")

    # node / npx（Windows 下 npx 是 npx.cmd，只能 which 不能直接执行）
    node = _run(["node", "--version"])
    rep["node"] = node or None
    if not node:
        rep["hints"].append("缺 Node.js（需 ≥18）：https://nodejs.org")
    rep["npx"] = shutil.which("npx") or shutil.which("npx.cmd")

    # 浏览器
    rep["browser"] = find_browser()
    if not rep["browser"]:
        rep["hints"].append("没找到 Chrome/Edge，Remotion 渲染需加 --browser-executable 指定")

    # 配音后端
    py_tts = find_python_with("edge_tts")
    rep["python_edge_tts"] = py_tts
    if not py_tts:
        rep["hints"].append("缺配音后端：python -m pip install edge-tts（系统 Python 装即可）")

    # 图像/数值依赖（可选，脚本里用得到）
    rep["python"] = sys.executable
    for pkg in ("numpy", "PIL"):
        rep["pkg_" + pkg] = find_python_with(pkg) is not None

    rep["render_cmd"] = render_cmd("SciVideo", "out/video.mp4",
                                   rep.get("browser"), concurrency=6, crf=14)
    if rep.get("python_edge_tts"):
        rep["tts_cmd"] = '"%s" scripts/tts.py --project .' % rep["python_edge_tts"]
    rep["ok"] = bool(rep.get("ffmpeg") and rep.get("node") and rep.get("browser"))
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rep = check()

    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return 0

    print("环境自检")
    print("  ffmpeg     :", rep.get("ffmpeg") or "缺失")
    print("  Node       :", rep.get("node") or "缺失")
    print("  npx        :", rep.get("npx") or "缺失")
    print("  浏览器     :", rep.get("browser") or "缺失")
    print("  配音(edge-tts) Python :", rep.get("python_edge_tts") or "缺失")
    print("\n渲染命令：")
    print("  " + rep["render_cmd"])
    if rep.get("tts_cmd"):
        print("配音命令：")
        print("  " + rep["tts_cmd"])
    if rep["hints"]:
        print("\n待处理：")
        for h in rep["hints"]:
            print("  - " + h)
    else:
        print("\n依赖齐全，可以直接开工。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
