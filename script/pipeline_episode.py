#!/usr/bin/env python3
"""
Reusable episode pipeline: submit → poll → download → TOS → tasks.json (full I/O).

Usage (per-episode script imports and calls):
    from pipeline_episode import Pipeline

    pipeline = Pipeline(project_root, episode="EP02", segments=[...])
    pipeline.run()

Or from CLI with a JSON segment definition file:
    python3 script/pipeline_episode.py dramas/<drama>/assets/generated/EP02/segments.json
"""
import subprocess, json, sys, time, os
from typing import Any

SEEDANCE_CLI = "mcps/volc-ark/scripts/ark_seedance_video.py"
TOS_CLI = "mcps/volc-ark/scripts/tos_upload.py"


class Pipeline:
    def __init__(
        self,
        project_root: str,
        episode: str,
        segments: list[dict[str, Any]],
        ark_api_key: str | None = None,
        model: str = "doubao-seedance-2-0-fast-260128",
        ratio: str = "9:16",
        resolution: str = "720p",
        poll_interval: int = 15,
        max_wait: int = 900,
    ):
        self.project_root = os.path.abspath(project_root)
        self.episode = episode.upper()
        self.segments = segments
        self.api_key = ark_api_key or os.environ.get("ARK_API_KEY", "")
        self.model = model
        self.ratio = ratio
        self.resolution = resolution
        self.poll_interval = poll_interval
        self.max_wait = max_wait
        self.ep_dir = os.path.join(self.project_root, "assets", "generated", self.episode)
        self.tasks_path = os.path.join(self.ep_dir, "tasks.json")
        self.submit_path = os.path.join(self.ep_dir, "submit_results.json")

        self._env = {**os.environ, "ARK_API_KEY": self.api_key}
        self._task_map: dict[str, str] = {}  # segment_id → task_id
        self._results: list[dict] = []

    # ── Step 1: Submit ──────────────────────────────────────────

    def submit(self) -> list[dict]:
        """Submit all segments. Writes segment_id → task_id map."""
        print(f"[{self.episode}] Submitting {len(self.segments)} segments...\n", flush=True)

        for i, seg in enumerate(self.segments):
            sid = seg["id"]
            cmd = [
                "/usr/bin/python3", SEEDANCE_CLI, "create",
                "--text", seg["text"],
                "--duration", str(seg["duration"]),
                "--ratio", self.ratio,
                "--resolution", self.resolution,
                "--generate-audio",
            ]
            for ref in seg.get("refs", []):
                cmd += ["--image-url", ref]

            print(f"  [{i+1}/{len(self.segments)}] {sid} ({seg['duration']}s)...", flush=True, end=" ")
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=self._env)
            if r.returncode != 0:
                print(f"✗ {r.stderr[:120]}", flush=True)
                self._results.append({"segment_id": sid, "status": "submit_error", "error": r.stderr[:300]})
            else:
                data = json.loads(r.stdout)
                tid = data.get("task_id", "?")
                self._task_map[sid] = tid
                self._results.append({"segment_id": sid, "task_id": tid, "status": "submitted"})
                print(f"✓ {tid}", flush=True)

            if i < len(self.segments) - 1:
                time.sleep(1.5)

        # Save submit results and task map
        os.makedirs(self.ep_dir, exist_ok=True)
        with open(self.submit_path, "w") as f:
            json.dump({"task_map": self._task_map, "results": self._results}, f, ensure_ascii=False, indent=2)
            f.write("\n")
        return self._results

    # ── Step 2: Poll ────────────────────────────────────────────

    def _check_one(self, seg_id: str, task_id: str) -> dict:
        r = subprocess.run(
            ["/usr/bin/python3", SEEDANCE_CLI, "get", "--task-id", task_id],
            capture_output=True, text=True, timeout=60, env=self._env,
        )
        return json.loads(r.stdout)

    def poll(self) -> dict[str, dict]:
        """Poll until all tasks complete. Returns {segment_id: task_data}."""
        print(f"\n[{self.episode}] Polling {len(self._task_map)} tasks...\n", flush=True)

        remaining = dict(self._task_map)
        all_data: dict[str, dict] = {}
        deadline = time.time() + self.max_wait

        while remaining and time.time() < deadline:
            done_now = []
            for sid, tid in list(remaining.items()):
                try:
                    data = self._check_one(sid, tid)
                    status = data.get("status", "?")
                    if status in ("succeeded", "failed", "cancelled", "expired"):
                        print(f"  {sid}: {status}", flush=True)
                        all_data[sid] = data
                        done_now.append(sid)
                except Exception as e:
                    print(f"  {sid}: poll error - {e}", flush=True)
            for sid in done_now:
                remaining.pop(sid)
            if remaining:
                print(f"  [{len(remaining)} remaining...]", flush=True)
                time.sleep(self.poll_interval)

        if remaining:
            print(f"\nTimeout! {len(remaining)} still pending: {list(remaining.keys())}", flush=True)
            for sid in remaining:
                all_data[sid] = {"status": "timeout", "task_id": self._task_map.get(sid)}

        return all_data

    # ── Step 3: Download ────────────────────────────────────────

    def download(self, all_data: dict[str, dict]) -> int:
        """Download succeeded segments. Returns count downloaded."""
        print(f"\n[{self.episode}] Downloading...\n", flush=True)
        count = 0

        for seg in self.segments:
            sid = seg["id"]
            data = all_data.get(sid, {})
            if data.get("status") != "succeeded":
                print(f"  {sid}: SKIP (status={data.get('status','?')})", flush=True)
                continue
            vu = data.get("video_url", "")
            if not vu:
                print(f"  {sid}: SKIP (no video_url)", flush=True)
                continue

            out_name = f"{self.episode}-{sid}.mp4"
            out_path = os.path.join(self.ep_dir, out_name)
            tid = self._task_map.get(sid, "")

            print(f"  {sid} → {out_name} ...", flush=True, end=" ")
            r = subprocess.run(
                ["/usr/bin/python3", SEEDANCE_CLI, "download", "--task-id", tid, "--output", out_path],
                capture_output=True, text=True, timeout=120, env=self._env,
            )
            if r.returncode == 0:
                size = os.path.getsize(out_path) if os.path.exists(out_path) else 0
                print(f"✓ {size/1024/1024:.1f}MB", flush=True)
                count += 1
            else:
                print(f"✗ {r.stderr[:120]}", flush=True)

        print(f"\n  Downloaded: {count}/{len(self.segments)}")
        return count

    # ── Step 4: TOS Upload ──────────────────────────────────────

    def upload_tos(self) -> int:
        """Upload generated/ to TOS. Returns exit code."""
        print(f"\n[{self.episode}] Uploading to TOS...\n", flush=True)
        r = subprocess.run(
            ["/usr/bin/python3", TOS_CLI, "sync", "--project-root", self.project_root],
            capture_output=True, text=True, timeout=300, env=self._env,
        )
        print(r.stdout[-500:] if len(r.stdout) > 500 else r.stdout, flush=True)
        if r.returncode != 0:
            print(r.stderr[-500:] if len(r.stderr) > 500 else r.stderr, flush=True)
        return r.returncode

    # ── Step 5: Write tasks.json (full I/O) ─────────────────────

    def write_tasks_json(self, all_data: dict[str, dict]):
        """Write tasks.json with complete input + output for every segment."""
        print(f"\n[{self.episode}] Writing tasks.json with full I/O...", flush=True)

        segments_out = []
        for seg in self.segments:
            sid = seg["id"]
            data = all_data.get(sid, {})
            task = data.get("task", {})
            entry = {
                "segment_id": sid,
                "input": {
                    "model": self.model,
                    "ratio": self.ratio,
                    "resolution": self.resolution,
                    "generate_audio": True,
                    "text": seg["text"],
                    "ref_images": [os.path.basename(p) for p in seg.get("refs", [])],
                },
                "output": {
                    "task_id": self._task_map.get(sid),
                    "status": data.get("status", "?"),
                    "video_url": data.get("video_url", ""),
                    "usage": task.get("usage", {}),
                },
            }
            segments_out.append(entry)

        result = {
            "episode": self.episode,
            "drama": os.path.basename(self.project_root),
            "generated_at": time.strftime("%Y-%m-%d"),
            "model": self.model,
            "ratio": self.ratio,
            "resolution": self.resolution,
            "total_segments": len(segments_out),
            "segments": segments_out,
        }

        os.makedirs(self.ep_dir, exist_ok=True)
        with open(self.tasks_path, "w") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            f.write("\n")

        print(f"  ✓ {self.tasks_path} ({len(segments_out)} segments)", flush=True)
        for t in segments_out:
            imgs = t["input"]["ref_images"]
            print(f"    {t['segment_id']}: in={len(t['input']['text'])}chars/{len(imgs)}imgs → out={t['output']['status']}", flush=True)

    # ── Orchestrator ────────────────────────────────────────────

    def run(self, skip_tos: bool = False, skip_download: bool = False):
        """Run full pipeline: submit → poll → download → TOS → tasks.json."""
        if not self.api_key:
            print("ERROR: No ARK_API_KEY set.", file=sys.stderr)
            return 1

        print(f"\n{'='*60}")
        print(f"  Pipeline: {os.path.basename(self.project_root)} / {self.episode}")
        print(f"  Segments: {len(self.segments)}")
        print(f"  Model: {self.model}")
        print(f"{'='*60}\n")

        # 1. Submit
        self.submit()
        if not self._task_map:
            print("FATAL: No segments submitted.", file=sys.stderr)
            return 1

        # 2. Poll
        all_data = self.poll()

        # 3. Download
        if not skip_download:
            self.download(all_data)

        # 4. TOS
        if not skip_tos:
            self.upload_tos()

        # 5. Write full I/O tasks.json
        self.write_tasks_json(all_data)

        succeeded = sum(1 for d in all_data.values() if d.get("status") == "succeeded")
        print(f"\n{'='*60}")
        print(f"  Done: {succeeded}/{len(self.segments)} succeeded")
        print(f"  Tasks: {self.tasks_path}")
        print(f"{'='*60}\n")

        return 0 if succeeded == len(self.segments) else 1


# ── CLI entry point (for JSON-based episode definition) ─────────

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 pipeline_episode.py <project_root> <episode> <segments.json>", file=sys.stderr)
        print("  segments.json: [{\"id\":\"SEG01\",\"duration\":10,\"text\":\"...\",\"refs\":[\"path.png\"]}, ...]", file=sys.stderr)
        sys.exit(1)

    project_root = sys.argv[1]
    episode = sys.argv[2]
    segments_file = sys.argv[3]

    with open(segments_file) as f:
        segments = json.load(f)

    pipeline = Pipeline(project_root, episode, segments)
    sys.exit(pipeline.run())
