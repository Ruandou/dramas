#!/usr/bin/env python3
"""
读取 EP##_segments.yaml → 校验 looks/scenes（+ 可选 voice_refs）→ 展开 Seedance API 请求体。

默认 dry-run；--submit 需 ARK_API_KEY。--wait --download 在提交后轮询并落盘 mp4。

用法（在 darams/天工开物 下）：
  python3 script/storyboard_submit_segments.py EP01 --check-only
  python3 script/storyboard_submit_segments.py EP01 --segment EP01-SEG04b
  export ARK_API_KEY=...
  python3 script/storyboard_submit_segments.py EP01 --segment EP01-SEG04b --submit --wait --download
  python3 script/storyboard_submit_segments.py EP01 --submit --wait --download
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[3]
_REPO_SCRIPTS = _REPO_ROOT / "mcps" / "volc-ark" / "scripts"
if str(_REPO_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_REPO_SCRIPTS))

from ark_media import resolve_image_url, resolve_media_url  # noqa: E402

EPISODE_DIR = ROOT / "分集剧本"
GENERATED_DIR = ROOT / "assets" / "generated"
REQUESTS_DIR = ROOT / "configs" / "seedance_requests"
ARK_VIDEO_CLI = _REPO_SCRIPTS / "ark_seedance_video.py"


def load_episode_segments(ep_id: str) -> dict:
    yaml_path = EPISODE_DIR / f"{ep_id}_segments.yaml"
    if not yaml_path.is_file():
        raise FileNotFoundError(f"缺少 {yaml_path}")
    text = yaml_path.read_text(encoding="utf-8")
    try:
        import yaml

        doc = yaml.safe_load(text)
    except ImportError:
        from storyboard_yaml import load_yaml

        doc = load_yaml(text)
    if not isinstance(doc, dict):
        raise RuntimeError(f"{yaml_path} 根节点须为对象")
    return doc


def resolve_asset_path(rel: str) -> Path:
    return (ROOT / rel).resolve()


def collect_segment_asset_paths(segment: dict) -> list[str]:
    assets = segment.get("assets") or {}
    paths: list[str] = []
    for mapping in (assets.get("look_urls") or {}).values():
        paths.append(mapping)
    for mapping in (assets.get("scene_urls") or {}).values():
        paths.append(mapping)
    for mapping in (segment.get("voice_refs") or {}).values():
        paths.append(mapping)
    return paths


def validate_segment_assets(segment: dict) -> list[str]:
    missing = []
    for rel in collect_segment_asset_paths(segment):
        p = resolve_asset_path(rel)
        if not p.is_file():
            missing.append(rel)
    return missing


def role_file_to_path(segment: dict, file_key: str) -> str | None:
    assets = segment.get("assets") or {}
    looks = assets.get("look_urls") or {}
    if file_key in looks:
        return looks[file_key]
    scenes = assets.get("scene_urls") or {}
    if file_key in scenes:
        return scenes[file_key]
    voice_refs = segment.get("voice_refs") or {}
    if file_key in voice_refs:
        return voice_refs[file_key]
    return None


def build_content_array(segment: dict) -> list[dict]:
    api = segment.get("api") or {}
    content: list[dict] = [{"type": "text", "text": api.get("text", "").strip()}]
    for role_spec in api.get("content_roles") or []:
        file_key = role_spec["file"]
        rel = role_file_to_path(segment, file_key)
        if not rel:
            raise ValueError(f"{segment.get('segment_id')}: 找不到素材 {file_key}")
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": resolve_image_url(rel, ROOT)},
                "role": role_spec["role"],
            }
        )
    for char_id, rel in (segment.get("voice_refs") or {}).items():
        if not rel:
            continue
        content.append(
            {
                "type": "audio_url",
                "audio_url": {"url": resolve_media_url(rel, ROOT)},
                "role": "reference_audio",
            }
        )
    return content


def duration_bounds(model: str) -> tuple[int, int]:
    """Seedance 2.0 fast：4–12 秒；标准版上限约 15 秒。"""
    if "fast" in model:
        return 4, 12
    return 4, 15


def clamp_duration(sec: int, model: str) -> int:
    lo, hi = duration_bounds(model)
    return max(lo, min(hi, int(sec)))


def load_shot_durations(ep_id: str) -> dict[str, int]:
    """从 EP##_shots.yaml 读取镜级 duration_sec（skip 镜无条目则 0）。"""
    path = EPISODE_DIR / f"{ep_id}_shots.yaml"
    if not path.is_file():
        return {}
    try:
        import yaml

        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        from storyboard_yaml import load_yaml

        doc = load_yaml(path.read_text(encoding="utf-8"))
    out: dict[str, int] = {}
    for shot in (doc or {}).get("shots") or []:
        sid = shot.get("shot_id")
        if not sid or shot.get("mode") == "skip":
            continue
        try:
            out[sid] = int(shot.get("duration_sec") or 0)
        except (TypeError, ValueError):
            out[sid] = 0
    return out


