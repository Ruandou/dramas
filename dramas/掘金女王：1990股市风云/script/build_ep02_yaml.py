#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EP02 shots.yaml + segments.yaml 构建脚本（segment-builder 规范，数据驱动保证忠实度）"""
import json, yaml, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根

# ---- CDN URL 注册表 ----
looks = json.load(open(f'{ROOT}/assets/looks/cdn_urls.json', encoding='utf-8'))
scenes = json.load(open(f'{ROOT}/assets/scenes/cdn_urls.json', encoding='utf-8'))
props = json.load(open(f'{ROOT}/assets/props/cdn_urls.json', encoding='utf-8'))

def mesh(look_id):  # look_id 如 CHAR-001-L01
    return looks[f'{look_id}-mesh']['tos_url']
def scene(sid):
    return scenes[sid]['tos_url']
def prop(pid):
    return props[pid]['tos_url']

# ---- voice_prompt（唯一来源：声音卡片，逐字复制）----
VOICE = {
    'CHAR-001': '成年女性，22岁，声线清冷锐利，语速偏快，说话简短有力，打算盘时指尖动作声清晰',
    'CHAR-002': '成年男性，35岁，语调平缓偏低沉，带有书卷气，语速适中，喜欢反问句',
    'CHAR-004': '成年女性，25岁，声线尖细带刺，语速快，阴阳怪气时语调上扬',
    'CHAR-005': '成年男性，23岁，嗓音憨厚，语速偏慢，直来直去不拐弯',
    'CHAR-GRP-03': '成年男性，40岁，嗓音沙哑带市井气，语速快，急切时语调上扬带恳求',
    'CHAR-GRP-04': '成年男性，45岁，嗓音粗粝，语速偏快，不耐烦时语调生硬带催促',
}

# ---- 角色元数据（name/gender/desc）----
CHAR = {
    'CHAR-001-L01': dict(name='林晓芸', gender='female', desc='白色确良衬衫+灰布褂+蓝灰工装裤，腰间别算盘，齐耳短发'),
    'CHAR-002-L01': dict(name='方志远', gender='male', desc='深灰西装+金丝眼镜，背头，温文尔雅'),
    'CHAR-004-L01': dict(name='苏曼', gender='female', desc='浅粉工装衬衫+大波浪卷发+胸针，红唇'),
    'CHAR-005-L01': dict(name='陈建国', gender='male', desc='蓝灰工装+工装裤，黑色平头，憨厚'),
    'CHAR-GRP-03-L01': dict(name='股民甲', gender='male', desc='灰蓝旧夹克+白汗衫，瘦削长脸，急切焦虑'),
    'CHAR-GRP-04-L01': dict(name='股民乙', gender='male', desc='棕色灯芯绒外套+灰毛衣，微胖圆脸，焦躁不耐'),
}
SCENE = {
    'SCENE-002': dict(name='证券营业部', desc='日内景，绿色油漆墙裙，手写行情黑板红绿箭头，长队股民'),
    'SCENE-005': dict(name='陈建国家', desc='夜内景，白炽灯泡冷光，简陋工人家庭，劳动模范奖状'),
}
PROP = {
    'PROP-001': dict(name='算盘', desc='深红木框黑珠木质算盘，别在腰间'),
}

def look2char(look_id):  # CHAR-001-L01 -> CHAR-001
    return look_id.rsplit('-L', 1)[0]

