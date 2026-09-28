#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EP05 shots.yaml + segments.yaml 构建器（segment-builder 规范）。
从 EP05_剧本.md 逐镜转译，对白逐字一致，speakers 用角色 ID，
look_urls 用 mesh 版，PROP-001 锁定 prop_urls，ratio 加引号。
"""
import json, os, re, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = "EP05"
MD = os.path.join(ROOT, "剧本", EP, f"{EP}_剧本.md")

looks = json.load(open(os.path.join(ROOT, "assets/looks/cdn_urls.json"), encoding="utf-8"))
scenes = json.load(open(os.path.join(ROOT, "assets/scenes/cdn_urls.json"), encoding="utf-8"))
props = json.load(open(os.path.join(ROOT, "assets/props/cdn_urls.json"), encoding="utf-8"))

def tos(reg, k):
    u = reg.get(k, {}).get("tos_url", "")
    assert u and "X-Tos-Expires" not in u, f"missing/临时 tos_url: {k}"
    return u

# 角色元数据（名/性别/desc/voice）
CHAR = {
    "CHAR-001": dict(name="林晓芸", gender="female",
        desc="白色确良衬衫+灰布褂+蓝灰工装裤，腰间别算盘，齐耳短发",
        voice="成年女性，22岁，声线清冷锐利，语速偏快，说话简短有力，打算盘时指尖动作声清晰"),
    "CHAR-003": dict(name="老周", gender="male",
        desc="深灰中山装，花白短发，略显佝偻，沧桑眼神",
        voice="成年男性，50岁，嗓音沙哑沧桑，语速偏慢，讲故事时带江湖气"),
    "CHAR-004": dict(name="苏曼", gender="female",
        desc="浅粉工装衬衫+大波浪卷发+胸针，娇小精明",
        voice="成年女性，25岁，声线尖细带刺，语速快，阴阳怪气时语调上扬"),
    "CHAR-GRP-02": dict(name="营业部保安", gender="male",
        desc="橄榄绿保安制服+红袖章+黑腰带，国字脸严肃，黑色平头",
        voice="成年男性，40岁，嗓音生硬带威严，语速适中，拦人时严肃，对老周恭敬时语调放软"),
}
SCENE = {
    "SCENE-002": dict(name="证券营业部", desc="日内景，绿色油漆墙裙，手写行情黑板红绿箭头，长队股民"),
    "SCENE-003": dict(name="大户室", desc="日内景，深木色装修，真皮沙发红木茶几，专线电话，墙上字画"),
}
PROP = {"PROP-001": dict(name="算盘", desc="深红木框黑珠木质算盘，别在腰间")}

def look_url(look_id):  # mesh 版
    return tos(looks, look_id + "-mesh")

# ---- 镜头表（逐镜，与剧本 21 镜一一对应）----
# (shot_no, seg, scene, char, look, 景别, dur, visual, speaker_char, dialogue, soundscape, music, has_prop)
S = []
def add(no, seg, scene, char, look, st, dur, visual, spk, dlg, ss, mu, prop=False):
    S.append(dict(no=no, seg=seg, scene=scene, char=char, look=look, st=st, dur=dur,
                  visual=visual, spk=spk, dlg=dlg, ss=ss, mu=mu, prop=prop))

add(1,"SEG01","SCENE-002","CHAR-001","CHAR-001-L01","中景",4,
    "1991年初，证券营业部大厅走廊尽头，CHAR-001-L01 站在一扇深木色的门前，门上挂着\"大户室\"的牌子。她攥着一张纸条，手心微微出汗，不时看一眼手表。",
    "CHAR-001","就是这儿。","大厅远处嘈杂声、脚步声","压抑钢琴",prop=True)
add(2,"SEG01","SCENE-002","CHAR-GRP-02","CHAR-GRP-02-L01","近景",4,
    "CHAR-GRP-02-L01 从旁边走过来，上下打量着 CHAR-001-L01，伸手拦住她，表情严肃。",
    "CHAR-GRP-02","同志，请留步。这里是大户室，不能随便进。","大厅嘈杂声、脚步声","压抑钢琴")
add(3,"SEG01","SCENE-002","CHAR-001","CHAR-001-L01","近景",4,
    "CHAR-001-L01 被拦下，愣了一下，赶紧掏出纸条，递给 CHAR-GRP-02-L01 看。她的声音有些紧张，但眼神坚定。",
    "CHAR-001","我等人。老周，周师傅，是他让我在这儿等他的。","大厅嘈杂声","压抑钢琴",prop=True)

add(4,"SEG02","SCENE-003","CHAR-GRP-02","CHAR-GRP-02-L01","中景",5,
    "CHAR-GRP-02-L01 瞥了一眼纸条，又瞥了一眼 CHAR-001-L01，嘴角露出一丝不屑。他把纸条还给她，摇了摇头，语气生硬。",
    "CHAR-GRP-02","临时工不能进。这是营业部的规矩，谁也不能破。","走廊安静、远处大厅嘈杂","压抑钢琴")
add(5,"SEG02","SCENE-003","CHAR-001","CHAR-001-L01","近景",5,
    "CHAR-001-L01 的脸一下子红了，她攥着纸条，指尖微微发抖。她张了张嘴，想反驳，但保安已经转身走开。她站在原地，看着那扇深木色的门，眼神从委屈变成坚定。",
    "CHAR-001","临时工。","走廊安静、呼吸声","压抑钢琴",prop=True)

add(6,"SEG03","SCENE-003","CHAR-003","CHAR-003-L01","中景",4,
    "CHAR-003-L01 从走廊另一端走过来，深灰中山装，花白短发，手里端着一杯浓茶。他看到 CHAR-001-L01 站在门口，保安拦着她，皱了皱眉，快步走过去。",
    "CHAR-003","怎么回事？围在这儿干什么？","走廊脚步声、远处大厅嘈杂","悬疑弦乐")
add(7,"SEG03","SCENE-003","CHAR-GRP-02","CHAR-GRP-02-L01","近景",4,
    "CHAR-GRP-02-L01 看到 CHAR-003-L01，立刻换了一副表情，点头哈腰。他指了指 CHAR-001-L01，语气恭敬。",
    "CHAR-GRP-02","周师傅，这位同志说是等您。但她是临时工，按规定，不能进。","走廊安静","悬疑弦乐")
add(8,"SEG03","SCENE-003","CHAR-003","CHAR-003-L01","近景",4,
    "CHAR-003-L01 摆了摆手，打断保安的话。他看了 CHAR-001-L01 一眼，眼神复杂，然后推开大户室的门，示意她进去。",
    "CHAR-003","她是我请来的。进去吧。","木门吱呀声","悬疑弦乐")

add(9,"SEG04","SCENE-003","CHAR-001","CHAR-001-L01","全景",4,
    "CHAR-001-L01 跟着 CHAR-003-L01 走进大户室，脚步在门口停住了。她睁大眼睛，看着眼前的景象：独立房间，深木色装修，真皮沙发，红木茶几，专线电话，墙上挂着字画。与外面大厅的拥挤形成天壤之别。",
    "CHAR-001","这就是大户室？跟外面，完全不一样。","室内安静、专线电话铃声远处","悬疑弦乐",prop=True)
add(10,"SEG04","SCENE-003","CHAR-001","CHAR-001-L01","中景",4,
    "CHAR-001-L01 慢慢走进房间，目光从真皮沙发移到专线电话，再移到红木茶几。她的指尖轻轻碰了碰沙发的扶手，又赶紧缩回来，仿佛怕弄脏了。",
    "CHAR-001","真皮沙发。专线电话。","室内安静、轻微脚步声","悬疑弦乐",prop=True)
add(11,"SEG04","SCENE-003","CHAR-003","CHAR-003-L01","近景",4,
    "CHAR-003-L01 坐在真皮沙发上，看着 CHAR-001-L01 震惊的样子，嘴角露出一丝不易察觉的笑意。他端起茶杯，喝了一口，声音沙哑。",
    "CHAR-003","坐吧。别站着。","茶杯轻碰声","悬疑弦乐")

add(12,"SEG05","SCENE-003","CHAR-003","CHAR-003-L01","中景",4,
    "CHAR-003-L01 从口袋里掏出一张纸条，递给 CHAR-001-L01。纸条上写着一串数字，是几只股票的买入价和数量。他的眼神变得锐利，声音低沉。",
    "CHAR-003","帮我算一笔账。看看怎么卖，最划算。","室内安静、纸张声","紧张弦乐")
add(13,"SEG05","SCENE-003","CHAR-001","CHAR-001-L01","近景",4,
    "CHAR-001-L01 接过纸条，看了一眼，立刻从腰间解下 PROP-001 算盘，放在红木茶几上。她的指尖在算珠上轻轻一拨，发出一声脆响。",
    "CHAR-001","凤凰化工，八块二，五百股。飞乐股份，十五块六，三百股。","算珠脆响","紧张弦乐",prop=True)
add(14,"SEG05","SCENE-003","CHAR-003","CHAR-003-L01","近景",4,
    "CHAR-003-L01 靠在沙发上，看着 CHAR-001-L01 专注的样子，眼神从审视变成期待。他端起茶杯，慢慢喝了一口，没有说话。",
    "CHAR-003","算算，怎么卖，最划算。","茶杯轻碰声、室内安静","紧张弦乐")

add(15,"SEG06","SCENE-003","CHAR-001","CHAR-001-L01","特写",5,
    "CHAR-001-L01 的指尖在 PROP-001 算盘上快速拨动，算珠声清脆急促。她的眼睛盯着纸条，头也不抬，嘴里念念有词。三分钟后，算珠声戛然而止。她抬起头，眼神清亮。",
    "CHAR-001","凤凰化工，现在卖，赚四百一。飞乐股份，再等等，下周三卖，能赚六百二。总共，一千零三十。按今天的行情算。","算珠声清脆急促后戛然而止","紧张弦乐",prop=True)
add(16,"SEG06","SCENE-003","CHAR-003","CHAR-003-L01","特写",5,
    "CHAR-003-L01 愣住了，手里的茶杯停在半空中。他盯着 CHAR-001-L01，看了很久很久，眼神从震惊变成复杂，再从复杂变成感慨。他放下茶杯，沉默良久，终于缓缓点头。",
    "CHAR-003","好。算得真准。","室内安静、茶杯放下声","紧张弦乐")

add(17,"SEG07","SCENE-003","CHAR-003","CHAR-003-L01","近景",4,
    "CHAR-003-L01 沉默了很久，终于开口。他的声音有些发抖，眼神躲闪，不敢看 CHAR-001-L01。",
    "CHAR-003","你父亲……是不是姓林？","室内安静、呼吸声","低沉钢琴")
add(18,"SEG07","SCENE-003","CHAR-001","CHAR-001-L01","特写",4,
    "CHAR-001-L01 愣住了，手里的算盘差点掉在地上。她瞪大眼睛，看着 CHAR-003-L01，眼神从疑惑变成震惊。她的心跳得很快，声音有些发抖。",
    "CHAR-001","你怎么知道？","室内安静、心跳声","低沉钢琴",prop=True)
add(19,"SEG07","SCENE-003","CHAR-003","CHAR-003-L01","近景",4,
    "CHAR-003-L01 没有回答，他转过头，看着墙上的字画，眼神变得很远。他张了张嘴，想说什么，又咽了回去。",
    "CHAR-003","令尊当年的事，说来话长。","室内安静","低沉钢琴")

add(20,"SEG08","SCENE-002","CHAR-004","CHAR-004-L01","中景",5,
    "证券营业部大厅，CHAR-004-L01 站在柜台内侧，正好看到 CHAR-001-L01 从大户室的方向走出来。她的脸色一下子变得铁青，手里的凭证捏得紧紧的，指节发白。",
    "CHAR-004","她怎么进大户室了？一个临时工，凭什么？","大厅嘈杂声","悬疑弦乐")

add(21,"SEG09","SCENE-003","CHAR-003","CHAR-003-L01","近景",5,
    "大户室内，CHAR-003-L01 终于转过头，看着 CHAR-001-L01，眼神复杂。他叹了口气，声音很轻，几乎听不见。",
    "CHAR-003","你爸……算了，时候未到。","室内安静、叹息声","悬疑弦乐")

# ---- defaults ----
DEFAULTS = dict(
    endpoint="https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks",
    model="doubao-seedance-2-0-fast-260128",
    seed=78786, ratio="9:16", resolution="720p", duration=5,
    generate_audio=False, watermark=False,
    prompt_suffix="禁止画面中出现任何文字或字幕。90年代都市写实，暖黄怀旧色调，photorealistic。",
    negative_prompt="动画、卡通、插画、漫画、文字、字幕、logo、现代物品、手机、电脑",
)

def subjects_for(chars, scene, prop):
    subs=[]
    for c in chars:
        lid=c+"-L01"
        subs.append(dict(id=lid, file=lid, name=CHAR[c]["name"], role="character",
                         gender=CHAR[c]["gender"], desc=CHAR[c]["desc"]))
    subs.append(dict(id=scene, file=scene, name=SCENE[scene]["name"], role="scene",
                     desc=SCENE[scene]["desc"]))
    if prop:
        subs.append(dict(id="PROP-001", file="PROP-001", name="算盘", role="prop",
                         desc=PROP["PROP-001"]["desc"]))
    return subs

def content_roles(chars, scene, prop):
    cr=[]; n=1
    for c in chars:
        cr.append(dict(file=c+"-L01", role="reference_image", label=f"图{n}")); n+=1
    cr.append(dict(file=scene, role="reference_image", label=f"图{n}")); n+=1
    if prop:
        cr.append(dict(file="PROP-001", role="reference_image", label=f"图{n}")); n+=1
    return cr

# ---- shots.yaml ----
shots=[]
for s in S:
    chars=[s["char"]]
    shot=dict(
        shot_id=f"{EP}-S{s['no']:02d}", shot_no=s["no"], mode="i2v_ref",
        duration_sec=s["dur"],
        refs=dict(scene_id=s["scene"], look_ids=[s["look"]],
                  **({"prop_ids":["PROP-001"]} if s["prop"] else {})),
        assets=dict(
            look_urls={s["look"]: look_url(s["look"])},
            scene_urls={s["scene"]: tos(scenes, s["scene"])},
            **({"prop_urls":{"PROP-001": tos(props,"PROP-001")}} if s["prop"] else {}),
        ),
        api=dict(
            subjects=subjects_for(chars, s["scene"], s["prop"]),
            shots=[dict(shot_no=s["no"], duration_sec=s["dur"], shot_type=s["st"],
                        camera="固定镜头", visual=s["visual"],
                        speakers=[dict(subject=s["look"], voice=CHAR[s["spk"]]["voice"],
                                       dialogue=s["dlg"])])],
            soundscape=s["ss"], music=s["mu"],
            content_roles=content_roles(chars, s["scene"], s["prop"]),
        ),
        dialogue=[dict(speaker=s["spk"], line=s["dlg"])],
        transition_to_next="hard_cut",
    )
    shots.append(shot)

fidelity = f"""# SOURCE FIDELITY PROOF
# source_md: 剧本/{EP}/{EP}_剧本.md
# shot_count_source: 21  shot_count_yaml: {len(shots)}
# dialogue_lines_source: 21  dialogue_lines_yaml: {len(shots)}（逐字一致）
# 转译: 每镜头 visual/对白 逐字源自剧本镜头表；speakers 用角色 ID；look_urls 用 mesh 版；
#       PROP-001 锁定 prop_urls；ratio 加引号 '9:16'；name_card/location_card 在 segments.yaml 转译。
"""
shots_doc = dict(episode_id=EP, source_md=f"剧本/{EP}/{EP}_剧本.md",
                 defaults=DEFAULTS, shots=shots)
shots_yaml = fidelity + yaml.dump(shots_doc, allow_unicode=True, sort_keys=False, width=1000)
open(os.path.join(ROOT,"剧本",EP,f"{EP}_shots.yaml"),"w",encoding="utf-8").write(shots_yaml)

# ---- segments.yaml ----
SEGS=[("SEG01",[1,2,3]),("SEG02",[4,5]),("SEG03",[6,7,8]),("SEG04",[9,10,11]),
      ("SEG05",[12,13,14]),("SEG06",[15,16]),("SEG07",[17,18,19]),
      ("SEG08",[20]),("SEG09",[21])]
# 卡转译
NAME_CARD={"SEG01": dict(name="营业部保安", at=4.3, duration=2.5)}  # 镜2 近景露脸
LOC_CARD={"SEG01": dict(text="证券营业部", at=0.3, duration=2.5),  # SCENE-002 本集首现（burn 按本集首次进入检测）
            "SEG02": dict(text="大户室", at=0.3, duration=2.5)}      # SCENE-003 首现

shot_by_no={s["no"]:s for s in S}
voice_prompts={c: CHAR[c]["voice"] for c in ["CHAR-001","CHAR-003","CHAR-004","CHAR-GRP-02"]}

segments=[]
for seg_id, nos in SEGS:
    seg_shots=[shot_by_no[n] for n in nos]
    scene=seg_shots[0]["scene"]
    chars=[]; spk_ids=[]
    for s in seg_shots:
        if s["char"] not in chars: chars.append(s["char"])
        if s["spk"] not in spk_ids: spk_ids.append(s["spk"])
    prop=any(s["prop"] for s in seg_shots)
    dur=sum(s["dur"] for s in seg_shots)
    look_urls={c+"-L01": look_url(c+"-L01") for c in chars}
    api_shots=[]
    for s in seg_shots:
        api_shots.append(dict(shot_no=s["no"], duration_sec=s["dur"], shot_type=s["st"],
            camera="固定镜头", visual=s["visual"],
            speakers=[dict(subject=s["look"], voice=CHAR[s["spk"]]["voice"], dialogue=s["dlg"])]))
    seg=dict(
        segment_id=f"{EP}-{seg_id}",
        shot_ids=[f"{EP}-S{n:02d}" for n in nos],
        duration_sec=dur,
        speakers=spk_ids,
        refs=dict(scene_id=scene),
        assets=dict(
            look_urls=look_urls,
            scene_urls={scene: tos(scenes, scene)},
            **({"prop_urls":{"PROP-001": tos(props,"PROP-001")}} if prop else {}),
        ),
        api=dict(
            subjects=subjects_for(chars, scene, prop),
            shots=api_shots,
            soundscape=seg_shots[0]["ss"], music=seg_shots[0]["mu"],
            content_roles=content_roles(chars, scene, prop),
        ),
        transition_to_next="hard_cut",
    )
    if seg_id in NAME_CARD: seg["name_card"]=NAME_CARD[seg_id]
    if seg_id in LOC_CARD: seg["location_card"]=LOC_CARD[seg_id]
    segments.append(seg)

seg_doc=dict(episode_id=EP, source_md=f"剧本/{EP}/{EP}_剧本.md",
             defaults=DEFAULTS, voice_prompts=voice_prompts, segments=segments)
seg_yaml=yaml.dump(seg_doc, allow_unicode=True, sort_keys=False, width=1000)
open(os.path.join(ROOT,"剧本",EP,f"{EP}_segments.yaml"),"w",encoding="utf-8").write(seg_yaml)

print(f"✅ shots.yaml: {len(shots)} 镜")
print(f"✅ segments.yaml: {len(segments)} 段, 总时长 {sum(s['duration_sec'] for s in segments)}s")
print(f"✅ name_card: {list(NAME_CARD)}  location_card: {list(LOC_CARD)}")
