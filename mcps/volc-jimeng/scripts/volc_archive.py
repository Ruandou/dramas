#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火山引擎任务归档管理
图片和视频分开归档
保存和查询任务归档
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def get_archive_base():
    """获取归档根目录"""
    # 向上三级：scripts -> volc-jimeng -> mcps -> 仓库根
    script_dir = os.path.dirname(os.path.abspath(__file__))
    archive_dir = os.path.join(script_dir, "..", "..", "..", "video", "jimeng_tasks")
    os.makedirs(archive_dir, exist_ok=True)
    return archive_dir

def get_archive_path(task_type: str = None):
    """获取归档文件路径"""
    base = get_archive_base()
    if task_type == "image":
        return os.path.join(base, "tasks_image.json")
    elif task_type == "video":
        return os.path.join(base, "tasks_video.json")
    else:
        return os.path.join(base, "tasks.json")

def load_archive(task_type: str = None):
    """加载任务归档"""
    path = get_archive_path(task_type)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tasks": []}

def save_archive(archive, task_type: str = None):
    """保存任务归档"""
    path = get_archive_path(task_type)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)

def add_task(task_type: str, task_id: str, params: dict, status: str = "pending"):
    """添加任务到归档"""
    # 根据类型选择归档文件
    archive_type = "image" if "image" in task_type.lower() or "jimeng_t2i" in str(params.get("req_key", "")) else "video"
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

def update_task(task_id: str, updates: dict, archive_type: str = None):
    """更新任务状态"""
    if archive_type:
        archive = load_archive(archive_type)
        found = False
        for task in archive["tasks"]:
            if task["task_id"] == task_id:
                task.update(updates)
                task["updated_at"] = datetime.now().isoformat()
                found = True
                break
        if found:
            save_archive(archive, archive_type)
    else:
        # 尝试在两个归档文件中查找
        for at in ["image", "video"]:
            archive = load_archive(at)
            for task in archive["tasks"]:
                if task["task_id"] == task_id:
                    task.update(updates)
                    task["updated_at"] = datetime.now().isoformat()
                    save_archive(archive, at)
                    return

def list_tasks(limit: int = 20, task_type: str = None):
    """列出最近的任务"""
    if task_type == "image":
        return load_archive("image")["tasks"][:limit]
    elif task_type == "video":
        return load_archive("video")["tasks"][:limit]
    else:
        # 合并两个归档
        image_tasks = load_archive("image")["tasks"]
        video_tasks = load_archive("video")["tasks"]
        all_tasks = image_tasks + video_tasks
        # 按时间排序
        all_tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return all_tasks[:limit]

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少子命令"}, ensure_ascii=False))
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add":
        # add <type> <task_id> <params_json>
        if len(sys.argv) < 4:
            print(json.dumps({"error": "缺少参数"}, ensure_ascii=False))
            sys.exit(1)
        task_type = sys.argv[2]
        task_id = sys.argv[3]
        params = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
        result = add_task(task_type, task_id, params)
        print(json.dumps(result, ensure_ascii=False))

    elif cmd == "update":
        # update <task_id> <updates_json> [archive_type]
        if len(sys.argv) < 4:
            print(json.dumps({"error": "缺少参数"}, ensure_ascii=False))
            sys.exit(1)
        task_id = sys.argv[2]
        updates = json.loads(sys.argv[3])
        archive_type = sys.argv[4] if len(sys.argv) > 4 else None
        update_task(task_id, updates, archive_type)
        print(json.dumps({"status": "ok"}))

    elif cmd == "list":
        # list [limit] [task_type]
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        task_type = sys.argv[3] if len(sys.argv) > 3 else None
        tasks = list_tasks(limit, task_type)
        print(json.dumps(tasks, ensure_ascii=False))

    elif cmd == "list-image":
        # 只列出图片任务
        tasks = list_tasks(100, "image")
        print(json.dumps(tasks, ensure_ascii=False))

    elif cmd == "list-video":
        # 只列出视频任务
        tasks = list_tasks(100, "video")
        print(json.dumps(tasks, ensure_ascii=False))

    else:
        print(json.dumps({"error": f"未知命令: {cmd}"}, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
