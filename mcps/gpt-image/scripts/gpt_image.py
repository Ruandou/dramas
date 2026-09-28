#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI 兼容中转 · gpt-image-2 文生图/图生图 CLI

文档：https://zrlef1mcfh.apifox.cn/1（OpenAI 兼容协议，base_url 需带 /v1/ 后缀）
接口：
  - 文生图：POST {base}/v1/images/generations（JSON）
  - 图生图：POST {base}/v1/images/edits（multipart/form-data，参考图真正生效）
API 地址：https://cn.getgoapi.com（国内节点，控制台可查）

鉴权：Authorization: Bearer <API_KEY>
环境变量：
  GPT_IMAGE_API_KEY（必填，兼容回退 OPENAI_API_KEY）
  GPT_IMAGE_BASE_URL（默认 https://cn.getgoapi.com，兼容回退 OPENAI_BASE_URL）
  GPT_IMAGE_MODEL（默认 gpt-image-2）
  GPT_IMAGE_QUALITY（low / medium / high / auto，默认 auto）
  GPT_IMAGE_SIZE_TIER（standard / 2k / 4k，默认 standard）

尺寸约束（gpt-image-2）：
  - 边长必须为 16 的倍数，最大边长 ≤ 3840px
  - 长边/短边 ≤ 3:1，总像素 655,360 ~ 8,294,400
  - 常用：1024x1024 / 1536x1024 / 1024x1536 / 2048x2048 / 2048x1152 /
    3840x2160 / 2160x3840 / auto

CLI：
  python3 gpt_image.py generate --prompt "..." --output out.png
  python3 gpt_image.py batch --yaml assets/looks/gpt_image_batch.yaml
  python3 gpt_image.py batch --yaml ... --dry-run --ids CHAR-001-L01
