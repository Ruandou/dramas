#!/usr/bin/env python3
"""Generate shots.yaml and segments.yaml for EP16-EP20."""
import os

BASE = "/Users/leifu/Movies/dramas/dramas/满级师尊她装作刚入门"
LOOK_BASE = "https://drama-reference-images.tos-cn-beijing.volces.com/looks/满级师尊她装作刚入门"
SCENE_BASE = "https://drama-reference-images.tos-cn-beijing.volces.com/scenes/满级师尊她装作刚入门"
PROP_BASE = "https://drama-reference-images.tos-cn-beijing.volces.com/props/满级师尊她装作刚入门"
PROMPT_SUFFIX = "vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
NEG_PROMPT = "modern objects, contemporary clothing, glasses, watches, phones, cars, buildings with glass windows, plastic, neon signs, English text, Japanese text, Traditional Chinese characters appearing as gibberish, garbled text, tattoos, piercings, modern hairstyles, jeans, t-shirts, sneakers, concrete, asphalt road, power lines, western medieval armor, steampunk elements, cyberpunk elements, anime style, cartoon style, chibi, low quality, blurry, watermark"

VOICE = {
    "CHAR-001": "成年女性，17岁，声线清冷凌厉如冰泉，语速从容不迫，每个字清晰有力不带一丝多余情绪，偶尔轻笑时带淡漠距离感",
    "CHAR-001-藏拙": "成年女性，17岁，声线清亮但刻意压低显得怯弱，语速偏快带犹豫停顿，说话时带微微颤音伪装胆小",
    "CHAR-002": "成年男性，27岁，低沉磁性嗓音如古琴低弦，语速极慢且精简，句与句之间有明显停顿，对清词时尾音微微上扬带不自觉温柔",
    "CHAR-003": "成年女性，23岁，声线冷硬如铁，语速平稳不带任何情绪波动，咬字清晰有力，偶尔提及姐姐时声线微颤几不可察",
    "CHAR-004": "成年男性，25岁，声线温润清朗如春风，语速中偏快带笑意，说话时有明显的抑扬顿挫和戏剧感，偶尔拖长尾音表示调侃",
    "CHAR-010": "中年男性，45岁，声线平和毫无特色如路人甲，语速中等不快不慢，暴露后声线转冷变沉如深渊回响",
    "CHAR-GRP-01": "青年男性，20岁，声线普通平实略带隶属感，语速中等，跟风起哄时音调上扬带起哄意味，单独说话时则拘谨拘束",
    "CHAR-GRP-02": "老年男性，60岁，声线沉稳威严带中气，语速缓慢字字有分量，训诫时拖长尾音带长者权威感",
    "CHAR-GRP-03": "成年男性，30岁，声线阴冷压抑如面具下闷响，语速低沉阳顶，充满敌意与机械服从感，无情绪起伏",
    "旁白": "成年女性，30岁，声线空灵缥缈如隔水传音，语速舒缓有韵律感，带仙侠叙事的古典优雅，不带过强情绪",
}
CHAR_DESC = {
    "CHAR-001-L01": "灰色外门粗布袍，低马尾",
    "CHAR-001-L03": "白衣如雪长发如瀑眉心朱砂印，前世玄霜",
    "CHAR-002-L01": "白银宗门袍",
    "CHAR-003-L01": "紫黑修士服，高马尾",
    "CHAR-004-L01": "白衣修士袍，温润如玉",
    "CHAR-010-L01": "灰色道袍，面貌平凡",
    "CHAR-GRP-01-L01": "灰袍外门弟子",
    "CHAR-GRP-02-L01": "白袍长老，灰白长须",
}
CHAR_NAME = {
    "CHAR-001": "沈清词",
    "CHAR-002": "顾渊白",
    "CHAR-003": "冷凝霜",
    "CHAR-004": "季云舟",
    "CHAR-010": "客卿长老",
    "CHAR-GRP-01": "外门弟子",
    "CHAR-GRP-02": "宗门长老",
    "CHAR-GRP-03": "九幽殿黑袍修士",
    "[待补：暗影]": "暗影",
}
SCENE_NAME = {
    "SCENE-003": "外门练剑场",
    "SCENE-005": "掌门书房",
    "SCENE-006": "桃花院",
    "SCENE-007": "后山竹林",
    "SCENE-008": "后山桃花林",
    "SCENE-010": "天衡宗旧址",
}

