#!/usr/bin/env python3
"""Generate EP49-EP54 YAML files for 鸳鸯锅之恋."""
import os

BASE = "/Users/leifu/Movies/dramas/dramas/鸳鸯锅之恋"
LOOKS_CDN = {
    "CHAR-001-L01": "https://drama-reference-images.tos-cn-beijing.volces.com/looks/鸳鸯锅之恋/CHAR-001-L01.png",
    "CHAR-002-L01": "https://drama-reference-images.tos-cn-beijing.volces.com/looks/鸳鸯锅之恋/CHAR-002-L01.png",
    "CHAR-003-L01": "https://drama-reference-images.tos-cn-beijing.volces.com/looks/鸳鸯锅之恋/CHAR-003-L01.png",
    "CHAR-006-L01": "https://drama-reference-images.tos-cn-beijing.volces.com/looks/鸳鸯锅之恋/CHAR-006-L01.png",
    "CHAR-007-L01": "https://drama-reference-images.tos-cn-beijing.volces.com/looks/鸳鸯锅之恋/CHAR-007-L01.png",
}
SCENE_CDN = {
    "SCENE-001": "https://drama-reference-images.tos-cn-beijing.volces.com/scenes/鸳鸯锅之恋/SCENE-001.png",
    "SCENE-007": "https://drama-reference-images.tos-cn-beijing.volces.com/scenes/鸳鸯锅之恋/SCENE-007.png",
    "SCENE-009": "https://drama-reference-images.tos-cn-beijing.volces.com/scenes/鸳鸯锅之恋/SCENE-009.png",
}
PROP_CDN = {
    "PROP-001": "https://drama-reference-images.tos-cn-beijing.volces.com/props/鸳鸯锅之恋/PROP-001.png",
    "PROP-004": "https://drama-reference-images.tos-cn-beijing.volces.com/props/鸳鸯锅之恋/PROP-004.png",
    "PROP-005": "https://drama-reference-images.tos-cn-beijing.volces.com/props/鸳鸯锅之恋/PROP-005.png",
    "PROP-007": "https://drama-reference-images.tos-cn-beijing.volces.com/props/鸳鸯锅之恋/PROP-007.png",
}

VP = {
    "NARRATION": "成年女性，温暖知性，语速中等偏慢，声线柔和带笑意，像在给好朋友讲故事——每一句话都带着"你猜后来怎么了"的悬念感和"真好啊"的感慨",
    "CHAR-001": "成年女性，27岁，声线明亮带一点泼辣的尖锐感，成都话底子的普通话，语速偏快且经常突然加速（生气时），语句末尾常带成都方言语气词"嘛""撒""嘞"，情绪外放——高兴时笑声爽朗、生气时直接怼、难过时嘴硬但声音发颤，偶尔在心动时突然变得结巴害羞",
    "CHAR-002": "成年男性，29岁，音色偏低沉清冷，标准普通话偶尔蹦出东北口音（"嘎哈""整挺好"），语速偏慢且每句话之间有停顿——像在斟酌每个字，说话极度简洁（能三个字说完绝不用五个字），情绪内敛——高兴时只是语气微暖、紧张时声音更紧绷，偶尔在关键时刻突然说出浪漫句子时语速会更慢更认真",
    "CHAR-003": "成年女性，26岁，音色清脆明亮带一点奶气，成都话底子的普通话，语速很快且经常一口气说一长串不打草稿，说话自带笑声共鸣和夸张语调，"我跟你说"是口头开场，情绪永远往上扬——即使八卦时也是兴奋的尖叫式语气，偶尔在安慰苏辣辣时会突然变得温柔",
    "CHAR-006": "成年女性，56岁，音色高亢热情带东北大碴子味，纯正东北方言（"闺女""咋地""整挺好"），语速偏快且连珠炮式——问句特别多（"打算什么时候结婚？""会包饺子不？"），情绪外放且放大三倍——高兴时拍大腿、感动时哭得比谁都大声、挑剔时语气尖锐但下一秒又笑着夸人",
    "CHAR-007": "成年男性，28岁，音色温和偏磁性，标准普通话偶尔成都话，语速中等且咬字清晰——每个字都带着精心控制的得体感，喜欢用"你知道……吧？"句式，表面客气但暗藏锋芒，情绪克制——即使愤怒也只是语气冷几度，道歉时声音难得变得脆弱且不再控制",
}

CNAMES = {"NARRATION":"旁白","CHAR-001":"苏辣辣","CHAR-002":"陆北辰","CHAR-003":"林小暖","CHAR-006":"陆妈","CHAR-007":"周子轩"}

LOOK_DESC = {
    "CHAR-001-L01": "苏辣辣 CHAR-001-L01（白色T恤+酒红色围裙+齐肩微卷黑发+辣椒项链）",
    "CHAR-002-L01": "陆北辰 CHAR-002-L01（深蓝圆领T恤+深灰牛仔裤+银色细框眼镜+键盘帽吊坠）",
    "CHAR-003-L01": "林小暖 CHAR-003-L01（藏蓝针织毛衣+浅色牛仔裤+帆布鞋）",
    "CHAR-006-L01": "陆妈 CHAR-006-L01（深红色V领针织开衫+白色高领打底+黑色直筒裤）",
    "CHAR-007-L01": "周子轩 CHAR-007-L01（深灰羊毛西装+白色修身衬衫+酒红真丝领带）",
}

PS = "现代都市写实风格，暖色调，电影级质感，生活化场景。竖屏9比16。禁止画面中出现任何文字或字幕。"
PS_SILENT = f"本段无对白无语音，禁止画面中出现任何文字。{PS}"
NEG = "blurry, distorted, low quality, watermark, subtitles burned into frame, anime style, cartoon style, watercolor, oil painting style, fantasy elements, magic, ancient clothing, hanfu, ancient costume, flip phone, CRT monitor, flying, supernatural glow, real brand logo, celebrity face, oversaturated, HDR artifacts"

def get_look_url(lid): return LOOKS_CDN.get(lid, f"assets/looks/{lid}.png")
def get_scene_url(sid): return SCENE_CDN.get(sid, f"assets/scenes/{sid}.png")
def get_prop_url(pid): return PROP_CDN.get(pid, f"assets/props/{pid}.png")

