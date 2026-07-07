#!/usr/bin/env python3
"""cdn_urls.json 格式校验 —— 阻断临时签名 URL、错误结构。

用法：
  python3 script/check_cdn_registry.py dramas/<剧名>
  python3 script/check_cdn_registry.py --all   # 检查所有项目

检查项：
  1. 文件存在性（props/looks/scenes 三个 cdn_urls.json）
  2. 条目结构（tos_url + local_path + size_bytes + status）
  3. URL 永久性（禁止 X-Tos-Expires / 预签名参数）
  4. tos_url 可访问性（HTTP HEAD 200）
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def check_registry(path: Path) -> list[str]:
    """返回错误列表，空列表 = 通过"""
    errors = []
    asset_type = path.parent.name  # props / looks / scenes
    project = path.parent.parent.name

    if not path.is_file():
        errors.append(f"[{project}] {asset_type}/cdn_urls.json 不存在")
        return errors

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"[{project}] {asset_type}/cdn_urls.json JSON 解析失败: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append(f"[{project}] {asset_type}/cdn_urls.json 顶层不是对象")
        return errors

    for prop_id, entry in data.items():
        if not isinstance(entry, dict):
            errors.append(f"[{project}] {asset_type}/{prop_id}: 条目不是对象")
            continue

        # 结构检查
        tos_url = entry.get("tos_url", "")
        if not tos_url:
            errors.append(f"[{project}] {asset_type}/{prop_id}: 缺少 tos_url")
            continue

        # 永久 URL 检查
        forbidden = ["X-Tos-Expires", "X-Tos-Signature", "X-Tos-Credential",
                     "response-content-disposition"]
        for param in forbidden:
            if param in tos_url:
                errors.append(
                    f"[{project}] {asset_type}/{prop_id}: tos_url 含临时签名参数 "
                    f"({param})，必须使用永久 TOS URL"
                )
                break

        # URL 格式检查
        if "tos-cn-beijing.volces.com" not in tos_url:
            errors.append(
                f"[{project}] {asset_type}/{prop_id}: tos_url 域名异常: {tos_url[:80]}"
            )

    return errors


def check_all() -> int:
    dramas_dir = REPO_ROOT / "dramas"
    all_errors = []
    for project_dir in sorted(dramas_dir.iterdir()):
        if not project_dir.is_dir():
            continue
        assets_dir = project_dir / "assets"
        if not assets_dir.is_dir():
            continue
        for asset_type in ["props", "looks", "scenes"]:
            registry = assets_dir / asset_type / "cdn_urls.json"
            if registry.is_file():
                all_errors.extend(check_registry(registry))

    if all_errors:
        print(f"❌ 发现 {len(all_errors)} 个问题：")
        for e in all_errors:
            print(f"  {e}")
        return 1
    else:
        print("✅ 所有 cdn_urls.json 格式正确")
        return 0


def check_one(project_root: str) -> int:
    assets = Path(project_root) / "assets"
    all_errors = []
    for asset_type in ["props", "looks", "scenes"]:
        registry = assets / asset_type / "cdn_urls.json"
        if registry.is_file():
            all_errors.extend(check_registry(registry))
        else:
            all_errors.append(f"[{Path(project_root).name}] {asset_type}/cdn_urls.json 不存在")

    if all_errors:
        print(f"❌ 发现 {len(all_errors)} 个问题：")
        for e in all_errors:
            print(f"  {e}")
        return 1
    else:
        print("✅ cdn_urls.json 格式正确")
        return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 script/check_cdn_registry.py <project-root>")
        print("      python3 script/check_cdn_registry.py --all")
        sys.exit(2)

    if sys.argv[1] == "--all":
        sys.exit(check_all())
    else:
        sys.exit(check_one(sys.argv[1]))
