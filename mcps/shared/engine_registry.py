#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
引擎注册表（engine registry）：能力(capability) → 引擎(engine) 的单一真相源。

目的：消除 agent 提示词 / 资产模板 / 脚本中对具体引擎名（Seedream/Seedance/gpt-image）
的硬编码。agent 只引用「能力」（image_gen / video_gen），由本注册表解析当前默认引擎。

切换引擎只需：
  1) 改本文件 DEFAULT_ENGINES，或
  2) 设环境变量覆盖：IMAGE_GEN_ENGINE=seedream / VIDEO_GEN_ENGINE=kling

新增引擎：在 ENGINES 注册一行（CLI 路径 + MCP 工具名前缀 + 归档 kind）。
"""
from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# 能力（capability）常量：agent / 模板 / 脚本只引用这些，不引用具体引擎
# ---------------------------------------------------------------------------
CAP_IMAGE_GEN = "image_gen"   # 图片生成（文生图/图生图）
CAP_VIDEO_GEN = "video_gen"   # 视频生成

# ---------------------------------------------------------------------------
# 引擎注册表：engine_id -> 元数据
#   cli          : 引擎 CLI 脚本（相对仓库根）
#   mcp_server   : MCP server 名（.cursor/mcp.json 的 key）
#   mcp_prefix   : MCP 工具名前缀（generate/batch/docs/reconcile 拼在其后）
#   archive_kind : 任务归档 kind（project_task_archive.KIND_*）
#   env_key      : 鉴权环境变量
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]

ENGINES = {
    "gpt-image": {
        "capability": CAP_IMAGE_GEN,
        "cli": "mcps/gpt-image/scripts/gpt_image.py",
        "mcp_server": "gpt-image",
        "mcp_prefix": "gpt_image",
        "archive_kind": "gpt_image",
        "env_key": "GPT_IMAGE_API_KEY",
        "display": "gpt-image-2（OpenAI 兼容中转，$0.10/张一口价）",
    },
    "seedream": {
        "capability": CAP_IMAGE_GEN,
        "cli": "mcps/volc-ark/scripts/ark_seedream_image.py",
        "mcp_server": "volc-ark",
        "mcp_prefix": "ark_seedream",
        "archive_kind": "seedream_image",
        "env_key": "ARK_API_KEY",
        "display": "Seedream 5.0 lite（火山方舟）",
    },
    "seedance": {
        "capability": CAP_VIDEO_GEN,
        "cli": "mcps/volc-ark/scripts/ark_seedance_video.py",
        "mcp_server": "volc-ark",
        "mcp_prefix": "ark_seedance",
        "archive_kind": "seedance_video",
        "env_key": "ARK_API_KEY",
        "display": "Seedance 2.0 fast（火山方舟）",
    },
    "kling": {
        "capability": CAP_VIDEO_GEN,
        "cli": "mcps/kling/scripts/kling_video.py",
        "mcp_server": "kling",
        "mcp_prefix": "kling_video",
        "archive_kind": "kling",
        "env_key": "KLING_AK",
        "display": "可灵 AI 视频",
    },
}

# 能力 -> 默认引擎（环境变量可覆盖）
DEFAULT_ENGINES = {
    CAP_IMAGE_GEN: "gpt-image",
    CAP_VIDEO_GEN: "seedance",
}

# 环境变量名（能力 -> 覆盖该能力默认引擎的 env var）
_CAP_ENV = {
    CAP_IMAGE_GEN: "IMAGE_GEN_ENGINE",
    CAP_VIDEO_GEN: "VIDEO_GEN_ENGINE",
}


def default_engine(capability: str) -> str:
    """返回某能力当前生效的引擎 id（环境变量优先于默认值）。"""
    env = _CAP_ENV.get(capability)
    if env:
        override = (os.environ.get(env) or "").strip()
        if override:
            if override not in ENGINES:
                raise ValueError(
                    f"{env}={override!r} 未注册；可用引擎: {sorted(ENGINES)}"
                )
            return override
    return DEFAULT_ENGINES[capability]


def engine_info(engine_id: str) -> dict:
    """返回引擎元数据（含解析后的绝对 CLI 路径）。"""
    if engine_id not in ENGINES:
        raise ValueError(f"未注册引擎: {engine_id!r}；可用: {sorted(ENGINES)}")
    info = dict(ENGINES[engine_id])
    info["engine_id"] = engine_id
    info["cli_abs"] = str(_REPO_ROOT / info["cli"])
    return info


def resolve(capability: str) -> dict:
    """返回某能力当前生效引擎的完整元数据。"""
    return engine_info(default_engine(capability))


def mcp_tool(capability: str, action: str) -> str:
    """拼出当前引擎某动作的 MCP 工具名，如 mcp_tool('image_gen','generate') -> 'gpt_image_generate'。"""
    return f"{resolve(capability)['mcp_prefix']}_{action}"


def cli_path(capability: str) -> str:
    """返回当前引擎 CLI 的绝对路径。"""
    return resolve(capability)["cli_abs"]


def engines_for(capability: str) -> list[str]:
    """返回某能力下所有已注册引擎 id。"""
    return [e for e, m in ENGINES.items() if m["capability"] == capability]


if __name__ == "__main__":
    import json

    out = {
        cap: {
            "default_engine": default_engine(cap),
            "available": engines_for(cap),
            "resolved": resolve(cap),
        }
        for cap in (CAP_IMAGE_GEN, CAP_VIDEO_GEN)
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