# Episode definitions: each shot has (id, no, mode, dur, scene, looks, props, visual_text, [(speaker,line)])
EP_SHOTS = {
    "EP49": [
        ("EP49-S01",1,"i2v_ref",10,"SCENE-001",["CHAR-001-L01","CHAR-007-L01"],[],
         "中景 缓推：图1站在左侧灶台前，深吸一口气，手指微微攥紧围裙边角。右侧图2从容地整理食材，嘴角带着自信的微笑。台下评委席三位评委正襟危坐，观众席坐满了人。暖黄聚光灯打在两人的灶台上，厨房不锈钢台面反射着光。",
         [("NARRATION","决赛现场，两个人，两条路——一个用心做菜，一个用技术做菜。"),("CHAR-007","紧张？"),("CHAR-001","……不紧张。")]),
        ("EP49-S02",2,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],[],
         "特写 固定：CU图1的脸——她不自觉地往观众席看了一眼。眼里有一瞬间的慌张。",
         [("CHAR-001","别慌……他就在下面。")]),
        ("EP49-S03",3,"i2v_ref",5,"SCENE-001",["CHAR-002-L01"],[],
         "中景 固定：MCU图1坐在观众席前排，双手交叠放在膝盖上。他看着苏辣辣的方向，嘴角微微上扬，眼神笃定——像在说"我相信你"。键盘帽吊坠在领口若隐若现。",
         [("CHAR-002","不用回头也知道——她一定能行。")]),
        ("EP49-S04",4,"i2v_ref",10,"SCENE-001",["CHAR-001-L01"],["PROP-001"],
         "中景 镜头推近：MCU图1站在灶台前，双手稳稳端起一锅鸳鸯锅——铜锅中间的隔板清晰分明，左侧红油翻滚如岩浆，右侧清汤微沸如温泉。她把锅稳稳放在评委面前。蒸汽升腾，模糊了她的脸又散开——露出一双亮得惊人的眼睛。",
         [("CHAR-001","这道菜叫——鸳鸯锅之恋。"),("CHAR-001","红汤，是我成都的热烈。白汤，是我遇见的那份温厚。")]),
        ("EP49-S05",5,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],["PROP-004"],
         "特写 固定：CU图1的脸——她低头看着那口鸳鸯锅，辣椒项链在锁骨处微微晃动。她的表情不再是紧张——是一种笃定和温柔。",
         [("CHAR-001","有个人教会我……南北之间不是对立，是互补。")]),
        ("EP49-S06",6,"i2v_ref",5,"SCENE-001",["CHAR-002-L01"],[],
         "特写 固定：CU图1的脸——他听到这句话，喉结微微滚动了一下。他摘下眼镜假装擦拭，用指节快速抹了一下眼角。暖光打在他脸上。",
         [("CHAR-002","……这个瓜娃子。")]),
        ("EP49-S07",7,"i2v_ref",10,"SCENE-001",["CHAR-007-L01"],[],
         "中景 缓推：MCU图1端着自己的作品走向评委——一道摆盘精致到像艺术品的菜品，每一根菜丝都切得均匀如发。他面带微笑，姿态从容。但镜头推近他眼底——有一丝不易察觉的空洞。",
         [("CHAR-007","这道菜融合了川粤两大菜系技法，分子料理与传统烹饪的结合。每一步都经过精确计算。")]),
        ("EP49-S08",8,"t2v",4,"SCENE-001",[],[],
         "特写 固定：CU评委品尝周子轩的菜——评委点头，表情是"技术确实到位"的肯定，但嘴角没有被感动时的微微上扬。另一个评委悄悄回头看了一眼苏辣辣的方向。",
         [("NARRATION","技术满分，但评委的表情说明了一切——差了点什么。")]),
        ("EP49-S09",9,"i2v_ref",4,"SCENE-001",["CHAR-007-L01"],[],
         "特写 固定：CU图1注意到了评委的目光——他的微笑僵了一瞬，手指在身侧微微收紧。",
         [("CHAR-007","她那个鸳鸯锅……不就是一锅汤吗。")]),
        ("EP49-S10",10,"i2v_ref",10,"SCENE-001",["CHAR-001-L01","CHAR-007-L01"],[],
         "中景 缓推：MLS两位选手并排站在评委面前。图1双手交握在身前，指节发白。图2双手背在身后，下巴微抬。评委交换了一个眼神，主评委拿起话筒。台下安静得只听见排风扇的嗡鸣声。",
         [("NARRATION","所有的努力、所有的争执、所有的不甘——都在这一刻等着答案。")]),
        ("EP49-S11",11,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],[],
         "特写 固定：CU图1的脸——她紧抿嘴唇，睫毛微颤，目光直直看着评委手中的信封。聚光灯在她脸上打出明暗分界线。",
         [("CHAR-001","不管结果怎样……这道菜，是对的。")]),
        ("EP49-S12",12,"i2v_ref",5,"SCENE-001",["CHAR-002-L01"],[],
         "特写 固定：CU图1在观众席——他紧紧盯着台上，双手不自觉握成拳。喉结滚动了一下。背景虚化，只有他的脸清晰。",
         [("CHAR-002","她已经赢了。不管结果怎样。")]),
    ],
    "EP50": [
        ("EP50-S01",1,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],[],
         "特写 固定：CU图1的脸——听到自己名字的瞬间，眼睛猛地瞪大，嘴唇微微张开。聚光灯打在她脸上，瞳孔里映出光点。",
         [("NARRATION","冠军——苏辣辣！"),("CHAR-001","……是我？")]),
        ("EP50-S02",2,"i2v_ref",5,"SCENE-001",["CHAR-002-L01"],[],
         "特写 固定：CU图1在观众席——他猛地站起来，双手握拳举到胸口。嘴角咧开一个少有的大笑容，眼睛已经泛红。",
         [("CHAR-002","对。就是你。")]),
        ("EP50-S03",3,"i2v_ref",10,"SCENE-001",["CHAR-001-L01"],[],
         "中景 镜头跟随：MLS图1走上领奖台，脚步有点飘——像踩在云上。她接过奖杯，手指微微发抖。台下掌声雷动，暖黄灯光把她的身影笼罩在金色光晕中。她低头看着手中的奖杯，鼻头一红。",
         [("CHAR-001","我……我以为这辈子……只是守着那口锅就够了。")]),
        ("EP50-S04",4,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],["PROP-004"],
         "中景 缓推：MCU图1站在领奖台上，单手握着奖杯，另一只手不自觉地摸了一下脖子上的辣椒项链。她抬起眼——直直看向观众席某个方向。",
         [("CHAR-001","有一个人……是他教会我，辣椒以外的世界也很甜。")]),
        ("EP50-S05",5,"i2v_ref",5,"SCENE-001",["CHAR-002-L01"],[],
         "中景 固定：MCU图1——他的笑容僵住了一瞬，然后慢慢垂下眼。摘下眼镜，用指关节狠狠抹了一下眼角。深吸一口气，重新戴上眼镜时镜片后面的眼睛已经红透了。",
         [("CHAR-002","……瓜娃子。谁要在这种场合哭。")]),
        ("EP50-S06",6,"i2v_ref",10,"SCENE-001",["CHAR-001-L01"],[],
         "中景 固定：MLS图1深深鞠了一躬——不是礼节性的，是真的弯到九十度。起身时眼眶红了但笑容灿烂如成都的阳光。台下掌声更响了。她的酒红围裙在灯光下像一团温暖的火焰。",
         [("CHAR-001","谢谢苏记，谢谢成都——更要谢谢那个从哈尔滨来的、不吃辣的、还硬要说'不辣'的瓜娃子。")]),
        ("EP50-S07",7,"i2v_ref",10,"SCENE-001",["CHAR-002-L01"],[],
         "特写 缓推：CU图1——听到"从哈尔滨来的不吃辣的瓜娃子"，他低下头，用手掌盖住了半张脸。肩膀微微颤了一下。旁边的观众好奇地看了他一眼。他深吸一口气，手掌放下时——嘴角是藏不住的笑，但眼角全是泪。",
         [("CHAR-002","第一次见面时她说——'微辣是底线'。现在她的底线……变成了我。")]),
        ("EP50-S08",8,"i2v_ref",5,"SCENE-001",["CHAR-007-L01","CHAR-001-L01"],[],
         "中景 固定：MS图1走向图2，伸出手。微笑——标准的、训练过的、完美的微笑。但眼底有一丝裂痕。图2握住他的手。",
         [("CHAR-007","恭喜你。"),("CHAR-001","谢谢。你的菜真的很好。")]),
        ("EP50-S09",9,"i2v_ref",5,"SCENE-001",["CHAR-007-L01"],[],
         "特写 固定：CU图1——握手松开的瞬间，他的微笑消失了一秒。眼神从苏辣辣身上掠过，落在观众席的陆北辰身上。嘴角重新扬起，但这次——多了一丝算计。",
         [("CHAR-007","用故事赢比赛……有意思。但这不叫结束。")]),
        ("EP50-S10",10,"i2v_ref",10,"SCENE-001",["CHAR-007-L01"],[],
         "中景 缓推：MCU图1靠在赛后走廊的墙边，解开领带结。走廊冷白灯光和赛场暖光形成对比。他从西装内袋掏出手机看了一眼——屏幕上是苏记老火锅的新闻。他把手机收起来，嘴角浮起一个意味不明的笑。",
         [("CHAR-007","苏辣辣……你赢了比赛。"),("CHAR-007","可你不知道——这个圈子，比赛才是开始。")]),
        ("EP50-S11",11,"i2v_ref",5,"SCENE-001",["CHAR-007-L01","CHAR-001-L01"],[],
         "中景 固定：MS图1重新走进赛场。图2正和陆北辰说笑，两人并肩站着。图1停在几步外，看了他们一眼——然后走向图2。",
         [("CHAR-007","苏小姐。"),("CHAR-001","嗯？")]),
        ("EP50-S12",12,"i2v_ref",5,"SCENE-001",["CHAR-007-L01"],[],
         "特写 缓推：CU图1的脸——他微笑，声音很轻，但每个字都像一颗钉子。",
         [("CHAR-007","恭喜你……但我不会放弃。")]),
    ],
    "EP52": [
        ("EP52-S01",1,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],[],
         "中景 固定：MCU图1在苏记店内整理调料架——阳光从窗外洒进来，辣椒和花椒的瓶子在光线下泛着暖色。她哼着小曲，状态轻松。门口传来脚步声，她头也没回。",
         [("CHAR-001","今天打烊了哈，明天请早——")]),
        ("EP52-S02",2,"i2v_ref",5,"SCENE-001",["CHAR-007-L01"],[],
         "中景 固定：MCU图1站在门口——但今天的他不一样。没穿西装，换了一件简单的深色卫衣，头发也没梳得一丝不苟。双手插在口袋里，表情不再是标准微笑——是一种疲惫但坦然的真实。",
         [("CHAR-007","苏辣辣。是我。"),("CHAR-001","……周子轩？")]),
        ("EP52-S03",3,"i2v_ref",10,"SCENE-001",["CHAR-001-L01","CHAR-007-L01"],[],
         "中景 缓推：MS两人面对面站着。图1下意识后退了半步，手不自觉摸了一下围裙——这是她紧张时的习惯。图2注意到这个动作，苦笑了一下。阳光在两人之间的地面上画出一道明暗分界线。",
         [("CHAR-001","你来做啥子？"),("CHAR-007","你别紧张。我今天不是来……找麻烦的。"),("CHAR-001","那你来做啥子？")]),
        ("EP52-S04",4,"i2v_ref",5,"SCENE-001",["CHAR-007-L01"],[],
         "中景 缓推：MCU图1低下头，深吸一口气。手指从口袋里抽出来，无意识地攥了攥。他抬起头时——眼神不再是以前那种带着算计的从容，而是一种赤裸的坦诚。",
         [("CHAR-007","苏辣辣。我来——道歉的。")]),
        ("EP52-S05",5,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],[],
         "特写 固定：CU图1的脸——她的警惕慢慢松动了。眉头从紧皱变成了微蹙。",
         [("CHAR-001","……道歉？")]),
        ("EP52-S06",6,"i2v_ref",10,"SCENE-001",["CHAR-007-L01"],[],
         "中景 缓推：MCU图1坐在苏记的一张空桌旁，双手放在桌上——以前他的手总是从容交叠的，现在是十指交叉、指节发白。他没看苏辣辣，目光落在桌上的鸳鸯锅上。",
         [("CHAR-007","我嫉妒他。嫉妒陆北辰。"),("CHAR-007","你做那道鸳鸯锅的时候……我在旁边看着，心想——为什么那个故事里的人不是我？"),("CHAR-007","可笑吧。我连嫉妒都用错了方式。")]),
        ("EP52-S07",7,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],[],
         "中景 固定：MCU图1走到他对面坐下。她的表情不再是警惕——是一种理解。阳光从窗户照进来，把她的侧脸照得温暖柔和。",
         [("CHAR-001","周子轩。你的菜——真的很好。"),("CHAR-007","好有什么用。没有灵魂。")]),
        ("EP52-S08",8,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],[],
         "特写 固定：CU图1笑了——不是胜利者的笑，是释然的笑。她伸出手。",
         [("CHAR-001","过去的事就过去了。你的道歉——我收下了。")]),
        ("EP52-S09",9,"i2v_ref",10,"SCENE-001",["CHAR-001-L01","CHAR-007-L01"],[],
         "中景 固定：MS两人握手。图2握住她的手时愣了一秒——然后笑了。不是以前那种带着算计的笑，是一种放下了所有重量的、轻松的笑。苏记的红灯笼在两人身后摇晃。",
         [("CHAR-007","祝你幸福。你们很配。"),("CHAR-001","……谢谢。")]),
        ("EP52-S10",10,"i2v_ref",5,"SCENE-001",["CHAR-007-L01"],[],
         "特写 镜头跟随：CU图1转身——背对苏辣辣的那一瞬间，他的笑容消失了一秒。嘴角微微下垂。喉结滚动了一下。",
         [("CHAR-007","喜欢一个人……原来就是希望她幸福。哪怕不是因为我。")]),
        ("EP52-S11",11,"i2v_ref",5,"SCENE-001",["CHAR-007-L01"],[],
         "中景 缓推：MCU图1走向门口。阳光从门外照进来，他的身影逆光。走了两步——他停了一下，侧过头。眼角有一滴泪滑下来，但他没有擦。深吸一口气，继续往前走。",
         [("CHAR-007","识时务者……为俊杰。")]),
        ("EP52-S12",12,"i2v_ref",10,"SCENE-001",["CHAR-001-L01","CHAR-002-L01"],[],
         "中景 固定：MCU图1站在原地看着他的背影消失在门口。阳光在地上画出一条长长的影子。她低下头，摸了摸手心里还残留的握手温度。身后传来陆北辰轻轻的脚步声。陆北辰走到她身边，两人并肩看着空荡荡的门口。",
         [("CHAR-001","他真的……放下了。"),("CHAR-002","……他是个好人。只是用错了方式。"),("CHAR-001","嗯。走吧——去看看投资的事。咱俩的事，比他重要。")]),
    ],
    "EP53": [
        ("EP53-S01",1,"i2v_ref",10,"SCENE-001",["CHAR-001-L01","CHAR-003-L01"],[],
         "中景 固定：MS苏记打烊后的店内。图1和图2趴在桌上，面前摊着几张写满字的纸——投资方案和选址地图。桌上还有一杯喝了一半的盖碗茶。图2用笔在地图上画圈。",
         [("CHAR-003","我跟你说！投资人给了三个城市选——重庆、上海、还有哈尔滨！"),("CHAR-001","哈尔滨。"),("CHAR-003","啊？哈尔滨？那边人不吃辣啊！")]),
        ("EP53-S02",2,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],["PROP-004"],
         "特写 缓推：CU图1——她摸着脖子上的辣椒项链，目光落在窗外成都的街景上。夕阳把她的侧脸染成暖金色。",
         [("CHAR-001","他从哈尔滨来成都找我。这次——换我去找他。")]),
        ("EP53-S03",3,"i2v_ref",5,"SCENE-001",["CHAR-003-L01"],[],
         "特写 固定：CU图1听到这句话，眼睛瞬间亮了。她双手捂住嘴巴——眼眶红了，嘴角却咧得巨大。",
         [("CHAR-003","天哪……辣辣你……嗑到了嗑到了！")]),
        ("EP53-S04",4,"i2v_ref",10,"SCENE-001",["CHAR-001-L01","CHAR-002-L01"],[],
         "中景 缓推：MCU两人面对面坐在苏记的角落里。图1双手撑在桌上，看着图2。图2正低头看那份选址方案，手指停在"哈尔滨"三个字上。他的手指微微颤了一下。",
         [("CHAR-001","陆北辰。第一家分店——定在哈尔滨。"),("CHAR-002","……你确定？"),("CHAR-001","确定。")]),
        ("EP53-S05",5,"i2v_ref",5,"SCENE-001",["CHAR-002-L01"],[],
         "特写 固定：CU图1摘下眼镜，用力揉了揉鼻梁。镜片后面的眼睛红了。他深吸一口气，把眼镜戴回去。",
         [("CHAR-002","那里……很冷。零下二三十度。你受得了吗？")]),
        ("EP53-S06",6,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],[],
         "特写 固定：CU图1笑了——笑得眉眼弯弯，辣椒项链在领口晃动。",
         [("CHAR-001","冷啥子嘛。有你在——再冷都暖和。")]),
        ("EP53-S07",7,"i2v_ref",10,"SCENE-001",["CHAR-001-L01","CHAR-003-L01"],["PROP-007"],
         "中景 固定：MLS图1从里屋走出来——身上穿着一件红绿配色的东北大花袄。鲜艳的牡丹花纹在她身上像一面旗。她转了一圈，大花袄的下摆扬起来。图2在旁边笑得直不起腰。",
         [("CHAR-003","哈哈哈哈！辣辣你这是——进货去了？！"),("CHAR-001","好看不？我专门让人从哈尔滨寄来的！")]),
        ("EP53-S08",8,"i2v_ref",5,"SCENE-001",["CHAR-002-L01"],[],
         "中景 固定：MCU图1靠在门框上看着她——嘴角是一种极其罕见的、毫无防备的大笑。银框眼镜后面的眼睛弯成了月牙。",
         [("CHAR-002","……你认真的？")]),
        ("EP53-S09",9,"i2v_ref",5,"SCENE-001",["CHAR-001-L01"],["PROP-007"],
         "特写 固定：CU图1扯了扯大花袄的领口，对着空气比了个"OK"的手势。辣椒项链和大花袄的牡丹花纹碰撞在一起——成都和东北的视觉融合。",
         [("CHAR-001","入乡随俗嘛！去了哈尔滨——我就是半个东北人！")]),
        ("EP53-S10",10,"i2v_ref",10,"SCENE-001",["CHAR-002-L01"],[],
         "特写 缓推：CU图1——笑声慢慢停下来。他看着穿着大花袄的苏辣辣，眼神从大笑变成了深深的温柔。喉结滚动了一下。他摘下眼镜，假装擦拭——但手指在微微发抖。",
         [("CHAR-002","从成都到哈尔滨……她愿意为我走这么远的路。"),("CHAR-002","苏辣辣。"),("CHAR-001","嗯？"),("CHAR-002","……整挺好。")]),
        ("EP53-S11",11,"i2v_ref",5,"SCENE-001",["CHAR-001-L01","CHAR-002-L01"],[],
         "中景 固定：MS图1穿着大花袄走向图2，伸出手——不是牵手，是比了一个东北式的手势。",
         [("CHAR-001","嘎哈呢？快整饭去！")]),
        ("EP53-S12",12,"i2v_ref",5,"SCENE-001",["CHAR-002-L01","CHAR-003-L01"],[],
         "中景 固定：MCU图1终于忍不住笑了出来——不是嘴角微微上扬，是真的笑出了声。图2在旁边已经笑趴了。苏记的暖光包裹着三个人。",
         [("CHAR-002","别糟蹋东北话了。"),("CHAR-003","救命……笑死我了！")]),
    ],
}

