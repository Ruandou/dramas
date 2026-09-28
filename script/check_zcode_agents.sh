#!/usr/bin/env bash
# 校验/修复 .qoder/agents 与 .zcode/agents 的硬链接同步。
# 背景：git 把硬链接存成两个独立 blob，编辑后只提交一边、或 checkout 换分支，
# 都会让两侧内容漂移且 inode 断开（ZCode 加载的是 .zcode 那份，漂移=按旧规则干活）。
# 用法：script/check_zcode_agents.sh        # 只报告
#       script/check_zcode_agents.sh --fix  # 以 .qoder 为准重建硬链接
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
fix="${1:-}"
drift=0
for src in .qoder/agents/*.md; do
  b=$(basename "$src")
  dst=".zcode/agents/$b"
  if [ ! -f "$dst" ]; then
    echo "MISSING  $b"; drift=1
  elif ! cmp -s "$src" "$dst"; then
    echo "CONTENT  $b  (两侧内容已漂移)"; drift=1
  elif [ "$(stat -f %i "$src")" != "$(stat -f %i "$dst")" ]; then
    echo "INODE    $b  (内容同但已断链，编辑一边不会同步)"; drift=1
  fi
done
if [ "$drift" -eq 0 ]; then
  echo "OK  $(ls .qoder/agents/*.md | wc -l | tr -d ' ') 个 agent 硬链接完好"
  exit 0
fi
if [ "$fix" = "--fix" ]; then
  for src in .qoder/agents/*.md; do
    b=$(basename "$src"); rm -f ".zcode/agents/$b"; ln "$src" ".zcode/agents/$b"
  done
  git add .zcode/agents 2>/dev/null || true
  echo "已按 .qoder/agents 为源重建硬链接（.zcode 侧改动已丢弃）"
  exit 0
fi
echo "运行 script/check_zcode_agents.sh --fix 修复"
exit 1
