#!/usr/bin/env python3
"""YAML 格式门控 — 检查 shots.yaml 和 segments.yaml 的格式一致性。drama-director G5 首项检查。"""
import argparse, os, re, sys, yaml

SHOT_FIELDS = ["shot_id", "shot_no", "mode", "duration_sec", "refs", "assets", "api", "dialogue"]
SEGMENT_FIELDS = ["segment_id", "shot_ids", "duration_sec", "speakers", "refs", "assets", "api", "transition_to_next"]
TOP_SHOT = ["episode_id", "defaults", "shots"]
TOP_SEGMENT = ["episode_id", "defaults", "voice_prompts", "segments"]
DEFAULTS_FIELDS = ["endpoint", "model", "ratio", "resolution", "generate_audio",
                   "watermark", "prompt_suffix", "negative_prompt"]
TOS_PATTERN = re.compile(r'https://drama-reference-images\.tos-cn-beijing\.volces\.com/')


def load_yaml(fpath: str) -> tuple:
    """Load YAML, return (data, errors)."""
    try:
        with open(fpath) as f:
            content = f.read()
        data = yaml.safe_load(content)
        return data, []
    except yaml.YAMLError as e:
        return None, [f"YAML 语法错误: {e}"]
    except Exception as e:
        return None, [f"读取失败: {e}"]


def check_semicolons(fpath: str) -> list:
    """Check for ; used as separator in flow mappings."""
    errors = []
    with open(fpath) as f:
        for i, line in enumerate(f, 1):
            stripped = line.strip()
            # Pattern 1: { ... ; ... }  — semicolon inside braces
            if re.search(r'\{\s*\S+[^,;]*;\s*\S+.*\}', stripped):
                errors.append(f"第{i}行: 流式映射中用 ';' 分隔，应改为 ','")
            # Pattern 2: key: value; key: value — semicolon-separated flow without braces
            elif ';' in stripped and not stripped.startswith('#'):
                # Check if it's a flow-style mapping using ;
                # Valid YAML flow: key: val, key: val or {key: val, key: val}
                if re.match(r'^\s*\w+[^:]*:\s*\S+.*;\s*\w+.*:\s*\S+', stripped):
                    errors.append(f"第{i}行: 用 ';' 分隔键值对，应改为 ','（或展开为多行缩进）")
    return errors


def check_top_fields(data: dict, required: list, label: str) -> list:
    errors = []
    for f in required:
        if f not in data:
            errors.append(f"{label} 缺顶层字段: {f}")
    return errors


def check_defaults(data: dict, label: str) -> list:
    errors = []
    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        return [f"{label} defaults 不是字典"]
    for f in DEFAULTS_FIELDS:
        if f not in defaults:
            errors.append(f"{label} defaults 缺: {f}")
    return errors


def check_urls(data: dict, label: str) -> list:
    """Recursively find all string values that look like URLs and verify TOS format."""
    errors = []
    def walk(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")
        elif isinstance(obj, str):
            if obj.startswith("https://") and "tos-cn-beijing" in obj:
                if not TOS_PATTERN.match(obj):
                    errors.append(f"{label}{path}: URL 不是 TOS 永久格式: {obj[:80]}...")
                elif "X-Tos-Expires" in obj or "X-Tos-Signature" in obj:
                    errors.append(f"{label}{path}: 使用了临时预签名 URL（含 X-Tos-Expires/Signature），应改用永久 TOS URL")
    walk(data)
    return errors


def check_shots(data: dict) -> list:
    errors = []
    shots = data.get("shots", [])
    if not isinstance(shots, list):
        return ["shots 字段不是数组"]
    for i, shot in enumerate(shots):
        if not isinstance(shot, dict):
            errors.append(f"shots[{i}] 不是字典"); continue
        for f in SHOT_FIELDS:
            if f not in shot:
                errors.append(f"shots[{i}] 缺字段: {f}")
        # Check dialogue
        dialogue = shot.get("dialogue", [])
        if isinstance(dialogue, list):
            for j, d in enumerate(dialogue):
                if isinstance(d, dict):
                    for ff in ["speaker", "line"]:
                        if ff not in d:
                            errors.append(f"shots[{i}].dialogue[{j}] 缺: {ff}")
    return errors


def check_segments(data: dict) -> list:
    errors = []
    segs = data.get("segments", [])
    if not isinstance(segs, list):
        return ["segments 字段不是数组"]
    for i, seg in enumerate(segs):
        if not isinstance(seg, dict):
            errors.append(f"segments[{i}] 不是字典"); continue
        for f in SEGMENT_FIELDS:
            if f not in seg:
                errors.append(f"segments[{i}] 缺字段: {f}")
    return errors


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ep", required=True)
    p.add_argument("--project-root", required=True)
    p.add_argument("--type", default="both", choices=["shots", "segments", "both"])
    a = p.parse_args()

    base = os.path.join(a.project_root, "剧本", a.ep)
    all_errors = []

    for fname, label, top_fields, item_check in [
        (f"{a.ep}_shots.yaml", "shots", TOP_SHOT, check_shots),
        (f"{a.ep}_segments.yaml", "segments", TOP_SEGMENT, check_segments),
    ]:
        if a.type not in ("both", label): continue
        fpath = os.path.join(base, fname)
        if not os.path.exists(fpath):
            all_errors.append(f"文件不存在: {fpath}"); continue

        data, errors = load_yaml(fpath)
        print(f"📋 {label.upper()} — {a.ep}")
        if data is None:
            for e in errors: print(f"  ❌ {e}")
            all_errors.extend(errors); continue

        checks = [
            ("分号检测", lambda: check_semicolons(fpath)),
            ("顶层字段", lambda: check_top_fields(data, top_fields, label)),
            ("defaults", lambda: check_defaults(data, label)),
            ("子项字段", lambda: item_check(data)),
            ("URL格式", lambda: check_urls(data, label)),
        ]
        for name, fn in checks:
            errs = fn()
            print(f"  {'✅' if not errs else '❌'} {name}")
            for e in errs: print(f"     {e}")
            all_errors.extend(errs)

    if all_errors:
        print(f"\n❌ {len(all_errors)} 个问题"); sys.exit(1)
    print("\n✅ 全部通过"); sys.exit(0)


if __name__ == "__main__":
    main()
