#!/usr/bin/env python3
"""Build EP18 full-spec segments.yaml"""
import yaml, os, io

BASE = os.path.dirname(os.path.dirname(__file__))
TOS = "https://drama-reference-images.tos-cn-beijing.volces.com"

VP = {
    'CHAR-001': "成年女性，28岁，声线清冷偏低，语速中等偏慢，平时克制内敛，说话精准有力，装傻时语速加快语气上扬带无辜感，关键时刻语调沉稳有穿透力，偶尔停顿制造张力",
    'CHAR-002': "成年男性，30岁，语调平稳偏低沉，声线冷冽有磁性，语速偏慢惜字如金，每个字都有分量感，表达感情时语气突然变温柔略带笨拙，常以短句句号结尾制造停顿感",
    'CHAR-003': "成年女性，32岁，声线优雅柔和表面温暖，语速中等偏慢如演讲节奏，咬字清晰得体，每句话都带着精心设计的温柔感，暗含攻击时语调微微上扬带笑意，崩溃时语速加快声音尖锐语无伦次",
    'CHAR-006': "年轻男性，26岁，声线阳光开朗有感染力，语速快节奏跳跃，综艺感强自带笑点语气，说话常自问自答，正经时突然变得沉稳有力形成强烈反差",
    'CHAR-GRP-04': "年轻女性，28岁，声线恭顺谨慎，语速中等偏快，说话小心翼翼，下属对大明星的紧张语气",
}

DEFAULTS = """defaults:
  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
  model: doubao-seedance-2-0-fast-260128
  ratio: "9:16"
  resolution: 720p
  generate_audio: true
  watermark: false
  prompt_suffix: "禁止画面中出现任何文字或字幕。photorealistic, cinematic lighting, modern urban setting, 9:16 vertical frame, high detail, natural skin texture, film grain subtle"
  prompt_suffix_silent: "本段无对白无语音，禁止画面中出现任何文字。photorealistic, cinematic lighting, modern urban setting, 9:16 vertical frame, high detail, natural skin texture, film grain subtle"
  negative_prompt: "anime, cartoon, illustration, painting, watercolor, low quality, blurry, deformed face, extra limbs, extra fingers, mutated hands, watermark, text overlay, brand logo, oversaturated skin, plastic skin, uncanny valley, 3D render, CGI look"
"""

def tos_url(typ, id_):
    return f"{TOS}/{typ}/满级影后她装新人/{id_}.png"

def build_yaml(ep_id, source_md, voice_chars, segments_data):
    buf = io.StringIO()
    buf.write(f"episode_id: {ep_id}\n")
    buf.write(f"source_md: {source_md}\n\n")
    buf.write(DEFAULTS)
    buf.write("\nvoice_prompts:\n")
    for c in voice_chars:
        comment = "  # ⏳ 待生成" if "GRP" in c and c != "CHAR-GRP-17" else ""
        buf.write(f'  {c}: "{VP[c]}"{comment}\n')
    buf.write("\nsegments:\n")
    for i, seg in enumerate(segments_data):
        buf.write(f"  - segment_id: {seg['id']}\n")
        buf.write(f"    shot_ids: [{', '.join(seg['shots'])}]\n")
        buf.write(f"    duration_sec: {seg['dur']}\n")
        buf.write(f"    speakers: [{', '.join(seg['speakers'])}]\n")
        buf.write(f"    refs:\n")
        buf.write(f"      scene_id: {seg['scene']}\n")
        buf.write(f"    assets:\n")
        buf.write(f"      look_urls:\n")
        for lk in seg.get('looks', []):
            buf.write(f"        {lk}: {tos_url('looks', lk)}\n")
        buf.write(f"      scene_urls:\n")
        buf.write(f"        {seg['scene']}: {tos_url('scenes', seg['scene'])}\n")
        buf.write(f"    api:\n")
        buf.write(f"      text: |\n")
        for line in seg['text'].strip().split('\n'):
            buf.write(f"        {line}\n")
        buf.write(f"      content_roles:\n")
        for j, cr in enumerate(seg['cr']):
            buf.write(f"        - {{ file: {cr}, role: reference_image, label: 图{j+1} }}\n")
        trans = seg.get('transition', 'hard_cut')
        buf.write(f"    transition_to_next: {trans}\n")
        if i < len(segments_data) - 1:
            buf.write("\n")
    return buf.getvalue()

