#!/usr/bin/env bash
# 一键同步同事段落成片：git pull → 按 tasks.json 补下 → 可选拼集
# 已并入 ./tgkw；本脚本保留为兼容入口。
# 推荐：./tgkw pull EP01 --concat
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT/tgkw" pull "$@"
