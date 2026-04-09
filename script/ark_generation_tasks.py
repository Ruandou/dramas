#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火山方舟：视频生成任务列表（最近约 7 天）查询与批量下载。

接口：
  GET https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks

鉴权：Authorization: Bearer <API Key>
环境变量：ARK_API_KEY 或 VOLC_ARK_API_KEY
可选：ARK_BASE_URL（默认北京域名）

注意：content.video_url 有效期约 24 小时；--ep01-names 按 created_at 升序取前 14 条，若同期有其他任务可能错位。

用法（仓库根）：
  export ARK_API_KEY=你的方舟APIKey
  python3 video/automation/ark_generation_tasks.py list --status succeeded
  python3 video/automation/ark_generation_tasks.py list --json
  python3 video/automation/ark_generation_tasks.py download --out-dir video/generated
  python3 video/automation/ark_generation_tasks.py download --ep01-names
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_BASE = "https://ark.cn-beijing.volces.com"
TASKS_PATH = "/api/v3/contents/generations/tasks"

EP01_FILENAMES = [
    "第01镜_场1-1A_jimeng.mp4",
    "第02镜_场1-1B_jimeng.mp4",
    "第03镜_场1-1C_jimeng.mp4",
    "第04镜_场1-1D_jimeng.mp4",
    "第05镜_场1-1E_jimeng.mp4",
    "第06镜_场1-2A_jimeng.mp4",
    "第07镜_场1-2B_jimeng.mp4",
    "第08镜_场1-2C_jimeng.mp4",
    "第09镜_场1-2D_jimeng.mp4",
    "第10镜_场1-2E_jimeng.mp4",
    "第11镜_场1-3A_jimeng.mp4",
    "第12镜_场1-3B_jimeng.mp4",
    "第13镜_场1-3C_jimeng.mp4",
    "第14镜_场1-3D_jimeng.mp4",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def api_key() -> str:
    return (os.environ.get("ARK_API_KEY") or os.environ.get("VOLC_ARK_API_KEY") or "").strip()


def fetch_tasks_page(
    base: str,
    key: str,
    page_num: int,
    page_size: int,
    status: str | None,
    model: str | None,
) -> dict:
    q: list[tuple[str, str]] = [
        ("page_num", str(page_num)),
        ("page_size", str(min(page_size, 500))),
    ]
    if status:
        q.append(("filter.status", status))
    if model:
        q.append(("filter.model", model))
    url = base.rstrip("/") + TASKS_PATH + "?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"HTTP {e.code}: {detail or e.reason}") from e
    return json.loads(body)


def extract_task_list(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("tasks", "items", "list", "data", "result"):
        v = payload.get(key)
        if isinstance(v, list):
            return [x for x in v if isinstance(x, dict)]
        if isinstance(v, dict):
            for sub in ("tasks", "items", "list", "records", "generations", "results"):
                if isinstance(v.get(sub), list):
                    return [x for x in v[sub] if isinstance(x, dict)]
    return []


def get_created_ts(task: dict) -> float:
    v = task.get("created_at") or task.get("createdAt") or task.get("create_time") or 0
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return 0.0
    return 0.0


def get_task_id(task: dict) -> str:
    return str(task.get("id") or task.get("task_id") or "")


def get_status(task: dict) -> str:
    return str(task.get("status") or "").lower()


def get_video_url(task: dict) -> str | None:
    content = task.get("content")
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            content = None
    if isinstance(content, dict):
        u = content.get("video_url") or content.get("videoUrl") or content.get("url")
        if isinstance(u, str) and u.startswith("http"):
            return u
    for k, v in task.items():
        if "url" in k.lower() and isinstance(v, str) and v.startswith("http") and ".mp4" in v.lower():
            return v
    return _walk_video_url(task)


def _walk_video_url(obj: object, depth: int = 0) -> str | None:
    if depth > 12:
        return None
    if isinstance(obj, str) and obj.startswith("http") and (".mp4" in obj.lower() or "video" in obj):
        return obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "video" in k.lower() and "url" in k.lower() and isinstance(v, str) and v.startswith("http"):
                return v
            hit = _walk_video_url(v, depth + 1)
            if hit:
                return hit
    if isinstance(obj, list):
        for x in obj:
            hit = _walk_video_url(x, depth + 1)
            if hit:
                return hit
    return None


def fetch_all_tasks(
    base: str,
    key: str,
    page_size: int,
    status: str | None,
    model: str | None,
    max_pages: int,
) -> list[dict]:
    out: list[dict] = []
    for page in range(1, max_pages + 1):
        data = fetch_tasks_page(base, key, page, page_size, status, model)
        batch = extract_task_list(data)
        if not batch and isinstance(data, dict):
            batch = extract_task_list(data.get("data"))
        if not batch:
            break
        out.extend(batch)
        if len(batch) < page_size:
            break
    return out


def download_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "demo1-ark-download/1.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        dest.write_bytes(resp.read())


def safe_name(filename: str) -> str:
    base = filename.strip().replace(".mp4", "")
    base = re.sub(r'[/\\:*?"<>|]', "_", base)
    return base + ".mp4" if base else "jimeng.mp4"


def cmd_list(args: argparse.Namespace) -> None:
    key = api_key()
    if not key:
        print("请设置环境变量 ARK_API_KEY 或 VOLC_ARK_API_KEY", file=sys.stderr)
        sys.exit(1)
    base = os.environ.get("ARK_BASE_URL") or DEFAULT_BASE
    tasks = fetch_all_tasks(base, key, args.page_size, args.status, args.model, args.max_pages)
    if args.json:
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
        return
    for t in tasks:
        tid = get_task_id(t)
        st = get_status(t) or "?"
        ts = get_created_ts(t)
        model = t.get("model") or ""
        vu = get_video_url(t) or ""
        preview = (vu[:80] + "…") if len(vu) > 80 else vu
        print(f"{tid}\t{st}\t{ts}\t{model}\t{preview}")


def cmd_download(args: argparse.Namespace) -> None:
    key = api_key()
    if not key:
        print("请设置环境变量 ARK_API_KEY 或 VOLC_ARK_API_KEY", file=sys.stderr)
        sys.exit(1)
    base = os.environ.get("ARK_BASE_URL") or DEFAULT_BASE
    tasks = fetch_all_tasks(base, key, args.page_size, args.status or "succeeded", args.model, args.max_pages)
    root = repo_root()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir

    candidates: list[dict] = []
    for t in tasks:
        if get_status(t) != "succeeded":
            continue
        u = get_video_url(t)
        if u:
            candidates.append(t)
    candidates.sort(key=get_created_ts)

    if args.ep01_names:
        if len(candidates) < len(EP01_FILENAMES):
            print(
                f"已成功且有 URL 的任务仅 {len(candidates)} 条，不足 {len(EP01_FILENAMES)}。请先用 list 查看。",
                file=sys.stderr,
            )
            sys.exit(1)
        pairs = list(zip(EP01_FILENAMES, candidates[: len(EP01_FILENAMES)]))
    else:
        pairs = []
        use = candidates[: args.limit] if args.limit else candidates
        for i, t in enumerate(use):
            tid = get_task_id(t) or f"task_{i}"
            safe = re.sub(r'[/\\:*?"<>|]', "_", tid) + ".mp4"
            pairs.append((safe, t))

    ok = fail = 0
    for name, t in pairs:
        u = get_video_url(t)
        if not u:
            fail += 1
            continue
        dest = out_dir / (name if name.endswith(".mp4") else safe_name(name))
        try:
            print(f"下载 {get_task_id(t)} -> {dest.name} …", file=sys.stderr)
            download_url(u, dest)
            print(f"OK {dest} ({dest.stat().st_size // 1024} KiB)")
            ok += 1
        except Exception as e:
            print(f"FAIL {name}: {e}", file=sys.stderr)
            fail += 1
    print(json.dumps({"downloaded": ok, "failed": fail, "out_dir": str(out_dir)}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description="方舟视频生成任务列表 / 下载")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="拉取任务列表并打印")
    p_list.add_argument("--page-size", type=int, default=100)
    p_list.add_argument("--max-pages", type=int, default=50)
    p_list.add_argument("--status", type=str, default=None)
    p_list.add_argument("--model", type=str, default=None)
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_dl = sub.add_parser("download", help="下载已成功任务的视频 URL")
    p_dl.add_argument("--page-size", type=int, default=100)
    p_dl.add_argument("--max-pages", type=int, default=50)
    p_dl.add_argument("--status", type=str, default="succeeded")
    p_dl.add_argument("--model", type=str, default=None)
    p_dl.add_argument("--out-dir", type=str, default="video/generated")
    p_dl.add_argument("--limit", type=int, default=0)
    p_dl.add_argument("--ep01-names", action="store_true")
    p_dl.set_defaults(func=cmd_download)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
