#!/usr/bin/env python3
"""
读取 EP##_segments.yaml → 校验 looks/scenes（+ 可选 voice_refs）→ 展开 Seedance API 请求体。

默认 dry-run；--submit 需 ARK_API_KEY。--wait --download 在提交后轮询并落盘 mp4。
任务登记（方案 A）：assets/generated/EP##/tasks.json（经 ark_seedance_record）。

用法（在 darams/天工开物 下）：
  python3 script/storyboard_submit_segments.py EP01 --check-only
  python3 script/storyboard_submit_segments.py EP01 --segment EP01-SEG04b
  export ARK_API_KEY=...
  python3 script/storyboard_submit_segments.py EP01 --segment EP01-SEG04b --submit --wait --download
  python3 script/storyboard_submit_segments.py EP01 --submit --wait --download
  python3 script/storyboard_submit_segments.py EP01 --pull              # 按 tasks.json 补下缺段
  bash script/pull_episode.sh EP01 --concat   # git pull + 补下 + 可选拼集
"""

from __future__ import annotations

import argparse
import json
import os
import re
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
from ark_seedance_record import record_status, record_submit  # noqa: E402

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


def narrator_voice_prompt(episode: dict) -> str | None:
    prompts = episode.get("voice_prompts") or {}
    raw = prompts.get("NARR-001")
    return str(raw).strip() if raw else None


def segment_has_narration(text: str) -> bool:
    """排除「无旁白」等否定表述。"""
    if "口播钩子" in text:
        return True
    return bool(re.search(r"旁白\s*[（(]", text))


def validate_narrator_voice(episode: dict) -> list[str]:
    """含画外旁白的 segment 须嵌入 NARR-001 全文；字幕镜（无旁白）不校验。"""
    narr_prompt = narrator_voice_prompt(episode)
    if not narr_prompt:
        return []
    errors: list[str] = []
    banned = (
        "旁白（沉稳男声）",
        "口播钩子（宋知行",
        "口播钩子（宋知行，同上声线）",
    )
    for seg in episode.get("segments") or []:
        sid = seg.get("segment_id", "?")
        if seg.get("subtitle_shots"):
            continue
        text = (seg.get("api") or {}).get("text") or ""
        if not segment_has_narration(text):
            continue
        for b in banned:
            if b in text:
                errors.append(f"{sid}: 含已废弃旁白写法「{b}」，请改用 NARR-001")
        if narr_prompt not in text:
            errors.append(f"{sid}: 含旁白但未嵌入 voice_prompts.NARR-001 全文")
        elif "NARR-001" not in text:
            errors.append(f"{sid}: 旁白须标注 NARR-001")
    return errors


def validate_subtitle_segments(episode: dict) -> list[str]:
    """全段须声明字幕规则；有对白段用 prompt_suffix，无对白段用 prompt_suffix_silent。"""
    defaults = episode.get("defaults") or {}
    sub_suffix = defaults.get("prompt_suffix") or ""
    silent_suffix = defaults.get("prompt_suffix_silent") or ""
    errors: list[str] = []
    for seg in episode.get("segments") or []:
        sid = seg.get("segment_id", "?")
        text = (seg.get("api") or {}).get("text") or ""
        if "字幕：" not in text:
            errors.append(f"{sid}: 须在 api.text 开头声明「字幕：…」规则")
        if "无清晰汉字" in text:
            errors.append(f"{sid}: 已启用全段字幕，勿使用「无清晰汉字」")
        silent = "本段无对白" in text or "不显示字幕" in text
        if silent:
            if silent_suffix and silent_suffix not in text:
                errors.append(f"{sid}: 无对白段须使用 defaults.prompt_suffix_silent")
        else:
            if "简体" not in text and "白字" not in text:
                errors.append(f"{sid}: 有对白段须写明简体白字字幕规则")
            if sub_suffix and sub_suffix not in text:
                errors.append(f"{sid}: 有对白段须包含 defaults.prompt_suffix 全文")
        if segment_has_narration(text) and "NARR-001" not in text:
            errors.append(f"{sid}: 画外旁白须标注 NARR-001 并嵌入 voice_prompts 全文")
        narr_prompt = narrator_voice_prompt(episode)
        if segment_has_narration(text) and narr_prompt and narr_prompt not in text:
            errors.append(f"{sid}: 旁白须嵌入 voice_prompts.NARR-001 全文")
    return errors


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


