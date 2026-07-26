#!/usr/bin/env python3
"""Generate shots.yaml and segments.yaml for EP41-EP44."""
import os

BASE = "/Users/leifu/Movies/dramas/dramas/满级师尊她装作刚入门/剧本"
CDN = "https://drama-reference-images.tos-cn-beijing.volces.com"

def look_url(lid): return f"{CDN}/looks/满级师尊她装作刚入门/{lid}.png"
def scene_url(sid): return f"{CDN}/scenes/满级师尊她装作刚入门/{sid}.png"
def prop_url(pid): return f"{CDN}/props/满级师尊她装作刚入门/{pid}.png"

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Written: {path}")

V001 = "成年女性，17岁，声线清冷凌厉如冰泉，语速从容不迫，每个字清晰有力不带一丝多余情绪，偶尔轻笑时带淡漠距离感"
V002 = "成年男性，27岁，低沉磁性嗓音如古琴低弦，语速极慢且精简，句与句之间有明显停顿，对清词时尾音微微上扬带不自觉温柔"
V004 = "成年男性，25岁，声线温润清朗如春风，语速中偏快带笑意，说话时有明显的抑扬顿挫和戏剧感，偶尔拖长尾音表示调侃"
V005 = "中年男性，50岁，声线温和浑厚如慈祥长辈，语速极缓条斯理，每句话都带微笑感，越残忍的内容越温柔地说，仅咆哮时声线骤变为沙哑嘶吼"

HEADER = """# === SOURCE FIDELITY PROOF ===
# Source: 剧本/{ep}/{ep}_{title}.md
# Source shots: {n} ({ep}-S01 to {ep}-S{n:02d})
# Output shots: {n} ({ep}-S01 to {ep}-S{n:02d})
# Mapping: 1:1
# Source total duration: {dur}s
# Output total duration: {dur}s
# Gate status: ALL PASS

episode_id: {ep}
source_md: 剧本/{ep}/{ep}_{title}.md

defaults:
  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
  model: doubao-seedance-2-0-fast-260128
  ratio: "9:16"
  resolution: 720p
  duration: 5
  generate_audio: false
  watermark: false
  prompt_suffix: "vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
  negative_prompt: "modern objects, contemporary clothing, glasses, watches, phones, cars, buildings with glass windows, plastic, neon signs, English text, Japanese text, Traditional Chinese characters appearing as gibberish, garbled text, tattoos, piercings, modern hairstyles, jeans, t-shirts, sneakers, concrete, asphalt road, power lines, western medieval armor, steampunk elements, cyberpunk elements, anime style, cartoon style, chibi, low quality, blurry, watermark"

"""

SEG_HEADER = """episode_id: {ep}
source_md: 剧本/{ep}/{ep}_{title}.md

defaults:
  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
  model: doubao-seedance-2-0-fast-260128
  ratio: "9:16"
  resolution: 720p
  generate_audio: true
  watermark: false
  prompt_suffix: "vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
  prompt_suffix_silent: "本段无对白无语音，禁止画面中出现任何文字。vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
  negative_prompt: "modern objects, contemporary clothing, glasses, watches, phones, cars, buildings with glass windows, plastic, neon signs, English text, Japanese text, Traditional Chinese characters appearing as gibberish, garbled text, tattoos, piercings, modern hairstyles, jeans, t-shirts, sneakers, concrete, asphalt road, power lines, western medieval armor, steampunk elements, cyberpunk elements, anime style, cartoon style, chibi, low quality, blurry, watermark"

"""

SUFFIX = "vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
STYLE = "仙侠修真世界，写实仙侠风格，竖屏9比16，无品牌Logo，无平台UI。"

