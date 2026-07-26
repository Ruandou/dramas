#!/usr/bin/env python3
"""Generate shots.yaml and segments.yaml for EP43-EP44."""
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
  model: doubao-seedance-2-0-fast
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
  model: doubao-seedance-2-0-fast
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

# ===== EP43 =====
print("EP43...")
ep43_shots = HEADER.format(ep="EP43", title="认主", n=9, dur=80) + "shots:\n" + "\n\n".join([
    shot_block("EP43-S01",1,10,"SCENE-008",["CHAR-005-L01"],[],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】SCENE-008。\n        近景 固定镜头：图1渊暝继续温和地说——如同讲述一段往事给晚辈听。他不急不缓。死气在他周围如浓雾翻涌。面容温和带笑。",
        [("CHAR-005","百年前——不只是我一个人。"),("CHAR-005","你的二师兄、三师姐——还有那些你信任的长老们。"),("CHAR-005","他们都参与了。你太强了——强到他们害怕。")]),
    shot_block("EP43-S02",2,8,"SCENE-008",["CHAR-001-L01"],[],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-008。\n        近景 固定镜头：图1跪在地上——听到师门多人参与背叛。眼中最后一丝光芒在熄灭。灵魂被摄魂术持续侵蚀。但手依然死死抓着腰间剑鞘——手指泛白。",
        [("CHAR-001","二师兄……三师姐也……"),("CHAR-001","我信任的人……全部都……"),("CHAR-001","不会放手……绝不……")]),
    shot_block("EP43-S03",3,10,"SCENE-008",["CHAR-005-L01","CHAR-001-L01"],[],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】SCENE-008。\n        中景 固定镜头：图1双手结印——摄魂术升级最高阶！黑色灵纹从地面升起缠绕图2全身如锁链！图2发出无声嘶吼——灵魂正在被强行剥离身体！",
        [("CHAR-005","最后一次——交出来吧。"),("CHAR-005","师伯不想伤害你。真的。"),("CHAR-001","啊——！！！")]),
    shot_block("EP43-S04",4,8,"SCENE-008",["CHAR-001-L01"],[],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-008。\n        特写 固定镜头：图1面容——泪水无意识流下。不是恐惧的泪——是愤怒和不甘。视线模糊。金色剑鞘已经脱离一半悬浮在身侧。",
        [("CHAR-001","不甘心——"),("CHAR-001","百年前输了一次——不能再输。"),("CHAR-001","你是我的——谁都别想拿走——")]),
    shot_block("EP43-S05",5,6,"SCENE-008",["CHAR-005-L01","CHAR-001-L01"],["PROP-003"],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】SCENE-008【图4】PROP-003。\n        中景 固定镜头：图1伸手——就要抓住图4天命剑鞘。金色剑鞘悬浮在图2和图1之间——两股力量拉扯。图1嘴角上扬——胜券在握。",
        [("CHAR-005","到手了——"),("CHAR-001","不要——！！")]),
    shot_block("EP43-S06",6,8,"SCENE-008",["CHAR-001-L01"],["PROP-003"],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-008【图3】PROP-003。\n        近景 固定镜头：渊暝即将触碰剑鞘的瞬间——图3突然爆发出刺目金光！金色光芒从内部向外扩散如太阳！渊暝的手被灼伤弹开！图1感到温暖力量涌入灵魂。",
        [("CHAR-001","这是——剑鞘……在回应我？"),("CHAR-001","它在……保护我——！")]),
    shot_block("EP43-S07",7,10,"SCENE-008",["CHAR-001-L01"],["PROP-003"],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-008【图3】PROP-003。\n        中景 固定镜头：图3天命剑鞘飞回图1手中——金色光芒大盛！剑鞘自主认主！金色铭文在图1手臂上浮现如烙印！银白发丝在金光中飞舞——前世巅峰气息涌出！",
        [("CHAR-001","天命剑鞘——认主了……"),("CHAR-001","我接受。")]),
    shot_block("EP43-S08",8,8,"SCENE-008",["CHAR-001-L01","CHAR-005-L01"],["PROP-003"],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图3】SCENE-008【图4】PROP-003。\n        全景 固定镜头：以图1为中心——金色冲击波向外爆发！摄魂术黑色锁链全部粉碎！图2被震退数十丈——第一次面露惊色！枯死桃花重新绽放！",
        [("CHAR-005","这——！自主认主？！不可能！"),("CHAR-005","区区转世之身——凭什么让它自主认主——！")]),
    shot_block("EP43-S09",9,12,"SCENE-008",["CHAR-001-L01","CHAR-005-L01"],["PROP-003"],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图3】SCENE-008【图4】PROP-003。\n        中景 固定镜头：图1站起——金色光芒环绕全身如战甲。图4剑鞘在手中嗡鸣。她看向图2——眼中是千年师尊威压。图2面色从惊色恢复温和——但后退一步。",
        [("CHAR-001","师伯——你说师父还活着。"),("CHAR-001","我会去救他。"),("CHAR-001","在那之前——你最好祈祷我不要太快找到你。"),("CHAR-005","有意思……下次见。玄霜。")]),
]) + "\n"
write_file(f"{BASE}/EP43/EP43_shots.yaml", ep43_shots)

