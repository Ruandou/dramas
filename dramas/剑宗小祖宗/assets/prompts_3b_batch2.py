#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage 3b 后续批次（CHAR-004~015 + CHAR-GRP-01~11 + L02 变体）L01/L02 Prompt 单一真相源。
角色卡片.md 与生成脚本均从此模块读取，确保文件与生成一致（自检 #32）。
Prompt 中的物理描述必须与角色卡片「外貌描写（L01）」表一一对应（自检 #32）。
"""
# ---------------------------------------------------------------------------
# 通用基底（与 CHAR-001/002/003 一致：正面全身白底 + 棚拍平光 + 9:16）
# ---------------------------------------------------------------------------
SHOT_BASE = (
    "Photorealistic costume reference, wide shot showing the entire figure from "
    "head to toe with feet and shoes clearly visible at the bottom edge of the "
    "frame, single person standing upright facing the camera, plain white "
    "background, clean flat studio lighting. Full body fully visible, not cropped. "
)

STYLE_SUFFIX = (
    "ancient Chinese xianxia fantasy, bright warm golden tones with spring green "
    "accents, soft bright atmosphere, comedic tone over oppression, cinematic "
    "lighting, high detail, 9:16 vertical composition. shot on 85mm lens, "
    "editorial portrait photograph, natural skin texture with visible pores, "
    "indistinguishable from a real photograph. Vertical 9:16, photorealistic "
    "costume reference, NOT anime, NOT cartoon, NOT illustration, NOT manga, "
    "no watermark, no logo, no modern objects, no english text, no latin letters, "
    "no asymmetric face, no plastic skin, no doll-like skin, no lifeless eyes, "
    "no distorted body, no uncanny valley."
)

# 儿童/少年专用风格后缀（避免“毛孔”在幼童脸上渲染怪异，改用细肤质）
STYLE_SUFFIX_CHILD = (
    "ancient Chinese xianxia fantasy, bright warm golden tones with spring green "
    "accents, soft bright atmosphere, comedic tone over oppression, cinematic "
    "lighting, high detail, 9:16 vertical composition. shot on 85mm lens, "
    "editorial portrait photograph, natural youthful skin texture with fine "
    "realistic detail, indistinguishable from a real photograph. Vertical 9:16, "
    "photorealistic costume reference, NOT anime, NOT cartoon, NOT illustration, "
    "NOT manga, NOT chibi, NOT deformed, no watermark, no logo, no modern "
    "objects, no english text, no latin letters, no asymmetric face, no plastic "
    "skin, no doll-like skin, no lifeless eyes, no distorted body, no uncanny valley."
)

# ---------------------------------------------------------------------------
# CHAR-004 顾清弦 · 玄黑劲装·清冷剑修·佩剑+剑穗（男主，25岁）
# 持有 PROP-004 剑穗（待生成道具，TOS 参考图 URL 传入 image_urls）
# ---------------------------------------------------------------------------
PROMPT_CHAR004 = SHOT_BASE + (
    "A 25-year-old Chinese man, the aloof chief sword-cultivator of a poor "
    "mountain xianxia sword sect, strikingly handsome with an icy noble bearing, "
    "cold and taciturn, a guardian who protects in silence, with a cultivation-world "
    "commanding bearing. [FACE ANCHOR START] perfectly symmetrical facial "
    "features, level lip line, centered features, angular chiseled face with a "
    "sharp defined jawline, narrow phoenix eyes with a cold intense gaze and "
    "natural catchlight, sharp sword-like brows with a faint perpetual frown "
    "crease between them, high straight nose, thin lips pressed in a cold calm "
    "line, clear healthy complexion with natural skin texture, tall athletic "
    "build (183cm) with broad shoulders tapering to a lean waist, V-taper "
    "physique visible through clothing, commanding upright posture [FACE ANCHOR "
    "END]. Hairstyle: black hair tied in a tall ponytail secured with a plain "
    "black cord, hair reaching the middle of his back, a few loose strands at "
    "the temples, no ornaments. Costume: wearing a fitted dark-black xianxia "
    "sword-cultivator martial robe (玄黑劲装), high stand collar, narrow martial "
    "cut fitted at the waist, layered black inner robe with subtle dark-gray "
    "cloud-pattern trim, black cloth wrist guards, a dark leather belt at the "
    "waist, wide flowing outer sleeves, black cloth boots with dark leather trim. "
    "Accessories: ONE single sheathed longsword with a matte black scabbard and "
    "dark iron guard hanging at his left hip on a dark leather belt, ONE single "
    "black silk sword tassel tied to the sword hilt — the tassel has a tightly "
    "braided cord loop at the top and long fine dark-black silk strands "
    "cascading downward with soft natural drape, one thin dark-crimson silk "
    "strand woven subtly through the black strands as an accent (only one of "
    "each, singular, no duplicates). Expression: cold aloof expression, brows "
    "slightly furrowed in a faint perpetual frown, calm distant eyes, guarded "
    "composed posture. " + STYLE_SUFFIX
)

# ---------------------------------------------------------------------------
# CHAR-005 钱多福 · 补丁账房袍·圆脸矮胖·算盘不离手（45岁，喜剧/救赎线）
# ---------------------------------------------------------------------------
PROMPT_CHAR005 = SHOT_BASE + (
    "A 45-year-old Chinese man, the miserly accountant-steward of a poor "
    "mountain xianxia sword sect, shrewd and servile, plump and comedic, a "
    "fawning money-counter who bows deeper the more powerful you are, with a "
    "cultivation-world humble bearing. [FACE ANCHOR START] perfectly "
    "symmetrical facial features, level lip line, centered features, round "
    "plump face with fleshy cheeks, small shrewd narrow eyes that squint when "
    "calculating, thin sparse brows, low broad nose, thin lips curved in a "
    "fawning grin, sallow-tan skin with natural texture, short stout build "
    "(165cm) with a round belly, stooped servile posture [FACE ANCHOR END]. "
    "Hairstyle: thinning dark hair combed back neatly with a small bald patch "
    "at the crown, a small low bun at the nape secured with a plain cloth cord. "
    "Costume: wearing a worn gray-brown accountant's long robe (账房袍) with "
    "several neat cloth patches at the elbows and hem, coarse fabric slightly "
    "shiny from long wear, a plain dark cloth sash tied high over his round "
    "belly, worn cloth shoes with scuffed toes. Accessories: holding ONE single "
    "wooden abacus with dark beads in his left hand, fingers resting on the "
    "beads (only one, singular, no duplicates). Expression: fawning crafty "
    "grin, eyes narrowed in calculation, shoulders hunched as if mid-bow. " +
    STYLE_SUFFIX
)

# ---------------------------------------------------------------------------
# CHAR-006 秦岳 · 灰白长袍文士·清癯阴冷（中层Boss→赎罪者，45岁）
# ---------------------------------------------------------------------------
PROMPT_CHAR006 = SHOT_BASE + (
    "A 45-year-old Chinese man, an elder of a poor mountain xianxia sword sect, "
    "a gaunt cold scholar with a sharp calculating mind, outwardly refined and "
    "inwardly cold, with a cultivation-world bearing. [FACE ANCHOR START] "
    "perfectly symmetrical facial features, level lip line, centered features, "
    "gaunt narrow face with prominent cheekbones, cold deep-set eyes with a "
    "wary shrewd gaze, thin arched brows, high narrow nose, thin lips curved "
    "in a faint cold smile, pale sallow skin with natural texture, tall thin "
    "scholar build (178cm) with a slender frame and long delicate fingers, "
    "erect restrained posture [FACE ANCHOR END]. Hairstyle: dark hair streaked "
    "with gray at the temples, pulled back into a neat low scholar's bun "
    "secured with a plain wooden hairpin. Costume: wearing a gray-white "
    "scholar's long robe (灰白长袍) with a high collar, plain coarse cloth, "
    "slightly worn and faded, a thin dark cloth sash at the waist, plain cloth "
    "shoes. Accessories: none. Expression: cold aloof expression, thin lips "
    "curved in a faint knowing smirk, eyes narrowed with hidden calculation. " +
    STYLE_SUFFIX
)

# CHAR-006-L02 重伤赎罪相（EP35-36/EP63/EP69，基于 L01）
PROMPT_CHAR006_L02 = (
    "SAME person as the reference image, same face as CHAR-006-L01, a 45-year-old Chinese man, full body visible from head to toe with feet visible at the bottom edge of the frame, now wounded "
    "and in atonement. [FACE ANCHOR START] perfectly symmetrical facial "
    "features, level lip line, centered features, gaunt narrow face with "
    "prominent cheekbones, cold deep-set eyes with a wary shrewd gaze, thin "
    "arched brows, high narrow nose, thin lips curved in a faint cold smile, "
    "pale sallow skin with natural texture, tall thin scholar build (178cm) "
    "with a slender frame and long delicate fingers, erect restrained posture "
    "[FACE ANCHOR END]. Hairstyle: dark hair streaked with gray at the temples, "
    "now slightly disheveled with loose strands falling across the forehead, "
    "low scholar's bun loosened. Costume: wearing the same gray-white scholar's "
    "long robe, now torn at the left shoulder with a cleanly wrapped cloth "
    "bandage over the left arm and chest, dust and faint dirt smudges on the "
    "hem, no visible blood, no gore — only clean white bandages and a pale "
    "wan complexion. Expression: pale wan expression, eyes sunken with dark "
    "circles, lips bloodless and pressed in a grim line, shoulders slumped in "
    "exhaustion. plain white background maintained, clean white studio "
    "background. " + STYLE_SUFFIX
)

# ---------------------------------------------------------------------------
# CHAR-007 玄冥 · 玄黑道袍·清癯道人·念珠+半枚玉锁（大Boss，50岁）
# 持有 PROP-001 半块玉锁同形制（待生成道具，TOS 参考图 URL 传入 image_urls）
# ---------------------------------------------------------------------------
PROMPT_CHAR007 = SHOT_BASE + (
    "A 50-year-old Chinese man, the master of the Imperial Spirit Sect (御灵宗), "
    "a gaunt Daoist with a deep oppressive presence, outwardly serene and "
    "inwardly obsessed, with a commanding cultivation-world bearing and a faint "
    "dark spiritual aura around the figure. [FACE ANCHOR START] perfectly "
    "symmetrical facial features, level lip line, centered features, gaunt "
    "ascetic face with sharp cheekbones, deep dark eyes with a calm oppressive "
    "gaze, thin long brows, high straight nose, thin lips set in a grave line, "
    "pale sallow skin with natural texture, tall lean Daoist build (180cm) "
    "with an erect imposing posture [FACE ANCHOR END]. Hairstyle: dark "
    "gray-streaked hair tied in a neat Daoist topknot (道髻) with a plain black "
    "jade hairpin, a neatly trimmed long beard and mustache. Costume: wearing "
    "a black Daoist robe (玄黑道袍) with wide sleeves and a high collar, dark "
    "fabric with subtle embroidered cloud patterns at the hem, a black cloth "
    "sash at the waist, plain black cloth shoes. Accessories: holding a string "
    "of dark wooden prayer beads (念珠) in his right hand, ONE single half of "
    "an ancient Chinese white jade lock-shaped pendant (半枚玉锁) hanging from "
    "the prayer beads by a short frayed remnant of red silk cord — warm ivory "
    "nephrite jade with a soft translucent luster and mellow patina, the broken "
    "half showing a rough but time-smoothed fracture surface with faint "
    "internal jade grain, faint carved cloud swirls on the front, a small hole "
    "at the top threaded with the red cord remnant (only one, singular, no "
    "duplicates, matching the reference jade lock form). Expression: calm "
    "dangerous expression, deep unreadable eyes, slow deliberate posture. " +
    STYLE_SUFFIX
)

# ---------------------------------------------------------------------------
# CHAR-008 宁婆婆 · 补丁布衣·花白头发·佝偻背·手藏袖（隐藏反派→救赎，60岁）
# ---------------------------------------------------------------------------
PROMPT_CHAR008 = SHOT_BASE + (
    "A 60-year-old Chinese woman, an elderly village grandmother posing as a "
    "mute old servant who has recently joined a poor mountain xianxia sword "
    "sect, kind-faced on the surface with a hidden secret, humble kitchen "
    "servant attire of the cultivation world. [FACE ANCHOR START] perfectly "
    "symmetrical facial features, level lip line, centered features, weathered "
    "oval face with deep wrinkles and gentle age lines, kind clouded eyes with "
    "a hidden sharp gleam, thin gray eyebrows, low broad nose, thin lips "
    "pressed in a gentle tired smile, sallow aged skin with deep natural "
    "texture, short stooped elder build (155cm) with a hunched back [FACE "
    "ANCHOR END]. Hairstyle: silver-gray hair pulled back into a neat low bun "
    "with a plain dark cloth headband, a few loose strands at the temples. "
    "Costume: wearing a faded indigo patched cloth garment (补丁布衣), coarse "
    "homespun fabric with neat cloth patches at the elbows and hem, a plain "
    "cloth apron tied over it, worn dark cloth shoes. Accessories: both hands "
    "folded and hidden inside the opposite sleeves (手藏袖), a small worn cloth "
    "bundle tied at her waist. Expression: gentle kind expression, eyes "
    "slightly narrowed with a faint watchful glint, shoulders stooped, a "
    "grandmotherly soft smile. " + STYLE_SUFFIX
)

# ---------------------------------------------------------------------------
# CHAR-009 萧拾遗 · 风尘独行客·背旧剑·眉宇沧桑（40岁，身世线揭秘者）
# ---------------------------------------------------------------------------
PROMPT_CHAR009 = SHOT_BASE + (
    "A 40-year-old Chinese man, a weathered lone wanderer of the cultivation "
    "world, a swordsman carrying thirty years of quiet pursuit, resolute and "
    "enduring, with a cultivation-world bearing. [FACE ANCHOR START] perfectly "
    "symmetrical facial features, level lip line, centered features, weathered "
    "angular face with deep creases and a strong chin, deep-set steady eyes "
    "with a quiet resolute gaze, thick brows slightly sun-bleached, high "
    "straight nose, thin lips set in a firm weathered line, sun-bronzed "
    "wind-worn skin with natural texture, tall lean wanderer build (178cm) "
    "with a wiry enduring posture [FACE ANCHOR END]. Hairstyle: dark hair with "
    "gray at the temples, half-tied in a loose low ponytail with a frayed cloth "
    "cord, wind-blown loose strands. Costume: wearing a dusty worn travel robe "
    "(江湖旧袍) in faded brown-gray, coarse cloth with travel stains and frayed "
    "edges, sleeves rolled to the forearms, a worn leather shoulder strap "
    "across the chest, travel-worn cloth boots with dust. Accessories: ONE "
    "single old sword in a plain worn leather scabbard strapped diagonally "
    "across his back (only one, singular, no duplicates), a small cloth satchel "
    "tied at his waist. Expression: quiet resolute expression, deep weathered "
    "eyes with steady calm, slightly tired but unbroken. " + STYLE_SUFFIX
)

# ---------------------------------------------------------------------------
# CHAR-010 小石头 · 补丁短打·瘦小机灵·攥拳（10岁，玩伴/拜师）
# ---------------------------------------------------------------------------
PROMPT_CHAR010 = SHOT_BASE + (
    "A 10-year-old Chinese boy, a lively small disciple of a poor mountain "
    "xianxia sword sect, wiry and quick-witted, brave and loud, clearly a "
    "school-age boy not a toddler, standing tall and proud. [FACE ANCHOR "
    "START] perfectly symmetrical facial features, level lip line, centered "
    "features, lean small face with a sun-tanned youthful complexion and a "
    "defined young jawline, bright alert eyes with natural sparkle, soft thick "
    "brows, small straight nose, wide mouth with a big toothy grin, natural "
    "youthful skin with a sun-kissed tan, lean wiry school-age build (about "
    "140cm), energetic upright posture [FACE ANCHOR END]. Hairstyle: black "
    "hair in a small messy topknot with a frayed red cloth cord, a few "
    "flyaway strands. Costume: wearing a patched gray-brown short disciple "
    "outfit (补丁短打), loose short jacket and knee-length trousers with neat "
    "cloth patches at the right shoulder and left knee, a thin dark cloth "
    "belt, worn cloth shoes. Accessories: both small hands clenched into fists "
    "at his sides, ready and eager (only two hands, singular pair). "
    "Expression: bright eager grin, chest puffed out, eyes shining with "
    "determination. " + STYLE_SUFFIX_CHILD
)

# CHAR-010-L02 拜师弟子服（EP72 起，基于 L01）
PROMPT_CHAR010_L02 = (
    "SAME person as the reference image, same face as CHAR-010-L01, a 10-year-old Chinese boy, full body visible from head to toe with feet visible at the bottom edge of the frame, now "
    "wearing the formal disciple robe of the Qingyun Sword Sect after formally "
    "becoming a disciple. [FACE ANCHOR START] perfectly symmetrical facial "
    "features, level lip line, centered features, lean small face with a "
    "sun-tanned youthful complexion and a defined young jawline, bright alert "
    "eyes with natural sparkle, soft thick brows, small straight nose, wide "
    "mouth with a big toothy grin, natural youthful skin with a sun-kissed "
    "tan, lean wiry school-age build (about 140cm), energetic upright posture "
    "[FACE ANCHOR END]. Hairstyle: black hair in a neat small topknot now "
    "secured with a proper dark cloth band, a few flyaway strands. Costume: "
    "wearing a clean gray-blue sect disciple robe with white trim at the "
    "collar and cuffs, a small embroidered white cloud pattern on the left "
    "chest, a plain dark cloth sash at the waist, clean gray cloth boots, "
    "plain white background maintained, clean white studio background. "
    "Expression: proud shy grin, chest out, eyes bright with pride. " +
    STYLE_SUFFIX_CHILD
)

# ---------------------------------------------------------------------------
# CHAR-011 玄枯 · 高冠锦袍·山羊胡·御灵宗使者（40岁，龙套反派）
# ---------------------------------------------------------------------------
PROMPT_CHAR011 = SHOT_BASE + (
    "A 40-year-old Chinese man, an envoy of the Imperial Spirit Sect (御灵宗), "
    "arrogant and greedy, a pompous swaggering official of the cultivation "
    "world. [FACE ANCHOR START] perfectly symmetrical facial features, level "
    "lip line, centered features, narrow face with a pointed chin, greedy "
    "small eyes with a calculating gleam, thin brows, high narrow nose, thin "
    "lips set in an arrogant sneer, a neat sparse goatee (山羊胡) at the chin, "
    "sallow skin with natural texture, medium build (172cm) with a puffed-up "
    "chest, swaggering official posture [FACE ANCHOR END]. Hairstyle: black "
    "hair hidden under a tall black gauze official hat (高冠) with upturned "
    "brim, small dark side locks visible at the temples. Costume: wearing a "
    "luxurious dark-purple brocade robe (锦袍) with gold-thread cloud patterns, "
    "wide sleeves, a dark brocade sash at the waist, an embroidered abstract "
    "spiral emblem on the chest (decorative pattern only, no text), black "
    "cloth boots. Accessories: none. Expression: arrogant sneering expression, "
    "chin lifted, eyes narrowed with greed. " + STYLE_SUFFIX
)

# ---------------------------------------------------------------------------
# CHAR-012 言溪 · 白衣女剑仙·长发·温柔眉眼（柔光虚影/画像态，27岁）
# 特殊：无清晰面部（虚影/画像态 → mesh 豁免登记），写实锚定防绘画风漂移
# ---------------------------------------------------------------------------
PROMPT_CHAR012 = (
    "Photorealistic costume reference, full body visible from head to toe with "
    "feet and shoes visible at the bottom edge of the frame, single ethereal "
    "figure standing upright, plain white background, clean flat studio "
    "lighting with a soft warm luminous halo. A luminous soft-glow afterimage "
    "of a 27-year-old Chinese woman, a white-clad female sword immortal, "
    "gentle and resolute, appearing like a soft glowing memory or an old "
    "painting come to life — her face softened and veiled by warm golden "
    "luminous light, no clear facial features visible, a dreamlike luminous "
    "silhouette. [FORM ANCHOR] tall willowy figure (168cm) with a flowing "
    "silhouette, elegant upright posture, long dark hair flowing softly in "
    "gentle waves [FORM ANCHOR END]. Costume: wearing layered white immortal "
    "robes with wide flowing sleeves and a pale gold sash, the hems softly "
    "glowing at the edges, a faint outline of a slender white jade sword "
    "beside her hand (soft glow outline only). Expression: gentle serene "
    "posture, head tilted slightly as if looking down with tenderness, face "
    "veiled by luminous light, no facial detail visible. ancient Chinese "
    "xianxia fantasy, bright warm golden tones, soft bright atmosphere, "
    "cinematic lighting, high detail, 9:16 vertical composition. shot on 85mm "
    "lens, soft focus, luminous veil over the face, natural skin glow under "
    "the light, indistinguishable from a real photograph of a glowing figure, "
    "editorial portrait photograph, photorealistic. Vertical 9:16, "
    "photorealistic costume reference, NOT anime, NOT cartoon, NOT "
    "illustration, NOT manga, NOT painting, NOT digital art, no watermark, no "
    "logo, no modern objects, no english text, no latin letters, no distorted "
    "body, no uncanny valley."
)

# ---------------------------------------------------------------------------
# CHAR-013 钱姑娘 · 风尘背剑姑娘·江湖气（20岁，龙套）
# ---------------------------------------------------------------------------
PROMPT_CHAR013 = SHOT_BASE + (
    "A 20-year-old Chinese woman, a young wandering swordswoman of the "
    "cultivation world, travel-worn yet bright and determined, seeking her "
    "father across a thousand li, with a cultivation-world bearing. [FACE "
    "ANCHOR START] perfectly symmetrical facial features, level lip line, "
    "centered features, oval face with clear defined features, bright "
    "determined eyes with natural sparkle, neat slender brows, high straight "
    "nose, full lips set in a firm resolute line, sun-touched healthy skin "
    "with natural texture, tall willowy figure (167cm) with graceful feminine "
    "proportions, upright steady posture [FACE ANCHOR END]. Hairstyle: dark "
    "hair tied in a simple high ponytail with a worn dark cloth band, a few "
    "wind-blown strands, no ornaments. Costume: wearing a simple travel-worn "
    "swordswoman outfit in faded indigo and gray, fitted short jacket with "
    "rolled sleeves, loose trousers tucked into worn cloth boots, a plain "
    "cloth sash at the waist, dust and travel wear on the cloth. Accessories: "
    "ONE single old straight sword in a plain worn scabbard strapped "
    "diagonally across her back (only one, singular, no duplicates), a small "
    "cloth bundle tied at her waist. Expression: bright determined expression, "
    "chin lifted, eyes clear and steady. " + STYLE_SUFFIX
)

# ---------------------------------------------------------------------------
# CHAR-014 小福 · 瘦弱怯生·破布衣裳·眼睛很亮（6岁，福宝宗首徒）
# ---------------------------------------------------------------------------
PROMPT_CHAR014 = SHOT_BASE + (
    "A 6-year-old Chinese boy, an abandoned orphan about to be taken in by a "
    "warm sect, thin and timid with surprisingly bright eyes, clearly a "
    "school-age child not a toddler, standing tall for his age. [FACE ANCHOR "
    "START] perfectly symmetrical facial features, level lip line, centered "
    "features, small thin face with delicate features, large bright clear eyes "
    "with a soft hopeful light, soft thin brows, small nose, small lips "
    "pressed together shyly, pale skin with a few faint dust smudges, natural "
    "youthful skin with fine realistic detail, small lean build (about 90cm), "
    "thin and light [FACE ANCHOR END]. Hairstyle: soft black hair, slightly "
    "unkempt, falling in uneven layers with a few strands over the forehead. "
    "Costume: wearing a worn patched ragged cloth garment (破布衣裳) in faded "
    "gray-brown, slightly too large for him with frayed hems, a thin cloth "
    "cord tied at the waist, small worn cloth shoes with scuffed toes. "
    "Accessories: small hands clutching the front of his robe nervously. "
    "Expression: timid shy expression, big bright eyes looking up, lips "
    "slightly parted, hesitating. " + STYLE_SUFFIX_CHILD
)

# ---------------------------------------------------------------------------
# CHAR-015 二长老 · 佝偻剪影（80岁，天机阁，不露正面 → mesh 豁免）
# 特殊：剪影 cameo，无清晰面部，L01 以背向剪影为基准（制片规范 §九 剪影代偿）
# ---------------------------------------------------------------------------
PROMPT_CHAR015 = (
    "Photorealistic reference, back view of a hunched silhouette, wide shot "
    "showing the entire figure from head to toe with feet visible at the "
    "bottom edge of the frame, single person seen completely from behind, "
    "plain white background, bright soft backlight creating a clear dark "
    "silhouette. The back view silhouette of a hunched 80-year-old Chinese "
    "man, an ancient elder of the Heaven Mechanism Pavilion (天机阁), very old "
    "and stooped, wearing a long dark flowing elder's robe with wide sleeves, "
    "hands clasped behind his back, head slightly bowed, shoulders hunched "
    "with age, standing still as if gazing into the distance, face completely "
    "hidden — no facial features, no front view, no profile, a pure dark "
    "silhouette against bright light. No face, no person in front view, no "
    "facial detail, no eyes, no features. ancient Chinese xianxia fantasy, "
    "bright warm golden tones, soft bright atmosphere, cinematic lighting, "
    "high detail, 9:16 vertical composition. shot on 85mm lens, photorealistic "
    "silhouette reference, soft rim light on the shoulders, indistinguishable "
    "from a real photograph. Vertical 9:16, photorealistic reference, NOT "
    "anime, NOT cartoon, NOT illustration, NOT manga, no watermark, no logo, "
    "no modern objects, no english text, no latin letters."
)

# ---------------------------------------------------------------------------
# 群演 CHAR-GRP-01~11（各 1 张 L01）
# ---------------------------------------------------------------------------
# GRP-01 旧派长老（60岁，板正守旧长老袍，EP04）
PROMPT_GRP01 = SHOT_BASE + (
    "A 60-year-old Chinese man, an orthodox conservative elder of a poor "
    "mountain xianxia sword sect, stern and stiff, upholding old rules, with "
    "a cultivation-world bearing. [FACE ANCHOR START] perfectly symmetrical "
    "facial features, level lip line, centered features, square stern face "
    "with a full gray beard, deep-set stern eyes, thick gray brows, high "
    "straight nose, thin lips pressed in a disapproving line, weathered skin "
    "with natural texture, medium elder build (170cm), rigid upright posture "
    "[FACE ANCHOR END]. Hairstyle: neat gray hair tied in a topknot with a "
    "plain wooden hairpin. Costume: wearing a plain dark-brown elder's robe "
    "(长老袍) with a high collar and wide sleeves, a simple dark cloth sash, "
    "plain cloth shoes. Accessories: none. Expression: stern disapproving "
    "expression, brow furrowed, arms crossed. " + STYLE_SUFFIX
)

# GRP-02 邻宗长老（50岁，富态锦袍·阴阳怪气，EP06）
PROMPT_GRP02 = SHOT_BASE + (
    "A 50-year-old Chinese man, a portly elder of a neighboring prosperous "
    "sect, wealthy and insincere, smiling with hidden mockery, with a "
    "cultivation-world bearing. [FACE ANCHOR START] perfectly symmetrical "
    "facial features, level lip line, centered features, round plump face "
    "with a double chin, small sly eyes with an insincere gleam, thin brows, "
    "broad nose, thin lips curved in an oily insincere smile, a thin neatly "
    "trimmed mustache, sallow skin with natural texture, portly build (170cm) "
    "with a round belly, haughty swaggering posture [FACE ANCHOR END]. "
    "Hairstyle: sleek dark hair with gray at the temples, pulled back into a "
    "neat low bun with a jade hairpin. Costume: wearing a rich dark-green "
    "brocade robe (锦袍) with gold-thread patterns, wide sleeves, a brocade "
    "sash at the waist, dark leather shoes. Accessories: ONE single pale-green "
    "jade ring on his right hand (only one, singular, no duplicates). "
    "Expression: insincere oily smile, eyes narrowed with mockery, chin "
    "slightly lifted. " + STYLE_SUFFIX
)

# GRP-03 钱庄掌柜（45岁，稳重掌柜袍，EP22）
PROMPT_GRP03 = SHOT_BASE + (
    "A 45-year-old Chinese man, a steady money-house manager of the "
    "cultivation world, courteous and methodical, with a respectable merchant "
    "bearing. [FACE ANCHOR START] perfectly symmetrical facial features, "
    "level lip line, centered features, broad honest face with a neat short "
    "beard, steady warm eyes, thick straight brows, high straight nose, full "
    "lips in a composed courteous line, healthy skin with natural texture, "
    "medium build (172cm) with a tidy upright posture [FACE ANCHOR END]. "
    "Hairstyle: dark hair with a few gray strands, tied in a neat low bun "
    "with a plain wooden hairpin. Costume: wearing a plain dark-brown manager's "
    "long robe (掌柜袍) with a high collar, clean and neat with a simple cloth "
    "sash, a small ledger book tucked into the sash, dark cloth shoes. "
    "Accessories: ONE single ledger book with a cloth cover tucked at the "
    "waist (only one, singular, no duplicates). Expression: courteous composed "
    "expression, hands folded in front, patient steady eyes. " + STYLE_SUFFIX
)

# GRP-04 青衣书生（25岁，御灵宗暗探，EP21）
PROMPT_GRP04 = SHOT_BASE + (
    "A 25-year-old Chinese man, a young scholar in blue-green robes, outwardly "
    "bookish and frail, secretly a spy with sharp hidden eyes, with a "
    "cultivation-world bearing. [FACE ANCHOR START] perfectly symmetrical "
    "facial features, level lip line, centered features, pale refined narrow "
    "face, narrow sharp eyes hidden behind a calm scholarly gaze, thin arched "
    "brows, high narrow nose, thin lips pressed in a polite faint smile, pale "
    "fair skin with natural texture, slender scholar build (175cm), "
    "bookish restrained posture [FACE ANCHOR END]. Hairstyle: black hair "
    "pulled back into a neat low bun with a plain blue cloth band, no "
    "ornaments. Costume: wearing a plain blue-green scholar robe (青衣) with a "
    "high collar, simple cloth sash, a small cloth book satchel slung across "
    "the shoulder, cloth shoes. Accessories: none. Expression: calm bookish "
    "expression with a hidden sharp glint in the eyes, lips curved in a "
    "polite faint smile. " + STYLE_SUFFIX
)

# GRP-05 邻村小孩（8岁，顽皮村童，EP21）
PROMPT_GRP05 = SHOT_BASE + (
    "An 8-year-old Chinese village boy, mischievous and cheeky, from a poor "
    "farming village near a mountain sword sect, clearly a school-age child "
    "not a toddler, standing tall and sturdy. [FACE ANCHOR START] perfectly "
    "symmetrical facial features, level lip line, centered features, round "
    "sun-tanned face with a mischievous gleam, bright playful eyes with "
    "natural sparkle, soft thick brows, small straight nose, wide mouth "
    "stretched in an impish grin, natural youthful skin with a sun-kissed "
    "tan, small sturdy school-age build (about 130cm), bouncing energetic "
    "posture [FACE ANCHOR END]. Hairstyle: short black hair in a messy cut, a "
    "few strands sticking up. Costume: wearing a patched faded village short "
    "outfit (村童短打) in gray-brown, loose short jacket and knee-length "
    "trousers with a couple of cloth patches, a thin rope belt, small worn "
    "cloth shoes. Accessories: none. Expression: mischievous cheeky grin, "
    "chin lifted, eyes bright and teasing. " + STYLE_SUFFIX_CHILD
)

# GRP-06 村长（70岁，朴素村长老者，EP17/EP83）
PROMPT_GRP06 = SHOT_BASE + (
    "A 70-year-old Chinese man, the simple honest village headman of "
    "Clearwater Village, weather-beaten and kind, with a humble country "
    "elder's bearing. [FACE ANCHOR START] perfectly symmetrical facial "
    "features, level lip line, centered features, weathered wrinkled face "
    "with a white-gray short beard, honest kind eyes with deep crow's feet, "
    "thick gray brows, broad nose, thin lips pressed in a humble earnest "
    "line, deeply tanned aged skin with natural texture, medium stooped "
    "elder build (168cm), bowed humble posture [FACE ANCHOR END]. Hairstyle: "
    "white-gray hair tied in a simple low bun with a plain cloth cord. "
    "Costume: wearing a simple faded gray village elder robe (粗布长衫) with a "
    "cloth sash, a plain straw rain hat hanging at his back by a cord, worn "
    "cloth shoes. Accessories: hands clasped together in front in a respectful "
    "gesture (作揖 posture). Expression: humble earnest expression, kind "
    "weathered eyes, lips parted as if about to plead. " + STYLE_SUFFIX
)

# GRP-07 玄冥使者（25岁，御灵宗使者劲装，EP61-62）
PROMPT_GRP07 = SHOT_BASE + (
    "A 25-year-old Chinese man, an envoy of the Imperial Spirit Sect (御灵宗), "
    "cold and officious, delivering orders with cold official authority, with "
    "a cultivation-world bearing. [FACE ANCHOR START] perfectly symmetrical "
    "facial features, level lip line, centered features, sharp cold young "
    "face, hard indifferent eyes, thin straight brows, high nose, thin lips "
    "pressed in a cold line, clear pale skin with natural texture, lean "
    "athletic build (178cm), stiff officious posture [FACE ANCHOR END]. "
    "Hairstyle: black hair pulled back into a tight high ponytail with a dark "
    "cloth band, no ornaments. Costume: wearing a dark military-style envoy "
    "uniform (使者劲装), fitted black tunic with dark-red trim at the collar "
    "and cuffs, high collar, a dark belt with a small iron buckle, black "
    "cloth boots. Accessories: ONE single dark metal order token (令牌) held "
    "in his right hand (only one, singular, no duplicates). Expression: cold "
    "officious expression, chin lifted, eyes flat and unreadable. " +
    STYLE_SUFFIX
)

# GRP-08 女弟子（20岁，剑宗女弟子·素色剑袍，EP79）
PROMPT_GRP08 = SHOT_BASE + (
    "A 20-year-old Chinese woman, a young female disciple of a poor mountain "
    "xianxia sword sect, quiet at first but growing resolute, with a "
    "cultivation-world bearing. [FACE ANCHOR START] perfectly symmetrical "
    "facial features, level lip line, centered features, oval face with soft "
    "delicate features, bright determined eyes with natural catchlight, soft "
    "slender brows, high straight nose, full lips pressed in an earnest "
    "resolute line, fair clear skin with natural texture, willowy figure "
    "(165cm) with graceful feminine proportions, upright steady posture "
    "[FACE ANCHOR END]. Hairstyle: black hair in a simple high ponytail with "
    "a plain pale-gray cloth band, a few loose strands at the temples, no "
    "ornaments. Costume: wearing a plain pale-gray and white female disciple "
    "robe (素色剑袍), high collar, layered gray outer robe with a simple "
    "pale-green cloth sash, wide sleeves, plain cloth boots. Accessories: ONE "
    "single sheathed sword with a plain dark scabbard at her left hip (only "
    "one, singular, no duplicates). Expression: earnest determined expression, "
    "brows slightly set, eyes bright and sincere. " + STYLE_SUFFIX
)

# GRP-09 算命先生（50岁，算命摊先生·神棍相，EP78）
PROMPT_GRP09 = SHOT_BASE + (
    "A 50-year-old Chinese man, a street fortune-teller of the cultivation "
    "world, shamanistic and sly, a slick-talking charlatan later exposed as a "
    "fraud, with a worldly street-corner bearing. [FACE ANCHOR START] "
    "perfectly symmetrical facial features, level lip line, centered features, "
    "narrow cunning face, shrewd narrow eyes with a sly gleam, thin brows, "
    "narrow nose, thin lips under a thin mustache and a sparse goatee, sallow "
    "skin with natural texture, lean build (170cm), hunched sly posture "
    "[FACE ANCHOR END]. Hairstyle: gray-streaked black hair tied in a loose "
    "small bun with a plain cloth cord, a few stray strands. Costume: wearing "
    "a faded gray-blue fortune-teller robe with a cloth waist sash, a small "
    "plain cloth banner over the shoulder (blank cloth, no text), a cloth "
    "pouch at the waist, worn cloth shoes. Accessories: ONE single bamboo "
    "fortune-stick cylinder held in his left hand (only one, singular, no "
    "duplicates). Expression: mysterious sly expression, eyes half-closed as "
    "if divining, lips curved in a knowing smirk. " + STYLE_SUFFIX
)

# GRP-10 老医师（70岁，苍老医者·药箱，EP32）
PROMPT_GRP10 = SHOT_BASE + (
    "A 70-year-old Chinese man, an aged physician of the cultivation world, "
    "steady and trustworthy, with a calm healer's bearing. [FACE ANCHOR START] "
    "perfectly symmetrical facial features, level lip line, centered features, "
    "weathered kindly face with a full white-gray beard, calm wise eyes, thick "
    "gray brows, broad nose, thin lips set in a grave composed line, deeply "
    "lined aged skin with natural texture, medium stooped build (165cm), "
    "calm steady posture [FACE ANCHOR END]. Hairstyle: white-gray hair tied "
    "in a neat low bun with a plain wooden hairpin. Costume: wearing a plain "
    "dark physician's robe (医者长袍) with a high collar, simple cloth sash, "
    "clean and neat, dark cloth shoes. Accessories: ONE single worn leather "
    "medicine box (药箱) with a shoulder strap hanging at his side (only one, "
    "singular, no duplicates). Expression: calm grave expression, steady "
    "wise eyes, composed and unhurried. " + STYLE_SUFFIX
)

# GRP-11 邻宗修士（25岁，邻宗守门修士，EP41）
PROMPT_GRP11 = SHOT_BASE + (
    "A 25-year-old Chinese man, a gate-guard cultivator of a neighboring sect, "
    "cold and dismissive, with a cultivation-world bearing. [FACE ANCHOR "
    "START] perfectly symmetrical facial features, level lip line, centered "
    "features, sharp young face, indifferent eyes with a dismissive gaze, "
    "thin straight brows, high nose, thin lips pressed in a bored line, clear "
    "pale skin with natural texture, lean athletic build (178cm), relaxed "
    "aloof posture [FACE ANCHOR END]. Hairstyle: black hair tied in a simple "
    "topknot with a dark cloth band, a few loose strands. Costume: wearing a "
    "simple dark-blue cultivator guard uniform with a high collar, a plain "
    "dark cloth belt, dark cloth boots. Accessories: ONE single long sword "
    "with a dark scabbard at his waist (only one, singular, no duplicates). "
    "Expression: cold dismissive expression, one brow slightly raised, eyes "
    "looking down with indifference. " + STYLE_SUFFIX
)

# ---------------------------------------------------------------------------
# 汇总
# ---------------------------------------------------------------------------
PROMPTS = {
    # 主角/主要角色（本批）
    "CHAR-004-L01": PROMPT_CHAR004,
    "CHAR-005-L01": PROMPT_CHAR005,
    "CHAR-006-L01": PROMPT_CHAR006,
    "CHAR-006-L02": PROMPT_CHAR006_L02,
    "CHAR-007-L01": PROMPT_CHAR007,
    "CHAR-008-L01": PROMPT_CHAR008,
    "CHAR-009-L01": PROMPT_CHAR009,
    "CHAR-010-L01": PROMPT_CHAR010,
    "CHAR-010-L02": PROMPT_CHAR010_L02,
    "CHAR-011-L01": PROMPT_CHAR011,
    "CHAR-012-L01": PROMPT_CHAR012,
    "CHAR-013-L01": PROMPT_CHAR013,
    "CHAR-014-L01": PROMPT_CHAR014,
    "CHAR-015-L01": PROMPT_CHAR015,
    # 群演
    "CHAR-GRP-01-L01": PROMPT_GRP01,
    "CHAR-GRP-02-L01": PROMPT_GRP02,
    "CHAR-GRP-03-L01": PROMPT_GRP03,
    "CHAR-GRP-04-L01": PROMPT_GRP04,
    "CHAR-GRP-05-L01": PROMPT_GRP05,
    "CHAR-GRP-06-L01": PROMPT_GRP06,
    "CHAR-GRP-07-L01": PROMPT_GRP07,
    "CHAR-GRP-08-L01": PROMPT_GRP08,
    "CHAR-GRP-09-L01": PROMPT_GRP09,
    "CHAR-GRP-10-L01": PROMPT_GRP10,
    "CHAR-GRP-11-L01": PROMPT_GRP11,
}

META = {
    "CHAR-004-L01": {"name": "顾清弦", "look_name": "玄黑劲装·清冷剑修·剑穗佩剑", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-004-L01.png"},
    "CHAR-005-L01": {"name": "钱多福", "look_name": "补丁账房袍·圆脸矮胖·算盘不离手", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-005-L01.png"},
    "CHAR-006-L01": {"name": "秦岳", "look_name": "灰白长袍文士·清癯阴冷", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-006-L01.png"},
    "CHAR-006-L02": {"name": "秦岳·重伤赎罪相", "look_name": "重伤赎罪相（EP35 起）", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-006-L02.png"},
    "CHAR-007-L01": {"name": "玄冥", "look_name": "玄黑道袍·清癯道人·念珠+半枚玉锁", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-007-L01.png"},
    "CHAR-008-L01": {"name": "宁婆婆", "look_name": "补丁布衣·花白头发·佝偻背·手藏袖", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-008-L01.png"},
    "CHAR-009-L01": {"name": "萧拾遗", "look_name": "风尘独行客·背旧剑·眉宇沧桑", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-009-L01.png"},
    "CHAR-010-L01": {"name": "小石头", "look_name": "补丁短打·瘦小机灵·攥拳", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-010-L01.png"},
    "CHAR-010-L02": {"name": "小石头·拜师弟子服", "look_name": "拜师后弟子服（EP72 起）", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-010-L02.png"},
    "CHAR-011-L01": {"name": "玄枯", "look_name": "高冠锦袍·山羊胡·御灵宗使者", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-011-L01.png"},
    "CHAR-012-L01": {"name": "言溪", "look_name": "白衣女剑仙·长发·温柔眉眼（柔光虚影/画像态）", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-012-L01.png"},
    "CHAR-013-L01": {"name": "钱姑娘", "look_name": "风尘背剑姑娘·江湖气", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-013-L01.png"},
    "CHAR-014-L01": {"name": "小福", "look_name": "瘦弱怯生·破布衣裳·眼睛很亮", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-014-L01.png"},
    "CHAR-015-L01": {"name": "二长老", "look_name": "佝偻剪影（不露正面）", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-015-L01.png"},
    "CHAR-GRP-01-L01": {"name": "旧派长老", "look_name": "板正守旧长老袍", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-01-L01.png"},
    "CHAR-GRP-02-L01": {"name": "邻宗长老", "look_name": "富态锦袍·阴阳怪气", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-02-L01.png"},
    "CHAR-GRP-03-L01": {"name": "钱庄掌柜", "look_name": "稳重掌柜袍", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-03-L01.png"},
    "CHAR-GRP-04-L01": {"name": "青衣书生", "look_name": "青衣书生·御灵宗暗探", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-04-L01.png"},
    "CHAR-GRP-05-L01": {"name": "邻村小孩", "look_name": "顽皮村童", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-05-L01.png"},
    "CHAR-GRP-06-L01": {"name": "清水村村长", "look_name": "朴素村长老者", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-06-L01.png"},
    "CHAR-GRP-07-L01": {"name": "玄冥使者", "look_name": "御灵宗使者劲装", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-07-L01.png"},
    "CHAR-GRP-08-L01": {"name": "女弟子", "look_name": "剑宗女弟子·素色剑袍", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-08-L01.png"},
    "CHAR-GRP-09-L01": {"name": "算命先生", "look_name": "算命摊先生·神棍相", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-09-L01.png"},
    "CHAR-GRP-10-L01": {"name": "老医师", "look_name": "苍老医者·药箱", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-10-L01.png"},
    "CHAR-GRP-11-L01": {"name": "邻宗修士", "look_name": "邻宗守门修士", "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-11-L01.png"},
}

# L01 参考图（TOS 永久 URL）映射：CHAR-004→PROP-004 剑穗、CHAR-007→PROP-001 玉锁
# L02 参考图在生成时从 cdn_urls.json 动态读取对应 L01
REF_URLS_L01 = {
    "CHAR-004-L01": ["https://drama-reference-images.tos-cn-beijing.volces.com/props/剑宗小祖宗/PROP-004.png"],
    "CHAR-007-L01": ["https://drama-reference-images.tos-cn-beijing.volces.com/props/剑宗小祖宗/PROP-001.png"],
}

# 群演顺序（生成优先级）
PRIORITY_GROUPS = {
    "l01-batch1": ["CHAR-004-L01", "CHAR-005-L01", "CHAR-011-L01", "CHAR-GRP-01-L01", "CHAR-GRP-02-L01"],
    "l01-batch2": ["CHAR-006-L01", "CHAR-007-L01", "CHAR-008-L01", "CHAR-009-L01", "CHAR-010-L01"],
    "l01-batch3": ["CHAR-012-L01", "CHAR-013-L01", "CHAR-014-L01", "CHAR-015-L01",
                   "CHAR-GRP-03-L01", "CHAR-GRP-04-L01", "CHAR-GRP-05-L01", "CHAR-GRP-06-L01",
                   "CHAR-GRP-07-L01", "CHAR-GRP-08-L01", "CHAR-GRP-09-L01", "CHAR-GRP-10-L01", "CHAR-GRP-11-L01"],
    "l02": ["CHAR-006-L02", "CHAR-010-L02"],
}

# mesh 豁免登记（无清晰面部）
MESH_EXEMPT = {
    "CHAR-012-L01": "mesh豁免（柔光虚影无脸）",
    "CHAR-015-L01": "mesh豁免（剪影无脸）",
}

if __name__ == "__main__":
    for k, v in PROMPTS.items():
        print(f"{k}: {len(v)} chars")