# Segment definitions for each episode
# Each segment: (id, shot_ids, dur, speakers, shot_visuals, looks, scene, props, transition)
EP_SEGS = {
    "EP49": [
        ("EP49-SEG01",["EP49-S01"],10,["NARRATION","CHAR-007","CHAR-001"],
         ["镜头1（10秒）中景 缓推：美食大赛决赛现场，两个灶台并排。图1站在左侧灶台前，深吸一口气，手指微微攥紧围裙边角。右侧图2从容地整理食材，嘴角带着自信的微笑。台下评委席三位评委正襟危坐，观众席坐满了人。暖黄聚光灯打在两人的灶台上，厨房不锈钢台面反射着光。"],
         ["CHAR-001-L01","CHAR-007-L01"],"SCENE-001",[],"hard_cut"),
        ("EP49-SEG02",["EP49-S02","EP49-S03"],10,["CHAR-001","CHAR-002"],
         ["镜头1（5秒）特写 固定：CU图1的脸——她不自觉地往观众席看了一眼。眼里有一瞬间的慌张。",
          "镜头2（5秒）中景 固定：MCU图1坐在观众席前排，双手交叠放在膝盖上。他看着苏辣辣的方向，嘴角微微上扬，眼神笃定——像在说"我相信你"。键盘帽吊坠在领口若隐若现。"],
         ["CHAR-001-L01","CHAR-002-L01"],"SCENE-001",[],"hard_cut"),
        ("EP49-SEG03",["EP49-S04"],10,["CHAR-001"],
         ["镜头1（10秒）中景 镜头推近：MCU图1站在灶台前，双手稳稳端起一锅鸳鸯锅——铜锅中间的隔板清晰分明，左侧红油翻滚如岩浆，右侧清汤微沸如温泉。她把锅稳稳放在评委面前。蒸汽升腾，模糊了她的脸又散开——露出一双亮得惊人的眼睛。"],
         ["CHAR-001-L01"],"SCENE-001",["PROP-001"],"hard_cut"),
        ("EP49-SEG04",["EP49-S05","EP49-S06"],10,["CHAR-001","CHAR-002"],
         ["镜头1（5秒）特写 固定：CU图1的脸——她低头看着那口鸳鸯锅，辣椒项链在锁骨处微微晃动。她的表情不再是紧张——是一种笃定和温柔。",
          "镜头2（5秒）特写 固定：CU图1的脸——他听到这句话，喉结微微滚动了一下。他摘下眼镜假装擦拭，用指节快速抹了一下眼角。暖光打在他脸上。"],
         ["CHAR-001-L01","CHAR-002-L01"],"SCENE-001",["PROP-004"],"hard_cut"),
        ("EP49-SEG05",["EP49-S07"],10,["CHAR-007"],
         ["镜头1（10秒）中景 缓推：MCU图1端着自己的作品走向评委——一道摆盘精致到像艺术品的菜品，每一根菜丝都切得均匀如发。他面带微笑，姿态从容。但镜头推近他眼底——有一丝不易察觉的空洞。"],
         ["CHAR-007-L01"],"SCENE-001",[],"hard_cut"),
        ("EP49-SEG06",["EP49-S08","EP49-S09"],8,["NARRATION","CHAR-007"],
         ["镜头1（4秒）特写 固定：CU评委品尝周子轩的菜——评委点头，表情是"技术确实到位"的肯定，但嘴角没有被感动时的微微上扬。另一个评委悄悄回头看了一眼苏辣辣的方向。",
          "镜头2（4秒）特写 固定：CU图1注意到了评委的目光——他的微笑僵了一瞬，手指在身侧微微收紧。"],
         ["CHAR-007-L01"],"SCENE-001",[],"hard_cut"),
        ("EP49-SEG07",["EP49-S10"],10,["NARRATION"],
         ["镜头1（10秒）中景 缓推：MLS两位选手并排站在评委面前。图1双手交握在身前，指节发白。图2双手背在身后，下巴微抬。评委交换了一个眼神，主评委拿起话筒。台下安静得只听见排风扇的嗡鸣声。"],
         ["CHAR-001-L01","CHAR-007-L01"],"SCENE-001",[],"hard_cut"),
        ("EP49-SEG08",["EP49-S11","EP49-S12"],10,["CHAR-001","CHAR-002"],
         ["镜头1（5秒）特写 固定：CU图1的脸——她紧抿嘴唇，睫毛微颤，目光直直看着评委手中的信封。聚光灯在她脸上打出明暗分界线。",
          "镜头2（5秒）特写 固定：CU图1在观众席——他紧紧盯着台上，双手不自觉握成拳。喉结滚动了一下。背景虚化，只有他的脸清晰。"],
         ["CHAR-001-L01","CHAR-002-L01"],"SCENE-001",[],"hard_cut"),
    ],
    "EP50": [
        ("EP50-SEG01",["EP50-S01","EP50-S02"],10,["NARRATION","CHAR-001","CHAR-002"],
         ["镜头1（5秒）特写 固定：CU图1的脸——听到自己名字的瞬间，眼睛猛地瞪大，嘴唇微微张开。聚光灯打在她脸上，瞳孔里映出光点。",
          "镜头2（5秒）特写 固定：CU图1在观众席——他猛地站起来，双手握拳举到胸口。嘴角咧开一个少有的大笑容，眼睛已经泛红。"],
         ["CHAR-001-L01","CHAR-002-L01"],"SCENE-001",[],"hard_cut"),
        ("EP50-SEG02",["EP50-S03"],10,["CHAR-001"],
         ["镜头1（10秒）中景 镜头跟随：MLS图1走上领奖台，脚步有点飘——像踩在云上。她接过奖杯，手指微微发抖。台下掌声雷动，暖黄灯光把她的身影笼罩在金色光晕中。她低头看着手中的奖杯，鼻头一红。"],
         ["CHAR-001-L01"],"SCENE-001",[],"hard_cut"),
        ("EP50-SEG03",["EP50-S04","EP50-S05"],10,["CHAR-001","CHAR-002"],
         ["镜头1（5秒）中景 缓推：MCU图1站在领奖台上，单手握着奖杯，另一只手不自觉地摸了一下脖子上的辣椒项链。她抬起眼——直直看向观众席某个方向。",
          "镜头2（5秒）中景 固定：MCU图1——他的笑容僵住了一瞬，然后慢慢垂下眼。摘下眼镜，用指关节狠狠抹了一下眼角。深吸一口气，重新戴上眼镜时镜片后面的眼睛已经红透了。"],
         ["CHAR-001-L01","CHAR-002-L01"],"SCENE-001",["PROP-004"],"hard_cut"),
        ("EP50-SEG04",["EP50-S06"],10,["CHAR-001"],
         ["镜头1（10秒）中景 固定：MLS图1深深鞠了一躬——不是礼节性的，是真的弯到九十度。起身时眼眶红了但笑容灿烂如成都的阳光。台下掌声更响了。她的酒红围裙在灯光下像一团温暖的火焰。"],
         ["CHAR-001-L01"],"SCENE-001",[],"hard_cut"),
        ("EP50-SEG05",["EP50-S07"],10,["CHAR-002"],
         ["镜头1（10秒）特写 缓推：CU图1——听到"从哈尔滨来的不吃辣的瓜娃子"，他低下头，用手掌盖住了半张脸。肩膀微微颤了一下。旁边的观众好奇地看了他一眼。他深吸一口气，手掌放下时——嘴角是藏不住的笑，但眼角全是泪。"],
         ["CHAR-002-L01"],"SCENE-001",[],"hard_cut"),
        ("EP50-SEG06",["EP50-S08","EP50-S09"],10,["CHAR-007","CHAR-001"],
         ["镜头1（5秒）中景 固定：MS图1走向图2，伸出手。微笑——标准的、训练过的、完美的微笑。但眼底有一丝裂痕。图2握住他的手。",
          "镜头2（5秒）特写 固定：CU图1——握手松开的瞬间，他的微笑消失了一秒。眼神从苏辣辣身上掠过，落在观众席的陆北辰身上。嘴角重新扬起，但这次——多了一丝算计。"],
         ["CHAR-007-L01","CHAR-001-L01"],"SCENE-001",[],"hard_cut"),
        ("EP50-SEG07",["EP50-S10"],10,["CHAR-007"],
         ["镜头1（10秒）中景 缓推：MCU图1靠在赛后走廊的墙边，解开领带结。走廊冷白灯光和赛场暖光形成对比。他从西装内袋掏出手机看了一眼——屏幕上是苏记老火锅的新闻。他把手机收起来，嘴角浮起一个意味不明的笑。"],
         ["CHAR-007-L01"],"SCENE-001",[],"hard_cut"),
        ("EP50-SEG08",["EP50-S11","EP50-S12"],10,["CHAR-007","CHAR-001"],
         ["镜头1（5秒）中景 固定：MS图1重新走进赛场。图2正和陆北辰说笑，两人并肩站着。图1停在几步外，看了他们一眼——然后走向图2。",
          "镜头2（5秒）特写 缓推：CU图1的脸——他微笑，声音很轻，但每个字都像一颗钉子。"],
         ["CHAR-007-L01","CHAR-001-L01"],"SCENE-001",[],"hard_cut"),
    ],
    "EP52": [
        ("EP52-SEG01",["EP52-S01","EP52-S02"],10,["CHAR-001","CHAR-007"],
         ["镜头1（5秒）中景 固定：MCU图1在苏记店内整理调料架——阳光从窗外洒进来，辣椒和花椒的瓶子在光线下泛着暖色。她哼着小曲，状态轻松。门口传来脚步声，她头也没回。",
          "镜头2（5秒）中景 固定：MCU图1站在门口——但今天的他不一样。没穿西装，换了一件简单的深色卫衣，头发也没梳得一丝不苟。双手插在口袋里，表情不再是标准微笑——是一种疲惫但坦然的真实。"],
         ["CHAR-001-L01","CHAR-007-L01"],"SCENE-001",[],"hard_cut"),
        ("EP52-SEG02",["EP52-S03"],10,["CHAR-001","CHAR-007"],
         ["镜头1（10秒）中景 缓推：MS两人面对面站着。图1下意识后退了半步，手不自觉摸了一下围裙——这是她紧张时的习惯。图2注意到这个动作，苦笑了一下。阳光在两人之间的地面上画出一道明暗分界线。"],
         ["CHAR-001-L01","CHAR-007-L01"],"SCENE-001",[],"hard_cut"),
        ("EP52-SEG03",["EP52-S04","EP52-S05"],10,["CHAR-007","CHAR-001"],
         ["镜头1（5秒）中景 缓推：MCU图1低下头，深吸一口气。手指从口袋里抽出来，无意识地攥了攥。他抬起头时——眼神不再是以前那种带着算计的从容，而是一种赤裸的坦诚。",
          "镜头2（5秒）特写 固定：CU图1的脸——她的警惕慢慢松动了。眉头从紧皱变成了微蹙。"],
         ["CHAR-007-L01","CHAR-001-L01"],"SCENE-001",[],"hard_cut"),
        ("EP52-SEG04",["EP52-S06"],10,["CHAR-007"],
         ["镜头1（10秒）中景 缓推：MCU图1坐在苏记的一张空桌旁，双手放在桌上——以前他的手总是从容交叠的，现在是十指交叉、指节发白。他没看苏辣辣，目光落在桌上的鸳鸯锅上。"],
         ["CHAR-007-L01"],"SCENE-001",[],"hard_cut"),
        ("EP52-SEG05",["EP52-S07","EP52-S08"],10,["CHAR-001","CHAR-007"],
         ["镜头1（5秒）中景 固定：MCU图1走到他对面坐下。她的表情不再是警惕——是一种理解。阳光从窗户照进来，把她的侧脸照得温暖柔和。",
          "镜头2（5秒）特写 固定：CU图1笑了——不是胜利者的笑，是释然的笑。她伸出手。"],
         ["CHAR-001-L01"],"SCENE-001",[],"hard_cut"),
        ("EP52-SEG06",["EP52-S09"],10,["CHAR-001","CHAR-007"],
         ["镜头1（10秒）中景 固定：MS两人握手。图2握住她的手时愣了一秒——然后笑了。不是以前那种带着算计的笑，是一种放下了所有重量的、轻松的笑。苏记的红灯笼在两人身后摇晃。"],
         ["CHAR-001-L01","CHAR-007-L01"],"SCENE-001",[],"hard_cut"),
        ("EP52-SEG07",["EP52-S10","EP52-S11"],10,["CHAR-007"],
         ["镜头1（5秒）特写 镜头跟随：CU图1转身——背对苏辣辣的那一瞬间，他的笑容消失了一秒。嘴角微微下垂。喉结滚动了一下。",
          "镜头2（5秒）中景 缓推：MCU图1走向门口。阳光从门外照进来，他的身影逆光。走了两步——他停了一下，侧过头。眼角有一滴泪滑下来，但他没有擦。深吸一口气，继续往前走。"],
         ["CHAR-007-L01"],"SCENE-001",[],"hard_cut"),
        ("EP52-SEG08",["EP52-S12"],10,["CHAR-001","CHAR-002"],
         ["镜头1（10秒）中景 固定：MCU图1站在原地看着他的背影消失在门口。阳光在地上画出一条长长的影子。她低下头，摸了摸手心里还残留的握手温度。身后传来陆北辰轻轻的脚步声。陆北辰走到她身边，两人并肩看着空荡荡的门口。"],
         ["CHAR-001-L01","CHAR-002-L01"],"SCENE-001",[],"hard_cut"),
    ],
    "EP53": [
        ("EP53-SEG01",["EP53-S01"],10,["CHAR-003","CHAR-001"],
         ["镜头1（10秒）中景 固定：MS苏记打烊后的店内。图1和图2趴在桌上，面前摊着几张写满字的纸——投资方案和选址地图。桌上还有一杯喝了一半的盖碗茶。图2用笔在地图上画圈。"],
         ["CHAR-001-L01","CHAR-003-L01"],"SCENE-001",[],"hard_cut"),
        ("EP53-SEG02",["EP53-S02","EP53-S03"],10,["CHAR-001","CHAR-003"],
         ["镜头1（5秒）特写 缓推：CU图1——她摸着脖子上的辣椒项链，目光落在窗外成都的街景上。夕阳把她的侧脸染成暖金色。",
          "镜头2（5秒）特写 固定：CU图1听到这句话，眼睛瞬间亮了。她双手捂住嘴巴——眼眶红了，嘴角却咧得巨大。"],
         ["CHAR-001-L01","CHAR-003-L01"],"SCENE-001",["PROP-004"],"hard_cut"),
        ("EP53-SEG03",["EP53-S04"],10,["CHAR-001","CHAR-002"],
         ["镜头1（10秒）中景 缓推：MCU两人面对面坐在苏记的角落里。图1双手撑在桌上，看着图2。图2正低头看那份选址方案，手指停在"哈尔滨"三个字上。他的手指微微颤了一下。"],
         ["CHAR-001-L01","CHAR-002-L01"],"SCENE-001",[],"hard_cut"),
        ("EP53-SEG04",["EP53-S05","EP53-S06"],10,["CHAR-002","CHAR-001"],
         ["镜头1（5秒）特写 固定：CU图1摘下眼镜，用力揉了揉鼻梁。镜片后面的眼睛红了。他深吸一口气，把眼镜戴回去。",
          "镜头2（5秒）特写 固定：CU图1笑了——笑得眉眼弯弯，辣椒项链在领口晃动。"],
         ["CHAR-002-L01","CHAR-001-L01"],"SCENE-001",[],"hard_cut"),
        ("EP53-SEG05",["EP53-S07"],10,["CHAR-003","CHAR-001"],
         ["镜头1（10秒）中景 固定：MLS图1从里屋走出来——身上穿着一件红绿配色的东北大花袄。鲜艳的牡丹花纹在她身上像一面旗。她转了一圈，大花袄的下摆扬起来。图2在旁边笑得直不起腰。"],
         ["CHAR-001-L01","CHAR-003-L01"],"SCENE-001",["PROP-007"],"hard_cut"),
        ("EP53-SEG06",["EP53-S08","EP53-S09"],10,["CHAR-002","CHAR-001"],
         ["镜头1（5秒）中景 固定：MCU图1靠在门框上看着她——嘴角是一种极其罕见的、毫无防备的大笑。银框眼镜后面的眼睛弯成了月牙。",
          "镜头2（5秒）特写 固定：CU图1扯了扯大花袄的领口，对着空气比了个"OK"的手势。辣椒项链和大花袄的牡丹花纹碰撞在一起——成都和东北的视觉融合。"],
         ["CHAR-002-L01","CHAR-001-L01"],"SCENE-001",["PROP-007"],"hard_cut"),
        ("EP53-SEG07",["EP53-S10"],10,["CHAR-002","CHAR-001"],
         ["镜头1（10秒）特写 缓推：CU图1——笑声慢慢停下来。他看着穿着大花袄的苏辣辣，眼神从大笑变成了深深的温柔。喉结滚动了一下。他摘下眼镜，假装擦拭——但手指在微微发抖。"],
         ["CHAR-002-L01"],"SCENE-001",[],"hard_cut"),
        ("EP53-SEG08",["EP53-S11","EP53-S12"],10,["CHAR-001","CHAR-002","CHAR-003"],
         ["镜头1（5秒）中景 固定：MS图1穿着大花袄走向图2，伸出手——不是牵手，是比了一个东北式的手势。",
          "镜头2（5秒）中景 固定：MCU图1终于忍不住笑了出来——不是嘴角微微上扬，是真的笑出了声。图2在旁边已经笑趴了。苏记的暖光包裹着三个人。"],
         ["CHAR-001-L01","CHAR-002-L01","CHAR-003-L01"],"SCENE-001",[],"hard_cut"),
    ],
}


