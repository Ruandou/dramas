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
CAP_STORAGE   = "storage"     # 对象存储 / CDN（参考图永久托管）

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
    "minimax": {
        "capability": CAP_VIDEO_GEN,
        "cli": "mcps/minimax/scripts/minimax_video.py",
        "mcp_server": "minimax",
        "mcp_prefix": "minimax_video",
        "archive_kind": "minimax_video",
        "env_key": "MINIMAX_API_KEY",
        "display": "MiniMax-H3（0.50 元/秒 768P / 0.80 元/秒 2K）",
    },
    # -----------------------------------------------------------------------
    # 对象存储 / CDN 引擎（参考图永久托管，供 image_gen / video_gen 引用）
    #   bucket       : 默认桶名
    #   endpoint     : 默认 endpoint（不含 scheme）
    #   region       : 默认 region
    #   url_template : 永久 URL 模板，{bucket}/{endpoint}/{key} 占位
    #   env_keys     : 鉴权环境变量列表（按优先级）
    # -----------------------------------------------------------------------
    "tos": {
        "capability": CAP_STORAGE,
        "cli": "mcps/volc-ark/scripts/tos_upload.py",
        "mcp_server": "volc-ark",
        "mcp_prefix": "tos",
        "archive_kind": "tos_upload",
        "env_key": "VOLC_ACCESS_KEY",
        "env_keys": ["VOLC_ACCESS_KEY", "VOLC_SECRET_KEY"],
        "bucket": "drama-reference-images",
        "endpoint": "tos-cn-beijing.volces.com",
        "region": "cn-beijing",
        "url_template": "https://{bucket}.{endpoint}/{key}",
        "display": "火山引擎 TOS 对象存储（参考图永久 CDN）",
    },
}

# ---------------------------------------------------------------------------
# 视频引擎默认参数（video_defaults）：制作参数权威源（引擎化）。agent 不硬编码
# 模型名/时长限制/采样参数，改由本表按当前 video_gen 引擎解析。segment-builder
# 构建 shots/segments YAML 的 `defaults` 块时从本表读取；制片规范中的引擎参数
# 定义以此为据。键与 YAML `defaults` 块字段一一对应。
# ---------------------------------------------------------------------------
VIDEO_DEFAULTS = {
    "seedance": {
        "model": "doubao-seedance-2-0-fast-260128",  # ⚠️ 必须带版本后缀，无后缀方舟 404
        "ratio": "9:16",
        "resolution": "720p",
        "image_resolution": "1600×2848",  # 图片生成参考图，9:16 竖屏
        "duration_sec": "8-10",
        "segment_duration_sec": "4-12",   # Seedance fast 单 segment 硬限制
        "generate_audio": True,
    },
    "kling": {
        "model": "kling-v2",
        "ratio": "9:16",
        "resolution": "720p",
        "image_resolution": "1600×2848",
        "duration_sec": "5-10",
        "segment_duration_sec": "5-10",
        "generate_audio": False,
    },
    "minimax": {
        "model": "MiniMax-H3",
        "ratio": "9:16",
        "resolution": "768P",
        "image_resolution": "1600×2848",
        "duration_sec": "4-15",
        "segment_duration_sec": "4-15",
        "generate_audio": True,  # H3 原生输出音轨，无需外部 TTS 混音
    },
}

# 能力 -> 默认引擎（环境变量可覆盖）
DEFAULT_ENGINES = {
    CAP_IMAGE_GEN: "gpt-image",
    CAP_VIDEO_GEN: "minimax",  # 2026-08-07 切换：MiniMax-H3（metaso）为默认出片引擎；seedance/kling 保留候选（VIDEO_GEN_ENGINE 可切换）
    CAP_STORAGE: "tos",
}

