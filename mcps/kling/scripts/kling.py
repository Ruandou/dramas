#!/usr/bin/env python3
"""
可灵AI视频生成工具 - Kling AI Video Generation CLI
支持图生视频、文生视频、音频生成

MCP模式：通过stdin接收JSON，输出JSON
CLI模式：命令行参数
"""

import json
import os
import sys
import time
import base64
import argparse
import hmac
import hashlib
import struct
import uuid
from datetime import datetime
from pathlib import Path

# ============ API配置 ============
KLING_API_BASE = "https://api-beijing.klingai.com"

# ============ imgbb配置 ============
IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "")

# ============ 图片上传 ============
def upload_to_imgbb(file_path: str) -> str:
    """上传本地文件到imgbb，返回公开URL"""
    import urllib.parse
    if not IMGBB_API_KEY:
        return None
    try:
        with open(file_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")
        url = "https://api.imgbb.com/1/upload"
        data = f"key={IMGBB_API_KEY}&image={urllib.parse.quote(img_data)}".encode()
        req = urllib.request.Request(url, data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
        if result.get("success"):
            return result["data"]["url"]
    except Exception:
        pass
    return None

def upload_image(file_path: str) -> str:
    """上传图片到imgbb图床"""
    file_path = os.path.expanduser(file_path)
    if not os.path.exists(file_path):
        return None
    if IMGBB_API_KEY:
        return upload_to_imgbb(file_path)
    return None

def imgbb_upload(file_path: str, mcp_mode: bool = False) -> dict:
    """上传本地文件到imgbb（独立工具）"""
    if not IMGBB_API_KEY:
        msg = "请设置IMGBB_API_KEY环境变量"
        if mcp_mode:
            return {"error": msg}
        print(msg, file=sys.stderr)
        sys.exit(1)

    file_path = os.path.expanduser(file_path)
    if not os.path.exists(file_path):
        msg = f"文件不存在: {file_path}"
        if mcp_mode:
            return {"error": msg}
        print(msg, file=sys.stderr)
        sys.exit(1)

    url = upload_to_imgbb(file_path)
    if url:
        response = {"status": "ok", "url": url, "file": file_path}
        if mcp_mode:
            return response
        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        msg = "上传失败"
        if mcp_mode:
            return {"error": msg}
        print(msg, file=sys.stderr)
        sys.exit(1)

# ============ 凭证管理 ============
def load_credentials():
    """从环境变量加载凭证"""
    ak = os.environ.get("KLING_AK", "")
    sk = os.environ.get("KLING_SK", "")
    return ak, sk

def save_credentials(ak: str, sk: str, path: str = "~/.kling_credentials"):
    """保存凭证到文件"""
    save_path = os.path.expanduser(path)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w") as f:
        json.dump({"ak": ak, "sk": sk}, f)
    return {"status": "ok", "message": f"凭证已保存到: {save_path}"}

def load_saved_credentials(path: str = "~/.kling_credentials"):
    """从文件加载凭证"""
    save_path = os.path.expanduser(path)
    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            creds = json.load(f)
            return creds.get("ak", ""), creds.get("sk", "")
    return "", ""

def generate_jwt_token(ak: str, sk: str, expires_in: int = 300) -> str:
    """生成JWT token用于API认证"""
    import time as time_module
    now = int(time_module.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": ak,
        "iat": now,
        "exp": now + expires_in,
        "nbf": now,
    }
    
    # Base64url encode header
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
    # Base64url encode payload
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
    
    # Create signature
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(sk.encode(), message.encode(), hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def download_video(url: str, output_path: str) -> dict:
    """下载视频，支持签名URL"""
    import urllib.request
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

def download_image(url: str, output_path: str, task_id: str = "", mcp_mode: bool = False) -> dict:
    """下载图片，支持签名URL"""
    # 绕过代理
    os.environ["no_proxy"] = "*"
    os.environ["NO_PROXY"] = "*"
    import urllib.request
    output_path = os.path.expanduser(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        with open(output_path, "wb") as f:
            f.write(data)
        result = {"status": "ok", "path": output_path, "size": len(data), "url": url}
        # 更新归档
        if task_id:
            update_task(task_id, {"image_url": url, "local_path": output_path})
        if mcp_mode:
            return result
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    except Exception as e:
        msg = str(e)
        if mcp_mode:
            return {"error": msg}
        print(f"错误: {msg}", file=sys.stderr)
        sys.exit(1)

# ============ 任务归档 ============
def get_archive_path():
    """获取归档文件路径"""
    project_root = os.environ.get("KLING_PROJECT_ROOT")
    if project_root:
        archive_dir = os.path.join(project_root, "video", "kling_tasks")
    else:
        # 向上两级找到仓库根 (mcps/kling/scripts -> 仓库根)
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        archive_dir = os.path.join(script_dir, "..", "..", "video", "kling_tasks")

    os.makedirs(archive_dir, exist_ok=True)
    return os.path.join(archive_dir, "tasks.json")

def load_archive():
    """加载任务归档"""
    path = get_archive_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tasks": []}

def save_archive(archive):
    """保存任务归档"""
    path = get_archive_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)

def add_task(task_type: str, task_id: str, params: dict, status: str = "pending"):
    """添加任务到归档"""
    archive = load_archive()
    task = {
        "task_id": task_id,
        "type": task_type,
        "params": params,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    archive["tasks"].insert(0, task)  # 最新在前面
    save_archive(archive)
    return task

def update_task(task_id: str, updates: dict):
    """更新任务状态"""
    archive = load_archive()
    for task in archive["tasks"]:
        if task["task_id"] == task_id:
            task.update(updates)
            task["updated_at"] = datetime.now().isoformat()
            break
    save_archive(archive)

def list_tasks(limit: int = 20):
    """列出最近的任务"""
    archive = load_archive()
    return archive["tasks"][:limit]

# ============ OmniImage 图片生成 ============
def omni_image(
    prompt: str = "",
    image_paths: str = "",  # 参考图片路径，逗号分隔
    resolution: str = "2k",  # 1k, 2k, 4k
    aspect_ratio: str = "9:16",  # 16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3, 21:9, auto
    n: int = 1,  # 生成数量 1-9
    model: str = "kling-v3-omni",
    mcp_mode: bool = False
):
    """OmniImage图片生成（支持参考图）"""
    ak, sk = load_credentials()
    if not ak or not sk:
        ak, sk = load_saved_credentials()
        if not ak or not sk:
            msg = "请设置KLING_AK和KLING_SK环境变量"
            if mcp_mode:
                return {"error": msg}
            print(msg, file=sys.stderr)
            sys.exit(1)

    body = {
        "model_name": model,
        "prompt": prompt,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "n": n,
    }

    # 处理参考图
    if image_paths:
        paths = [p.strip() for p in image_paths.split(",") if p.strip()]
        image_list = []
        for i, p in enumerate(paths, 1):
            p = os.path.expanduser(p)
            if os.path.exists(p):
                url = upload_image(p)
                if url:
                    image_list.append({"image": url})
                else:
                    with open(p, "rb") as f:
                        img_b64 = base64.b64encode(f.read()).decode("utf-8")
                    image_list.append({"image": img_b64})
            elif p.startswith("http://") or p.startswith("https://"):
                image_list.append({"image": p})
            else:
                msg = f"无效的图片路径或URL: {p}"
                if mcp_mode:
                    return {"error": msg}
                print(msg, file=sys.stderr)
                sys.exit(1)
        if image_list:
            body["image_list"] = image_list

    result = make_request("POST", "/v1/images/omni-image", body, ak, sk)

    if "error" in result:
        if mcp_mode:
            return result
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)

    task_id = result.get("task_id")
    if task_id:
        params = {
            "prompt": prompt,
            "image_paths": image_paths,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "n": n,
            "model": model,
        }
        add_task("omni_image", task_id, params)

        response = {
            "status": "submitted",
            "task_id": task_id,
            "message": f"图片生成任务已提交，使用模型 {model}",
        }
        if mcp_mode:
            return response
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return task_id

    if mcp_mode:
        return result
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return None


def query_image_task(task_id: str, mcp_mode: bool = False):
    """查询图片生成任务状态"""
    ak, sk = load_credentials()
    if not ak or not sk:
        ak, sk = load_saved_credentials()
        if not ak or not sk:
            msg = "请设置KLING_AK和KLING_SK环境变量"
            if mcp_mode:
                return {"error": msg}
            print(msg, file=sys.stderr)
            sys.exit(1)

    result = make_request("GET", f"/v1/images/omni-image/{task_id}", {}, ak, sk)

    if "error" in result:
        if mcp_mode:
            return result
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if "task_id" in result:
        status = result.get("status") or result.get("task_status", "unknown")
        status_msg = {
            "pending": "排队中...",
            "processing": "生成中...",
            "submitted": "已提交",
            "succeed": "完成!",
            "completed": "完成!",
            "failed": "失败",
        }.get(status, status)

        images = result.get("images", [])
        image_urls = [img.get("url") for img in images if img.get("url")]

        response = {
            "task_id": task_id,
            "status": status,
            "message": status_msg,
        }
        if image_urls:
            response["image_urls"] = image_urls

        update_task(task_id, {"status": status, "image_urls": image_urls})

        if mcp_mode:
            return response
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return response

    if mcp_mode:
        return result
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def wait_for_image_task(task_id: str, max_wait: int = 300, interval: int = 10, mcp_mode: bool = False):
    """轮询等待图片任务完成"""
    start = time.time()
    while time.time() - start < max_wait:
        result = query_image_task(task_id, mcp_mode=True)
        if result and "status" in result:
            status = result["status"]
            if status in ("succeed", "completed"):
                if mcp_mode:
                    return result
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return True
            elif status == "failed":
                if mcp_mode:
                    return result
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return False
        remaining = int(max_wait - (time.time() - start))
        if mcp_mode:
            return {"status": "waiting", "remaining_seconds": remaining}
        print(f"等待中... 剩余{remaining}秒", file=sys.stderr)
        time.sleep(interval)

    msg = "等待超时"
    if mcp_mode:
        return {"error": msg}
    print(msg, file=sys.stderr)
    return False


def omni_video(
    image_paths: str = "",  # 逗号分隔的图片路径或URL
    prompt: str = "",
    duration: int = 5,
    aspect_ratio: str = "9:16",
    model: str = "kling-v3-omni",
    mcp_mode: bool = False
):
    """Omni多图视频（支持多图主体控制）"""
    ak, sk = load_credentials()
    if not ak or not sk:
        ak, sk = load_saved_credentials()
        if not ak or not sk:
            msg = "请设置KLING_AK和KLING_SK环境变量"
            if mcp_mode:
                return {"error": msg}
            print(msg, file=sys.stderr)
            sys.exit(1)

    if not image_paths:
        msg = "请提供 image_paths 参数（逗号分隔的图片路径或URL）"
        if mcp_mode:
            return {"error": msg}
        print(msg, file=sys.stderr)
        sys.exit(1)

    # 解析图片列表
    paths = [p.strip() for p in image_paths.split(",") if p.strip()]
    if not paths:
        msg = "image_paths 格式错误"
        if mcp_mode:
            return {"error": msg}
        print(msg, file=sys.stderr)
        sys.exit(1)

    # 处理每张图片：本地文件上传图床(七牛或imgbb)，否则保持URL
    image_list = []
    for i, p in enumerate(paths, 1):
        p = os.path.expanduser(p)
        if os.path.exists(p):
            # 本地文件：上传到图床
            url = upload_image(p)
            if url:
                image_list.append({"image_url": url})
            else:
                # 图床失败，回退base64
                with open(p, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode("utf-8")
                image_list.append({"image_url": img_b64})
        elif p.startswith("http://") or p.startswith("https://"):
            # URL，保持原样
            image_list.append({"image_url": p})
        else:
            msg = f"无效的图片路径或URL: {p}"
            if mcp_mode:
                return {"error": msg}
            print(msg, file=sys.stderr)
            sys.exit(1)

    # 构建请求
    body = {
        "model_name": model,
        "prompt": prompt,
        "image_list": image_list,
        "duration": str(duration),
        "aspect_ratio": aspect_ratio,
        "sound": "on",  # 开启配音
    }

    result = make_request("POST", "/v1/videos/omni-video", body, ak, sk)

    if "error" in result:
        if mcp_mode:
            return result
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if "data" in result and "task_id" in result["data"]:
        task_id = result["data"]["task_id"]

        # 保存到归档
        params = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "model": model,
            "image_paths": image_paths,
        }
        add_task("omni_video", task_id, params)

        response = {
            "status": "submitted",
            "task_id": task_id,
            "message": f"任务已提交，已归档到本地"
        }
        if mcp_mode:
            return response
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return task_id

    if mcp_mode:
        return result
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return None

# ============ API请求 ============
def make_request(method: str, endpoint: str, body: dict, ak: str, sk: str) -> dict:
    """发送API请求"""
    import urllib.request
    import urllib.error

    # 绕过代理
    os.environ["no_proxy"] = "*"
    os.environ["NO_PROXY"] = "*"

    # 生成JWT token
    jwt_token = generate_jwt_token(ak, sk)
    url = f"{KLING_API_BASE}{endpoint}"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method=method
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP Error: {e.code}", "detail": e.read().decode("utf-8")}
    except Exception as e:
        return {"error": str(e)}

# ============ 核心功能 ============
def image_to_video(
    image_path: str = "",
    prompt: str = "",
    duration: int = 5,
    aspect_ratio: str = "9:16",
    audio_prompt: str = "",
    model: str = "kling-v3-omni",
    image_paths: str = "",  # 逗号分隔的多图路径
    mcp_mode: bool = False
):
    """图生视频（支持单图或多图主体）"""
    ak, sk = load_credentials()
    if not ak or not sk:
        ak, sk = load_saved_credentials()
        if not ak or not sk:
            msg = "请设置KLING_AK和KLING_SK环境变量"
            if mcp_mode:
                return {"error": msg}
            print(msg, file=sys.stderr)
            sys.exit(1)

    # 处理多图
    all_images = []
    if image_paths:
        # 多图模式：逗号分隔的路径
        paths = [p.strip() for p in image_paths.split(",") if p.strip()]
        for p in paths:
            p = os.path.expanduser(p)
            if not os.path.exists(p):
                msg = f"图片不存在: {p}"
                if mcp_mode:
                    return {"error": msg}
                print(msg, file=sys.stderr)
                sys.exit(1)
            with open(p, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")
            all_images.append({"image": img_data})
    elif image_path:
        # 单图模式
        image_path = os.path.expanduser(image_path)
        if not os.path.exists(image_path):
            msg = f"图片不存在: {image_path}"
            if mcp_mode:
                return {"error": msg}
            print(msg, file=sys.stderr)
            sys.exit(1)
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")
        all_images.append({"image": img_data})
    else:
        msg = "请提供 image_path 或 image_paths 参数"
        if mcp_mode:
            return {"error": msg}
        print(msg, file=sys.stderr)
        sys.exit(1)

    # 构建请求
    body = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
    }

    # 多图用 image_list，单图用 image
    if len(all_images) > 1:
        body["image_list"] = all_images
    else:
        body["image"] = all_images[0]["image"]

    if audio_prompt:
        body["audio_prompt"] = audio_prompt

    result = make_request("POST", "/v1/videos/image2video", body, ak, sk)

    if "error" in result:
        if mcp_mode:
            return result
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if "task_id" in result:
        task_id = result["task_id"]

        # 保存到归档
        params = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "model": model,
        }
        if len(all_images) > 1:
            params["image_paths"] = image_paths
        else:
            params["image_path"] = image_path
        if audio_prompt:
            params["audio_prompt"] = audio_prompt
        add_task("image_to_video", task_id, params)

        response = {
            "status": "submitted",
            "task_id": task_id,
            "message": f"任务已提交，已归档到本地"
        }
        if mcp_mode:
            return response
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return task_id

    if mcp_mode:
        return result
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return None

def text_to_video(
    prompt: str,
    duration: int = 5,
    aspect_ratio: str = "9:16",
    audio_prompt: str = "",
    model: str = "kling-v3-omni",
    mcp_mode: bool = False
):
    """文生视频"""
    ak, sk = load_credentials()
    if not ak or not sk:
        ak, sk = load_saved_credentials()
        if not ak or not sk:
            msg = "请设置KLING_AK和KLING_SK环境变量"
            if mcp_mode:
                return {"error": msg}
            print(msg, file=sys.stderr)
            sys.exit(1)

    body = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
    }

    if audio_prompt:
        body["audio_prompt"] = audio_prompt

    result = make_request("POST", "/v1/videos/text2video", body, ak, sk)

    if "error" in result:
        if mcp_mode:
            return result
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if "task_id" in result:
        task_id = result["task_id"]

        # 保存到归档
        params = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "model": model,
        }
        if audio_prompt:
            params["audio_prompt"] = audio_prompt
        add_task("text_to_video", task_id, params)

        response = {
            "status": "submitted",
            "task_id": task_id,
            "message": f"任务已提交，已归档到本地"
        }
        if mcp_mode:
            return response
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return task_id

    if mcp_mode:
        return result
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return None