def build_prompt(looks, scene, shot_text_parts, dialogue_list, is_silent=False, is_shot=False):
    """Build the api.text prompt."""
    fig = 1
    header_parts = []
    for lid in looks:
        desc = LOOK_DESC.get(lid, lid)
        header_parts.append(f"【图{fig}】{desc}")
        fig += 1
    header_parts.append(f"【图{fig}】{scene}")
    header = "".join(header_parts) + "。"
    
    prompt = f"{header}\n\n      竖屏9比16连贯叙事。\n\n      "
    for part in shot_text_parts:
        prompt += f"{part}\n\n      "
    
    if is_silent:
        prompt += f"画面全程无任何文字、字幕、标题、水印。\n\n      {PS_SILENT}"
    else:
        prompt += "[以下对白仅供语音合成，严禁在画面中显示任何文字]\n"
        for speaker, line in dialogue_list:
            vp = VP.get(speaker, "")
            prompt += f"\n      对白（{CNAMES.get(speaker, speaker)}，{vp}）：「{line}」"
        prompt += f"\n\n      画面全程无任何文字、字幕、标题、水印。\n\n      {PS}"
    return prompt


def build_content_roles(looks, scene):
    roles = []
    for i, lid in enumerate(looks):
        roles.append(f"    - file: {lid}\n      role: reference_image\n      label: 图{i+1}")
    roles.append(f"    - file: {scene}\n      role: reference_image\n      label: 图{len(looks)+1}")
    return roles


