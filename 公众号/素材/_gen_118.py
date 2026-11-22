"""Render the WeChat submission example from existing source material.

Run with an empty --output directory. Project files are read only.
"""

from __future__ import annotations

import argparse
import io
import json
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "dramas" / "机甲维修店老板娘"
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
PAPER = "#F2F2EC"
WHITE = "#FCFCF9"
INK = "#132C35"
MUTED = "#486269"
LINE = "#CAD7D3"
PALE = "#DDEAE3"
MINT = "#D9EDAD"
COVER = "封面_118_20261122_900x383.png"
FIGURE = "118_图1_送审制作证明对照_1080.png"
SAMPLE = "118_制作证明脱敏样例.mp4"
EXCERPTS = {"EP01": "倚着门框", "EP02": "逆光站在门口"}


@lru_cache
def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT, size, index=2 if bold else 0)


class Panel:
    def __init__(self, size, background):
        self.image = Image.new("RGB", size, background)
        self.draw = ImageDraw.Draw(self.image)

    def text(self, x, y, value, size, color=INK, bold=False, anchor="lt", box=None):
        face = font(size, bold)
        left, top, right, bottom = self.draw.textbbox(
            (x, y), value, font=face, anchor=anchor
        )
        bounds = box or (0, 0, *self.image.size)
        assert (
            bounds[0] <= left < right <= bounds[2]
            and bounds[1] <= top < bottom <= bounds[3]
        ), (value, (left, top, right, bottom), bounds)
        self.draw.text((x, y), value, font=face, fill=color, anchor=anchor)

    def photo(self, source, bounds, radius=14, contain=False):
        x, y, right, bottom = bounds
        size = (right - x, bottom - y)
        rgb = source.convert("RGB")
        if contain:
            thumbnail = ImageOps.contain(rgb, size, Image.Resampling.LANCZOS)
            picture = Image.new("RGB", size, PAPER)
            picture.paste(thumbnail, ((size[0] - thumbnail.width) // 2, 0))
        else:
            picture = ImageOps.fit(rgb, size, Image.Resampling.LANCZOS)
        mask = Image.new("L", size)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, *size), radius, fill=255)
        self.image.paste(picture, (x, y), mask)

    def save(self, path):
        with path.open("xb") as f:
            self.image.save(f, "PNG", optimize=True)
        with Image.open(path) as image:
            assert image.size == self.image.size
            image.verify()


def probe(path):
    command = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=width,height,codec_name", "-of", "json", str(path),
    ]
    return json.loads(subprocess.check_output(command))


def frame(path):
    command = [
        "ffmpeg", "-v", "error", "-ss", "1", "-i", str(path),
        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-",
    ]
    with Image.open(io.BytesIO(subprocess.check_output(command))) as image:
        return image.convert("RGB")


def episode_data(episode):
    config = PROJECT / "剧本" / episode / f"{episode}_segments.yaml"
    segments = yaml.safe_load(config.read_text())["segments"]
    first = segments[0]
    assert EXCERPTS[episode] in first["api"]["text"]
    folder = PROJECT / "assets" / "generated" / episode
    source = folder / f"{first['segment_id']}.mp4"
    source_duration = float(probe(source)["format"]["duration"])
    final = float(probe(folder / f"{episode}_成片.mp4")["format"]["duration"])
    assert source_duration >= 3
    return {
        "episode": episode,
        "segment": first["segment_id"],
        "shot_ids": first["shot_ids"],
        "segments": len(segments),
        "source": source,
        "excerpt": EXCERPTS[episode],
        "asset_ids": {key: list(first.get("assets", {}).get(key, {}))
                      for key in ("look_urls", "scene_urls", "prop_urls")},
        "final_duration": final,
        "frame": frame(source),
    }


def cover(path, episodes):
    p = Panel((900, 383), INK)
    p.photo(episodes[0]["frame"], (-24, 23, 242, 360), 20)
    p.photo(episodes[1]["frame"], (658, 23, 924, 360), 20)
    p.draw.rectangle((239, 0, 661, 383), fill=INK)
    p.draw.line((252, 35, 252, 350), fill="#39535A", width=2)
    p.draw.line((648, 35, 648, 350), fill="#39535A", width=2)
    safe = (270, 18, 630, 364)
    p.text(450, 60, "微信短剧", 24, MINT, True, "mt", safe)
    p.text(450, 123, "AI短剧送审", 54, WHITE, True, "mt", safe)
    p.text(450, 206, "制作证明怎么准备", 39, WHITE, True, "mt", safe)
    p.draw.rounded_rectangle((418, 283, 482, 289), radius=3, fill=MINT)
    p.text(450, 314, "一人短剧厂牌", 21, "#B5C7C9", False, "mt", safe)
    p.save(path)


