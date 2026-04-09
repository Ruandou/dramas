#!/usr/bin/env python3
"""
imgbb图片上传工具
免费图床，支持HTTPS
"""

import os
import sys
import json
import argparse
import base64
import urllib.request
import urllib.error
import urllib.parse

# ============ 配置 ============
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "")

def upload_to_imgbb(file_path: str) -> dict:
    """上传图片到imgbb，返回公开URL"""
    if not IMGBB_API_KEY:
        return {"error": "请设置IMGBB_API_KEY环境变量"}

    if not os.path.exists(file_path):
        return {"error": f"文件不存在: {file_path}"}

    try:
        with open(file_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")

        url = "https://api.imgbb.com/1/upload"
        data = f"key={IMGBB_API_KEY}&image={urllib.parse.quote(img_data)}".encode()

        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())

        if result.get("success"):
            return {
                "status": "ok",
                "url": result["data"]["url"],
                "delete_url": result["data"]["delete_url"],
                "filename": result["data"]["image"]["filename"]
            }
        else:
            return {"error": "上传失败"}

    except Exception as e:
        return {"error": str(e)}

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

    if command == "upload":
        result = upload_to_imgbb(params.get("file_path", ""))
    else:
        result = {"error": f"未知命令: {command}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser(description="imgbb图片上传工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    upload_parser = subparsers.add_parser("upload", help="上传图片")
    upload_parser.add_argument("file_path", help="本地图片文件路径")

    mcp_parser = subparsers.add_parser("mcp", help="MCP模式")

    args = parser.parse_args()

    if args.command == "upload":
        result = upload_to_imgbb(args.file_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "mcp":
        mcp_main()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
