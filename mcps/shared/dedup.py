#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""内容指纹 + 本地/远程对账 + submitting 卡位（防重复扣费）。

为什么需要这一层（根因见 AGENTS.md 事故复盘）：
- 视频 Seedance 是异步任务，POST 建单后无法取消；agent "以为 cancel 成功" 仍计费。
- 提交后归档写入是"先 POST 后落盘"，网络抖动会导致方舟已扣费但本地无记录 → agent 重发 = 双倍扣费。
- 图片 Seedream 是同步 API，无历史列表端点，无法远程对账，只能本地指纹+output 文件兜底。

设计原则：
- CLI 层强制锁死，不靠 agent 自觉（无论走 CLI 还是 MCP，都走同一批 python 脚本）。
- 指纹覆盖"内容"，prompt/参考图/参数任一变化才视作新提交，原样重跑被拦。
- 视频：本地归档 + 远程近 7 天任务双查；图片：本地归档 + output 文件存在双查。
- submitting 占位（带 client_request_id）在 POST 之前落盘，下次对账发现卡位未更新 → 视频
  走远程幂等回写、图片不自动重发而是拒发并提示人工。"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

# 注：远程对账的方舟任务列表由 ark_seedance_video 的 list_tasks() 直接获取后传入比对，
# 本模块不直接发 HTTP 请求（避免两套鉴权/路径逻辑）。

# 复用现有归档模块
from project_task_archive import (
    KIND_SEEDANCE,
    add_task,
    archive_file,
    load_doc,
    save_doc,
)

# 与 ark_common / ark_seedance_video 保持一致的默认 base
# 视频任务模型默认值，回退用（避免 hard import ark_common 造成循环依赖）
DEFAULT_VIDEO_MODEL = "doubao-seedance-2-0-fast-260128"

# submitting 卡位的"过期"阈值（秒）：超过则视为提交时网络中断、API 可能已建单
SUBMITTING_STALE_SEC = 600


def _norm(s: Any) -> str:
    return "" if s is None else str(s).strip()


def _hash(*parts: str) -> str:
    """稳定短指纹（sha256 前 16 hex）。parts 之间用单元分隔符避免歧义。"""
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8", "ignore"))
        h.update(b"\x1f")  # unit separator
    return h.hexdigest()[:16]


def _sorted_urls(urls: Any) -> list[str]:
    if not urls:
        return []
    if isinstance(urls, str):
        urls = [urls]
    return sorted({u for u in (_norm(x) for x in urls) if u})


# ---------------------------------------------------------------------------
# 指纹
# ---------------------------------------------------------------------------

def fingerprint_image(
    prompt: str,
    *,
    size: str | None = None,
    ratio: str | None = None,
    image_urls: list[str] | None = None,
) -> str:
    """图片内容指纹：prompt + 尺寸 + 比例 + 排序后的参考图。"""
    return _hash(
        _norm(prompt),
        _norm(size),
        _norm(ratio),
        "\x1e".join(_sorted_urls(image_urls)),  # record separator
    )


def fingerprint_video(
    *,
    prompt: str = "",
    model: str | None = None,
    duration: Any = None,
    ratio: str | None = None,
    resolution: str | None = None,
    media_urls: list[str] | None = None,
) -> str:
    """视频内容指纹：prompt + model + 时长 + 比例 + 分辨率 + 排序后的素材图。

    用于远程对账——远程任务不携带我们的 segment_id/shot_id，只能靠"提交请求内容"
    比对，所以包含 prompt 文本本身。"""
    return _hash(
        _norm(prompt),
        _norm(model),
        _norm(duration),
        _norm(ratio),
        _norm(resolution),
        "\x1e".join(_sorted_urls(media_urls)),
    )


def video_text_from_segment(seg: dict) -> str:
    """从 segment 字典里抽出 text prompt。

    兼容两种 schema：
    - 真实 schema：text 在 seg.api.text（content_roles 之上）
    - 已构 body 的 segment（如从 build 出来的 content 列表）：content[*].text
    """
    content = seg.get("content") or []
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(str(item.get("text") or item.get("chars") or ""))
        if texts:
            return "\n".join(texts)
    api = seg.get("api") or {}
    return _norm(api.get("text") or seg.get("text") or seg.get("prompt") or "")