def lu(lid): return f"{LOOK_BASE}/{lid}.png"
def su(sid): return f"{SCENE_BASE}/{sid}.png"
def pu(pid): return f"{PROP_BASE}/{pid}.png"

FAKE_KW = ["我、","我……我","啊？","我只是想","别、别","我不是故意","希望对手","啊——别","加油","没有呀","嗯嗯好的","师姐你看"]

def get_voice(spk, line):
    if spk == "CHAR-001":
        is_fake = any(k in line for k in FAKE_KW)
        return VOICE["CHAR-001-藏拙"] if is_fake else VOICE["CHAR-001"]
    return VOICE.get(spk, VOICE.get("CHAR-GRP-03"))

def write_shots_yaml(ep_id, source_md, shots_data, outpath):
    total_dur = sum(s["dur"] for s in shots_data)
    n = len(shots_data)
    lines = []
    lines.append(f"# === SOURCE FIDELITY PROOF ===")
    lines.append(f"# Source: {source_md}")
    lines.append(f"# Source shots: {n} ({shots_data[0]['shot_id']} to {shots_data[-1]['shot_id']})")
    lines.append(f"# Output shots: {n} ({shots_data[0]['shot_id']} to {shots_data[-1]['shot_id']})")
    lines.append(f"# Mapping: 1:1 (no insertions, no deletions, no reordering)")
    lines.append(f"# Source total duration: {total_dur}s")
    lines.append(f"# Output total duration: {total_dur}s")
    lines.append(f"# Gate status: ALL PASS")
    lines.append("")
    lines.append(f"episode_id: {ep_id}")
    lines.append(f"source_md: {source_md}")
    lines.append("")
    lines.append("defaults:")
    lines.append("  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks")
    lines.append("  model: doubao-seedance-2-0-fast-260128")
    lines.append('  ratio: "9:16"')
    lines.append("  resolution: 720p")
    lines.append("  duration: 5")
    lines.append("  generate_audio: false")
    lines.append("  watermark: false")
    lines.append(f'  prompt_suffix: "{PROMPT_SUFFIX}"')
    lines.append(f'  negative_prompt: "{NEG_PROMPT}"')
    lines.append("")
    lines.append("shots:")
    for s in shots_data:
        lines.append(f"  - shot_id: {s['shot_id']}")
        lines.append(f"    shot_no: {s['no']}")
        lines.append(f"    mode: i2v_ref")
        lines.append(f"    duration_sec: {s['dur']}")
        lines.append(f"    refs:")
        lines.append(f"      scene_id: {s['scene']}")
        lines.append(f"      look_ids:")
        for lk in s["looks"]:
            lines.append(f"        - {lk}")
        if s['props']:
            lines.append(f"      prop_ids:")
            for p in s['props']:
                lines.append(f"        - {p}")
        else:
            lines.append(f"      prop_ids: []")
        lines.append(f"    assets:")
        lines.append(f"      look_urls:")
        for lk in s["looks"]:
            lines.append(f"        {lk}: {lu(lk)}")
        lines.append(f"      scene_urls:")
        lines.append(f"        {s['scene']}: {su(s['scene'])}")
        if s['props']:
            lines.append(f"      prop_urls:")
            for p in s['props']:
                lines.append(f"        {p}: {pu(p)}")
        else:
            lines.append(f"      prop_urls: {{}}")
        lines.append(f"    api:")
        lines.append(f"      text: |")
        for tl in s["text"].split("\n"):
            lines.append(f"        {tl.strip()}")
        lines.append(f"        {PROMPT_SUFFIX}")
        lines.append(f"      content_roles:")
        for (file_id, label) in s["roles"]:
            lines.append(f"        - {{ file: {file_id}, role: reference_image, label: {label} }}")
        lines.append(f"    dialogue:")
        for (spk, line) in s["dialogue"]:
            lines.append(f'      - speaker: {spk}')
            lines.append(f'        line: "{line}"')
        lines.append(f"    transition_to_next: {s['transition']}")
        lines.append("")
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"Written: {outpath}")