# ---- 镜头数据（严格忠实 EP02 剧本，对白逐字）----
# 每镜: shot_no, seg, scene_id, look_id(画面主体), 景别, 时长, visual, speakers[(look_id, dialogue)], extra_looks(画面中其他角色), props, soundscape, music, dialogue[(char_id, line)]
SHOTS = [
    # SEG01 — 初进营业部·红马甲冲击
    dict(no=1, seg=1, scene='SCENE-002', look='CHAR-001-L01', stype='全景', dur=4,
         visual='证券营业部大厅，绿色油漆墙裙，手写行情黑板上白色粉笔字密密麻麻，红绿箭头交错。大厅里挤满了股民，有人踮脚看黑板，有人围在柜台前。CHAR-001-L01 站在门口，白色确良衬衫，腰间别着 PROP-001 算盘，眼睛睁得大大的，被眼前的景象震住了，低声自语。',
         speakers=[('CHAR-001-L01', '这就是证券营业部？')],
         extra_looks=[], props=['PROP-001'],
         soundscape='股民嘈杂声、算盘声、行情黑板粉笔声', music='紧张弦乐渐起',
         dialogue=[('CHAR-001', '这就是证券营业部？')]),
    dict(no=2, seg=1, scene='SCENE-002', look='CHAR-GRP-03-L01', stype='中景', dur=4,
         visual='柜台后，一个穿红马甲的工作人员正快速写着凭证，头也不抬。柜台前围了一圈股民，七嘴八舌。CHAR-GRP-03-L01 挤在最前面，手里攥着一张皱巴巴的认购证。',
         speakers=[('CHAR-GRP-03-L01', '同志，帮我看看，凤凰化工今天多少？')],
         extra_looks=[], props=[],
         soundscape='股民嘈杂声、七嘴八舌议论声', music='紧张弦乐',
         dialogue=[('CHAR-GRP-03', '同志，帮我看看，凤凰化工今天多少？')]),
    dict(no=3, seg=1, scene='SCENE-002', look='CHAR-001-L01', stype='近景', dur=4,
         visual='CHAR-001-L01 的目光从黑板移到柜台，再移到那些红马甲身上。她下意识地摸了摸腰间的 PROP-001 算盘，指尖在算珠上轻轻一拨，发出一声脆响。周围嘈杂的人声仿佛都远了。她看着红马甲，低声自语。',
         speakers=[('CHAR-001-L01', '穿红马甲的，就是管股票的人。')],
         extra_looks=[], props=['PROP-001'],
         soundscape='算珠脆响声、远处股民嘈杂声', music='紧张弦乐渐弱',
         dialogue=[('CHAR-001', '穿红马甲的，就是管股票的人。')]),
    # SEG02 — 方志远面试·会打算盘
    dict(no=4, seg=2, scene='SCENE-002', look='CHAR-002-L01', stype='中景', dur=4,
         visual='营业部角落一张办公桌后，CHAR-002-L01 坐着，金丝眼镜，深灰西装，手里翻着一份简历。他抬起头，目光透过镜片落在 CHAR-001-L01 身上，温和中带着审视。',
         speakers=[('CHAR-002-L01', '林晓芸？纺织厂会计。王阿姨介绍来的。')],
         extra_looks=['CHAR-001-L01'], props=[],
         soundscape='股民嘈杂声、纸张翻动声', music='期待弦乐',
         dialogue=[('CHAR-002', '林晓芸？纺织厂会计。王阿姨介绍来的。')]),
    dict(no=5, seg=2, scene='SCENE-002', look='CHAR-001-L01', stype='近景', dur=4,
         visual='CHAR-001-L01 站得笔直，双手垂在身侧，指尖微微收紧。她看着 CHAR-002-L01，眼神清亮，不卑不亢。',
         speakers=[('CHAR-001-L01', '是。我在厂里管账，三年了。')],
         extra_looks=['CHAR-002-L01'], props=[],
         soundscape='股民嘈杂声', music='期待弦乐',
         dialogue=[('CHAR-001', '是。我在厂里管账，三年了。')]),
    dict(no=6, seg=2, scene='SCENE-002', look='CHAR-002-L01', stype='近景', dur=4,
         visual='CHAR-002-L01 放下简历，身体微微前倾，手指在桌面上轻轻敲了两下。他推了推眼镜，眼神变得锐利了些。',
         speakers=[('CHAR-002-L01', '会打算盘？')],
         extra_looks=[], props=[],
         soundscape='股民嘈杂声、手指敲桌声', music='期待弦乐',
         dialogue=[('CHAR-002', '会打算盘？')]),
    # SEG03 — 一心二用·当场演示
    dict(no=7, seg=3, scene='SCENE-002', look='CHAR-001-L01', stype='中景', dur=4,
         visual='CHAR-001-L01 没有回答，而是从腰间解下 PROP-001 算盘，放在桌上。她左手按在算盘上，右手拿起一支笔，抬头看着 CHAR-002-L01。',
         speakers=[('CHAR-001-L01', '方经理，您念一笔流水，我试试。')],
         extra_looks=['CHAR-002-L01'], props=['PROP-001'],
         soundscape='算盘放桌声、股民嘈杂声', music='期待弦乐',
         dialogue=[('CHAR-001', '方经理，您念一笔流水，我试试。')]),
    dict(no=8, seg=3, scene='SCENE-002', look='CHAR-002-L01', stype='近景', dur=4,
         visual='CHAR-002-L01 挑了挑眉，随手翻开一本账本，念了起来。他的语速不快，但数字密集。',
         speakers=[('CHAR-002-L01', '三月十二，买入凤凰化工，三百股，十二块八。')],
         extra_looks=[], props=[],
         soundscape='账本翻动声、股民嘈杂声', music='期待弦乐',
         dialogue=[('CHAR-002', '三月十二，买入凤凰化工，三百股，十二块八。')]),
    dict(no=9, seg=3, scene='SCENE-002', look='CHAR-001-L01', stype='特写', dur=4,
         visual='CHAR-001-L01 左手在 PROP-001 算盘上快速拨动，算珠声清脆急促，右手同时在纸上写着凭证，字迹工整。她的眼睛看着账本，头也不抬，一心二用，行云流水。',
         speakers=[('CHAR-001-L01', '记下了。三百股，十二块八，合计三千八百四十。')],
         extra_looks=[], props=['PROP-001'],
         soundscape='算珠清脆急促声、笔尖书写声', music='期待弦乐渐强',
         dialogue=[('CHAR-001', '记下了。三百股，十二块八，合计三千八百四十。')]),
    # SEG04 — 只给临时工·端茶倒水
    dict(no=10, seg=4, scene='SCENE-002', look='CHAR-002-L01', stype='近景', dur=4,
         visual='CHAR-002-L01 看着 CHAR-001-L01 写完最后一个字，点了点头，嘴角露出一丝不易察觉的笑意。他合上账本，身体靠回椅背。',
         speakers=[('CHAR-002-L01', '不错。一心二用，是块料子。')],
         extra_looks=['CHAR-001-L01'], props=[],
         soundscape='账本合上声、股民嘈杂声', music='期待弦乐',
         dialogue=[('CHAR-002', '不错。一心二用，是块料子。')]),
    dict(no=11, seg=4, scene='SCENE-002', look='CHAR-001-L01', stype='近景', dur=4,
         visual='CHAR-001-L01 眼睛一亮，刚要开口，CHAR-002-L01 却抬手打断了她。他的语气依旧平缓，但话里的意思让她愣住。',
         speakers=[('CHAR-002-L01', '不过，营业部有营业部的规矩。临时工，先站柜台，端茶倒水。你确定要来？')],
         extra_looks=['CHAR-002-L01'], props=[],
         soundscape='股民嘈杂声', music='期待弦乐转压抑',
         dialogue=[('CHAR-002', '不过，营业部有营业部的规矩。临时工，先站柜台，端茶倒水。你确定要来？')]),
    dict(no=12, seg=4, scene='SCENE-002', look='CHAR-001-L01', stype='特写', dur=4,
         visual='CHAR-001-L01 的笑容僵在脸上，指尖在 PROP-001 算盘上停住了。她看着 CHAR-002-L01，眼神从期待变成复杂，最后归于平静。她咬了咬唇，点头。',
         speakers=[('CHAR-001-L01', '我来。')],
         extra_looks=['CHAR-002-L01'], props=['PROP-001'],
         soundscape='股民嘈杂声、算珠停住声', music='压抑钢琴',
         dialogue=[('CHAR-001', '我来。')]),
    # SEG05 — 苏曼冷眼·又一个镀金的
    dict(no=13, seg=5, scene='SCENE-002', look='CHAR-004-L01', stype='中景', dur=5,
         visual='柜台内侧，CHAR-004-L01 正整理着凭证，大波浪卷发，红唇，工装衬衫领口别着胸针。她瞥了一眼站在柜台外的 CHAR-001-L01，嘴角微微上扬，翻了个白眼。',
         speakers=[('CHAR-004-L01', '哟，又来了个临时工。')],
         extra_looks=['CHAR-001-L01'], props=[],
         soundscape='凭证整理声、股民嘈杂声', music='压抑钢琴',
         dialogue=[('CHAR-004', '哟，又来了个临时工。')]),
    dict(no=14, seg=5, scene='SCENE-002', look='CHAR-004-L01', stype='近景', dur=5,
         visual='CHAR-004-L01 把一叠凭证往柜台上一放，声音不大不小，刚好让周围几个红马甲都听见。她上下打量着 CHAR-001-L01，眼神带刺。',
         speakers=[('CHAR-004-L01', '又一个来镀金的。端茶倒水都嫌手粗吧？')],
         extra_looks=['CHAR-001-L01'], props=[],
         soundscape='凭证放桌声、股民嘈杂声', music='压抑钢琴',
         dialogue=[('CHAR-004', '又一个来镀金的。端茶倒水都嫌手粗吧？')]),
    # SEG06 — 站柜台·端茶倒水
    dict(no=15, seg=6, scene='SCENE-002', look='CHAR-001-L01', stype='中景', dur=5,
         visual='CHAR-001-L01 站在柜台外侧，手里端着一个搪瓷杯，给排队的股民倒水。CHAR-GRP-04-L01 接过水，头也不抬。她的目光却越过柜台，落在行情黑板上，眼神专注。',
         speakers=[('CHAR-GRP-04-L01', '倒水的，快点儿！')],
         extra_looks=['CHAR-GRP-04-L01'], props=[],
         soundscape='倒水声、股民嘈杂声', music='压抑钢琴',
         dialogue=[('CHAR-GRP-04', '倒水的，快点儿！')]),
    dict(no=16, seg=6, scene='SCENE-002', look='CHAR-001-L01', stype='近景', dur=5,
         visual='CHAR-001-L01 把水递过去，脸上没有表情，但指尖在杯壁上微微收紧。她转头看了一眼黑板上的红绿箭头，又看了一眼柜台里 CHAR-004-L01 忙碌的背影，低声自语。',
         speakers=[('CHAR-001-L01', '端茶倒水也行。我先看清楚，这里怎么运转。')],
         extra_looks=['CHAR-004-L01'], props=[],
         soundscape='股民嘈杂声、搪瓷杯轻放声', music='压抑钢琴',
         dialogue=[('CHAR-001', '端茶倒水也行。我先看清楚，这里怎么运转。')]),
    # SEG07 — 陈建国得知·摔饭盒
    dict(no=17, seg=7, scene='SCENE-005', look='CHAR-005-L01', stype='中景', dur=4,
         visual='陈建国家，白炽灯泡光线偏冷。CHAR-005-L01 坐在方桌边，面前摆着铝饭盒。CHAR-001-L01 站在桌旁，刚说完营业部的事。CHAR-005-L01 猛地站起来，饭盒被带得翻倒在地，剩菜洒了一桌。',
         speakers=[('CHAR-005-L01', '你说什么？你要去股票那种地方？！')],
         extra_looks=['CHAR-001-L01'], props=[],
         soundscape='饭盒翻倒声、剩菜洒落声', music='冲突打击乐',
         dialogue=[('CHAR-005', '你说什么？你要去股票那种地方？！')]),
    dict(no=18, seg=7, scene='SCENE-005', look='CHAR-001-L01', stype='近景', dur=4,
         visual='CHAR-001-L01 被他的反应吓了一跳，后退半步，但很快站稳。她看着洒了一桌的饭菜，又看着 CHAR-005-L01 涨红的脸，眼神平静。',
         speakers=[('CHAR-001-L01', '建国，那是证券营业部，不是投机倒把。')],
         extra_looks=['CHAR-005-L01'], props=[],
         soundscape='白炽灯电流声', music='冲突打击乐',
         dialogue=[('CHAR-001', '建国，那是证券营业部，不是投机倒把。')]),
    dict(no=19, seg=7, scene='SCENE-005', look='CHAR-005-L01', stype='近景', dur=4,
         visual='CHAR-005-L01 指着 CHAR-001-L01 的鼻子，手指发抖，声音响彻整个小屋。他弯腰捡起饭盒，狠狠摔在桌上，铝饭盒发出刺耳的声响。',
         speakers=[('CHAR-005-L01', '不是投机倒把是什么？！晓芸，你疯了！那是赌博！你一个女人家，去那种地方，以后怎么做人！')],
         extra_looks=['CHAR-001-L01'], props=[],
         soundscape='铝饭盒摔桌刺耳声', music='冲突打击乐高潮',
         dialogue=[('CHAR-005', '不是投机倒把是什么？！晓芸，你疯了！那是赌博！你一个女人家，去那种地方，以后怎么做人！')]),
    # SEG08 — 苏曼摔凭证·集末悬念
    dict(no=20, seg=8, scene='SCENE-002', look='CHAR-004-L01', stype='中景', dur=5,
         visual='营业部快下班时，CHAR-004-L01 从柜台后绕出来，抱着一摞高高的凭证，走到 CHAR-001-L01 面前。她故意把凭证往 CHAR-001-L01 面前的桌上一摔，凭证散开，堆得比 CHAR-001-L01 还高。周围几个红马甲偷偷看过来。',
         speakers=[('CHAR-004-L01', '今天对不完账，别下班。')],
         extra_looks=['CHAR-001-L01'], props=[],
         soundscape='凭证摔桌散开声、股民嘈杂声渐弱', music='悬疑弦乐',
         dialogue=[('CHAR-004', '今天对不完账，别下班。')]),
    dict(no=21, seg=8, scene='SCENE-002', look='CHAR-001-L01', stype='全景', dur=5,
         visual='CHAR-001-L01 站在那堆凭证前，凭证堆得比她还高，几乎要把她淹没。她抬起头，看着 CHAR-004-L01 转身离去的背影，又低头看着那堆凭证，眼神从震惊慢慢变得坚定。她伸手，拿起最上面的一张凭证，指尖在 PROP-001 算盘上轻轻一拨。',
         speakers=[('CHAR-001-L01', '对不完？我偏要对完给你看。')],
         extra_looks=['CHAR-004-L01'], props=['PROP-001'],
         soundscape='算珠轻拨声、股民嘈杂声渐弱', music='悬疑弦乐渐强',
         dialogue=[('CHAR-001', '对不完？我偏要对完给你看。')]),
]

