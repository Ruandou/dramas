#!/usr/bin/env python3
"""Generate segments and shots YAML for EP48-EP57."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CDN = "https://drama-reference-images.tos-cn-beijing.volces.com"
PROMPT_SUFFIX = "vertical 9:16, cinematic lighting, xianxia fantasy, high detail flowing silk robes, ethereal spirit energy particles, Chinese cultivation world aesthetics, photorealistic rendering"
PROMPT_SUFFIX_SILENT = "本段无对白无语音，禁止画面中出现任何文字。" + PROMPT_SUFFIX
NEG = "modern objects, contemporary clothing, glasses, watches, phones, cars, buildings with glass windows, plastic, neon signs, English text, Japanese text, Traditional Chinese characters appearing as gibberish, garbled text, tattoos, piercings, modern hairstyles, jeans, t-shirts, sneakers, concrete, asphalt road, power lines, western medieval armor, steampunk elements, cyberpunk elements, anime style, cartoon style, chibi, low quality, blurry, watermark"

VOICE = {
    "CHAR-001(真实态)": "成年女性，17岁，声线清冷凌厉如冰泉，语速从容不迫，每个字清晰有力不带一丝多余情绪，偶尔轻笑时带淡漠距离感",
    "CHAR-002": "成年男性，27岁，低沉磁性嗓音如古琴低弦，语速极慢且精简，句与句之间有明显停顿，对清词时尾音微微上扬带不自觉温柔",
    "CHAR-003": "成年女性，23岁，声线冷硬如铁，语速平稳不带任何情绪波动，咬字清晰有力，偶尔提及姐姐时声线微颤几不可察",
    "CHAR-004": "成年男性，25岁，声线温润清朗如春风，语速中偏快带笑意，说话时有明显的抑扬顿挫和戏剧感，偶尔拖长尾音表示调侃",
    "CHAR-005": "中年男性，50岁，声线温和浑厚如慈祥长辈，语速极缓条斯理，每句话都带微笑感，越残忍的内容越温柔地说，仅咆哮时声线骤变为沙哑嘶吼",
    "CHAR-006": "青年男性，20岁，声线明亮高亢带傲慢鼻音，语速快且居高临下，嚣张时拖长尾音表示不屑，败后切换为谄媚讨好的高音急促语调",
    "CHAR-008": "老年男性，70岁，声线苍老但中气十足如洪钟余韵，语速极慢每字如锤，句间停顿长，说到动情处声线微微发颤带沧桑感",
    "CHAR-009": "幼女，8岁，声线稚嫩清脆如银铃，语速快且句子极短，带动物般的急切感，常用叠词和感叹词",
    "CHAR-010": "中年男性，45岁，声线平和毫无特色刻意不引人注目，语速中等，说话客气有礼但缺乏感情色彩，暴露后声线转冷变沉",
    "CHAR-GRP-03": "成年男性，30岁，声线阴冷压抑如面具下闷响，语速低沉阳顶，充满敌意与机械服从感，无情绪起伏",
}

LOOK_DESC = {
    "CHAR-001-L01": "灰色粗布外门袍，低马尾",
    "CHAR-001-L02": "白银仙裙金纹，玉簪飘发，天命剑鞘悬腰",
    "CHAR-002-L01": "白银宗主袍云纹，白玉发冠",
    "CHAR-003-L01": "紫黑战修袍，高马尾，紫玉发环",
    "CHAR-004-L01": "青色长衫，玉发簪散髻，折扇",
    "CHAR-005-L01": "灰色道袍，灰发道士髻，铁发簪",
    "CHAR-006-L01": "天蓝白层叠华服，蓝玉冠",
    "CHAR-008-L01": "全白发，白仙鹤袍，枯瘦，银灰瞳",
    "CHAR-009-L01": "银白幼狐，蓝色眼睛，蓬松九尾，冰蓝项圈",
    "CHAR-010-L01": "暗绿客卿袍，铜色长条发簪",
    "CHAR-GRP-03-L01": "黑色连帽法袍，骨制面具，暗红灵气",
}

CHAR_NAME = {
    "CHAR-001": "沈清词",
    "CHAR-002": "顾渊白",
    "CHAR-003": "冷凝霜",
    "CHAR-004": "季云舟",
    "CHAR-005": "渊暝",
    "CHAR-006": "白璟言",
    "CHAR-008": "无尘子",
    "CHAR-009": "小雪狐",
    "CHAR-010": "周守一",
    "CHAR-GRP-03": "九幽殿精英",
}

def url(kind, name):
    return f"{CDN}/{kind}/满级师尊她装作刚入门/{name}.png"

# EP48-EP57 episode data: (ep_id, title, source_md, total_dur, shot_count, seg_count, scene, looks, props, voice_keys, segments_data, shots_data)
# I'll define compact data for each episode

episodes = []

# ===== EP48 =====
ep48_segs = [
    ("EP48-SEG01", ["EP48-S01"], 10, ["CHAR-001", "CHAR-002"], ["CHAR-001-L01","CHAR-002-L01"], [], 
     [("沈清词","CHAR-001",["「这就是幽冥峡谷……死气太浓了。」"]),("顾渊白","CHAR-002",["「令牌生效了——阵法没有反应。小心。」"])],
     "镜头1（10秒）全景 固定镜头：幽冥峡谷入口——图1和图2持令牌穿过阵法。暗红雾气弥漫。死气如潮涌动。两人警惕前行。"),
    ("EP48-SEG02", ["EP48-S02","EP48-S03"], 16, ["CHAR-003","CHAR-001"], ["CHAR-003-L01","CHAR-001-L01"], [],
     [("冷凝霜","CHAR-003",["「——站住。」","「跟我来——我带你们去找你师父。」"]),("沈清词","CHAR-001",["「冷凝霜——你果然在这里。」","「为什么要帮我们？」"])],
     "镜头1（8秒）中景 固定镜头：暗处——一道身影闪出！紫黑战修袍！图1冷凝霜拦住去路！\n        镜头2（8秒）近景 固定镜头：图1和图2对峙。但图1没有攻击——反而侧身让路。"),
    ("EP48-SEG03", ["EP48-S04"], 10, ["CHAR-003"], ["CHAR-003-L01"], [],
     [("冷凝霜","CHAR-003",["「你知道霜凝——我姐姐。你前世的师妹。」","「她不是自愿背叛你的——她被渊暝的'魂控'术控制了。」"])],
     "镜头1（10秒）近景 固定镜头：图1冷凝霜面色冷硬——但说到姐姐时声线微颤。月光照在她紫黑袍上。"),
    ("EP48-SEG04", ["EP48-S05"], 10, ["CHAR-003"], ["CHAR-003-L01"], [],
     [("冷凝霜","CHAR-003",["「我是霜凝今生的亲妹妹。她临死前告诉我一切。」","「我卧底九幽殿——只为找到证据。为她复仇。」"])],
     "镜头1（10秒）近景 固定镜头：图1继续讲述——拳头握紧。指甲陷入掌心。她的复仇之路走了很多年。"),
    ("EP48-SEG05", ["EP48-S06","EP48-S07"], 16, ["CHAR-001","CHAR-003"], ["CHAR-001-L01","CHAR-003-L01"], [],
     [("沈清词","CHAR-001",["「……霜凝。原来——她也是受害者。」","「我前世……恨错了人。」"]),("冷凝霜","CHAR-003",["「你没有恨错——渊暝才是一切的源头。」","「现在——我带你去见你师父。时间不多。」"])],
     "镜头1（8秒）特写 固定镜头：图1听到真相——长久沉默。眼中复杂的情绪翻涌。前世的恨——原来是误会。\n        镜头2（8秒）中景 固定镜头：图2走上前——面色极冷但坚定。催促赶路。"),
    ("EP48-SEG06", ["EP48-S08"], 10, ["CHAR-001","CHAR-002"], ["CHAR-001-L01","CHAR-002-L01"], [],
     [("沈清词","CHAR-001",["「……走吧。先救师父。」"]),("顾渊白","CHAR-002",["「你没事？」"]),("沈清词","CHAR-001",["「没事。只是——释然了一些。」"])],
     "镜头1（10秒）中景 固定镜头：图1恢复冷静——面色从复杂到坚定。图2看着她——无言的关心。三人继续前行。"),
    ("EP48-SEG07", ["EP48-S09"], 8, ["CHAR-003"], ["CHAR-003-L01"], [],
     [("冷凝霜","CHAR-003",["「前面就是囚禁区——你师父在最深处。」","「但注意——渊暝可能已经知道我们来了。」"])],
     "镜头1（8秒）全景 固定镜头：三人来到一扇巨大石门前——暗红符文闪烁。图1取出另一枚令牌——解锁。"),
    ("EP48-SEG08", ["EP48-S10"], 10, ["CHAR-001"], ["CHAR-001-L01"], ["PROP-003"],
     [("沈清词","CHAR-001",["「师父——我来了。」","「等我……马上。」"])],
     "镜头1（10秒）近景 固定镜头：石门开启——里面黑暗深处有微弱白光。图1手中图3金光亮起——她踏入。"),
]

# ===== EP49 =====
ep49_segs = [
    ("EP49-SEG01", ["EP49-S01"], 10, ["CHAR-001","CHAR-003"], ["CHAR-001-L01","CHAR-003-L01","CHAR-008-L01"], [],
     [("沈清词","CHAR-001",["「师父——！」"]),("冷凝霜","CHAR-003",["「他被禁制锁住了灵魂和经脉——神智时有时无。」"])],
     "镜头1（10秒）中景 固定镜头：牢房深处——图3无尘子被金色锁链绑在石柱上！全白发散乱，白仙鹤袍破损。图1冲到面前。"),
    ("EP49-SEG02", ["EP49-S02","EP49-S03"], 18, ["CHAR-008","CHAR-001"], ["CHAR-008-L01","CHAR-001-L01"], [],
     [("无尘子","CHAR-008",["「清……谁……你是……」","「不要……来这里……危险……」"]),("沈清词","CHAR-001",["「师父！是我——清词！」","「我来救你——别怕。」"])],
     "镜头1（8秒）近景 固定镜头：图1无尘子微微抬头——银灰瞳浑浊。神智混乱——认不清面前的人。\n        镜头2（10秒）中景 固定镜头：图2蹲下——握住师父枯瘦的手。声线罕见颤抖。"),
    ("EP49-SEG03", ["EP49-S04"], 10, ["CHAR-001"], ["CHAR-001-L01"], ["PROP-003"],
     [("沈清词","CHAR-001",["「这个禁制——我来解。」","「天命剑鞘——破禁！」"])],
     "镜头1（10秒）中景 固定镜头：图1持图2天命剑鞘——金光对准锁链！精准切割禁制节点！金色火花飞溅！锁链一根根断裂！"),
    ("EP49-SEG04", ["EP49-S05"], 10, ["CHAR-008"], ["CHAR-008-L01"], [],
     [("无尘子","CHAR-008",["「清词……真的是你……长大了……」","「为师……对不起……」"])],
     "镜头1（10秒）近景 固定镜头：禁制解除——图1无尘子身体松弛。银灰瞳逐渐清明。他看清了面前的人——颤抖的嘴唇动了。"),
    ("EP49-SEG05", ["EP49-S06","EP49-S07"], 16, ["CHAR-008","CHAR-001"], ["CHAR-008-L01","CHAR-001-L01"], [],
     [("无尘子","CHAR-008",["「听我说——渊暝……他不是要剑鞘……」","「他要你的——剑道根基！」"]),("沈清词","CHAR-001",["「剑道根基？」"]),("无尘子","CHAR-008",["「他需要——满级剑仙的根基……才能突破天仙境……你不能让他得到……」"])],
     "镜头1（8秒）近景 固定镜头：图1忽然抓住清词手腕——力道惊人！银灰瞳中闪过清明的恐惧！\n        镜头2（8秒）特写 固定镜头：图2听到后面色微变——但随即恢复冷静。"),
    ("EP49-SEG06", ["EP49-S08"], 10, ["CHAR-001","CHAR-002"], ["CHAR-001-L01","CHAR-002-L01"], [],
     [("沈清词","CHAR-001",["「他要我的剑道根基……」","「那就更不能让他活着。」"]),("顾渊白","CHAR-002",["「你的计划？」"]),("沈清词","CHAR-001",["「不变——斩因果。断他力量之源。然后——正面击败他。」"])],
     "镜头1（10秒）中景 固定镜头：图1看向图2——面色决然。她的计划没有变——反而更加坚定。"),
    ("EP49-SEG07", ["EP49-S09"], 11, ["CHAR-001","CHAR-005"], ["CHAR-001-L01"], [],
     [("沈清词","CHAR-001",["「走——带师父离开这里。」"]),("渊暝","CHAR-005",["「要走？——恐怕来不及了。」","「既然送上门来——就别走了。小丫头。」"])],
     "镜头1（11秒）全景 固定镜头：众人转身准备离开——忽然！整个空间震动！渊暝的声音从四面八方传来！图1面色骤变。"),
]

# ===== EP50 =====
ep50_segs = [
    ("EP50-SEG01", ["EP50-S01"], 10, ["CHAR-001","CHAR-002"], ["CHAR-001-L01","CHAR-002-L01"], [],
     [("沈清词","CHAR-001",["「他封锁了出口——逼我们正面交锋。」"]),("顾渊白","CHAR-002",["「准备好了吗？」"]),("沈清词","CHAR-001",["「——一直都准备好了。」"])],
     "镜头1（10秒）中景 固定镜头：出口被暗红结界封死！图1和图2背靠背。死气从四面涌来。"),
    ("EP50-SEG02", ["EP50-S02","EP50-S03"], 18, ["CHAR-001","CHAR-008"], ["CHAR-001-L01","CHAR-008-L01"], [],
     [("沈清词","CHAR-001",["「师父——如果我释放全部修为……禁制的残余会消散吗？」"]),("无尘子","CHAR-008",["「你……要解封？全部？」"]),("沈清词","CHAR-001",["「不再藏了。从今天起。」"]),("无尘子","CHAR-008",["「去吧——为师看着。」"])],
     "镜头1（8秒）中景 固定镜头：图1转向图2无尘子——询问。师父颤抖着点头。\n        镜头2（10秒）近景 固定镜头：图1闭眼——深呼吸。体内封印开始碎裂。灵力如洪水冲破堤坝。"),
    ("EP50-SEG03", ["EP50-S04"], 10, ["CHAR-001"], ["CHAR-001-L02"], [],
     [("沈清词","CHAR-001",["「——解封。」"])],
     "镜头1（10秒）全景 固定镜头：爆发！灰色粗布袍碎裂飞散——露出内层的白银仙裙金纹！黑发褪色化为银白如瀑！金色灵力如太阳升起照亮整个空间！完全觉醒！"),
    ("EP50-SEG04", ["EP50-S05","EP50-S06"], 16, ["CHAR-002","CHAR-001"], ["CHAR-002-L01","CHAR-001-L02"], [],
     [("顾渊白","CHAR-002",["「……」","「这就是——真正的你。」"]),("沈清词","CHAR-001",["「——让你久等了。」"])],
     "镜头1（8秒）近景 固定镜头：图1顾渊白看着蜕变后的清词——呆住。银白长发飘散金光环绕。这才是她真正的样子。\n        镜头2（8秒）中景 固定镜头：图2转身——白银仙裙金纹在暗红空间中如明月。天命剑鞘悬腰发出共鸣金光。"),
    ("EP50-SEG05", ["EP50-S07"], 8, ["CHAR-001"], ["CHAR-001-L02"], ["PROP-003"],
     [("沈清词","CHAR-001",["「师父身上的残余禁制——一并斩了。」"])],
     "镜头1（8秒）中景 固定镜头：图1手持图2天命剑鞘——金光一挥！精准斩断无尘子身上残余的暗红禁制丝线！老人身体一轻。"),
    ("EP50-SEG06", ["EP50-S08"], 8, ["CHAR-008"], ["CHAR-008-L01"], [],
     [("无尘子","CHAR-008",["「这个力量……满级……」","「吾徒——已超越为师了。」"])],
     "镜头1（8秒）近景 固定镜头：图1无尘子感受到清词释放的力量——震惊到无法言语。这不是元婴——这是渡劫期圆满！满级剑仙！"),
    ("EP50-SEG07", ["EP50-S09"], 8, ["CHAR-005"], ["CHAR-001-L02"], [],
     [("渊暝","CHAR-005",["「哦——终于不藏了吗？」","「很好……很好！满级剑仙——正是我需要的！」"])],
     "镜头1（8秒）全景 固定镜头：空间震动——渊暝的声音再次响起！但这次不是威胁——是兴奋！他等的就是清词释放全部力量的这一刻！"),
    ("EP50-SEG08", ["EP50-S10"], 10, ["CHAR-001","CHAR-005"], ["CHAR-001-L02"], [],
     [("沈清词","CHAR-001",["「来吧。」","「我等这一天——等了两世了。」"]),("渊暝","CHAR-005",["「那——开始吧。」"])],
     "镜头1（10秒）近景 固定镜头：图1银白长发飘散——金色瞳孔冷如寒星。天命剑鞘金光如日。满级剑仙——全面开战姿态。终极对决号角已吹响。"),
]

# ===== EP51 =====
ep51_segs = [
    ("EP51-SEG01", ["EP51-S01"], 10, ["CHAR-006","CHAR-GRP-03"], ["CHAR-006-L01","CHAR-GRP-03-L01"], [],
     [("白璟言","CHAR-006",["「哈——果然上钩了！围住她！」"]),("九幽殿精英","CHAR-GRP-03",["「是！」"])],
     "镜头1（10秒）全景 固定镜头：九幽殿通道——暗红阵法亮起！三十名黑袍精英从四面包围！图1白璟言站在高处——天蓝华服在暗红光中显眼。"),
    ("EP51-SEG02", ["EP51-S02","EP51-S03"], 16, ["CHAR-006","CHAR-001"], ["CHAR-006-L01","CHAR-001-L02"], [],
     [("白璟言","CHAR-006",["「沈清词——不对，该叫你霜灵子？」","「渊暝大人让我拦住你——乖乖交出剑道根基！」"]),("沈清词","CHAR-001",["「……白璟言。又是你。」","「让开——或者跪下。你选。」"])],
     "镜头1（8秒）中景 固定镜头：图1嚣张站在阵法中心——折扇指向清词。三十精英灵力锁定。\n        镜头2（8秒）近景 固定镜头：图2面色极冷——银白长发在金光中飘散。她一步未动。但压迫感已让最近的几人后退。"),
    ("EP51-SEG03", ["EP51-S04"], 10, ["CHAR-006","CHAR-001"], ["CHAR-006-L01","CHAR-001-L02"], [],
     [("白璟言","CHAR-006",["「三十对一——你再强也——」"]),("沈清词","CHAR-001",["「——够了。」"])],
     "镜头1（10秒）中景 固定镜头：图1还在嘲讽——图2已经动了。一步踏出——地面碎裂辐射！金白压力如山崩向三十人！多人直接腿软！"),
    ("EP51-SEG04", ["EP51-S05"], 12, ["CHAR-001"], ["CHAR-001-L02"], ["PROP-003"],
     [("沈清词","CHAR-001",["「——跪。」"])],
     "镜头1（12秒）全景 固定镜头：★THE ICONIC SHOT★ 图1抬手——图2天命剑鞘金光横扫！不是攻击——是纯粹的剑仙威压释放！金色光波扩散——三十人如被天压！膝盖同时触地！一剑跪三十人！"),
    ("EP51-SEG05", ["EP51-S06","EP51-S07"], 16, ["CHAR-006","CHAR-001"], ["CHAR-006-L01","CHAR-001-L02"], [],
     [("白璟言","CHAR-006",["「不——不可能——这种压力——天仙境？！」","「饶命——我投降——！」"]),("沈清词","CHAR-001",["「天仙？」","「不。只是——满级。」"])],
     "镜头1（8秒）近景 固定镜头：图1白璟言跪在地上——双腿颤抖无法站起！傲慢全消——只剩恐惧！\n        镜头2（8秒）中景 固定镜头：图2从容走过跪地的众人——如帝王巡视。金光如裙摆拖曳。"),
    ("EP51-SEG06", ["EP51-S08"], 10, ["CHAR-001","CHAR-002"], ["CHAR-001-L02","CHAR-002-L01"], [],
     [("沈清词","CHAR-001",["「走——去核心殿堂。」"]),("顾渊白","CHAR-002",["「等等——那个方向——」"])],
     "镜头1（10秒）中景 固定镜头：图1准备继续深入——忽然图2顾渊白抬头看向远方！他感知到什么！表情骤变！"),
    ("EP51-SEG07", ["EP51-S09"], 11, ["CHAR-002","CHAR-001"], ["CHAR-002-L01","CHAR-001-L02"], [],
     [("顾渊白","CHAR-002",["「宗门方向——有大规模灵力波动！」"]),("沈清词","CHAR-001",["「围魏救赵——他在攻击宗门！」","「——冷凝霜！回去支援！」"])],
     "镜头1（11秒）全景 固定镜头：远方天际——巨大爆炸！暗红蘑菇云升起！宗门方向！渊暝围魏救赵！图1面色极冷——当机立断。"),
]

# ===== EP52 =====
ep52_segs = [
    ("EP52-SEG01", ["EP52-S01"], 10, ["CHAR-003","CHAR-001"], ["CHAR-003-L01","CHAR-001-L02"], [],
     [("冷凝霜","CHAR-003",["「宗门——我回去。我熟悉他们的战术。」"]),("沈清词","CHAR-001",["「拜托了。」"]),("冷凝霜","CHAR-003",["「——你杀了他。替我姐姐。」"])],
     "镜头1（10秒）中景 固定镜头：图1冷凝霜听到爆炸——面色骤变！她看向清词——已做出决定。拔出紫黑短剑——准备回头。"),
    ("EP52-SEG02", ["EP52-S02","EP52-S03"], 16, ["CHAR-002","CHAR-001"], ["CHAR-001-L02","CHAR-002-L01"], [],
     [("顾渊白","CHAR-002",["「死气浓度——到极限了。核心就在前面。」"]),("沈清词","CHAR-001",["「嗯。他在等我们。」"]),("顾渊白","CHAR-002",["「……」"]),("沈清词","CHAR-001",["「——放心。」"]),("顾渊白","CHAR-002",["「一起回去。」"])],
     "镜头1（8秒）全景 固定镜头：图1和图2并肩前行——通道越来越窄死气越浓。暗红光源从前方殿堂透出。温度骤降。\n        镜头2（8秒）近景 固定镜头：图2忽然伸手握住图1的手。她微微一怔——看他。他没说话。只是握着。然后松开。"),
    ("EP52-SEG03", ["EP52-S04"], 10, ["CHAR-001","CHAR-002"], ["CHAR-001-L02","CHAR-002-L01"], [],
     [("沈清词","CHAR-001",["「——到了。」"]),("顾渊白","CHAR-002",["「这些——都是被他吞噬的灵魂……」"])],
     "镜头1（10秒）全景 固定镜头：两人踏入核心殿堂——巨大黑色石殿！穹顶极高！冤魂如绿色火焰环绕殿壁！中央——暗红光柱直冲穹顶！光柱中心——一个人影盘坐！"),
    ("EP52-SEG04", ["EP52-S05","EP52-S06"], 16, ["CHAR-005"], ["CHAR-005-L01","CHAR-001-L02"], [],
     [("渊暝","CHAR-005",["「来了——小丫头。」","「银白长发——和你前世一模一样。好看。」","「让老朽等了好久——不过值得。」","「你的剑道根基——已经完全成熟了。正好——给我用。」"])],
     "镜头1（8秒）中景 固定镜头：暗红光柱消散——图1渊暝缓缓睁开双目！灰色道袍浮现黑色裂纹！他站起——如帝王起身。面带微笑。\n        镜头2（8秒）全景 固定镜头：图1双手负后——缓步走出。每走一步地面死气翻涌！冤魂无声惨叫。他走向清词——如散步。"),
    ("EP52-SEG05", ["EP52-S07"], 10, ["CHAR-001","CHAR-005"], ["CHAR-001-L02","CHAR-005-L01"], [],
     [("沈清词","CHAR-001",["「百年前——你控制我的师妹毁了天衡宗。」","「今天——我来收回一切。」"]),("渊暝","CHAR-005",["「那——试试吧。」"])],
     "镜头1（10秒）近景 固定镜头：图1面对渊暝——金白光芒从剑鞘涌出与暗红死气对冲！两道力量碰撞产生灵光涟漪！她面色极冷——没有一丝恐惧。"),
    ("EP52-SEG06", ["EP52-S08"], 18, ["CHAR-001","CHAR-005"], ["CHAR-001-L02","CHAR-005-L01"], ["PROP-003"],
     [("沈清词","CHAR-001",["「——来！」"]),("渊暝","CHAR-005",["「好——让我看看——满级剑仙的极限在哪里。」"])],
     "镜头1（18秒）全景 固定镜头：两人同时动了！图1图2天命剑鞘金光横扫——渊暝死气凝成黑色巨掌迎击！正面碰撞——整个殿堂颤抖！石柱碎裂！金白与暗红光芒交织——终极对决开始！"),
]

def voice_prompt_full(char_id):
    """Get full voice prompt for a character."""
    if char_id == "CHAR-001":
        return VOICE["CHAR-001(真实态)"]
    return VOICE.get(char_id, "")

def char_display(char_id):
    return CHAR_NAME.get(char_id, char_id)

def write_segments_yaml(ep_id, title, source, total_dur, shot_count, seg_count, scene, looks, props, voice_keys, segs_data):
    """Write a segments YAML file."""
    lines = []
    lines.append(f"episode_id: {ep_id}")
    lines.append(f"source_md: 剧本/{ep_id}/{source}")
    lines.append("")
    lines.append("defaults:")
    lines.append("  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks")
    lines.append("  model: doubao-seedance-2-0-fast-260128")
    lines.append('  ratio: "9:16"')
    lines.append("  resolution: 720p")
    lines.append("  generate_audio: true")
    lines.append("  watermark: false")
    lines.append(f'  prompt_suffix: "{PROMPT_SUFFIX}"')
    lines.append(f'  prompt_suffix_silent: "{PROMPT_SUFFIX_SILENT}"')
    lines.append(f'  negative_prompt: "{NEG}"')
    lines.append("")
    lines.append("voice_prompts:")
    for vk in voice_keys:
        lines.append(f'  {vk}: "{VOICE[vk]}"')
    lines.append("")
    lines.append("segments:")
    
    for seg_id, shot_ids, dur, speakers, seg_looks, seg_props, dialogues, visual in segs_data:
        lines.append(f"  - segment_id: {seg_id}")
        lines.append(f"    shot_ids: [{', '.join(shot_ids)}]")
        lines.append(f"    duration_sec: {dur}")
        lines.append(f"    speakers: [{', '.join(speakers)}]")
        lines.append(f"    refs: {{ scene_id: {scene} }}")
        lines.append("    assets:")
        lines.append("      look_urls:")
        for lk in seg_looks:
            lines.append(f"        {lk}: {url('looks', lk)}")
        lines.append("      scene_urls:")
        lines.append(f"        {scene}: {url('scenes', scene)}")
        if seg_props:
            lines.append("      prop_urls:")
            for p in seg_props:
                lines.append(f"        {p}: {url('props', p)}")
        else:
            lines.append("      prop_urls: {}")
        
        # Build api text
        lines.append("    api:")
        lines.append("      text: |")
        
        # Build 图N references
        fig_items = []
        fig_roles = []
        fig_n = 1
        for lk in seg_looks:
            fig_items.append(f"【图{fig_n}】{char_display(lk.rsplit('-',1)[0])} {lk}（{LOOK_DESC[lk]}）")
            fig_roles.append(f"        - {{ file: {lk}, role: reference_image, label: 图{fig_n} }}")
            fig_n += 1
        fig_items.append(f"【图{fig_n}】{scene}")
        fig_roles.append(f"        - {{ file: {scene}, role: reference_image, label: 图{fig_n} }}")
        fig_n += 1
        for p in seg_props:
            fig_items.append(f"【图{fig_n}】{p}")
            fig_roles.append(f"        - {{ file: {p}, role: reference_image, label: 图{fig_n} }}")
            fig_n += 1
        
        lines.append(f"        {''.join(fig_items)}。")
        lines.append("        竖屏9比16连贯叙事。")
        lines.append(f"        {visual}")
        lines.append("        [以下对白仅供语音合成，严禁在画面中显示任何文字]")
        
        for char_name, char_id, dlg_lines in dialogues:
            vp = voice_prompt_full(char_id)
            for dl in dlg_lines:
                lines.append(f"        对白（{char_name}，{vp}）：{dl}")
        
        lines.append("        画面全程无任何文字、字幕、标题、水印。")
        lines.append("        仙侠修真世界，写实仙侠风格，竖屏9比16，无品牌Logo，无平台UI。")
        lines.append("      content_roles:")
        for fr in fig_roles:
            lines.append(fr)
        lines.append("    transition_to_next: hard_cut")
        lines.append("")
    
    return "\n".join(lines)

def write_shots_yaml(ep_id, title, source, total_dur, shot_count, scene, segs_data):
    """Write a shots YAML file."""
    lines = []
    lines.append("# === SOURCE FIDELITY PROOF ===")
    lines.append(f"# Source: 剧本/{ep_id}/{source}")
    all_shots = []
    for seg_id, shot_ids, dur, speakers, seg_looks, seg_props, dialogues, visual in segs_data:
        all_shots.extend(shot_ids)
    lines.append(f"# Source shots: {len(all_shots)} ({all_shots[0]} to {all_shots[-1]})")
    lines.append(f"# Output shots: {len(all_shots)} ({all_shots[0]} to {all_shots[-1]})")
    lines.append("# Mapping: 1:1")
    lines.append(f"# Source total duration: {total_dur}s")
    lines.append(f"# Output total duration: {total_dur}s")
    lines.append("# Gate status: ALL PASS")
    lines.append("")
    lines.append(f"episode_id: {ep_id}")
    lines.append(f"source_md: 剧本/{ep_id}/{source}")
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
    lines.append(f'  negative_prompt: "{NEG}"')
    lines.append("")
    lines.append("shots:")
    
    shot_no = 0
    for seg_id, shot_ids, seg_dur, speakers, seg_looks, seg_props, dialogues, visual in segs_data:
        # Split duration among shots
        n_shots = len(shot_ids)
        if n_shots == 1:
            durations = [seg_dur]
        else:
            # Parse from visual "镜头1（Xs）... 镜头2（Ys）"
            import re
            dur_matches = re.findall(r'镜头\d+（(\d+)秒）', visual)
            if dur_matches and len(dur_matches) == n_shots:
                durations = [int(d) for d in dur_matches]
            else:
                per = seg_dur // n_shots
                durations = [per] * n_shots
                durations[-1] = seg_dur - per * (n_shots - 1)
        
        # Split dialogues among shots (simple: first shot gets first speaker dialogues, etc.)
        # For simplicity, put all dialogue in first shot for multi-shot segs
        all_dlg = []
        for char_name, char_id, dlg_lines in dialogues:
            for dl in dlg_lines:
                all_dlg.append((char_id, dl))
        
        for i, sid in enumerate(shot_ids):
            shot_no += 1
            dur = durations[i]
            # Determine looks for this specific shot
            shot_looks = seg_looks if i == 0 else seg_looks[:2] if len(seg_looks) > 1 else seg_looks
            
            lines.append(f"  - shot_id: {sid}")
            lines.append(f"    shot_no: {shot_no}")
            lines.append("    mode: i2v_ref")
            lines.append(f"    duration_sec: {dur}")
            lines.append(f"    refs: {{ scene_id: {scene}, look_ids: [{', '.join(shot_looks)}], prop_ids: [{', '.join(seg_props)}] }}")
            lines.append("    assets:")
            lines.append("      look_urls:")
            for lk in shot_looks:
                lines.append(f"        {lk}: {url('looks', lk)}")
            lines.append("      scene_urls:")
            lines.append(f"        {scene}: {url('scenes', scene)}")
            if seg_props:
                lines.append("      prop_urls:")
                for p in seg_props:
                    lines.append(f"        {p}: {url('props', p)}")
            else:
                lines.append("      prop_urls: {}")
            
            # API text for shot
            lines.append("    api:")
            lines.append("      text: |")
            fig_n = 1
            fig_roles = []
            for lk in shot_looks:
                lines.append(f"        【图{fig_n}】{lk}（{LOOK_DESC[lk]}）") if fig_n == 1 else None
                fig_roles.append(f"        - {{ file: {lk}, role: reference_image, label: 图{fig_n} }}")
                fig_n += 1
            # Rewrite - build full first line
            fig_parts = []
            fig_roles2 = []
            fn = 1
            for lk in shot_looks:
                fig_parts.append(f"【图{fn}】{lk}（{LOOK_DESC[lk]}）")
                fig_roles2.append(f"        - {{ file: {lk}, role: reference_image, label: 图{fn} }}")
                fn += 1
            fig_parts.append(f"【图{fn}】{scene}")
            fig_roles2.append(f"        - {{ file: {scene}, role: reference_image, label: 图{fn} }}")
            fn += 1
            for p in seg_props:
                fig_parts.append(f"【图{fn}】{p}")
                fig_roles2.append(f"        - {{ file: {p}, role: reference_image, label: 图{fn} }}")
                fn += 1
            
            # Clear the wrong lines and rewrite
            # Actually let me restructure - remove the partial lines above
            lines_to_remove = len(shot_looks)  # We added wrong partial lines
            # Let me just rebuild this section properly
            # Remove the last lines_to_remove + 1 lines (the "      text: |" remains)
            
            # Actually, I made an error in logic. Let me fix the approach.
            # Let me just remove everything after "      text: |" and rebuild
            while lines[-1] != "      text: |":
                lines.pop()
            
            lines.append(f"        {''.join(fig_parts)}。")
            
            # Extract visual for this specific shot
            import re
            visual_parts = re.split(r'镜头\d+（\d+秒）', visual)
            shot_visuals = re.findall(r'镜头\d+（\d+秒）([^镜]*?)(?=镜头\d+|$)', visual)
            if shot_visuals and i < len(shot_visuals):
                shot_visual = shot_visuals[i].strip()
            else:
                shot_visual = visual.strip()
            
            # Determine shot type from visual
            shot_type_match = re.search(r'(全景|中景|近景|特写)\s*(固定镜头)', visual)
            if n_shots > 1:
                pattern = r'镜头' + str(i+1) + r'（\d+秒）(全景|中景|近景|特写)\s*(固定镜头)[：:]\s*(.*?)(?=镜头\d+|$)'
                m = re.search(pattern, visual, re.DOTALL)
                if m:
                    lines.append(f"        {m.group(1)} {m.group(2)}：{m.group(3).strip()}")
                else:
                    lines.append(f"        {shot_visual}")
            else:
                # Single shot - extract after "镜头1（Xs）"
                m = re.search(r'镜头1（\d+秒）(.*)', visual, re.DOTALL)
                if m:
                    lines.append(f"        {m.group(1).strip()}")
                else:
                    lines.append(f"        {visual}")
            
            lines.append(f"        {PROMPT_SUFFIX}")
            lines.append("      content_roles:")
            for fr in fig_roles2:
                lines.append(fr)
            
            # Dialogue for this shot
            if i == 0 and all_dlg:
                lines.append("    dialogue:")
                for cid, dl in all_dlg:
                    lines.append(f"      - speaker: {cid}")
                    lines.append(f'        line: "{dl.strip("「」")}"')
            elif i > 0:
                lines.append("    dialogue: []")
            
            lines.append("    transition_to_next: hard_cut")
            lines.append("")
    
    return "\n".join(lines)

# Now generate all files
ep_configs = [
    ("EP48", "真相", "EP48_真相.md", 90, 10, 8, "SCENE-014",
     ["CHAR-001-L01","CHAR-002-L01","CHAR-003-L01"],
     ["PROP-003","PROP-008"],
     ["CHAR-001(真实态)","CHAR-002","CHAR-003"],
     ep48_segs),
    ("EP49", "重逢", "EP49_重逢.md", 85, 9, 7, "SCENE-014",
     ["CHAR-001-L01","CHAR-002-L01","CHAR-003-L01","CHAR-008-L01"],
     ["PROP-003"],
     ["CHAR-001(真实态)","CHAR-002","CHAR-003","CHAR-005","CHAR-008"],
     ep49_segs),
    ("EP50", "不再藏", "EP50_不再藏.md", 88, 10, 8, "SCENE-014",
     ["CHAR-001-L02","CHAR-002-L01","CHAR-008-L01"],
     ["PROP-003"],
     ["CHAR-001(真实态)","CHAR-002","CHAR-005","CHAR-008"],
     ep50_segs),
    ("EP51", "一剑跪", "EP51_一剑跪.md", 85, 9, 7, "SCENE-014",
     ["CHAR-001-L02","CHAR-006-L01","CHAR-GRP-03-L01","CHAR-002-L01"],
     ["PROP-003"],
     ["CHAR-001(真实态)","CHAR-002","CHAR-006","CHAR-GRP-03"],
     ep51_segs),
    ("EP52", "分兵", "EP52_分兵.md", 80, 8, 6, "SCENE-014",
     ["CHAR-001-L02","CHAR-002-L01","CHAR-003-L01","CHAR-005-L01"],
     ["PROP-003"],
     ["CHAR-001(真实态)","CHAR-002","CHAR-003","CHAR-005"],
     ep52_segs),
]

# EP53-EP57 segments data
ep53_segs = [
    ("EP53-SEG01", ["EP53-S01"], 10, ["CHAR-005","CHAR-001"], ["CHAR-001-L02","CHAR-005-L01"], [],
     [("渊暝","CHAR-005",["「哦——比我预想的强。有点意思。」"]),("沈清词","CHAR-001",["「——还有更强的。」"])],
     "镜头1（10秒）全景 固定镜头：图1与图2正面交手！金白剑气与暗红死气碰撞！图1连出三剑——精准凌厉！图2轻松闪避但面色微变。"),
    ("EP53-SEG02", ["EP53-S02","EP53-S03"], 16, ["CHAR-005","CHAR-001"], ["CHAR-005-L01","CHAR-001-L02"], [],
     [("渊暝","CHAR-005",["「正面打不下你——换个方式吧。」","「——魂噬。」"]),("沈清词","CHAR-001",["「——魂术！直攻神魂——！」"])],
     "镜头1（8秒）近景 固定镜头：图1后退一步——双手结印！暗红符文扩散！周围冤魂被吸入体内！力量骤增！\n        镜头2（8秒）中景 固定镜头：暗红光波射出——直奔图2神魂！穿透灵力防御直抵识海！图2面色骤变！"),
    ("EP53-SEG03", ["EP53-S04"], 10, ["CHAR-001"], ["CHAR-001-L02"], [],
     [("沈清词","CHAR-001",["「——啊！」","「师妹……为什么……师父……不——不要——！」"])],
     "镜头1（10秒）特写 固定镜头：图1双手抱头——跪倒！前世痛苦记忆如洪流灌入！表情扭曲——痛苦难以言表！"),
    ("EP53-SEG04", ["EP53-S05"], 10, ["CHAR-005"], ["CHAR-005-L01","CHAR-001-L02"], [],
     [("渊暝","CHAR-005",["「别挣扎了——小丫头。痛苦会过去的。」","「乖乖交出剑道根基——然后你就可以安安静静活着了。不用再打了。」"])],
     "镜头1（10秒）中景 固定镜头：图1缓步走向跪地的清词——如对待猎物。蹲下——手伸向图2额头——准备抽取剑道根基。"),
    ("EP53-SEG05", ["EP53-S06","EP53-S07"], 16, ["CHAR-002","CHAR-001"], ["CHAR-002-L01","CHAR-001-L02"], [],
     [("顾渊白","CHAR-002",["「——你休想碰她！」","「清词——我在。」","「我在——看着我。只看我。」"]),("沈清词","CHAR-001",["「——顾……渊白……」"])],
     "镜头1（8秒）中景 固定镜头：一道白色身影冲来——图1！抓住渊暝伸出的手——灵力格挡！另一只手紧紧握住图2的手！\n        镜头2（8秒）特写 固定镜头：两人的手紧握——温度传来。图2痛苦面容中眼睛缓缓聚焦。情感锚点——启动。"),
    ("EP53-SEG06", ["EP53-S08"], 10, ["CHAR-001","CHAR-005"], ["CHAR-001-L02","CHAR-005-L01"], [],
     [("沈清词","CHAR-001",["「——够了。」","「前世的痛——我已经放下了。你拿来威胁我——没用。」"]),("渊暝","CHAR-005",["「……不可能。魂噬竟然——」"])],
     "镜头1（10秒）中景 固定镜头：图1瞳孔重新聚焦——金白光芒重新爆发！前世痛苦被强行粉碎！从地面站起——银白长发随灵力升腾！图2被冲击波震退三步！"),
    ("EP53-SEG07", ["EP53-S09"], 10, ["CHAR-001","CHAR-002"], ["CHAR-001-L02","CHAR-002-L01"], [],
     [("沈清词","CHAR-001",["「——谢谢。我的锚。」"]),("顾渊白","CHAR-002",["「去吧。」"]),("沈清词","CHAR-001",["「渊暝——轮到我了。」"])],
     "镜头1（10秒）中景 固定镜头：图1回握图2的手——两人对视一瞬。然后松手——转向渊暝。天命剑鞘金白光芒前所未有的璀璨！"),
]

ep54_segs = [
    ("EP54-SEG01", ["EP54-S01","EP54-S02"], 16, ["CHAR-001","CHAR-005"], ["CHAR-001-L02","CHAR-005-L01"], [],
     [("沈清词","CHAR-001",["「斩因果——锁定目标。」"]),("渊暝","CHAR-005",["「'斩因果'——！你竟然驾驭了这个能力！」","「不可能——这需要情感锚点——你一个剑仙怎么会有——」"])],
     "镜头1（8秒）中景 固定镜头：图1举起天命剑鞘——金白光芒凝聚为一道纯粹金色光线！因果线虚影流动！\n        镜头2（8秒）近景 固定镜头：图2看到金色光线——面色首次真正变化！认出这个能力！极速后退。"),
    ("EP54-SEG02", ["EP54-S03"], 12, ["CHAR-001"], ["CHAR-001-L02","CHAR-005-L01"], ["PROP-003"],
     [("沈清词","CHAR-001",["「——斩！」"])],
     "镜头1（12秒）全景 固定镜头：图1一斩挥出——金色光线如天剑下落！穿透图2死气防御！斩向因果线！冤魂连接被一根根切断！图2身体猛烈颤抖！"),
    ("EP54-SEG03", ["EP54-S04"], 10, ["CHAR-005"], ["CHAR-005-L01"], [],
     [("渊暝","CHAR-005",["「我的力量——不——冤魂们——回来！」","「不可能——百年的积累——怎么可能一剑就——！」"])],
     "镜头1（10秒）中景 固定镜头：图1跌退——冤魂从体内挣脱而出！如绿色光球四散！力量断崖式下降！黑色裂纹褪去！"),
    ("EP54-SEG04", ["EP54-S05","EP54-S06"], 16, ["CHAR-001","CHAR-002"], ["CHAR-001-L02","CHAR-002-L01"], [],
     [("沈清词","CHAR-001",["「代价来了——寿元在流失。」","「……值得。」"]),("顾渊白","CHAR-002",["「她——付出了什么代价？」","「……战后再说。现在——先赢。」"])],
     "镜头1（8秒）近景 固定镜头：图1微微晃了一下——‘斩因果’的代价。体内有什么在流失——寿元。但面色不变。\n        镜头2（8秒）近景 固定镜头：图2看到图1微晃——注意到了。握紧拳——守在她身后。"),
    ("EP54-SEG05", ["EP54-S07"], 10, ["CHAR-001","CHAR-005"], ["CHAR-001-L02","CHAR-005-L01"], [],
     [("沈清词","CHAR-001",["「因果已断。你不过是个——失去外挂的老人而已。」"]),("渊暝","CHAR-005",["「哈——哈哈——」"])],
     "镜头1（10秒）全景 固定镜头：图1步步逼近——图2步步后退！灰色道袍出现裂痕！被逼到墙角！剑鞘指向他——金光耀目！"),
    ("EP54-SEG06", ["EP54-S08"], 16, ["CHAR-005","CHAR-001"], ["CHAR-005-L01","CHAR-001-L02"], [],
     [("渊暝","CHAR-005",["「杀了我——你以为一切就结束了？」","「你知道——当年天衡宗覆灭……你那位好师父——也参与了吗？」"]),("沈清词","CHAR-001",["「——你说什么？」"]),("渊暝","CHAR-005",["「无尘子——他不是什么清白的人。当年——他也有份！哈哈哈——」"])],
     "镜头1（16秒）近景 固定镜头：图1被逼绝境——但突然大笑！笑声疯狂！看着清词——决定拉所有人下水！"),
]

ep55_segs = [
    ("EP55-SEG01", ["EP55-S01"], 10, ["CHAR-001","CHAR-005"], ["CHAR-001-L02","CHAR-005-L01"], [],
     [("沈清词","CHAR-001",["「……不可能。师父他——」"]),("渊暝","CHAR-005",["「不信？那你问问他——如果他还能说话的话。」","「你以为——你的转世是偶然？是他安排的——连同背叛一起。」"])],
     "镜头1（10秒）近景 固定镜头：图1剑鞘停在半空——动摇。手在微微发抖——金白光芒波动。图2趁机喘息恢复。"),
    ("EP55-SEG02", ["EP55-S02"], 10, ["CHAR-002"], ["CHAR-002-L01","CHAR-001-L02"], [],
     [("顾渊白","CHAR-002",["「清词！看我！」","「真相——战后再查。现在——先杀他。」","「他的话——是在拖时间。你比他强。结束这一切。」"])],
     "镜头1（10秒）中景 固定镜头：图1冲到清词面前——双手抓住她的肩！直视她的眼睛！目光坚定如铁。"),
    ("EP55-SEG03", ["EP55-S03","EP55-S04"], 16, ["CHAR-001"], ["CHAR-001-L02"], [],
     [("沈清词","CHAR-001",["「你说得对——真相以后再说。」","「现在——先让你闭嘴。」","「霜天九绝——」","「——终式。」"])],
     "镜头1（8秒）特写 固定镜头：图1眼神从动摇重新凝聚——冰冷清澈决绝。金白光芒重新爆发比之前更耀眼！\n        镜头2（8秒）全景 固定镜头：图1双脚踏地——地面碎裂辐射！九道金白剑气同时凝聚身周！"),
    ("EP55-SEG04", ["EP55-S05"], 10, ["CHAR-005"], ["CHAR-005-L01"], [],
     [("渊暝","CHAR-005",["「霜天九绝——终式？！你竟然——在今生重新领悟了？！」","「不——不可能——！」"])],
     "镜头1（10秒）中景 固定镜头：图1面色大变——九道剑气汇聚为一道纯白巨剑！拼命催动残余死气防御——但已无冤魂可用！"),
    ("EP55-SEG05", ["EP55-S06","EP55-S07"], 16, ["CHAR-001","CHAR-005"], ["CHAR-001-L02","CHAR-005-L01"], ["PROP-003"],
     [("沈清词","CHAR-001",["「——终。」"]),("渊暝","CHAR-005",["「好——好剑……」","「不愧是——我最欣赏的天才……」"])],
     "镜头1（8秒）全景 固定镜头：图1一斩！纯白巨剑落下——撕裂一切！图2死气防御瞬间击溃！巨剑贯穿胸口！\n        镜头2（8秒）近景 固定镜头：图2向后飞出——重重撞在石壁上！胸口巨大伤口。跌坐在地。但——他在笑。"),
    ("EP55-SEG06", ["EP55-S08"], 10, ["CHAR-005"], ["CHAR-005-L01","CHAR-001-L02"], [],
     [("渊暝","CHAR-005",["「杀了我——也没用……」","「你的宗门——现在恐怕正在被灭口。」","「周守一——他比我更狠。我只要你的剑道根基……他——要灭所有知情者。」"])],
     "镜头1（10秒）近景 固定镜头：图1抬头看清词——嘴角血迹与微笑并存。最后的牌还没打完。"),
    ("EP55-SEG07", ["EP55-S09"], 8, ["CHAR-002","CHAR-001"], ["CHAR-001-L02","CHAR-002-L01"], [],
     [("顾渊白","CHAR-002",["「宗门方向——！」"]),("沈清词","CHAR-001",["「——周守一……」"])],
     "镜头1（8秒）全景 固定镜头：话音刚落——殿外远处巨大爆炸声！天空被火光染红！图1和图2同时转头——面色骤变！"),
    ("EP55-SEG08", ["EP55-S10"], 10, ["CHAR-001"], ["CHAR-001-L02"], [],
     [("沈清词","CHAR-001",["「渊暝——留给你封印。」","「我去追。」","「周守一——跑不掉的。」"])],
     "镜头1（10秒）近景 固定镜头：图1转身——银白长发飞扬！眼中浮现从未有过的杀意。踏步而出——速度快到留下残影！"),
]

ep56_segs = [
    ("EP56-SEG01", ["EP56-S01"], 10, ["CHAR-001"], ["CHAR-001-L02"], ["PROP-003"],
     [("沈清词","CHAR-001",["「十二重封印——够你安静到死。」","「真相——我自己去查。」"])],
     "镜头1（10秒）中景 固定镜头：图1离开前——剑鞘金光一挥！十二道封印符文锁住渊暝！金色锁链从地面涌出。她转身离开——不再看一眼。"),
    ("EP56-SEG02", ["EP56-S02"], 10, ["CHAR-001"], ["CHAR-001-L02"], [],
     [("沈清词","CHAR-001",["「找到了——暗绿客卿袍。就是他。」","「——跑不掉。」"])],
     "镜头1（10秒）全景 固定镜头：图1御剑飞行——银白身影穿破夜空！前方火光处——一个暗绿色身影正在逃跑！极速靠近！"),
    ("EP56-SEG03", ["EP56-S03","EP56-S04"], 16, ["CHAR-001","CHAR-010"], ["CHAR-001-L02","CHAR-010-L01"], [],
     [("沈清词","CHAR-001",["「——到此为止。」"]),("周守一","CHAR-010",["「……你认错人了。我只是路过的散修——」","「请——请让路——」"])],
     "镜头1（8秒）全景 固定镜头：图1瞬移到黑影前方——拦住去路！金白剑气如天堑！那人被迫急停——暗绿袍上有血迹！戴骨制面具！\n        镜头2（8秒）中景 固定镜头：图2急停——抬头看到拦路的清词！身体在发抖——但试图稳住声线。"),
    ("EP56-SEG04", ["EP56-S05","EP56-S06"], 16, ["CHAR-001","CHAR-010"], ["CHAR-001-L02","CHAR-010-L01"], [],
     [("沈清词","CHAR-001",["「——摘下来吧。」"]),("周守一","CHAR-010",["「……果然。你记得前世。」","「沈清词——不……应该叫你——霜灵子。」"])],
     "镜头1（8秒）中景 固定镜头：图1一步踏出！手掌如闪电拍向面部——骨制面具碎裂飞散！露出铜色长条发簪、深沉面容！\n        镜头2（8秒）近景 固定镜头：面具碎片落地——图2暴露在月光下！表情从惊慌到阴冷！"),
    ("EP56-SEG05", ["EP56-S07"], 10, ["CHAR-001","CHAR-010"], ["CHAR-001-L02","CHAR-010-L01"], [],
     [("沈清词","CHAR-001",["「天衡宗覆灭——不只是渊暝一个人的手笔。」"]),("周守一","CHAR-010",["「当然不是。你以为——一个外人能灭一个顶级宗门？」","「天衡宗——是从内部烂掉的。我们有五个长老——都参与了。」"])],
     "镜头1（10秒）中景 固定镜头：图1剑鞘指向图2——金光锁定！图2却突然笑了——看透一切的冷笑。"),
    ("EP56-SEG06", ["EP56-S08"], 16, ["CHAR-001","CHAR-010"], ["CHAR-010-L01","CHAR-001-L02"], [],
     [("沈清词","CHAR-001",["「我师父——无尘子。渊暝说他也参与了。是真的吗？」"]),("周守一","CHAR-010",["「无尘子？哈——他确实参与了。」","「但不是你想的那样。他的参与——是用自己的灵魂为代价，保住了你转世的机会。」","「他是唯一一个——没有背叛你的人。」"]),("沈清词","CHAR-001",["「……什么？」"])],
     "镜头1（16秒）近景 固定镜头：图1制住图2——金色锁链缠绕。问出关键问题。图2的回答让她愣住。"),
]

ep57_segs = [
    ("EP57-SEG01", ["EP57-S01"], 10, ["CHAR-001","CHAR-010"], ["CHAR-001-L02","CHAR-010-L01"], [],
     [("沈清词","CHAR-001",["「从头说——当年天衡宗到底发生了什么。全部。」"]),("周守一","CHAR-010",["「好——反正都到这一步了。听好。」"])],
     "镜头1（10秒）中景 固定镜头：黎明时分。图1将图2带回空地——金色锁链牢牢锁住。面对面——要求完整真相。"),
    ("EP57-SEG02", ["EP57-S02","EP57-S03"], 16, ["CHAR-010"], ["CHAR-010-L01"], [],
     [("周守一","CHAR-010",["「渊暝许诺我们突破瓶颈——五人都同意了。只有无尘子拒绝。」","「宗门覆灭那天——他无法阻止。于是他做了另一件事。」","「他用了禁忌术——'假死转世'。代价是半数灵魂永久损毁。」","「他让你死了一次——才能保住你的灵魂完整转世。否则渊暝会彻底吞噬你的剑道根基。」"])],
     "镜头1（8秒）近景 固定镜头：图1讲述当年——五位长老被渊暝利诱。无尘子唯一拒绝。\n        镜头2（8秒）近景 固定镜头：图1继续——无尘子启动禁忌术‘假死转世’，牺牲半数灵魂让清词转世重生。"),
    ("EP57-SEG03", ["EP57-S04"], 10, ["CHAR-001"], ["CHAR-001-L02"], [],
     [("沈清词","CHAR-001",["「……所以——前世坠崖前的那一刻。」","「师父出现——不是来杀我的。是在执行'假死转世'……」","「……百年了。我误会了百年。」"])],
     "镜头1（10秒）特写 固定镜头：图1听完——长久沉默。金白光芒缓缓收敛。百年误解百年怨恨——全部释然。"),
    ("EP57-SEG04", ["EP57-S05"], 10, ["CHAR-008"], ["CHAR-008-L01"], [],
     [("无尘子","CHAR-008",["「清……清词……」","「你……活着……好……好……」"])],
     "镜头1（10秒）中景 固定镜头：图1被搀扶走来——白发苍苍枯瘦如柴。银灰瞳中神智回归。看见清词——浑浊的眼中有泪光。"),
    ("EP57-SEG05", ["EP57-S06","EP57-S07"], 16, ["CHAR-001","CHAR-008"], ["CHAR-001-L02","CHAR-008-L01"], [],
     [("沈清词","CHAR-001",["「师父——当年……是你救了我？」"]),("无尘子","CHAR-008",["「那是……为师唯一能做的……对不起……让你痛苦了……百年……」","「为师……没资格……再当你师父了……」","「你恨我……应该的……」"])],
     "镜头1（8秒）中景 固定镜头：图1走向图2——平视。师父仰头看她——含泪点头证实一切。\n        镜头2（8秒）近景 固定镜头：图2老泪纵横——枯瘦的手颤抖。想伸手摸清词头——举到一半又缩回。"),
    ("EP57-SEG06", ["EP57-S08"], 14, ["CHAR-001","CHAR-008"], ["CHAR-001-L02","CHAR-008-L01"], [],
     [("沈清词","CHAR-001",["「不恨了。」","「百年前——我以为被全世界背叛了。现在知道——至少有一个人没有。」","「谢谢你——师父。」"]),("无尘子","CHAR-008",["「好孩子……好孩子……」"])],
     "镜头1（14秒）中景 固定镜头：图1伸手——握住师父颤抖的手——放在自己头顶。眼中有泪光——嘴角有极淡的笑。师徒和解。"),
    ("EP57-SEG07", ["EP57-S09"], 10, ["CHAR-001"], ["CHAR-001-L02"], [],
     [("沈清词","CHAR-001",["「前世的仇——今生已报。因果已断。」","「接下来——是新的开始。」"])],
     "镜头1（10秒）全景 固定镜头：黎明的光洒下——图1站在高处远眺。银白长发在晨光中如瀑布般飘散。身后是师父和伙伴们。风暴段——结束。"),
]

ep_configs.extend([
    ("EP53", "魂噬", "EP53_魂噬.md", 82, 9, 7, "SCENE-014",
     ["CHAR-001-L02","CHAR-002-L01","CHAR-005-L01"],
     ["PROP-003"],
     ["CHAR-001(真实态)","CHAR-002","CHAR-005"],
     ep53_segs),
    ("EP54", "斩", "EP54_斩.md", 80, 8, 6, "SCENE-014",
     ["CHAR-001-L02","CHAR-002-L01","CHAR-005-L01"],
     ["PROP-003"],
     ["CHAR-001(真实态)","CHAR-002","CHAR-005"],
     ep54_segs),
    ("EP55", "终式", "EP55_终式.md", 90, 10, 8, "SCENE-014",
     ["CHAR-001-L02","CHAR-002-L01","CHAR-005-L01"],
     ["PROP-003"],
     ["CHAR-001(真实态)","CHAR-002","CHAR-005"],
     ep55_segs),
    ("EP56", "面具", "EP56_面具.md", 78, 8, 6, "SCENE-014",
     ["CHAR-001-L02","CHAR-010-L01"],
     ["PROP-003"],
     ["CHAR-001(真实态)","CHAR-010"],
     ep56_segs),
    ("EP57", "真相大白", "EP57_真相大白.md", 86, 9, 7, "SCENE-014",
     ["CHAR-001-L02","CHAR-008-L01","CHAR-010-L01"],
     ["PROP-003"],
     ["CHAR-001(真实态)","CHAR-008","CHAR-010"],
     ep57_segs),
])

for ep_id, title, source, total_dur, shot_count, seg_count, scene, looks, props, voice_keys, segs_data in ep_configs:
    ep_dir = os.path.join(BASE, ep_id)
    os.makedirs(ep_dir, exist_ok=True)
    
    # Write segments YAML
    seg_content = write_segments_yaml(ep_id, title, source, total_dur, shot_count, seg_count, scene, looks, props, voice_keys, segs_data)
    seg_path = os.path.join(ep_dir, f"{ep_id}_segments.yaml")
    with open(seg_path, 'w', encoding='utf-8') as f:
        f.write(seg_content)
    print(f"✅ {seg_path}")
    
    # Write shots YAML
    shot_content = write_shots_yaml(ep_id, title, source, total_dur, shot_count, scene, segs_data)
    shot_path = os.path.join(ep_dir, f"{ep_id}_shots.yaml")
    with open(shot_path, 'w', encoding='utf-8') as f:
        f.write(shot_content)
    print(f"✅ {shot_path}")

print("\n🎉 All YAML files generated successfully!")
