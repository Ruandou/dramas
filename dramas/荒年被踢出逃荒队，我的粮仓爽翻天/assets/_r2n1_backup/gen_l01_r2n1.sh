#!/bin/zsh
# R2-N1: CHAR-001-L01 重制（移除腰挂账本 PROP-009，同脸锚定旧 L01）
# Prompt 逐字复制自 资产/角色卡片.md CHAR-001-L01 定妆 Prompt（R2-N1 修订版）
set -e
cd "/Users/lei/Movies/demo1/dramas/荒年被踢出逃荒队，我的粮仓爽翻天"

PROMPT='Photorealistic costume reference, wide shot showing entire figure from head to toe with feet and shoes clearly visible at the bottom edge of the frame, single person standing upright facing the camera, plain white background, clean flat studio lighting, full body fully visible, not cropped. SAME person as the reference image, keep the SAME face, same facial proportions, same identity. An 18-year-old Chinese young woman from a famine-stricken farming village, strikingly beautiful despite hardship — beneath the light road dust an unmistakably delicate and lovely face. [FACE ANCHOR START] perfectly symmetrical facial features, level lip line, centered features; slim oval face with a softly pointed chin; large bright almond-shaped eyes with dark-brown irises, clear determined gaze with natural catchlight in the eyes; straight neat dark eyebrows; small straight nose; soft full lips held level and symmetrical; fair skin with natural texture; tall willowy near-adult figure (165cm) with slim waist and upright poised posture [FACE ANCHOR END] Cheeks very slightly hollowed by hunger, complexion faintly dulled by loess dust yet clear. Black hair combed into one simple low bun at the back of her head, a few loose strands at the temples, the bun secured with ONE single slender warm honey-brown wooden hairpin whose flat oval head bears a raised carved wheat-ear relief, exactly the same wooden hairpin as in the reference image, only one, singular. Wearing a patched coarse hemp blouse and long skirt in low-saturation loess-grey and dull earth-brown, narrow cloth waistband tied plainly with NOTHING hanging from it — no book, no ledger, no pouch, no cord, the waistband and both hips completely bare and empty; both arms relaxed naturally at her sides, empty hands holding nothing; worn cloth shoes. Calm steady expression with quiet resolve. Vertical 9:16 photorealistic costume reference, ancient East Asian famine-era farming period drama, fictional dynasty, Ming-adjacent folk costume, no real-dynasty reference, realistic photograph, editorial portrait photograph, shot on 85mm lens, natural skin texture with visible pores, no modern objects, NOT anime, NOT cartoon, NOT illustration, NOT manga, NO ledger book, NO hanging book at the waist, NO text on clothing.'

REF_L01='https://drama-reference-images.tos-cn-beijing.volces.com/looks/%E8%8D%92%E5%B9%B4%E8%A2%AB%E8%B8%A2%E5%87%BA%E9%80%83%E8%8D%92%E9%98%9F%EF%BC%8C%E6%88%91%E7%9A%84%E7%B2%AE%E4%BB%93%E7%88%BD%E7%BF%BB%E5%A4%A9/CHAR-001-L01.png'

python3 /Users/lei/Movies/demo1/mcps/volc-ark/scripts/ark_seedream_image.py generate \
  --prompt "$PROMPT" \
  --image-url "$REF_L01" \
  --output assets/looks/CHAR-001-L01.png \
  --size 1600x2848 \
  --project-root . \
  "$@"