DEFAULTS = dict(
    endpoint='https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks',
    model='doubao-seedance-2-0-fast-260128',
    seed=78786,
    ratio='9:16',
    resolution='720p',
    duration=5,
    generate_audio=False,
    watermark=False,
    prompt_suffix='禁止画面中出现任何文字或字幕。90年代都市写实，暖黄怀旧色调，photorealistic。',
    negative_prompt='动画、卡通、插画、漫画、文字、字幕、logo、现代物品、手机、电脑',
)

def build_subjects(shot):
    """subjects 列表：主 look + extra_looks + scene + props"""
    subs = []
    lid = shot['look']
    c = CHAR[lid]
    subs.append(dict(id=lid, file=lid, name=c['name'], role='character', gender=c['gender'], desc=c['desc']))
    for el in shot['extra_looks']:
        ec = CHAR[el]
        subs.append(dict(id=el, file=el, name=ec['name'], role='character', gender=ec['gender'], desc=ec['desc']))
    sid = shot['scene']
    subs.append(dict(id=sid, file=sid, name=SCENE[sid]['name'], role='scene', desc=SCENE[sid]['desc']))
    for pid in shot['props']:
        subs.append(dict(id=pid, file=pid, name=PROP[pid]['name'], role='prop', desc=PROP[pid]['desc']))
    return subs