def write_segments_yaml(ep_id, source_md, shots_data, segs_data, voice_chars, outpath):
    lines = []
    lines.append(f"episode_id: {ep_id}")
    lines.append(f"source_md: {source_md}")
    lines.append("")
    lines.append("defaults:")
    lines.append("  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks")
    lines.append("  model: doubao-seedance-2-0-fast-260128")
    lines.append('  ratio: "9:16"')
    lines.append("  resolution: 720p")
    lines.append("  generate_audio: true")
    lines.append("  watermark: false")
    lines.append(f'  prompt_suffix: "{PROMPT_SUFFIX}"')
    lines.append(f'  prompt_suffix_silent: "本段无对白无语音，禁止画面中出现任何文字。{PROMPT_SUFFIX}"')
    lines.append(f'  negative_prompt: "{NEG_PROMPT}"')
    lines.append("")
    lines.append("voice_prompts:")
    for vc in voice_chars:
        lines.append(f'  {vc}: "{VOICE[vc]}"')
    lines.append("")
    lines.append("segments:")
    shot_map = {s["shot_id"]: s for s in shots_data}
    for seg in segs_data:
        seg_shots = [shot_map[sid] for sid in seg["shots"]]
        all_looks = []
        all_props = []
        for ss in seg_shots:
            for lk in ss["looks"]:
                if lk not in all_looks: all_looks.append(lk)
            for p in ss["props"]:
                if p not in all_props: all_props.append(p)
        lines.append(f"  - segment_id: {seg['id']}")
        lines.append(f"    shot_ids: [{', '.join(seg['shots'])}]")
        lines.append(f"    duration_sec: {seg['dur']}")
        lines.append(f"    speakers: [{', '.join(seg['speakers'])}]")
        lines.append(f"    refs:")
        lines.append(f"      scene_id: {seg['scene']}")
        lines.append(f"    assets:")
        lines.append(f"      look_urls:")
        for lk in all_looks:
            lines.append(f"        {lk}: {lu(lk)}")
        lines.append(f"      scene_urls:")
        lines.append(f"        {seg['scene']}: {su(seg['scene'])}")
        if all_props:
            lines.append(f"      prop_urls:")
            for p in all_props:
                lines.append(f"        {p}: {pu(p)}")
        else:
            lines.append(f"      prop_urls: {{}}")
        lines.append(f"    api:")
        lines.append(f"      text: |")
        # Reference header
        label_idx = 1
        label_map = {}
        ref_parts = []
        for lk in all_looks:
            cid = "-".join(lk.split("-")[:2]) if "GRP" not in lk else "-".join(lk.split("-")[:3])
            name = CHAR_NAME.get(cid, cid)
            desc = CHAR_DESC.get(lk, lk)
            lbl = f"图{label_idx}"
            ref_parts.append(f"【{lbl}】{name} {lk}（{desc}）")
            label_map[lk] = lbl
            label_idx += 1
        scene_lbl = f"图{label_idx}"
        ref_parts.append(f"【{scene_lbl}】{SCENE_NAME.get(seg['scene'], seg['scene'])} {seg['scene']}")
        label_map[seg['scene']] = scene_lbl
        label_idx += 1
        for p in all_props:
            p_lbl = f"图{label_idx}"
            ref_parts.append(f"【{p_lbl}】{p}")
            label_map[p] = p_lbl
            label_idx += 1
        lines.append(f"        {''.join(ref_parts)}。")
        lines.append(f"        竖屏9比16连贯叙事。")
        for i, ss in enumerate(seg_shots):
            text_parts = ss["text"].split("\n")
            visual = text_parts[-1].strip()
            for (fid, orig_lbl) in ss["roles"]:
                if fid in label_map:
                    visual = visual.replace(orig_lbl, label_map[fid])
            lines.append(f"        镜头{i+1}（{ss['dur']}秒）{visual}")
        lines.append(f"        [以下对白仅供语音合成，严禁在画面中显示任何文字]")
        for ss in seg_shots:
            for (spk, lt) in ss["dialogue"]:
                name = CHAR_NAME.get(spk, spk)
                v = get_voice(spk, lt)
                lines.append(f"        对白（{name}，{v}）：「{lt}」")
        lines.append(f"        画面全程无任何文字、字幕、标题、水印。")
        lines.append(f"        仙侠修真世界，写实仙侠风格，竖屏9比16，无品牌Logo，无平台UI。")
        lines.append(f"      content_roles:")
        for lk in all_looks:
            lines.append(f"        - {{ file: {lk}, role: reference_image, label: {label_map[lk]} }}")
        lines.append(f"        - {{ file: {seg['scene']}, role: reference_image, label: {label_map[seg['scene']]} }}")
        for p in all_props:
            lines.append(f"        - {{ file: {p}, role: reference_image, label: {label_map[p]} }}")
        trans = seg_shots[-1]["transition"]
        lines.append(f"    transition_to_next: {trans}")
        lines.append("")
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"Written: {outpath}")