def warn_thin_segment(segment: dict, shot_durations: dict[str, int]) -> str | None:
    """
    分镜自然时长合计过短却单独成段 → 建议并入邻段，勿硬凑 API 最短 4 秒。
    """
    shot_ids = segment.get("shot_ids") or []
    if not shot_ids:
        return None
    natural = sum(shot_durations.get(sid, 0) for sid in shot_ids)
    api_dur = segment.get("duration_sec")
    try:
        api_dur = int(api_dur)
    except (TypeError, ValueError):
        return None
    if natural > 0 and natural < 4 and len(shot_ids) <= 2 and api_dur <= 5:
        return (
            f"镜级合计约 {natural}s，却单独成段 duration_sec={api_dur}；"
            f"建议并入同场景相邻段（勿为凑 4s 多开 API）"
        )
    return None


def validate_duration_sec(segment: dict, episode: dict) -> str | None:
    """YAML 中 duration_sec 须在合法区间内，避免 API 400。"""
    defaults = episode.get("defaults") or {}
    model = defaults.get("model", "doubao-seedance-2-0-fast-260128")
    lo, hi = duration_bounds(model)
    raw = segment.get("duration_sec", defaults.get("duration", 5))
    try:
        sec = int(raw)
    except (TypeError, ValueError):
        return f"duration_sec 无效: {raw!r}"
    if sec < lo or sec > hi:
        return f"duration_sec={sec} 超出 [{lo}, {hi}]（model={model}）"
    return None


def build_request_body(episode: dict, segment: dict) -> dict[str, Any]:
    defaults = episode.get("defaults") or {}
    model = defaults.get("model", "doubao-seedance-2-0-fast-260128")
    raw_dur = segment.get("duration_sec", defaults.get("duration", 5))
    body: dict[str, Any] = {
        "model": model,
        "content": build_content_array(segment),
        "ratio": defaults.get("ratio", "9:16"),
        "resolution": defaults.get("resolution", "720p"),
        "duration": clamp_duration(raw_dur, model),
        "generate_audio": defaults.get("generate_audio", True),
        "watermark": defaults.get("watermark", False),
    }
    api = segment.get("api") or {}
    if api.get("return_last_frame"):
        body["return_last_frame"] = True
    if api.get("seed") is not None:
        body["seed"] = api["seed"]
    return body


def post_task(endpoint: str, api_key: str, body: dict) -> dict:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"HTTP {e.code}: {detail or e.reason}") from e


