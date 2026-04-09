#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按 task_id 批量查询即梦异步结果并下载 MP4 到 video/generated/。
依赖：与 MCP 相同的环境变量 VOLC_ACCESS_KEY、VOLC_SECRET_KEY；pip install 'volcengine>=1.0.130,<2'。

用法（仓库根 demo1）：
  cp video/automation/ep01_task_ids.example.json video/automation/ep01_task_ids.json
  # 编辑 ep01_task_ids.json，把每条 task_id 从即梦创作记录里粘进去
  export VOLC_ACCESS_KEY=... VOLC_SECRET_KEY=...
  python3 video/automation/download_jimeng_from_tasks.py
  python3 video/automation/download_jimeng_from_tasks.py --json video/automation/ep01_task_ids.json --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def submit_script() -> Path:
    return repo_root() / "mcp" / "volc-jimeng" / "scripts" / "volc_visual_submit.py"


def query_task(py: Path, script: Path, req_key: str, version: str, task_id: str) -> object:
    payload = {
        "action": "CVSync2AsyncGetResult",
        "version": version,
        "body": {"req_key": req_key, "task_id": task_id},
    }
    r = subprocess.run(
        [str(py), str(script)],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
        cwd=str(script.parent),
        env={**os.environ},
    )
    out = r.stdout.decode("utf-8", errors="replace").strip()
    err = r.stderr.decode("utf-8", errors="replace").strip()
    if r.returncode != 0:
        raise RuntimeError(err or out or f"exit {r.returncode}")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return out


def _walk_find_video_url(obj: object, depth: int = 0) -> str | None:
    if depth > 20:
        return None
    if isinstance(obj, str):
        s = obj.strip()
        if s.startswith("http") and (".mp4" in s.lower() or "/video" in s.lower() or "tos-" in s):
            return s
        try:
            return _walk_find_video_url(json.loads(s), depth + 1)
        except (json.JSONDecodeError, TypeError):
            return None
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).lower()
            if lk in ("video_url", "url", "videourl") and isinstance(v, str) and v.startswith("http"):
                return v
            hit = _walk_find_video_url(v, depth + 1)
            if hit:
                return hit
    if isinstance(obj, list):
        for x in obj:
            hit = _walk_find_video_url(x, depth + 1)
            if hit:
                return hit
    return None


def safe_name(filename: str) -> str:
    base = filename.strip().replace(".mp4", "")
    base = re.sub(r'[/\\:*?"<>|]', "_", base)
    return base + ".mp4" if base else "jimeng.mp4"


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "demo1-download_jimeng/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--json",
        default="video/automation/ep01_task_ids.json",
        help="任务列表 JSON（相对仓库根或绝对路径）",
    )
    ap.add_argument("--dry-run", action="store_true", help="只打印查询结果，不下载")
    args = ap.parse_args()
    root = repo_root()
    cfg_path = Path(args.json)
    if not cfg_path.is_file():
        cfg_path = root / args.json
    if not cfg_path.is_file():
        print(
            f"找不到配置: {cfg_path}\n请先: cp video/automation/ep01_task_ids.example.json video/automation/ep01_task_ids.json\n再在即梦创作记录里填入各镜 task_id。",
            file=sys.stderr,
        )
        sys.exit(1)

    raw_cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    req_key = raw_cfg.get("req_key") or "jimeng_ti2v_v30_pro"
    version = raw_cfg.get("version") or "2022-08-31"
    clips = raw_cfg.get("clips") or []

    script = submit_script()
    if not script.is_file():
        print(f"缺少: {script}", file=sys.stderr)
        sys.exit(1)

    py = Path(sys.executable)
    out_dir = root / "video" / "generated"
    ok, skip, fail = 0, 0, 0

    for item in clips:
        if isinstance(item, str):
            continue
        tid = (item.get("task_id") or "").strip()
        fn = item.get("filename") or "jimeng"
        if not tid:
            print(f"[跳过] 无 task_id: {fn}")
            skip += 1
            continue
        try:
            res = query_task(py, script, req_key, version, tid)
        except Exception as e:
            print(f"[失败] {fn} query: {e}", file=sys.stderr)
            fail += 1
            continue

        if args.dry_run:
            print(json.dumps({"file": fn, "task_id": tid, "response": res}, ensure_ascii=False, indent=2))
            continue

        url = _walk_find_video_url(res)
        if not url:
            print(f"[失败] {fn}: 响应里未找到视频 URL\n{json.dumps(res, ensure_ascii=False)[:800]}", file=sys.stderr)
            fail += 1
            continue

        dest = out_dir / safe_name(fn)
        try:
            download(url, dest)
            print(f"[OK] {dest.name} ({dest.stat().st_size // 1024} KiB)")
            ok += 1
        except Exception as e:
            print(f"[失败] {fn} 下载: {e}", file=sys.stderr)
            fail += 1

    if not args.dry_run:
        print(json.dumps({"downloaded": ok, "skipped_no_id": skip, "failed": fail}, indent=2))


if __name__ == "__main__":
    main()
