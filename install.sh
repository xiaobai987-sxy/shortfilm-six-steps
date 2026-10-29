#!/usr/bin/env bash
# 短片六工序 · 安装脚本
# 用法：./install.sh          装到所有已存在的 skill 目录
#       ./install.sh --link   用软链接（改源文件立即生效）
#       ./install.sh --dry    只看会做什么

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/skills"
NAMES=(juben dingxi jingtou sucai shengcheng jianji)
MODE="copy"; DRY=0
for a in "$@"; do
  case "$a" in
    --link) MODE="link";;
    --dry)  DRY=1;;
    -h|--help) sed -n '2,6p' "$0"; exit 0;;
  esac
done

# 候选目录（存在才装）
CANDS=(
  "$HOME/.agents/skills"          # DeepSeek Harness / 通用 agents
  "$HOME/.claude/skills"          # Claude Code
  "$HOME/.codex/skills"           # Codex
  "$HOME/.cursor/skills"          # Cursor
  "$HOME/.config/agents/skills"
)

found=0
for root in "${CANDS[@]}"; do
  [ -d "$root" ] || continue
  found=1
  echo "→ $root"
  for n in "${NAMES[@]}"; do
    dst="$root/$n"
    if [ -e "$dst" ]; then
      if [ "$DRY" = 1 ]; then echo "   [dry] 会备份 $n 并覆盖"; continue; fi
      bak="$dst.bak.$(date +%Y%m%d%H%M%S)"
      mv "$dst" "$bak"; echo "   备份旧版 → $(basename "$bak")"
    fi
    [ "$DRY" = 1 ] && { echo "   [dry] 会安装 $n"; continue; }
    if [ "$MODE" = "link" ]; then
      ln -s "$SRC/$n" "$dst"
    else
      mkdir -p "$dst"
      cp -R "$SRC/$n/." "$dst/"
    fi
    echo "   装好 $n"
  done
done

if [ "$found" = 0 ]; then
  # 一个都没有：建最常见的两个
  mkdir -p "$HOME/.agents/skills" "$HOME/.claude/skills"
  echo "没找到现成的 skill 目录，已新建："
  echo "  ~/.agents/skills"
  echo "  ~/.claude/skills"
  for root in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
    for n in "${NAMES[@]}"; do
      cp -R "$SRC/$n" "$root/"
    done
  done
  echo "六个都装好了。"
  echo
  echo "如果你的 agent 用别的目录，手动把 skills/ 里六个文件夹拷过去。"
fi

[ "$DRY" = 1 ] || echo
[ "$DRY" = 1 ] || echo "完成。开新会话验证：说「做个关于 X 的短片」，看是否触发 juben。"