def append_task_log(ep_id: str, entry: dict) -> None:
    log_dir = GENERATED_DIR / ep_id
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "task_log.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def ark_wait_download(task_id: str, out_mp4: Path) -> int:
    if not ARK_VIDEO_CLI.is_file():
        print(f"找不到 {ARK_VIDEO_CLI}", file=sys.stderr)
        return 1
    r1 = subprocess.run(
        [sys.executable, str(ARK_VIDEO_CLI), "wait", "--task-id", task_id, "--max-wait", "600"],
        cwd=str(_REPO_ROOT),
    )
    if r1.returncode != 0:
        return r1.returncode
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    r2 = subprocess.run(
        [
            sys.executable,
            str(ARK_VIDEO_CLI),
            "download",
            "--task-id",
            task_id,
            "-o",
            str(out_mp4),
        ],
        cwd=str(_REPO_ROOT),
    )
    return r2.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seedance 段落提交（默认 dry-run）")
    parser.add_argument("episode", help="如 EP01")
    parser.add_argument("--segment", help="仅指定 segment_id")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--wait", action="store_true", help="提交后等待任务完成")
    parser.add_argument("--download", action="store_true", help="等待后下载到 assets/generated/")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="若 assets/generated/EP##/SEGxx.mp4 已存在则跳过",
    )
    args = parser.parse_args(argv)

    ep_id = args.episode.upper()
    episode = load_episode_segments(ep_id)
    defaults = episode.get("defaults") or {}
    endpoint = defaults.get(
        "endpoint",
        "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks",
    )

    segments = episode.get("segments") or []
    if args.segment:
        segments = [s for s in segments if s.get("segment_id") == args.segment]
        if not segments:
            print(f"未找到段落 {args.segment}", file=sys.stderr)
            return 1

    req_dir = REQUESTS_DIR / ep_id
    req_dir.mkdir(parents=True, exist_ok=True)

    missing_all: list[str] = []
    duration_errors: list[str] = []
    thin_warnings: list[str] = []
    shot_durations = load_shot_durations(ep_id)
    ready = 0

    for seg in segments:
        sid = seg.get("segment_id", "?")
        thin = warn_thin_segment(seg, shot_durations)
        if thin:
            thin_warnings.append(f"{sid}: {thin}")
            print(f"⚠ {sid} {thin}", file=sys.stderr)
        dur_err = validate_duration_sec(seg, episode)
        if dur_err:
            duration_errors.append(f"{sid}: {dur_err}")
            if args.check_only:
                print(f"✗ {sid} {dur_err}", file=sys.stderr)
        if args.skip_existing:
            existing = GENERATED_DIR / ep_id / f"{sid}.mp4"
            if existing.is_file():
                print(f"⊙ {sid} 已存在，跳过")
                ready += 1
                continue
        miss = validate_segment_assets(seg)
        if miss:
            missing_all.extend(f"{sid}: {m}" for m in miss)
            if args.check_only:
                print(f"✗ {sid} 缺 {len(miss)} 个文件")
            continue
        if dur_err:
            continue

        ready += 1
        if args.check_only:
            print(f"✓ {sid} 素材齐全 · duration_sec={seg.get('duration_sec')} OK")
            continue

        body = build_request_body(episode, seg)
        out_path = req_dir / f"{sid}.json"
        out_path.write_text(
            json.dumps(body, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"→ {out_path.relative_to(ROOT)}")

        if args.submit:
            key = (os.environ.get("ARK_API_KEY") or os.environ.get("VOLC_ARK_API_KEY") or "").strip()
            if not key:
                print("提交需要 ARK_API_KEY", file=sys.stderr)
                return 1
            result = post_task(endpoint, key, body)
            task_id = result.get("id") or result.get("task_id") or result.get("data", {}).get("id")
            print(f"  submitted {sid} task_id={task_id}")
            append_task_log(
                ep_id,
                {
                    "ts": time.time(),
                    "segment_id": sid,
                    "task_id": task_id,
                    "response": result,
                },
            )
            if task_id and (args.wait or args.download):
                mp4 = GENERATED_DIR / ep_id / f"{sid}.mp4"
                rc = ark_wait_download(str(task_id), mp4)
                if rc == 0:
                    print(f"  downloaded {mp4.relative_to(ROOT)}")
                else:
                    return rc
            time.sleep(0.5)

    print(
        f"\n{ep_id}: segments_ready={ready} missing_entries={len(missing_all)} "
        f"duration_errors={len(duration_errors)} thin_warnings={len(thin_warnings)}"
    )
    if thin_warnings and args.check_only:
        print("\n薄段建议合并（非 API 错误，但会造成时长/费用浪费）", file=sys.stderr)
    if duration_errors:
        print("\n非法 duration_sec：", file=sys.stderr)
        for line in duration_errors:
            print(f"  - {line}", file=sys.stderr)
        print("fast 模型请写 4–12 秒", file=sys.stderr)
        return 1
    if missing_all and args.check_only:
        for line in missing_all[:20]:
            print(f"  - {line}")
        return 1
    if missing_all and not args.check_only:
        print("\n缺失素材：")
        for line in missing_all[:20]:
            print(f"  - {line}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
