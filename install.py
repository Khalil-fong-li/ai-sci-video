# -*- coding: utf-8 -*-
"""ai-sci-video 一键安装（多智能体适配）。

做三件事：
  1. 扫描本机已存在的智能体技能目录，把技能装进每一个（WorkBuddy / Codex / Claude Code /
     Cursor / Gemini / OpenCode / CodeBuddy / Copilot / Trae / Kiro / Qoder / Kimi / Qwen …）；
  2. 若一个都没找到，就装到共享目录 ~/.agents/skills（Codex、OpenCode、Gemini、Zed、Copilot 都读）；
  3. 打印"谁装上了、要重启会话才生效"。

用法:
  python install.py                # 自动安装到所有检测到的智能体
  python install.py --list         # 只探测，不安装
  python install.py --project .    # 额外装到当前项目的 .agents/skills（团队共享）
  python install.py --only codex   # 只装指定目标（可多次）
"""
import argparse
import os
import shutil
import sys

NAME = "ai-sci-video"
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")

# (显示名, 相对 home 的目录, 说明)  —— 顺序即优先级
AGENTS = [
    ("WorkBuddy", ".workbuddy/skills", ""),
    ("Codex", ".codex/skills", "CLI / IDE 扩展"),
    ("Claude Code", ".claude/skills", ""),
    ("CodeBuddy", ".codebuddy/skills", ""),
    ("Cursor", ".cursor/skills", ""),
    ("Gemini CLI", ".gemini/skills", ""),
    ("Antigravity", ".gemini/config/skills", ""),
    ("OpenCode", ".config/opencode/skills", ""),
    ("GitHub Copilot", ".copilot/skills", ""),
    ("Trae", ".trae/skills", ""),
    ("Kiro", ".kiro/skills", ""),
    ("Qoder", ".qoder/skills", ""),
    ("通义灵码", ".lingma/skills", ""),
    ("Kimi Code", ".kimi-code/skills", ""),
    ("Qwen Code", ".qwen/skills", ""),
    ("Warp", ".warp/skills", ""),
    ("Amp", ".config/amp/skills", ""),
    ("Goose", ".config/goose/skills", ""),
    ("Crush", ".config/crush/skills", ""),
    ("Droid", ".factory/skills", ""),
    ("Cline", ".cline/skills", ""),
    ("Mistral Vibe", ".vibe/skills", ""),
]
SHARED = ("共享目录 .agents", ".agents/skills", "Codex / OpenCode / Gemini / Zed / Copilot 共读")


def copy_skill(dest_parent, overwrite=True):
    dest = os.path.join(dest_parent, NAME)
    if os.path.exists(dest):
        if not overwrite:
            return dest, False
        shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(dest_parent, exist_ok=True)
    shutil.copytree(SKILL_DIR, dest, ignore=shutil.ignore_patterns(
        "install.py", "install.bat", "install.sh", "__pycache__", "*.pyc",
        ".git", ".github", "node_modules", ".DS_Store", "Thumbs.db"))
    return dest, True


def detect():
    found = []
    for label, rel, note in AGENTS:
        parent = os.path.join(HOME, rel.replace("/", os.sep))
        if os.path.isdir(parent):
            found.append((label, parent, note))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="只探测不安装")
    ap.add_argument("--project", help="额外安装到该项目的 .agents/skills")
    ap.add_argument("--only", action="append", default=[], help="只装指定名（workbuddy/codex/...）")
    ap.add_argument("--no-shared", action="store_true", help="不装到 ~/.agents/skills")
    args = ap.parse_args()

    targets = detect()
    if args.only:
        keys = {k.lower().replace("-", "").replace(" ", "") for k in args.only}
        targets = [t for t in targets
                   if t[0].lower().replace("-", "").replace(" ", "") in keys]

    if args.list:
        print("检测到的智能体技能目录：")
        for label, parent, note in targets:
            mark = "已装" if os.path.isdir(os.path.join(parent, NAME)) else "未装"
            print("  [%s] %-14s %s %s" % (mark, label, parent, note))
        if not targets:
            print("  （无）将安装到共享目录 ~/.agents/skills")
        return 0

    if not targets and not args.no_shared:
        targets = [SHARED]

    installed = []
    for label, parent, note in targets:
        try:
            dest, _ = copy_skill(parent)
            installed.append((label, dest))
        except Exception as e:
            print("[WARN] %s 安装失败：%s" % (label, e))

    if args.project:
        proj = os.path.join(os.path.abspath(args.project), ".agents", "skills")
        dest, _ = copy_skill(proj)
        installed.append(("项目共享 " + os.path.basename(args.project), dest))

    print("\n已安装 %d 处：" % len(installed))
    for label, dest in installed:
        print("  - %-14s %s" % (label, dest))
    print("\n技能名：%s（说“做个科普视频 / 知识短视频 / 讲解视频”即触发）" % NAME)
    print("重启对应智能体的会话后生效。")
    if installed:
        print("依赖自检（缺 ffmpeg / Node / 浏览器会提示）：")
        print('  python "%s"' % os.path.join(installed[0][1], "scripts", "env_check.py"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
