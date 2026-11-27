#!/usr/bin/env bash
# ai-sci-video 安装器（macOS / Linux）
# 用法: bash install.sh            自动装到所有检测到的智能体
#       bash install.sh --list     只探测
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$SRC/install.py" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "$SRC/install.py" "$@"
fi

echo "Python 未安装，回退到共享目录 ~/.agents/skills"
DEST="$HOME/.agents/skills/ai-sci-video"
mkdir -p "$DEST"
cp -R "$SRC"/. "$DEST"/
rm -f "$DEST/install.sh" "$DEST/install.bat" "$DEST/install.py"
echo "[OK] Installed to $DEST"
echo "重启对应智能体会话后生效。"
