#!/usr/bin/env python3
"""YAML 格式门控 — 检查 shots.yaml 和 segments.yaml 的格式一致性。drama-director G5 首项检查。"""
import argparse, os, re, sys, yaml

SHOT_FIELDS = ["shot_id", "shot_no", "mode", "duration_sec", "refs", "assets", "api", "dialogue"]
SEGMENT_FIELDS = ["segment_id", "shot_ids", "duration_sec", "speakers", "refs", "assets", "api"]
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

def check_content_roles(data: dict, label: str) -> list:
    """Check content_roles format is [{file, role, label}], not flat map."""
    errors = []
    items = data.get("segments", []) if label == "segments" else data.get("shots", [])
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        api = item.get("api", {})
        if not isinstance(api, dict):
            continue
        cr = api.get("content_roles", [])
        if isinstance(cr, dict):
            errors.append(f"{label}[{i}].api.content_roles 是扁平 map，应为对象列表")
        elif isinstance(cr, list):
            for j, role_item in enumerate(cr):
                if isinstance(role_item, dict):
                    for ff in ["file", "role", "label"]:
                        if ff not in role_item:
                            errors.append(f"{label}[{i}].content_roles[{j}] 缺: {ff}")
    return errors


def check_warning_comments(fpath: str) -> list:
    """Check for ⚠️ comments in YAML — indicates fabricated data."""
    errors = []
    with open(fpath) as f:
        for i, line in enumerate(f, 1):
            if '⚠️' in line and '#' in line:
                errors.append(f"第{i}行: 含 ⚠️ 注释——voice_prompt 来源不明，应补充声音卡片而非标注警告")
    return errors


def check_tu_refs(data: dict, label: str) -> list:
    """Check api.text uses 图N references instead of character names.

    仅适用于旧格式（无结构化 api 块）；已迁移的结构化块（subjects+shots）
    text 仅为兜底产物，图N/角色名校验由 check_structured_api 负责，此处跳过。"""
    errors = []
    import re
    items = data.get("segments", []) if label == "segments" else data.get("shots", [])
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        api = item.get("api", {})
        if not isinstance(api, dict):
            continue
        if isinstance(api.get("subjects"), list) and isinstance(api.get("shots"), list):
            continue  # 结构化块跳过（text 为兜底）
        text = api.get("text", "")
        if not isinstance(text, str):
            continue
        # Find lines with 镜头描述 (lens descriptions only, not对白 lines)
        lens_lines = re.findall(r'镜头\d+[^。]*', text)
        for ll in lens_lines:
            # Check for 2-3 char Chinese sequence that could be a name, but exclude:
            # - Words after 对白/图N markers
            # - Common verbs/adverbs/prepositions
            # Only check if no图N reference found in the same line
            if '图1' not in ll and '图2' not in ll and '图3' not in ll and '图4' not in ll and '图5' not in ll:
                if re.search(r'(?:推开|站起|坐下|走进|走出|拿起|放下|看着|转头|伸手|起身|转身|低头|抬头)\b', ll):
                    # Has action verb but no图N - likely using character name
                    errors.append(f"{label}[{i}].api.text 镜头描述可能含角色名而非图N引用")
                    break
    return errors