def video_media_urls_from_segment(seg: dict) -> list[str]:
    """从 segment 字典抽出参考图 URL。

    content_roles 用 file key 引用素材，不是 URL；但提交后会 resolve 成 TOS URL。
    远程对账时我们只能比对最终提交 body 的 url —— 故这里同步从已构 content 列表
    抽取 url；若直接是 api file key（未 resolve）则跳过（远程任务也带 url，可比对）。"""
    content = seg.get("content") or []
    urls: list[str] = []
    if isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                continue
            iu = item.get("image_url") or item.get("audio_url") or {}
            if isinstance(iu, dict):
                u = _norm(iu.get("url"))
                if u:
                    urls.append(u)
    # api.content_roles 是 file key（如 CHAR-001-L01），不是稳定的 url，
    # 远程比对不可靠；用得是 file key 的话，相同 key 列表也纳入指纹代替
    if not urls:
        api = seg.get("api") or {}
        keys = []
        for role_spec in api.get("content_roles") or []:
            if isinstance(role_spec, dict):
                fk = _norm(role_spec.get("file"))
                if fk:
                    keys.append(fk)
        if keys:
            urls = ["local:" + k for k in keys]
    # 兜底：直接字段
    for k in ("image_urls", "image_url"):
        v = seg.get(k)
        if v:
            urls.extend(_sorted_urls(v))
    return _sorted_urls(urls)


def fingerprint_segment(seg: dict, *, model: str | None = None) -> str:
    """算 segment 指纹。

    ⚠ 必须与 build_segment 在 cmd_segments/cmd_shots 里构 body 时的默认一致，
    否则同内容两次会被算出不同指纹 → 去重失效。当前 build 默认 ratio="9:16"、
    resolution="720p"，故 seg 缺这俩字段时这里也补同样默认。"""
    ratio = seg.get("ratio") or "9:16"
    resolution = seg.get("resolution") or "720p"
    return fingerprint_video(
        prompt=video_text_from_segment(seg),
        model=model or seg.get("model") or DEFAULT_VIDEO_MODEL,
        duration=seg.get("duration"),
        ratio=ratio,
        resolution=resolution,
        media_urls=video_media_urls_from_segment(seg),
    )


# ---------------------------------------------------------------------------
# 本地归档读取 / 卡位写入
# ---------------------------------------------------------------------------

def read_local_index(
    project_root: Path | str,
    *,
    kind: str,
    episode_id: str | None = None,
) -> dict[str, dict]:
    """读归档，返回 {task_id: task} 统一索引（视频按集/图片全集）。"""
    path = archive_file(project_root, kind, episode_id)
    if not path.is_file():
        return {}
    doc = load_doc(path)
    out: dict[str, dict] = {}
    for t in doc.get("tasks", []) or []:
        tid = _norm(t.get("task_id"))
        if tid:
            out[tid] = t
    return out


def find_local_by_identity(
    project_root: Path | str,
    *,
    kind: str,
    episode_id: str | None,
    identity_key: str,  # 视频 segment_id/shot_id；图片用 output 文件 stem
) -> list[dict]:
    """本地归档里同一身份 key 的所有条目（不去除 failed）。

    图片旧归档的 params.output 常是完整路径而非 stem，故对 output 既比完整路径也比 stem。"""
    idx = read_local_index(project_root, kind=kind, episode_id=episode_id)
    hits: list[dict] = []
    ik = _norm(identity_key)
    for t in idx.values():
        params = t.get("params") or {}
        seg = _norm(params.get("segment_id"))
        shot = _norm(params.get("shot_id"))
        ident = _norm(params.get("identity"))
        outp = _norm(params.get("output"))
        out_stem = _norm(Path(outp).stem) if outp else ""
        if ik and ik in (seg, shot, ident, outp, out_stem):
            hits.append(t)
    return hits


def add_submitting_placeholder(
    project_root: Path | str,
    *,
    kind: str,
    episode_id: str | None,
    client_request_id: str,
    fingerprint: str,
    identity_key: str,
    extra_params: dict | None = None,
) -> None:
    """POST 之前先落 submitting 卡位。client_request_id 即临时 task_id。

    下次对账若发现 submitting 卡位且 stale → 视频走远程幂等回写，图片拒自动重发。
    归档写入失败必须抛错（不让 agent 闷头重发）。"""
    params: dict[str, Any] = {
        "fingerprint": fingerprint,
        "client_request_id": client_request_id,
        "submit_started_at": time.time(),
        "status_hint": "submitting",
    }
    if episode_id:
        params.setdefault("episode", episode_id.upper())
    if extra_params:
        params.update(extra_params)
    # 视频用 segment_id/shot_id 身份；图片用 output stem 记 identity
    if kind == KIND_SEEDANCE:
        # 上层调用方传入 extra_params 时应带 segment_id/shot_id
        params.setdefault("segment_id", identity_key)
    else:
        params.setdefault("identity", identity_key)
    add_task(
        kind=kind,
        task_id=client_request_id,
        params=params,
        project_root=project_root,
        status="submitting",
        episode_id=episode_id,
    )


