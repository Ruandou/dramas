#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火山方舟 · Seedream 5.0 lite 文生图（图片生成 API）

文档：
  - 教程：https://www.volcengine.com/docs/82379/1824121?lang=zh
  - API：https://www.volcengine.com/docs/82379/1541523?lang=zh
  - 图片生成 API 总览：https://www.volcengine.com/docs/82379/1666945?lang=zh

鉴权：Authorization: Bearer <ARK_API_KEY>
环境变量：
  ARK_API_KEY 或 VOLC_ARK_API_KEY（必填）
  ARK_BASE_URL（默认 https://ark.cn-beijing.volces.com）
  ARK_SEEDREAM_MODEL（默认 doubao-seedream-5-0-lite-260128，方舟控制台「5.0 lite」）
  ARK_SEEDREAM_SIZE_TIER（2K 或 3K，默认 2K）

CLI：
  python3 ark_seedream_image.py generate --prompt "..." --output out.png
  python3 ark_seedream_image.py batch --yaml assets/looks/seedream_batch.yaml
  python3 ark_seedream_image.py batch --yaml ... --dry-run --ids CHAR-001-L01
"""
from __future__ import annotations

import argparse
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
import dedup
from project_task_archive import KIND_SEEDREAM, assert_valid_drama_project_root
from cdn_registry import update_cdn_urls_json
import uuid

DEFAULT_BASE = "https://ark.cn-beijing.volces.com"
IMAGES_PATH = "/api/v3/images/generations"
DEFAULT_MODEL = "doubao-seedream-5-0-lite-260128"

# 官方推荐像素（2K / 3K），见 Seedream 5.0 lite 文档
SIZE_BY_RATIO = {
    "2K": {
        "1:1": "2048x2048",
        "16:9": "2848x1600",
        "9:16": "1600x2848",
        "4:3": "2304x1728",
        "3:4": "1728x2304",
    },
    "3K": {
        "1:1": "3072x3072",
        "16:9": "4096x2304",
        "9:16": "2304x4096",
        "4:3": "3456x2592",
        "3:4": "2592x3456",
    },
}

IMAGE_URL_RE = re.compile(
    r"!\[[^\]]*\]\((https://[^)\s]+)\)|"
    r'"(?:url|image_url|download_url)"\s*:\s*"(https://[^"]+)"|'
    r"(https://ark[^\s\"')]+\.(?:png|jpeg|jpg|webp)(?:\?[^\s\"')]*)?)",
    re.IGNORECASE,
)


def api_key() -> str:
    return (os.environ.get("ARK_API_KEY") or os.environ.get("VOLC_ARK_API_KEY") or "").strip()


def base_url() -> str:
    return (os.environ.get("ARK_BASE_URL") or DEFAULT_BASE).rstrip("/")


def default_model() -> str:
    return (os.environ.get("ARK_SEEDREAM_MODEL") or DEFAULT_MODEL).strip()


def size_tier() -> str:
    t = (os.environ.get("ARK_SEEDREAM_SIZE_TIER") or "2K").strip().upper()
    return t if t in SIZE_BY_RATIO else "2K"


def resolve_size(ratio: str | None, size: str | None) -> str:
    if size and "x" in size.lower():
        return size.lower().replace("×", "x")
    r = (ratio or "9:16").strip()
    tier = size_tier()
    preset = SIZE_BY_RATIO.get(tier, SIZE_BY_RATIO["2K"])
    if r in preset:
        return preset[r]
    # 关键词 2K / 3K
    if size and size.upper() in ("2K", "3K"):
        return preset.get("9:16", "1600x2848")
    return preset.get("9:16", "1600x2848")


def build_payload(
    prompt: str,
    *,
    model: str | None = None,
    size: str | None = None,
    ratio: str | None = None,
    image_urls: list[str] | None = None,
    project_root: Path | None = None,
    web_search: bool = False,
    watermark: bool = False,
    output_format: str = "png",
    sequential: str = "disabled",
    max_images: int = 1,
    stream: bool = False,
) -> dict[str, Any]:
    """构造 POST /api/v3/images/generations 请求体（5.0 lite 走此接口，非 Responses）。"""
    body: dict[str, Any] = {
        "model": model or default_model(),
        "prompt": prompt,
        "size": resolve_size(ratio, size),
        "response_format": "url",
        "watermark": watermark,
    }
    if sequential == "auto":
        body["sequential_image_generation"] = "auto"
        body["sequential_image_generation_options"] = {"max_images": max(1, min(max_images, 15))}
    elif sequential != "disabled":
        body["sequential_image_generation"] = sequential
    if output_format and output_format != "png":
        body["output_format"] = output_format
    if web_search:
        body["tools"] = [{"type": "web_search"}]
    if image_urls:
        resolved = [
            resolve_image_url(u, project_root) for u in image_urls[:10]
        ]
        body["image"] = resolved[0] if len(resolved) == 1 else resolved
    return body


def http_post_json(url: str, key: str, payload: dict[str, Any], timeout: int = 300) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace") if e.fp else ""
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


def download_file(url: str, dest: Path) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "volc-ark-cli/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return {"path": str(dest.resolve()), "bytes": len(data), "url": url}


def generate_one(
    prompt: str,
    output: Path | None,
    *,
    model: str | None = None,
    size: str | None = None,
    ratio: str | None = None,
    image_urls: list[str] | None = None,
    web_search: bool = False,
    watermark: bool = False,
    dry_run: bool = False,
    index: int = 0,
    project_root: Path | None = None,
) -> dict[str, Any]:
    key = api_key()
    if not key and not dry_run:
        return {"error": "未设置 ARK_API_KEY 或 VOLC_ARK_API_KEY"}

    payload = build_payload(
        prompt,
        model=model,
        size=size,
        ratio=ratio,
        image_urls=image_urls,
        project_root=project_root,
        web_search=web_search,
        watermark=watermark,
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
    # 卡位让下次对账发现"提交状态不明"→ 拒自动重发避免双倍扣费）。
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
                kind=KIND_SEEDREAM,
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
                f"⚠️ 归档写卡位失败但即将继续 POST，方舟可能已扣费：{e}",
                file=sys.stderr,
            )

    t0 = time.time()
    try:
        resp = http_post_json(base_url() + IMAGES_PATH, key, payload)
    except Exception as e:
        # POST 失败/超时：可能方舟已扣费但本地拿不到响应
        if placeholder_ok:
            print(
                "⚠️ 图片提交状态不明，方舟可能已扣费但本地无法对账（Seedream 无历史列表 API）。"
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
    if not urls:
        return {
            "error": "响应中未解析到图片 URL",
            "response_id": resp.get("id"),
            "status": resp.get("status"),
            "raw_preview": json.dumps(resp, ensure_ascii=False)[:2000],
        }

    pick = urls[min(index, len(urls) - 1)]
    rid = resp.get("id") or resp.get("created")
    if rid:
        if project_root:
            os.environ.setdefault("DRAMA_PROJECT_ROOT", str(Path(project_root).resolve()))
        if placeholder_ok:
            # 提拔 submitting 卡位 → 写入真实 id
            try:
                dedup.promote_submitting(
                    project_root,
                    kind=KIND_SEEDREAM,
                    episode_id=None,
                    client_request_id=client_request_id,
                    real_task_id=str(rid),
                    extra_updates={
                        "prompt": prompt[:500],
                        "model": payload.get("model"),
                        "size": payload.get("size"),
                        "has_ref_images": bool(image_urls),
                        "output": str(output) if output else None,
                        "cdn_url": pick,
                        "identity": identity_key,
                        "fingerprint": fp,
                    },
                )
            except Exception:
                add_task(
                    "seedream_image",
                    str(rid),
                    {
                        "prompt": prompt[:500],
                        "model": payload.get("model"),
                        "size": payload.get("size"),
                        "has_ref_images": bool(image_urls),
                        "output": str(output) if output else None,
                        "cdn_url": pick,
                        "identity": identity_key,
                        "fingerprint": fp,
                    },
                    status=str(resp.get("status") or "completed"),
                )
        else:
            add_task(
                "seedream_image",
                str(rid),
                {
                    "prompt": prompt[:500],
                    "model": payload.get("model"),
                    "size": payload.get("size"),
                    "has_ref_images": bool(image_urls),
                    "output": str(output) if output else None,
                    "cdn_url": pick,
                    "identity": identity_key,
                    "fingerprint": fp,
                },
                status=str(resp.get("status") or "completed"),
            )
    result: dict[str, Any] = {
        "status": "ok",
        "model": payload["model"],
        "size": payload["size"],
        "image_url": pick,
        "all_urls": urls,
        "response_id": rid,
        "elapsed_sec": round(time.time() - t0, 2),
        "usage": resp.get("usage"),
        "archive_dir": str(get_archive_base()),
    }

    if output:
        dl = download_file(pick, output)
        result["saved"] = dl
        # Auto-update cdn_urls.json for looks/scenes assets
        cdn_json = update_cdn_urls_json(
            output,
            cdn_url=pick,
            task_id=str(rid) if rid else None,
            model=payload.get("model"),
            size=payload.get("size"),
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
    # 相对路径：优先相对 yaml 所在项目的 assets 父级（天工开物根）
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


def _resolve_image_size(prompts_ratio: str | None, size: str | None) -> str:
    """近似生成 one 用到的 size 字符串，用于指纹。"""
    return resolve_size(prompts_ratio, size)


def _seedream_dedup_check(
    *,
    output: Path | None,
    prompt: str,
    ratio: str | None,
    size: str | None,
    image_urls: list[str] | None,
    project_root: Path | None,
    force: bool,
) -> dict[str, Any] | None:
    """图片去重前置：本地指纹命中或 output 已存在且指纹相同 → skip。

    Seedream 无远程历史列表，对账只走本地归档 + output 文件存在双查。
    返回 None = 放行；返回 dict = 已命中，调用方应 skip。"""
    ok_force, force_msg = dedup.require_force_confirm(force)
    if force and not ok_force:
        print(force_msg, file=sys.stderr)
        force = False
    if force:
        return None
    if project_root is None or output is None:
        # 无 project_root 无法写本地归档，退回旧行为：仅按 output 文件存在
        if output and output.is_file():
            return {"status": "skip", "reason": "文件已存在", "output": str(output)}
        return None
    fp = dedup.fingerprint_image(
        prompt, size=size or resolve_size(ratio, size), ratio=ratio, image_urls=image_urls,
    )
    identity_key = output.stem
    local = dedup.local_lookup(
        project_root, kind=KIND_SEEDREAM, episode_id=None,
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
        # 图片无远程对账，submitting 卡位 → 拒自动重发
        return {
            "status": "blocked",
            "reason": "本地 submitting 卡位未结算（可能方舟已扣费，Seedream 无历史列表无法远程对账）。如确认原请求未真发出，用 --force + ARK_ALLOW_FORCE=1 重发。",
            "output": str(output),
        }
    if output.is_file():
        # 文件存在但本地指纹没命中（旧图）→ 视为已生成 skip
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
    # 去重前置
    hit = _seedream_dedup_check(
        output=out, prompt=args.prompt, ratio=args.ratio, size=args.size,
        image_urls=image_urls or None, project_root=project_root, force=args.force,
    )
    if hit is not None:
        print(json.dumps(hit, ensure_ascii=False, indent=2))
        # blocked（设计拒重发）≠ 失败：与 cmd_batch 一致返回 0，不诱导 agent 拿非零退出码重试
        return 0 if hit.get("status") in ("skip", "blocked") else 1
    result = generate_one(
        args.prompt,
        out,
        model=args.model,
        size=args.size,
        ratio=args.ratio,
        image_urls=image_urls or None,
        project_root=project_root,
        web_search=args.web_search,
        watermark=args.watermark,
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
        # setdefault 而非 =：不覆盖调用方已显式注入的 DRAMA_PROJECT_ROOT（如长期运行 daemon 场景）
        os.environ.setdefault("DRAMA_PROJECT_ROOT", str(project_root))

    default_model = args.model or doc.get("model")
    default_size = args.size or doc.get("size")
    default_ratio = args.ratio or doc.get("ratio")
    default_watermark = args.watermark or bool(doc.get("watermark"))

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
        ratio = item.get("ratio") or default_ratio
        item_images = item.get("image_urls") or item.get("image_url")
        if isinstance(item_images, str):
            item_images = [item_images]
        image_urls = [str(u).strip() for u in (item_images or []) if str(u).strip()] or None

        if getattr(args, "status", False):
            # dry-run 状态查询
            fp = dedup.fingerprint_image(
                prompt, size=item.get("size") or default_size or resolve_size(ratio, None),
                ratio=ratio, image_urls=image_urls,
            )
            local = dedup.local_lookup(
                project_root, kind=KIND_SEEDREAM, episode_id=None,
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

        # 去重前置
        hit = _seedream_dedup_check(
            output=out_path, prompt=prompt, ratio=ratio,
            size=item.get("size") or default_size,
            image_urls=image_urls, project_root=project_root, force=args.force,
        )
        if getattr(args, "pending", False):
            # 增量：只生成未生成的；命中 hit（skip/blocked）跳过
            if hit is not None:
                if hit.get("status") == "skip":
                    skip += 1
                    results.append({"id": item_id, "status": "skip", "reason": hit.get("reason"), "output": str(out_path)})
                else:
                    blocked += 1  # blocked 不算失败，不诱导重试
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

        r = generate_one(
            prompt,
            out_path,
            model=item.get("model") or default_model,
            size=item.get("size") or default_size,
            ratio=ratio,
            image_urls=image_urls,
            project_root=project_root,
            web_search=args.web_search,
            watermark=bool(item.get("watermark", default_watermark)),
            dry_run=args.dry_run,
        )
        r["id"] = item_id
        r["output"] = str(out_path)
        results.append(r)
        if r.get("status") == "ok":
            ok += 1
        elif r.get("status") == "dry_run":
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
            "https://www.volcengine.com/docs/82379/1824121?lang=zh",
            "https://www.volcengine.com/docs/82379/1541523?lang=zh",
            "https://www.volcengine.com/docs/82379/1666945?lang=zh",
        ],
        "endpoint": base_url() + IMAGES_PATH,
        "model_default": default_model(),
        "auth": "Bearer ARK_API_KEY",
        "env": ["ARK_API_KEY", "ARK_BASE_URL", "ARK_SEEDREAM_MODEL", "ARK_SEEDREAM_SIZE_TIER"],
        "archive_dir": str(get_archive_base()),
        "size_9_16_2k": SIZE_BY_RATIO["2K"]["9:16"],
        "size_9_16_3k": SIZE_BY_RATIO["3K"]["9:16"],
        "note": "参考图可为本地路径，自动转 data URI；任务写入 video/ark_tasks/tasks_image.json",
    }
    print(json.dumps(text, ensure_ascii=False, indent=2))
    return 0


def cmd_reconcile(args: argparse.Namespace) -> int:
    """图片本地归档与 output 文件对账（Seedream 无远程历史列表 API）。

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
            ratio = item.get("ratio")
            item_images = item.get("image_urls") or item.get("image_url")
            if isinstance(item_images, str):
                item_images = [item_images]
            image_urls = [str(u).strip() for u in (item_images or []) if str(u).strip()] or None
            fp = dedup.fingerprint_image(
                prompt, size=item.get("size") or resolve_size(ratio, None),
                ratio=ratio, image_urls=image_urls,
            )
            local = dedup.local_lookup(
                project_root, kind=KIND_SEEDREAM, episode_id=None,
                identity_key=out_path.stem, fingerprint=fp,
            )
            if local and local.get("matched"):
                results.append({"id": item_id, "status": "archive_ok", "task_id": local["existing_task"].get("task_id")})
            elif out_path.is_file():
                # 图在盘但归档缺 → 补一条记录（无真实 task_id，仅作指纹冻结避免重出）
                try:
                    dedup.add_submitting_placeholder(
                        project_root, kind=KIND_SEEDREAM, episode_id=None,
                        client_request_id=f"local-recon-{out_path.stem}",
                        fingerprint=fp, identity_key=out_path.stem,
                        extra_params={"output": str(out_path), "status_hint": "file_present_no_archive"},
                    )
                    dedup.promote_submitting(
                        project_root, kind=KIND_SEEDREAM, episode_id=None,
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
        idx = dedup.read_local_index(project_root or Path("."), kind=KIND_SEEDREAM, episode_id=None)
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
    parser = argparse.ArgumentParser(description="火山方舟 Seedream 5.0 lite 文生图 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="单张文生图")
    p_gen.add_argument("--prompt", "-p", required=True)
    p_gen.add_argument("--output", "-o", help="保存路径（.png）")
    p_gen.add_argument("--model", default=None)
    p_gen.add_argument("--size", help="如 1600x2848 或 2K")
    p_gen.add_argument("--ratio", default="9:16", help="9:16 / 16:9 / 1:1 …")
    p_gen.add_argument("--image-url", action="append", help="参考图 URL，可多次")
    p_gen.add_argument("--web-search", action="store_true")
    p_gen.add_argument("--watermark", action="store_true")
    p_gen.add_argument("--dry-run", action="store_true")
    p_gen.add_argument("--index", type=int, default=0, help="组图时取第几张，默认 0")
    p_gen.add_argument("--project-root", help="相对路径图片的根目录")
    p_gen.add_argument("--force", action="store_true", help="忽略去重强制重出（需 ARK_ALLOW_FORCE=1）")
    p_gen.set_defaults(func=cmd_generate)

    p_batch = sub.add_parser("batch", help="从 seedream_batch.yaml 批量出图")
    p_batch.add_argument("--yaml", "-y", required=True)
    p_batch.add_argument("--project-root", help="解析 output 相对路径的根目录")
    p_batch.add_argument("--ids", help="逗号分隔，只处理指定 id")
    p_batch.add_argument("--model", default=None)
    p_batch.add_argument("--size", default=None)
    p_batch.add_argument("--ratio", default=None)
    p_batch.add_argument("--web-search", action="store_true")
    p_batch.add_argument("--watermark", action="store_true")
    p_batch.add_argument("--dry-run", action="store_true")
    p_batch.add_argument("--force", action="store_true", help="覆盖已存在文件（需 ARK_ALLOW_FORCE=1）")
    p_batch.add_argument("--delay", type=float, default=1.0, help="每张间隔秒数")
    p_batch.add_argument("--pending", action="store_true", help="只生成未生成的（增量）")
    p_batch.add_argument("--status", action="store_true", help="只打印每项状态不生成")
    p_batch.set_defaults(func=cmd_batch)

    p_docs = sub.add_parser("docs", help="打印文档链接与默认配置")
    p_docs.set_defaults(func=cmd_docs)

    p_rec = sub.add_parser("reconcile", help="图片本地归档与 output 文件对账（无远程 API）")
    p_rec.add_argument("--yaml", "-y", help="seedream_batch.yaml，用于算指纹比对；不指定则只扫 assets 下的图")
    p_rec.add_argument("--project-root", help="短剧项目根")
    p_rec.set_defaults(func=cmd_reconcile)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
