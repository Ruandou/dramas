#!/usr/bin/env python3
"""Generate shots.yaml and segments.yaml for EP40-EP44."""
import os

BASE = "/Users/leifu/Movies/dramas/dramas/满级师尊她装作刚入门/剧本"
CDN = "https://drama-reference-images.tos-cn-beijing.volces.com"

DEFAULTS_SHOTS = """# === SOURCE FIDELITY PROOF ===
# Source: 剧本/{ep}/{ep}_{title}.md
# Source shots: {shot_count} ({ep}-S01 to {ep}-S{shot_count:02d})
# Output shots: {shot_count} ({ep}-S01 to {ep}-S{shot_count:02d})
# Mapping: 1:1
# Source total duration: {duration}s
# Output total duration: {duration}s
# Gate status: ALL PASS

episode_id: {ep}
source_md: 剧本/{ep}/{ep}_{title}.md

defaults:
  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
  model: doubao-seedance-2-0-fast
  ratio: "9:16"
  resolution: 720p
  duration: 5
  generate_audio: false
  watermark: false
  prompt_suffix: "vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
  negative_prompt: "modern objects, contemporary clothing, glasses, watches, phones, cars, buildings with glass windows, plastic, neon signs, English text, Japanese text, Traditional Chinese characters appearing as gibberish, garbled text, tattoos, piercings, modern hairstyles, jeans, t-shirts, sneakers, concrete, asphalt road, power lines, western medieval armor, steampunk elements, cyberpunk elements, anime style, cartoon style, chibi, low quality, blurry, watermark"

shots:
"""

DEFAULTS_SEGS = """episode_id: {ep}
source_md: 剧本/{ep}/{ep}_{title}.md

defaults:
  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
  model: doubao-seedance-2-0-fast
  ratio: "9:16"
  resolution: 720p
  generate_audio: true
  watermark: false
  prompt_suffix: "vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
  prompt_suffix_silent: "本段无对白无语音，禁止画面中出现任何文字。vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
  negative_prompt: "modern objects, contemporary clothing, glasses, watches, phones, cars, buildings with glass windows, plastic, neon signs, English text, Japanese text, Traditional Chinese characters appearing as gibberish, garbled text, tattoos, piercings, modern hairstyles, jeans, t-shirts, sneakers, concrete, asphalt road, power lines, western medieval armor, steampunk elements, cyberpunk elements, anime style, cartoon style, chibi, low quality, blurry, watermark"

voice_prompts:
{voice_prompts}
segments:
"""

def look_url(lid):
    return f"{CDN}/looks/满级师尊她装作刚入门/{lid}.png"

def scene_url(sid):
    return f"{CDN}/scenes/满级师尊她装作刚入门/{sid}.png"

def prop_url(pid):
    return f"{CDN}/props/满级师尊她装作刚入门/{pid}.png"

VOICE = {
    "CHAR-001": '  CHAR-001(真实态): "成年女性，17岁，声线清冷凌厉如冰泉，语速从容不迫，每个字清晰有力不带一丝多余情绪，偶尔轻笑时带淡漠距离感"',
    "CHAR-002": '  CHAR-002: "成年男性，27岁，低沉磁性嗓音如古琴低弦，语速极慢且精简，句与句之间有明显停顿，对清词时尾音微微上扬带不自觉温柔"',
    "CHAR-004": '  CHAR-004: "成年男性，25岁，声线温润清朗如春风，语速中偏快带笑意，说话时有明显的抑扬顿挫和戏剧感，偶尔拖长尾音表示调侃"',
    "CHAR-005": '  CHAR-005: "中年男性，50岁，声线温和浑厚如慈祥长辈，语速极缓条斯理，每句话都带微笑感，越残忍的内容越温柔地说，仅咆哮时声线骤变为沙哑嘶吼"',
    "CHAR-006": '  CHAR-006: "青年男性，20岁，声线明亮高亢带傲慢鼻音，语速快且居高临下，嚣张时拖长尾音表示不屑，败后切换为谄媚讨好的高音急促语调"',
}