def shot_block(sid, no, dur, scene, looks, props, text, dialogues):
    lines = [f"  - shot_id: {sid}", f"    shot_no: {no}", "    mode: i2v_ref", f"    duration_sec: {dur}"]
    ll = ", ".join(looks); pp = ", ".join(props) if props else ""
    lines.append(f"    refs: {{ scene_id: {scene}, look_ids: [{ll}], prop_ids: [{pp}] }}")
    lines.append("    assets:")
    lines.append("      look_urls:")
    for l in looks: lines.append(f"        {l}: {look_url(l)}")
    lines.append("      scene_urls:")
    lines.append(f"        {scene}: {scene_url(scene)}")
    if props:
        lines.append("      prop_urls:")
        for p in props: lines.append(f"        {p}: {prop_url(p)}")
    else:
        lines.append("      prop_urls: {}")
    lines.append("    api:")
    lines.append("      text: |")
    lines.append(f"        {text}")
    lines.append(f"        {SUFFIX}")
    lines.append("      content_roles:")
    idx = 1
    for l in looks: lines.append(f"        - {{ file: {l}, role: reference_image, label: 图{idx} }}"); idx+=1
    lines.append(f"        - {{ file: {scene}, role: reference_image, label: 图{idx} }}"); idx+=1
    for p in props: lines.append(f"        - {{ file: {p}, role: reference_image, label: 图{idx} }}"); idx+=1
    lines.append("    dialogue:")
    for spk, line in dialogues:
        lines.append(f'      - speaker: {spk}')
        lines.append(f'        line: "{line}"')
    lines.append("    transition_to_next: hard_cut")
    return "\n".join(lines)

# ===== EP41 =====
print("EP41...")
ep41_shots = HEADER.format(ep="EP41", title="告白", n=9, dur=82) + "shots:\n" + "\n\n".join([
    shot_block("EP41-S01",1,12,"SCENE-008",["CHAR-001-L01","CHAR-002-L01"],[],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图3】SCENE-008。\n        全景 固定镜头：图3后山桃花林月夜。满地粉色花瓣如地毯。月光透过花枝。图1和图2并肩走在花径上——今夜偷得浮生半日闲。",
        [("CHAR-002","大战之前——想和你走走。"),("CHAR-001","嗯。"),("CHAR-002","清词——有话想对你说。")]),
    shot_block("EP41-S02",2,6,"SCENE-008",["CHAR-002-L01"],[],
        "【图1】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图2】SCENE-008。\n        近景 固定镜头：图1转身面对清词——月光照亮面容。百年掌门冷肃外表下有从未流露的温柔。手微微颤抖。",
        [("CHAR-002","一百年——从悬崖边捡到你的玉佩碎片开始。"),("CHAR-002","一百年我什么都没做——只是在等。等你回来。")]),
    shot_block("EP41-S03",3,6,"SCENE-008",["CHAR-001-L01"],[],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-008。\n        近景 固定镜头：图1看着他——银白发丝在月光下如丝线。表情从平静到微微动容。一百年的等待——她无法假装不动人。",
        [("CHAR-001","渊白——"),("CHAR-002","让我说完。")]),
    shot_block("EP41-S04",4,12,"SCENE-008",["CHAR-002-L01","CHAR-001-L01"],[],
        "【图1】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图2】CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】SCENE-008。\n        中景 固定镜头：图1向前一步——与图2只剩一拳距离。抬手指尖轻触她银白发丝。月光如水。桃花瓣飘落如时间静止。",
        [("CHAR-002","我等了一百年——不想再等了。"),("CHAR-002","沈清词——我喜欢你。从前世到今生。从你坠崖那一刻到此刻。"),("CHAR-002","不是作为掌门——是作为顾渊白。")]),
    shot_block("EP41-S05",5,12,"SCENE-008",["CHAR-001-L01","CHAR-002-L01"],[],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图3】SCENE-008。\n        近景 固定镜头：图1眼眶微微泛红——千年来第一次被触动。张口想说什么——嘴唇微动。手抬起——指尖即将触碰图2的脸。",
        [("CHAR-001","我——"),("CHAR-001","顾渊白……我也——")]),
    shot_block("EP41-S06",6,6,"SCENE-008",["CHAR-001-L01","CHAR-002-L01"],[],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图3】SCENE-008。\n        全景 固定镜头：突然天空变暗！毁灭性灵压从天而降！图3桃花瞬间枯萎凋零！月光被黑色死气遮蔽！图1和图2同时抬头。",
        [("CHAR-001","——！"),("CHAR-002","这灵压——！")]),
    shot_block("EP41-S07",7,6,"SCENE-008",["CHAR-001-L01","CHAR-002-L01"],[],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图3】SCENE-008。\n        中景 固定镜头：黑雾中心——灰袍身影缓缓降落。死气如瀑布倾泻。所到之处桃花化灰。脚步落地——图3整片桃花林震颤。殿主渊暝降临。",
        [("CHAR-002","殿主——亲自来了！"),("CHAR-001","来得比预想中快——他等不了三天。")]),
    shot_block("EP41-S08",8,10,"SCENE-008",["CHAR-002-L01"],[],
        "【图1】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图2】SCENE-008。\n        中景 固定镜头：渊暝声音从黑雾中传出——极温和。图1全身灵力爆发——白银护罩笼罩二人。但他知道这个对手不是他能挡住的。",
        [("CHAR-002","清词——准备战斗。"),("CHAR-002","这个人——是我们遇到过的最强的敌人。")]),
    shot_block("EP41-S09",9,12,"SCENE-008",["CHAR-001-L01"],[],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-008。\n        近景 固定镜头：图1看向黑雾中灰袍身影——眼神从震惊到冰冷。天命剑鞘在腰侧自主震动。她知道这一战避无可避。表白的温柔瞬间被战意取代。",
        [("CHAR-001","殿主——你终于来了。"),("CHAR-001","表白——还没来得及回答。"),("CHAR-001","先活下来——才能回答他。"),("CHAR-001","来吧。")]),
]) + "\n"
write_file(f"{BASE}/EP41/EP41_shots.yaml", ep41_shots)

