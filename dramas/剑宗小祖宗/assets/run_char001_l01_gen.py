#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CHAR-001-L01 3-candidate generator (Stage 3b-G).
Reads GPT_IMAGE_API_KEY from .cursor/mcp.json without printing it.
Run from workspace root: python3 dramas/剑宗小祖宗/assets/run_char001_l01_gen.py
"""
import json
import os
import subprocess
import sys

ROOT = "/Users/lei/Movies/demo1"

BASE = (
    "Photorealistic costume reference, wide shot showing the entire figure from head to toe "
    "with feet and shoes clearly visible at the bottom edge of the frame, single person standing "
    "upright facing the camera, plain white background, clean flat studio lighting. Full body "
    "fully visible, not cropped. A 3-and-a-half-year-old Chinese toddler girl, an adorable plump "
    "baby heroine, clearly a toddler not an infant, standing upright on her own two feet with "
    "sturdy little toddler posture. [FACE ANCHOR START] perfectly symmetrical facial features, "
    "level lip line, centered features, round face with soft chubby toddler cheeks, large bright "
    "round sparkling eyes with natural catchlight, soft fine baby eyebrows, small button nose, "
    "small rosy lips, fair soft baby skin with natural healthy glow, tiny toddler stature about "
    "95cm tall with plump rounded build, chubby little hands and feet with dimpled knuckles "
    "[FACE ANCHOR END]. Hairstyle: twin round topknot buns on both sides of her head, soft fluffy "
    "baby hairs framing the round face, bright candy-pink small silk flower hair ties and a tiny "
    "spring-green ribbon bow on each bun (candy-color accents). Costume: wearing a small "
    "pale-pink-and-white xianxia sect toddler robe, pale pink upper robe with white collar trim "
    "and a tiny embroidered white cloud pattern on the chest, white pleated mini skirt below, thin "
    "pale-green cloth sash at the waist, tiny soft-soled white cloth shoes with small pink "
    "pom-poms. Accessories: ONE single small silver jingle bell tied at the chest with a thin red "
    "cord (only one, singular, no duplicates); her right hand gently open near her chest revealing "
    "a faint light-blue raindrop-shaped spirit mark on the palm (subtle tiny mark). "
)

SUFFIX = (
    "ancient Chinese xianxia fantasy, bright warm golden tones with spring green accents, cute "
    "candy-color accents on the baby heroine, soft bright atmosphere, comedic tone over "
    "oppression, cinematic lighting, high detail, 9:16 vertical composition. shot on 85mm lens, "
    "editorial portrait photograph, natural soft baby skin texture with fine realistic detail, "
    "soft natural catchlight in eyes, indistinguishable from a real photograph. Vertical 9:16, "
    "photorealistic costume reference, NOT anime, NOT cartoon, NOT illustration, NOT manga, NOT "
    "chibi, NOT deformed, no watermark, no logo, no modern objects, no english text."
)

CANDIDATES = [
    ("CHAR-001-L01-cand1", "bright cheerful giggling smile, rosy cheeks, eyes curved with joy"),
    ("CHAR-001-L01-cand2",
     "curious wide-eyed innocent look, head slightly tilted, mouth slightly open in wonder, "
     "right hand held palm-up in front of her showing the raindrop spirit mark"),
    ("CHAR-001-L01-cand3",
     "sweet gentle shy smile, both hands clasped in front of her chest, the raindrop spirit mark "
     "subtly visible on the right palm"),
]


def main():
    with open(os.path.join(ROOT, ".cursor/mcp.json")) as f:
        mcp = json.load(f)
    api_key = mcp["mcpServers"]["gpt-image"]["env"]["GPT_IMAGE_API_KEY"]

    env = dict(os.environ)
    env["GPT_IMAGE_API_KEY"] = api_key
    env["GPT_IMAGE_RESPONSE_FORMAT"] = "none"
    env["ARK_ALLOW_FORCE"] = "1"

    cli = os.path.join(ROOT, "mcps/gpt-image/scripts/gpt_image.py")
    failed = []
    for name, expr in CANDIDATES:
        prompt = BASE + "Expression: " + expr + ". " + SUFFIX
        out = os.path.join(ROOT, f"dramas/剑宗小祖宗/assets/looks/{name}.png")
        cmd = [
            sys.executable, cli, "generate",
            "--prompt", prompt,
            "--output", out,
            "--model", "gpt-image-2",
            "--size", "1600x2848",
            "--force",
        ]
        print(f"=== Generating {name} ...", flush=True)
        r = subprocess.run(cmd, env=env, cwd=ROOT, capture_output=True, text=True)
        print(r.stdout[-3000:] if r.stdout else "", flush=True)
        if r.stderr:
            print("STDERR:", r.stderr[-2000:], flush=True)
        if r.returncode != 0 or not os.path.exists(out):
            failed.append(name)
            print(f"!!! {name} FAILED rc={r.returncode}", flush=True)
        else:
            print(f"OK {name} -> {out} ({os.path.getsize(out)} bytes)", flush=True)
    print("DONE failed:", failed or "none")


if __name__ == "__main__":
    main()
