#!/bin/bash
# 每天 15:00 抓当日三榜；日志落在 data/（已 gitignore）。
set -euo pipefail

ROOT="/Users/lei/Movies/demo1/公众号/榜单"
LOG="$ROOT/data/fetch_daily.log"
PY="/usr/local/bin/python3"

cd "$ROOT"
mkdir -p "$ROOT/data"
{
  echo "== $(date '+%Y-%m-%d %H:%M:%S') fetch today =="
  "$PY" fetch.py today
  "$PY" fetch.py verify
  echo
} >> "$LOG" 2>&1