MIN_MP4_BYTES = 80 * 1024  # 小于约 80KB 视为异常/占位，--pull 时会重下


def load_segment_task_map(ep_id: str) -> dict[str, str]:
    """segment_id → task_id（同段多条时取 updated_at 最新）。"""
    path = GENERATED_DIR / ep_id / "tasks.json"
    if not path.is_file():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    best: dict[str, tuple[str, str]] = {}
    for row in doc.get("tasks") or []:
        tid = row.get("task_id")
        params = row.get("params") or {}
        sid = params.get("segment_id")
        if not tid or not sid:
            continue
        ts = row.get("updated_at") or row.get("created_at") or ""
        prev = best.get(sid)
        if prev is None or ts >= prev[1]:
            best[sid] = (str(tid), ts)
    return {sid: tid for sid, (tid, _) in best.items()}


def mp4_needs_pull(path: Path, force: bool) -> bool:
    if force or not path.is_file():
        return True
    try:
        return path.stat().st_size < MIN_MP4_BYTES
    except OSError:
        return True


def ark_download_existing(
    task_id: str,
    out_mp4: Path,
    *,
    project_root: Path,
    episode_id: str,
    wait_if_pending: bool,
) -> int:
    """已提交任务：先 download；失败且 wait_if_pending 则 wait 后再下。"""
    if not ARK_VIDEO_CLI.is_file():
        print(f"找不到 {ARK_VIDEO_CLI}", file=sys.stderr)
        return 1
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    base = [
        sys.executable,
        str(ARK_VIDEO_CLI),
        "download",
        "--task-id",
        task_id,
        "-o",
        str(out_mp4),
    ]

    def _run_download() -> int:
        r = subprocess.run(base, cwd=str(_REPO_ROOT))
        if r.returncode != 0:
            return r.returncode
        try:
            local_rel = str(out_mp4.resolve().relative_to(ROOT))
        except ValueError:
            local_rel = str(out_mp4.resolve())
        record_status(
            task_id,
            "succeeded",
            project_root=project_root,
            episode=episode_id,
            local_mp4=local_rel,
        )
        return 0

    if _run_download() == 0:
        return 0
    if not wait_if_pending:
        return 1
    print(f"  download 失败，轮询任务 {task_id} …", file=sys.stderr)
    return ark_wait_download(
        task_id, out_mp4, project_root=project_root, episode_id=episode_id
    )


def run_pull(ep_id: str, segments: list[dict], *, force: bool, wait_pending: bool) -> int:
    task_map = load_segment_task_map(ep_id)
    if not task_map:
        print(
            f"缺少 {GENERATED_DIR / ep_id / 'tasks.json'}，请先 git pull 或请同事提交任务登记",
            file=sys.stderr,
        )
        return 1

    ok = skip = fail = no_tid = 0
    for seg in segments:
        sid = seg.get("segment_id", "?")
        mp4 = GENERATED_DIR / ep_id / f"{sid}.mp4"
        if not mp4_needs_pull(mp4, force):
            print(f"⊙ {sid} 已有 {mp4.stat().st_size // 1024}KB，跳过")
            skip += 1
            continue
        tid = task_map.get(sid)
        if not tid:
            print(f"✗ {sid} tasks.json 中无 task_id（请同事生成后 push tasks.json）", file=sys.stderr)
            no_tid += 1
            continue
        print(f"↓ {sid} ← {tid}")
        rc = ark_download_existing(
            tid,
            mp4,
            project_root=ROOT,
            episode_id=ep_id,
            wait_if_pending=wait_pending,
        )
        if rc == 0:
            print(f"  ✓ {mp4.relative_to(ROOT)} ({mp4.stat().st_size // 1024}KB)")
            ok += 1
        else:
            print(f"  ✗ 下载失败（链接可能已过期 >24h 或任务未成功）", file=sys.stderr)
            fail += 1

    print(f"\n{ep_id} --pull: downloaded={ok} skipped={skip} no_task_id={no_tid} failed={fail}")
    return 1 if (fail or no_tid) else 0