def query_task(task_id: str, mcp_mode: bool = False):
    """查询任务状态"""
    ak, sk = load_credentials()
    if not ak or not sk:
        ak, sk = load_saved_credentials()
        if not ak or not sk:
            msg = "请设置KLING_AK和KLING_SK环境变量"
            if mcp_mode:
                return {"error": msg}
            print(msg, file=sys.stderr)
            sys.exit(1)

    # 尝试普通视频端点
    result = make_request("GET", f"/v1/videos/{task_id}", {}, ak, sk)

    # 如果是404，尝试omni端点
    if result.get("error") and "404" in str(result.get("error", "")):
        result = make_request("GET", f"/v1/videos/omni-video/{task_id}", {}, ak, sk)

    if "error" in result:
        if mcp_mode:
            return result
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(1)

    # 处理普通视频响应
    if "task_id" in result:
        # 尝试多种status字段名
        status = result.get("status") or result.get("task_status", "unknown")

        status_msg = {
            "pending": "排队中...",
            "processing": "生成中...",
            "submitted": "已提交",
            "succeed": "完成!",
            "completed": "完成!",
            "failed": "失败",
        }.get(status, status)

        # 更新归档
        updates = {"status": status}
        # 尝试多种video_url字段
        video_url = result.get("video_url") or result.get("task_result", {}).get("videos", [{}])[0].get("url")
        if status in ("succeed", "completed") and video_url:
            updates["video_url"] = video_url
        elif status == "failed":
            updates["error"] = result.get("error", "未知")
        update_task(task_id, updates)

        response = {
            "task_id": task_id,
            "status": status,
            "message": status_msg,
        }

        if video_url:
            response["video_url"] = video_url

        if mcp_mode:
            return response
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return response

    if mcp_mode:
        return result
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

