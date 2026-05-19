#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火山方舟 · Seedream 5.0 lite 文生图（Responses API）

文档：
  - 教程：https://www.volcengine.com/docs/82379/1824121?lang=zh
  - API：https://www.volcengine.com/docs/82379/1541523?lang=zh
  - 图片生成 API 总览：https://www.volcengine.com/docs/82379/1666945?lang=zh

鉴权：Authorization: Bearer <ARK_API_KEY>
环境变量：
  ARK_API_KEY 或 VOLC_ARK_API_KEY（必填）
  ARK_BASE_URL（默认 https://ark.cn-beijing.volces.com）
  ARK_SEEDREAM_MODEL（默认 doubao-seedream-5.0-lite）
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
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from ark_archive import add_task, get_archive_base
from ark_media import resolve_image_url

DEFAULT_BASE = "https://ark.cn-beijing.volces.com"
RESPONSES_PATH = "/api/v3/responses"
DEFAULT_MODEL = "doubao-seedream-5.0-lite"

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
    """构造 POST /api/v3/responses 请求体。"""
    body: dict[str, Any] = {
        "model": model or default_model(),
        "input": prompt,
        "size": resolve_size(ratio, size),
        "sequential_image_generation": sequential,
        "stream": stream,
        "output_format": output_format,
        "response_format": "url",
        "watermark": watermark,
    }
    if sequential == "auto":
        body["sequential_image_generation_options"] = {"max_images": max(1, min(max_images, 15))}
    if web_search:
        body["tools"] = [{"type": "web_search"}]
    if image_urls:
        resolved = [
            resolve_image_url(u, project_root) for u in image_urls[:10]
        ]
        body["input"] = [
            *[{"type": "input_image", "image_url": u} for u in resolved],
            {"type": "input_text", "text": prompt},
        ]
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
            "endpoint": base_url() + RESPONSES_PATH,
            "payload": payload,
            "output": str(output) if output else None,
            "archive_dir": str(get_archive_base()),
        }

    t0 = time.time()
    resp = http_post_json(base_url() + RESPONSES_PATH, key, payload)
    urls = extract_image_urls(resp)
    if not urls:
        return {
            "error": "响应中未解析到图片 URL",
            "response_id": resp.get("id"),
            "status": resp.get("status"),
            "raw_preview": json.dumps(resp, ensure_ascii=False)[:2000],
        }

    pick = urls[min(index, len(urls) - 1)]
    rid = resp.get("id")
    if rid:
        add_task(
            "seedream_image",
            str(rid),
            {
                "prompt": prompt[:500],
                "model": payload.get("model"),
                "size": payload.get("size"),
                "has_ref_images": bool(image_urls),
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


def cmd_generate(args: argparse.Namespace) -> int:
    out = Path(args.output).expanduser() if args.output else None
    image_urls = [u.strip() for u in (args.image_url or []) if u.strip()]
    project_root = (
        Path(args.project_root).expanduser().resolve() if args.project_root else None
    )
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

    project_root = Path(args.project_root).expanduser().resolve() if args.project_root else None
    items = load_batch_yaml(yaml_path)
    id_filter = None
    if args.ids:
        id_filter = {x.strip() for x in args.ids.split(",") if x.strip()}

    results: list[dict[str, Any]] = []
    ok = 0
    fail = 0
    skip = 0

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
        if out_path.is_file() and not args.force:
            results.append({"id": item_id, "status": "skip", "reason": "文件已存在", "output": str(out_path)})
            skip += 1
            continue

        ratio = item.get("ratio") or args.ratio
        r = generate_one(
            prompt,
            out_path,
            model=args.model,
            size=args.size,
            ratio=ratio,
            project_root=project_root,
            web_search=args.web_search,
            watermark=args.watermark,
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

    summary = {"ok": ok, "fail": fail, "skip": skip, "yaml": str(yaml_path), "items": results}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if fail == 0 else 1


def cmd_docs(_: argparse.Namespace) -> int:
    text = {
        "docs": [
            "https://www.volcengine.com/docs/82379/1824121?lang=zh",
            "https://www.volcengine.com/docs/82379/1541523?lang=zh",
            "https://www.volcengine.com/docs/82379/1666945?lang=zh",
        ],
        "endpoint": base_url() + RESPONSES_PATH,
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
    p_batch.add_argument("--force", action="store_true", help="覆盖已存在文件")
    p_batch.add_argument("--delay", type=float, default=1.0, help="每张间隔秒数")
    p_batch.set_defaults(func=cmd_batch)

    p_docs = sub.add_parser("docs", help="打印文档链接与默认配置")
    p_docs.set_defaults(func=cmd_docs)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