def check_structured_api(data: dict, label: str) -> list:
    """结构化 api 块校验（P2 主推写法）：speakers.subject 必须命中 subjects 的 id；

    voice / dialogue 必须非空。画外音角色（未出现在 subjects 的 speaker，如电话里的
    周叔/江野）允许 subject 非 ID，但 voice 仍须非空（声音卡片 P0 全文透传）。
    仅校验存在 subjects+shots 的结构化块；旧 api.text 写法跳过。"""
    errors = []
    items = data.get("segments", []) if label == "segments" else data.get("shots", [])
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        api = item.get("api", {})
        if not isinstance(api, dict):
            continue
        subjects = api.get("subjects")
        shots = api.get("shots")
        if not isinstance(subjects, list) or not isinstance(shots, list):
            continue  # 旧格式（仅 api.text）不校验
        sub_ids = set()
        sub_names = set()
        for si, s in enumerate(subjects):
            if isinstance(s, dict) and s.get("id"):
                sub_ids.add(str(s["id"]))
            if isinstance(s, dict) and s.get("file"):
                sub_ids.add(str(s["file"]))
            if isinstance(s, dict) and s.get("name"):
                sub_names.add(str(s["name"]))
            # role 必须是受控枚举（character/scene/prop），非法值会丢 LOCK FACE / 场景声明
            if isinstance(s, dict):
                r = str(s.get("role") or "").strip()
                if r not in ("character", "scene", "prop"):
                    errors.append(
                        f"{label}[{i}].api.subjects[{si}] role '{r}' 非法——"
                        f"必须为 character/scene/prop（非法值会导致 LOCK FACE 声明丢失）")
            # character 必须声明 gender（渲染器据此输出 LOCK HER/HIS FACE；
            # 缺省默认 female → 男性角色会错误输出 LOCK HER FACE）
            if isinstance(s, dict) and str(s.get("role")).strip() == "character":
                g = str(s.get("gender") or "").strip().lower()
                if g not in ("female", "male", "女", "男"):
                    errors.append(
                        f"{label}[{i}].api.subjects[{si}] character "
                        f"'{s.get('name') or s.get('id')}' 缺 gender（female/male）——"
                        f"渲染器默认 female，男性角色会错误输出 LOCK HER FACE")
        for j, sh in enumerate(shots):
            if not isinstance(sh, dict):
                continue
            for k, sp in enumerate(sh.get("speakers") or []):
                if not isinstance(sp, dict):
                    continue
                subj = str(sp.get("subject") or "").strip()
                if not subj:
                    errors.append(f"{label}[{i}].api.shots[{j}].speakers[{k}] 缺 subject")
                    continue
                if subj in sub_names and subj not in sub_ids:
                    # 命中角色名而非素材 ID——锁脸关联断裂（v1 迁移 bug 形态）
                    errors.append(
                        f"{label}[{i}].api.shots[{j}].speakers[{k}] subject '{subj}' "
                        f"是角色名而非素材 ID（应引用 subjects 的 id）")
                elif subj not in sub_ids:
                    # 形似素材 ID（CHAR-/SCENE-/PROP-/GRP- 前缀）但不在 subjects：
                    # 不是画外音（画外音是中文名如周叔/江野），是拼错/指向不存在素材的 ID，
                    # 锁脸关联断裂，无论 voice 是否非空都报错。
                    if re.match(r'^(?:CHAR|SCENE|PROP|GRP)-', subj):
                        errors.append(
                            f"{label}[{i}].api.shots[{j}].speakers[{k}] subject '{subj}' "
                            f"形似素材 ID 但不在 subjects——疑似 ID 拼错或指向不存在素材（锁脸断裂）")
                    # 画外音角色（无参考图，中文名）允许非 ID；voice 仍须非空
                    elif not sp.get("voice"):
                        errors.append(
                            f"{label}[{i}].api.shots[{j}].speakers[{k}] subject '{subj}' "
                            f"不在 subjects 且 voice 为空——疑似角色名/ID 不匹配或画外音缺声音描述")
                if not str(sp.get("voice") or "").strip():
                    errors.append(
                        f"{label}[{i}].api.shots[{j}].speakers[{k}] voice 为空——"
                        f"必须全文复制声音卡片 P0 voice_prompt")
                if not str(sp.get("dialogue") or "").strip():
                    errors.append(
                        f"{label}[{i}].api.shots[{j}].speakers[{k}] dialogue 为空")
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
            ("⚠️注释检测", lambda: check_warning_comments(fpath)),
            ("顶层字段", lambda: check_top_fields(data, top_fields, label)),
            ("defaults", lambda: check_defaults(data, label)),
            ("子项字段", lambda: item_check(data)),
            ("content_roles", lambda: check_content_roles(data, label)),
            ("URL格式", lambda: check_urls(data, label)),
            ("图N引用", lambda: check_tu_refs(data, label)),
            ("结构化api块", lambda: check_structured_api(data, label)),
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