def wait_for_task(task_id: str, max_wait: int = 300, interval: int = 10, mcp_mode: bool = False):
    """轮询等待任务完成"""
    start = time.time()
    while time.time() - start < max_wait:
        result = query_task(task_id, mcp_mode=True)
        if result and "status" in result:
            status = result["status"]
            if status == "completed":
                if mcp_mode:
                    return result
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return True
            elif status == "failed":
                if mcp_mode:
                    return result
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return False
        remaining = int(max_wait - (time.time() - start))
        if mcp_mode:
            return {"status": "waiting", "remaining_seconds": remaining}
        print(f"等待中... 剩余{remaining}秒", file=sys.stderr)
        time.sleep(interval)

    msg = "等待超时"
    if mcp_mode:
        return {"error": msg}
    print(msg, file=sys.stderr)
    return False

def list_archive_tasks(limit: int = 20, mcp_mode: bool = False):
    """列出归档的任务"""
    tasks = list_tasks(limit)
    if mcp_mode:
        return tasks
    print(json.dumps(tasks, ensure_ascii=False, indent=2))
    return tasks

def auth(ak: str, sk: str, mcp_mode: bool = False):
    """设置凭证"""
    result = save_credentials(ak, sk)
    if mcp_mode:
        return result
    print(json.dumps(result, ensure_ascii=False, indent=2))