def build_look_urls(shot):
    d = {shot['look']: mesh(shot['look'])}
    for el in shot['extra_looks']:
        d[el] = mesh(el)
    return d

def build_prop_urls(shot):
    return {pid: prop(pid) for pid in shot['props']}

def build_content_roles(shot):
    """content_roles: 主look=图1, extra_looks 依次, scene, props"""
    roles = []
    n = 1
    files = [shot['look']] + shot['extra_looks'] + [shot['scene']] + shot['props']
    for f in files:
        roles.append(dict(file=f, role='reference_image', label=f'图{n}'))
        n += 1
    return roles

def build_api_shot(shot):
    spk = []
    for (lid, line) in shot['speakers']:
        char_id = look2char(lid)
        spk.append(dict(subject=lid, voice=VOICE[char_id], dialogue=line))
    return dict(
        shot_no=shot['no'], duration_sec=shot['dur'], shot_type=shot['stype'],
        camera='固定镜头', visual=shot['visual'], speakers=spk,
    )

# ---- 构建 shots.yaml ----
shots_list = []
for shot in SHOTS:
    entry = dict(
        shot_id=f"EP02-S{shot['no']:02d}",
        shot_no=shot['no'],
        mode='i2v_ref',
        duration_sec=shot['dur'],
        refs=dict(
            scene_id=shot['scene'],
            look_ids=[shot['look']] + shot['extra_looks'],
            prop_ids=shot['props'],
        ),
        assets=dict(
            look_urls=build_look_urls(shot),
            scene_urls={shot['scene']: scene(shot['scene'])},
            prop_urls=build_prop_urls(shot),
        ),
        api=dict(
            subjects=build_subjects(shot),
            shots=[build_api_shot(shot)],
            soundscape=shot['soundscape'],
            music=shot['music'],
            content_roles=build_content_roles(shot),
        ),
        dialogue=[dict(speaker=cid, line=line) for (cid, line) in shot['dialogue']],
        transition_to_next='hard_cut',
    )
    shots_list.append(entry)

