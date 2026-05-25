#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Upload reference images to Volcengine TOS for permanent CDN hosting.

Volcengine TOS (Target Object Storage) provides permanent, non-expiring URLs
for reference images used in Seedance 2.0 API submissions — eliminating the
24-hour expiry limitation of Seedream-generated CDN URLs.

Usage:
    python3 tos_upload.py upload --file PATH --key KEY
    python3 tos_upload.py upload-dir --dir DIR --prefix PREFIX
    python3 tos_upload.py sync --project-root ROOT
    python3 tos_upload.py update-registry --project-root ROOT
    python3 tos_upload.py list [--prefix PREFIX]

Credential Resolution (first found wins):
    1. Shell environment variables (highest priority, for CI/automation)
    2. .env file in workspace root (/Users/leifu/Movies/dramas/.env)
    3. .cursor/mcp.json env section (from volc-jimeng or volc-ark entry)

Variables:
    VOLC_ACCESS_KEY  - Volcengine Access Key (required)
    VOLC_SECRET_KEY  - Volcengine Secret Key (required)
    TOS_BUCKET       - Bucket name (default: drama-reference-images)
    TOS_REGION       - Region (default: cn-beijing)
    TOS_ENDPOINT     - Endpoint (default: tos-cn-beijing.volces.com)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_BUCKET = "drama-reference-images"
DEFAULT_REGION = "cn-beijing"
DEFAULT_ENDPOINT = "tos-cn-beijing.volces.com"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm"}
ASSET_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

# Paths for credential sources (relative to workspace root)
_SCRIPT_DIR = Path(__file__).resolve().parent
_MCP_DIR = _SCRIPT_DIR.parent  # mcps/volc-ark/
_WORKSPACE_ROOT = _MCP_DIR.parent.parent  # /Users/leifu/Movies/dramas

_PLACEHOLDER_VALUES = frozenset([
    "你的火山引擎AK",
    "你的火山引擎SK",
    "your_ak",
    "your_sk",
    "your-access-key",
    "your-secret-key",
    "",
])


def _parse_dotenv(path: Path) -> dict[str, str]:
    """Parse a .env file manually (no dependencies).

    Handles:
      - KEY=VALUE
      - KEY="VALUE" or KEY='VALUE' (strips quotes)
      - Comments (#) and blank lines skipped
      - export KEY=VALUE (strips leading 'export ')
    """
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Strip optional 'export ' prefix
            if line.startswith("export "):
                line = line[7:]
            # Split on first '='
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Strip surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            result[key] = value
    except OSError:
        pass
    return result


def _load_mcp_json_env() -> dict[str, str]:
    """Load credentials from .cursor/mcp.json (volc-jimeng or volc-ark entry)."""
    mcp_path = _WORKSPACE_ROOT / ".cursor" / "mcp.json"
    if not mcp_path.is_file():
        return {}
    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    result: dict[str, str] = {}
    # Look in mcpServers for volc-jimeng or volc-ark entries
    servers = data.get("mcpServers", {})
    for name in ("volc-ark", "volc-jimeng"):
        entry = servers.get(name, {})
        env_section = entry.get("env", {})
        if isinstance(env_section, dict):
            for key, value in env_section.items():
                if isinstance(value, str) and key not in result:
                    result[key] = value
    return result


def _is_placeholder(value: str) -> bool:
    """Check if a credential value is a placeholder or empty."""
    return value.strip() in _PLACEHOLDER_VALUES


def _resolve_credential(key: str, env_vars: dict[str, str], dotenv_vars: dict[str, str],
                        mcp_vars: dict[str, str], default: str = "") -> str:
    """Resolve a credential value with priority: shell env > .env > mcp.json > default."""
    # 1. Shell environment (highest priority)
    val = env_vars.get(key, "").strip()
    if val and not _is_placeholder(val):
        return val
    # 2. .env file
    val = dotenv_vars.get(key, "").strip()
    if val and not _is_placeholder(val):
        return val
    # 3. mcp.json
    val = mcp_vars.get(key, "").strip()
    if val and not _is_placeholder(val):
        return val
    # 4. Default
    return default


