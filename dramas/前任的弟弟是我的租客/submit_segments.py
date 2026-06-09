#!/usr/bin/env python3
"""Submit EP01 SEG04-SEG14 to Seedance API."""
import subprocess, sys, yaml, os, json

ARK_API_KEY = "973a9b4b-2975-4e57-ae08-4c18fd2e2f58"
PROJECT_ROOT = "/Users/lei/Movies/demo1/dramas/前任的弟弟是我的租客"
SCRIPT = "/Users/lei/Movies/demo1/mcps/volc-ark/scripts/ark_seedance_video.py"
SEGMENTS_YAML = os.path.join(PROJECT_ROOT, "剧本/EP01/EP01_segments.yaml")

def main():
    target = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    # SEG01-SEG03 already done; only submit SEG04-SEG14 now
    default_skip = {'SEG01', 'SEG02', 'SEG03'}
    if target is None:
        target = {'SEG04','SEG05','SEG06','SEG07','SEG08','SEG09','SEG10','SEG11','SEG12','SEG13','SEG14'}

    with open(SEGMENTS_YAML) as f:
        data = yaml.safe_load(f)

    segments = data.get('segments', data) if isinstance(data, dict) else data

    for seg in segments:
        sid = seg['seg_id']
        if sid in default_skip:
            continue
        if sid not in target:
            continue

        # Determine mode
        mode = seg.get('mode', 'i2v_ref')
        is_t2v = (mode == 't2v')

        # Build command
        cmd = [
            'python3', SCRIPT, 'create',
            '--model', 'doubao-seedance-2-0-fast-260128',
            '--ratio', '9:16',
            '--resolution', '720p',
            '--duration', str(seg['duration_sec']),
            '--generate-audio',
            '--project-root', PROJECT_ROOT,
        ]

        # Add reference images for i2v_ref mode
        if not is_t2v:
            api_cfg = seg.get('api', {})
            content_roles = api_cfg.get('content_roles', [])
            assets = seg.get('assets', {})
            look_urls = assets.get('look_urls', {})
            scene_urls = assets.get('scene_urls', {})

            # Add images in order from content_roles
            for cr in content_roles:
                fid = cr['file']
                if fid.startswith('CHAR-') or fid.startswith('SCENE-'):
                    # Determine if it's a look or scene
                    if fid in look_urls:
                        url = look_urls[fid]
                    elif fid in scene_urls:
                        url = scene_urls[fid]
                    else:
                        continue
                    cmd.extend(['--image-url', url])
                # else: could be PROP, skip for now

        # Add text prompt directly
        text = seg['api']['text']
        cmd.extend(['--text', text])

        env = os.environ.copy()
        env['ARK_API_KEY'] = ARK_API_KEY
        env['DRAMA_PROJECT_ROOT'] = PROJECT_ROOT

        print(f"\n{'='*60}")
        print(f"Submitting {sid} ({seg['duration_sec']}s, {mode})...")
        print(f"{'='*60}")

        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            print(f"STDERR: {result.stderr}")
            print(f"STDOUT: {result.stdout}")
        else:
            try:
                resp = json.loads(result.stdout)
                tid = resp.get('task_id', resp.get('id', '?'))
                status = resp.get('status', '?')
                print(f"  ✅ {sid}: {tid} ({status})")
            except:
                print(f"  Output: {result.stdout[:200]}")

if __name__ == '__main__':
    main()