shots_yaml = dict(
    episode_id='EP02',
    source_md='剧本/EP02/EP02_剧本.md',
    defaults=DEFAULTS,
    shots=shots_list,
)

# ---- 构建 segments.yaml ----
# 按 seg 分组
segs = {}
for shot in SHOTS:
    segs.setdefault(shot['seg'], []).append(shot)

# voice_prompts 汇总（本集出现的角色）
used_chars = []
for shot in SHOTS:
    for (cid, _) in shot['dialogue']:
        if cid not in used_chars:
            used_chars.append(cid)
voice_prompts = {cid: VOICE[cid] for cid in used_chars}

segments_list = []
for seg_no in sorted(segs):
    seg_shots = segs[seg_no]
    # 合并 segment 级资产（所有 shot 的并集，保持顺序）
    look_urls, prop_urls = {}, {}
    subjects = []
    seen_subj = set()
    speakers = []
    scene_id = seg_shots[0]['scene']
    for shot in seg_shots:
        for k, v in build_look_urls(shot).items():
            look_urls.setdefault(k, v)
        for k, v in build_prop_urls(shot).items():
            prop_urls.setdefault(k, v)
        for sub in build_subjects(shot):
            if sub['id'] not in seen_subj:
                subjects.append(sub)
                seen_subj.add(sub['id'])
        for (cid, _) in shot['dialogue']:
            if cid not in speakers:
                speakers.append(cid)
    # content_roles: 主 looks + scene + props（按首次出现顺序）
    content_roles = []
    n = 1
    for f in list(look_urls.keys()) + [scene_id] + list(prop_urls.keys()):
        content_roles.append(dict(file=f, role='reference_image', label=f'图{n}'))
        n += 1
    api_shots = [build_api_shot(s) for s in seg_shots]
    # soundscape/music 取 seg 内各 shot 合并（用首 shot 的，或拼接）
    soundscape = seg_shots[0]['soundscape']
    music = seg_shots[0]['music']
    duration = sum(s['dur'] for s in seg_shots)
    segments_list.append(dict(
        segment_id=f'EP02-SEG{seg_no:02d}',
        shot_ids=[f"EP02-S{s['no']:02d}" for s in seg_shots],
        duration_sec=duration,
        speakers=speakers,
        refs=dict(scene_id=scene_id),
        assets=dict(
            look_urls=look_urls,
            scene_urls={scene_id: scene(scene_id)},
            prop_urls=prop_urls,
        ),
        api=dict(
            subjects=subjects,
            shots=api_shots,
            soundscape=soundscape,
            music=music,
            content_roles=content_roles,
        ),
        transition_to_next='hard_cut',
    ))

segments_yaml = dict(
    episode_id='EP02',
    source_md='剧本/EP02/EP02_剧本.md',
    defaults=DEFAULTS,
    voice_prompts=voice_prompts,
    segments=segments_list,
)

# ---- 写出（保留中文，不转义）----
class Dumper(yaml.SafeDumper):
    pass
Dumper.add_representer(str, lambda d, s: d.represent_scalar('tag:yaml.org,2002:str', s))

def write(obj, path):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(obj, f, Dumper=Dumper, allow_unicode=True, sort_keys=False, width=1000)
    print('written:', path)

write(shots_yaml, f'{ROOT}/剧本/EP02/EP02_shots.yaml')
write(segments_yaml, f'{ROOT}/剧本/EP02/EP02_segments.yaml')
print(f"shots={len(shots_list)} segments={len(segments_list)} total_dur={sum(s['dur'] for s in SHOTS)}s")