def get_config() -> dict[str, str]:
    """Read TOS configuration with priority: env vars > .env > mcp.json."""
    # Gather all credential sources
    env_vars = dict(os.environ)
    dotenv_vars = _parse_dotenv(_WORKSPACE_ROOT / ".env")
    # Also check MCP-local .env
    dotenv_vars_mcp = _parse_dotenv(_MCP_DIR / ".env")
    # Merge: workspace root .env takes priority over MCP-local .env
    merged_dotenv = {**dotenv_vars_mcp, **dotenv_vars}
    mcp_vars = _load_mcp_json_env()

    return {
        "access_key": _resolve_credential("VOLC_ACCESS_KEY", env_vars, merged_dotenv, mcp_vars),
        "secret_key": _resolve_credential("VOLC_SECRET_KEY", env_vars, merged_dotenv, mcp_vars),
        "bucket": _resolve_credential("TOS_BUCKET", env_vars, merged_dotenv, mcp_vars, DEFAULT_BUCKET),
        "region": _resolve_credential("TOS_REGION", env_vars, merged_dotenv, mcp_vars, DEFAULT_REGION),
        "endpoint": _resolve_credential("TOS_ENDPOINT", env_vars, merged_dotenv, mcp_vars, DEFAULT_ENDPOINT),
    }


def check_credentials(cfg: dict[str, str]) -> bool:
    """Verify credentials are present; print setup instructions if not."""
    if not cfg["access_key"] or not cfg["secret_key"]:
        print("ERROR: TOS credentials not configured.\n", file=sys.stderr)
        print(
            "Credentials are loaded with this priority (first found wins):", file=sys.stderr)
        print("  1. Shell environment variables", file=sys.stderr)
        print("  2. .env file in workspace root", file=sys.stderr)
        print("  3. .cursor/mcp.json env section\n", file=sys.stderr)
        print(
            f"To configure in .env file, create {_WORKSPACE_ROOT / '.env'}:", file=sys.stderr)
        print("  VOLC_ACCESS_KEY=your_ak", file=sys.stderr)
        print("  VOLC_SECRET_KEY=your_sk", file=sys.stderr)
        print(f"  TOS_BUCKET={DEFAULT_BUCKET}\n", file=sys.stderr)
        print("Or add to .cursor/mcp.json under the volc-ark env section:",
              file=sys.stderr)
        print('  "VOLC_ACCESS_KEY": "your_ak",', file=sys.stderr)
        print('  "VOLC_SECRET_KEY": "your_sk",', file=sys.stderr)
        print(f'  "TOS_BUCKET": "{DEFAULT_BUCKET}"\n', file=sys.stderr)
        print("Or set shell environment variables (for CI/automation):",
              file=sys.stderr)
        print("  export VOLC_ACCESS_KEY='your-access-key'", file=sys.stderr)
        print("  export VOLC_SECRET_KEY='your-secret-key'\n", file=sys.stderr)
        print("Optional (with defaults):", file=sys.stderr)
        print(f"  TOS_BUCKET='{DEFAULT_BUCKET}'", file=sys.stderr)
        print(f"  TOS_REGION='{DEFAULT_REGION}'", file=sys.stderr)
        print(f"  TOS_ENDPOINT='{DEFAULT_ENDPOINT}'\n", file=sys.stderr)
        print("To obtain credentials:", file=sys.stderr)
        print("  1. Log in to Volcengine Console: https://console.volcengine.com/", file=sys.stderr)
        print("  2. Go to IAM > Access Keys", file=sys.stderr)
        print("  3. Create a new Access Key pair", file=sys.stderr)
        print("  4. Ensure the key has TOS read/write permissions", file=sys.stderr)
        return False
    return True


def build_public_url(cfg: dict[str, str], key: str) -> str:
    """Construct the permanent public URL for an object."""
    return f"https://{cfg['bucket']}.{cfg['endpoint']}/{key}"


def get_client(cfg: dict[str, str]):
    """Create and return a TOS client instance."""
    try:
        import tos
    except ImportError:
        print("ERROR: TOS SDK not installed.", file=sys.stderr)
        print("  pip install tos", file=sys.stderr)
        sys.exit(1)

    client = tos.TosClientV2(
        ak=cfg["access_key"],
        sk=cfg["secret_key"],
        endpoint=f"https://{cfg['endpoint']}",
        region=cfg["region"],
    )
    return client