def body_figure(path, episodes):
    p = Panel((1080, 1240), PAPER)
    p.text(66, 48, "本地归档演示", 31, MUTED, True)
    p.text(62, 99, "把提示词和片段对上", 64, INK, True)
    p.text(66, 194, "同一部剧的两集素材", 31, MUTED)
    for y, data in zip((270, 700), episodes):
        p.draw.rounded_rectangle((62, y, 1018, y + 390), 24, fill=WHITE, outline=LINE, width=2)
        p.draw.rounded_rectangle((94, y + 33, 236, y + 82), 13, fill=PALE)
        p.text(114, y + 44, data["episode"], 31, INK, True)
        p.text(96, y + 119, data["segment"], 43, INK, True)
        p.text(97, y + 188, "提示词节选", 28, MUTED, True)
        p.text(96, y + 239, "“" + data["excerpt"] + "”", 43, INK, True)
        p.text(97, y + 327, " → 同编号第1镜截帧", 30, MUTED)
        p.photo(data["frame"], (742, y + 24, 984, y + 365))
    p.draw.line((65, 1140, 1014, 1140), fill=LINE, width=2)
    p.text(65, 1170, "本地归档演示，未经平台提审；画面为生成视频截帧。", 26, MUTED)
    p.save(path)


def asset_slate(path, episodes):
    p = Panel((720, 1008), PAPER)
    p.text(38, 35, "本地归档演示", 38, INK, True)
    p.text(38, 94, "未经平台提审", 32, MUTED, True)
    p.text(38, 180, "同一项目，两集材料", 43, INK, True)
    p.text(38, 253, "剧集列表", 32, MUTED, True)
    for y, data in zip((320, 500), episodes):
        p.draw.rounded_rectangle((35, y, 685, y + 145), 20, fill=WHITE, outline=LINE)
        p.text(60, y + 23, data["episode"], 43, INK, True)
        p.text(60, y + 87,
               f'{data["segments"]} 段 · 成片 {data["final_duration"]:.2f} 秒', 33, MUTED)
    p.text(38, 713, "以下逐段展示引用资产、", 34, INK, True)
    p.text(38, 766, "第1镜提示词节选及片段。", 34, INK, True)
    p.text(38, 843, "不代替真实生成工具录屏", 29, MUTED)
    p.save(path)


def prompt_slate(path, data):
    p = Panel((720, 1008), PAPER)
    p.text(36, 31, "本地归档演示", 36, INK, True)
    p.text(36, 84, "未经平台提审", 29, MUTED, True)
    p.text(35, 143, data["segment"], 45, INK, True)
    p.text(36, 207, "第1镜 · " + data["shot_ids"][0], 31, MUTED)
    p.text(35, 263, "“" + data["excerpt"] + "”", 46, INK, True)
    p.draw.rounded_rectangle((32, 343, 355, 842), 17, fill=WHITE)
    p.text(48, 361, "该段引用资产", 29, MUTED, True)
    y = 416
    for label, key in (("角色", "look_urls"), ("场景", "scene_urls"), ("道具", "prop_urls")):
        p.text(48, y, label, 27, MUTED, True)
        y += 39
        for code in data["asset_ids"][key] or ["未独立引用"]:
            p.text(48, y, code, 28, INK, True)
            y += 41
        y += 13
    assert y < 830, y
    p.draw.rectangle((378, 309, 684, 843), fill=INK)
    p.text(35, 871, "原片1—3秒循环，仅展示第1镜", 30, MUTED)
    p.save(path)


def encode(output, slate, source=None):
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-n", "-loop", "1",
        "-framerate", "24", "-i", str(slate),
    ]
    if source:
        command += [
            "-ss", "1", "-t", "2", "-i", str(source), "-filter_complex",
            "[1:v]fps=24,scale=304:532,setsar=1,loop=loop=3:size=48:start=0[clip];"
            "[0:v][clip]overlay=379:310:shortest=1",
        ]
    command += [
        "-t", "8" if source else "7", "-an", "-c:v", "libx264", "-crf", "23",
        "-preset", "fast", "-pix_fmt", "yuv420p", str(output),
    ]
    subprocess.run(command, check=True)


def proof_video(output, episodes):
    with tempfile.TemporaryDirectory(prefix="submission-118-") as temp:
        work = Path(temp)
        first = work / "index.png"
        asset_slate(first, episodes)
        encode(work / "part0.mp4", first)
        for i, data in enumerate(episodes, 1):
            slate = work / f"prompt{i}.png"
            prompt_slate(slate, data)
            encode(work / f"part{i}.mp4", slate, data["source"])
        listing = work / "concat.txt"
        listing.write_text("".join(f"file part{i}.mp4\n" for i in range(3)))
        command = [
            "ffmpeg", "-v", "error", "-n", "-f", "concat", "-safe", "1",
            "-i", str(listing), "-c", "copy", "-movflags", "+faststart", str(output),
        ]
        subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    assert not any((output / x).exists() for x in (COVER, FIGURE, SAMPLE))
    episodes = [episode_data(ep) for ep in EXCERPTS]
    cover(output / COVER, episodes)
    body_figure(output / FIGURE, episodes)
    proof_video(output / SAMPLE, episodes)
    metadata = probe(output / SAMPLE)
    assert int(metadata["format"]["size"]) < 10_000_000
    assert abs(float(metadata["format"]["duration"]) - 23) < 0.1
    print(json.dumps(metadata, ensure_ascii=False))


if __name__ == "__main__":
    main()