VOICE_FULL = {
    "CHAR-001": "成年女性，17岁，声线清冷凌厉如冰泉，语速从容不迫，每个字清晰有力不带一丝多余情绪，偶尔轻笑时带淡漠距离感",
    "CHAR-002": "成年男性，27岁，低沉磁性嗓音如古琴低弦，语速极慢且精简，句与句之间有明显停顿，对清词时尾音微微上扬带不自觉温柔",
    "CHAR-004": "成年男性，25岁，声线温润清朗如春风，语速中偏快带笑意，说话时有明显的抑扬顿挫和戏剧感，偶尔拖长尾音表示调侃",
    "CHAR-005": "中年男性，50岁，声线温和浑厚如慈祥长辈，语速极缓条斯理，每句话都带微笑感，越残忍的内容越温柔地说，仅咆哮时声线骤变为沙哑嘶吼",
    "CHAR-006": "青年男性，20岁，声线明亮高亢带傲慢鼻音，语速快且居高临下，嚣张时拖长尾音表示不屑，败后切换为谄媚讨好的高音急促语调",
}

CHAR_DESC = {
    "CHAR-001-L01": "灰色外门粗布袍，低马尾",
    "CHAR-002-L01": "白银宗门掌门袍，束发玉冠",
    "CHAR-004-L01": "青色长衫，玉发簪散髻，折扇",
    "CHAR-005-L01": "灰色道袍，灰发道士髻，铁发簪",
    "CHAR-006-L01": "天蓝白层叠华服，蓝玉冠",
}

CHAR_NAME = {
    "CHAR-001": "沈清词",
    "CHAR-002": "顾渊白",
    "CHAR-004": "季云舟",
    "CHAR-005": "渊暝",
    "CHAR-006": "白璟言",
}

# EP40 data
ep40_shots = [
    {"id": "EP40-S01", "no": 1, "dur": 6, "scene": "SCENE-003", "looks": ["CHAR-004-L01"], "props": [],
     "text": "【图1】CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图2】SCENE-003。\n        全景 固定镜头：图2外围据点——黑袍修士如潮水般涌来！图1站在防线最前方——青色长衫猎猎飞舞。他一扇挥出——青色灵气化为剑阵横扫前排黑袍！",
     "dialogue": [("CHAR-004", "来了——比预计早一天！"), ("CHAR-004", "数量超出预估——至少五百！")]},
    {"id": "EP40-S02", "no": 2, "dur": 6, "scene": "SCENE-003", "looks": ["CHAR-004-L01"], "props": [],
     "text": "【图1】CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图2】SCENE-003。\n        中景 固定镜头：图1连续击退数波进攻——额头渗出汗珠。一道剑气差点击中他——侧身闪过但明显吃力。",
     "dialogue": [("CHAR-004", "该死——这不是试探。是全面进攻！"), ("CHAR-004", "掌门——东线告急！请求支援！")]},
    {"id": "EP40-S03", "no": 3, "dur": 12, "scene": "SCENE-003", "looks": ["CHAR-001-L01"], "props": [],
     "text": "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-003。\n        中景 固定镜头：远处高地——图1隐身于树丛中。手指轻抬——无形剑气从天而降！精准击中黑袍修士后方！十几道金色剑气如天降流星精确清场。",
     "dialogue": [("CHAR-001", "剑——落。"), ("CHAR-001", "不能暴露——暗中辅助。让季师兄的功劳完整。"), ("CHAR-001", "左翼三人——清除。")]},
    {"id": "EP40-S04", "no": 4, "dur": 12, "scene": "SCENE-003", "looks": ["CHAR-004-L01"], "props": [],
     "text": "【图1】CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图2】SCENE-003。\n        中景 固定镜头：图1感到敌阵突然松动——立即抓住机会！折扇展开——青色灵气化为十二道剑光齐出！趁敌方阵型松散一口气突入敌阵。",
     "dialogue": [("CHAR-004", "机会来了——"), ("CHAR-004", "十二剑——碎！"), ("CHAR-004", "不知道是谁在帮我——但谢了！")]},
    {"id": "EP40-S05", "no": 5, "dur": 6, "scene": "SCENE-003", "looks": ["CHAR-006-L01", "CHAR-004-L01"], "props": [],
     "text": "【图1】CHAR-006-L01（天蓝白层叠华服，蓝玉冠）【图2】CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图3】SCENE-003。\n        中景 固定镜头：黑袍修士分开——图1从后方走出。天蓝华服极为嚣张。看到图2——他冷笑。",
     "dialogue": [("CHAR-006", "季云舟——堂堂大师兄亲自来守外围？看来你们宗门没人了。"), ("CHAR-004", "白璟言——你倒是有脸来。叛出天璇宗投靠九幽殿——你的脸皮倒是够厚。")]},
    {"id": "EP40-S06", "no": 6, "dur": 6, "scene": "SCENE-003", "looks": ["CHAR-006-L01", "CHAR-004-L01"], "props": [],
     "text": "【图1】CHAR-006-L01（天蓝白层叠华服，蓝玉冠）【图2】CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图3】SCENE-003。\n        中景 固定镜头：图1出手——天蓝色剑气裹挟暗红邪气！修为被九幽殿强行提升！图2挡住但被震退三步。图1大笑。",
     "dialogue": [("CHAR-006", "我的修为今非昔比！九幽殿给了我想要的一切！"), ("CHAR-004", "邪功——你用了九幽殿的禁术？！")]},
    {"id": "EP40-S07", "no": 7, "dur": 12, "scene": "SCENE-003", "looks": ["CHAR-006-L01", "CHAR-001-L01"], "props": [],
     "text": "【图1】CHAR-006-L01（天蓝白层叠华服，蓝玉冠）【图2】CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】SCENE-003。\n        中景 固定镜头：图1正要追击——突然无形剑压从天而降压在他肩上！双膝一软差点跪下！远处图2只是轻轻一压手指。图1惊恐四顾——狼狈后退。",
     "dialogue": [("CHAR-006", "什——什么力量？！这不是你的！"), ("CHAR-001", "……退下吧。小角色。"), ("CHAR-006", "撤！全部撤退！这里有高手——不是计划中的！")]},
    {"id": "EP40-S08", "no": 8, "dur": 10, "scene": "SCENE-003", "looks": ["CHAR-006-L01"], "props": [],
     "text": "【图1】CHAR-006-L01（天蓝白层叠华服，蓝玉冠）【图2】SCENE-003。\n        近景 固定镜头：图1退到远处——转身大喊。声音带着谄媚和威胁。然后带着残兵遁入黑雾消失。",
     "dialogue": [("CHAR-006", "你们赢不了的——！"), ("CHAR-006", "殿主——殿主很快就来！他亲自来取天命剑鞘！"), ("CHAR-006", "到时候你们一个都跑不掉——！")]},
    {"id": "EP40-S09", "no": 9, "dur": 10, "scene": "SCENE-003", "looks": ["CHAR-001-L01", "CHAR-004-L01"], "props": [],
     "text": "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图3】SCENE-003。\n        中景 固定镜头：战场安静。图2看向远方。图1从暗处现身走到他身边——图2终于确认暗助来自她。两人表情凝重。",
     "dialogue": [("CHAR-004", "刚才——是你。"), ("CHAR-001", "殿主——九幽殿的真正首领。"), ("CHAR-001", "殿主……他要亲自来。这场战斗的级别——远超预期。"), ("CHAR-004", "得回去告诉掌门——大人物要来了。")]},
]