def ensure_bucket(client, cfg: dict[str, str]) -> bool:
    """Check if bucket exists; auto-create with public-read ACL if not."""
    try:
        client.head_bucket(cfg["bucket"])
        return True
    except Exception as e:
        err_str = str(e)
        if '404' in err_str or 'NoSuchBucket' in err_str or 'not exist' in err_str.lower() or 'StatusCode: 404' in err_str:
            print(f"Bucket '{cfg['bucket']}' not found. Creating...")
            from tos.enum import ACLType
            client.create_bucket(cfg["bucket"], acl=ACLType.ACL_Public_Read)
            print(
                f"Created bucket '{cfg['bucket']}' with public-read ACL in {cfg['region']}")
            return True
        # Other error (permissions, network, etc.)
        print(
            f"ERROR: Cannot access bucket '{cfg['bucket']}': {e}", file=sys.stderr)
        return False


def object_exists(client, bucket: str, key: str) -> bool:
    """Check if an object already exists in the bucket."""
    try:
        client.head_object(bucket, key)
        return True
    except Exception:
        return False


def upload_file(client, cfg: dict[str, str], local_path: Path, key: str) -> dict[str, Any]:
    """Upload a single file to TOS with public-read ACL.

    Returns dict with key, url, size on success; raises on failure.
    """
    from tos.enum import ACLType

    file_size = local_path.stat().st_size

    with open(local_path, "rb") as f:
        client.put_object(
            bucket=cfg["bucket"],
            key=key,
            content=f,
            content_length=file_size,
            acl=ACLType.ACL_Public_Read,
        )

    url = build_public_url(cfg, key)
    return {"key": key, "url": url, "size": file_size}


# ---------------------------------------------------------------------------
# CLI Commands
# ---------------------------------------------------------------------------

def cmd_upload(args: argparse.Namespace) -> int:
    """Upload a single file."""
    cfg = get_config()
    if not check_credentials(cfg):
        return 1

    local_path = Path(args.file).expanduser().resolve()
    if not local_path.is_file():
        print(f"ERROR: File not found: {local_path}", file=sys.stderr)
        return 1

    key = args.key or local_path.name

    client = get_client(cfg)
    if not ensure_bucket(client, cfg):
        return 1

    try:
        result = upload_file(client, cfg, local_path, key)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as e:
        print(f"ERROR: Upload failed: {e}", file=sys.stderr)
        return 1


def cmd_upload_dir(args: argparse.Namespace) -> int:
    """Upload all image files from a directory."""
    cfg = get_config()
    if not check_credentials(cfg):
        return 1

    dir_path = Path(args.dir).expanduser().resolve()
    if not dir_path.is_dir():
        print(f"ERROR: Directory not found: {dir_path}", file=sys.stderr)
        return 1

    prefix = args.prefix.rstrip("/") + "/" if args.prefix else ""

    # Collect image files
    files = sorted(
        f for f in dir_path.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    )

    if not files:
        print(f"No image files found in {dir_path}")
        return 0

    client = get_client(cfg)
    if not ensure_bucket(client, cfg):
        return 1

    uploaded = 0
    skipped = 0
    failed = 0

    for f in files:
        key = prefix + f.name
        if object_exists(client, cfg["bucket"], key):
            print(f"  SKIP (exists): {key}")
            skipped += 1
            continue
        try:
            result = upload_file(client, cfg, f, key)
            print(f"  UPLOADED: {key} ({result['size']:,} bytes)")
            uploaded += 1
        except Exception as e:
            print(f"  FAILED: {key} — {e}", file=sys.stderr)
            failed += 1

    print(
        f"\nSummary: {uploaded} uploaded, {skipped} skipped, {failed} failed")
    return 0 if failed == 0 else 1