ep43_segs = SEG_HEADER.format(ep="EP43", title="认主") + f"""voice_prompts:
  CHAR-001(真实态): "{V001}"
  CHAR-005: "{V005}"

segments:
  - segment_id: EP43-SEG01
    shot_ids: [EP43-S01, EP43-S02]
    duration_sec: 18
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
        【图1】渊暝 CHAR-005-L01（灰色道袍，灰发道士髻）【图2】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】桃花林 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（10秒）近景 固定镜头：图1继续温和地说——如讲述往事给晚辈听。不急不缓。死气翻涌。
        镜头2（8秒）近景 固定镜头：图2跪在地上——听到多人背叛。眼中光芒熄灭。手死死抓着剑鞘——手指泛白。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（渊暝，{V005}）：「百年前——不只是我一个人。」
        对白（渊暝，{V005}）：「你的二师兄、三师姐——还有那些你信任的长老们。」
        对白（渊暝，{V005}）：「他们都参与了。你太强了——强到他们害怕。」
        对白（沈清词，{V001}）：「二师兄……三师姐也……」
        对白（沈清词，{V001}）：「我信任的人……全部都……」
        对白（沈清词，{V001}）：「不会放手……绝不……」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-005-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP43-SEG02
    shot_ids: [EP43-S03]
    duration_sec: 10
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
        镜头1（10秒）中景 固定镜头：图1双手结印——摄魂术升级最高阶！黑色灵纹从地面升起缠绕图2全身如锁链！图2无声嘶吼——灵魂强行剥离！
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（渊暝，{V005}）：「最后一次——交出来吧。」
        对白（渊暝，{V005}）：「师伯不想伤害你。真的。」
        对白（沈清词，{V001}）：「啊——！！！」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-005-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP43-SEG03
    shot_ids: [EP43-S04, EP43-S05]
    duration_sec: 14
    speakers: [CHAR-001, CHAR-005]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-001-L01: {look_url("CHAR-001-L01")}
        CHAR-005-L01: {look_url("CHAR-005-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls:
        PROP-003: {prop_url("PROP-003")}
    api:
      text: |
        【图1】沈清词 CHAR-001-L01（灰色外门粗布袍）【图2】渊暝 CHAR-005-L01（灰色道袍）【图3】桃花林 SCENE-008【图4】天命剑鞘 PROP-003。
        竖屏9比16连贯叙事。
        镜头1（8秒）特写 固定镜头：图1面容——泪水无意识流下。不是恐惧——是不甘。图4剑鞘已脱离一半悬浮身侧。
        镜头2（6秒）中景 固定镜头：图2伸手——就要抓住图4。金色剑鞘悬浮在图1和图2之间——两股力量拉扯。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（沈清词·内心，{V001}）：「不甘心——」
        对白（沈清词·内心，{V001}）：「百年前输了一次——不能再输。」
        对白（沈清词·内心，{V001}）：「你是我的——谁都别想拿走——」
        对白（渊暝，{V005}）：「到手了——」
        对白（沈清词，{V001}）：「不要——！！」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-001-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-005-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
        - {{ file: PROP-003, role: reference_image, label: 图4 }}
    transition_to_next: hard_cut

  - segment_id: EP43-SEG04
    shot_ids: [EP43-S06]
    duration_sec: 8
    speakers: [CHAR-001]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-001-L01: {look_url("CHAR-001-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls:
        PROP-003: {prop_url("PROP-003")}
    api:
      text: |
        【图1】沈清词 CHAR-001-L01（灰色外门粗布袍）【图2】桃花林 SCENE-008【图3】天命剑鞘 PROP-003。
        竖屏9比16连贯叙事。
        镜头1（8秒）近景 固定镜头：渊暝即将触碰剑鞘瞬间——图3爆发刺目金光！金色光芒如太阳向外扩散！渊暝手被灼伤弹开！图1感到温暖力量涌入灵魂。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（沈清词，{V001}）：「这是——剑鞘……在回应我？」
        对白（沈清词，{V001}）：「它在……保护我——！」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-001-L01, role: reference_image, label: 图1 }}
        - {{ file: SCENE-008, role: reference_image, label: 图2 }}
        - {{ file: PROP-003, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP43-SEG05
    shot_ids: [EP43-S07, EP43-S08]
    duration_sec: 18
    speakers: [CHAR-001, CHAR-005]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-001-L01: {look_url("CHAR-001-L01")}
        CHAR-005-L01: {look_url("CHAR-005-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls:
        PROP-003: {prop_url("PROP-003")}
    api:
      text: |
        【图1】沈清词 CHAR-001-L01（灰色外门粗布袍）【图2】渊暝 CHAR-005-L01（灰色道袍）【图3】桃花林 SCENE-008【图4】天命剑鞘 PROP-003。
        竖屏9比16连贯叙事。
        镜头1（10秒）中景 固定镜头：图4飞回图1手中——金色光芒大盛！剑鞘自主认主！金色铭文在图1手臂浮现如烙印！银白发丝在金光中飞舞！
        镜头2（8秒）全景 固定镜头：以图1为中心——金色冲击波向外爆发！摄魂黑色锁链全部粉碎！图2被震退数十丈——首次面露惊色！枯死桃花重新绽放！
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（沈清词，{V001}）：「天命剑鞘——认主了……」
        对白（沈清词，{V001}）：「我接受。」
        对白（渊暝，{V005}）：「这——！自主认主？！不可能！」
        对白（渊暝，{V005}）：「区区转世之身——凭什么让它自主认主——！」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-001-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-005-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
        - {{ file: PROP-003, role: reference_image, label: 图4 }}
    transition_to_next: hard_cut

  - segment_id: EP43-SEG06
    shot_ids: [EP43-S09]
    duration_sec: 12
    speakers: [CHAR-001, CHAR-005]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-001-L01: {look_url("CHAR-001-L01")}
        CHAR-005-L01: {look_url("CHAR-005-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls:
        PROP-003: {prop_url("PROP-003")}
    api:
      text: |
        【图1】沈清词 CHAR-001-L01（灰色外门粗布袍）【图2】渊暝 CHAR-005-L01（灰色道袍）【图3】桃花林 SCENE-008【图4】天命剑鞘 PROP-003。
        竖屏9比16连贯叙事。
        镜头1（12秒）中景 固定镜头：图1站起——金色光芒环绕全身如战甲。图4在手中嗡鸣。她看向图2——千年师尊威压。图2面色恢复温和——但后退一步。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（沈清词，{V001}）：「师伯——你说师父还活着。」
        对白（沈清词，{V001}）：「我会去救他。」
        对白（沈清词，{V001}）：「在那之前——你最好祈祷我不要太快找到你。」
        对白（渊暝，{V005}）：「有意思……下次见。玄霜。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-001-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-005-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
        - {{ file: PROP-003, role: reference_image, label: 图4 }}
    transition_to_next: hard_cut
"""
write_file(f"{BASE}/EP43/EP43_segments.yaml", ep43_segs)
print("EP43 done!")

