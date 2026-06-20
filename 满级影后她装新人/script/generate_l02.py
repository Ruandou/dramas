#!/usr/bin/env python3
"""Generate L02+ derivative character images using L01 TOS URLs as face reference."""
import subprocess, sys, os

PROJ = "/Users/leifu/Movies/dramas/满级影后她装新人"
CLI = "/Users/leifu/Movies/dramas/mcps/volc-ark/scripts/ark_seedream_image.py"
os.environ["ARK_API_KEY"] = "973a9b4b-2975-4e57-ae08-4c18fd2e2f58"

TOS_BASE = "https://drama-reference-images.tos-cn-beijing.volces.com/looks/满级影后她装新人"
PROP_TOS_BASE = "https://drama-reference-images.tos-cn-beijing.volces.com/props/满级影后她装新人"

FACE_001 = "perfectly symmetrical facial features, level lip line, centered features, refined oval face with delicate pointed chin, large expressive almond-shaped eyes with deep brown irises and natural catchlight, slightly upswept eye corners, natural thin softly arched eyebrows, high straight nose bridge with a subtle upturned tip, thin lips with natural rose tint and symmetrically slightly upturned corners, fair skin with cool undertone and natural texture visible at close range."
FACE_002 = "perfectly symmetrical facial features, level lip line, centered features, angular face with strong defined jawline, narrow phoenix eyes with deep black irises and sharp piercing gaze, thick straight sword-like eyebrows, high straight nose bridge with clean line, thin lips naturally pressed together with neutral expression, clear healthy complexion with natural skin texture visible at close range."
FACE_003 = "perfectly symmetrical facial features, level lip line, centered features, elegant oval face with high refined cheekbones, large almond-shaped eyes with deep brown irises and a sharp calculating look beneath the warm surface, perfectly groomed high-arched eyebrows, straight refined nose with delicate tip, full lips painted in rose-mauve lipstick showing a practiced perfect smile with visible teeth, fair flawless skin with meticulous makeup foundation visible at close range."

STYLE_SUFFIX = "Vertical 9:16, photorealistic costume reference, contemporary urban realism, shot on 85mm lens, butterfly lighting with beauty dish, natural skin texture with visible pores, editorial portrait photograph, realistic photograph, NOT anime, NOT cartoon, NOT illustration, NOT manga."
STYLE_SUFFIX_VINTAGE = "Vertical 9:16, desaturated warm vintage tone, soft vignette, 2010s era clothing, slightly grainy film texture, nostalgic mood, photorealistic, shot on 85mm lens, natural skin texture, realistic photograph, NOT anime, NOT cartoon, NOT illustration, NOT manga."
STYLE_SUFFIX_REMBRANDT = "Vertical 9:16, photorealistic costume reference, contemporary urban realism, shot on 85mm lens, golden hour warm directional light, natural skin texture with visible pores, editorial portrait photograph, realistic photograph, NOT anime, NOT cartoon, NOT illustration, NOT manga."