def cmd_sync(args: argparse.Namespace) -> int:
    """Smart sync for drama project: upload looks + scenes + props + generated videos, update registry."""
    cfg = get_config()
    if not check_credentials(cfg):
        return 1

    project_root = Path(args.project_root).expanduser().resolve()
    assets_dir = project_root / "assets"

    if not assets_dir.is_dir():
        print(
            f"ERROR: assets/ directory not found at {assets_dir}", file=sys.stderr)
        return 1

    client = get_client(cfg)
    if not ensure_bucket(client, cfg):
        return 1

    total_uploaded = 0
    total_skipped = 0
    total_failed = 0

    # Directories to sync: (local_subdir, tos_prefix, recursive, extensions)
    project_name = project_root.name
    sync_dirs = [
        ("looks", "looks", False, IMAGE_EXTENSIONS),
        ("scenes", "scenes", False, IMAGE_EXTENSIONS),
        ("props", "props", False, IMAGE_EXTENSIONS),
        ("generated", f"generated/{project_name}", True, VIDEO_EXTENSIONS),
    ]

    for subdir, prefix, recursive, extensions in sync_dirs:
        local_dir = assets_dir / subdir
        if not local_dir.is_dir():
            continue

        if recursive:
            files = sorted(
                f for f in local_dir.rglob("*")
                if f.is_file() and f.suffix.lower() in extensions
            )
        else:
            files = sorted(
                f for f in local_dir.iterdir()
                if f.is_file() and f.suffix.lower() in extensions
            )

        if not files:
            continue

        file_type = "videos" if recursive else "images"
        print(f"\n--- {subdir}/ ({len(files)} {file_type}) ---")

        # Track all files for registry (uploaded + previously existing)
        registry_entries: list[tuple[str, str, int]] = []

        for f in files:
            if recursive:
                key = f"{prefix}/{f.relative_to(local_dir)}"
                rel_path = str(f.relative_to(local_dir))
            else:
                key = f"{prefix}/{f.name}"
                rel_path = ""
            tos_url = build_public_url(cfg, key)

            if object_exists(client, cfg["bucket"], key):
                print(f"  SKIP: {key}")
                total_skipped += 1
                if recursive:
                    registry_entries.append(
                        (rel_path, tos_url, f.stat().st_size))
                continue
            try:
                result = upload_file(client, cfg, f, key)
                print(f"  UPLOADED: {key} ({result['size']:,} bytes)")
                total_uploaded += 1
                if recursive:
                    registry_entries.append(
                        (rel_path, tos_url, result["size"]))
            except Exception as e:
                print(f"  FAILED: {key} — {e}", file=sys.stderr)
                total_failed += 1

        # Always rebuild generated/ cdn_urls.json from full TOS state
        if recursive and registry_entries:
            _update_video_registry(
                cfg, project_root, subdir, prefix, registry_entries)

    print(
        f"\n=== Sync complete: {total_uploaded} uploaded, {total_skipped} skipped, {total_failed} failed ===")

    # Auto-update registry after sync
    if total_uploaded > 0:
        print("\nUpdating cdn_urls.json registries...")
        _update_registry_for_project(cfg, project_root)

    return 0 if total_failed == 0 else 1


def cmd_update_registry(args: argparse.Namespace) -> int:
    """Update cdn_urls.json files with permanent TOS URLs."""
    cfg = get_config()
    if not check_credentials(cfg):
        return 1

    project_root = Path(args.project_root).expanduser().resolve()
    _update_registry_for_project(cfg, project_root)
    return 0


def _update_registry_for_project(cfg: dict[str, str], project_root: Path) -> None:
    """Update cdn_urls.json in looks/ and scenes/ with tos_url fields."""
    assets_dir = project_root / "assets"

    for subdir, prefix in [("looks", "looks"), ("scenes", "scenes")]:
        registry_path = assets_dir / subdir / "cdn_urls.json"
        if not registry_path.is_file():
            print(f"  No {subdir}/cdn_urls.json found, skipping.")
            continue

        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"  ERROR reading {registry_path}: {e}", file=sys.stderr)
            continue

        updated = 0
        for asset_id, entry in registry.items():
            if not isinstance(entry, dict):
                continue
            # Determine the filename
            local_name = entry.get("local", "")
            if not local_name:
                local_name = f"{asset_id}.png"
            key = f"{prefix}/{local_name}"
            tos_url = build_public_url(cfg, key)

            if entry.get("tos_url") != tos_url:
                entry["tos_url"] = tos_url
                updated += 1

        if updated > 0:
            registry_path.write_text(
                json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(
                f"  Updated {subdir}/cdn_urls.json: {updated} entries got tos_url")
        else:
            print(f"  {subdir}/cdn_urls.json: already up-to-date")


def _update_video_registry(cfg: dict[str, str], project_root: Path, subdir: str,
                           prefix: str, uploaded: list[tuple[str, str, int]]) -> None:
    """Write/update generated/cdn_urls.json with TOS URLs for videos."""
    registry_path = project_root / "assets" / subdir / "cdn_urls.json"

    # Load existing registry if any
    registry: dict[str, dict[str, Any]] = {}
    if registry_path.is_file():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    new_count = 0
    for rel_path, tos_url, size in uploaded:
        entry = registry.get(rel_path, {})
        entry["local"] = rel_path
        entry["tos_url"] = tos_url
        entry["size"] = size
        registry[rel_path] = entry
        new_count += 1

    if new_count > 0:
        registry_path.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"  Updated {subdir}/cdn_urls.json: {new_count} video entries")