# 环境变量名（能力 -> 覆盖该能力默认引擎的 env var）
_CAP_ENV = {
    CAP_IMAGE_GEN: "IMAGE_GEN_ENGINE",
    CAP_VIDEO_GEN: "VIDEO_GEN_ENGINE",
    CAP_STORAGE: "STORAGE_ENGINE",
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


def storage_info() -> dict:
    """返回当前对象存储引擎的完整元数据（含解析后的绝对 CLI 路径）。"""
    return resolve(CAP_STORAGE)


def storage_url(key: str) -> str:
    """按当前存储引擎的 url_template 拼出某 object key 的永久 CDN URL。"""
    info = storage_info()
    return info["url_template"].format(
        bucket=info["bucket"], endpoint=info["endpoint"], key=key
    )


def video_defaults(engine_id: str | None = None) -> dict:
    """返回视频引擎的默认参数（model/时长限制/generate_audio 等）。

    不传 engine_id 时解析当前 video_gen 默认引擎。segment-builder 构建
    shots/segments YAML 的 `defaults` 块时读取；也是制片规范引擎参数定义的依据。
    """
    eid = engine_id or default_engine(CAP_VIDEO_GEN)
    if eid not in VIDEO_DEFAULTS:
        raise ValueError(
            f"视频引擎 {eid!r} 无默认参数；已配置: {sorted(VIDEO_DEFAULTS)}"
        )
    return dict(VIDEO_DEFAULTS[eid])


# 合法宽高比白名单（字符串形式）。YAML 1.1 会把无引号 `9:16` 按六十进制
# 解析成 int（9*60+16=556），导致请求体 ratio=556 被引擎 HTTP 400 拒绝。
# 本函数在解析端统一兜底：int 还原、str 规范化、非法值回退默认。
VALID_RATIOS = {"9:16", "16:9", "1:1", "4:3", "3:4", "3:2", "2:3", "21:9", "auto"}

# 六十进制 int → 标准 ratio 字符串的还原映射（PyYAML sexagesimal 解析产物）
_SEXAGESIMAL_TO_RATIO = {
    556: "9:16",   # 9*60+16
    976: "16:9",   # 16*60+9
    61: "1:1",     # 1*60+1
    243: "4:3",    # 4*60+3
    183: "3:4",    # 3*60+4
    182: "3:2",    # 3*60+2
    122: "2:3",    # 2*60+3
    1269: "21:9",  # 21*60+9
}


def normalize_ratio(value, default: str = "9:16") -> str:
    """把 YAML/参数解析后的 ratio 归一化为合法字符串，解析端统一兜底。

    处理三类输入：
      - int（YAML 1.1 无引号 `9:16` 被六十进制解析成 556）→ 还原为 "9:16"
      - str（"9:16" / " 9:16 " / 带空白）→ strip 后校验白名单
      - 其他/非法值 → 回退 default

    所有视频引擎 CLI 在构造请求体前必须调用本函数，不得直接透传
    `defaults.get("ratio")`（可能携带 int 556 导致引擎 HTTP 400）。
    """
    if isinstance(value, bool):  # bool 是 int 子类，先排除
        return default
    if isinstance(value, int):
        return _SEXAGESIMAL_TO_RATIO.get(value, default)
    if isinstance(value, float):  # 兜底：9.16 之类非法浮点
        return default
    if isinstance(value, str):
        r = value.strip()
        if r in VALID_RATIOS:
            return r
        # 尝试把 "556" 这类数字字符串也还原
        if r.isdigit():
            return _SEXAGESIMAL_TO_RATIO.get(int(r), default)
        return default
    return default


if __name__ == "__main__":
    import json

    out = {
        cap: {
            "default_engine": default_engine(cap),
            "available": engines_for(cap),
            "resolved": resolve(cap),
        }
        for cap in (CAP_IMAGE_GEN, CAP_VIDEO_GEN, CAP_STORAGE)
    }
    out["video_defaults"] = video_defaults()
    out["storage_url_example"] = storage_url("looks/<剧名>/CHAR-001-L01.png")
    print(json.dumps(out, ensure_ascii=False, indent=2))
