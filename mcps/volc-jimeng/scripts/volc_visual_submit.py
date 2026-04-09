#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调用火山引擎「视觉智能 / 即梦」类 OpenAPI（POST + JSON Body + 签名）。
文档入口：https://www.volcengine.com/docs/6444/69732?lang=zh
即梦视频接口说明见控制台文档，例如：
https://www.volcengine.com/docs/85621/1777001?lang=zh

环境变量（任选一种命名）：
  VOLC_ACCESS_KEY + VOLC_SECRET_KEY
  或 VOLC_ACCESSKEY + VOLC_SECRETKEY

stdin JSON 示例：
{
  "action": "CVSync2AsyncSubmitTask",
  "version": "2022-08-31",
  "body": { ... 与官方接口文档一致 ... }
}

注意：action / version / body 字段名必须以你控制台「即梦视频 3.0 Pro」接口文档为准，此处仅为占位。
"""
from __future__ import annotations

import json
import os
import sys
import warnings

# macOS 自带 LibreSSL 时 urllib3 会刷 OpenSSL 警告，避免 stderr 干扰 MCP 解析
warnings.filterwarnings("ignore", message=".*OpenSSL.*")

try:
    from volcengine.ApiInfo import ApiInfo
    from volcengine.visual.VisualService import VisualService
except ImportError as e:
    print(
        json.dumps(
            {
                "error": "未安装 volcengine（旧版 SDK）。请执行: pip3 install 'volcengine>=1.0.130,<2'",
                "detail": str(e),
            },
            ensure_ascii=False,
        )
    )
    sys.exit(1)


def _creds():
    ak = os.environ.get("VOLC_ACCESS_KEY") or os.environ.get("VOLC_ACCESSKEY")
    sk = os.environ.get("VOLC_SECRET_KEY") or os.environ.get("VOLC_SECRETKEY")
    return ak, sk


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        print(
            json.dumps({"error": "stdin 为空，请传入 JSON"}, ensure_ascii=False)
        )
        sys.exit(1)
    payload = json.loads(raw)
    action = payload.get("action") or os.environ.get("VOLC_VISUAL_ACTION")
    version = payload.get("version") or os.environ.get("VOLC_VISUAL_VERSION", "2022-08-31")
    body = payload.get("body")
    if not action:
        print(
            json.dumps(
                {
                    "error": "缺少 action（或环境变量 VOLC_VISUAL_ACTION）",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)
    if body is None:
        body = {}

    ak, sk = _creds()
    if not ak or not sk:
        print(
            json.dumps(
                {
                    "error": "缺少密钥：请设置 VOLC_ACCESS_KEY 与 VOLC_SECRET_KEY",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    svc = VisualService()
    svc.set_ak(ak)
    svc.set_sk(sk)

    # 动态注册 Action（旧版 SDK 未内置最新即梦接口名时）
    if action not in svc.api_info:
        svc.api_info[action] = ApiInfo(
            "POST",
            "/",
            {"Action": action, "Version": version},
            {},
            {},
        )

    try:
        res = svc.json(action, {}, json.dumps(body, ensure_ascii=False))
        print(res)
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
