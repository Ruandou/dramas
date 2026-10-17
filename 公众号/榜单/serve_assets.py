#!/usr/bin/env python3
"""公众号后台「喂图」用的本地静态服务（带 CORS）。

**为什么需要**：后台编辑器（贴图/图文）上传图片走的是原生文件选择器，浏览器自动化
（ZCode in-app browser / IAB 明确不支持 file chooser）喂不进去。2026-09-29 起实测可行的
通道是「本地 HTTP 源 + 页内经 fetch 造 File + DataTransfer 喂 hidden input」，本脚本就是
那条通道的本地源，2026-10-17（榜003）起固化进仓库。

用法:
  python3 serve_assets.py [目录] [端口]        # 默认：公众号/素材、8791

页面内用法（浏览器 evaluate，参考 榜003_编辑信息.json「backend_verified」）:
  const r = await fetch('http://127.0.0.1:8791/' + encodeURIComponent('榜003_贴图1_热播榜_1080.png'));
  const dt = new DataTransfer();
  dt.items.add(new File([await r.blob()], name, { type: 'image/png' }));
  input.files = dt.files;
  input.dispatchEvent(new Event('change', { bubbles: true }));

注意：
- 只绑 127.0.0.1，仅供本机页面读取；上传完记得停掉（Ctrl-C 或 kill）。
- 上传前先看字节数：正文粘贴通道对 ≈345 KB 以上会 ERR_ABORTED，>200 KB 一律先出 `_q` 量化版。
- 喂图前确认目标是**图片区**那个 input：贴图页第 1 个 input 是正文的「本地上传」，
  喂错会把图插进正文（2026-09-29 事故）。
"""
from __future__ import annotations

import functools
import http.server
import socketserver
import sys
from pathlib import Path

DEFAULT_DIR = Path(__file__).resolve().parents[1] / '素材'
DEFAULT_PORT = 8791


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write('%s - %s\n' % (self.address_string(), fmt % args))


def main() -> None:
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    assert directory.is_dir(), f'目录不存在：{directory}'
    socketserver.TCPServer.allow_reuse_address = True
    handler = functools.partial(Handler, directory=str(directory))
    with socketserver.TCPServer(('127.0.0.1', port), handler) as httpd:
        print(f'serving {directory} at http://127.0.0.1:{port}/ (CORS *)', flush=True)
        httpd.serve_forever()


if __name__ == '__main__':
    main()
