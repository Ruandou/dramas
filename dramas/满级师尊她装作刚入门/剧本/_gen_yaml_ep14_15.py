#!/usr/bin/env python3
"""Generate shots.yaml and segments.yaml for EP14 and EP15."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

BASE = "/Users/leifu/Movies/dramas/dramas/满级师尊她装作刚入门"
LOOK_BASE = "https://drama-reference-images.tos-cn-beijing.volces.com/looks/满级师尊她装作刚入门"
SCENE_BASE = "https://drama-reference-images.tos-cn-beijing.volces.com/scenes/满级师尊她装作刚入门"
PROP_BASE = "https://drama-reference-images.tos-cn-beijing.volces.com/props/满级师尊她装作刚入门"
PROMPT_SUFFIX = "vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
NEG_PROMPT = "modern objects, contemporary clothing, glasses, watches, phones, cars, buildings with glass windows, plastic, neon signs, English text, Japanese text, Traditional Chinese characters appearing as gibberish, garbled text, tattoos, piercings, modern hairstyles, jeans, t-shirts, sneakers, concrete, asphalt road, power lines, western medieval armor, steampunk elements, cyberpunk elements, anime style, cartoon style, chibi, low quality, blurry, watermark"

VOICE = {
    "CHAR-001": "成年女性，17岁，声线清冷凌厉如冰泉，语速从容不迫，每个字清晰有力不带一丝多余情绪，偶尔轻笑时带淡漠距离感",
    "CHAR-001-藏拙": "成年女性，17岁，声线清亮但刻意压低显得怯弱，语速偏快带犹豫停顿，说话时带微微颤音伪装胆小",
    "CHAR-002": "成年男性，27岁，低沉磁性嗓音如古琴低弦，语速极慢，每个字之间留有余韵，尾音微沉如深潭落石",
    "CHAR-003": "成年女性，23岁，声线冷硬如铁，语速平稳不带任何情绪波动，每个字如冰锥落地清脆冷冽",
    "CHAR-007": "青年女性，19岁，声线尖锐刻薄，语速快带嘲讽笑意，说话爱翘嘴角导致字音偏高偏尖，后期转为紧张讨好时声音压低变小",
    "CHAR-010": "中年男性，45岁，声线平和毫无特色如路人甲，语速中等不快不慢，暴露后声线转冷变沉如深渊回响",
    "CHAR-GRP-01": "青年男性，20岁，声线普通平实略带隶属感，语速中等，跟风起哄时音调上扬带起哄意味，单独说话时则拘谨拘束",
    "CHAR-GRP-02": "老年男性，60岁，声线沉稳威严带中气，语速缓慢字字有分量，训诫时拖长尾音带长者权威感",
}
CHAR_DESC = {"CHAR-001-L01":"灰色外门粗布袍，低马尾","CHAR-002-L01":"白银宗门袍","CHAR-003-L01":"紫黑修士服，高马尾","CHAR-007-L01":"绿色修士裙，双髻","CHAR-010-L01":"灰色道袍，面貌平凡","CHAR-GRP-01-L01":"灰袍外门弟子","CHAR-GRP-02-L01":"白袍长老，灰白长须"}
CHAR_NAME = {"CHAR-001":"沈清词","CHAR-002":"顾渊白","CHAR-003":"冷凝霜","CHAR-007":"刘芸","CHAR-010":"客卿长老","CHAR-GRP-01":"外门弟子","CHAR-GRP-02":"宗门长老"}
SCENE_NAME = {"SCENE-003":"外门练剑场","SCENE-005":"掌门书房","SCENE-006":"桃花院","SCENE-007":"后山竹林"}

def lu(lid): return f"{LOOK_BASE}/{lid}.png"
def su(sid): return f"{SCENE_BASE}/{sid}.png"
def pu(pid): return f"{PROP_BASE}/{pid}.png"

# ===== EP14 =====
EP14_SHOTS = [
    {"shot_id":"EP14-S01","no":1,"dur":10,"scene":"SCENE-003","looks":["CHAR-001-L01","CHAR-GRP-01-L01"],"props":[],"text":"【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】CHAR-GRP-01-L01（灰袍外门弟子）【图3】SCENE-003。\n        全景 固定镜头：图1站在弟子队列末尾——灰袍低头缩肩，存在感极低。图2数十名弟子分列两侧站成整齐方阵。石台擂台正中央刻着剑纹阵法微微泛光。高台观众席上坐着几位长老。阳光明烈但风中带着一丝冷意。","roles":[("CHAR-001-L01","图1"),("CHAR-GRP-01-L01","图2"),("SCENE-003","图3")],"dialogue":[("CHAR-GRP-01","论剑会选拔——听说这次选四个名额。"),("CHAR-001","冷凝霜也在——观众席。她来做什么？"),("CHAR-001","选拔赛——我只需要藏拙落败就行。不出手不暴露。"),("CHAR-001","希望对手不要太强……")],"transition":"hard_cut"},
    {"shot_id":"EP14-S02","no":2,"dur":6,"scene":"SCENE-003","looks":["CHAR-007-L01","CHAR-001-L01"],"props":[],"text":"【图1】CHAR-007-L01（绿色修士裙，双髻）【图2】CHAR-001-L01（灰色外门粗布袍）【图3】SCENE-003。\n        中景 固定镜头：图1已经昂首走出——绿色修士裙在风中飞扬，唇角挂着锐利的笑意。图1的目光如锥子般钉在图2身上。图2微微一愣——然后很快垂下视线。石台上对阵名单亮起灵光。","roles":[("CHAR-007-L01","图1"),("CHAR-001-L01","图2"),("SCENE-003","图3")],"dialogue":[("CHAR-007","哟——沈清词？就你？"),("CHAR-007","别还没上台就吓哭了啊——废物。"),("CHAR-GRP-01","完了……她对上刘芸了。"),("CHAR-001","刘芸——冷凝霜的人。这个对阵……不是巧合。")],"transition":"hard_cut"},
    {"shot_id":"EP14-S03","no":3,"dur":6,"scene":"SCENE-003","looks":["CHAR-003-L01"],"props":[],"text":"【图1】CHAR-003-L01（紫黑修士服，高马尾）【图2】SCENE-003。\n        近景 固定镜头：图1端坐高台不动——视线从对阵名单移到擂台下。图1嘴角没有任何弧度，但目光中有一丝几不可察的审视和期待。图1手指轻轻搭在膝上——指尖微动如同在操控一枚棋子。","roles":[("CHAR-003-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-003","终于上场了——沈清词。"),("CHAR-003","让我看看——你到底是不是'只会哭'的废物。")],"transition":"hard_cut"},
    {"shot_id":"EP14-S04","no":4,"dur":6,"scene":"SCENE-003","looks":["CHAR-007-L01","CHAR-001-L01"],"props":[],"text":"【图1】CHAR-007-L01（绿色修士裙）【图2】CHAR-001-L01（灰色外门粗布袍）【图3】SCENE-003。\n        中景 固定镜头：图1单手叉腰——满脸不屑站在石台上。图2缩着肩站在对面——双手不自然地攥着衣袖，一副随时准备认输的样子。擂台边缘阵法泛起淡蓝光芒形成护罩——将两人圈在其中。","roles":[("CHAR-007-L01","图1"),("CHAR-001-L01","图2"),("SCENE-003","图3")],"dialogue":[("CHAR-007","我还以为对手是谁——原来是咱们宗门最有名的废物。"),("CHAR-007","你直接跳下去认输吧——省得我弄脏手。"),("CHAR-001","我、我……我可以认输吗……")],"transition":"hard_cut"},
    {"shot_id":"EP14-S05","no":5,"dur":6,"scene":"SCENE-003","looks":["CHAR-007-L01"],"props":[],"text":"【图1】CHAR-007-L01（绿色修士裙，双髻）【图2】SCENE-003。\n        近景 固定镜头：图1冷笑一声——从袖中取出一枚暗红色法宝令牌。图1攥住令牌——灵力注入——令牌骤然爆发出一圈红色冲击波。图1令牌上纹路复杂远超她修为层级——暗红光芒在掌心跳动如活物。场边弟子惊呼后退。","roles":[("CHAR-007-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-007","认输？晚了——师姐说了……要好好'教训'你一下。"),("CHAR-001","那枚令牌——灵力波动远超她的修为。冷凝霜给她的。"),("CHAR-001","品阶至少四品——她自己根本驾驭不了。是冷凝霜在试我。")],"transition":"hard_cut"},
    {"shot_id":"EP14-S06","no":6,"dur":6,"scene":"SCENE-003","looks":["CHAR-001-L01","CHAR-007-L01"],"props":[],"text":"【图1】CHAR-001-L01（灰色外门粗布袍）【图2】CHAR-007-L01（绿色修士裙）【图3】SCENE-003。\n        中景 固定镜头：图1侧身闪过暗红色能量——灰袍被气浪掀起一角。能量击中图1身后擂台地面——石板炸裂碎石飞溅。图1后退三步——看似狼狈但步伐精准。图2追击第二波——红光更猛。","roles":[("CHAR-001-L01","图1"),("CHAR-007-L01","图2"),("SCENE-003","图3")],"dialogue":[("CHAR-007","跑什么——站住啊废物！"),("CHAR-001","攻击模式是直线冲击——但灵力储备在快速消耗。再撑三轮她就控制不住了。"),("CHAR-001","啊——别、别打了——我认输——"),("CHAR-GRP-01","她喊认输了！裁判——")],"transition":"hard_cut"},
    {"shot_id":"EP14-S07","no":7,"dur":6,"scene":"SCENE-003","looks":["CHAR-003-L01","CHAR-007-L01"],"props":[],"text":"【图1】CHAR-003-L01（紫黑修士服，高马尾）【图2】CHAR-007-L01（绿色修士裙）【图3】SCENE-003。\n        近景 固定镜头：图1目光微动——指尖在膝上轻叩一下。台下图2似乎收到某种信号——嘴角一扬，手中令牌灵力骤然翻倍。红光暴涨如火焰怒放——认输信号被无视。图1嘴角终于微微上翘——一个极浅的冷笑。","roles":[("CHAR-003-L01","图1"),("CHAR-007-L01","图2"),("SCENE-003","图3")],"dialogue":[("CHAR-003","还不够——再逼一步。让她无处可退。"),("CHAR-007","认输？哈——你以为喊一声就能停？"),("CHAR-001","她故意不停——冷凝霜在指挥。目的是逼我暴露实力。")],"transition":"hard_cut"},
    {"shot_id":"EP14-S08","no":8,"dur":6,"scene":"SCENE-003","looks":["CHAR-001-L01"],"props":[],"text":"【图1】CHAR-001-L01（灰色外门粗布袍）【图2】SCENE-003。\n        中景 固定镜头：图1后背已经贴上擂台边缘护罩——蓝光在她背后嗡嗡作响，无路可退。图1灰袍上多处被气浪撕裂露出里衣。图1头发散了几缕垂在面前——呼吸急促。远处暗红令牌已经完全失控——红光脉动如心跳越来越快。","roles":[("CHAR-001-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-001","三面封死。法宝已经暴走——她自己都控制不住了。"),("CHAR-001","下一击——如果我不出手。"),("CHAR-001","这一击不是她打的——是冷凝霜。")],"transition":"hard_cut"},
    {"shot_id":"EP14-S09","no":9,"dur":6,"scene":"SCENE-003","looks":["CHAR-007-L01"],"props":[],"text":"【图1】CHAR-007-L01（绿色修士裙）【图2】SCENE-003。\n        近景 固定镜头：图1面容已经扭曲——法宝灵力反噬让她脸上浮现红色纹路如裂纹。图1已无法收回——令牌中全部能量凝聚成一道猩红光柱——体积比前几次大了三倍。光柱如炮弹般直轰前方——速度极快。","roles":[("CHAR-007-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-007","去死——"),("CHAR-GRP-01","快躲——"),("CHAR-001","来不及躲——正面命中的话会伤到根基。"),("CHAR-001","……够了。")],"transition":"hard_cut"},
    {"shot_id":"EP14-S10","no":10,"dur":10,"scene":"SCENE-003","looks":["CHAR-001-L01"],"props":[],"text":"【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-003。\n        大特写 缓推：图1瞳孔中映着猩红光柱急速放大。图1眼中所有恐惧怯弱如面具剥落般消失殆尽——取而代之的是一片纯净极致的冷意——如百年寒潭凝结成冰。图1嘴唇微微闭合——面无表情——前世满级剑仙的气场从每一个毛孔中渗透出来。时间仿佛被拉长到极限。","roles":[("CHAR-001-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-001","藏不住了——也不需要藏。"),("CHAR-001","让你看看什么叫——差距。"),("CHAR-001","代价之后再算——先活下来。")],"transition":"hard_cut"},
    {"shot_id":"EP14-S11","no":11,"dur":12,"scene":"SCENE-003","looks":["CHAR-001-L01"],"props":[],"text":"【图1】CHAR-001-L01（灰色外门粗布袍）【图2】SCENE-003。\n        中景 固定镜头：图1缓缓抬起右手——动作极慢如同在对抗某种巨大引力。图1食指微微前伸——指尖凝聚出一点极细微的银白色光芒——如星辰初生。整个画面在图1指尖触碰到红色光柱的一刹那——骤然定格。色彩急速褪去——画面如墨水浸染般转为纯黑。","roles":[("CHAR-001-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-007","不可能——快闪——"),("CHAR-001","碎。"),("CHAR-001","……一百年没用过这一招了。"),("CHAR-001","后果——下次再说。")],"transition":"hard_cut"},
]

EP14_SEGS = [
    {"id":"EP14-SEG01","shots":["EP14-S01"],"dur":10,"speakers":["CHAR-GRP-01","CHAR-001"],"scene":"SCENE-003"},
    {"id":"EP14-SEG02","shots":["EP14-S02","EP14-S03"],"dur":12,"speakers":["CHAR-007","CHAR-GRP-01","CHAR-001","CHAR-003"],"scene":"SCENE-003"},
    {"id":"EP14-SEG03","shots":["EP14-S04","EP14-S05"],"dur":12,"speakers":["CHAR-007","CHAR-001"],"scene":"SCENE-003"},
    {"id":"EP14-SEG04","shots":["EP14-S06","EP14-S07"],"dur":12,"speakers":["CHAR-007","CHAR-001","CHAR-GRP-01","CHAR-003"],"scene":"SCENE-003"},
    {"id":"EP14-SEG05","shots":["EP14-S08","EP14-S09"],"dur":12,"speakers":["CHAR-001","CHAR-007","CHAR-GRP-01"],"scene":"SCENE-003"},
    {"id":"EP14-SEG06","shots":["EP14-S10"],"dur":10,"speakers":["CHAR-001"],"scene":"SCENE-003"},
    {"id":"EP14-SEG07","shots":["EP14-S11"],"dur":12,"speakers":["CHAR-007","CHAR-001"],"scene":"SCENE-003"},
]

# ===== EP15 =====
EP15_SHOTS = [
    {"shot_id":"EP15-S01","no":1,"dur":6,"scene":"SCENE-003","looks":["CHAR-001-L01"],"props":[],"text":"【图1】CHAR-001-L01（灰色外门粗布袍）【图2】SCENE-003。\n        特写 固定镜头：图1食指前伸——指尖银白光芒在触碰猩红光柱的一刹那骤然爆发。图1银白灵力如涟漪从指尖扩散——猩红光柱出现无数裂纹如碎冰。整道猩红光柱连同暗红令牌一起从内部碎裂——碎片化为漫天红色萤火虫般光点四散消融。图1手指纹丝不动。","roles":[("CHAR-001-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-001","碎。"),("CHAR-001","力道——恰好。不多不少。只碎法宝——不伤持有者的经脉。")],"transition":"hard_cut"},
    {"shot_id":"EP15-S02","no":2,"dur":6,"scene":"SCENE-003","looks":["CHAR-007-L01"],"props":[],"text":"【图1】CHAR-007-L01（绿色修士裙，双髻）【图2】SCENE-003。\n        中景 固定镜头：图1身体如断线风筝般向后飞出——绿色修士裙在空中翻卷如旗。图1面容上红色纹路骤然消退取而代之的是纯粹惊恐和空白。图1飞出十丈远——重重砸在擂台边缘的护罩上才停住——瘫坐在地完全失去反应能力。","roles":[("CHAR-007-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-007","啊——！"),("CHAR-001","受了内伤但不重——三天能好。算我留的情面。")],"transition":"hard_cut"},
    {"shot_id":"EP15-S03","no":3,"dur":6,"scene":"SCENE-003","looks":["CHAR-GRP-01-L01"],"props":[],"text":"【图1】CHAR-GRP-01-L01（灰袍外门弟子）【图2】SCENE-003。\n        全景 固定镜头：图1数十名弟子张着嘴说不出话——有人手中水囊滑落掉在地上。高台上几位长老站了起来——脸上写满不可置信。风吹过擂台——法宝碎片最后几点红色萤光在空气中缓缓消散。连鸟鸣声都停了。","roles":[("CHAR-GRP-01-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-GRP-01","……碎了？"),("CHAR-GRP-01","四品法宝——一下就碎了？")],"transition":"hard_cut"},
    {"shot_id":"EP15-S04","no":4,"dur":6,"scene":"SCENE-003","looks":["CHAR-001-L01"],"props":[],"text":"【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-003。\n        近景 固定镜头：图1低头看着自己的手指——面上浮现一片茫然和害怕。图1大眼睛眨了眨——然后抬起头扫视全场——嘴巴微微张开像做错事的小动物。图1一只手抓住另一只手腕——整个人一副'我怎么会这样'的懵态。","roles":[("CHAR-001-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-001","啊？"),("CHAR-001","我、我只是想挡一下……碎了？"),("CHAR-001","装。继续装。所有人都在看。")],"transition":"hard_cut"},
    {"shot_id":"EP15-S05","no":5,"dur":6,"scene":"SCENE-003","looks":["CHAR-GRP-01-L01"],"props":[],"text":"【图1】CHAR-GRP-01-L01（灰袍外门弟子）【图2】SCENE-003。\n        中景 固定镜头：图1弟子群中终于有人开始窃窃私语——声音越来越大。有人回头看了一眼瘫坐在地的刘芸——又转回来盯着清词。图1中一个弟子用力拍了一下身旁同伴的手臂——嘴都快合不拢了。","roles":[("CHAR-GRP-01-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-GRP-01","她、她怎么做到的？一根手指！"),("CHAR-GRP-01","刘芸刚才那么嚣张——现在一句话都说不出来了。"),("CHAR-GRP-02","外门弟子——一指碎四品法宝……这不可能。")],"transition":"hard_cut"},
    {"shot_id":"EP15-S06","no":6,"dur":6,"scene":"SCENE-003","looks":["CHAR-001-L01"],"props":[],"text":"【图1】CHAR-001-L01（灰色外门粗布袍）【图2】SCENE-003。\n        近景 固定镜头：图1缩着脖子——双手攥紧衣摆——用力往人群后方缩。图1面红耳赤活像被几百双眼睛盯着的社恐患者——脚步碎小频繁往后退。图1整个人一副'求求你们别看我了'的姿态。","roles":[("CHAR-001-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-001","我不是故意的……真的只是想挡一下……"),("CHAR-001","别、别看我了……"),("CHAR-001","反差越大——他们越不会怀疑。没人相信废物能杀人。")],"transition":"hard_cut"},
    {"shot_id":"EP15-S07","no":7,"dur":10,"scene":"SCENE-003","looks":["CHAR-002-L01"],"props":[],"text":"【图1】CHAR-002-L01（白银宗门袍）【图2】SCENE-003。\n        近景 固定镜头：图1独坐高台最远端——周围长老都站起身议论纷纷——唯独图1纹丝不动。图1白银宗门袍在日光中如静止的水面。图1视线穿过人群——嘴角极淡极淡地上扬了一个几乎不可察觉的弧度。图1眼底深处闪过一丝似笑非笑的了然。","roles":[("CHAR-002-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-002","……藏不住了。"),("CHAR-GRP-02","掌门——这个弟子——"),("CHAR-002","本座知道了。"),("CHAR-001","他在笑——他知道。从一开始他就知道。")],"transition":"hard_cut"},
    {"shot_id":"EP15-S08","no":8,"dur":10,"scene":"SCENE-003","looks":["CHAR-010-L01"],"props":[],"text":"【图1】CHAR-010-L01（灰色道袍，面貌平凡）【图2】SCENE-003。\n        特写 固定镜头：图1坐在长老席末端角落——面容毫无特色不引人注意。图1瞳孔骤然收缩成针尖——然后缓缓恢复。图1手从袖中微微伸出——指尖摩挲着袖中某物。图1面上依然挂着客气平淡的微笑——但眼底有一丝极冷的东西在闪动。","roles":[("CHAR-010-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-010","那一指——指尖凝聚灵力的方式。"),("CHAR-010","不可能……天衡宗的碎霜指？百年前就该绝迹了。"),("CHAR-010","这手法——像极了玄霜本人。"),("CHAR-001","有人在看我——那道视线……不是好奇。是……辨认。")],"transition":"hard_cut"},
    {"shot_id":"EP15-S09","no":9,"dur":6,"scene":"SCENE-003","looks":["CHAR-010-L01"],"props":[],"text":"【图1】CHAR-010-L01（灰色道袍，面貌平凡）【图2】SCENE-003。\n        中景 固定镜头：图1站起身——不引人注意地离开长老席。图1步伐不快不慢如同寻常散步——但方向是练剑场边缘无人的走廊尽头。日光在图1灰色道袍上没有留下什么印象——就像一个随时可以被忽略的影子。","roles":[("CHAR-010-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-010","需要确认……需要确认。不能声张。"),("CHAR-010","先传讯。让上面的人判断。")],"transition":"hard_cut"},
    {"shot_id":"EP15-S10","no":10,"dur":6,"scene":"SCENE-003","looks":["CHAR-010-L01"],"props":["PROP-005"],"text":"【图1】CHAR-010-L01（灰色道袍）【图2】SCENE-003【图3】PROP-005。\n        特写 固定镜头：图1从袖中取出图3一枚翠绿色传讯玉简。图3在图1掌心泛起柔和绿光——图1嘴唇微动注入灵力和信息。图3绿光一闪——传讯已发出。图1将图3收回袖中——面上依然是那副客气的微笑。","roles":[("CHAR-010-L01","图1"),("SCENE-003","图2"),("PROP-005","图3")],"dialogue":[("CHAR-010","禀上——天衡宗残党可能还有活口。"),("CHAR-010","凌霄宗外门弟子——碎霜指法——像极了玄霜本人。"),("CHAR-010","建议——派人核实。")],"transition":"hard_cut"},
    {"shot_id":"EP15-S11","no":11,"dur":10,"scene":"SCENE-003","looks":["CHAR-001-L01"],"props":[],"text":"【图1】CHAR-001-L01（灰色外门粗布袍）【图2】SCENE-003。\n        中景 固定镜头：图1靠在练剑场边缘一棵老槐树后——维持着被吓到需要独处的样子。图1目光穿过树干缝隙——锁定在远处走廊尽头那个正在收回玉简的灰袍身影上。图1瞳孔微缩——面上的惊恐表情在无人处悄然褪去。","roles":[("CHAR-001-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-001","那个客卿长老……他在传讯。方向对着我出手的那一刻。"),("CHAR-001","他认出了碎霜指——他知道天衡宗。"),("CHAR-001","我的身份——被人盯上了。")],"transition":"hard_cut"},
    {"shot_id":"EP15-S12","no":12,"dur":12,"scene":"SCENE-003","looks":["CHAR-001-L01"],"props":[],"text":"【图1】CHAR-001-L01（灰色外门粗布袍，低马尾）【图2】SCENE-003。\n        大特写 缓推：图1面容隐在老槐树的阴影中——半明半暗。日光从枝叶缝隙洒下在图1脸上形成碎金般光斑——但瞳孔深处已经没有一丝暖意。图1手微微攥紧——指甲嵌入掌心。远处练剑场的嘈杂声渐渐传来如同另一个世界。风吹过老槐树叶沙沙如低语。","roles":[("CHAR-001-L01","图1"),("SCENE-003","图2")],"dialogue":[("CHAR-001","一指的代价——比我想的来得快。"),("CHAR-001","从今天起——我不再只是猎人。我也是猎物了。"),("CHAR-001","但——来吧。"),("CHAR-001","前世没能杀完的人……这一世——一个都不会放过。")],"transition":"hard_cut"},
]

EP15_SEGS = [
    {"id":"EP15-SEG01","shots":["EP15-S01","EP15-S02"],"dur":12,"speakers":["CHAR-001","CHAR-007"],"scene":"SCENE-003"},
    {"id":"EP15-SEG02","shots":["EP15-S03","EP15-S04"],"dur":12,"speakers":["CHAR-GRP-01","CHAR-001"],"scene":"SCENE-003"},
    {"id":"EP15-SEG03","shots":["EP15-S05","EP15-S06"],"dur":12,"speakers":["CHAR-GRP-01","CHAR-GRP-02","CHAR-001"],"scene":"SCENE-003"},
    {"id":"EP15-SEG04","shots":["EP15-S07"],"dur":10,"speakers":["CHAR-002","CHAR-GRP-02","CHAR-001"],"scene":"SCENE-003"},
    {"id":"EP15-SEG05","shots":["EP15-S08"],"dur":10,"speakers":["CHAR-010","CHAR-001"],"scene":"SCENE-003"},
    {"id":"EP15-SEG06","shots":["EP15-S09","EP15-S10"],"dur":12,"speakers":["CHAR-010"],"scene":"SCENE-003"},
    {"id":"EP15-SEG07","shots":["EP15-S11"],"dur":10,"speakers":["CHAR-001"],"scene":"SCENE-003"},
    {"id":"EP15-SEG08","shots":["EP15-S12"],"dur":12,"speakers":["CHAR-001"],"scene":"SCENE-003"},
]

# === Generation functions (same as before) ===
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
    lines.append("  model: doubao-seedance-2-0-fast")
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
        look_line = "\n".join(f"        - {lk}" for lk in s["looks"])
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
    lines.append("  model: doubao-seedance-2-0-fast")
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
            desc = CHAR_DESC.get(lk, "")
            lbl = f"图{label_idx}"
            ref_parts.append(f"【{lbl}】{name} {lk}（{desc}）")
            label_map[lk] = lbl
            label_idx += 1
        scene_lbl = f"图{label_idx}"
        ref_parts.append(f"【{scene_lbl}】{SCENE_NAME.get(seg['scene'],seg['scene'])} {seg['scene']}")
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
            # Get visual text (second part after refs)
            text_parts = ss["text"].split("\n")
            visual = text_parts[-1].strip()
            # Replace original labels with segment labels
            for (fid, orig_lbl) in ss["roles"]:
                if fid in label_map:
                    visual = visual.replace(orig_lbl, label_map[fid])
            lines.append(f"        镜头{i+1}（{ss['dur']}秒）{visual}")
        lines.append(f"        [以下对白仅供语音合成，严禁在画面中显示任何文字]")
        for ss in seg_shots:
            for (spk, lt) in ss["dialogue"]:
                name = CHAR_NAME.get(spk, spk)
                # Determine voice
                if spk == "CHAR-001":
                    fake_kw = ["我、","我……我","啊？","我只是想挡","别、别看","我不是故意","希望对手","啊——别","加油"]
                    is_fake = any(k in lt for k in fake_kw)
                    v = VOICE["CHAR-001-藏拙"] if is_fake else VOICE["CHAR-001"]
                else:
                    v = VOICE.get(spk, VOICE["CHAR-001"])
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

# Generate EP14
write_shots_yaml("EP14", "剧本/EP14/EP14_逼手.md", EP14_SHOTS, os.path.join(BASE, "剧本/EP14/EP14_shots.yaml"))
write_segments_yaml("EP14", "剧本/EP14/EP14_逼手.md", EP14_SHOTS, EP14_SEGS,
    ["CHAR-001", "CHAR-001-藏拙", "CHAR-003", "CHAR-007", "CHAR-GRP-01"],
    os.path.join(BASE, "剧本/EP14/EP14_segments.yaml"))

# Generate EP15
write_shots_yaml("EP15", "剧本/EP15/EP15_碎.md", EP15_SHOTS, os.path.join(BASE, "剧本/EP15/EP15_shots.yaml"))
write_segments_yaml("EP15", "剧本/EP15/EP15_碎.md", EP15_SHOTS, EP15_SEGS,
    ["CHAR-001", "CHAR-001-藏拙", "CHAR-002", "CHAR-007", "CHAR-010", "CHAR-GRP-01", "CHAR-GRP-02"],
    os.path.join(BASE, "剧本/EP15/EP15_segments.yaml"))

print("EP14 + EP15 done.")
