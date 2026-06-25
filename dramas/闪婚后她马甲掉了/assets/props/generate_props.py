#!/usr/bin/env python3
"""Generate prop reference images using Seedream API."""
import subprocess
import sys
import json
import os

# Load API key from mcp.json
mcp_config = json.load(open('/Users/leifu/Movies/dramas/.cursor/mcp.json'))
os.environ['ARK_API_KEY'] = mcp_config['mcpServers']['volc-ark']['env']['ARK_API_KEY']

SCRIPT = "/Users/leifu/Movies/dramas/mcps/volc-ark/scripts/ark_seedream_image.py"
OUTPUT_DIR = "/Users/leifu/Movies/dramas/dramas/闪婚后她马甲掉了/assets/props"

PROPS = {
    "PROP-001": (
        'Prop reference photograph, single object isolated on warm neutral silk background, '
        'dramatic product lighting with soft shadows. ONE single traditional Chinese acupuncture '
        'needle set in an aged handcrafted rosewood box with lid opened at 45 degrees, revealing '
        'nine polished sterling silver needles of varying lengths neatly arranged in parallel slots '
        'on deep burgundy silk lining inside. The box lid exterior features intricate hand-carved '
        'peony motifs in low relief, with the characters "回阳" inlaid in gold leaf using regular '
        'script (楷书) prominently displayed on the lid surface. The rosewood surface shows rich '
        'dark reddish-brown patina from years of careful handling, subtle wear on carved edges, and '
        'fine micro-scratches on the polished wood. Box dimensions approximately 20cm long by 10cm '
        'wide, compact and elegant. Warm-toned directional lighting emphasizing wood grain texture '
        'and silver needle reflections. Photorealistic product photography, shot on macro lens, '
        'natural material textures, commercial product shot, studio lighting. NOT inscribed with any '
        'other characters or text besides what is specified, photorealistic, cinematic lighting, '
        '9:16 vertical frame, urban luxury aesthetic, shallow depth of field, modern Chinese city '
        'setting. Vertical 9:16, detailed prop reference sheet.'
    ),
    "PROP-003": (
        'Prop reference photograph, single object isolated on warm neutral silk background, '
        'dramatic product lighting with soft shadows. ONE single premium black VIP card made of '
        'matte black brushed titanium metal, credit card sized and shaped with slightly rounded '
        'corners. The front face features a single elegant embossed letter "L" in polished chrome '
        'finish, centered on the card surface, catching specular highlights. The card has subtle '
        'beveled edges with a thin polished chrome line trim along the perimeter. The back face '
        'shows a minimal matte black surface with a barely visible magnetic stripe. The metal '
        'surface displays fingerprint-free matte texture with selective mirror-like highlights on '
        'the raised "L" letter. Slight angle showing card thickness of approximately 1mm, conveying '
        'premium weight and luxury quality. Warm-toned directional lighting emphasizing brushed '
        'metal texture and chrome letter reflections. Photorealistic product photography, shot on '
        'macro lens, natural material textures, commercial product shot, studio lighting. '
        'photorealistic, cinematic lighting, 9:16 vertical frame, urban luxury aesthetic, shallow '
        'depth of field, modern Chinese city setting. Vertical 9:16, detailed prop reference sheet.'
    ),
    "PROP-004": (
        'Prop reference photograph, single object isolated on warm neutral silk background, '
        'dramatic product lighting with soft shadows. ONE single modern smartphone with a sleek '
        'matte black protective case, lying flat at a slight three-quarter angle showing the screen. '
        'The screen displays an encrypted secure messaging application interface with dark navy blue '
        'background, showing a minimalist lock icon at the top center, abstract geometric shield '
        'patterns in cool blue tones, encrypted text message bubbles represented by blurred '
        'horizontal lines suggesting redacted content, and a numeric PIN entry keypad at the bottom '
        'of the screen. No human faces, no photographs, no portraits visible anywhere on the screen '
        'display. The phone body has a standard modern design with slim bezels and a small front '
        'camera notch. Screen emits a subtle cool blue glow against the warm silk background, '
        'contrasting with the warm ambient lighting. Warm-toned product lighting with screen light '
        'adding secondary cool illumination. Photorealistic product photography, shot on macro lens, '
        'natural material textures, commercial product shot, studio lighting. photorealistic, '
        'cinematic lighting, 9:16 vertical frame, urban luxury aesthetic, shallow depth of field, '
        'modern Chinese city setting. Vertical 9:16, detailed prop reference sheet.'
    ),
    "PROP-005": (
        'Prop reference photograph, single object isolated on warm neutral silk background, '
        'dramatic product lighting with soft shadows. ONE single high-end motorized electric '
        'wheelchair with a sleek matte black powder-coated aluminum alloy frame. Premium black '
        'genuine leather seat cushion and backrest with diamond-pattern quilted stitching and subtle '
        'embossed detail. Black padded armrests with integrated joystick controller on the right '
        'side featuring a small LED status indicator light. Two large rear motorized wheels with '
        'polished chrome hub caps and black rubber tires, two smaller front caster wheels for '
        'maneuverability. Compact foldable footrests in matching black metal. The wheelchair presents '
        'a sophisticated modern medical device aesthetic with luxury automotive-level craftsmanship, '
        'clean industrial design lines. Slight three-quarter front angle showing full wheelchair '
        'structure and premium build quality. Dramatic warm-toned directional lighting emphasizing '
        'the leather texture, chrome hub reflections, and matte black metal surface finish. '
        'Photorealistic product photography, shot on wide-angle macro lens, natural material '
        'textures, commercial product shot, studio lighting. No person sitting in the wheelchair, '
        'empty seat only. photorealistic, cinematic lighting, 9:16 vertical frame, urban luxury '
        'aesthetic, shallow depth of field, modern Chinese city setting. Vertical 9:16, detailed '
        'prop reference sheet.'
    ),
    "PROP-006": (
        'Prop reference photograph, single object isolated on warm neutral silk background, '
        'dramatic product lighting with soft shadows. ONE single aged leather-bound journal notebook '
        'with a distressed tan cowhide cover showing visible signs of aging including yellowed '
        'discoloration, slight warping from moisture exposure over years, and softened edges from '
        'frequent handling. The cover has a simple debossed rectangular border frame with no title '
        'or text. Cream-colored thick paper pages visible at the edges, some pages slightly '
        'dog-eared and curled at corners. A faded dark brown cotton ribbon bookmark extends from '
        'between the pages. The notebook is shown at a slight three-quarter angle, partially open '
        'revealing handwritten cursive ink impressions visible on the top page in dark blue ink with '
        'Simplified Chinese characters. Pages show foxing spots, slight yellowing from age, and '
        'gentle waviness. Approximately 20cm by 14cm in size, conveying a personal intimate diary. '
        'Warm-toned directional lighting emphasizing leather grain texture, page edge detail, and '
        'the aged patina of a treasured keepsake stored away for many years. Photorealistic product '
        'photography, shot on macro lens, natural material textures, commercial product shot, studio '
        'lighting. photorealistic, cinematic lighting, 9:16 vertical frame, urban luxury aesthetic, '
        'shallow depth of field, modern Chinese city setting. Vertical 9:16, detailed prop '
        'reference sheet.'
    ),
    "PROP-007": (
        'Prop reference photograph, single object isolated on warm neutral silk background, '
        'dramatic product lighting with soft shadows. ONE single antique Chinese jade pendant paired '
        'with a jadeite necklace, displayed together as a mother\'s precious keepsake set. The jade '
        'pendant is a smooth oval-shaped translucent nephrite jade disc in deep celadon green with '
        'subtle warm honey-brown natural veining, approximately 5cm across, with a small circular '
        'hole at the top for threading. The character "方" is carved in Simplified Chinese regular '
        'script (楷书) on the face of the pendant, showing fine craftsmanship with clean precise '
        'strokes. A faded dark red silk cord is threaded through the pendant hole. Beside the '
        'pendant lies a delicate jadeite pendant necklace featuring a teardrop-shaped translucent '
        'imperial green jadeite pendant with glass-like luster and internal light refraction, '
        'suspended on a fine 18-karat yellow gold chain with small round jade bead accents spaced '
        'evenly along the chain length. No human faces, no portraits, no photographs of people '
        'visible anywhere in the composition. Warm-toned directional lighting emphasizing the '
        'translucent jade quality, internal color gradients, and gold chain reflections. '
        'Photorealistic product photography, shot on macro lens, natural material textures, '
        'commercial product shot, studio lighting. NOT inscribed with any other characters or text '
        'besides what is specified. photorealistic, cinematic lighting, 9:16 vertical frame, urban '
        'luxury aesthetic, shallow depth of field, modern Chinese city setting. Vertical 9:16, '
        'detailed prop reference sheet.'
    ),
    "PROP-010": (
        'Prop reference photograph, single object isolated on warm neutral silk background, '
        'dramatic product lighting with soft shadows. ONE single black genuine leather journal '
        'notebook with a smooth, well-preserved dark cover showing minimal wear — distinctly modern '
        'and more formal than a rustic old diary. A small integrated combination lock clasp in '
        'brushed gunmetal gray is mounted on the front cover edge, with visible numbered cipher '
        'dials showing a 4-digit code mechanism. The cover has a subtle debossed geometric grid '
        'pattern on the lower right corner suggesting encrypted data organization. Cream-colored '
        'pages visible at the edges, some pages showing columns of handwritten numeric cipher '
        'sequences alternating with handwritten Simplified Chinese notes in black fountain pen ink. '
        'A thin black elastic closure band wraps around the cover. Approximately 22cm by 15cm in '
        'size. The overall aesthetic is modern, secretive, and intellectual — a coded intelligence '
        'journal, not a sentimental personal diary. Warm-toned directional lighting emphasizing the '
        'smooth black leather grain texture, gunmetal lock mechanism detail, and page edge contrast. '
        'Photorealistic product photography, shot on macro lens, natural material textures, '
        'commercial product shot, studio lighting. photorealistic, cinematic lighting, 9:16 vertical '
        'frame, urban luxury aesthetic, shallow depth of field, modern Chinese city setting. '
        'Vertical 9:16, detailed prop reference sheet.'
    ),
}

def generate_prop(prop_id, prompt):
    output_path = os.path.join(OUTPUT_DIR, f"{prop_id}.png")
    print(f"\n{'='*60}")
    print(f"Generating {prop_id} -> {output_path}")
    print(f"{'='*60}")
    
    cmd = [
        sys.executable, SCRIPT, "generate",
        "--prompt", prompt,
        "--ratio", "9:16",
        "--output", output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print(f"STDOUT: {result.stdout}")
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    print(f"Return code: {result.returncode}")
    
    if result.returncode == 0 and os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"✅ {prop_id} generated successfully ({size} bytes)")
        return True
    else:
        print(f"❌ {prop_id} generation failed")
        return False

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    results = {}
    for prop_id, prompt in PROPS.items():
        success = generate_prop(prop_id, prompt)
        results[prop_id] = success
    
    print(f"\n{'='*60}")
    print("GENERATION SUMMARY")
    print(f"{'='*60}")
    for prop_id, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {prop_id}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n  Total: {passed}/{total} successful")