def build_ep18():
    vp = VP
    segs = []

    # SEG01: S01(5)+S02(5)=10s, speakers: CHAR-006
    segs.append({
        'id': 'EP18-SEG01', 'shots': ['EP18-S01', 'EP18-S02'], 'dur': 10,
        'speakers': ['CHAR-006'], 'scene': 'SCENE-006',
        'looks': ['CHAR-006-L01', 'CHAR-003-L01'],
        'cr': ['CHAR-006-L01', 'CHAR-003-L01', 'SCENE-006'],
        'text': f"""【图1】沈逸辰 CHAR-006-L01（浅蓝牛仔外套+白T）【图2】方芷晴 CHAR-003-L01（酒红色丝绒西装裙）【图3】综艺舞台 SCENE-006。
竖屏9比16连贯叙事。
镜头1（5秒）中景 固定镜头：综艺舞台灯光全开，巨大的LED屏上滚动着炫彩字样。图1站在舞台中央手持话筒，标志性的灿烂笑容，全场观众欢呼声此起彼伏。
镜头2（5秒）中全景 固定镜头：镜头摇向台下嘉宾席。图2坐在第一排评委席，面带完美微笑鼓掌。隔两个座位的位置上有人黑衣灰外套，单手随意搭在扶手上，目光扫向舞台。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（沈逸辰，{vp['CHAR-006']}）：「各位观众朋友们——欢迎来到新星计划杀青showcase！」
对白（沈逸辰，{vp['CHAR-006']}）：「今晚的舞台属于这群最耀眼的年轻人！」
对白（沈逸辰，{vp['CHAR-006']}）：「让我来介绍一下今晚的第一位表演者——」
画面全程无任何文字、字幕、标题、水印。
综艺舞台璀璨灯光，LED屏炫彩背景，现场观众欢呼氛围，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })

    # SEG02: S03(5)+S04(6)=11s, speakers: CHAR-006, CHAR-001
    segs.append({
        'id': 'EP18-SEG02', 'shots': ['EP18-S03', 'EP18-S04'], 'dur': 11,
        'speakers': ['CHAR-006', 'CHAR-001'], 'scene': 'SCENE-006',
        'looks': ['CHAR-006-L01', 'CHAR-001-L01'],
        'cr': ['CHAR-006-L01', 'CHAR-001-L01', 'SCENE-006'],
        'text': f"""【图1】沈逸辰 CHAR-006-L01（浅蓝牛仔外套+白T）【图2】苏念晚 CHAR-001-L01（白衬衫+浅蓝牛仔裙）【图3】综艺舞台 SCENE-006。
竖屏9比16连贯叙事。
镜头1（5秒）中近景 固定镜头：图1转身看向舞台入口，声音提高八度，现场欢呼声更热烈了。
镜头2（6秒）中景 镜头跟随：图2从舞台侧面走出来——没有华丽服装，白衬衫加浅蓝牛仔裙，简单干净。她走到舞台中央的话筒架前，微微低头调整话筒高度。聚光灯从上方打下，在她脸上投下柔和的光影。她抬起头，目光平静地扫过台下。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（沈逸辰，{vp['CHAR-006']}）：「网剧《追光》女主角——林小晚！」
对白（苏念晚，{vp['CHAR-001']}）：「这首歌……十年了。」
对白（苏念晚，{vp['CHAR-001']}）：「终于可以唱给你们听了。」
画面全程无任何文字、字幕、标题、水印。
综艺舞台聚光灯下，歌手登场的宁静时刻，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })

    # SEG03: S05(6)+S06(5)=11s, speakers: CHAR-001, CHAR-002
    segs.append({
        'id': 'EP18-SEG03', 'shots': ['EP18-S05', 'EP18-S06'], 'dur': 11,
        'speakers': ['CHAR-001', 'CHAR-002'], 'scene': 'SCENE-006',
        'looks': ['CHAR-001-L01', 'CHAR-002-L01'],
        'cr': ['CHAR-001-L01', 'CHAR-002-L01', 'SCENE-006'],
        'text': f"""【图1】苏念晚 CHAR-001-L01（白衬衫+浅蓝牛仔裙）【图2】陆景深 CHAR-002-L01（黑衣灰外套）【图3】综艺舞台 SCENE-006。
竖屏9比16连贯叙事。
镜头1（6秒）近景 固定镜头：前奏响起——一段清亮的钢琴前奏。图1闭上眼，等她再睁开时，整个人沉入了歌里。她的声音清澈而有穿透力，第一句唱出来，全场就安静了。
镜头2（5秒）中景 固定镜头：台下渐渐安静到几乎没有杂音。图2原本随意靠在椅背上的身体微微前倾——他被歌声吸引了。他看着台上的图1，眼神里多了一丝探究。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（苏念晚，{vp['CHAR-001']}）：「风停了，雨停了，只有回忆不肯停——」
对白（苏念晚，{vp['CHAR-001']}）：「你说过的话，像是刻在骨里的刺。」
对白（苏念晚，{vp['CHAR-001']}）：「那个夏天的梦，我从未忘记——」
对白（陆景深，{vp['CHAR-002']}）：「这个旋律……在哪里听过。」
画面全程无任何文字、字幕、标题、水印。
综艺舞台聚光灯独唱，全场寂静与歌声回荡，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })

    # SEG04: S07(5)+S08(6)=11s, speakers: CHAR-003, CHAR-001
    segs.append({
        'id': 'EP18-SEG04', 'shots': ['EP18-S07', 'EP18-S08'], 'dur': 11,
        'speakers': ['CHAR-003', 'CHAR-001'], 'scene': 'SCENE-006',
        'looks': ['CHAR-003-L01', 'CHAR-001-L01'],
        'cr': ['CHAR-003-L01', 'CHAR-001-L01', 'SCENE-006'],
        'text': f"""【图1】方芷晴 CHAR-003-L01（酒红色丝绒西装裙）【图2】苏念晚 CHAR-001-L01（白衬衫+浅蓝牛仔裙）【图3】综艺舞台 SCENE-006。
竖屏9比16连贯叙事。
镜头1（5秒）特写 固定镜头：图1原本漫不经心地看着台上——然后她的笑容凝固了。那首旋律像一把钥匙，插进了她记忆深处某个锁孔。她的手指猛地攥紧了座位扶手，指节泛白。
镜头2（6秒）中景 固定镜头：图2唱到副歌，目光扫过台下——精准地落在图1脸上。两人隔空对视，只有半秒。图2的眼神里带着一丝图1才能读懂的意味——不是挑衅，是确认。图1的完美微笑彻底碎了。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（方芷晴，{vp['CHAR-003']}）：「这个旋律——」
对白（方芷晴，{vp['CHAR-003']}）：「不可能……这不可能。」
对白（苏念晚，{vp['CHAR-001']}）：「当你以为我走了——我却在这里。」
对白（方芷晴，{vp['CHAR-003']}）：「她故意的。她就是冲我来的。」
画面全程无任何文字、字幕、标题、水印。
综艺舞台璀璨灯光下的暗流涌动，台上台下隔空对峙，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })

    # SEG05: S09(5)+S10(5)=10s, speakers: CHAR-001, CHAR-GRP-04, CHAR-003
    segs.append({
        'id': 'EP18-SEG05', 'shots': ['EP18-S09', 'EP18-S10'], 'dur': 10,
        'speakers': ['CHAR-001', 'CHAR-GRP-04', 'CHAR-003'], 'scene': 'SCENE-006',
        'looks': ['CHAR-001-L01', 'CHAR-003-L01'],
        'cr': ['CHAR-001-L01', 'CHAR-003-L01', 'SCENE-006'],
        'text': f"""【图1】苏念晚 CHAR-001-L01（白衬衫+浅蓝牛仔裙）【图2】方芷晴 CHAR-003-L01（酒红色丝绒西装裙）【图3】综艺舞台 SCENE-006。
竖屏9比16连贯叙事。
镜头1（5秒）大特写 镜头推近：图1闭着眼唱到最高潮——她的声音微微颤抖，不是紧张，是十年的情绪在这一刻倾泻而出。聚光灯把她的影子拉得很长。观众席中，有人悄悄抹了抹眼角。
镜头2（5秒）近景 固定镜头：图2的助理从侧台快步走来，弯腰凑到图2耳边压低声音。图2听完，脸色由白转青——她死死盯着台上，呼吸变得急促。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（苏念晚，{vp['CHAR-001']}）：「我回来了——以你认不出的方式。」
对白（助理，{vp['CHAR-GRP-04']}）：「方老师，这首歌……我十年前在一张Demo上听过。」
对白（方芷晴，{vp['CHAR-003']}）：「闭嘴。我知道。」
画面全程无任何文字、字幕、标题、水印。
综艺舞台歌声高潮与台下的震惊暗涌，聚光灯与侧台阴影对比，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })

    # SEG06: S11(6)+S12(5)=11s, speakers: CHAR-006, CHAR-001, CHAR-002
    segs.append({
        'id': 'EP18-SEG06', 'shots': ['EP18-S11', 'EP18-S12'], 'dur': 11,
        'speakers': ['CHAR-006', 'CHAR-001', 'CHAR-002'], 'scene': 'SCENE-006',
        'looks': ['CHAR-001-L01', 'CHAR-006-L01', 'CHAR-003-L01'],
        'cr': ['CHAR-001-L01', 'CHAR-006-L01', 'CHAR-003-L01', 'SCENE-006'],
        'text': f"""【图1】苏念晚 CHAR-001-L01（白衬衫+浅蓝牛仔裙）【图2】沈逸辰 CHAR-006-L01（浅蓝牛仔外套+白T）【图3】方芷晴 CHAR-003-L01（酒红色丝绒西装裙）【图4】综艺舞台 SCENE-006。
竖屏9比16连贯叙事。
镜头1（6秒）中景 固定镜头：歌曲结束。图1深深鞠躬。全场爆发出雷鸣般的掌声——甚至有观众站起来鼓掌。图2快步走上台，做出一副被震撼到说不出话的表情。
镜头2（5秒）中景 固定镜头：图3突然从座位上站起来——在全场注目中转身快步离席，高跟鞋敲击地面的声音急促。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（沈逸辰，{vp['CHAR-006']}）：「太好听了……我这眼泪都出来了。小晚你也太深藏不露了吧！」
对白（苏念晚，{vp['CHAR-001']}）：「谢谢沈老师，谢谢大家。」
对白（陆景深，{vp['CHAR-002']}）：「她认出来了。」
画面全程无任何文字、字幕、标题、水印。
综艺舞台掌声雷动与离席的紧张反差，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })

    # SEG07: S13(6)+S14(5)=11s, speakers: CHAR-003, CHAR-GRP-04
    segs.append({
        'id': 'EP18-SEG07', 'shots': ['EP18-S13', 'EP18-S14'], 'dur': 11,
        'speakers': ['CHAR-003', 'CHAR-GRP-04'], 'scene': 'SCENE-006',
        'looks': ['CHAR-003-L01'],
        'cr': ['CHAR-003-L01', 'SCENE-006'],
        'transition': 'audio_bridge',
        'text': f"""【图1】方芷晴 CHAR-003-L01（酒红色丝绒西装裙）【图2】综艺舞台后台走廊 SCENE-006。
竖屏9比16连贯叙事。
镜头1（6秒）中景 镜头跟随：后台走廊灯光惨白，与舞台的璀璨形成鲜明对比。图1疾步走在前面，助理小跑着追在身后。图1的表情在脱离公众视线后彻底垮掉——没有微笑，只有阴鸷。
镜头2（5秒）特写 固定镜头：图1停在一盏日光灯下，脸上的光让她看起来苍白而可怖。她低头想了三秒，然后缓缓抬起眼——那眼神里有一丝恐惧，但更多的是狠厉。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（方芷晴，{vp['CHAR-003']}）：「选曲是谁定的？」
对白（助理，{vp['CHAR-GRP-04']}）：「是她自己报的曲目……节目组没干涉。」
对白（方芷晴，{vp['CHAR-003']}）：「她就这么明目张胆。」
对白（方芷晴，{vp['CHAR-003']}）：「她不怕被认出来？」
对白（方芷晴，{vp['CHAR-003']}）：「她是故意的。」
画面全程无任何文字、字幕、标题、水印。
后台走廊惨白日光灯，阴冷压抑氛围，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })

    # SEG08: S15(6)+S16(6)=12s, speakers: CHAR-003, CHAR-GRP-04, transition: fade
    segs.append({
        'id': 'EP18-SEG08', 'shots': ['EP18-S15', 'EP18-S16'], 'dur': 12,
        'speakers': ['CHAR-003', 'CHAR-GRP-04'], 'scene': 'SCENE-006',
        'looks': ['CHAR-003-L01'],
        'cr': ['CHAR-003-L01', 'SCENE-006'],
        'transition': 'fade',
        'text': f"""【图1】方芷晴 CHAR-003-L01（酒红色丝绒西装裙）【图2】综艺舞台后台走廊 SCENE-006。
竖屏9比16连贯叙事。
镜头1（6秒）中近景 固定镜头：图1转身面对助理，声音压到最低但每个字都像冰锥。走廊尽头传来舞台的欢呼声，衬得这段对话格外隐秘。
镜头2（6秒）特写 固定镜头：图1的瞳孔里映着惨白的灯光，那张精致的脸在阴影里半明半暗。她说完这句话后，嘴角浮起一个极其危险的弧度——不是笑，是下定决心的冷意。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（方芷晴，{vp['CHAR-003']}）：「那首歌……是苏念晚写的。」
对白（助理，{vp['CHAR-GRP-04']}）：「苏……苏念晚？！」
对白（方芷晴，{vp['CHAR-003']}）：「她不可能只是一个新人。」
对白（方芷晴，{vp['CHAR-003']}）：「查。给我查清楚她到底想干什么。」
画面全程无任何文字、字幕、标题、水印。
后台走廊惨白灯光下的冰冷决心，阴影与光明对半，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })

    content = build_yaml('EP18', '剧本/EP18/EP18_综艺名场面.md',
        ['CHAR-001', 'CHAR-002', 'CHAR-003', 'CHAR-006', 'CHAR-GRP-04'], segs)

    out_path = os.path.join(BASE, '剧本/EP18/EP18_segments.yaml')
    with open(out_path, 'w') as f:
        f.write(content)

    # Verify
    data = yaml.safe_load(content)
    total = sum(s['duration_sec'] for s in data['segments'])
    shots = sum(len(s['shot_ids']) for s in data['segments'])
    seg_count = len(data['segments'])
    print(f"EP18: {seg_count} segments, {shots} shots, {total}s")

    # Shot ID check
    expected = [f'EP18-S{i:02d}' for i in range(1, 17)]
    actual = []
    for s in data['segments']:
        actual.extend(s['shot_ids'])
    if actual == expected:
        print("  Shot IDs: ✅ match")
    else:
        print(f"  Shot IDs: ❌ expected {expected}, got {actual}")

    # Duration check
    if 75 <= total <= 120:
        print(f"  Duration: ✅ {total}s (75-120 range)")
    else:
        print(f"  Duration: ❌ {total}s out of range")

    # Segment duration check
    for s in data['segments']:
        d = s['duration_sec']
        if d < 4 or d > 12:
            print(f"  ❌ {s['segment_id']} duration {d}s out of 4-12 range")

    # URL check
    for s in data['segments']:
        for k, v in s['assets'].get('look_urls', {}).items():
            if 'tos-cn-beijing' not in v:
                print(f"  ⚠️ {k}: {v} (not TOS)")

    print("  Write: ✅")

build_ep18()
