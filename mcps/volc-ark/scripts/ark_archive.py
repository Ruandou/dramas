#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方舟 volc-ark 任务归档。

方案 A（默认）：设置 DRAMA_PROJECT_ROOT 或调用时传入 project_root →
  {project}/assets/generated/EP##/tasks.json 、assets/tasks_seedream.json

无 project_root 时回退仓库 video/ark_tasks/（遗留，勿再用于天工开物）。

CLI:
  python3 ark_archive.py list [--project-root PATH] [--type image|video] [--episode EP01]
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import project_task_archive as pta


def _map_kind(task_type: str, params: dict | None = None) -> tuple[str, str | None]:
    t = task_type.lower()
    p = params or {}
    if "seedream" in t:
        return pta.KIND_SEEDREAM, None
    if "seedance" in t:
        return pta.KIND_SEEDANCE, (p.get("episode") or "").upper() or None
    return pta.KIND_SEEDREAM, None


def get_archive_base() -> str:
    proot = pta.resolve_project_root()
    if proot:
        return str(proot / "assets")
    script_dir = Path(__file__).resolve().parent
    archive_dir = script_dir.parent.parent.parent / "video" / "ark_tasks"
    archive_dir.mkdir(parents=True, exist_ok=True)
    return str(archive_dir)


def get_archive_path(task_type: str | None = None) -> str:
    proot = pta.resolve_project_root()
    if proot:
        kind, ep = _map_kind(task_type or "seedance_video", {})
        if task_type == "image" or (task_type and "seedream" in task_type):
            kind = pta.KIND_SEEDREAM
            ep = None
        elif task_type == "video":
            kind = pta.KIND_SEEDANCE
        return str(pta.archive_file(proot, kind, ep))
    base = get_archive_base()
    if task_type == "image":
        return os.path.join(base, "tasks_image.json")
    if task_type == "video":
        return os.path.join(base, "tasks_video.json")
    return os.path.join(base, "tasks.json")


def load_archive(task_type: str | None = None) -> dict:
    path = Path(get_archive_path(task_type))
    return pta.load_doc(path)


def save_archive(archive: dict, task_type: str | None = None) -> None:
    path = Path(get_archive_path(task_type))
    kind, ep = _map_kind(task_type or "seedance_video", {})
    if task_type == "image":
        kind = pta.KIND_SEEDREAM
    elif task_type == "video":
        kind = pta.KIND_SEEDANCE
    pta.save_doc(path, archive, kind=kind, episode_id=ep)


def add_task(
    task_type: str,
    task_id: str,
    params: dict,
    status: str = "pending",
) -> dict:
    proot = pta.resolve_project_root()
    if proot:
        kind, ep = _map_kind(task_type, params)
        return pta.add_task(
            kind,
            task_id,
            params,
            project_root=proot,
            status=status,
            episode_id=ep,
            task_type=task_type,
        )
    kind_legacy = "image" if "seedream" in task_type.lower() or "image" in task_type.lower() else "video"
    archive = load_archive(kind_legacy)
    task = {
        "task_id": task_id,
        "type": task_type,
        "params": params,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    archive["tasks"].insert(0, task)
    save_archive(archive, kind_legacy)
    return task


def update_task(task_id: str, updates: dict, kind: str | None = None) -> bool:
    proot = pta.resolve_project_root()
    if proot:
        pta_kind = pta.KIND_SEEDANCE if kind == "video" else pta.KIND_SEEDREAM if kind == "image" else None
        return pta.update_task(
            task_id,
            updates,
            project_root=proot,
            kind=pta_kind,
        )
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
    proot = pta.resolve_project_root()
    if proot:
        pta_kind = None
        if kind == "image":
            pta_kind = pta.KIND_SEEDREAM
        elif kind == "video":
            pta_kind = pta.KIND_SEEDANCE
        return pta.list_tasks(proot, kind=pta_kind, limit=limit)
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
        proot = pta.resolve_project_root()
        args = sys.argv[2:]
        i = 0
        kind = None
        episode = None
        limit = 20
        while i < len(args):
            if args[i] == "--project-root" and i + 1 < len(args):
                proot = Path(args[i + 1]).resolve()
                i += 2
            elif args[i] == "--type" and i + 1 < len(args):
                kind = args[i + 1]
                i += 2
            elif args[i] == "--episode" and i + 1 < len(args):
                episode = args[i + 1].upper()
                i += 2
            elif args[i] == "--limit" and i + 1 < len(args):
                limit = int(args[i + 1])
                i += 2
            else:
                i += 1
        if proot and episode:
            tasks = pta.list_tasks(
                proot, kind=pta.KIND_SEEDANCE, episode_id=episode, limit=limit
            )
        elif proot:
            pta_kind = pta.KIND_SEEDREAM if kind == "image" else pta.KIND_SEEDANCE if kind == "video" else None
            tasks = pta.list_tasks(proot, kind=pta_kind, limit=limit)
        else:
            tasks = list_tasks(limit, kind)
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
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
