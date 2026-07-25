#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 1 L01 generation runner — 我头顶飘着一条别人的弹幕 (Stage 3b character-designer).
Prompts are copied verbatim from 资产/角色卡片.md (source of truth).
Usage: python3 assets/gen_characters_l01.py
"""
import subprocess, sys, os, json
from pathlib import Path

ROOT = Path("/Users/leifu/Movies/dramas/dramas/我头顶飘着一条别人的弹幕")
REPO = Path("/Users/leifu/Movies/dramas")
CLI = "/Users/leifu/Movies/dramas/mcps/volc-ark/scripts/ark_seedream_image.py"
LOOKS = ROOT / "assets" / "looks"
LOOKS.mkdir(parents=True, exist_ok=True)

def bootstrap_credentials():
    """Populate ARK/VOLC/TOS credentials from the project's .cursor/mcp.json."""
    for p in (REPO / ".cursor" / "mcp.json", Path.home() / ".cursor" / "mcp.json"):
        if not p.is_file():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        servers = data.get("mcpServers") or {}
        for srv in ("volc-ark", "volc-jimeng"):
            env = (servers.get(srv) or {}).get("env") or {}
            for k, v in env.items():
                if v and not os.environ.get(k):
                    os.environ[k] = str(v)
    # CLI reads ARK_API_KEY; jimeng may store it there.
    if not os.environ.get("ARK_API_KEY") and os.environ.get("VOLC_ARK_API_KEY"):
        os.environ["ARK_API_KEY"] = os.environ["VOLC_ARK_API_KEY"]

bootstrap_credentials()

PROP002 = "https://drama-reference-images.tos-cn-beijing.volces.com/props/我头顶飘着一条别人的弹幕/PROP-002.png"

COMMON_NEG = ("NOT anime, NOT cartoon, NOT illustration, NOT manga, no ghost, no supernatural glow, "
              "no floating on-screen text, no danmaku text baked in, no watermark, no burned-in subtitles, no exposed brand logo.")