# ============ MCP入口 ============
def mcp_main():
    """MCP模式：读取stdin JSON，输出JSON"""
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

    try:
        if command == "auth":
            result = auth(params.get("ak", ""), params.get("sk", ""), mcp_mode=True)
        elif command == "image2video":
            result = image_to_video(
                params.get("image_path", ""),
                params.get("prompt", ""),
                params.get("duration", 5),
                params.get("aspect_ratio", "9:16"),
                params.get("audio_prompt", ""),
                params.get("model", "kling-v3-omni"),
                mcp_mode=True
            )
        elif command == "text2video":
            result = text_to_video(
                params.get("prompt", ""),
                params.get("duration", 5),
                params.get("aspect_ratio", "9:16"),
                params.get("audio_prompt", ""),
                params.get("model", "kling-v3-omni"),
                mcp_mode=True
            )
        elif command == "query":
            result = query_task(params.get("task_id", ""), mcp_mode=True)
        elif command == "wait":
            result = wait_for_task(
                params.get("task_id", ""),
                params.get("max_wait", 300),
                mcp_mode=True
            )
        elif command == "list":
            result = list_archive_tasks(params.get("limit", 20), mcp_mode=True)
        elif command == "omni":
            result = omni_video(
                params.get("image_paths", ""),
                params.get("prompt", ""),
                params.get("duration", 5),
                params.get("aspect_ratio", "9:16"),
                params.get("model", "kling-v3-omni"),
                mcp_mode=True
            )
        elif command == "imgbb":
            result = imgbb_upload(params.get("file_path", ""), mcp_mode=True)
        else:
            result = {"error": f"未知命令: {command}"}

        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

