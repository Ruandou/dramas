#!/usr/bin/env python3
"""
字幕生成工具 - 使用faster-whisper将视频/音频转字幕
"""
import os
import sys
import json
import argparse
import subprocess
import re

# 添加本地依赖路径
DEPS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faster_whisper_deps")
if os.path.exists(DEPS_PATH):
    sys.path.insert(0, DEPS_PATH)

def extract_audio(video_path: str, audio_path: str = None) -> str:
    """用ffmpeg从视频提取音频"""
    if audio_path is None:
        audio_path = video_path.rsplit(".", 1)[0] + "_audio.wav"
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        audio_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return audio_path

def transcribe(audio_path: str, language: str = "zh") -> list:
    """用faster-whisper转写音频，返回时间戳+文字"""
    from faster_whisper import WhisperModel
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    segments, _ = model.transcribe(audio_path, language=language, word_timestamps=True)
    result = []
    for seg in segments:
        result.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip()
        })
    return result

def format_srt_timestamp(seconds: float) -> str:
    """秒转SRT时间戳 00:00:00,000"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def segments_to_srt(segments: list) -> str:
    """将分段转成SRT格式"""
    srt_lines = []
    for i, seg in enumerate(segments, 1):
        start = format_srt_timestamp(seg["start"])
        end = format_srt_timestamp(seg["end"])
        text = seg["text"]
        srt_lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(srt_lines)

def video_to_srt(video_path: str, output_srt: str = None, language: str = "zh") -> dict:
    """视频转SRT字幕"""
    video_path = os.path.expanduser(video_path)
    if not os.path.exists(video_path):
        return {"error": f"文件不存在: {video_path}"}

    if output_srt is None:
        output_srt = video_path.rsplit(".", 1)[0] + ".srt"

    # 提取音频
    audio_path = video_path.rsplit(".", 1)[0] + "_audio.wav"
    try:
        extract_audio(video_path, audio_path)
    except Exception as e:
        return {"error": f"提取音频失败: {e}"}

    try:
        # 转写
        segments = transcribe(audio_path, language)
        if not segments:
            return {"error": "未检测到语音"}

        # 生成SRT
        srt_content = segments_to_srt(segments)
        with open(output_srt, "w", encoding="utf-8") as f:
            f.write(srt_content)

        return {
            "status": "ok",
            "srt_file": output_srt,
            "segments": len(segments),
            "duration": segments[-1]["end"] if segments else 0
        }
    finally:
        # 清理临时音频
        if os.path.exists(audio_path):
            os.remove(audio_path)

def mcp_main():
    """MCP模式入口"""
    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"error": "stdin为空"}, ensure_ascii=False))
        sys.exit(1)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"error": "无效的JSON"}, ensure_ascii=False))
        sys.exit(1)

    command = payload.get("command")
    params = payload.get("params", {})

    if command == "video_to_srt":
        result = video_to_srt(
            params.get("video_path", ""),
            params.get("output_srt"),
            params.get("language", "zh")
        )
    else:
        result = {"error": f"未知命令: {command}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser(description="字幕生成工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    v2s_parser = subparsers.add_parser("video2srt", help="视频转SRT")
    v2s_parser.add_argument("video_path", help="视频文件路径")
    v2s_parser.add_argument("--output", "-o", help="输出SRT路径")
    v2s_parser.add_argument("--lang", "-l", default="zh", help="语言，默认中文")

    mcp_parser = subparsers.add_parser("mcp", help="MCP模式")

    args = parser.parse_args()

    if args.command == "video2srt":
        result = video_to_srt(args.video_path, args.output, args.lang)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "mcp":
        mcp_main()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
