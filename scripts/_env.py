# -*- coding: utf-8 -*-
"""跨平台环境探测：ffmpeg / 浏览器。供其他脚本 import。

优先顺序：显式参数 → 环境变量 → imageio_ffmpeg 包 → 常见安装路径 → PATH。
"""
import glob
import os
import shutil
import sys


def find_ffmpeg(explicit=None):
    if explicit:
        return explicit
    env = os.environ.get("FFMPEG_BIN")
    if env and os.path.exists(env):
        return env
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    patterns = [
        "~/AppData/Local/Programs/Python/Python*/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-*.exe",
        "C:/ffmpeg/bin/ffmpeg.exe",
        "C:/ProgramData/chocolatey/bin/ffmpeg.exe",
        "~/scoop/apps/ffmpeg/current/bin/ffmpeg.exe",
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg",
    ]
    hits = []
    for pat in patterns:
        hits.extend(glob.glob(os.path.expanduser(pat)))
    if hits:
        return sorted(hits)[-1]
    found = shutil.which("ffmpeg")
    if found:
        return found
    raise SystemExit(
        "找不到 ffmpeg。安装方式任选其一：\n"
        "  pip install imageio-ffmpeg\n"
        "  winget install Gyan.FFmpeg  /  brew install ffmpeg  /  apt install ffmpeg\n"
        "或用环境变量 FFMPEG_BIN 指定可执行文件路径。"
    )


def find_browser(explicit=None):
    """返回可用于 Remotion --browser-executable 的 Chromium 系浏览器路径。"""
    if explicit:
        return explicit
    env = os.environ.get("REMOTION_BROWSER")
    if env and os.path.exists(env):
        return env
    candidates = []
    if sys.platform.startswith("win"):
        candidates = [
            r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
            r"C:/Program Files/Microsoft/Edge/Application/msedge.exe",
            r"C:/Program Files/Google/Chrome/Application/chrome.exe",
            r"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            os.path.expanduser(r"~/AppData/Local/Google/Chrome/Application/chrome.exe"),
        ]
    elif sys.platform == "darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    else:
        for name in ("google-chrome", "google-chrome-stable", "chromium",
                     "chromium-browser", "microsoft-edge"):
            p = shutil.which(name)
            if p:
                candidates.append(p)
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def render_cmd(entry, out, browser=None, concurrency=6, crf=12):
    """生成可直接粘贴的 Remotion 渲染命令（自动带浏览器路径，路径含空格时加引号）。"""
    parts = ["npx", "remotion", "render", entry, out]
    if browser:
        parts.append(f'--browser-executable="{browser}"')
    parts += ["--gl=angle", f"--concurrency={concurrency}", f"--crf={crf}", "--codec=h264"]
    return " ".join(parts)