# ============ CLI入口 ============
def main():
    parser = argparse.ArgumentParser(description="可灵AI视频生成工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # auth命令
    auth_parser = subparsers.add_parser("auth", help="设置API凭证")
    auth_parser.add_argument("ak", help="Access Key")
    auth_parser.add_argument("sk", help="Secret Key")

    # image2video命令
    i2v_parser = subparsers.add_parser("image2video", help="图生视频")
    i2v_parser.add_argument("--image", "-i", help="单张图片路径")
    i2v_parser.add_argument("--image-paths", help="多张图片路径，逗号分隔（最多4张）")
    i2v_parser.add_argument("--prompt", "-p", required=True, help="视频描述")
    i2v_parser.add_argument("--duration", "-d", type=int, default=5, help="时长(秒)")
    i2v_parser.add_argument("--ratio", "-r", default="9:16", help="宽高比")
    i2v_parser.add_argument("--audio", "-a", default="", help="音频描述")
    i2v_parser.add_argument("--model", "-m", default="kling-v3-omni", help="模型")

    # text2video命令
    t2v_parser = subparsers.add_parser("text2video", help="文生视频")
    t2v_parser.add_argument("--prompt", "-p", required=True, help="视频描述")
    t2v_parser.add_argument("--duration", "-d", type=int, default=5, help="时长(秒)")
    t2v_parser.add_argument("--ratio", "-r", default="9:16", help="宽高比")
    t2v_parser.add_argument("--audio", "-a", default="", help="音频描述")
    t2v_parser.add_argument("--model", "-m", default="kling-v3-omni", help="模型")

    # query命令
    query_parser = subparsers.add_parser("query", help="查询任务")
    query_parser.add_argument("--task-id", "-t", required=True, help="任务ID")

    # wait命令
    wait_parser = subparsers.add_parser("wait", help="等待任务完成")
    wait_parser.add_argument("--task-id", "-t", required=True, help="任务ID")
    wait_parser.add_argument("--max", "-m", type=int, default=300, help="最大等待秒数")

    # list命令
    list_parser = subparsers.add_parser("list", help="列出归档任务")
    list_parser.add_argument("--limit", "-n", type=int, default=20, help="显示条数")

    # omni命令（多图）
    omni_parser = subparsers.add_parser("omni", help="Omni多图视频")
    omni_parser.add_argument("--paths", required=True, help="图片路径或URL，逗号分隔")
    omni_parser.add_argument("--prompt", required=True, help="视频描述")
    omni_parser.add_argument("--duration", "-d", type=int, default=5, help="时长(秒)")
    omni_parser.add_argument("--ratio", "-r", default="9:16", help="宽高比")
    omni_parser.add_argument("--model", "-m", default="kling-v3-omni", help="模型")

    # omni_image命令（图片生成）
    omi_parser = subparsers.add_parser("omni_image", help="OmniImage图片生成")
    omi_parser.add_argument("--prompt", "-p", required=True, help="图片描述")
    omi_parser.add_argument("--paths", help="参考图片路径，逗号分隔")
    omi_parser.add_argument("--resolution", "-r", default="2k", choices=["1k", "2k", "4k"], help="分辨率")
    omi_parser.add_argument("--ratio", "-t", default="9:16", help="宽高比")
    omi_parser.add_argument("--n", "-n", type=int, default=1, help="生成数量")
    omi_parser.add_argument("--model", "-m", default="kling-v3-omni", help="模型")

    # query_image命令
    qi_parser = subparsers.add_parser("query_image", help="查询图片任务")
    qi_parser.add_argument("--task-id", "-t", required=True, help="任务ID")

    # wait_image命令
    wi_parser = subparsers.add_parser("wait_image", help="等待图片任务完成")
    wi_parser.add_argument("--task-id", "-t", required=True, help="任务ID")
    wi_parser.add_argument("--max", "-m", type=int, default=300, help="最大等待秒数")

    # imgbb命令
    imgbb_parser = subparsers.add_parser("imgbb", help="上传图片到imgbb")
    imgbb_parser.add_argument("file_path", help="本地文件路径")

    # download命令
    dl_parser = subparsers.add_parser("download", help="下载视频")
    dl_parser.add_argument("--url", required=True, help="视频URL")
    dl_parser.add_argument("--output", "-o", required=True, help="输出路径")

    # download_image命令
    di_parser = subparsers.add_parser("download_image", help="下载图片")
    di_parser.add_argument("--url", required=True, help="图片URL")
    di_parser.add_argument("--output", "-o", required=True, help="输出路径")
    di_parser.add_argument("--task-id", "-t", default="", help="任务ID（用于归档）")

    # mcp命令
    mcp_parser = subparsers.add_parser("mcp", help="MCP模式")

    args = parser.parse_args()

    if args.command == "auth":
        auth(args.ak, args.sk)
    elif args.command == "image2video":
        image_to_video(
            args.image, args.prompt, args.duration,
            args.ratio, args.audio, args.model,
            args.image_paths
        )
    elif args.command == "text2video":
        text_to_video(
            args.prompt, args.duration,
            args.ratio, args.audio, args.model
        )
    elif args.command == "query":
        query_task(args.task_id)
    elif args.command == "wait":
        wait_for_task(args.task_id, args.max)
    elif args.command == "list":
        list_archive_tasks(args.limit)
    elif args.command == "omni":
        omni_video(args.paths, args.prompt, args.duration, args.ratio, args.model)
    elif args.command == "omni_image":
        omni_image(args.prompt, args.paths, args.resolution, args.ratio, args.n, args.model)
    elif args.command == "query_image":
        query_image_task(args.task_id)
    elif args.command == "wait_image":
        wait_for_image_task(args.task_id, args.max)
    elif args.command == "imgbb":
        imgbb_upload(args.file_path)
    elif args.command == "download":
        result = download_video(args.url, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "download_image":
        download_image(args.url, args.output, args.task_id)
    elif args.command == "mcp":
        mcp_main()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
