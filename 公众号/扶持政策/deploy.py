#!/usr/bin/env python3
"""把本地 dist 产物部署到 Cloudflare Pages，并核验线上版本。

默认只在七个部署产物与部署小仓库镜像不一致时部署；--dry-run 只看判断，
--force 无条件部署。密钥只从 600 权限的本地文件读取，不打印。
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
DEPLOY_DIR = Path.home() / "Movies" / "duanju-policy"
MIRROR = DEPLOY_DIR / "dist"
TOKEN_FILE = Path.home() / ".config" / "duanju-policy" / "cf_token"
LOCK_FILE = Path.home() / ".local" / "state" / "yiren-catalog" / "deploy.lock"
LOG_FILE = ROOT / "deploy_log.jsonl"

FILES = ("index.html", "policies.html", "catalog.js", "catalog.css",
         "catalog.json", "404.html", "_headers")
SITE = "https://duanju-policy.pages.dev"
PROJECT = "duanju-policy"
BRANCH = "main"
ACCOUNT_ID = "66e4284ea93f7d90a59b90e6879c36d0"
CST = timezone(timedelta(hours=8))


def now_iso() -> str:
    return datetime.now(CST).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def hashes(directory: Path) -> dict[str, str | None]:
    return {name: (sha256(directory / name) if (directory / name).is_file() else None)
            for name in FILES}


def _embedded_data(path: Path) -> dict | None:
    match = re.search(r'<script type="application/json" id="catalog-data">(.*?)</script>',
                      path.read_text(encoding="utf-8"), re.S)
    return json.loads(match.group(1)) if match else None


def fingerprint(name: str, directory: Path) -> str | None:
    """用于判断是否需要部署：忽略 maintenance.generated_at 的纯时间戳变化。"""
    path = directory / name
    if not path.is_file():
        return None
    if name == "catalog.json":
        data = json.loads(path.read_text(encoding="utf-8"))
    elif name in ("index.html", "policies.html"):
        data = _embedded_data(path)
        if data is None:
            return sha256(path)
    else:
        return sha256(path)
    if isinstance(data.get("maintenance"), dict):
        data["maintenance"].pop("generated_at", None)
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fingerprints(directory: Path) -> dict[str, str | None]:
    return {name: fingerprint(name, directory) for name in FILES}


def changed_files(local: dict[str, str | None], remote: dict[str, str | None]) -> list[str]:
    return [name for name in FILES if local[name] != remote[name]]


def check_build() -> tuple[bool, str]:
    proc = subprocess.run([sys.executable, str(ROOT / "build.py"), "--check"],
                          cwd=ROOT.parent.parent, capture_output=True, text=True)
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, output


def check_token() -> str:
    if not TOKEN_FILE.is_file():
        raise RuntimeError(f"缺少密钥文件：{TOKEN_FILE}")
    if TOKEN_FILE.stat().st_mode & 0o077:
        raise RuntimeError(f"密钥文件权限不是 600：{TOKEN_FILE}")
    token = TOKEN_FILE.read_text(encoding="utf-8").strip()
    if not token:
        raise RuntimeError("密钥文件为空")
    return token


def copy_verified() -> None:
    MIRROR.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        src, dst = DIST / name, MIRROR / name
        dst.write_bytes(src.read_bytes())
        if dst.read_bytes() != src.read_bytes():
            raise RuntimeError(f"拷贝校验失败：{name}")


def parse_deployment_url(output: str) -> str | None:
    match = re.search(r"https://[a-z0-9-]+\.duanju-policy\.pages\.dev", output)
    return match.group(0) if match else None


def deploy(token: str) -> tuple[str | None, str]:
    if not shutil.which("npx"):
        raise RuntimeError("找不到 npx")
    env = dict(os.environ, CLOUDFLARE_API_TOKEN=token, CLOUDFLARE_ACCOUNT_ID=ACCOUNT_ID)
    proc = subprocess.run(
        ["npx", "--yes", "wrangler@latest", "pages", "deploy", str(MIRROR),
         "--project-name", PROJECT, "--branch", BRANCH, "--commit-dirty=true"],
        env=env, capture_output=True, text=True, timeout=300)
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        raise RuntimeError("wrangler 部署失败：\n" + output[-1500:])
    return parse_deployment_url(output), output


def fetch(url: str) -> tuple[int, bytes, dict[str, str]]:
    request = urllib.request.Request(url, headers={"User-Agent": "yiren-deploy-check/1.0",
                                                   "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(request, timeout=20) as resp:
            return resp.status, resp.read(), {k.lower(): v for k, v in resp.headers.items()}
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), {k.lower(): v for k, v in exc.headers.items()}


def verify(local: dict[str, str], attempts: int = 12, delay: float = 3.0) -> dict:
    stamp = str(int(time.time()))
    last = {}
    for _ in range(attempts):
        status, body, headers = fetch(f"{SITE}/catalog.json?deploy={stamp}")
        index_status, index_body, index_headers = fetch(f"{SITE}/?deploy={stamp}")
        missing_status, _, _ = fetch(f"{SITE}/__deploy_check_{stamp}")
        live = {
            "catalog.json": hashlib.sha256(body).hexdigest() if status == 200 else None,
            "index.html": hashlib.sha256(index_body).hexdigest() if index_status == 200 else None,
        }
        last = {
            "catalog_status": status,
            "index_status": index_status,
            "missing_status": missing_status,
            "catalog_match": live["catalog.json"] == local["catalog.json"],
            "index_match": live["index.html"] == local["index.html"],
            "csp": "content-security-policy" in headers,
            "nosniff": headers.get("x-content-type-options") == "nosniff",
            "referrer": headers.get("referrer-policy") == "strict-origin-when-cross-origin",
        }
        if (last["catalog_status"] == 200 and last["index_status"] == 200
                and last["catalog_match"] and last["index_match"]
                and last["missing_status"] == 404
                and last["csp"] and last["nosniff"] and last["referrer"]):
            return {"ok": True, **last}
        time.sleep(delay)
    return {"ok": False, **last}


def append_log(record: dict) -> None:
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auto", action="store_true", help="仅在产物变化时部署（默认）")
    parser.add_argument("--force", action="store_true", help="产物未变也部署")
    parser.add_argument("--dry-run", action="store_true", help="只判断，不拷贝不部署")
    parser.add_argument("--trigger", default="auto", help="写入日志的触发来源")
    args = parser.parse_args()

    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    lock = LOCK_FILE.open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("已有部署在运行，跳过")
        return 0

    ok, message = check_build()
    if not ok:
        print("构建校验失败，停止部署：\n" + message)
        append_log({"at": now_iso(), "trigger": args.trigger, "action": "aborted",
                    "reason": "build --check failed", "detail": message[-800:]})
        return 1

    local = hashes(DIST)
    missing = [name for name, digest in local.items() if digest is None]
    if missing:
        print("dist 产物缺失：" + ", ".join(missing))
        return 1
    local_fp = fingerprints(DIST)
    remote_fp = fingerprints(MIRROR)
    changed = changed_files(local_fp, remote_fp)

    if not changed and not args.force:
        print("产物无变化，跳过部署：" + ", ".join(FILES))
        return 0
    if args.dry_run:
        print(f"需要部署；变化文件：{', '.join(changed) if changed else '（强制）'}")
        return 0

    if not DEPLOY_DIR.is_dir():
        print(f"部署小仓库不存在：{DEPLOY_DIR}")
        return 1
    try:
        token = check_token()
        copy_verified()
        url, output = deploy(token)
    except Exception as exc:  # noqa: BLE001
        print(str(exc))
        append_log({"at": now_iso(), "trigger": args.trigger, "action": "failed",
                    "changed": changed, "reason": str(exc)[-800:]})
        return 2

    result = verify(local)
    record = {
        "at": now_iso(),
        "trigger": args.trigger,
        "action": "deployed",
        "changed": changed,
        "deployment_url": url,
        "site": SITE,
        "verify": result,
        "files": {name: local[name][:12] for name in FILES},
    }
    append_log(record)
    if result["ok"]:
        print(f"部署完成并核验通过：{SITE}（{url or '未解析到预览 URL'}）")
        return 0
    print("部署已提交，但线上核验未通过：" + json.dumps(result, ensure_ascii=False))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
