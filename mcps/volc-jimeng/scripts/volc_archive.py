#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
即梦/视觉任务归档（方案 A）。

设置 DRAMA_PROJECT_ROOT → {project}/assets/tasks_jimeng_image.json | tasks_jimeng_video.json
未设置时回退 video/jimeng_tasks/（遗留）。
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

_VOLC_SCRIPTS = Path(__file__).resolve().parent
_ARK_SCRIPTS = _VOLC_SCRIPTS.parent.parent / "volc-ark" / "scripts"
if str(_ARK_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_ARK_SCRIPTS))

import project_task_archive as pta  # noqa: E402


def _jimeng_kind(task_type: str, params: dict | None = None) -> str:
    t = task_type.lower()
    p = params or {}
    if "image" in t or "jimeng_t2i" in str(p.get("req_key", "")):
        return pta.KIND_JIMENG_IMAGE
    return pta.KIND_JIMENG_VIDEO


def get_archive_base() -> str:
    proot = pta.resolve_project_root()
    if proot:
        return str(proot / "assets")
    script_dir = Path(__file__).resolve().parent
    archive_dir = script_dir.parent.parent.parent / "video" / "jimeng_tasks"
    archive_dir.mkdir(parents=True, exist_ok=True)
    return str(archive_dir)


def get_archive_path(task_type: str | None = None) -> str:
    proot = pta.resolve_project_root()
    if proot:
        kind = pta.KIND_JIMENG_IMAGE if task_type == "image" else pta.KIND_JIMENG_VIDEO
        return str(pta.archive_file(proot, kind))
    base = get_archive_base()
    if task_type == "image":
        return os.path.join(base, "tasks_image.json")
    if task_type == "video":
        return os.path.join(base, "tasks_video.json")
    return os.path.join(base, "tasks.json")


def load_archive(task_type: str | None = None) -> dict:
    return pta.load_doc(Path(get_archive_path(task_type)))


def save_archive(archive: dict, task_type: str | None = None) -> None:
    path = Path(get_archive_path(task_type))
    kind = pta.KIND_JIMENG_IMAGE if task_type == "image" else pta.KIND_JIMENG_VIDEO
    pta.save_doc(path, archive, kind=kind)


def add_task(task_type: str, task_id: str, params: dict, status: str = "pending") -> dict:
    proot = pta.resolve_project_root()
    if proot:
        kind = _jimeng_kind(task_type, params)
        return pta.add_task(
            kind,
            task_id,
            params,
            project_root=proot,
            status=status,
            task_type=task_type,
        )
    archive_type = "image" if _jimeng_kind(task_type, params) == pta.KIND_JIMENG_IMAGE else "video"
    archive = load_archive(archive_type)
    task = {
        "task_id": task_id,
        "type": task_type,
        "params": params,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    archive["tasks"].insert(0, task)
    save_archive(archive, archive_type)
    return task


def update_task(task_id: str, updates: dict, archive_type: str | None = None) -> bool:
    proot = pta.resolve_project_root()
    if proot:
        kind = None
        if archive_type == "image":
            kind = pta.KIND_JIMENG_IMAGE
        elif archive_type == "video":
            kind = pta.KIND_JIMENG_VIDEO
        return pta.update_task(task_id, updates, project_root=proot, kind=kind)
    if archive_type:
        archive = load_archive(archive_type)
        for task in archive["tasks"]:
            if task.get("task_id") == task_id:
                task.update(updates)
                task["updated_at"] = datetime.now().isoformat()
                save_archive(archive, archive_type)
                return True
        return False
    for at in ("image", "video"):
        if update_task(task_id, updates, at):
            return True
    return False


def list_tasks(limit: int = 20, task_type: str | None = None) -> list[dict]:
    proot = pta.resolve_project_root()
    if proot:
        if task_type == "image":
            return pta.list_tasks(proot, kind=pta.KIND_JIMENG_IMAGE, limit=limit)
        if task_type == "video":
            return pta.list_tasks(proot, kind=pta.KIND_JIMENG_VIDEO, limit=limit)
        return pta.list_tasks(proot, limit=limit)
    if task_type == "image":
        return load_archive("image")["tasks"][:limit]
    if task_type == "video":
        return load_archive("video")["tasks"][:limit]
    image_tasks = load_archive("image")["tasks"]
    video_tasks = load_archive("video")["tasks"]
    merged = image_tasks + video_tasks
    merged.sort(key=lambda t: t.get("created_at", ""), reverse=True)
    return merged[:limit]


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    if cmd == "list":
        task_type = None
        limit = 20
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--type" and i + 1 < len(args):
                task_type = args[i + 1]
                i += 2
            elif args[i] == "--limit" and i + 1 < len(args):
                limit = int(args[i + 1])
                i += 2
            else:
                i += 1
        print(json.dumps(list_tasks(limit, task_type), ensure_ascii=False, indent=2))
        return 0
    if cmd == "add" and len(sys.argv) >= 5:
        add_task(sys.argv[2], sys.argv[3], json.loads(sys.argv[4]))
        return 0
    if cmd == "update" and len(sys.argv) >= 4:
        updates = json.loads(sys.argv[2])
        tid = sys.argv[3]
        archive_type = sys.argv[4] if len(sys.argv) > 4 else None
        ok = update_task(tid, updates, archive_type)
        print(json.dumps({"updated": ok, "task_id": tid}, ensure_ascii=False))
        return 0 if ok else 1
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
