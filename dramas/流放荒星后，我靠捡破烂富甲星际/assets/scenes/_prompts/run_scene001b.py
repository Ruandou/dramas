#!/usr/bin/env python3
"""SCENE-001B 弹射舱内部 · 增量生成 wrapper（R2-EP01 N2 裁决）
凭据经 drama_env.ensure_credentials 从 mcp.json 注入；Prompt 与 资产/场景卡片.md SCENE-001B 条目逐字一致。
"""
import sys
from pathlib import Path

REPO = Path("/Users/lei/Movies/demo1")
sys.path.insert(0, str(REPO / "mcps/volc-ark/scripts"))
import drama_env  # noqa: E402

drama_env.ensure_credentials(REPO)

PROMPT = (
    "Interior of a cramped single-person ejection pod aboard an interstellar deportation starship, "
    "tight vertical composition with the riveted walls pressing in claustrophobically: "
    "a single metal crash seat with black four-point restraint harness straps mounted at center, "
    "one round porthole on the sealed hatch showing pitch-black starfield outside, "
    "a red strip warning light glowing along the ceiling rendered as a plain luminous color bar with no markings, "
    "rust-streaked iron handrail bars bolted beside the seat, "
    "the inner hatch door painted with yellow-black hazard stripes, "
    "cold riveted metal walls with exposed cable conduits and worn bolt heads, "
    "harsh cold white overhead lighting as the main source with the red warning strip as the only warm-red accent, "
    "faint rust-orange corrosion creeping along weld seams and rivet lines, "
    "scuffed steel floor plating with drag scratches, "
    "oppressive airtight capsule atmosphere before launch. "
    "Cinematic photorealistic sci-fi environment reference, rusted metal textures, dramatic lighting, film grain, "
    "desaturated cold palette with rust-orange accents and red warning glow, vertical 9:16 composition. "
    "Empty interior, no people, no human figures, no faces, no silhouettes, "
    "the warning light and hazard stripes are pure color blocks with no writing, "
    "no text, no lettering, no numbers, no stenciled letters, no signage, "
    "no characters of any language anywhere. NOT inscribed with any characters or text. "
    "No watermark, no logo."
)

OUTPUT = str(
    REPO
    / "dramas/流放荒星后，我靠捡破烂富甲星际/assets/scenes/SCENE-001B.png"
)

sys.argv = [
    "ark_seedream_image.py",
    "generate",
    "--prompt", PROMPT,
    "--output", OUTPUT,
    "--size", "1600x2848",
]
import ark_seedream_image  # noqa: E402

sys.exit(ark_seedream_image.main())
