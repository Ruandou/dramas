#!/usr/bin/env python3
"""
Seedance 任务登记（方案 A）→ {project_root}/assets/generated/EP##/tasks.json

所有提交入口须经本模块；禁止写 video/ark_tasks 或 task_log.jsonl。

CLI（委托 project_task_archive）:
  python3 ark_seedance_record.py list --project-root dramas/天工开物 [--episode EP01]
  python3 ark_seedance_record.py import-jsonl <path> --project-root ... --episode EP01
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# 公共基建层 mcps/shared（本项目脚本从 mcps/shared/ 直接运行时无需此段）
_SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

import project_task_archive as pta

KIND = pta.KIND_SEEDANCE


def summarize_content(content: list | None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in content or []:
        if not isinstance(item, dict):
            continue
        t = item.get("type")
        if t == "text":
            out.append({"type": "text", "chars": len(item.get("text") or "")})
        elif t == "image_url":
            u = (item.get("image_url") or {}).get("url") or ""
            out.append(
                {
                    "type": "image_url",
                    "role": item.get("role"),
                    "source": "data_uri" if u.startswith("data:") else "url",
                }
            )
        elif t == "audio_url":
            out.append({"type": "audio_url", "role": item.get("role")})
    return out


def archive_params_from_body(body: dict[str, Any], extra: dict | None = None) -> dict:
    p: dict[str, Any] = {
        "model": body.get("model"),
        "ratio": body.get("ratio"),
        "resolution": body.get("resolution"),
        "duration": body.get("duration"),
        "generate_audio": body.get("generate_audio"),
        "content": summarize_content(body.get("content")),
    }
    if extra:
        p.update(extra)
    return p


def record_submit(
    task_id: str,
    body: dict[str, Any],
    *,
    project_root: Path | str,
    episode: str,
    project_name: str = "天工开物",
    segment_id: str | None = None,
    shot_id: str | None = None,
) -> Path:
    if not task_id:
        raise ValueError("task_id 为空")
    extra: dict[str, Any] = {"episode": episode.upper(), "project": project_name}
    if segment_id:
        extra["segment_id"] = segment_id
    if shot_id:
        extra["shot_id"] = shot_id
    pta.add_task(
        KIND,
        str(task_id),
        archive_params_from_body(body, extra),
        project_root=project_root,
        status="pending",
        episode_id=episode,
    )
    return pta.archive_file(project_root, KIND, episode)


def record_status(
    task_id: str,
    status: str,
    *,
    project_root: Path | str | None = None,
    episode: str | None = None,
    video_url: str | None = None,
    local_mp4: str | None = None,
    error: str | None = None,
) -> bool:
    if not task_id:
        return False
    proot = Path(project_root).resolve() if project_root else pta.resolve_project_root()
    if not proot:
        return False
    updates: dict[str, Any] = {"status": status}
    if video_url:
        updates["video_url"] = video_url
    if local_mp4:
        updates["local_mp4"] = local_mp4
    if error:
        updates["error"] = error
    return pta.update_task(
        str(task_id),
        updates,
        project_root=proot,
        kind=KIND,
        episode_id=episode,
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(pta.main())