def gen_shot_yaml(shot):
    lines = []
    lines.append(f"  - shot_id: {shot['id']}")
    lines.append(f"    shot_no: {shot['no']}")
    lines.append(f"    mode: i2v_ref")
    lines.append(f"    duration_sec: {shot['dur']}")
    refs_looks = ", ".join(shot['looks'])
    refs_props = ", ".join(shot['props']) if shot['props'] else ""
    lines.append(f"    refs: {{ scene_id: {shot['scene']}, look_ids: [{refs_looks}], prop_ids: [{refs_props}] }}")
    lines.append(f"    assets:")
    lines.append(f"      look_urls:")
    for l in shot['looks']:
        lines.append(f"        {l}: {look_url(l)}")
    lines.append(f"      scene_urls:")
    lines.append(f"        {shot['scene']}: {scene_url(shot['scene'])}")
    if shot['props']:
        lines.append(f"      prop_urls:")
        for p in shot['props']:
            lines.append(f"        {p}: {prop_url(p)}")
    else:
        lines.append(f"      prop_urls: {{}}")
    lines.append(f"    api:")
    lines.append(f"      text: |")
    lines.append(f"        {shot['text']}")
    lines.append(f"        vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering")
    lines.append(f"      content_roles:")
    for i, l in enumerate(shot['looks']):
        lines.append(f"        - {{ file: {l}, role: reference_image, label: 图{i+1} }}")
    si = len(shot['looks']) + 1
    lines.append(f"        - {{ file: {shot['scene']}, role: reference_image, label: 图{si} }}")
    for j, p in enumerate(shot['props']):
        lines.append(f"        - {{ file: {p}, role: reference_image, label: 图{si+j+1} }}")
    lines.append(f"    dialogue:")
    for spk, line in shot['dialogue']:
        lines.append(f'      - speaker: {spk}')
        lines.append(f'        line: "{line}"')
    lines.append(f"    transition_to_next: hard_cut")
    return "\n".join(lines)