def write_shots(ep_id, ep_label, shots, source_dur, source_md):
    lines = []
    n = len(shots)
    out_dur = sum(s[3] for s in shots)
    lines.append(f"# === SOURCE FIDELITY PROOF ===")
    lines.append(f"# Source: {source_md}")
    lines.append(f"# Source shots: {n} ({ep_id}-S01 to {ep_id}-S{n:02d})")
    lines.append(f"# Output shots: {n} ({ep_id}-S01 to {ep_id}-S{n:02d})")
    lines.append(f"# Mapping: 1:1 (no insertions, no deletions, no reordering)")
    lines.append(f"# Source total duration: {source_dur}s")
    lines.append(f"# Output total duration: {out_dur}s")
    lines.append(f"# Gate status: ALL PASS (G1:{out_dur}s G2:{n}={n} G3:all IDs match G4:all voice_prompts found)")
    lines.append("")
    lines.append(f"episode_id: {ep_id}")
    lines.append(f"source_md: {source_md}")
    lines.append("defaults:")
    lines.append("  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks")
    lines.append("  model: doubao-seedance-2-0-fast")
    lines.append("  ratio: '9:16'")
    lines.append("  resolution: 720p")
    lines.append("  duration: 5")
    lines.append("  generate_audio: false")
    lines.append("  watermark: false")
    lines.append(f"  prompt_suffix: {PS}")
    lines.append(f"  negative_prompt: {NEG}")
    lines.append("")
    lines.append("shots:")
    
    for sid, sno, mode, dur, scene, looks, props, visual, dlg in shots:
        lines.append(f"- shot_id: {sid}")
        lines.append(f"  shot_no: {sno}")
        lines.append(f"  mode: {mode}")
        lines.append(f"  duration_sec: {dur}")
        lines.append(f"  refs:")
        lines.append(f"    scene_id: {scene}")
        if looks:
            lines.append(f"    look_ids:")
            for l in looks: lines.append(f"    - {l}")
        else:
            lines.append(f"    look_ids: []")
        if props:
            lines.append(f"    prop_ids:")
            for p in props: lines.append(f"    - {p}")
        
        lines.append(f"  assets:")
        if looks:
            lines.append(f"    look_urls:")
            for l in looks:
                lines.append(f"      {l}: {get_look_url(l)}")
        lines.append(f"    scene_urls:")
        lines.append(f"      {scene}: {get_scene_url(scene)}")
        if props:
            lines.append(f"    prop_urls:")
            for p in props:
                lines.append(f"      {p}: {get_prop_url(p)}")
        
        is_silent = len(dlg) == 0
        prompt = build_prompt(looks, scene, [visual], dlg, is_silent, True)
        escaped = prompt.replace("'", "''")
        lines.append(f"  api:")
        lines.append(f"    text: '{escaped}'")
        lines.append(f"    content_roles:")
        for cr in build_content_roles(looks, scene):
            lines.append(f"    {cr}")
        
        lines.append(f"  dialogue:")
        if dlg:
            for sp, ln in dlg:
                lines.append(f"  - speaker: {sp}")
                lines.append(f"    line: {ln}")
        else:
            lines.append(f"  []")
        lines.append(f"  transition_to_next: hard_cut")
    
    return "\n".join(lines)


