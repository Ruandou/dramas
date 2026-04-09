#!/usr/bin/env python3
"""
MiniMax 海螺AI 工具 - MCP 模式
支持文生图、语音合成等功能

MCP模式：通过stdin接收JSON，输出JSON
CLI模式：命令行参数
"""

import json
import os
import sys
import time
import base64
import argparse
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# ============ API配置 ============
MINIMAX_API_HOST = os.environ.get("MINIMAX_API_HOST", "https://api.minimaxi.com")

# ============ 凭证管理 ============
def load_credentials():
    """从环境变量加载凭证"""
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    return api_key

def get_headers(api_key: str):
    """生成请求头"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

# ============ 文生图 ============
def text_to_image(prompt: str, model: str = "image-01", aspect_ratio: str = "9:16",
                  n: int = 1, prompt_optimizer: bool = False,
                  output_directory: str = None, mcp_mode: bool = False) -> dict:
    """文生图"""
    api_key = load_credentials()
    if not api_key:
        return {"error": "请设置 MINIMAX_API_KEY 环境变量"}

    url = f"{MINIMAX_API_HOST}/v1/image_generation"

    payload = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "n": n,
        "prompt_optimizer": prompt_optimizer
    }

    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url, data=data,
            headers=get_headers(api_key),
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())

        if result.get("base_resp", {}).get("status_code") == 0 or result.get("status_code") == 0:
            images = result.get("data", {}).get("image_urls", [])
            if not images:
                images = result.get("image_urls", [])

            if images:
                response = {
                    "status": "ok",
                    "images": images,
                    "model": model,
                    "aspect_ratio": aspect_ratio
                }

                # 如果指定了输出目录，下载图片
                if output_directory and images:
                    output_dir = Path(output_directory).expanduser()
                    output_dir.mkdir(parents=True, exist_ok=True)
                    saved_paths = []
                    for i, img_url in enumerate(images):
                        try:
                            filename = f"minimax_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.jpeg"
                            dest_path = output_dir / filename
                            download_file(img_url, str(dest_path))
                            saved_paths.append(str(dest_path))
                        except Exception as e:
                            saved_paths.append(f"下载失败: {str(e)}")
                    response["saved_paths"] = saved_paths

                if mcp_mode:
                    return response
                print(json.dumps(response, ensure_ascii=False, indent=2))
            else:
                msg = f"生成失败: {result}"
                if mcp_mode:
                    return {"error": msg}
                print(msg, file=sys.stderr)
        else:
            msg = f"API错误: {result}"
            if mcp_mode:
                return {"error": msg}
            print(msg, file=sys.stderr)
    except Exception as e:
        msg = f"请求失败: {str(e)}"
        if mcp_mode:
            return {"error": msg}
        print(msg, file=sys.stderr)

# ============ 语音合成 ============
def text_to_audio(text: str, model: str = "speech-02-hd", voice_id: str = "female-shaonv",
                  output_directory: str = None, mcp_mode: bool = False) -> dict:
    """语音合成"""
    api_key = load_credentials()
    if not api_key:
        return {"error": "请设置 MINIMAX_API_KEY 环境变量"}

    url = f"{MINIMAX_API_HOST}/v1/t2a_v2"

    payload = {
        "model": model,
        "text": text,
        "voice_id": voice_id,
        "stream": False
    }

    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url, data=data,
            headers=get_headers(api_key),
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())

        if result.get("base_resp", {}).get("status_code") == 0 or result.get("status_code") == 0:
            audio_url = result.get("data", {}).get("audio_url") or result.get("audio_url")

            response = {
                "status": "ok",
                "audio_url": audio_url,
                "model": model,
                "voice_id": voice_id
            }

            # 如果指定了输出目录，下载音频
            if output_directory and audio_url:
                output_dir = Path(output_directory).expanduser()
                output_dir.mkdir(parents=True, exist_ok=True)
                filename = f"minimax_tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                dest_path = output_dir / filename
                download_file(audio_url, str(dest_path))
                response["saved_path"] = str(dest_path)

            if mcp_mode:
                return response
            print(json.dumps(response, ensure_ascii=False, indent=2))
        else:
            msg = f"API错误: {result}"
            if mcp_mode:
                return {"error": msg}
            print(msg, file=sys.stderr)
    except Exception as e:
        msg = f"请求失败: {str(e)}"
        if mcp_mode:
            return {"error": msg}
        print(msg, file=sys.stderr)

# ============ 列出音色 ============
def list_voices(mcp_mode: bool = False) -> dict:
    """列出可用音色"""
    api_key = load_credentials()
    if not api_key:
        return {"error": "请设置 MINIMAX_API_KEY 环境变量"}

    url = f"{MINIMAX_API_HOST}/v1/voices"

    try:
        req = urllib.request.Request(
            url,
            headers=get_headers(api_key),
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())

        voices = result.get("data", {}).get("voices", []) or result.get("voices", [])
        response = {
            "status": "ok",
            "voices": voices
        }

        if mcp_mode:
            return response
        print(json.dumps(response, ensure_ascii=False, indent=2))
    except Exception as e:
        msg = f"请求失败: {str(e)}"
        if mcp_mode:
            return {"error": msg}
        print(msg, file=sys.stderr)

# ============ 下载文件 ============
def download_file(url: str, output_path: str) -> dict:
    """下载文件到本地"""
    output_path = os.path.expanduser(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        with open(output_path, "wb") as f:
            f.write(data)
        return {"status": "ok", "path": output_path, "size": len(data)}
    except Exception as e:
        return {"error": str(e)}

# ============ MCP 模式 ============
def mcp_handler():
    """处理 MCP JSON-RPC 请求"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            method = request.get("method", "")
            params = request.get("params", {})
            request_id = request.get("id")

            result = None
            error = None

            if method == "text_to_image":
                result = text_to_image(
                    prompt=params.get("prompt", ""),
                    model=params.get("model", "image-01"),
                    aspect_ratio=params.get("aspect_ratio", "9:16"),
                    n=params.get("n", 1),
                    prompt_optimizer=params.get("prompt_optimizer", False),
                    output_directory=params.get("output_directory"),
                    mcp_mode=True
                )
            elif method == "text_to_audio":
                result = text_to_audio(
                    text=params.get("text", ""),
                    model=params.get("model", "speech-02-hd"),
                    voice_id=params.get("voice_id", "female-shaonv"),
                    output_directory=params.get("output_directory"),
                    mcp_mode=True
                )
            elif method == "list_voices":
                result = list_voices(mcp_mode=True)
            else:
                error = {"code": -32601, "message": f"Unknown method: {method}"}

            response = {"jsonrpc": "2.0"}
            if request_id:
                response["id"] = request_id
            if error:
                response["error"] = error
            else:
                response["result"] = result

            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": str(e)}
            }
            print(json.dumps(error_response, ensure_ascii=False))
            sys.stdout.flush()

