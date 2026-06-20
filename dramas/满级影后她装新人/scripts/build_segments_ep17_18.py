#!/usr/bin/env python3
"""Build EP17 and EP18 full-spec segments.yaml files"""
import yaml, os, io

BASE = os.path.dirname(os.path.dirname(__file__))
TOS = "https://drama-reference-images.tos-cn-beijing.volces.com"

# Voice prompts (from voice card)
VP = {
    'CHAR-001': "成年女性，28岁，声线清冷偏低，语速中等偏慢，平时克制内敛，说话精准有力，装傻时语速加快语气上扬带无辜感，关键时刻语调沉稳有穿透力，偶尔停顿制造张力",
    'CHAR-002': "成年男性，30岁，语调平稳偏低沉，声线冷冽有磁性，语速偏慢惜字如金，每个字都有分量感，表达感情时语气突然变温柔略带笨拙，常以短句句号结尾制造停顿感",
    'CHAR-005': "年轻女性，20岁，声线甜美活泼明亮，语速快说话像机关枪，语气充满活力和天真感，紧张时语速更快声音微颤，背叛后说话变得小心翼翼声音压低，赎罪后恢复开朗但多了一份沉稳",
    'CHAR-GRP-18': "成年男性，40岁，声线职业化中气十足，语速中等偏快，导演指令干脆利落，兴奋时语调上扬声音变大",
}

DEFAULTS = """defaults:
  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
  model: doubao-seedance-2-0-fast
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
    """Build YAML string from structured segment data"""
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

# ============ EP17 ============
def build_ep17():
    vp = VP
    segs = []
    
    # SEG01: S01(5)+S02(6)=11, chars: GRP-18,001,002
    segs.append({
        'id': 'EP17-SEG01', 'shots': ['EP17-S01','EP17-S02'], 'dur': 11,
        'speakers': ['CHAR-GRP-18','CHAR-001','CHAR-002'], 'scene': 'SCENE-015',
        'looks': ['CHAR-001-L01','CHAR-002-L01'],
        'cr': ['CHAR-001-L01','CHAR-002-L01','SCENE-015'],
        'text': f"""【图1】苏念晚 CHAR-001-L01（白衬衫+深蓝背带裙）【图2】陆景深 CHAR-002-L01（灰色休闲风衣）【图3】片场浪漫布景 SCENE-015。
