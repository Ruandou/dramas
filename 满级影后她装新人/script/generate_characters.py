#!/usr/bin/env python3
"""Generate all L01 character reference images from batch YAML."""
import subprocess, sys, os, yaml

PROJ = "/Users/leifu/Movies/dramas/满级影后她装新人"
YAML_PATH = os.path.join(PROJ, "assets/seedream_batch_characters.yaml")
CLI = "/Users/leifu/Movies/dramas/mcps/volc-ark/scripts/ark_seedream_image.py"

os.environ["ARK_API_KEY"] = "973a9b4b-2975-4e57-ae08-4c18fd2e2f58"

with open(YAML_PATH) as f:
    data = yaml.safe_load(f)

start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
end_idx = int(sys.argv[2]) if len(sys.argv) > 2 else len(data["items"])

items = data["items"][start_idx:end_idx]
print(f"Generating items {start_idx} to {end_idx-1} ({len(items)} images)")

for i, item in enumerate(items):
    idx = start_idx + i
    print(f"\n{'='*60}")
    print(f"[{idx+1}/{len(data['items'])}] {item['id']}: {item['name']}")
    print(f"{'='*60}")
    
    output_path = os.path.join(PROJ, item["output"])
    
    cmd = [
        sys.executable, CLI, "generate",
        "--prompt", item["prompt"],
        "--output", output_path,
        "--ratio", "9:16",
        "--project-root", PROJ,
    ]
    
    # Add image_urls if present
    if item.get("image_urls"):
        for url in item["image_urls"]:
            cmd.extend(["--image-url", url])
    
    print(f"Output: {output_path}")
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ {item['id']} generated successfully")
    else:
        print(f"❌ {item['id']} FAILED (exit code {result.returncode})")

print(f"\n{'='*60}")
print("Batch generation complete!")