# ===== EP44 =====
print("EP44...")
ep44_shots = HEADER.format(ep="EP44", title="援军", n=9, dur=82) + "shots:\n" + "\n\n".join([
    shot_block("EP44-S01",1,10,"SCENE-008",["CHAR-004-L01"],[],
        "【图1】CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图2】SCENE-008。\n        全景 固定镜头：天际——无数飞剑如流星划破夜空！青色白色金色灵光汇成光河！图1季云舟率全宗弟子+友方修士从远方赶至！数百人飞剑列阵！号角声响彻云霄！",
        [("CHAR-004","天璇宗全员——已到！"),("CHAR-004","师妹！掌门！我们来了——！")]),
    shot_block("EP44-S02",2,8,"SCENE-008",["CHAR-004-L01","CHAR-005-L01"],[],
        "【图1】CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图2】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图3】SCENE-008。\n        全景 固定镜头：数百修士落地展开阵型包围图2！图1折扇一挥——十二道剑光锁定渊暝方位！友方长老灵力汇聚——巨型封印阵法启动！",
        [("CHAR-004","六方封印阵——起！"),("CHAR-005","哦——来了不少人。有意思。")]),
    shot_block("EP44-S03",3,10,"SCENE-008",["CHAR-002-L01","CHAR-001-L01"],["PROP-003"],
        "【图1】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图2】CHAR-001-L01（灰色外门粗布袍，低马尾）【图3】SCENE-008【图4】PROP-003。\n        中景 固定镜头：图1挣扎站起——走到图2身边。两人相视。图2手中图4金光未灭——她还站着。图1伸手握住她的手——两人并肩面对渊暝。",
        [("CHAR-002","你没事……太好了。"),("CHAR-001","答案——等打完再说。"),("CHAR-002","好。一起。")]),
    shot_block("EP44-S04",4,10,"SCENE-008",["CHAR-005-L01"],[],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】SCENE-008。\n        中景 固定镜头：图1环视被围——面色依然温和。轻轻一挥袖——死气波动将数名冲锋弟子震退！但没有伤人——只是防御。他在思考。",
        [("CHAR-005","人数不少——但可惜。蚁群再多——也只是蚁群。"),("CHAR-005","不过……天命剑鞘已认主。今天——强取不了了。")]),
    shot_block("EP44-S05",5,12,"SCENE-008",["CHAR-005-L01"],[],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】SCENE-008。\n        近景 固定镜头：图1收起死气——双手负后。如散步老者准备离去。面向清词方向——微笑如慈祥长辈留下教诲。但每个字都是冰冷威胁。",
        [("CHAR-005","今天就到这里吧——小丫头。"),("CHAR-005","对了——你师父还在我那里做客。住得很好。"),("CHAR-005","一个月后——我再来。届时带上你师父。"),("CHAR-005","你若乖乖交出剑鞘——或许还能父女团聚。")]),
    shot_block("EP44-S06",6,8,"SCENE-008",["CHAR-005-L01","CHAR-004-L01"],[],
        "【图1】CHAR-005-L01（灰色道袍，灰发道士髻，铁发簪）【图2】CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图3】SCENE-008。\n        全景 固定镜头：图1身形化为黑雾——直接穿透封印阵法升空！六方封印阵如纸般破碎！众修士惊骇。图1如来时一样从容离去。",
        [("CHAR-004","封印阵——被直接穿透了？！"),("CHAR-005","一个月——记住了。")]),
    shot_block("EP44-S07",7,6,"SCENE-008",["CHAR-001-L01"],["PROP-003"],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-008【图3】PROP-003。\n        近景 固定镜头：图1看着渊暝远去方向——手中图3金光缓缓收敛。表情不是恐惧——是决然。一个月——足够了。",
        [("CHAR-001","一个月——"),("CHAR-001","够了。")]),
    shot_block("EP44-S08",8,8,"SCENE-008",["CHAR-002-L01","CHAR-004-L01"],[],
        "【图1】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图2】CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图3】SCENE-008。\n        中景 固定镜头：图1和图2对视——无言确认平安。图2走上前扶住摇晃的掌门。战场上弟子们救治伤者。夜空恢复清澈——月光重新洒下。",
        [("CHAR-004","掌门！你的伤——"),("CHAR-002","无碍。她——才是关键。"),("CHAR-004","师妹她……那个金光——到底是什么？")]),
    shot_block("EP44-S09",9,10,"SCENE-008",["CHAR-001-L01","CHAR-002-L01"],[],
        "【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】CHAR-002-L01（白银宗门掌门袍，束发玉冠）【图3】SCENE-008。\n        中景 固定镜头：图1走向图2——月光洒在两人身上。她停在他面前。手中剑鞘安静。银白发丝被夜风拂动。表情从战意到一丝柔和。",
        [("CHAR-001","一个月。他给了一个月的时间。"),("CHAR-002","够吗？"),("CHAR-001","够。"),("CHAR-001","还有——上次的话……等这一切结束后。我给你答案。")]),
]) + "\n"
write_file(f"{BASE}/EP44/EP44_shots.yaml", ep44_shots)