"""
from __future__ import annotations

import argparse
import base64
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

# 公共基建层 mcps/shared（本项目脚本从 mcps/shared/ 直接运行时无需此段）
_SHARED_DIR = Path(__file__).resolve().parents[2] / "shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from archive import add_task, get_archive_base
from media_utils import resolve_image_url
from cdn_registry import update_cdn_urls_json
import dedup
from project_task_archive import KIND_GPT_IMAGE, assert_valid_drama_project_root
import uuid

DEFAULT_BASE = "https://cn.getgoapi.com"
IMAGES_PATH = "/v1/images/generations"
EDITS_PATH = "/v1/images/edits"
DEFAULT_MODEL = "gpt-image-2"
MAX_REF_IMAGES = 16  # 参考图上限（gpt-image-2 官方限制）

# 按比例/档位预置尺寸（满足 16 倍数、像素区间约束）
SIZE_BY_TIER = {
    "standard": {
        "1:1": "1024x1024",
        "16:9": "1536x1024",
        "9:16": "1024x1536",
        "4:3": "1280x960",
        "3:4": "960x1280",
    },
    "2k": {
        "1:1": "2048x2048",
        "16:9": "2048x1152",
        "9:16": "1152x2048",
        "4:3": "2048x1536",
        "3:4": "1536x2048",
    },
    "4k": {
        "1:1": "2880x2880",
        "16:9": "3840x2160",
        "9:16": "2160x3840",
        "4:3": "3264x2448",
        "3:4": "2448x3264",
    },
}

IMAGE_URL_RE = re.compile(
    r"!\[[^\]]*\]\((https://[^)\s]+)\)|"
    r'"(?:url|image_url|download_url)"\s*:\s*"(https://[^"]+)"|'
    r"(https://[^\s\"')]+\.(?:png|jpeg|jpg|webp)(?:\?[^\s\"')]*)?)",
    re.IGNORECASE,
)


def api_key() -> str:
    return (
        os.environ.get("GPT_IMAGE_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or ""
    ).strip()


def base_url() -> str:
    return (
        os.environ.get("GPT_IMAGE_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or DEFAULT_BASE
    ).rstrip("/")


def default_model() -> str:
    return (os.environ.get("GPT_IMAGE_MODEL") or DEFAULT_MODEL).strip()


def default_quality() -> str:
    return (os.environ.get("GPT_IMAGE_QUALITY") or "auto").strip().lower()


def size_tier() -> str:
    t = (os.environ.get("GPT_IMAGE_SIZE_TIER") or "standard").strip().lower()
    return t if t in SIZE_BY_TIER else "standard"


def resolve_size(ratio: str | None, size: str | None, tier: str | None = None) -> str:
    if size and "x" in size.lower():
        return size.lower().replace("×", "x")
    r = (ratio or "9:16").strip()
    t = (tier or size_tier()).lower()
    if size and size.upper() in ("STANDARD", "2K", "4K"):
        t = size.lower()  # --size 2k 等价 --tier 2k
    preset = SIZE_BY_TIER.get(t, SIZE_BY_TIER["standard"])
    if r in preset:
        return preset[r]


def build_payload(
    prompt: str,
    *,
    model: str | None = None,
    size: str | None = None,
    ratio: str | None = None,
    tier: str | None = None,
    quality: str | None = None,
    image_urls: list[str] | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """构造 POST /v1/images/generations 请求体（OpenAI 兼容 JSON）。"""
    body: dict[str, Any] = {
        "model": model or default_model(),
        "prompt": prompt,
        "size": resolve_size(ratio, size, tier),
    }
    # response_format 默认 url（兼容旧版）；部分中转渠道不支持该参数，
    # 设 GPT_IMAGE_RESPONSE_FORMAT=none 时省略（gpt-image-2 原生返回 b64_json）。
    _rf = (os.environ.get("GPT_IMAGE_RESPONSE_FORMAT") or "url").strip().lower()
    if _rf and _rf != "none":
        body["response_format"] = _rf
    q = (quality or default_quality()).strip().lower()
    if q and q != "auto":
        body["quality"] = q
    if image_urls:
        urls = image_urls[:MAX_REF_IMAGES]
        if len(image_urls) > MAX_REF_IMAGES:
            print(
                f"⚠️ 参考图超过 {MAX_REF_IMAGES} 张，仅取前 {MAX_REF_IMAGES} 张",
                file=sys.stderr,
            )
        resolved = [resolve_image_url(u, project_root) for u in urls]
        _ref_field = (os.environ.get("GPT_IMAGE_REF_FIELD") or "input_image").strip()  # 默认 input_image（GetGoAPI 中转站实测，image 会被拒 400）；换 OpenAI 官方兼容站可设 GPT_IMAGE_REF_FIELD=image
        body[_ref_field] = resolved  # 参考图字段名
    return body


def http_post_json(url: str, key: str, payload: dict[str, Any], timeout: int = 600) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw_bytes = resp.read()
            # gzip 解压（GetGoAPI 大响应强制 gzip）
            if raw_bytes[:2] == b"\x1f\x8b":
                raw_bytes = gzip.decompress(raw_bytes)
            raw = raw_bytes.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        detail = ""
        if e.fp:
            err_bytes = e.fp.read()
            if err_bytes[:2] == b"\x1f\x8b":
                err_bytes = gzip.decompress(err_bytes)
            detail = err_bytes.decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {detail or e.reason}") from e
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"响应非 JSON: {raw[:500]}") from e


def http_post_multipart(
    url: str,
    key: str,
    fields: dict[str, str],
    files: list[tuple[str, str, bytes, str]],
    timeout: int = 600,
) -> dict[str, Any]:
    """multipart/form-data POST（用于 /v1/images/edits 图生图）。

    fields: 文本字段 {"model": "gpt-image-2", "prompt": "...", ...}
    files: [(field_name, filename, data_bytes, content_type), ...]
    """
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex[:16]}"
    body = io.BytesIO()

    # 文本字段
    for name, value in fields.items():
        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.write(f"{value}\r\n".encode())

    # 文件字段
    for field_name, filename, data, content_type in files:
        body.write(f"--{boundary}\r\n".encode())
        body.write(
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode()
        )
        body.write(f"Content-Type: {content_type}\r\n\r\n".encode())
        body.write(data)
        body.write(b"\r\n")

    body.write(f"--{boundary}--\r\n".encode())
    body_bytes = body.getvalue()

    req = urllib.request.Request(
        url,
        data=body_bytes,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw_bytes = resp.read()
            if raw_bytes[:2] == b"\x1f\x8b":
                raw_bytes = gzip.decompress(raw_bytes)
            raw = raw_bytes.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        detail = ""
        if e.fp:
            err_bytes = e.fp.read()
            if err_bytes[:2] == b"\x1f\x8b":
                err_bytes = gzip.decompress(err_bytes)
            detail = err_bytes.decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {detail or e.reason}") from e
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"响应非 JSON: {raw[:500]}") from e


def extract_image_urls(payload: Any) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()

    def add(u: str) -> None:
        u = u.strip()
        if u.startswith("http") and u not in seen:
            seen.add(u)
            urls.append(u)

    def walk(obj: Any) -> None:
        if isinstance(obj, str):
            for m in IMAGE_URL_RE.finditer(obj):
                for g in m.groups():
                    if g:
                        add(g)
        elif isinstance(obj, dict):
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(payload)
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        for item in payload["data"]:
            if isinstance(item, dict) and isinstance(item.get("url"), str):
                add(item["url"])
    return urls


def extract_b64_images(payload: Any) -> list[str]:
    """gpt-image-2 默认返回 b64_json；response_format=url 时无此项，作兜底。"""
    b64s: list[str] = []
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        for item in payload["data"]:
            if isinstance(item, dict) and isinstance(item.get("b64_json"), str):
                b64s.append(item["b64_json"])
    return b64s


def save_image_bytes(data: bytes, dest: Path) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return {"path": str(dest.resolve()), "bytes": len(data)}


def download_file(url: str, dest: Path) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "gpt-image-cli/1.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = resp.read()
    return save_image_bytes(data, dest)


def generate_one(
    prompt: str,
    output: Path | None,
    *,
    model: str | None = None,
    size: str | None = None,
    ratio: str | None = None,
    tier: str | None = None,
    quality: str | None = None,
    image_urls: list[str] | None = None,
    dry_run: bool = False,
    index: int = 0,
    project_root: Path | None = None,
) -> dict[str, Any]:
    key = api_key()
    if not key and not dry_run:
        return {"error": "未设置 GPT_IMAGE_API_KEY 或 OPENAI_API_KEY"}

    payload = build_payload(
        prompt,
        model=model,
        size=size,
        ratio=ratio,
        tier=tier,
        quality=quality,
        image_urls=image_urls,
        project_root=project_root,
    )

    if dry_run:
        return {
            "status": "dry_run",
            "endpoint": base_url() + IMAGES_PATH,
            "payload": payload,
            "output": str(output) if output else None,
            "archive_dir": str(get_archive_base()),
        }

    # 指纹 + submitting 卡位（图片 API 无历史列表，提交后网络中断无远程对账兜底，
    # 卡位让下次对账发现"提交状态不明"→ 拒自动重发避免双倍扣费）
    fp = dedup.fingerprint_image(
        prompt, size=payload.get("size"), ratio=ratio, image_urls=image_urls,
    )
    identity_key = output.stem if output else ""
    client_request_id = f"local-{uuid.uuid4()}"
    placeholder_ok = False
    if project_root and identity_key:
        try:
            os.environ.setdefault("DRAMA_PROJECT_ROOT", str(Path(project_root).resolve()))
            dedup.add_submitting_placeholder(
                project_root,
                kind=KIND_GPT_IMAGE,
                episode_id=None,
                client_request_id=client_request_id,
                fingerprint=fp,
                identity_key=identity_key,
                extra_params={
                    "prompt": prompt[:500],
                    "model": payload.get("model"),
                    "size": payload.get("size"),
                    "output": str(output) if output else None,
                },
            )
            placeholder_ok = True
        except Exception as e:
            print(
                f"⚠️ 归档写卡位失败但即将继续 POST，中转站可能已扣费：{e}",
                file=sys.stderr,
            )

    t0 = time.time()
    try:
        resp = http_post_json(base_url() + IMAGES_PATH, key, payload)
    except Exception as e:
        # POST 失败/超时：可能已扣费但本地拿不到响应
        if placeholder_ok:
            print(
                "⚠️ 图片提交状态不明，可能已扣费但本地无法对账（gpt-image-2 无历史列表 API）。"
                "不自动重发。如确认原请求真没发出，用 --force + ARK_ALLOW_FORCE=1 重发。",
                file=sys.stderr,
            )
            return {
                "error": "post_failed",
                "detail": str(e),
                "pending_placeholder": client_request_id,
                "fingerprint": fp,
            }
        return {"error": "post_failed", "detail": str(e)}

    urls = extract_image_urls(resp)
    b64s = extract_b64_images(resp) if not urls else []
    if not urls and not b64s:
        return {
            "error": "响应中未解析到图片（无 url 也无 b64_json）",
            "response_id": resp.get("id"),
            "raw_preview": json.dumps(resp, ensure_ascii=False)[:2000],
        }

    rid = resp.get("id") or resp.get("created")
    if rid:
        if project_root:
            os.environ.setdefault("DRAMA_PROJECT_ROOT", str(Path(project_root).resolve()))
        if placeholder_ok:
            try:
                dedup.promote_submitting(
                    project_root,
                    kind=KIND_GPT_IMAGE,
                    episode_id=None,
                    client_request_id=client_request_id,
                    real_task_id=str(rid),
                    extra_updates={
                        "prompt": prompt[:500],
                        "model": payload.get("model"),
                        "size": payload.get("size"),
                        "has_ref_images": bool(image_urls),
                        "output": str(output) if output else None,
                        "cdn_url": urls[0] if urls else None,
                        "identity": identity_key,
                        "fingerprint": fp,
                    },
                )
            except Exception:
                add_task(
                    KIND_GPT_IMAGE,
                    str(rid),
                    {
                        "prompt": prompt[:500],
                        "model": payload.get("model"),
                        "size": payload.get("size"),
                        "has_ref_images": bool(image_urls),
                        "output": str(output) if output else None,
                        "cdn_url": urls[0] if urls else None,
                        "identity": identity_key,
                        "fingerprint": fp,
                    },
                    status=str(resp.get("status") or "completed"),
                )
        else:
            add_task(
                KIND_GPT_IMAGE,
                str(rid),
                {
                    "prompt": prompt[:500],
                    "model": payload.get("model"),
                    "size": payload.get("size"),
                    "has_ref_images": bool(image_urls),
                    "output": str(output) if output else None,
                    "cdn_url": urls[0] if urls else None,
                    "identity": identity_key,
                    "fingerprint": fp,
                },
                status=str(resp.get("status") or "completed"),
            )

    pick_url = urls[min(index, len(urls) - 1)] if urls else None
    result: dict[str, Any] = {
        "status": "ok",
        "model": payload["model"],
        "size": payload["size"],
        "image_url": pick_url,
        "all_urls": urls,
        "response_id": rid,
        "elapsed_sec": round(time.time() - t0, 2),
        "usage": resp.get("usage"),
        "archive_dir": str(get_archive_base()),
    }

    if output:
        if pick_url:
            result["saved"] = download_file(pick_url, output)
        elif b64s:
            raw = base64.b64decode(b64s[min(index, len(b64s) - 1)])
            result["saved"] = save_image_bytes(raw, output)
        # Auto-update cdn_urls.json for looks/scenes assets
        if pick_url:
            cdn_json = update_cdn_urls_json(
                output,
                cdn_url=pick_url,
                task_id=str(rid) if rid else None,
                model=payload.get("model"),
                size=payload.get("size"),
                project_root=project_root,
            )
            if cdn_json:
                result["cdn_urls_json"] = str(cdn_json)
    return result


def _download_to_bytes(url_or_path: str, project_root: Path | None = None) -> tuple[bytes, str]:
    """下载或读取参考图，返回 (bytes, filename)。"""
    from urllib.parse import quote, urlsplit, urlunsplit
    s = url_or_path.strip()
    if s.startswith(("http://", "https://")):
        # URL 中非 ASCII 字符（中文等）需要 percent-encode
        parts = urlsplit(s)
        encoded_path = quote(parts.path, safe="/")
        encoded_url = urlunsplit((parts.scheme, parts.netloc, encoded_path, parts.query, parts.fragment))
        req = urllib.request.Request(encoded_url, headers={"User-Agent": "gpt-image-cli/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        # 从 URL 提取文件名
        fname = s.split("/")[-1].split("?")[0] or "ref.png"
        return data, fname
    # 本地路径
    p = Path(s).expanduser()
    if not p.is_absolute() and project_root is not None:
        p = project_root / p
    p = p.resolve()
    if not p.is_file():
        raise FileNotFoundError(f"参考图不存在: {p}")
    return p.read_bytes(), p.name


def _guess_content_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "png"
    return {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
    }.get(ext, "image/png")


def edit_one(
    prompt: str,
    output: Path | None,
    *,
    model: str | None = None,
    size: str | None = None,
    ratio: str | None = None,
    tier: str | None = None,
    quality: str | None = None,
    image_urls: list[str] | None = None,
    dry_run: bool = False,
    index: int = 0,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """图生图：POST /v1/images/edits（multipart/form-data）。

    参考图通过 multipart 文件上传，真正传入模型（image_tokens > 0）。
    与 generate_one（generations 端点，input_image 被静默忽略）不同。
    """
    key = api_key()
    if not key and not dry_run:
        return {"error": "未设置 GPT_IMAGE_API_KEY 或 OPENAI_API_KEY"}

    if not image_urls:
        return {"error": "edit 模式必须提供至少 1 张参考图（--image-url）"}

    # 下载/读取参考图
    ref_files: list[tuple[str, str, bytes, str]] = []
    for u in image_urls[:MAX_REF_IMAGES]:
        data, fname = _download_to_bytes(u, project_root)
        ct = _guess_content_type(fname)
        ref_files.append(("image[]", fname, data, ct))

    resolved_size = resolve_size(ratio, size, tier)
    edit_model = model or default_model()
    # edits 端点模型名不带 openai/ 前缀
    if edit_model.startswith("openai/"):
        edit_model = edit_model.split("/", 1)[1]

    fields: dict[str, str] = {
        "model": edit_model,
        "prompt": prompt,
    }
    if resolved_size:
        fields["size"] = resolved_size
    q = (quality or default_quality()).strip().lower()
    if q and q != "auto":
        fields["quality"] = q

    if dry_run:
        return {
            "status": "dry_run",
            "endpoint": base_url() + EDITS_PATH,
            "method": "multipart/form-data",
            "fields": fields,
            "ref_files": [{"filename": f[1], "size_bytes": len(f[2]), "content_type": f[3]} for f in ref_files],
            "output": str(output) if output else None,
        }

    # 指纹 + submitting 卡位
    fp = dedup.fingerprint_image(
        prompt, size=resolved_size, ratio=ratio, image_urls=image_urls,
    )
    identity_key = output.stem if output else ""
    client_request_id = f"local-{uuid.uuid4()}"
    placeholder_ok = False
    if project_root and identity_key:
        try:
            os.environ.setdefault("DRAMA_PROJECT_ROOT", str(Path(project_root).resolve()))
            dedup.add_submitting_placeholder(
                project_root,
                kind=KIND_GPT_IMAGE,
                episode_id=None,
                client_request_id=client_request_id,
                fingerprint=fp,
                identity_key=identity_key,
                extra_params={
                    "prompt": prompt[:500],
                    "model": edit_model,
                    "size": resolved_size,
                    "output": str(output) if output else None,
                    "endpoint": "edits",
                },
            )
            placeholder_ok = True
        except Exception as e:
            print(
                f"⚠️ 归档写卡位失败但即将继续 POST，中转站可能已扣费：{e}",
                file=sys.stderr,
            )

    t0 = time.time()
    try:
        resp = http_post_multipart(
            base_url() + EDITS_PATH, key, fields, ref_files,
        )
    except Exception as e:
        if placeholder_ok:
            print(
                "⚠️ 图片提交状态不明，可能已扣费但本地无法对账。"
                "不自动重发。如确认原请求真没发出，用 --force + ARK_ALLOW_FORCE=1 重发。",
                file=sys.stderr,
            )
            return {
                "error": "post_failed",
                "detail": str(e),
                "pending_placeholder": client_request_id,
                "fingerprint": fp,
            }
        return {"error": "post_failed", "detail": str(e)}

    urls = extract_image_urls(resp)
    b64s = extract_b64_images(resp) if not urls else []
    if not urls and not b64s:
        return {
            "error": "响应中未解析到图片（无 url 也无 b64_json）",
            "response_id": resp.get("id"),
            "raw_preview": json.dumps(resp, ensure_ascii=False)[:2000],
        }

    rid = resp.get("id") or resp.get("created")
    if rid and project_root:
        os.environ.setdefault("DRAMA_PROJECT_ROOT", str(Path(project_root).resolve()))
        if placeholder_ok:
            try:
                dedup.promote_submitting(
                    project_root,
                    kind=KIND_GPT_IMAGE,
                    episode_id=None,
                    client_request_id=client_request_id,
                    real_task_id=str(rid),
                    extra_updates={
                        "prompt": prompt[:500],
                        "model": edit_model,
                        "size": resolved_size,
                        "has_ref_images": True,
                        "output": str(output) if output else None,
                        "cdn_url": urls[0] if urls else None,
                        "identity": identity_key,
                        "fingerprint": fp,
                        "endpoint": "edits",
                    },
                )
            except Exception:
                add_task(
                    KIND_GPT_IMAGE,
                    str(rid),
                    {
                        "prompt": prompt[:500],
                        "model": edit_model,
                        "size": resolved_size,
                        "has_ref_images": True,
                        "output": str(output) if output else None,
                        "cdn_url": urls[0] if urls else None,
                        "identity": identity_key,
                        "fingerprint": fp,
                        "endpoint": "edits",
                    },
                    status=str(resp.get("status") or "completed"),
                )
        else:
            add_task(
                KIND_GPT_IMAGE,
                str(rid),
                {
                    "prompt": prompt[:500],
                    "model": edit_model,
                    "size": resolved_size,
                    "has_ref_images": True,
                    "output": str(output) if output else None,
                    "cdn_url": urls[0] if urls else None,
                    "identity": identity_key,
                    "fingerprint": fp,
                    "endpoint": "edits",
                },
                status=str(resp.get("status") or "completed"),
            )

    pick_url = urls[min(index, len(urls) - 1)] if urls else None
    result: dict[str, Any] = {
        "status": "ok",
        "model": edit_model,
        "size": resolved_size,
        "endpoint": "edits",
        "image_url": pick_url,
        "all_urls": urls,
        "response_id": rid,
        "elapsed_sec": round(time.time() - t0, 2),
        "usage": resp.get("usage"),
        "archive_dir": str(get_archive_base()),
    }

    if output:
        if pick_url:
            result["saved"] = download_file(pick_url, output)
        elif b64s:
            raw = base64.b64decode(b64s[min(index, len(b64s) - 1)])
            result["saved"] = save_image_bytes(raw, output)
        if pick_url:
            cdn_json = update_cdn_urls_json(
                output,
                cdn_url=pick_url,
                task_id=str(rid) if rid else None,
                model=edit_model,
                size=resolved_size,
                project_root=project_root,
            )
            if cdn_json:
                result["cdn_urls_json"] = str(cdn_json)
    return result


def load_batch_yaml(yaml_path: Path) -> list[dict[str, Any]]:
    if yaml is None:
        raise RuntimeError("批量模式需要 PyYAML: pip3 install pyyaml")
    doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise RuntimeError("YAML 根节点须为对象")
    items = doc.get("items") or []
    if not isinstance(items, list):
        raise RuntimeError("缺少 items 列表")
    return [x for x in items if isinstance(x, dict)]


def resolve_batch_output(item: dict[str, Any], yaml_path: Path, project_root: Path | None) -> Path:
    rel = item.get("output") or item.get("id", "out") + ".png"
    rel = str(rel).strip()
    p = Path(rel)
    if p.is_absolute():
        return p
    # 相对路径：优先相对 yaml 所在项目的 assets 父级
    root = project_root
    if root is None:
        root = yaml_path.parent
        for _ in range(5):
            if (root / "assets").is_dir() or (root / "分集剧本").is_dir():
                break
            if root.parent == root:
                break
            root = root.parent
    return (root / p).resolve()


def _norm_ratio(v: Any) -> str | None:
    """YAML 里 ratio 可能被 1.1 规则解析成六十进制整数（9:16 → 556），还原为字符串。"""
    if v is None:
        return None
    if isinstance(v, int) and not isinstance(v, bool):
        m, s = divmod(v, 60)
        if 0 < s < 60:
            return f"{m}:{s}"
    return str(v).strip()


def _dedup_check(
    *,
    output: Path | None,
    prompt: str,
    ratio: str | None,
    size: str | None,
    tier: str | None,
    image_urls: list[str] | None,
    project_root: Path | None,
    force: bool,
) -> dict[str, Any] | None:
    """图片去重前置：本地指纹命中或 output 已存在且指纹相同 → skip。

    返回 None = 放行；返回 dict = 已命中，调用方应 skip。"""
    ok_force, force_msg = dedup.require_force_confirm(force)
    if force and not ok_force:
        print(force_msg, file=sys.stderr)
        force = False
    if force:
        return None
    if project_root is None or output is None:
        if output and output.is_file():
            return {"status": "skip", "reason": "文件已存在", "output": str(output)}
        return None
    fp = dedup.fingerprint_image(
        prompt, size=size or resolve_size(ratio, size, tier), ratio=ratio, image_urls=image_urls,
    )
    identity_key = output.stem
    local = dedup.local_lookup(
        project_root, kind=KIND_GPT_IMAGE, episode_id=None,
        identity_key=identity_key, fingerprint=fp,
    )
    if local.get("matched") and local.get("kind") == "submitted":
        existing = local["existing_task"]
        return {
            "status": "skip",
            "reason": "本地指纹命中已生成",
            "existing_task_id": existing.get("task_id"),
            "cdn_url": (existing.get("params") or {}).get("cdn_url"),
            "output": str(output),
        }
    if local.get("matched") and local.get("kind") == "submitting":
        return {
            "status": "blocked",
            "reason": "本地 submitting 卡位未结算（可能已扣费，无历史列表无法远程对账）。如确认原请求未真发出，用 --force + ARK_ALLOW_FORCE=1 重发。",
            "output": str(output),
        }
    if output.is_file():
        return {"status": "skip", "reason": "文件已存在", "output": str(output)}
    return None


def cmd_generate(args: argparse.Namespace) -> int:
    out = Path(args.output).expanduser() if args.output else None
    image_urls = [u.strip() for u in (args.image_url or []) if u.strip()]
    try:
        project_root = (
            assert_valid_drama_project_root(args.project_root) if args.project_root else None
        )
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    hit = _dedup_check(
        output=out, prompt=args.prompt, ratio=args.ratio, size=args.size,
        tier=args.tier, image_urls=image_urls or None,
        project_root=project_root, force=args.force,
    )
    if hit is not None:
        print(json.dumps(hit, ensure_ascii=False, indent=2))
        return 0 if hit.get("status") in ("skip", "blocked") else 1
    # 有参考图 → 走 edits 端点（multipart，参考图真正生效）
    # 无参考图 → 走 generations 端点（纯文生图）
    if image_urls:
        result = edit_one(
            args.prompt,
            out,
            model=args.model,
            size=args.size,
            ratio=args.ratio,
            tier=args.tier,
            quality=args.quality,
            image_urls=image_urls,
            project_root=project_root,
            dry_run=args.dry_run,
            index=args.index,
        )
    else:
        result = generate_one(
            args.prompt,
            out,
            model=args.model,
            size=args.size,
            ratio=args.ratio,
            tier=args.tier,
            quality=args.quality,
            image_urls=None,
            project_root=project_root,
            dry_run=args.dry_run,
            index=args.index,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ("ok", "dry_run") else 1


def cmd_batch(args: argparse.Namespace) -> int:
    yaml_path = Path(args.yaml).expanduser().resolve()
    if not yaml_path.is_file():
        print(json.dumps({"error": f"文件不存在: {yaml_path}"}, ensure_ascii=False))
        return 1

    if yaml is None:
        print(json.dumps({"error": "批量模式需要 PyYAML: pip3 install pyyaml"}, ensure_ascii=False))
        return 1
    doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        print(json.dumps({"error": "YAML 根节点须为对象"}, ensure_ascii=False))
        return 1

    try:
        project_root = assert_valid_drama_project_root(args.project_root) if args.project_root else None
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    if project_root is None and doc.get("project_root"):
        project_root = Path(str(doc["project_root"])).expanduser().resolve()
    if project_root:
        os.environ.setdefault("DRAMA_PROJECT_ROOT", str(project_root))

    default_model = args.model or doc.get("model")
    default_size = args.size or doc.get("size")
    default_ratio = args.ratio or doc.get("ratio")
    default_tier = args.tier or doc.get("tier")
    default_quality = args.quality or doc.get("quality")

    items = load_batch_yaml(yaml_path)
    id_filter = None
    if args.ids:
        id_filter = {x.strip() for x in args.ids.split(",") if x.strip()}

    results: list[dict[str, Any]] = []
    ok = 0
    fail = 0
    skip = 0
    blocked = 0  # 设计上拒重发（≠失败，不进 fail/退出码，避免 agent 误判重试）

    for item in items:
        item_id = str(item.get("id", "")).strip()
        if id_filter and item_id not in id_filter:
            continue
        prompt = (item.get("prompt_en") or item.get("prompt") or "").strip()
        if not prompt:
            results.append({"id": item_id, "status": "skip", "reason": "prompt 为空"})
            skip += 1
            continue

        out_path = resolve_batch_output(item, yaml_path, project_root)
        ratio = _norm_ratio(item.get("ratio") or default_ratio)
        item_images = item.get("image_urls") or item.get("image_url")
        if isinstance(item_images, str):
            item_images = [item_images]
        image_urls = [str(u).strip() for u in (item_images or []) if str(u).strip()] or None

        if getattr(args, "status", False):
            # dry-run 状态查询
            fp = dedup.fingerprint_image(
                prompt, size=item.get("size") or default_size or resolve_size(ratio, None, item.get("tier") or default_tier),
                ratio=ratio, image_urls=image_urls,
            )
            local = dedup.local_lookup(
                project_root, kind=KIND_GPT_IMAGE, episode_id=None,
                identity_key=out_path.stem, fingerprint=fp,
            ) if project_root else None
            if local and local.get("matched") and local.get("kind") == "submitted":
                label = f"✅submitted(task_id={local['existing_task'].get('task_id')})"
            elif local and local.get("matched") and local.get("kind") == "submitting":
                label = f"⏳submitting({'stale' if local.get('stale') else 'in_progress'})"
            elif out_path.is_file():
                label = "✅file_exists(no archive)"
            else:
                label = "❓not_generated"
            print(f"{item_id}\t{label}", file=sys.stderr)
            results.append({"id": item_id, "status": label})
            continue

        hit = _dedup_check(
            output=out_path, prompt=prompt, ratio=ratio,
            size=item.get("size") or default_size, tier=item.get("tier") or default_tier,
            image_urls=image_urls, project_root=project_root, force=args.force,
        )
        if getattr(args, "pending", False):
            # 增量：只生成未生成的；命中 hit（skip/blocked）跳过
            if hit is not None:
                if hit.get("status") == "skip":
                    skip += 1
                    results.append({"id": item_id, "status": "skip", "reason": hit.get("reason"), "output": str(out_path)})
                else:
                    blocked += 1
                    results.append({"id": item_id, "status": "blocked", "reason": hit.get("reason"), "output": str(out_path)})
                continue
        else:
            if hit is not None:
                if hit.get("status") == "skip":
                    results.append(hit)
                    skip += 1
                else:
                    blocked += 1
                    results.append({"id": item_id, **hit})
                continue

        # 有参考图 → edits 端点（multipart，参考图真正生效）
        # 无参考图 → generations 端点（纯文生图）
        if image_urls:
            r = edit_one(
                prompt,
                out_path,
                model=item.get("model") or default_model,
                size=item.get("size") or default_size,
                ratio=ratio,
                tier=item.get("tier") or default_tier,
                quality=item.get("quality") or default_quality,
                image_urls=image_urls,
                project_root=project_root,
                dry_run=args.dry_run,
            )
        else:
            r = generate_one(
                prompt,
                out_path,
                model=item.get("model") or default_model,
                size=item.get("size") or default_size,
                ratio=ratio,
                tier=item.get("tier") or default_tier,
                quality=item.get("quality") or default_quality,
                image_urls=None,
                project_root=project_root,
                dry_run=args.dry_run,
            )
        r["id"] = item_id
        r["output"] = str(out_path)
        results.append(r)
        if r.get("status") in ("ok", "dry_run"):
            ok += 1
        else:
            fail += 1
        if not args.dry_run and args.delay > 0:
            time.sleep(args.delay)

    summary = {"ok": ok, "fail": fail, "skip": skip, "blocked": blocked, "yaml": str(yaml_path), "items": results}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if fail == 0 else 1


def cmd_docs(_: argparse.Namespace) -> int:
    text = {
        "docs": [
            "https://zrlef1mcfh.apifox.cn/1（OpenAI 兼容协议，base_url 需带 /v1/ 后缀）",
        ],
        "endpoint_generations": base_url() + IMAGES_PATH,
        "endpoint_edits": base_url() + EDITS_PATH,
        "model_default": default_model(),
        "auth": "Bearer GPT_IMAGE_API_KEY",
        "env": [
            "GPT_IMAGE_API_KEY（必填，兼容回退 OPENAI_API_KEY）",
            "GPT_IMAGE_BASE_URL（默认 https://cn.getgoapi.com）",
            "GPT_IMAGE_MODEL（默认 gpt-image-2）",
            "GPT_IMAGE_QUALITY（low/medium/high/auto，默认 auto）",
            "GPT_IMAGE_SIZE_TIER（standard/2k/4k，默认 standard）",
        ],
        "archive_dir": str(get_archive_base()),
        "size_9_16_standard": SIZE_BY_TIER["standard"]["9:16"],
        "size_9_16_2k": SIZE_BY_TIER["2k"]["9:16"],
        "size_9_16_4k": SIZE_BY_TIER["4k"]["9:16"],
        "constraints": "边长须为 16 的倍数，最大边长 ≤3840，长边/短边 ≤3:1，总像素 655,360~8,294,400",
        "note": "有参考图时自动走 /v1/images/edits（multipart）；无参考图走 /v1/images/generations（JSON）。任务写入项目 assets/tasks_gpt_image.json",
    }
    print(json.dumps(text, ensure_ascii=False, indent=2))
    return 0


def cmd_reconcile(args: argparse.Namespace) -> int:
    """图片本地归档与 output 文件对账（gpt-image-2 无远程历史列表 API）。

    把"图在盘但归档缺指纹/缺条目"补回，让本地指纹去重更可靠；清理落盘文件不存在的孤儿条目。"""
    try:
        project_root = assert_valid_drama_project_root(args.project_root) if args.project_root else None
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2
    results: list[dict[str, Any]] = []

    if args.yaml and project_root:
        yaml_path = Path(args.yaml).expanduser().resolve()
        items = load_batch_yaml(yaml_path)
        for item in items:
            item_id = str(item.get("id", ""))
            out_path = resolve_batch_output(item, yaml_path, project_root)
            prompt = (item.get("prompt_en") or item.get("prompt") or "").strip()
            ratio = _norm_ratio(item.get("ratio"))
            item_images = item.get("image_urls") or item.get("image_url")
            if isinstance(item_images, str):
                item_images = [item_images]
            image_urls = [str(u).strip() for u in (item_images or []) if str(u).strip()] or None
            fp = dedup.fingerprint_image(
                prompt, size=item.get("size") or resolve_size(ratio, None, item.get("tier")),
                ratio=ratio, image_urls=image_urls,
            )
            local = dedup.local_lookup(
                project_root, kind=KIND_GPT_IMAGE, episode_id=None,
                identity_key=out_path.stem, fingerprint=fp,
            )
            if local and local.get("matched"):
                results.append({"id": item_id, "status": "archive_ok", "task_id": local["existing_task"].get("task_id")})
            elif out_path.is_file():
                # 图在盘但归档缺 → 补一条记录（无真实 task_id，仅作指纹冻结避免重出）
                try:
                    dedup.add_submitting_placeholder(
                        project_root, kind=KIND_GPT_IMAGE, episode_id=None,
                        client_request_id=f"local-recon-{out_path.stem}",
                        fingerprint=fp, identity_key=out_path.stem,
                        extra_params={"output": str(out_path), "status_hint": "file_present_no_archive"},
                    )
                    dedup.promote_submitting(
                        project_root, kind=KIND_GPT_IMAGE, episode_id=None,
                        client_request_id=f"local-recon-{out_path.stem}",
                        real_task_id=f"file:{out_path.stem}",
                        extra_updates={"fingerprint": fp, "identity": out_path.stem, "output": str(out_path)},
                    )
                    results.append({"id": item_id, "status": "补归档(file_present)", "output": str(out_path)})
                    print(f"⊙ {item_id} 盘上有图但归档缺，已补指纹冻结", file=sys.stderr)
                except Exception as e:
                    results.append({"id": item_id, "status": "write_failed", "error": str(e)})
            else:
                results.append({"id": item_id, "status": "未生成，可安全出图"})
    else:
        # 不指定 yaml：扫描归档清理孤儿（落盘文件不存在的条目标记）
        idx = dedup.read_local_index(project_root or Path("."), kind=KIND_GPT_IMAGE, episode_id=None)
        for tid, t in idx.items():
            outp = (t.get("params") or {}).get("output")
            real = dedup.resolve_output_anywhere(outp, project_root or Path(".")) if outp else None
            if outp and real is None:
                results.append({"task_id": tid, "status": "孤儿条目（output 不存在）", "output": outp})
            else:
                results.append({"task_id": tid, "status": "ok", "resolved": str(real) if real else None})

    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="OpenAI 兼容中转 gpt-image-2 文生图/图生图 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="单张文生图/图生图")
    p_gen.add_argument("--prompt", "-p", required=True)
    p_gen.add_argument("--output", "-o", help="保存路径（.png）")
    p_gen.add_argument("--model", default=None)
    p_gen.add_argument("--size", help="如 1024x1536 / 2160x3840 / 2k / 4k")
    p_gen.add_argument("--ratio", default="9:16", help="9:16 / 16:9 / 1:1 / 4:3 / 3:4")
    p_gen.add_argument("--tier", default=None, help="standard / 2k / 4k（--size 未给时按档位映射比例）")
    p_gen.add_argument("--quality", default=None, help="low / medium / high / auto")
    p_gen.add_argument("--image-url", action="append", help="参考图 URL/本地路径，可多次（≤16 张）")
    p_gen.add_argument("--dry-run", action="store_true")
    p_gen.add_argument("--index", type=int, default=0, help="组图时取第几张，默认 0")
    p_gen.add_argument("--project-root", help="相对路径图片的根目录")
    p_gen.add_argument("--force", action="store_true", help="忽略去重强制重出（需 ARK_ALLOW_FORCE=1）")
    p_gen.set_defaults(func=cmd_generate)

    p_batch = sub.add_parser("batch", help="从 gpt_image_batch.yaml 批量出图")
    p_batch.add_argument("--yaml", "-y", required=True)
    p_batch.add_argument("--project-root", help="解析 output 相对路径的根目录")
    p_batch.add_argument("--ids", help="逗号分隔，只处理指定 id")
    p_batch.add_argument("--model", default=None)
    p_batch.add_argument("--size", default=None)
    p_batch.add_argument("--ratio", default=None)
    p_batch.add_argument("--tier", default=None)
    p_batch.add_argument("--quality", default=None)
    p_batch.add_argument("--dry-run", action="store_true")
    p_batch.add_argument("--force", action="store_true", help="覆盖已存在文件（需 ARK_ALLOW_FORCE=1）")
    p_batch.add_argument("--delay", type=float, default=1.0, help="每张间隔秒数")
    p_batch.add_argument("--pending", action="store_true", help="只生成未生成的（增量）")
    p_batch.add_argument("--status", action="store_true", help="只打印每项状态不生成")
    p_batch.set_defaults(func=cmd_batch)

    p_docs = sub.add_parser("docs", help="打印文档链接与默认配置")
    p_docs.set_defaults(func=cmd_docs)

    p_rec = sub.add_parser("reconcile", help="图片本地归档与 output 文件对账（无远程 API）")
    p_rec.add_argument("--yaml", "-y", help="gpt_image_batch.yaml，用于算指纹比对；不指定则只扫归档孤儿")
    p_rec.add_argument("--project-root", help="短剧项目根")
    p_rec.set_defaults(func=cmd_reconcile)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
