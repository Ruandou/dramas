#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方舟 volc-ark 任务归档（与 volc-jimeng 的 video/jimeng_tasks 并列）

  video/ark_tasks/tasks_image.json   # Seedream
  video/ark_tasks/tasks_video.json   # Seedance

CLI:
  python3 ark_archive.py list [--type image|video] [--limit 20]
  python3 ark_archive.py add <type> <task_id> '<params_json>'
  python3 ark_archive.py update <task_id> '<updates_json>' [image|video]
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def get_archive_base() -> str:
    script_dir = Path(__file__).resolve().parent
    archive_dir = script_dir.parent.parent.parent / "video" / "ark_tasks"
    archive_dir.mkdir(parents=True, exist_ok=True)
    return str(archive_dir)


def get_archive_path(task_type: str | None = None) -> str:
    base = get_archive_base()
    if task_type == "image":
        return os.path.join(base, "tasks_image.json")
    if task_type == "video":
        return os.path.join(base, "tasks_video.json")
    return os.path.join(base, "tasks.json")


def load_archive(task_type: str | None = None) -> dict:
    path = get_archive_path(task_type)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"tasks": []}


def save_archive(archive: dict, task_type: str | None = None) -> None:
    path = get_archive_path(task_type)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)


def archive_kind(task_type: str, params: dict | None = None) -> str:
    t = task_type.lower()
    if "seedream" in t or "image" in t:
        return "image"
    if "seedance" in t or "video" in t:
        return "video"
    if params and "req_key" in str(params):
        return "image"
    return "video"


def add_task(
    task_type: str,
    task_id: str,
    params: dict,
    status: str = "pending",
) -> dict:
    kind = archive_kind(task_type, params)
    archive = load_archive(kind)
    task = {
        "task_id": task_id,
        "type": task_type,
        "params": params,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    archive["tasks"].insert(0, task)
    save_archive(archive, kind)
    return task


def update_task(task_id: str, updates: dict, kind: str | None = None) -> bool:
    kinds = [kind] if kind in ("image", "video") else ["image", "video"]
    for at in kinds:
        archive = load_archive(at)
        for task in archive["tasks"]:
            if task.get("task_id") == task_id:
                task.update(updates)
                task["updated_at"] = datetime.now().isoformat()
                save_archive(archive, at)
                return True
    return False


def list_tasks(limit: int = 20, kind: str | None = None) -> list[dict]:
    if kind == "image":
        return load_archive("image")["tasks"][:limit]
    if kind == "video":
        return load_archive("video")["tasks"][:limit]
    merged = load_archive("image")["tasks"] + load_archive("video")["tasks"]
    merged.sort(key=lambda t: t.get("created_at", ""), reverse=True)
    return merged[:limit]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "list":
        kind = None
        limit = 20
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--type" and i + 1 < len(args):
                kind = args[i + 1]
                i += 2
            elif args[i] == "--limit" and i + 1 < len(args):
                limit = int(args[i + 1])
                i += 2
            else:
                i += 1
        print(json.dumps(list_tasks(limit, kind), ensure_ascii=False, indent=2))
        return 0
    if cmd == "add" and len(sys.argv) >= 5:
        add_task(sys.argv[2], sys.argv[3], json.loads(sys.argv[4]))
        return 0
    if cmd == "update" and len(sys.argv) >= 4:
        updates = json.loads(sys.argv[2])
        tid = sys.argv[3]
        kind = sys.argv[4] if len(sys.argv) > 4 else None
        ok = update_task(tid, updates, kind)
        print(json.dumps({"updated": ok, "task_id": tid}, ensure_ascii=False))
        return 0 if ok else 1
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
