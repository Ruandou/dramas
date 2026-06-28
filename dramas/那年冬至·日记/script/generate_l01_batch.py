#!/usr/bin/env python3
"""Batch generate L01 character images from seedream_batch_characters.yaml"""
import yaml, subprocess, sys, os, time

PROJECT_ROOT = "/Users/leifu/Movies/dramas/dramas/那年冬至·日记"
BATCH_YAML = os.path.join(PROJECT_ROOT, "assets/seedream_batch_characters.yaml")
SCRIPT = "/Users/leifu/Movies/dramas/mcps/volc-ark/scripts/ark_seedream_image.py"

def main():
    with open(BATCH_YAML) as f:
        data = yaml.safe_load(f)

    items = data["items"]
    total = len(items)
    success = 0
    failed = []

    for i, item in enumerate(items):
        output = os.path.join(PROJECT_ROOT, item["output"])
        # Skip if already exists
        if os.path.exists(output) and os.path.getsize(output) > 10000:
            print(f"[{i+1}/{total}] SKIP {item['id']} ({item['name']}) - already exists")
            success += 1
            continue

        print(f"[{i+1}/{total}] Generating {item['id']} ({item['name']})...")

        cmd = [
            sys.executable, SCRIPT, "generate",
            "--prompt", item["prompt"],
            "--output", output,
            "--ratio", "9:16"
        ]

        # Add image_urls if present
        if item.get("image_urls"):
            for url in item["image_urls"]:
                cmd.extend(["--image-url", url])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                print(f"  ✅ {item['id']} generated")
                success += 1
            else:
                print(f"  ❌ {item['id']} failed: {result.stderr[-200:]}")
                failed.append(item['id'])
        except subprocess.TimeoutExpired:
            print(f"  ⏰ {item['id']} timeout")
            failed.append(item['id'])

        time.sleep(1)  # Rate limit

    print(f"\n{'='*50}")
    print(f"Done: {success}/{total} success, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")

if __name__ == "__main__":
    main()