def promote_submitting(
    project_root: Path | str,
    *,
    kind: str,
    episode_id: str | None,
    client_request_id: str,
    real_task_id: str,
    extra_updates: dict | None = None,
) -> None:
    """POST 成功后把 submitting 卡位更新为 submitted + 写入真实 task_id。

    顺序：先 add submitted 条目，确认落盘后再 delete submitting 占位。
    反向（先 delete 再 add）若两步间崩溃会丢记录 → 下次对账无 record 重发扣费。
    本顺序最坏残留 submitting 卡位，下次对账仍拦下不重发（已存在 submitted 优先认领）。"""
    params: dict[str, Any] = {}
    if extra_updates:
        params.update(extra_updates)
    add_task(
        kind=kind,
        task_id=real_task_id,
        params=params,
        project_root=project_root,
        status="submitted",
        episode_id=episode_id,
    )
    _delete_task_by_id(project_root, kind=kind, episode_id=episode_id, task_id=client_request_id)


def _delete_task_by_id(
    project_root: Path | str,
    *,
    kind: str,
    episode_id: str | None,
    task_id: str,
) -> bool:
    path = archive_file(project_root, kind, episode_id)
    if not path.is_file():
        return False
    doc = load_doc(path)
    before = len(doc.get("tasks", []) or [])
    doc["tasks"] = [t for t in (doc.get("tasks", []) or []) if _norm(t.get("task_id")) != _norm(task_id)]
    if len(doc["tasks"]) == before:
        return False
    save_doc(path, doc, kind=kind, episode_id=episode_id)
    return True


def stale_submitting(task: dict) -> bool:
    """是否为 stale submitting 卡位（超过阈值未更新）。"""
    if _norm(task.get("status")) != "submitting":
        return False
    started = task.get("params", {}).get("submit_started_at")
    if not started:
        return True  # 无时间戳的 submitting 视为 stale（保守）
    try:
        return (time.time() - float(started)) > SUBMITTING_STALE_SEC
    except (TypeError, ValueError):
        return True


# ---------------------------------------------------------------------------
# 本地对账决策
# ---------------------------------------------------------------------------

def local_lookup(
    project_root: Path | str,
    *,
    kind: str,
    episode_id: str | None,
    identity_key: str,
    fingerprint: str,
) -> dict | None:
    """本地归档找已提交的同一内容。

    返回 dict 命中信息。策略（防重复优先于防漏拦）：
    - 本地无指纹的旧条目（旧脚本生成的归档）→ 身份命中即视为已提交拦下（保守）
    - 本地有指纹且与新指纹一致 → 命中拦下
    - 本地有指纹但与新指纹不同 → 改稿放行（identity_found=True，matched=False）
    - submitting 占位 → 拦下交调用方处理（视频远程回写/图片拒重发）
    非 failed/cancelled 的 status（含旧归档常用的 pending）均视为"已发"。
    """
    hits = find_local_by_identity(project_root, kind=kind, episode_id=episode_id, identity_key=identity_key)
    if not hits:
        return {
            "matched": False,
            "existing_task": None,
            "identity_found": False,
            "fingerprint_change": False,
        }
    has_fingerprint_diff = False  # 至少一条本地有指纹且与新不同
    for t in hits:
        lfp = _norm((t.get("params") or {}).get("fingerprint"))
        status = _norm(t.get("status"))
        if status in ("failed", "cancelled"):
            continue
        if status == "submitting":
            return {
                "matched": True,
                "existing_task": t,
                "identity_found": True,
                "fingerprint_change": False,
                "kind": "submitting",
                "stale": stale_submitting(t),
            }
        # 非 submitting、非 failed → 视为"已发"
        if not lfp:
            # 旧归档无指纹 → 保守拦下（防重复扣费优先）
            return {
                "matched": True,
                "existing_task": t,
                "identity_found": True,
                "fingerprint_change": False,
                "kind": "submitted",
                "no_fingerprint": True,  # 旧条目
            }
        if fingerprint and lfp == fingerprint:
            return {
                "matched": True,
                "existing_task": t,
                "identity_found": True,
                "fingerprint_change": False,
                "kind": "submitted",
            }
        if fingerprint and lfp and lfp != fingerprint:
            has_fingerprint_diff = True
    # 所有命中条目都有指纹且都≠新指纹 → 改稿放行
    return {
        "matched": False,
        "existing_task": hits[0],
        "identity_found": True,
        "fingerprint_change": has_fingerprint_diff,
    }


# ---------------------------------------------------------------------------
# 远程对账（视频；图片 API 无历史列表，不支持）