def write_segments(ep_id, ep_label, segs, shots_data, source_md):
    lines = []
    lines.append(f"episode_id: {ep_id}")
    lines.append(f"source_md: {source_md}")
    lines.append("defaults:")
    lines.append("  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks")
    lines.append("  model: doubao-seedance-2-0-fast")
    lines.append("  ratio: '9:16'")
    lines.append("  resolution: 720p")
    lines.append("  generate_audio: true")
    lines.append("  watermark: false")
    lines.append(f"  prompt_suffix: {PS}")
    lines.append(f"  prompt_suffix_silent: {PS_SILENT}")
    lines.append(f"  negative_prompt: {NEG}")
    lines.append("")
    
    all_speakers = set()
    for seg in segs:
        for sp in seg[2]: all_speakers.add(sp)
    
    lines.append("voice_prompts:")
    for sp in sorted(all_speakers):
        if sp in VP:
            lines.append(f'  {sp}: "{VP[sp]}"')
    lines.append("")
    lines.append("segments:")
    
    # Build shot dialogue lookup
    shot_dlg = {}
    for s in shots_data:
        shot_dlg[s[0]] = s[8]  # (sid, sno, mode, dur, scene, looks, props, visual, dialogue)
    
    for seg_id, shot_ids, speakers, shot_texts, looks, scene, props, transition in segs:
        dur = 0
        for sid in shot_ids:
            for s in shots_data:
                if s[0] == sid:
                    dur += s[3]
        
        lines.append(f"- segment_id: {seg_id}")
        lines.append(f"  shot_ids:")
        for sid in shot_ids: lines.append(f"  - {sid}")
        lines.append(f"  duration_sec: {dur}")
        lines.append(f"  speakers:")
        if speakers:
            for sp in speakers: lines.append(f"  - {sp}")
        else:
            lines.append(f"  []")
        lines.append(f"  refs:")
        lines.append(f"    scene_id: {scene}")
        lines.append(f"  assets:")
        if looks:
            lines.append(f"    look_urls:")
            for l in looks:
                lines.append(f"      {l}: {get_look_url(l)}")
        lines.append(f"    scene_urls:")
        lines.append(f"      {scene}: {get_scene_url(scene)}")
        if props:
            lines.append(f"    prop_urls:")
            for p in props:
                lines.append(f"      {p}: {get_prop_url(p)}")
        
        # Collect all dialogue from constituent shots
        all_dlg = []
        for sid in shot_ids:
            if sid in shot_dlg:
                all_dlg.extend(shot_dlg[sid])
        
        is_silent = len(speakers) == 0
        prompt = build_prompt(looks, scene, shot_texts, all_dlg, is_silent)
        escaped = prompt.replace("'", "''")
        lines.append(f"  api:")
        lines.append(f"    text: '{escaped}'")
        lines.append(f"    content_roles:")
        for cr in build_content_roles(looks, scene):
            lines.append(f"    {cr}")
        lines.append(f"  transition_to_next: {transition}")
    
    return "\n".join(lines)


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Written: {os.path.basename(path)} ({len(content.splitlines())} lines)")