def cmd_list(args: argparse.Namespace) -> int:
    """List objects in bucket with optional prefix."""
    cfg = get_config()
    if not check_credentials(cfg):
        return 1

    client = get_client(cfg)
    if not ensure_bucket(client, cfg):
        return 1

    prefix = args.prefix or ""
    try:
        result = client.list_objects_type2(
            bucket=cfg["bucket"],
            prefix=prefix,
            max_keys=1000,
        )
        contents = result.contents or []
        if not contents:
            print(f"No objects found with prefix '{prefix}'")
            return 0

        print(
            f"Objects in {cfg['bucket']}/{prefix} ({len(contents)} items):\n")
        for obj in contents:
            url = build_public_url(cfg, obj.key)
            size_kb = (obj.size or 0) / 1024
            print(f"  {obj.key:50s}  {size_kb:8.1f} KB  {url}")
        return 0
    except Exception as e:
        print(f"ERROR: List failed: {e}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="tos_upload",
        description="Upload reference images to Volcengine TOS for permanent CDN hosting.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Credential Resolution (first found wins):
  1. Shell environment variables (highest priority)
  2. .env file at workspace root
  3. .cursor/mcp.json env section (volc-ark or volc-jimeng)

Variables:
  VOLC_ACCESS_KEY   Volcengine Access Key (required)
  VOLC_SECRET_KEY   Volcengine Secret Key (required)
  TOS_BUCKET        Bucket name (default: drama-reference-images)
  TOS_REGION        Region (default: cn-beijing)
  TOS_ENDPOINT      Endpoint (default: tos-cn-beijing.volces.com)

URL Format:
  https://{TOS_BUCKET}.{TOS_ENDPOINT}/{key}
  Example: https://drama-reference-images.tos-cn-beijing.volces.com/looks/CHAR-001-L01.png

Examples:
  # Upload a single image
  python3 tos_upload.py upload --file assets/looks/CHAR-001-L01.png --key looks/CHAR-001-L01.png

  # Upload all images from a directory
  python3 tos_upload.py upload-dir --dir assets/looks/ --prefix looks/

  # Sync entire project (looks + scenes + props)
  python3 tos_upload.py sync --project-root /path/to/drama/project

  # Update cdn_urls.json with permanent TOS URLs
  python3 tos_upload.py update-registry --project-root /path/to/drama/project

  # List uploaded images
  python3 tos_upload.py list --prefix looks/
""",
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands")

    # upload
    p_upload = subparsers.add_parser("upload", help="Upload a single file")
    p_upload.add_argument("--file", "-f", required=True,
                          help="Local file path")
    p_upload.add_argument(
        "--key", "-k", help="Object key in bucket (default: filename)")

    # upload-dir
    p_upload_dir = subparsers.add_parser(
        "upload-dir", help="Upload all images from directory")
    p_upload_dir.add_argument(
        "--dir", "-d", required=True, help="Source directory")
    p_upload_dir.add_argument(
        "--prefix", "-p", default="", help="Key prefix in bucket")

    # sync
    p_sync = subparsers.add_parser("sync", help="Smart sync for drama project")
    p_sync.add_argument("--project-root", "-r", required=True,
                        help="Drama project root directory")

    # update-registry
    p_registry = subparsers.add_parser(
        "update-registry", help="Update cdn_urls.json with TOS URLs")
    p_registry.add_argument("--project-root", "-r",
                            required=True, help="Drama project root directory")

    # list
    p_list = subparsers.add_parser("list", help="List objects in bucket")
    p_list.add_argument("--prefix", "-p", default="",
                        help="Filter by key prefix")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "upload": cmd_upload,
        "upload-dir": cmd_upload_dir,
        "sync": cmd_sync,
        "update-registry": cmd_update_registry,
        "list": cmd_list,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