ep44_segs = SEG_HEADER.format(ep="EP44", title="援军") + f"""voice_prompts:
  CHAR-001(真实态): "{V001}"
  CHAR-002: "{V002}"
  CHAR-004: "{V004}"
  CHAR-005: "{V005}"

segments:
  - segment_id: EP44-SEG01
    shot_ids: [EP44-S01]
    duration_sec: 10
    speakers: [CHAR-004]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-004-L01: {look_url("CHAR-004-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】季云舟 CHAR-004-L01（青色长衫，玉发簪散髻，折扇）【图2】桃花林 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（10秒）全景 固定镜头：天际——无数飞剑如流星划破夜空！图1率全宗弟子+友方修士从远方赶至！数百人飞剑列阵！号角声响彻！
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（季云舟，{V004}）：「天璇宗全员——已到！」
        对白（季云舟，{V004}）：「师妹！掌门！我们来了——！」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-004-L01, role: reference_image, label: 图1 }}
        - {{ file: SCENE-008, role: reference_image, label: 图2 }}
    transition_to_next: hard_cut

  - segment_id: EP44-SEG02
    shot_ids: [EP44-S02, EP44-S03]
    duration_sec: 18
    speakers: [CHAR-004, CHAR-005, CHAR-002, CHAR-001]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-004-L01: {look_url("CHAR-004-L01")}
        CHAR-005-L01: {look_url("CHAR-005-L01")}
        CHAR-002-L01: {look_url("CHAR-002-L01")}
        CHAR-001-L01: {look_url("CHAR-001-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls:
        PROP-003: {prop_url("PROP-003")}
    api:
      text: |
        【图1】季云舟 CHAR-004-L01（青色长衫）【图2】渊暝 CHAR-005-L01（灰色道袍）【图3】顾渊白 CHAR-002-L01（白银掌门袍）【图4】沈清词 CHAR-001-L01（灰色外门粗布袍）【图5】桃花林 SCENE-008【图6】天命剑鞘 PROP-003。
        竖屏9比16连贯叙事。
        镜头1（8秒）全景 固定镜头：数百修士包围图2！图1折扇一挥——十二道剑光锁定！封印阵法启动！
        镜头2（10秒）中景 固定镜头：图3挣扎站起走到图4身边。图4手中图6金光未灭。图3握住她手——两人并肩。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（季云舟，{V004}）：「六方封印阵——起！」
        对白（渊暝，{V005}）：「哦——来了不少人。有意思。」
        对白（顾渊白，{V002}）：「你没事……太好了。」
        对白（沈清词，{V001}）：「答案——等打完再说。」
        对白（顾渊白，{V002}）：「好。一起。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-004-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-005-L01, role: reference_image, label: 图2 }}
        - {{ file: CHAR-002-L01, role: reference_image, label: 图3 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图4 }}
        - {{ file: SCENE-008, role: reference_image, label: 图5 }}
        - {{ file: PROP-003, role: reference_image, label: 图6 }}
    transition_to_next: hard_cut

  - segment_id: EP44-SEG03
    shot_ids: [EP44-S04]
    duration_sec: 10
    speakers: [CHAR-005]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-005-L01: {look_url("CHAR-005-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】渊暝 CHAR-005-L01（灰色道袍，灰发道士髻）【图2】桃花林 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（10秒）中景 固定镜头：图1环视被围——面色温和。轻挥袖死气波动震退冲锋弟子。但没有伤人——只是防御。他在思考。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（渊暝，{V005}）：「人数不少——但可惜。蚁群再多——也只是蚁群。」
        对白（渊暝，{V005}）：「不过……天命剑鞘已认主。今天——强取不了了。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-005-L01, role: reference_image, label: 图1 }}
        - {{ file: SCENE-008, role: reference_image, label: 图2 }}
    transition_to_next: hard_cut

  - segment_id: EP44-SEG04
    shot_ids: [EP44-S05]
    duration_sec: 12
    speakers: [CHAR-005]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-005-L01: {look_url("CHAR-005-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】渊暝 CHAR-005-L01（灰色道袍，灰发道士髻）【图2】桃花林 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（12秒）近景 固定镜头：图1收起死气——双手负后。如散步老者准备离去。微笑如慈祥长辈——但每个字冰冷。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（渊暝，{V005}）：「今天就到这里吧——小丫头。」
        对白（渊暝，{V005}）：「对了——你师父还在我那里做客。住得很好。」
        对白（渊暝，{V005}）：「一个月后——我再来。届时带上你师父。」
        对白（渊暝，{V005}）：「你若乖乖交出剑鞘——或许还能父女团聚。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-005-L01, role: reference_image, label: 图1 }}
        - {{ file: SCENE-008, role: reference_image, label: 图2 }}
    transition_to_next: hard_cut

  - segment_id: EP44-SEG05
    shot_ids: [EP44-S06, EP44-S07]
    duration_sec: 14
    speakers: [CHAR-004, CHAR-005, CHAR-001]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-005-L01: {look_url("CHAR-005-L01")}
        CHAR-004-L01: {look_url("CHAR-004-L01")}
        CHAR-001-L01: {look_url("CHAR-001-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls:
        PROP-003: {prop_url("PROP-003")}
    api:
      text: |
        【图1】渊暝 CHAR-005-L01（灰色道袍）【图2】季云舟 CHAR-004-L01（青色长衫）【图3】沈清词 CHAR-001-L01（灰色外门粗布袍）【图4】桃花林 SCENE-008【图5】天命剑鞘 PROP-003。
        竖屏9比16连贯叙事。
        镜头1（8秒）全景 固定镜头：图1身形化为黑雾——穿透封印阵法升空！六方封印阵如纸般破碎！众修士惊骇。
        镜头2（6秒）近景 固定镜头：图3看着渊暝远去方向——手中图5金光缓缓收敛。表情决然。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（季云舟，{V004}）：「封印阵——被直接穿透了？！」
        对白（渊暝，{V005}）：「一个月——记住了。」
        对白（沈清词，{V001}）：「一个月——」
        对白（沈清词·内心，{V001}）：「够了。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-005-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-004-L01, role: reference_image, label: 图2 }}
        - {{ file: CHAR-001-L01, role: reference_image, label: 图3 }}
        - {{ file: SCENE-008, role: reference_image, label: 图4 }}
        - {{ file: PROP-003, role: reference_image, label: 图5 }}
    transition_to_next: hard_cut

  - segment_id: EP44-SEG06
    shot_ids: [EP44-S08]
    duration_sec: 8
    speakers: [CHAR-004, CHAR-002]
    refs: {{ scene_id: SCENE-008 }}
    assets:
      look_urls:
        CHAR-002-L01: {look_url("CHAR-002-L01")}
        CHAR-004-L01: {look_url("CHAR-004-L01")}
      scene_urls:
        SCENE-008: {scene_url("SCENE-008")}
      prop_urls: {{}}
    api:
      text: |
        【图1】顾渊白 CHAR-002-L01（白银掌门袍）【图2】季云舟 CHAR-004-L01（青色长衫）【图3】桃花林 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（8秒）中景 固定镜头：图1和图2对视——无言确认平安。图2走上前扶住摇晃的图1。弟子们救治伤者。月光洒下。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（季云舟，{V004}）：「掌门！你的伤——」
        对白（顾渊白，{V002}）：「无碍。她——才是关键。」
        对白（季云舟，{V004}）：「师妹她……那个金光——到底是什么？」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-002-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-004-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut

  - segment_id: EP44-SEG07
    shot_ids: [EP44-S09]
    duration_sec: 10
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
        【图1】沈清词 CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】顾渊白 CHAR-002-L01（白银掌门袍，束发玉冠）【图3】桃花林 SCENE-008。
        竖屏9比16连贯叙事。
        镜头1（10秒）中景 固定镜头：图1走向图2——月光洒在两人身上。她停在他面前。银白发丝被夜风拂动。表情从战意到一丝柔和。
        [以下对白仅供语音合成，严禁在画面中显示任何文字]
        对白（沈清词，{V001}）：「一个月。他给了一个月的时间。」
        对白（顾渊白，{V002}）：「够吗？」
        对白（沈清词，{V001}）：「够。」
        对白（沈清词，{V001}）：「还有——上次的话……等这一切结束后。我给你答案。」
        画面全程无任何文字、字幕、标题、水印。
        {STYLE}
      content_roles:
        - {{ file: CHAR-001-L01, role: reference_image, label: 图1 }}
        - {{ file: CHAR-002-L01, role: reference_image, label: 图2 }}
        - {{ file: SCENE-008, role: reference_image, label: 图3 }}
    transition_to_next: hard_cut
"""
write_file(f"{BASE}/EP44/EP44_segments.yaml", ep44_segs)
print("EP44 done!")

print("\nAll EP43-EP44 generated successfully!")