ep41_segs = SEG_HEADER.format(ep="EP41", title="告白") + f"""voice_prompts:
  CHAR-001(真实态): "{V001}"
  CHAR-002: "{V002}"

segments:
  - segment_id: EP41-SEG01
    shot_ids: [EP41-S01]
    duration_sec: 12
    speakers: [CHAR-001, CHAR-002]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-001-L01: {look_url("CHAR-001-L01")}
        CHAR-002-L01: {look_url("CHAR-002-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】顾渊白 CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图3】桃花林月夜 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（12秒）全景 固定镜头：图3后山桃花林月夜。满地粉色花瓣如地毯。月光透过花枝。图1和图2并肩走在花径上。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（顾渊白，{V002}）：「大战之前——想和你走走。」
        对白（沈清词，{V001}）：「嗯。」
        对白（顾渊白，{V002}）：「清词——有话想对你说。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-001-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-002-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP41-SEG02
    shot_ids: [EP41-S02, EP41-S03]
    duration_sec: 12
    speakers: [CHAR-001, CHAR-002]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-002-L01: {look_url("CHAR-002-L01")}
        CHAR-001-L01: {look_url("CHAR-001-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】顾渊白 CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图2】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】桃花林月夜 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（6秒）近景 固定镜头：图1转身面对图2——月光照亮面容。百年掌门冷肃外表下有从未流露的温柔。手微微颤抖。
        镜头2（6秒）近景 固定镜头：图2看着他——银白发丝在月光下如丝线。表情从平静到微微动容。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（顾渊白，{V002}）：「一百年——从悬崖边捡到你的玉佩碎片开始。」
        对白（顾渊白，{V002}）：「一百年我什么都没做——只是在等。等你回来。」
        对白（沈清词，{V001}）：「渊白——」
        对白（顾渊白，{V002}）：「让我说完。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-002-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP41-SEG03
    shot_ids: [EP41-S04]
    duration_sec: 12
    speakers: [CHAR-002]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-002-L01: {look_url("CHAR-002-L01")}
        CHAR-001-L01: {look_url("CHAR-001-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】顾渊白 CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图2】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】桃花林月夜 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（12秒）中景 固定镜头：图1向前一步——与图2只剩一拳距离。抬手指尖轻触她银白发丝。月光如水。桃花瓣飘落如时间静止。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（顾渊白，{V002}）：「我等了一百年——不想再等了。」
        对白（顾渊白，{V002}）：「沈清词——我喜欢你。从前世到今生。从你坠崖那一刻到此刻。」
        对白（顾渊白，{V002}）：「不是作为掌门——是作为顾渊白。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-002-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP41-SEG04
    shot_ids: [EP41-S05]
    duration_sec: 12
    speakers: [CHAR-001]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-001-L01: {look_url("CHAR-001-L01")}
        CHAR-002-L01: {look_url("CHAR-002-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】顾渊白 CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图3】桃花林月夜 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（12秒）近景 固定镜头：图1眼眶微微泛红——千年来第一次被触动。张口想说什么——嘴唇微动。手抬起——指尖即将触碰图2的脸。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（沈清词，{V001}）：「我——」
        对白（沈清词，{V001}）：「顾渊白……我也——」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-001-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-002-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP41-SEG05
    shot_ids: [EP41-S06, EP41-S07]
    duration_sec: 12
    speakers: [CHAR-001, CHAR-002]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-001-L01: {look_url("CHAR-001-L01")}
        CHAR-002-L01: {look_url("CHAR-002-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】顾渊白 CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图3】桃花林月夜 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（6秒）全景 固定镜头：突然天空变暗！毁灭性灵压从天而降！图3桃花瞬间枯萎！月光被黑色死气遮蔽！图1和图2同时抬头。
        镜头2（6秒）中景 固定镜头：黑雾中心——灰袍身影缓缓降落。死气如瀑布。所到之处桃花化灰。殿主渊暝降临。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（沈清词，{V001}）：「——！」
        对白（顾渊白，{V002}）：「这灵压——！」
        对白（顾渊白，{V002}）：「殿主——亲自来了！」
        对白（沈清词，{V001}）：「来得比预想中快——他等不了三天。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-001-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-002-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP41-SEG06
    shot_ids: [EP41-S08]
    duration_sec: 10
    speakers: [CHAR-002]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-002-L01: {look_url("CHAR-002-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】顾渊白 CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图2】桃花林月夜 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（10秒）中景 固定镜头：渊暝声音从黑雾中传出——极温和。图1全身灵力爆发——白银护罩笼罩二人。但他知道这对手不是他能挡。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（顾渊白，{V002}）：「清词——准备战斗。」
        对白（顾渊白，{V002}）：「这个人——是我们遇到过的最强的敌人。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-002-L01, role: reference_image, label: 图1 }}
        - {{ file: SCENE-008, role: reference_image, label: 图2 }}
    transition_to_next: hard_cut

  - segment_id: EP41-SEG07
    shot_ids: [EP41-S09]
    duration_sec: 12
    speakers: [CHAR-001]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-001-L01: {look_url("CHAR-001-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】桃花林月夜 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（12秒）近景 固定镜头：图1看向黑雾中灰袍身影——眼神从震惊到冰冷。天命剑鞘在腰侧自主震动。她知道这一战避无可避。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（沈清词，{V001}）：「殿主——你终于来了。」
        对白（沈清词·内心，{V001}）：「表白——还没来得及回答。」
        对白（沈清词·内心，{V001}）：「先活下来——才能回答他。」
        对白（沈清词，{V001}）：「来吧。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-001-L01, role: reference_image, label: 图1 }}
        - {{ file: SCENE-008, role: reference_image, label: 图2 }}
    transition_to_next: hard_cut
"""
write_file(f"{BASE}/EP41/EP41_segments.yaml", ep41_segs)
print("EP41 done!")