def ark_wait_download(
    task_id: str,
    out_mp4: Path,
    *,
    project_root: Path,
    episode_id: str,
) -> int:
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
    if r2.returncode != 0:
        return r2.returncode
    try:
        local_rel = str(out_mp4.resolve().relative_to(ROOT))
    except ValueError:
        local_rel = str(out_mp4.resolve())
    record_status(
        task_id,
        "succeeded",
        project_root=project_root,
        episode=episode_id,
        local_mp4=local_rel,
    )
    return 0


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
    parser.add_argument(
        "--pull",
        action="store_true",
        help="按 segments.yaml + tasks.json 补下缺失段落（同事 push 任务后本地执行；需 ARK_API_KEY）",
    )
    parser.add_argument(
        "--pull-wait",
        action="store_true",
        help="与 --pull 合用：若任务未完成则轮询等待后再下载",
    )
    parser.add_argument(
        "--pull-force",
        action="store_true",
        help="与 --pull 合用：已存在 mp4 也重新下载",
    )
    parser.add_argument(
        "--concat",
        action="store_true",
        help="pull/submit 完成后执行 ffmpeg_concat_episode.sh 生成 EP##_full.mp4",
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

    if args.pull:
        if not (os.environ.get("ARK_API_KEY") or os.environ.get("VOLC_ARK_API_KEY")):
            print("--pull 需要 ARK_API_KEY", file=sys.stderr)
            return 1
        rc = run_pull(
            ep_id,
            segments,
            force=args.pull_force,
            wait_pending=args.pull_wait,
        )
        if rc != 0:
            return rc
        if args.concat:
            concat_sh = ROOT / "script" / "ffmpeg_concat_episode.sh"
            if not concat_sh.is_file():
                print(f"找不到 {concat_sh}", file=sys.stderr)
                return 1
            return subprocess.run(["bash", str(concat_sh), ep_id], cwd=str(ROOT)).returncode
        return 0

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
            if task_id:
                tasks_path = record_submit(
                    str(task_id),
                    body,
                    project_root=ROOT,
                    episode=ep_id,
                    project_name="天工开物",
                    segment_id=sid,
                )
                print(f"  archived → {tasks_path.relative_to(ROOT)}")
            if task_id and (args.wait or args.download):
                mp4 = GENERATED_DIR / ep_id / f"{sid}.mp4"
                rc = ark_wait_download(
                    str(task_id),
                    mp4,
                    project_root=ROOT,
                    episode_id=ep_id,
                )
                if rc == 0:
                    print(f"  downloaded {mp4.relative_to(ROOT)}")
                else:
                    return rc
            time.sleep(0.5)

    print(
        f"\n{ep_id}: segments_ready={ready} missing_entries={len(missing_all)} "
        f"duration_errors={len(duration_errors)} thin_warnings={len(thin_warnings)}"
    )
    narr_errors = validate_narrator_voice(episode)
    subtitle_errors = validate_subtitle_segments(episode)
    if narr_errors and args.check_only:
        print("\n旁白 NARR-001 校验失败：", file=sys.stderr)
        for line in narr_errors:
            print(f"  - {line}", file=sys.stderr)
    if subtitle_errors and args.check_only:
        print("\n字幕段校验失败：", file=sys.stderr)
        for line in subtitle_errors:
            print(f"  - {line}", file=sys.stderr)
    if thin_warnings and args.check_only:
        print("\n薄段建议合并（非 API 错误，但会造成时长/费用浪费）", file=sys.stderr)
    if duration_errors or narr_errors or subtitle_errors:
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
    if args.concat:
        concat_sh = ROOT / "script" / "ffmpeg_concat_episode.sh"
        if not concat_sh.is_file():
            print(f"找不到 {concat_sh}", file=sys.stderr)
            return 1
        return subprocess.run(["bash", str(concat_sh), ep_id], cwd=str(ROOT)).returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