tasks = [
    {
        "id": "CHAR-001-L02",
        "name": "苏念晚 · 真实身份·影后",
        "image_urls": [f"{TOS_BASE}/CHAR-001-L01.png"],
        "output": "assets/looks/CHAR-001-L02.png",
        "prompt": f"Photorealistic costume reference, wide shot showing entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single person standing upright facing the camera, plain white background, clean flat studio lighting. Full body fully visible, not cropped. The SAME person as the reference image, a 28-year-old Chinese woman, now with long straight black hair cascading past shoulders with natural volume and silky highlights, confident poised expression with a knowing subtle look in her deep brown eyes. [FACE ANCHOR] {FACE_001} [FACE ANCHOR END] Tall and slender with graceful feminine proportions (167cm), slim waist, elegant upright posture with commanding actress bearing. Wearing a fitted black midi dress with three-quarter sleeves, V-neckline, sleek silhouette, silver stud earrings, black stiletto heels, a thin silver chain bracelet on the left wrist. Confident glamorous actress energy, the transformation from plain trainee to stunning star. Plain white background maintained. {STYLE_SUFFIX}"
    },
    {
        "id": "CHAR-001-L03",
        "name": "苏念晚 · 闪回·18岁封后",
        "image_urls": [f"{TOS_BASE}/CHAR-001-L01.png"],
        "output": "assets/looks/CHAR-001-L03.png",
        "prompt": f"Photorealistic costume reference, wide shot showing entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single person standing upright facing the camera, plain white background, clean flat studio lighting. Full body fully visible, not cropped. The SAME person as the reference image, now appearing younger at 18 years old, bright youthful eyes with innocent joyful sparkle, softer rounder cheeks of adolescence, radiant fresh-faced beauty. [FACE ANCHOR] {FACE_001} [FACE ANCHOR END] Long straight black hair pulled into a high ponytail with a white ribbon. Slender youthful figure (167cm) with energetic posture. Wearing a simple white cotton summer dress with short puff sleeves, white flat shoes, holding ONE single golden trophy statuette in both hands at chest level, a gold-plated female figurine holding a star aloft on a dark wood base, only one trophy, no duplicates. Bright beaming smile of a young girl at the peak of her dreams. Plain white background maintained. {STYLE_SUFFIX_VINTAGE}"
    },
    {
        "id": "CHAR-001-L04",
        "name": "苏念晚 · 白色礼服·红毯回归",
        "image_urls": [f"{TOS_BASE}/CHAR-001-L01.png", f"{PROP_TOS_BASE}/PROP-009.png"],
        "output": "assets/looks/CHAR-001-L04.png",
        "prompt": f"Photorealistic costume reference, wide shot showing entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single person standing upright facing the camera, plain white background, clean flat studio lighting. Full body fully visible, not cropped. The SAME person as the reference image, a 28-year-old Chinese woman, now with long straight black hair styled in loose waves over one shoulder, calm confident expression with eyes that carry ten years of resilience and quiet determination. [FACE ANCHOR] {FACE_001} [FACE ANCHOR END] Tall and slender with graceful feminine proportions (167cm), slim waist, elegant poised posture. Wearing ONE single white floor-length formal evening gown, luxurious silk satin fabric with subtle pearl-like sheen, fitted bodice with delicate crystal beading along the neckline, flowing A-line skirt with a modest train (matching PROP-009 white gown design), small crystal drop earrings, red stiletto heels. Red carpet glamour, triumphant return energy. Plain white background maintained. {STYLE_SUFFIX}"
    },
    {
        "id": "CHAR-002-L02",
        "name": "陆景深 · 休闲/私人",
        "image_urls": [f"{TOS_BASE}/CHAR-002-L01.png"],
        "output": "assets/looks/CHAR-002-L02.png",
        "prompt": f"Photorealistic costume reference, wide shot showing entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single person standing upright facing the camera, plain white background, clean flat studio lighting. Full body fully visible, not cropped. The SAME person as the reference image, a 30-year-old Chinese man, now with a softer relaxed expression, the icy aura melted into quiet warmth, a faint hint of a smile at the lip corners. [FACE ANCHOR] {FACE_002} [FACE ANCHOR END] Tall athletic build (183cm) with broad shoulders and lean frame, relaxed natural posture. Wearing a loose white linen button-up shirt with sleeves rolled to the elbows, khaki casual trousers, white minimalist sneakers, no accessories. Casual private look, the rare soft side of a cold man. Plain white background maintained. {STYLE_SUFFIX_REMBRANDT}"
    },
    {
        "id": "CHAR-003-L02",
        "name": "方芷晴 · 崩溃状态",
        "image_urls": [f"{TOS_BASE}/CHAR-003-L01.png"],
        "output": "assets/looks/CHAR-003-L02.png",
        "prompt": f"Photorealistic costume reference, wide shot showing entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single person standing upright facing the camera, plain white background, clean flat studio lighting. Full body fully visible, not cropped. The SAME person as the reference image, a 32-year-old Chinese woman, now in a state of emotional breakdown, red puffy eyes with smeared black eyeliner running down the cheeks, lipstick smudged and blurred, foundation cracked showing flushed skin underneath, hair disheveled with curls falling apart in messy strands, expression of desperation and rage. [FACE ANCHOR] {FACE_003} [FACE ANCHOR END] Tall and slender figure (170cm), hunched defeated posture. Wearing the same wine-red velvet blazer dress but now wrinkled and disheveled, one earring missing, shoes scuffed. The glamorous facade completely shattered. Plain white background maintained. {STYLE_SUFFIX}"
    },
]

for i, task in enumerate(tasks):
    output_path = os.path.join(PROJ, task["output"])
    cmd = [sys.executable, CLI, "generate",
           "--prompt", task["prompt"],
           "--output", output_path,
           "--ratio", "9:16",
           "--project-root", PROJ]
    for url in task["image_urls"]:
        cmd.extend(["--image-url", url])
    
    print(f"\n{'='*60}")
    print(f"[{i+1}/{len(tasks)}] Generating {task['id']} — {task['name']}")
    print(f"  Reference URLs: {task['image_urls']}")
    print(f"  Output: {output_path}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0 and os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"✅ {task['id']} generated successfully ({size:,} bytes)")
    else:
        print(f"❌ {task['id']} FAILED (exit code: {result.returncode})")

print(f"\n{'='*60}")
print(f"L02+ generation complete. {len(tasks)} tasks processed.")
