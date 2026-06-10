#!/usr/bin/env python3
"""
方案 A：短剧任务归档落在项目 assets/ 下（贴近成片/素材），不混仓库 video/*_tasks。

路径约定（project_root = 如 darams/天工开物）：
  assets/generated/EP01/tasks.json     — Seedance 段落/镜级视频（按集）
  assets/tasks_seedream.json           — Seedream 出图
  assets/tasks_jimeng_image.json       — 即梦/视觉 图片
  assets/tasks_jimeng_video.json       — 即梦/视觉 视频
  assets/tasks_kling.json              — Kling

环境变量（任选）：DRAMA_PROJECT_ROOT / ARK_PROJECT_ROOT / KLING_PROJECT_ROOT

CLI:
  python3 project_task_archive.py list --project-root PATH [--episode EP01] [--kind seedance]
  python3 project_task_archive.py import-jsonl PATH --project-root PATH --episode EP01
  python3 project_task_archive.py migrate-legacy-video --project-root PATH
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

KIND_SEEDANCE = "seedance_video"
KIND_SEEDREAM = "seedream_image"
KIND_JIMENG_IMAGE = "jimeng_image"
KIND_JIMENG_VIDEO = "jimeng_video"
KIND_KLING = "kling"

KIND_TO_FILENAME = {
    KIND_SEEDREAM: "tasks_seedream.json",
    KIND_JIMENG_IMAGE: "tasks_jimeng_image.json",
    KIND_JIMENG_VIDEO: "tasks_jimeng_video.json",
    KIND_KLING: "tasks_kling.json",
    KIND_SEEDANCE: "tasks_seedance.json",
}


def resolve_project_root(explicit: Path | str | None = None) -> Path | None:
    if explicit:
        p = Path(explicit).expanduser()
        return p.resolve() if p.is_dir() else None
    for key in ("DRAMA_PROJECT_ROOT", "ARK_PROJECT_ROOT", "KLING_PROJECT_ROOT"):
        v = (os.environ.get(key) or "").strip()
        if v:
            p = Path(v).expanduser()
            if p.is_dir():
                return p.resolve()
    return None


def archive_file(
    project_root: Path | str,
    kind: str,
    episode_id: str | None = None,
) -> Path:
    root = Path(project_root).resolve()
    if kind == KIND_SEEDANCE and episode_id:
        ep = episode_id.upper()
        d = root / "assets" / "generated" / ep
        d.mkdir(parents=True, exist_ok=True)
        return d / "tasks.json"
    name = KIND_TO_FILENAME.get(kind, f"tasks_{kind}.json")
    assets = root / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    return assets / name


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def legacy_video_archive() -> Path:
    return _repo_root() / "video" / "ark_tasks" / "tasks_video.json"


def legacy_image_archive() -> Path:
    return _repo_root() / "video" / "ark_tasks" / "tasks_image.json"


def legacy_jimeng_archive(kind: str) -> Path:
    base = _repo_root() / "video" / "jimeng_tasks"
    if kind == KIND_JIMENG_IMAGE:
        return base / "tasks_image.json"
    if kind == KIND_JIMENG_VIDEO:
        return base / "tasks_video.json"
    return base / "tasks.json"


def legacy_kling_archive() -> Path:
    return _repo_root() / "video" / "kling_tasks" / "tasks.json"


def load_doc(path: Path) -> dict:
    if not path.is_file():
        return {"tasks": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"tasks": data}
    if not isinstance(data, dict):
        return {"tasks": []}
    data.setdefault("tasks", [])
    return data


def save_doc(path: Path, doc: dict, *, kind: str, episode_id: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.setdefault("schema", "drama_tasks_v1")
    doc["kind"] = kind
    if episode_id:
        doc["episode_id"] = episode_id.upper()
    doc["archive_path"] = str(path)
    doc["updated_at"] = datetime.now().isoformat()
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_task(
    kind: str,
    task_id: str,
    params: dict,
    *,
    project_root: Path | str,
    status: str = "pending",
    episode_id: str | None = None,
    task_type: str | None = None,
) -> dict:
    path = archive_file(project_root, kind, episode_id)
    doc = load_doc(path)
    task = {
        "task_id": str(task_id),
        "type": task_type or kind,
        "params": params,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    doc["tasks"] = [t for t in doc["tasks"] if t.get("task_id") != task["task_id"]]
    doc["tasks"].insert(0, task)
    save_doc(path, doc, kind=kind, episode_id=episode_id)
    return task


def update_task(
    task_id: str,
    updates: dict,
    *,
    project_root: Path | str,
    kind: str | None = None,
    episode_id: str | None = None,
) -> bool:
    root = Path(project_root).resolve()
    paths: list[Path] = []
    if kind and episode_id:
        paths.append(archive_file(root, kind, episode_id))
    elif kind:
        paths.append(archive_file(root, kind, None))
    else:
        assets = root / "assets"
        if assets.is_dir():
            paths.extend(sorted(assets.glob("tasks_*.json")))
            gen = assets / "generated"
            if gen.is_dir():
                paths.extend(sorted(gen.glob("*/tasks.json")))
    for path in paths:
        if not path.is_file():
            continue
        doc = load_doc(path)
        for task in doc["tasks"]:
            if task.get("task_id") == str(task_id):
                task.update(updates)
                task["updated_at"] = datetime.now().isoformat()
                k = doc.get("kind") or kind or KIND_SEEDANCE
                ep = doc.get("episode_id") or episode_id
                save_doc(path, doc, kind=k, episode_id=ep)
                return True
    return False


def list_tasks(
    project_root: Path | str,
    *,
    kind: str | None = None,
    episode_id: str | None = None,
    limit: int = 50,
) -> list[dict]:
    root = Path(project_root).resolve()
    paths: list[Path] = []
    if kind == KIND_SEEDANCE and episode_id:
        paths.append(archive_file(root, kind, episode_id))
    elif kind:
        paths.append(archive_file(root, kind, None))
    else:
        assets = root / "assets"
        if assets.is_dir():
            paths.extend(sorted(assets.glob("tasks_*.json")))
            gen = assets / "generated"
            if gen.is_dir():
                paths.extend(sorted(gen.glob("*/tasks.json")))
    merged: list[dict] = []
    for path in paths:
        if not path.is_file():
            continue
        for t in load_doc(path).get("tasks") or []:
            row = dict(t)
            row["_archive_file"] = str(path.relative_to(root))
            merged.append(row)
    merged.sort(key=lambda x: x.get("updated_at") or x.get("created_at") or "", reverse=True)
    return merged[:limit]


def find_by_segment_id(
    segment_id: str,
    *,
    project_root: Path | str,
    episode_id: str,
    exclude_statuses: tuple[str, ...] = ("failed", "cancelled"),
) -> list[dict]:
    """Return archived tasks for a given segment_id (non-failed).

    Searches assets/generated/EP##/tasks.json for tasks whose
    params.segment_id matches, filtering out failed/cancelled ones.
    """
    root = Path(project_root).resolve()
    path = archive_file(root, KIND_SEEDANCE, episode_id)
    if not path.is_file():
        return []
    doc = load_doc(path)
    results = []
    for task in doc.get("tasks", []):
        params = task.get("params") or {}
        if params.get("segment_id") == segment_id:
            status = task.get("status", "unknown")
            if status not in exclude_statuses:
                results.append(task)
    return results


def get_submitted_segment_ids(
    *,
    project_root: Path | str,
    episode_id: str,
    exclude_statuses: tuple[str, ...] = ("failed", "cancelled"),
) -> dict[str, str]:
    """Return {segment_id: task_id} for all non-failed segments in an episode.

    Used for dedup checks before batch submission.
    """
    root = Path(project_root).resolve()
    path = archive_file(root, KIND_SEEDANCE, episode_id)
    if not path.is_file():
        return {}
    doc = load_doc(path)
    result: dict[str, str] = {}
    for task in doc.get("tasks", []):
        params = task.get("params") or {}
        sid = params.get("segment_id")
        status = task.get("status", "unknown")
        if sid and status not in exclude_statuses:
            if sid not in result:  # keep first (most recent, since list is newest-first)
                result[sid] = task.get("task_id", "")
    return result


def get_submitted_shot_ids(
    *,
    project_root: Path | str,
    episode_id: str,
    exclude_statuses: tuple[str, ...] = ("failed", "cancelled"),
) -> dict[str, str]:
    """Return {shot_id: task_id} for all non-failed shots in an episode.

    Used for dedup checks before batch shot submission.
    """
    root = Path(project_root).resolve()
    path = archive_file(root, KIND_SEEDANCE, episode_id)
    if not path.is_file():
        return {}
    doc = load_doc(path)
    result: dict[str, str] = {}
    for task in doc.get("tasks", []):
        params = task.get("params") or {}
        sid = params.get("shot_id")
        status = task.get("status", "unknown")
        if sid and status not in exclude_statuses:
            if sid not in result:
                result[sid] = task.get("task_id", "")
    return result


def import_jsonl(
    path: Path,
    *,
    project_root: Path | str,
    episode_id: str,
    project_name: str = "",
) -> int:
    existing: set[str] = set()
    for t in list_tasks(project_root, episode_id=episode_id, kind=KIND_SEEDANCE, limit=500):
        existing.add(str(t.get("task_id")))
    n = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        tid = row.get("task_id") or (row.get("response") or {}).get("id")
        if not tid or str(tid) in existing:
            continue
        params: dict[str, Any] = {
            "episode": episode_id.upper(),
            "imported_from": str(path),
            "imported_at": datetime.now().isoformat(),
        }
        if project_name:
            params["project"] = project_name
        if row.get("segment_id"):
            params["segment_id"] = row["segment_id"]
        if row.get("shot_id"):
            params["shot_id"] = row["shot_id"]
        add_task(
            KIND_SEEDANCE,
            str(tid),
            params,
            project_root=project_root,
            status="unknown",
            episode_id=episode_id,
        )
        existing.add(str(tid))
        n += 1
    return n


def migrate_legacy_ark_video(project_root: Path | str) -> int:
    """video/ark_tasks/tasks_video.json → 各集 assets/generated/EP##/tasks.json"""
    leg = legacy_video_archive()
    if not leg.is_file():
        return 0
    tasks = load_doc(leg).get("tasks") or []
    n = 0
    for t in tasks:
        tid = t.get("task_id")
        if not tid:
            continue
        params = dict(t.get("params") or {})
        ep = (params.get("episode") or "EP00").upper()
        add_task(
            KIND_SEEDANCE,
            str(tid),
            params,
            project_root=project_root,
            status=str(t.get("status") or "unknown"),
            episode_id=ep,
            task_type=str(t.get("type") or KIND_SEEDANCE),
        )
        for k in ("video_url", "local_mp4", "error"):
            if t.get(k):
                update_task(
                    str(tid),
                    {k: t[k]},
                    project_root=project_root,
                    kind=KIND_SEEDANCE,
                    episode_id=ep,
                )
        n += 1
    return n


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    args = sys.argv[2:]

    def pop_opt(name: str, default: str | None = None) -> str | None:
        nonlocal args
        if name in args:
            i = args.index(name)
            if i + 1 < len(args):
                v = args[i + 1]
                args = args[:i] + args[i + 2 :]
                return v
        return default

    proot_s = pop_opt("--project-root") or pop_opt("-p")
    proot = resolve_project_root(proot_s)
    if not proot and cmd not in ("help",):
        print(json.dumps({"error": "需要 --project-root 或 DRAMA_PROJECT_ROOT"}, ensure_ascii=False))
        return 1

    if cmd == "list":
        episode = pop_opt("--episode")
        kind = pop_opt("--kind")
        limit = int(pop_opt("--limit", "30") or "30")
        tasks = list_tasks(proot, kind=kind, episode_id=episode, limit=limit)
        print(
            json.dumps(
                {"project_root": str(proot), "count": len(tasks), "tasks": tasks},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if cmd == "import-jsonl" and args:
        ep = (pop_opt("--episode") or "EP01").upper()
        pname = pop_opt("--project", "") or ""
        p = Path(args[0]).expanduser().resolve()
        if not p.is_file():
            print(json.dumps({"error": f"找不到 {p}"}, ensure_ascii=False))
            return 1
        n = import_jsonl(p, project_root=proot, episode_id=ep, project_name=pname)
        print(
            json.dumps(
                {"imported": n, "episode": ep, "tasks_file": str(archive_file(proot, KIND_SEEDANCE, ep))},
                ensure_ascii=False,
            )
        )
        return 0

    if cmd == "migrate-legacy-video":
        n = migrate_legacy_ark_video(proot)
        print(json.dumps({"migrated": n, "project_root": str(proot)}, ensure_ascii=False))
        return 0

    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
