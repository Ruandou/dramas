#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt 渲染层（prompt renderer）：平台无关结构化 api 块 → 引擎最终 text。

背景：api.text 原为手写 Seedance 格式（【图N】+ 独立对白区块），H3 直接消费导致
锁脸声明缺失（人脸漂移）与对白/画面割裂（嘴型不同步）。本模块将引擎差异收敛在
渲染器内：YAML 只存结构化数据（subjects/shots/soundscape/music），CLI 提交时按
引擎调用 render() 生成最终 text。

- minimax（H3）  → _render_ref2va：官方 Ref2VA 六段式（subject_definitions/
  summary/retention_analysis/detailed_description/overall_soundscape/
  non_diegetic_music），character 强制 LOCK FACE，对白内嵌 <d>[中文] 于镜头句。
- seedance       → _render_legacy：旧【图N】格式（逐字等价历史手写 text）。

无结构化块（旧 YAML 仅 api.text）或引擎无渲染器时回退 api.text 原样返回。
"""
from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# 渲染分发
# ---------------------------------------------------------------------------


def render(
    engine: str,
    api: dict[str, Any],
    prompt_suffix: str | None = None,
) -> str:
    """按引擎渲染 api 结构化块；无结构化块或引擎无渲染器时回退 api.text。"""
    if not isinstance(api, dict):
        return ""
    if "subjects" not in api or "shots" not in api:
        return api.get("text", "") or ""
    fn = RENDERERS.get(engine)
    if not fn:
        return api.get("text", "") or ""
    return fn(api, prompt_suffix=prompt_suffix)


# 通用工具

_NO_SUFFIX_MARKER = "画面全程无任何文字、字幕、标题、水印。"


def _with_suffix(body: str, prompt_suffix: str | None) -> str:
    """尾部追加画面文字禁令 + 统一风格尾缀（与历史手写 text 一致）。"""
    if not body.strip():
        return body
    out = body.rstrip()
    if _NO_SUFFIX_MARKER not in out:
        out += "\n" + _NO_SUFFIX_MARKER
    if prompt_suffix and prompt_suffix.strip() not in out:
        out += "\n" + prompt_suffix.strip()
    return out


def _role_name(role: str) -> str:
    return {
        "character": "character",
        "scene": "scene",
        "prop": "object",
    }.get(role, role)


def _is_male(subject: dict[str, Any]) -> bool:
    return str(subject.get("gender") or "").strip().lower() in ("male", "男")


# ---------------------------------------------------------------------------
# MiniMax-H3：Ref2VA 六段式
# ---------------------------------------------------------------------------


def _render_ref2va(api: dict[str, Any], prompt_suffix: str | None = None) -> str:
    subjects = api.get("subjects") or []
    shots = api.get("shots") or []
    if not subjects or not shots:
        return api.get("text", "") or ""

    # 编号映射：subject id / file → <Subject N>；file 同时映射 <Picture N>
    sub_by_id: dict[str, dict[str, Any]] = {}
    sub_by_name: dict[str, dict[str, Any]] = {}  # 角色名 → subject（兼容迁移产物 speaker 用角色名）
    enhanced: list[dict[str, Any]] = []
    for i, s in enumerate(subjects, 1):
        s = dict(s)
        s["_no"] = i
        s["_tag"] = f"<Subject {i}>"
        s["_pic"] = f"<Picture {i}>"
        enhanced.append(s)
        if s.get("id"):
            sub_by_id[str(s["id"])] = s
        if s.get("file"):
            sub_by_id.setdefault(str(s["file"]), s)
        if s.get("name"):
            sub_by_name.setdefault(str(s["name"]), s)
    subjects = enhanced

    def tag_of(ref: str) -> str:
        s = sub_by_id.get(str(ref).strip()) or sub_by_name.get(str(ref).strip())
        return s["_tag"] if s else str(ref)

    def replace_refs(visual: str) -> str:
        """visual 中的素材引用替换为 <Subject N>：asset id/角色名/图号。

        顺序：asset id → 图号 → 角色名兜底（仅 character）。图号与角色名相邻时
        （「图1钱多宝」）只保留图号替换结果，角色名作为叙述文字保留，
        避免重复标签。"""
        # 第一轮：asset id（精确，无歧义）
        for ref, s in sub_by_id.items():
            if ref and ref in visual:
                visual = visual.replace(ref, s["_tag"])
        # 第二轮：图号（旧格式指代，替换后加空格防粘连）
        for s in enhanced:
            if f"图{s['_no']}" in visual:
                visual = visual.replace(f"图{s['_no']}", s["_tag"] + " ")
        # 第三轮：character 角色名兜底（仅当该角色名后不是紧跟 <Subject 标签，防重复）
        for name, s in sub_by_name.items():
            if not name or str(s.get("role")) != "character":
                continue
            tag = s["_tag"]
            # 若 visual 已含该角色的标签（图号已替换），跳过角色名替换
            if tag in visual:
                continue
            if name in visual:
                visual = visual.replace(name, tag + " ")
        return visual

    # --- subject_definitions ---
    lines: list[str] = ["subject_definitions:"]
    for s in subjects:
        role = _role_name(str(s.get("role") or ""))
        lock = ""
        if str(s.get("role")) == "character":
            lock = "LOCK HER FACE" if not _is_male(s) else "LOCK HIS FACE"
        desc = str(s.get("desc") or "").strip()
        tail = f". {desc}" if desc else ""
        if lock:
            lines.append(
                f"{s['_tag']} is {s.get('name') or s.get('id')} in {s['_pic']} "
                f"({s.get('file') or s.get('id')}): {role} reference, {lock}{tail}")
        else:
            lines.append(
                f"{s['_tag']} is {s.get('name') or s.get('id')} in {s['_pic']} "
                f"({s.get('file') or s.get('id')}): {role} reference{tail}")

    # --- summary ---
    summary = str(api.get("summary") or "").strip()
    if not summary:
        names = [str(s.get("name") or s.get("id")) for s in subjects]
        summary = f"参考图素材驱动的短视频：{'、'.join(names)}，按镜头时间线连贯叙事。"
    lines.append("")
    lines.append("summary:")
    lines.append(f"[reference generation] {summary}")

    # --- retention_analysis ---
    lines.append("")
    lines.append("retention_analysis:")
    for s in subjects:
        role = str(s.get("role") or "")
        note = "脸/发型/服装完全保留" if role == "character" else "结构与外观完全保留"
        lines.append(
            f"{s['_tag']} (appears in all shots): fully_preserved - {note}")

    # --- detailed_description ---
    lines.append("")
    lines.append("detailed_description:")
    # 说话人 (Sx) 按首次发声顺序分配
    speaker_ids: dict[str, int] = {}
    n_speaker = 0
    for sh in shots:
        shot_no = sh.get("shot_no", "")
        dur = sh.get("duration_sec", "")
        shot_type = str(sh.get("shot_type") or "中景")
        camera = str(sh.get("camera") or "固定镜头")
        visual = str(sh.get("visual") or "").strip()
        # visual 中的 subject 引用替换为 <Subject N>
        visual = replace_refs(visual)
        parts = [f"镜头{shot_no}（{dur}秒）{shot_type} {camera}：{visual}"]
        speakers = sh.get("speakers") or []
        for sp in speakers:
            sub_ref = str(sp.get("subject") or "").strip()
            tag = tag_of(sub_ref) if sub_ref else ""
            if sub_ref not in speaker_ids:
                n_speaker += 1
                speaker_ids[sub_ref] = n_speaker
            sx = f"(S{speaker_ids[sub_ref]})"
            voice = str(sp.get("voice") or "").strip()
            dialogue = str(sp.get("dialogue") or "").strip()
            voice_part = f"以{voice}说道" if voice else "说道"
            if tag:
                parts.append(f"{tag} {sx} {voice_part}，<d>[中文] {dialogue}</d>，说完闭唇。")
            else:
                parts.append(f"{sx} {voice_part}，<d>[中文] {dialogue}</d>，说完闭唇。")
        lines.append(" ".join(parts))

    # --- overall_soundscape / non_diegetic_music ---
    soundscape = str(api.get("soundscape") or "").strip()
    music = str(api.get("music") or "").strip()
    lines.append("")
    lines.append("overall_soundscape:")
    lines.append(soundscape if soundscape else "环境音贯穿。")
    lines.append("")
    lines.append("non_diegetic_music:")
    lines.append(music if music else "N/A")

    return _with_suffix("\n".join(lines), prompt_suffix)


# ---------------------------------------------------------------------------
# Seedance：旧【图N】格式
# ---------------------------------------------------------------------------


def _render_legacy(api: dict[str, Any], prompt_suffix: str | None = None) -> str:
    """结构化块 → 旧格式（【图N】声明 + 角色分工 + 镜头 + 对白区块）。

    与历史手写 api.text 逐字等价（P2 迁移后 Seedance 路径可复现）。"""
    subjects = api.get("subjects") or []
    shots = api.get("shots") or []
    if not subjects or not shots:
        return api.get("text", "") or ""

    sub_by_id: dict[str, dict[str, Any]] = {}
    enhanced: list[dict[str, Any]] = []
    for i, s in enumerate(subjects, 1):
        s = dict(s)
        s["_no"] = i
        enhanced.append(s)
        if s.get("id"):
            sub_by_id[str(s["id"])] = s
        if s.get("file"):
            sub_by_id.setdefault(str(s["file"]), s)
    subjects = enhanced

    lines: list[str] = []
    # 【图N】头部声明
    heads: list[str] = []
    for s in subjects:
        no = s["_no"]
        name = s.get("name") or s.get("id")
        fid = s.get("file") or s.get("id")
        desc = str(s.get("desc") or "").strip()
        heads.append(f"【图{no}】{name} {fid}（{desc}）" if desc else f"【图{no}】{name} {fid}")
    lines.append("".join(heads) + "。")

    # 角色分工（character 互动提示）
    chars = [s for s in subjects if str(s.get("role")) == "character"]
    if len(chars) >= 1:
        parts = [f"仅图{s['_no']}可执行动作" for s in chars]
        lines.append("角色分工：" + "；".join(parts) + "。")

    lines.append("竖屏9比16连贯叙事。")
    for sh in shots:
        shot_no = sh.get("shot_no", "")
        dur = sh.get("duration_sec", "")
        shot_type = str(sh.get("shot_type") or "中景")
        camera = str(sh.get("camera") or "固定镜头")
        visual = str(sh.get("visual") or "").strip()
        for ref, s in sub_by_id.items():
            if ref and ref in visual:
                visual = visual.replace(ref, f"图{s['_no']}")
        lines.append(f"镜头{shot_no}（{dur}秒）{shot_type} {camera}：{visual}")

    # 对白区块
    all_dialogues: list[tuple[str, str, str]] = []  # (subject_ref, voice, dialogue)
    for sh in shots:
        for sp in sh.get("speakers") or []:
            sub_ref = str(sp.get("subject") or "").strip()
            voice = str(sp.get("voice") or "").strip()
            dialogue = str(sp.get("dialogue") or "").strip()
            all_dialogues.append((sub_ref, voice, dialogue))
    if all_dialogues:
        lines.append("[以下对白仅供语音合成，严禁在画面中显示任何文字]")
        for sub_ref, voice, dialogue in all_dialogues:
            s = sub_by_id.get(sub_ref)
            name = s.get("name") if s else sub_ref
            lines.append(f"对白（{name}，{voice}）：「{dialogue}」")

    return _with_suffix("\n".join(lines), prompt_suffix)


# ---------------------------------------------------------------------------
# 渲染分发表（置于渲染器定义之后）
# ---------------------------------------------------------------------------

RENDERERS: dict[str, Any] = {
    "minimax": _render_ref2va,
    "seedance": _render_legacy,
}