def remote_fingerprint_from_task(task: dict) -> str | None:
    """从方舟返回的任务对象重建内容指纹。list 通常不含完整 content，尽力而为。"""
    # 优先 content（GET 单查会带；list 可能精简）
    content = task.get("content")
    prompt = ""
    media: list[str] = []
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            content = None
    if isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text":
                t = item.get("text") or item.get("chars")
                if isinstance(t, str):
                    prompt = t
            elif item.get("type") in ("image_url", "audio_url"):
                u = (item.get("image_url") or item.get("audio_url") or {}).get("url")
                if isinstance(u, str):
                    media.append(u)
    # list 可能只有 prompt/text 顶层字段
    if not prompt:
        prompt = _norm(task.get("prompt") or task.get("text"))
    if not media:
        for k in ("image_urls", "image_url"):
            v = task.get(k)
            if v:
                media.extend(_sorted_urls(v))
    if not prompt and not media:
        return None
    return fingerprint_video(
        prompt=prompt,
        model=task.get("model"),
        duration=task.get("duration"),
        # 与 fingerprint_segment 同样补 default（远端 list 可能漏 ratio/resolution，
        # 否则带/不带该字段的同内容会被算成不同指纹 → 对账漏命中）
        ratio=task.get("ratio") or "9:16",
        resolution=task.get("resolution") or "720p",
        media_urls=media,
    )


def write_back_remote(
    project_root: Path | str,
    *,
    episode_id: str,
    remote_task_id: str,
    fingerprint: str,
    identity_key: str,
    extra_params: dict | None = None,
) -> None:
    """远程命中→把"丢的归档"补回本地（避免下次仍盲重发）。

    先删同身份的 submitting 占位（它就是被这次远程命中所替换的旧卡位），
    再写 submitted 条目。否则两条共存 → 下次 local_lookup 仍先撞 submitting 拦下，
    让 agent 拿到"submitting_blocked"提示去走 --force，反而诱导重发。"""
    # 删同身份 submitting 占位
    for t in find_local_by_identity(project_root, kind=KIND_SEEDANCE,
                                    episode_id=episode_id, identity_key=identity_key):
        if _norm(t.get("status")) == "submitting":
            _delete_task_by_id(project_root, kind=KIND_SEEDANCE,
                               episode_id=episode_id, task_id=_norm(t.get("task_id")))
    params: dict[str, Any] = {
        "fingerprint": fingerprint,
        "reconciled_from_remote": True,
        "segment_id": identity_key,  # 视频专用
    }
    if extra_params:
        params.update(extra_params)
    # identity 同时写 segment_id 便于本地查找
    add_task(
        kind=KIND_SEEDANCE,
        task_id=remote_task_id,
        params=params,
        project_root=project_root,
        status="submitted",
        episode_id=episode_id,
    )


def resolve_output_anywhere(outp: str | None, project_root: Path | str) -> Path | None:
    """容忍历史脏归档：尝试多种路径解析找出真实落盘文件。

    旧脚本生成的 output 常见毛病：
    - 绝对路径少了 dramas/ 一层 → 实际在 <repo>/dramas/<项目名>/...
    - 相对路径只写 `项目名/assets/...`
    故尝试：原样 / 相对 project_root / 剥项目名前缀相对 project_root / 在 ancestors 下补 dramas 再拼。
    命中即返回真实 Path，都找不到返回 None。"""
    if not outp:
        return None
    p = Path(outp)
    proot = Path(project_root).resolve()
    name = proot.name
    candidates: list[Path] = []
    if p.is_absolute():
        candidates.append(p)
        s = str(p)
        i = s.find(f"/{name}/")
        if i > 0:
            # 项目名之后的相对尾巴
            tail = (s[i + 1 + len(name):]).lstrip("/")  # "assets/looks/xxx.png"
            # 在 proot 之上的每一层祖先下补 项目名 + tail
            anc = proot.parent
            for _ in range(6):
                candidates.append(anc / name / tail)
                anc = anc.parent
                if anc == anc.parent:
                    break
        # 在 proot 下找同名文件（按文件名）
        leaf = p.name
    else:
        candidates.append(proot / p)
        if p.parts and p.parts[0] == proot.name:
            candidates.append(proot / Path(*p.parts[1:]))
        leaf = p.name
    seen: set[str] = set()
    for c in candidates:
        key = str(c)
        if key in seen:
            continue
        seen.add(key)
        if c.is_file():
            return c
    return None


# ---------------------------------------------------------------------------
# force 二次确认
# ---------------------------------------------------------------------------

def require_force_confirm(force: bool) -> tuple[bool, str]:
    """`--force` 必须同时设 ARK_ALLOW_FORCE=1 才真生效。挡 agent 随手加 --force。"""
    allow = (os.environ.get("ARK_ALLOW_FORCE") or "").strip() == "1"
    if force and not allow:
        return False, (
            "⚠️ --force 被忽略：需同时设置环境变量 ARK_ALLOW_FORCE=1 才能强制重发。"
            "（防止 agent 随手 --force 重复扣费）"
        )
    return force, ""