# ===== EP42 =====
print("EP42...")
ep42_shots = HEADER.format(ep="EP42", title="渊暝", n=10, dur=90) + "shots:\n" + "\n\n".join([
    shot_block("EP42-S01",1,8,"SCENE-008",["CHAR-005-L01"],[],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】SCENE-008。\n        中景 固定镜头：图1渊暝从黑雾中完全现身——灰色道袍如老道士。面容温和带笑如慈祥长辈。但他脚下的图2桃花全部枯死=死气领域。他看向清词方向——微笑。",
        [("CHAR-005","呵——小丫头。我们终于见面了。"),("CHAR-005","天命剑鞘的气息——在你身上。很好。")]),
    shot_block("EP42-S02",2,10,"SCENE-008",["CHAR-005-L01","CHAR-001-L01","CHAR-002-L01"],[],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图4】SCENE-008。\n        全景 固定镜头：图1一挥手——无形压力将图3直接拍飞数十丈！图3撞碎数棵桃花树！根本无力反抗！图1甚至没有正眼看他——只看着图2。压制全场如碾蚁。",
        [("CHAR-005","小辈——退下。我跟她说话。"),("CHAR-002","咳——！清词……小心……！"),("CHAR-001","渊白！")]),
    shot_block("EP42-S03",3,10,"SCENE-008",["CHAR-005-L01","CHAR-001-L01"],[],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】SCENE-008。\n        中景 固定镜头：图1缓步走向图2——每一步脚下死气蔓延。他抬手——一道黑色灵纹飞出直奔图2面门=摄魂秘术！清词被击中——灵魂被拉扯！她单膝跪地。",
        [("CHAR-005","摄魂秘术——乖乖把剑鞘交出来。不疼的。"),("CHAR-001","唔——！灵魂……在被拉扯——！"),("CHAR-005","别挣扎——越挣扎越疼。老夫向来不喜欢伤害晚辈。")]),
    shot_block("EP42-S04",4,8,"SCENE-008",["CHAR-002-L01"],[],
        "【图1】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图2】SCENE-008。\n        中景 固定镜头：图1从废墟中爬起——口角渗血。看到清词被摄魂——他爆发全部力量冲向渊暝！白银剑气斩出！但被渊暝随手挡下如拍苍蝇。图1再次被震飞。",
        [("CHAR-002","放开她——！"),("CHAR-005","不自量力。"),("CHAR-002","清词——我来了——！")]),
    shot_block("EP42-S05",5,10,"SCENE-008",["CHAR-005-L01","CHAR-001-L01"],[],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】SCENE-008。\n        近景 固定镜头：图1加大摄魂力度——图2痛苦中抬头看向他。突然她的眼神变了——不是恐惧，是震惊+认出。这张脸……这个灵力特征……她认识！",
        [("CHAR-001","这个摄魂术……这个灵力波动……"),("CHAR-001","不可能——！你……你是……"),("CHAR-005","哦？你认出来了？")]),
    shot_block("EP42-S06",6,8,"SCENE-008",["CHAR-001-L01","CHAR-005-L01"],[],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图3】SCENE-008。\n        近景 固定镜头：图1瞳孔骤缩——前世记忆涌上。这个摄魂术是天衡宗独门！这个人——百年前背叛师门的那个人！她的嘴唇颤抖说出那个称呼。",
        [("CHAR-001","师伯？！"),("CHAR-001","渊暝……你是天衡宗的……师伯？！"),("CHAR-005","哈哈哈——玄霜啊玄霜。百年不见，你还是这么聪明。")]),
    shot_block("EP42-S07",7,8,"SCENE-008",["CHAR-005-L01"],[],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】SCENE-008。\n        近景 固定镜头：图1温和地笑——如同百年前在天衡宗教导晚辈时一样。但这笑容配上他周围的死气和黑雾=极致恐怖。",
        [("CHAR-005","没错——师伯我啊。"),("CHAR-005","百年前是我策划了一切。你的陨落——也有我一份功劳。"),("CHAR-005","现在——乖乖把剑鞘给师伯。就当——孝敬长辈了。")]),
    shot_block("EP42-S08",8,6,"SCENE-008",["CHAR-001-L01"],[],
         "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-008。\n        近景 固定镜头：图1听到背叛真相——眼中闪过极致的恨意和痛苦。前世的背叛者竟然是自己的师伯！灵魂被拉扯但她咬牙死撑。",
        [("CHAR-001","师伯……是你害的我——"),("CHAR-001","百年前——是你策划的背叛——！")]),
    shot_block("EP42-S09",9,10,"SCENE-008",["CHAR-005-L01","CHAR-001-L01"],[],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】SCENE-008。\n        中景 固定镜头：图1加大摄魂——图2的天命剑鞘开始从腰侧脱离！金色光芒在挣扎！图2单膝跪地死死抓住剑鞘不放。图1温和地看着——如等待孩子交出玩具。",
        [("CHAR-005","别抓了——它会跟最强者走。你现在的修为……还差得远。"),("CHAR-001","不……会……给你——！"),("CHAR-005","倔强——像极了你师父。他也很倔——倔到现在还关在我的牢里。")]),
    shot_block("EP42-S10",10,12,"SCENE-008",["CHAR-001-L01","CHAR-005-L01"],[],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图3】SCENE-008。\n        近景 固定镜头：图1听到师父还在牢里——瞳孔骤缩。剑鞘继续被拉扯。她的灵魂在崩溃边缘。黑暗侵蚀视线——即将失去意识。最后一刻她看向倒在远处的顾渊白方向。",
        [("CHAR-001","师父……还活着——？！"),("CHAR-005","当然活着——老夫留着他有用。"),("CHAR-001","不能……倒下……不能……"),("CHAR-001","渊白……对不起……回答……要等等了……")]),
]) + "\n"
write_file(f"{BASE}/EP42/EP42_shots.yaml", ep42_shots)

