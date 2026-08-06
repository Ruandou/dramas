#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage 3b 后续批次（CHAR-002 / CHAR-003 / CHAR-GRP-12）L01 Prompt 单一真相源。
角色卡片.md 与生成脚本均从此模块读取，确保文件与生成一致（自检 #32）。
"""
# ---------------------------------------------------------------------------
# 通用基底（参考 CHAR-001-L01 结构：正面全身白底 + 棚拍平光 + 9:16）
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

# ---------------------------------------------------------------------------
# CHAR-002 云昭 · 青白剑袍大师姐·利落高马尾·佩剑
# ---------------------------------------------------------------------------
PROMPT_CHAR002 = SHOT_BASE + (
    "A 22-year-old Chinese woman, a strikingly beautiful sword-cultivator senior "
    "sister of a poor mountain xianxia sword sect, calm and determined, the "
    "protective eldest senior disciple, with a qi-infused upright bearing. "
    "[FACE ANCHOR START] perfectly symmetrical facial features, level lip line, "
    "centered features, oval face with refined delicate bone structure, large "
    "expressive almond-shaped eyes with bright clear determined gaze and natural "
    "catchlight, sharp slender sword-like brows, high straight nose, full rosy "
    "lips pressed in a calm firm line, luminous radiant complexion with natural "
    "skin texture, tall willowy figure (167cm) with graceful feminine "
    "proportions, slim elegant waist, cultivator's poised upright posture "
    "[FACE ANCHOR END]. Hairstyle: neat high ponytail secured with a simple dark "
    "cloth band, silky black hair with natural highlights and a few loose strands "
    "framing her face, no elaborate ornaments. Costume: wearing an ancient "
    "Chinese xianxia sword-cultivator robe in pale cyan and white, white inner "
    "robe with a high collar, layered pale cyan outer robe fitted at the waist "
    "with dark cyan fabric trim and simple cloth buttons at the chest, a slim "
    "pale-green cloth sash tied at the waist with a short hanging end, wide "
    "flowing sleeves, plain pale-gray cloth boots with dark trim. Accessories: "
    "ONE single sheathed longsword with a dark scabbard and bronze guard hanging "
    "at the left side of her waist on a dark belt (only one, singular, no "
    "duplicates, no tassel). Expression: calm determined expression, steady "
    "clear eyes, composed confident posture. " + STYLE_SUFFIX
)

# ---------------------------------------------------------------------------
# CHAR-003 冷孤鸿 · 破旧掌门袍·花白胡须·腰别酒葫芦
# ---------------------------------------------------------------------------
PROMPT_CHAR003 = SHOT_BASE + (
    "A 60-year-old Chinese man, the sect master of a poor mountain xianxia sword "
    "sect, an old rascal with a lively mischievous temperament, dignified yet "
    "comedic, with a cultivation-world bearing. [FACE ANCHOR START] perfectly "
    "symmetrical facial features, level lip line, centered features, oval "
    "weathered face with deep laugh lines at the eyes, bright lively eyes with "
    "natural sparkle that can widen in surprise, bushy gray eyebrows, high "
    "straight nose, full gray-streaked beard and mustache neatly combed, warm "
    "tanned skin with visible age texture, medium sturdy elder build (170cm), "
    "dignified upright bearing [FACE ANCHOR END]. Hairstyle: neat gray-streaked "
    "hair tied in a small topknot with a plain wooden hairpin, sideburns brushed "
    "back. Costume: wearing a worn dark-blue ancient Chinese xianxia sect master "
    "robe, high collar and wide sleeves, coarse fabric visibly faded, two neat "
    "cloth patches stitched at the right elbow and left shoulder (poor sect but "
    "clean, carefully mended), a simple dark cloth sash at the waist, worn but "
    "clean gray cloth boots. Accessories: ONE single small dark-brown gourd "
    "flask with a cork stopper tied at his right waist with a thin rope (only "
    "one, singular, no duplicates). Expression: lively mischievous expression, "
    "eyes wide and bright as if about to exclaim, beard tips slightly upturned, "
    "a knowing grin. " + STYLE_SUFFIX
)

# ---------------------------------------------------------------------------
# CHAR-GRP-12 巡山弟子 · 补丁短打·提破灯笼·风霜少年
# ---------------------------------------------------------------------------
PROMPT_GRP12 = SHOT_BASE + (
    "A lean 18-year-old Chinese young man, a poor mountain xianxia sect patrol "
    "disciple, boyish and excitable, wind-roughened from night patrols, not a "
    "child — a physically mature young adult with adolescent bone structure. "
    "[FACE ANCHOR START] perfectly symmetrical facial features, level lip line, "
    "centered features, lean youthful oval face with defined adolescent "
    "jawline, bright alert wide eyes with natural sparkle, soft straight brows, "
    "high straight nose, thin lips slightly parted as if about to call out, "
    "sun-tanned weather-beaten young skin with natural texture, tall lean "
    "adolescent build (175cm), wiry quick posture [FACE ANCHOR END]. Hairstyle: "
    "black hair slightly damp and darkened, a few wet strands plastered to his "
    "forehead, the rest tied back loosely at the nape. Costume: wearing a "
    "gray-brown coarse cloth patched short robe (xianxia sect disciple work "
    "clothes), visible cloth patches at the right shoulder and left knee, "
    "sleeves rolled to the forearm, loose trousers with cuffs rolled up to the "
    "shin with a few mud flecks, worn dark cloth shoes with mud splashes. "
    "Accessories: holding ONE single broken paper lantern in his right hand, "
    "the paper shade cracked with a visible tear, warm yellow light glowing "
    "through the crack (only one, singular, no duplicates). Expression: alert "
    "wide-eyed expression, mouth slightly open as if about to shout, a mix of "
    "nervousness and eager excitement. " + STYLE_SUFFIX
)

PROMPTS = {
    "CHAR-002-L01": PROMPT_CHAR002,
    "CHAR-003-L01": PROMPT_CHAR003,
    "CHAR-GRP-12-L01": PROMPT_GRP12,
}

META = {
    "CHAR-002-L01": {
        "name": "云昭",
        "look_name": "青白剑袍大师姐·利落高马尾·佩剑",
        "output": "dramas/剑宗小祖宗/assets/looks/CHAR-002-L01.png",
    },
    "CHAR-003-L01": {
        "name": "冷孤鸿",
        "look_name": "破旧掌门袍·花白胡须·腰别酒葫芦",
        "output": "dramas/剑宗小祖宗/assets/looks/CHAR-003-L01.png",
    },
    "CHAR-GRP-12-L01": {
        "name": "巡山弟子",
        "look_name": "补丁短打·提破灯笼·风霜少年",
        "output": "dramas/剑宗小祖宗/assets/looks/CHAR-GRP-12-L01.png",
    },
}

if __name__ == "__main__":
    for k, v in PROMPTS.items():
        print(f"{k}: {len(v)} chars")