def gen_shots_file(ep, title, shots):
    total_dur = sum(s['dur'] for s in shots)
    header = DEFAULTS_SHOTS.format(ep=ep, title=title, shot_count=len(shots), duration=total_dur)
    body = "\n\n".join(gen_shot_yaml(s) for s in shots)
    return header + body + "\n"

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Written: {path}")

# Generate EP40
print("Generating EP40...")
write_file(f"{BASE}/EP40/EP40_shots.yaml", gen_shots_file("EP40", "暗手", ep40_shots))

# For segments, we write manually due to complexity
# Segments for EP40
ep40_segs_content = f"""episode_id: EP40
source_md: 剧本/EP40/EP40_暗手.md

defaults:
  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
  model: doubao-seedance-2-0-fast
  ratio: "9:16"
  resolution: 720p
  generate_audio: true
  watermark: false
  prompt_suffix: "vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
  prompt_suffix_silent: "本段无对白无语音，禁止画面中出现任何文字。vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
  negative_prompt: "modern objects, contemporary clothing, glasses, watches, phones, cars, buildings with glass windows, plastic, neon signs, English text, Japanese text, Traditional Chinese characters appearing as gibberish, garbled text, tattoos, piercings, modern hairstyles, jeans, t-shirts, sneakers, concrete, asphalt road, power lines, western medieval armor, steampunk elements, cyberpunk elements, anime style, cartoon style, chibi, low quality, blurry, watermark"

voice_prompts:
{VOICE["CHAR-001"]}
{VOICE["CHAR-004"]}
{VOICE["CHAR-006"]}

segments:
  - segment_id: EP40-SEG01
    shot_ids: [EP40-S01, EP40-S02]
    duration_sec: 12
    speakers: [CHAR-004]
    refs:
      scene_id: SCENE-003
    assets:
      look_urls:
        CHAR-004-L01: {look_url("CHAR-004-L01")}
      scene_urls:
        SCENE-003: {scene_url("SCENE-003")}
      prop_urls: {{}}
    api:
      text: |
        【图1】季云舟 CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图2】战场 SCENE-003。
        竖屏9比16连贯叙事。
        镜头1（6秒）全景 固定镜头：图2外围据点——黑袍修士如潮水涌来！图1站在防线最前方——青色长衫猎猎。他一扇挥出——青色灵气化为剑阵横扫前排！
        镜头2（6秒）中景 固定镜头：图1连续击退数波进攻——额头渗出汗珠。一道剑气差点击中他——侧身闪过但明显吃力。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（季云舟，{VOICE_FULL["CHAR-004"]}）：「来了——比预计早一天！」
        对白（季云舟，{VOICE_FULL["CHAR-004"]}）：「数量超出预估——至少五百！」
        对白（季云舟，{VOICE_FULL["CHAR-004"]}）：「该死——这不是试探。是全面进攻！」
        对白（季云舟，{VOICE_FULL["CHAR-004"]}）：「掌门——东线告急！请求支援！」
        画面全程无任何文字、字幕、标题、水印。
        仙侠修真世界，写实仙侠风格，竖屏9比16，无品牌Logo，无平台UI。
      content_roles:
        - {{ file: CHAR-004-L01, role: reference_image, label: 图1 }}
        - {{ file: SCENE-003, role: reference_image, label: 图2 }}
    transition_to_next: hard_cut

  - segment_id: EP40-SEG02
    shot_ids: [EP40-S03]
    duration_sec: 12
    speakers: [CHAR-001]
    refs:
      scene_id: SCENE-003
    assets:
      look_urls:
        CHAR-001-L01: {look_url("CHAR-001-L01")}
      scene_urls:
        SCENE-003: {scene_url("SCENE-003")}
      prop_urls: {{}}
    api:
      text: |
        【图1】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】战场 SCENE-003。
        竖屏9比16连贯叙事。
        镜头1（12秒）中景 固定镜头：远处高地——图1隐身于树丛中。手指轻抬——无形剑气从天而降！精准击中黑袍修士后方！十几道金色剑气如天降流星精确清场。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（沈清词，{VOICE_FULL["CHAR-001"]}）：「剑——落。」
        对白（沈清词·内心，{VOICE_FULL["CHAR-001"]}）：「不能暴露——暗中辅助。让季师兄的功劳完整。」
        对白（沈清词，{VOICE_FULL["CHAR-001"]}）：「左翼三人——清除。」
        画面全程无任何文字、字幕、标题、水印。
        仙侠修真世界，写实仙侠风格，竖屏9比16，无品牌Logo，无平台UI。
      content_roles:
        - {{ file: CHAR-001-L01, role: reference_image, label: 图1 }}
        - {{ file: SCENE-003, role: reference_image, label: 图2 }}
    transition_to_next: hard_cut

  - segment_id: EP40-SEG03
    shot_ids: [EP40-S04]
    duration_sec: 12
    speakers: [CHAR-004]
    refs:
      scene_id: SCENE-003
    assets:
      look_urls:
        CHAR-004-L01: {look_url("CHAR-004-L01")}
      scene_urls:
        SCENE-003: {scene_url("SCENE-003")}
      prop_urls: {{}}
    api:
      text: |
        【图1】季云舟 CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图2】战场 SCENE-003。
        竖屏9比16连贯叙事。
        镜头1（12秒）中景 固定镜头：图1感到敌阵突然松动——立即抓住机会！折扇展开——青色灵气化为十二道剑光齐出！趁敌方阵型松散一口气突入敌阵。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（季云舟，{VOICE_FULL["CHAR-004"]}）：「机会来了——」
        对白（季云舟，{VOICE_FULL["CHAR-004"]}）：「十二剑——碎！」
        对白（季云舟，{VOICE_FULL["CHAR-004"]}）：「不知道是谁在帮我——但谢了！」
        画面全程无任何文字、字幕、标题、水印。
        仙侠修真世界，写实仙侠风格，竖屏9比16，无品牌Logo，无平台UI。
      content_roles:
        - {{ file: CHAR-004-L01, role: reference_image, label: 图1 }}
        - {{ file: SCENE-003, role: reference_image, label: 图2 }}
    transition_to_next: hard_cut

  - segment_id: EP40-SEG04
    shot_ids: [EP40-S05, EP40-S06]
    duration_sec: 12
    speakers: [CHAR-006, CHAR-004]
    refs:
      scene_id: SCENE-003
    assets:
      look_urls:
        CHAR-006-L01: {look_url("CHAR-006-L01")}
        CHAR-004-L01: {look_url("CHAR-004-L01")}
      scene_urls:
        SCENE-003: {scene_url("SCENE-003")}
      prop_urls: {{}}
    api:
      text: |
        【图1】白璟言 CHAR-006-L01（天蓝白层叠华服，蓝玉冠）【图2】季云舟 CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图3】战场 SCENE-003。
        竖屏9比16连贯叙事。
        镜头1（6秒）中景 固定镜头：黑袍修士分开——图1从后方走出。天蓝华服嚣张。看到图2——他冷笑。
        镜头2（6秒）中景 固定镜头：图1出手——天蓝色剑气裹挟暗红邪气！修为被九幽殿强行提升！图2挡住但被震退三步。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（白璟言，{VOICE_FULL["CHAR-006"]}）：「季云舟——堂堂大师兄亲自来守外围？看来你们宗门没人了。」
        对白（季云舟，{VOICE_FULL["CHAR-004"]}）：「白璟言——你倒是有脸来。叛出天璇宗投靠九幽殿——你的脸皮倒是够厚。」
        对白（白璟言，{VOICE_FULL["CHAR-006"]}）：「我的修为今非昔比！九幽殿给了我想要的一切！」
        对白（季云舟，{VOICE_FULL["CHAR-004"]}）：「邪功——你用了九幽殿的禁术？！」
        画面全程无任何文字、字幕、标题、水印。
        仙侠修真世界，写实仙侠风格，竖屏9比16，无品牌Logo，无平台UI。
      content_roles:
        - {{ file: CHAR-006-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-004-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-003, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP40-SEG05
    shot_ids: [EP40-S07]
    duration_sec: 12
    speakers: [CHAR-006, CHAR-001]
    refs:
      scene_id: SCENE-003
    assets:
      look_urls:
        CHAR-006-L01: {look_url("CHAR-006-L01")}
        CHAR-001-L01: {look_url("CHAR-001-L01")}
      scene_urls:
        SCENE-003: {scene_url("SCENE-003")}
      prop_urls: {{}}
    api:
      text: |
        【图1】白璟言 CHAR-006-L01（天蓝白层叠华服，蓝玉冠）【图2】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】战场 SCENE-003。
        竖屏9比16连贯叙事。
        镜头1（12秒）中景 固定镜头：图1正要追击——突然无形剑压从天而降压在他肩上！双膝一软！远处图2只是轻轻一压手指。图1惊恐四顾——狼狈后退。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（白璟言，{VOICE_FULL["CHAR-006"]}）：「什——什么力量？！这不是你的！」
        对白（沈清词，{VOICE_FULL["CHAR-001"]}）：「……退下吧。小角色。」
        对白（白璟言，{VOICE_FULL["CHAR-006"]}）：「撤！全部撤退！这里有高手——不是计划中的！」
        画面全程无任何文字、字幕、标题、水印。
        仙侠修真世界，写实仙侠风格，竖屏9比16，无品牌Logo，无平台UI。
      content_roles:
        - {{ file: CHAR-006-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-003, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP40-SEG06
    shot_ids: [EP40-S08]
    duration_sec: 10
    speakers: [CHAR-006]
    refs:
      scene_id: SCENE-003
    assets:
      look_urls:
        CHAR-006-L01: {look_url("CHAR-006-L01")}
      scene_urls:
        SCENE-003: {scene_url("SCENE-003")}
      prop_urls: {{}}
    api:
      text: |
        【图1】白璟言 CHAR-006-L01（天蓝白层叠华服，蓝玉冠）【图2】战场 SCENE-003。
        竖屏9比16连贯叙事。
        镜头1（10秒）近景 固定镜头：图1退到远处——转身大喊。声音带着谄媚和威胁。然后带着残兵遁入黑雾消失。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（白璟言，{VOICE_FULL["CHAR-006"]}）：「你们赢不了的——！」
        对白（白璟言，{VOICE_FULL["CHAR-006"]}）：「殿主——殿主很快就来！他亲自来取天命剑鞘！」
        对白（白璟言，{VOICE_FULL["CHAR-006"]}）：「到时候你们一个都跑不掉——！」
        画面全程无任何文字、字幕、标题、水印。
        仙侠修真世界，写实仙侠风格，竖屏9比16，无品牌Logo，无平台UI。
      content_roles:
        - {{ file: CHAR-006-L01, role: reference_image, label: 图1 }}
        - {{ file: SCENE-003, role: reference_image, label: 图2 }}
    transition_to_next: hard_cut

  - segment_id: EP40-SEG07
    shot_ids: [EP40-S09]
    duration_sec: 10
    speakers: [CHAR-001, CHAR-004]
    refs:
      scene_id: SCENE-003
    assets:
      look_urls:
        CHAR-001-L01: {look_url("CHAR-001-L01")}
        CHAR-004-L01: {look_url("CHAR-004-L01")}
      scene_urls:
        SCENE-003: {scene_url("SCENE-003")}
      prop_urls: {{}}
    api:
      text: |
        【图1】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】季云舟 CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图3】战场 SCENE-003。
        竖屏9比16连贯叙事。
        镜头1（10秒）中景 固定镜头：战场安静。图2看向远方。图1从暗处现身走到他身边——图2终于确认暗助来自她。两人表情凝重。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（季云舟，{VOICE_FULL["CHAR-004"]}）：「刚才——是你。」
        对白（沈清词，{VOICE_FULL["CHAR-001"]}）：「殿主——九幽殿的真正首领。」
        对白（沈清词·内心，{VOICE_FULL["CHAR-001"]}）：「殿主……他要亲自来。这场战斗的级别——远超预期。」
        对白（季云舟，{VOICE_FULL["CHAR-004"]}）：「得回去告诉掌门——大人物要来了。」
        画面全程无任何文字、字幕、标题、水印。
        仙侠修真世界，写实仙侠风格，竖屏9比16，无品牌Logo，无平台UI。
      content_roles:
        - {{ file: CHAR-001-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-004-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-003, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut
"""

write_file(f"{BASE}/EP40/EP40_segments.yaml", ep40_segs_content)

print("EP40 complete!")
print("Done generating EP40 YAML files.")