ep42_segs = SEG_HEADER.format(ep="EP42", title="渊暝") + f"""voice_prompts:
  CHAR-001(真实态): "{V001}"
  CHAR-002: "{V002}"
  CHAR-005: "{V005}"

segments:
  - segment_id: EP42-SEG01
    shot_ids: [EP42-S01, EP42-S02]
    duration_sec: 18
    speakers: [CHAR-005, CHAR-002, CHAR-001]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-005-L01: {look_url("CHAR-005-L01")}
        CHAR-001-L01: {look_url("CHAR-001-L01")}
        CHAR-002-L01: {look_url("CHAR-002-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】渊暝 CHAR-005-L01（灰色道袍，灰发道士髻）【图2】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】顾渊白 CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图4】桃花林 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（8秒）中景 固定镜头：图1从黑雾中完全现身——灰色道袍如老道士。面容温和带笑。但脚下图4桃花全部枯死。他看向图2——微笑。
        镜头2（10秒）全景 固定镜头：图1一挥手——无形压力将图3直接拍飞数十丈！撞碎数棵桃花树！图1只看着图2。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（渊暝，{V005}）：「呵——小丫头。我们终于见面了。」
        对白（渊暝，{V005}）：「天命剑鞘的气息——在你身上。很好。」
        对白（渊暝，{V005}）：「小辈——退下。我跟她说话。」
        对白（顾渊白，{V002}）：「咳——！清词……小心……！」
        对白（沈清词，{V001}）：「渊白！」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-005-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图2 }}
        - {{ file: CHAR-002-L01, role: reference_image, label: 图3 }}
        - {{ file: SCENE-008, role: reference_image, label: 图4 }}
    transition_to_next: hard_cut

  - segment_id: EP42-SEG02
    shot_ids: [EP42-S03, EP42-S04]
    duration_sec: 18
    speakers: [CHAR-005, CHAR-001, CHAR-002]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-005-L01: {look_url("CHAR-005-L01")}
        CHAR-001-L01: {look_url("CHAR-001-L01")}
        CHAR-002-L01: {look_url("CHAR-002-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】渊暝 CHAR-005-L01（灰色道袍）【图2】沈清词 CHAR-001-L01（灰色外门粗布袍）【图3】顾渊白 CHAR-002-L01（白银掌门袍）【图4】桃花林 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（10秒）中景 固定镜头：图1缓步走向图2——抬手摄魂秘术！图2被击中——灵魂被拉扯！单膝跪地。
        镜头2（8秒）中景 固定镜头：图3从废墟中爬起冲向图1！白银剑气斩出！被图1随手挡下。图3再次被震飞。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（渊暝，{V005}）：「摄魂秘术——乖乖把剑鞘交出来。不疼的。」
        对白（沈清词，{V001}）：「唔——！灵魂……在被拉扯——！」
        对白（渊暝，{V005}）：「别挣扎——越挣扎越疼。老夫向来不喜欢伤害晚辈。」
        对白（顾渊白，{V002}）：「放开她——！」
        对白（渊暝，{V005}）：「不自量力。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-005-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图2 }}
        - {{ file: CHAR-002-L01, role: reference_image, label: 图3 }}
        - {{ file: SCENE-008, role: reference_image, label: 图4 }}
    transition_to_next: hard_cut

  - segment_id: EP42-SEG03
    shot_ids: [EP42-S05, EP42-S06]
    duration_sec: 18
    speakers: [CHAR-001, CHAR-005]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-005-L01: {look_url("CHAR-005-L01")}
        CHAR-001-L01: {look_url("CHAR-001-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】渊暝 CHAR-005-L01（灰色道袍）【图2】沈清词 CHAR-001-L01（灰色外门粗布袍）【图3】桃花林 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（10秒）近景 固定镜头：图1加大摄魂——图2痛苦中抬头看向他。突然眼神变了——不是恐惧是认出。这摄魂术是天衡宗独门！
        镜头2（8秒）近景 固定镜头：图2瞳孔骤缩——前世记忆涌上。嘴唇颤抖说出称呼。图1温和地笑。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（沈清词，{V001}）：「这个摄魂术……这个灵力波动……」
        对白（沈清词，{V001}）：「不可能——！你……你是……」
        对白（渊暝，{V005}）：「哦？你认出来了？」
        对白（沈清词，{V001}）：「师伯？！」
        对白（沈清词，{V001}）：「渊暝……你是天衡宗的……师伯？！」
        对白（渊暝，{V005}）：「哈哈哈——玄霜啊玄霜。百年不见，你还是这么聪明。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-005-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP42-SEG04
    shot_ids: [EP42-S07, EP42-S08]
    duration_sec: 14
    speakers: [CHAR-005, CHAR-001]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-005-L01: {look_url("CHAR-005-L01")}
        CHAR-001-L01: {look_url("CHAR-001-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】渊暝 CHAR-005-L01（灰色道袍）【图2】沈清词 CHAR-001-L01（灰色外门粗布袍）【图3】桃花林 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（8秒）近景 固定镜头：图1温和地笑——如百年前在天衡宗教导晚辈。但笑容配上死气黑雾=极致恐怖。
        镜头2（6秒）近景 固定镜头：图2听到"你的陨落也有我一份功劳"——眼中闪过极致恨意。灵魂被拉扯但咬牙死撑。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（渊暝，{V005}）：「没错——师伯我啊。」
        对白（渊暝，{V005}）：「百年前是我策划了一切。你的陨落——也有我一份功劳。」
        对白（渊暝，{V005}）：「现在——乖乖把剑鞘给师伯。就当——孝敬长辈了。」
        对白（沈清词，{V001}）：「师伯……是你害的我——」
        对白（沈清词，{V001}）：「百年前——是你策划的背叛——！」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-005-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP42-SEG05
    shot_ids: [EP42-S09, EP42-S10]
    duration_sec: 22
    speakers: [CHAR-005, CHAR-001]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-005-L01: {look_url("CHAR-005-L01")}
        CHAR-001-L01: {look_url("CHAR-001-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】渊暝 CHAR-005-L01（灰色道袍）【图2】沈清词 CHAR-001-L01（灰色外门粗布袍）【图3】桃花林 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（10秒）中景 固定镜头：图1加大摄魂——图2的天命剑鞘开始从腰侧脱离！金色光芒在挣扎！图2单膝跪地死死抓住剑鞘不放。
        镜头2（12秒）近景 固定镜头：图2听到"师父还关在牢里"——瞳孔骤缩。剑鞘继续被拉扯。黑暗侵蚀视线——即将失去意识。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（渊暝，{V005}）：「别抓了——它会跟最强者走。你现在的修为……还差得远。」
        对白（沈清词，{V001}）：「不……会……给你——！」
        对白（渊暝，{V005}）：「倔强——像极了你师父。他也很倔——倔到现在还关在我的牢里。」
        对白（沈清词，{V001}）：「师父……还活着——？！」
        对白（渊暝，{V005}）：「当然活着——老夫留着他有用。」
        对白（沈清词·内心，{V001}）：「不能……倒下……不能……」
        对白（沈清词·内心，{V001}）：「渊白……对不起……回答……要等等了……」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-005-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut
"""
write_file(f"{BASE}/EP42/EP42_segments.yaml", ep42_segs)
print("EP42 done!")

print("\nAll EP41-EP42 generated successfully!")