竖屏9比16连贯叙事。
镜头1（5秒）中全景 固定镜头：片场布景改为暖色调——暖黄路灯道具、长椅、人造落叶铺地，营造都市夜晚浪漫氛围。导演站在监视器后做最后调整。图1站在标记点前，低头整理衬衫袖口，深呼吸。图2从化妆间走出来，大衣换成了灰色休闲风衣，目光落在她身上。
镜头2（6秒）中近景 固定镜头：图1站在长椅旁，图2从对面缓步走来停在她面前。他高出她半个头，低头看她时，那双凤眼里带着她看不懂的情绪。图1的指尖微微蜷缩。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（苏念晚，{vp['CHAR-001']}）：「感情戏……控制好分寸。」
对白（片场导演，{vp['CHAR-GRP-18']}）：「灯光再偏左一点——好。演员就位！」
对白（苏念晚，{vp['CHAR-001']}）：「他走近了。保持住。」
对白（陆景深，{vp['CHAR-002']}）：「准备好了？」
对白（苏念晚，{vp['CHAR-001']}）：「嗯。」
画面全程无任何文字、字幕、标题、水印。
现代中国都市片场浪漫布景，暖黄灯光与人造落叶，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })
    
    # SEG02: S03(5)+S04(6)=11, chars: GRP-18,001,002
    segs.append({
        'id': 'EP17-SEG02', 'shots': ['EP17-S03','EP17-S04'], 'dur': 11,
        'speakers': ['CHAR-GRP-18','CHAR-001','CHAR-002'], 'scene': 'SCENE-015',
        'looks': ['CHAR-001-L01','CHAR-002-L01'],
        'cr': ['CHAR-001-L01','CHAR-002-L01','SCENE-015'],
        'text': f"""【图1】苏念晚 CHAR-001-L01（白衬衫+深蓝背带裙）【图2】陆景深 CHAR-002-L01（灰色休闲风衣）【图3】片场浪漫布景 SCENE-015。
竖屏9比16连贯叙事。
镜头1（5秒）中景 固定镜头：导演举起场记板。监视器屏幕上出现两人同框的构图。
镜头2（6秒）近景 缓推：图1进入角色，抬起眼时目光柔和了三分——这是"林小晚"的温柔眼神，不是苏念晚的锋芒。图2看着她，他的表演从冷面变成了克制的心动。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（片场导演，{vp['CHAR-GRP-18']}）：「第三场第一次——开始！」
对白（苏念晚，{vp['CHAR-001']}）：「你来了。我等了你很久。」
对白（陆景深，{vp['CHAR-002']}）：「等我？为什么等我？」
对白（苏念晚，{vp['CHAR-001']}）：「因为我知道你会来。」
画面全程无任何文字、字幕、标题、水印。
片场浪漫布景，暖色灯光下两人对戏，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })
    
    # SEG03: S05(5)+S06(6)=11, chars: 002,001
    segs.append({
        'id': 'EP17-SEG03', 'shots': ['EP17-S05','EP17-S06'], 'dur': 11,
        'speakers': ['CHAR-002','CHAR-001'], 'scene': 'SCENE-015',
        'looks': ['CHAR-002-L01','CHAR-001-L01'],
        'cr': ['CHAR-002-L01','CHAR-001-L01','SCENE-015'],
        'text': f"""【图1】陆景深 CHAR-002-L01（灰色休闲风衣）【图2】苏念晚 CHAR-001-L01（白衬衫+深蓝背带裙）【图3】片场浪漫布景 SCENE-015。
竖屏9比16连贯叙事。
镜头1（5秒）特写 固定镜头：图1的目光突然变了——不是角色的眼神，是他自己的。那双狭长凤眼里多了一丝认真和试探。图2敏锐地察觉到了异样——词不对。剧本里没有接下来的这句。她呼吸微滞。
镜头2（6秒）大特写 固定镜头：图1又近了一步——近到图2能看清他睫毛的弧度。他压低了声音，像只对她一个人说话。监视器后的导演皱了皱眉——这词不对——但没说停。图2的耳尖开始泛红。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（陆景深，{vp['CHAR-002']}）：「你是不是每天都在躲我？」
对白（苏念晚，{vp['CHAR-001']}）：「我……没有。」
对白（陆景深，{vp['CHAR-002']}）：「那你为什么不敢看我？」
对白（苏念晚，{vp['CHAR-001']}）：「不是剧本里的词……」
对白（苏念晚，{vp['CHAR-001']}）：「我没有躲你。」
画面全程无任何文字、字幕、标题、水印。
片场浪漫布景，即兴偏离剧本与心跳加速，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })
    
    # SEG04: S07(5)+S08(5)=10, chars: GRP-18,005,001,002
    segs.append({
        'id': 'EP17-SEG04', 'shots': ['EP17-S07','EP17-S08'], 'dur': 10,
        'speakers': ['CHAR-GRP-18','CHAR-005','CHAR-001','CHAR-002'], 'scene': 'SCENE-015',
        'looks': ['CHAR-005-L01','CHAR-001-L01','CHAR-002-L01'],
        'cr': ['CHAR-005-L01','CHAR-001-L01','CHAR-002-L01','SCENE-015'],
        'text': f"""【图1】乔乐安 CHAR-005-L01（粉色圆领卫衣，双丸子头）【图2】苏念晚 CHAR-001-L01（白衬衫+深蓝背带裙）【图3】陆景深 CHAR-002-L01（灰色休闲风衣）【图4】片场 SCENE-015。
竖屏9比16连贯叙事。
镜头1（5秒）中景 固定镜头：导演猛地从监视器后站起来，眼睛发亮，兴奋地大喊——他以为这是即兴发挥的巅峰表演。
镜头2（5秒）中全景 固定镜头：片场瞬间热闹起来。图1从工作人员身后跳出来，双手捂脸尖叫。图2退后一步拉开距离，耳根红了一片，假装低头整理衣角。图3站在原地，看着她慌乱的样子，嘴角微不可察地扬起。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（片场导演，{vp['CHAR-GRP-18']}）：「卡！过！这段太好了！」
对白（乔乐安，{vp['CHAR-005']}）：「天哪天哪天哪！姐姐你们也太甜了吧！」
对白（苏念晚，{vp['CHAR-001']}）：「乐乐别闹……」
对白（陆景深，{vp['CHAR-002']}）：「果然。」
画面全程无任何文字、字幕、标题、水印。
片场收工后热闹氛围，暖色灯光，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })
    
    # SEG05: S09(6)+S10(5)=11, chars: 001
    segs.append({
        'id': 'EP17-SEG05', 'shots': ['EP17-S09','EP17-S10'], 'dur': 11,
        'speakers': ['CHAR-001'], 'scene': 'SCENE-015',
        'looks': ['CHAR-001-L01'],
        'cr': ['CHAR-001-L01','SCENE-015'],
        'text': f"""【图1】苏念晚 CHAR-001-L01（白衬衫+深蓝背带裙）【图2】片场休息区 SCENE-015。
竖屏9比16连贯叙事。
镜头1（6秒）中景 镜头跟随：图1走到休息区角落，背对人群。她抬起手按住胸口——心跳太快了，隔着衬衫都能感觉到。她闭上眼，深吸一口气，试图让脸上的热度退下去。
镜头2（5秒）特写 固定镜头：她睁开眼，看向片场方向——图2正被工作人员围着说话，他侧脸的线条在暖色灯光下格外清晰。她立刻移开视线。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（苏念晚，{vp['CHAR-001']}）：「心跳这么快……冷静下来。」
对白（苏念晚，{vp['CHAR-001']}）：「又不是没拍过感情戏。」
对白（苏念晚，{vp['CHAR-001']}）：「可这次不一样。」
对白（苏念晚，{vp['CHAR-001']}）：「不一样。」
画面全程无任何文字、字幕、标题、水印。
片场休息区角落，暖色灯光渐暗，内心动摇与自我怀疑，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })
    
    # SEG06: S11(4)+S12(5)=9, chars: 005,001
    segs.append({
        'id': 'EP17-SEG06', 'shots': ['EP17-S11','EP17-S12'], 'dur': 9,
        'speakers': ['CHAR-005','CHAR-001'], 'scene': 'SCENE-015',
        'looks': ['CHAR-005-L01','CHAR-001-L01'],
        'cr': ['CHAR-005-L01','CHAR-001-L01','SCENE-015'],
        'text': f"""【图1】乔乐安 CHAR-005-L01（粉色圆领卫衣，双丸子头）【图2】苏念晚 CHAR-001-L01（白衬衫+深蓝背带裙）【图3】片场休息区 SCENE-015。
竖屏9比16连贯叙事。
镜头1（4秒）中近景 固定镜头：图1一路小跑过来，一把抓住图2的手臂来回晃，眼睛亮晶晶的。
镜头2（5秒）近景 固定镜头：图1凑近了压低声音，脸上带着八卦的笑容。图2的笑容僵了一瞬——然后勉力维持住。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（乔乐安，{vp['CHAR-005']}）：「姐姐姐姐！你刚才那个反应绝了！我截图了！」
对白（苏念晚，{vp['CHAR-001']}）：「截图删掉。」
对白（乔乐安，{vp['CHAR-005']}）：「你老实说——跟陆影帝搭戏，是不是心动了？」
对白（苏念晚，{vp['CHAR-001']}）：「演戏而已。」
对白（乔乐安，{vp['CHAR-005']}）：「是吗——你耳朵都红透了。」
画面全程无任何文字、字幕、标题、水印。
片场休息区，闺蜜八卦与心虚，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })
    
    # SEG07: S13(6)+S14(5)=11, chars: 001
    segs.append({
        'id': 'EP17-SEG07', 'shots': ['EP17-S13','EP17-S14'], 'dur': 11,
        'speakers': ['CHAR-001'], 'scene': 'SCENE-015',
        'looks': ['CHAR-001-L01'],
        'cr': ['CHAR-001-L01','SCENE-015'],
        'text': f"""【图1】苏念晚 CHAR-001-L01（白衬衫+深蓝背带裙）【图2】片场休息区 SCENE-015。
竖屏9比16连贯叙事。
镜头1（6秒）中景 固定镜头：收工了，片场灯光渐次熄灭。图1独自坐在休息区角落的折叠椅上，周围人声渐远。她从口袋里掏出手机，屏幕亮光照着她的脸。
镜头2（5秒）大特写 固定镜头：手机屏幕突然亮起——微信新消息通知。发送者头像：陆景深的侧影。图1的手指悬在屏幕上方，犹豫了半秒。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（苏念晚，{vp['CHAR-001']}）：「只是演戏……别想太多。」
对白（苏念晚，{vp['CHAR-001']}）：「他发消息了……现在？」
对白（苏念晚，{vp['CHAR-001']}）：「要不要点开……」
画面全程无任何文字、字幕、标题、水印。
片场收工后昏暗角落，手机屏幕光与犹豫氛围，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })
    
    # SEG08: S15(6)+S16(6)=12, chars: 001, transition: fade
    segs.append({
        'id': 'EP17-SEG08', 'shots': ['EP17-S15','EP17-S16'], 'dur': 12,
        'speakers': ['CHAR-001'], 'scene': 'SCENE-015',
        'looks': ['CHAR-001-L01'],
        'cr': ['CHAR-001-L01','SCENE-015'],
        'transition': 'fade',
        'text': f"""【图1】苏念晚 CHAR-001-L01（白衬衫+深蓝背带裙）【图2】片场休息区 SCENE-015。
竖屏9比16连贯叙事。
镜头1（6秒）大特写 镜头推近：她点开了消息。屏幕上的文字简短直接——像他这个人。图1的瞳孔微微放大，睫毛颤了一下，呼吸变得很浅。手机的光映在她眼底。
镜头2（6秒）大特写 固定镜头：她的脸庞特写——从额头到下颌线缓缓泛起的红晕清晰可见。她咬住下唇，想压下那个不自觉浮起的笑意。但失败了。她闭上眼，然后睁开，像是终于对自己承认了什么。
[以下对白仅供语音合成，严禁在画面中显示任何文字]
对白（苏念晚，{vp['CHAR-001']}）：「……」
对白（苏念晚，{vp['CHAR-001']}）：「被他说中了……」
对白（苏念晚，{vp['CHAR-001']}）：「是真的。」
画面全程无任何文字、字幕、标题、水印。
片场收工后角落，手机光映照下的情感觉醒，写实风格，竖屏9比16，无品牌 Logo，无平台 UI。"""
    })
    
    content = build_yaml('EP17', '剧本/EP17/EP17_感情戏.md',
        ['CHAR-001','CHAR-002','CHAR-005','CHAR-GRP-18'], segs)
    
    out_path = os.path.join(BASE, '剧本/EP17/EP17_segments.yaml')
    with open(out_path, 'w') as f:
        f.write(content)
    
    # Verify
    data = yaml.safe_load(content)
    total = sum(s['duration_sec'] for s in data['segments'])
    shots = sum(len(s['shot_ids']) for s in data['segments'])
    print(f"EP17: {len(data['segments'])} segments, {total}s, {shots} shots ✅")

build_ep17()