# ============ CLI 模式 ============
def main():
    parser = argparse.ArgumentParser(description="MiniMax 海螺AI 工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 文生图
    img_parser = subparsers.add_parser("image", help="文生图")
    img_parser.add_argument("--prompt", "-p", required=True, help="图片描述")
    img_parser.add_argument("--model", "-m", default="image-01", help="模型")
    img_parser.add_argument("--ratio", "-r", default="9:16", help="宽高比")
    img_parser.add_argument("--n", "-n", type=int, default=1, help="生成数量")
    img_parser.add_argument("--no-optimizer", action="store_true", help="关闭prompt优化")
    img_parser.add_argument("--output", "-o", help="输出目录")

    # 语音合成
    audio_parser = subparsers.add_parser("audio", help="语音合成")
    audio_parser.add_argument("--text", "-t", required=True, help="合成文本")
    audio_parser.add_argument("--model", "-m", default="speech-02-hd", help="模型")
    audio_parser.add_argument("--voice", "-v", default="female-shaonv", help="音色ID")
    audio_parser.add_argument("--output", "-o", help="输出目录")

    # 列出音色
    subparsers.add_parser("voices", help="列出可用音色")

    args = parser.parse_args()

    if args.command == "image":
        text_to_image(
            prompt=args.prompt,
            model=args.model,
            aspect_ratio=args.ratio,
            n=args.n,
            prompt_optimizer=not args.no_optimizer,
            output_directory=args.output
        )
    elif args.command == "audio":
        text_to_audio(
            text=args.text,
            model=args.model,
            voice_id=args.voice,
            output_directory=args.output
        )
    elif args.command == "voices":
        list_voices()
    elif args.command == "mcp":
        mcp_handler()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