ITEMS = [
 ("CHAR-001-L01",
  "Photorealistic character reference sheet, full-body wide shot showing the entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single Chinese woman standing upright facing the camera, plain white background, clean soft butterfly beauty lighting. [FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 26-year-old Chinese woman with an oval face, large expressive almond-shaped eyes with natural catchlight, soft gently arched brows, a delicate straight nose, full rosy lips, fair luminous skin with natural texture and visible pores; tall and slender with graceful feminine proportions (168cm), slim waist, elegant upright posture [FACE ANCHOR END]. Shoulder-length soft black hair with natural sheen and side-swept bangs. Wearing a soft beige knit cardigan over a simple white top, high-waisted light-grey trousers, minimal delicate stud earrings, flat white sneakers. Holding ONE single modern 2026 smartphone with a spiderweb-cracked screen in her right hand, only one, singular. Gentle, slightly guarded expression with a quiet resilience in her eyes, strikingly beautiful and refined with delicate bone structure and a luminous radiant complexion. Shot on 85mm lens, editorial portrait photograph, photorealistic urban realism, modern city of 2026, natural skin texture, shallow depth of field, leave headroom space above her head. " + COMMON_NEG,
  [PROP002]),
 ("CHAR-002-L01",
  "Photorealistic character reference sheet, full-body wide shot showing the entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single Chinese man standing upright facing the camera, plain white background, clean soft Rembrandt studio lighting. [FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 29-year-old Chinese man with an angular face and a sharp defined jawline, deep-set intense eyes with a calm clean gaze, straight sword-like brows, a high straight nose, well-defined lips, fair neutral skin with natural texture and visible pores; tall athletic yet lean build (183cm) with broad shoulders tapering to a lean waist, commanding upright posture [FACE ANCHOR END]. Short black slightly tousled hair, clean sharp hairline, clean-shaven with sharp jaw definition. Wearing a charcoal-grey henley shirt with sleeves rolled up to the forearms, a faint thin old scar on his left forearm, dark slim trousers, minimalist dark leather shoes, a simple canvas cafe apron tied at the waist. Quiet restrained expression, strikingly handsome with chiseled features and a reserved warmth behind guarded eyes. Shot on 85mm lens, editorial portrait photograph, photorealistic urban realism, modern city of 2026, natural skin texture, shallow depth of field, leave headroom space above his head. " + COMMON_NEG,
  []),
 ("CHAR-003-L01",
  "Photorealistic character reference sheet, full-body wide shot showing the entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single Chinese woman standing upright facing the camera, plain white background, clean flat studio lighting. [FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 25-year-old Chinese woman with a soft rounded oval face, large bright lively eyes with natural sparkle, expressive brows, a small nose, full lips in a wide cheerful smile, warm healthy skin tone with natural texture; petite yet well-proportioned figure (163cm), energetic youthful posture [FACE ANCHOR END]. Chestnut-brown dyed hair in a bouncy high ponytail with a colorful hair clip. Wearing a bright oversized graphic t-shirt, a mustard-yellow cropped cardigan, denim shorts over black leggings, chunky white sneakers, playful layered bracelets. A big animated grin, bubbly warm energy, pretty and approachable. Shot on 85mm lens, editorial portrait photograph, photorealistic urban realism, modern city of 2026, natural skin texture, shallow depth of field, leave headroom space above her head. " + COMMON_NEG,
  []),
 ("CHAR-004-L01",
  "Photorealistic character reference sheet, full-body wide shot showing the entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single Chinese woman standing upright facing the camera, plain white background, clean flat studio lighting. [FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 27-year-old Chinese woman with a delicate heart-shaped face, large doe eyes with a subtly cold appraising gaze, thin softly arched brows, a dainty nose, glossy lips curved into a practiced sweet smile, fair skin with natural texture; slender graceful figure (166cm), poised posture [FACE ANCHOR END]. Long softly-waved chestnut hair, carefully styled. Wearing a soft blush-pink ruffled blouse, a cream pencil skirt, a delicate thin gold necklace, nude low heels. A saccharine sweet smile that never quite reaches her coldly calculating, sizing-up eyes, with a subtle sidelong appraising glance — pretty and deliberately demure yet chillingly insincere. Shot on 85mm lens, editorial portrait photograph, photorealistic urban realism, modern city of 2026, natural skin texture, shallow depth of field, leave headroom space above her head. " + COMMON_NEG,
  []),
 ("CHAR-005-L01",
  "Photorealistic character reference sheet, full-body wide shot showing the entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single Chinese man standing upright facing the camera, plain white background, clean flat studio lighting. [FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 30-year-old Chinese man with a symmetrical slightly soft-angular face, narrow eyes with a shifty restless gaze, neatly groomed brows, a straight nose, thin lips curved in a rehearsed charming smile, fair skin with natural texture; tall slim build (180cm), a slightly slouched self-satisfied posture [FACE ANCHOR END]. Slicked-back over-gelled black hair. Wearing an over-fitted glossy dress shirt with the top buttons undone, a flashy try-hard designer-style jacket (generic, no logo), a chunky metal wristwatch, pointed leather shoes. An over-groomed, over-rehearsed sincere-looking smile that curdles into a smug shifty sidelong glance — smarmy, self-satisfied and insincere yet conventionally handsome. Shot on 85mm lens, editorial portrait photograph, photorealistic urban realism, modern city of 2026, natural skin texture, shallow depth of field, leave headroom space above his head. " + COMMON_NEG,
  []),
 ("CHAR-006-L01",
  "Photorealistic character reference sheet, full-body wide shot showing the entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single Chinese woman standing upright facing the camera, plain white background, clean flat studio lighting. [FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 40-year-old mature Chinese woman with a sharp angular mature face, narrow phoenix eyes with a sharp scrutinizing gaze, sharply sculpted brows, a high straight nose, thin lips pressed into a condescending line, fair skin with mature refined texture and subtle fine lines; tall elegant frame (170cm), rigidly upright commanding posture [FACE ANCHOR END]. A sleek severe dark chin-length bob, not a strand out of place. Wearing a sharp charcoal power suit with structured shoulders over a silk blouse, a single statement gold brooch, minimalist heels. Chin lifted in condescension, a thin patronizing smile paired with cold scrutinizing eyes — corporate power and veiled contempt, elegant and intimidating. Clearly a mature woman in her early forties. Shot on 85mm lens, editorial portrait photograph, photorealistic urban realism, modern city of 2026, cold white office fluorescent undertone, natural skin texture, shallow depth of field, leave headroom space above her head. " + COMMON_NEG,
  []),
 ("CHAR-007-L01",
  "Photorealistic character reference sheet, full-body wide shot showing the entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single Chinese man standing upright facing the camera, plain white background, clean soft studio lighting with a cool sci-tech blue fill. [FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 38-year-old Chinese man with a refined oval-angular face, deep calm eyes carrying a hidden burning intensity, neat straight brows, a straight nose, composed restrained lips, fair skin with natural texture; tall elegant build (182cm), poised refined posture [FACE ANCHOR END]. Neat side-swept dark hair with subtle grey at the temples. Wearing a minimalist fine-knit dark turtleneck under a tailored charcoal blazer, dark trousers, a slim modern watch, sleek leather shoes. A composed charismatic expression — visionary and calm on the surface with an obsessive glint deep in his eyes. Handsome, distinguished and magnetic. Shot on 85mm lens, editorial portrait photograph, photorealistic urban realism, modern city of 2026, low-saturation cool tech-blue accent light, natural skin texture, shallow depth of field, leave headroom space above his head. " + COMMON_NEG,
  []),
 ("CHAR-008-L01",
  "Photorealistic character reference sheet, full-body wide shot showing the entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single Chinese man standing upright facing the camera, plain white background, clean soft clinical studio lighting. [FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 45-year-old mature Chinese man with a kind mature oval face, warm gentle eyes with soft crow's feet, soft brows, a straight nose, a gentle reassuring smile, fair skin with mature natural texture and gentle laugh lines; tall composed build (178cm), calm approachable posture [FACE ANCHOR END]. Neat greying professional side-part hair, clean-shaven. Wearing a white doctor's coat over a light blue collared shirt and a navy tie, a stethoscope around his neck, a blank hospital ID clip (no readable text). A warm, trustworthy, fatherly smile — gentle and reassuring, the very picture of a caring physician. Distinguished and kindly. Shot on 85mm lens, editorial portrait photograph, photorealistic urban realism, modern city of 2026, natural skin texture, shallow depth of field, leave headroom space above his head. " + COMMON_NEG,
  []),
 ("CHAR-009-L01",
  "Photorealistic character reference sheet, full-body wide shot showing the entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single Chinese woman standing upright facing the camera, plain white background, clean soft warm nostalgic studio lighting. [FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 22-year-old Chinese woman with a soft oval face gently resembling her older brother, large warm gentle eyes, soft brows, a small nose, a serene gentle smile, fair skin with youthful natural texture and healthy rosy tone; slender youthful figure (165cm), gentle relaxed posture [FACE ANCHOR END]. Long soft black hair with natural sheen, loosely falling. Wearing a simple warm cream knit sweater, a light beige scarf, simple jeans, white canvas shoes. A warm, serene, peaceful smile — kind, hopeful, healthy and full of life, depicted as a living young woman in a warm archival memory. Strikingly gentle and clear beauty. Shot on 85mm lens, editorial portrait photograph, photorealistic urban realism, natural skin texture, warm soft lighting, shallow depth of field, leave headroom space above her head. Depicted as a healthy LIVING young woman. NOT a ghost, NOT translucent, NOT a spirit, NOT glowing, no supernatural aura, no vertical slit pupils, " + COMMON_NEG,
  []),
 ("CHAR-010-L01",
  "Photorealistic character reference sheet, full-body wide shot showing the entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single Chinese woman standing upright facing the camera, plain white background, clean flat studio lighting. [FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 55-year-old middle-aged Chinese woman with a round warm mature face, kind lively eyes with laugh lines, soft brows, a rounded nose, an animated talkative mouth caught mid-expression, fair mature skin with natural wrinkles and texture; average homely build with natural proportions (158cm), lively energetic posture [FACE ANCHOR END]. A short permed middle-aged hairstyle with natural greying, dark brown. Wearing a floral-print blouse under a warm mauve knit cardigan, comfortable dark trousers, a small crossbody handbag, flat comfortable shoes. A warm, nagging, animated expression with hands slightly gesturing as if mid-scolding-out-of-love, homely and lively. Clearly a woman in her mid-fifties. Shot on 85mm lens, editorial portrait photograph, photorealistic urban realism, modern city of 2026, natural skin texture, shallow depth of field, leave headroom space above her head. " + COMMON_NEG,
  []),
]

def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    ok, fail = [], []
    for cid, prompt, refs in ITEMS:
        if only and only not in cid:
            continue
        out = LOOKS / f"{cid}.png"
        cmd = ["python3", CLI, "generate", "--prompt", prompt,
               "--output", str(out), "--ratio", "9:16", "--size", "1600x2848"]
        for r in refs:
            cmd += ["--image-url", r]
        print(f"=== generating {cid} (refs={len(refs)}) ===", flush=True)
        rc = subprocess.run(cmd).returncode
        if rc == 0 and out.exists():
            ok.append(cid)
        else:
            fail.append((cid, rc))
        print(f"--- {cid} rc={rc} exists={out.exists()} ---", flush=True)
    print("\n==== SUMMARY ====")
    print("OK:", ok)
    print("FAIL:", fail)

if __name__ == "__main__":
    main()