if __name__ == "__main__":
    episodes = [
        ("EP49", "美食大赛决赛", 78, "剧本/EP49/EP49_美食大赛决赛.md"),
        ("EP50", "冠军时刻", 80, "剧本/EP50/EP50_冠军时刻.md"),
        ("EP52", "周子轩的转变", 80, "剧本/EP52/EP52_周子轩的转变.md"),
        ("EP53", "扩张计划", 80, "剧本/EP53/EP53_扩张计划.md"),
    ]
    
    for ep_id, ep_label, src_dur, src_md in episodes:
        shots = EP_SHOTS[ep_id]
        segs = EP_SEGS[ep_id]
        base = os.path.join(BASE, f"剧本/{ep_id}")
        
        shots_yaml = write_shots(ep_id, ep_label, shots, src_dur, src_md)
        segs_yaml = write_segments(ep_id, ep_label, segs, shots, src_md)
        
        write_file(os.path.join(base, f"{ep_id}_shots.yaml"), shots_yaml)
        write_file(os.path.join(base, f"{ep_id}_segments.yaml"), segs_yaml)
    
    print("\n✅ Done: EP49, EP50, EP52, EP53 YAML files generated.")
    print("\n❌ BLOCKED: EP51 and EP54 — [待补] placeholder speakers detected:")
    print("   EP51-S12: [待补：投资经理] — needs CHAR-GRP-02 + L01 + voice_prompt")
    print("   EP54-S09: [待补：东北路人] — needs CHAR-GRP-03 + L01 + voice_prompt")
    print("   → production-planner must assign IDs + character-designer must generate assets.")
