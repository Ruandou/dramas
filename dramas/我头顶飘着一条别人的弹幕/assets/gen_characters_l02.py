#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 2 L02 variant generation runner — 我头顶飘着一条别人的弹幕 (Stage 3b character-designer).
HARD GATE: every L02 passes its character's L01 TOS URL via --image-url as face anchor.
Prompts copied verbatim from 资产/角色卡片.md (source of truth).
"""
import subprocess, sys, os, json
from pathlib import Path

ROOT = Path("/Users/leifu/Movies/dramas/dramas/我头顶飘着一条别人的弹幕")
REPO = Path("/Users/leifu/Movies/dramas")
CLI = "/Users/leifu/Movies/dramas/mcps/volc-ark/scripts/ark_seedream_image.py"
LOOKS = ROOT / "assets" / "looks"


def bootstrap_credentials():
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
    if not os.environ.get("ARK_API_KEY") and os.environ.get("VOLC_ARK_API_KEY"):
        os.environ["ARK_API_KEY"] = os.environ["VOLC_ARK_API_KEY"]


bootstrap_credentials()

# L01 face-reference TOS URLs (hard gate)
L01_001 = "https://drama-reference-images.tos-cn-beijing.volces.com/looks/我头顶飘着一条别人的弹幕/CHAR-001-L01.png"
L01_008 = "https://drama-reference-images.tos-cn-beijing.volces.com/looks/我头顶飘着一条别人的弹幕/CHAR-008-L01.png"

COMMON_NEG = ("NOT anime, NOT cartoon, NOT illustration, NOT manga, no ghost, no supernatural glow, "
              "no floating on-screen text, no danmaku text, no watermark, no burned-in subtitles.")

ITEMS = [
 ("CHAR-001-L02",
  "[FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 26-year-old Chinese woman with an oval face, large expressive almond-shaped eyes with natural catchlight, soft gently arched brows, a delicate straight nose, full rosy lips, fair luminous skin with natural texture and visible pores; tall and slender with graceful feminine proportions (168cm), slim waist, elegant upright posture [FACE ANCHOR END]. SAME person as the reference image, keep the SAME face, identical facial features. Full-body wide shot from head to toe, feet visible, plain white background maintained, clean studio lighting. Now with a confident sharp expression, a knowing slight smile and bright determined eyes; hair styled sleeker and neater. Wearing a sharply tailored dark blazer over a silk camisole, high-waisted trousers, subtle bolder makeup, a confident power stance. Strikingly beautiful, refined, commanding presence. Shot on 85mm lens, editorial portrait photograph, photorealistic urban realism, natural skin texture, shallow depth of field, leave headroom space above her head. " + COMMON_NEG,
  L01_001),
 ("CHAR-008-L02",
  "[FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; a 45-year-old mature Chinese man with a kind mature oval face, warm gentle eyes with soft crow's feet, soft brows, a straight nose, fair skin with mature natural texture and gentle laugh lines; tall composed build (178cm) [FACE ANCHOR END]. SAME person as the reference image, keep the SAME face, identical facial features. Full-body wide shot from head to toe, feet visible, plain white background maintained, cold hard directional studio lighting. Now the warm mask is gone — a cold flat obsessive stare, a thin humorless pressed smile, hard fixated eyes with a subtly deranged intensity, deep nasolabial folds and clenched jaw muscles visible under the skin. Still wearing the white doctor's coat, now slightly dishevelled with the collar loosened and top button undone, standing rigidly. Shot on 85mm lens, editorial portrait photograph, photorealistic, natural skin texture with visible pores, subsurface scattering, shallow depth of field, leave headroom space above his head. " + COMMON_NEG,
  L01_008),
]


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    ok, fail = [], []
    for cid, prompt, ref in ITEMS:
        if only and only not in cid:
            continue
        out = LOOKS / f"{cid}.png"
        cmd = ["python3", CLI, "generate", "--prompt", prompt,
               "--output", str(out), "--ratio", "9:16", "--size", "1600x2848",
               "--image-url", ref]
        print(f"=== generating {cid} (face-ref={ref.split('/')[-1]}) ===", flush=True)
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
