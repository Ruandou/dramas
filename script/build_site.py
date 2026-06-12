#!/usr/bin/env python3
"""
静态站点生成器 — 将项目剧本/资产/视频生成为可部署的手机友好 HTML 站点。

用法：
    python3 script/build_site.py              # 生成到 site/
    python3 script/build_site.py --output dist # 生成到 dist/

部署：
    - GitHub Pages: cd site && git init && git add -A && git commit -m "deploy" && git push
    - Netlify: 拖拽 site/ 文件夹到 netlify.com/drop
    - Vercel: cd site && npx vercel
"""

import argparse
import json
import os
import re
import shutil
from pathlib import Path

import markdown

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DRAMAS_DIR = ROOT / "dramas"
DOCS_DIR = ROOT / "docs"
VIDEO_DIR = ROOT / "video"
VIDEOS_DIR = ROOT / "videos_2026-06-09"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".avi"}
MD_EXTS = {".md"}

# ---------------------------------------------------------------------------
# HTML 模板
# ---------------------------------------------------------------------------

TAILWIND_CDN = "https://cdn.tailwindcss.com"

BASE_HEAD = """\
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
<meta name="theme-color" content="#0f172a">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
<script src="{tailwind}"></script>
<script>tailwind.config={{theme:{{fontFamily:{{sans:['Noto Sans SC','system-ui','sans-serif']}}}}}})</script>
<style>
  .prose h1 {{ font-size:1.5rem; font-weight:700; margin:1.5rem 0 0.75rem; }}
  .prose h2 {{ font-size:1.25rem; font-weight:700; margin:1.25rem 0 0.5rem; border-bottom:1px solid #334155; padding-bottom:0.25rem; }}
  .prose h3 {{ font-size:1.1rem; font-weight:600; margin:1rem 0 0.5rem; }}
  .prose p  {{ margin:0.5rem 0; line-height:1.8; }}
  .prose ul, .prose ol {{ margin:0.5rem 0; padding-left:1.5rem; }}
  .prose li {{ margin:0.25rem 0; line-height:1.7; }}
  .prose blockquote {{ border-left:3px solid #6366f1; padding-left:0.75rem; margin:0.75rem 0; color:#94a3b8; }}
  .prose pre {{ background:#1e293b; padding:0.75rem; border-radius:0.5rem; overflow-x:auto; font-size:0.85rem; }}
  .prose code {{ background:#1e293b; padding:0.1rem 0.3rem; border-radius:0.25rem; font-size:0.85rem; }}
  .prose pre code {{ background:transparent; padding:0; }}
  /* 表格：手机端横滚，不挤压文字 */
  .table-wrap {{ overflow-x:auto; -webkit-overflow-scrolling:touch; margin:0.75rem 0; border:1px solid #334155; border-radius:0.5rem; }}
  .prose table {{ width:100%; border-collapse:collapse; font-size:0.85rem; min-width:500px; }}
  .prose th, .prose td {{ border-bottom:1px solid #334155; padding:0.6rem 0.75rem; text-align:left; white-space:nowrap; }}
  .prose th {{ background:#1e293b; font-weight:600; position:sticky; top:0; }}
  .prose tr:last-child td {{ border-bottom:none; }}
  .prose tr:hover {{ background:rgba(99,102,241,0.08); }}
  .prose hr {{ border:none; border-top:1px solid #334155; margin:1.5rem 0; }}
  .prose strong {{ color:#e2e8f0; }}
  .prose a {{ color:#818cf8; text-decoration:underline; }}
  .card {{ transition:transform 0.15s, box-shadow 0.15s; }}
  .card:hover {{ transform:translateY(-2px); box-shadow:0 8px 25px rgba(0,0,0,0.3); }}
  .gallery-img {{ aspect-ratio:1; object-fit:cover; cursor:pointer; }}
  .gallery-img:hover {{ opacity:0.85; }}
  .shot-cards code {{ font-size:0.7rem; background:#1e293b; padding:0.1rem 0.4rem; border-radius:0.25rem; }}
  .modal {{ display:none; position:fixed; inset:0; z-index:50; background:rgba(0,0,0,0.85); align-items:center; justify-content:center; }}
  .modal.active {{ display:flex; }}
  .modal img {{ max-width:95vw; max-height:90vh; border-radius:0.5rem; }}
  .tab-btn {{ padding:0.5rem 1rem; border-bottom:2px solid transparent; color:#94a3b8; transition:all 0.15s; }}
  .tab-btn.active {{ color:#818cf8; border-color:#818cf8; }}
  .search-box {{ background:#1e293b; border:1px solid #334155; border-radius:0.5rem; padding:0.5rem 1rem; width:100%; color:#e2e8f0; outline:none; }}
  .search-box:focus {{ border-color:#6366f1; }}
  .badge {{ display:inline-block; padding:0.15rem 0.5rem; border-radius:9999px; font-size:0.7rem; font-weight:500; }}
  .back-link {{ display:inline-flex; align-items:center; gap:0.35rem; color:#818cf8; padding:0.5rem 0; }}
  .back-link:hover {{ color:#a5b4fc; }}
</style>
""".format(tailwind=TAILWIND_CDN)


def page(title, body, breadcrumbs=None):
    """包装完整 HTML 页面"""
    bc_html = ""
    if breadcrumbs:
        parts = []
        for href, label in breadcrumbs[:-1]:
            parts.append(f'<a href="{href}" class="text-indigo-400 hover:text-indigo-300">{label}</a>')
            parts.append('<span class="text-slate-500 mx-1">/</span>')
        parts.append(f'<span class="text-slate-300">{breadcrumbs[-1][1]}</span>')
        bc_html = f'<nav class="text-sm mb-4 flex flex-wrap items-center">{" ".join(parts)}</nav>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<title>{title} · AI 短剧制作</title>
{BASE_HEAD}
</head>
<body class="bg-slate-900 text-slate-200 font-sans min-h-screen">
<div class="max-w-4xl mx-auto px-4 py-4 pb-20">
{bc_html}
{body}
</div>
</body>
</html>"""


def write_page(out_dir, rel_path, content):
    """写入页面文件，自动创建目录"""
    p = out_dir / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Markdown 渲染
# ---------------------------------------------------------------------------

_md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])


def _convert_wide_tables_in_md(text):
    """在 markdown 层面把宽分镜表格（>=9列）转为卡片列表，避免 HTML 解析问题"""
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        # 检测表格开始：当前行和下一行都是 | 开头
        if (i + 1 < len(lines)
                and lines[i].strip().startswith('|')
                and lines[i + 1].strip().startswith('|')
                and '---' in lines[i + 1]):
            # 解析表头
            header_line = lines[i]
            headers = [c.strip() for c in header_line.strip('|').split('|')]

            # 判断是否为宽分镜表（>=9 列或含 shot_id）
            if len(headers) >= 9 and 'shot_id' in headers:
                col_map = {h: idx for idx, h in enumerate(headers)}
                # 跳过分隔行
                i += 2
                cards = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    cells = [c.strip() for c in lines[i].strip('|').split('|')]
                    # 补齐列数
                    while len(cells) < len(headers):
                        cells.append('')

                    def cell(name):
                        raw = cells[col_map[name]] if name in col_map and col_map[name] < len(cells) else ''
                        return raw.strip('`').strip()

                    shot_num = cell('镜号')
                    shot_id = cell('shot_id')
                    scene = cell('场景')
                    shot_type = cell('景别')
                    duration = cell('时长')
                    mode = cell('模式')
                    camera = cell('运镜')
                    visual = cell('画面')
                    dialogue = cell('对白/备注') if '对白/备注' in col_map else ''

                    badge_class = "bg-indigo-900/60 text-indigo-300"
                    if mode == 'skip':
                        badge_class = "bg-slate-700 text-slate-400"
                    elif 'i2v_ref' in mode:
                        badge_class = "bg-emerald-900/60 text-emerald-300"

                    dur_badge = f'<span class="badge bg-slate-700 text-slate-300">{duration}s</span>' if duration and duration != '-' else ''

                    dialogue_html = ''
                    if dialogue:
                        dialogue_html = f'<div class="mt-2 text-sm text-slate-300 leading-relaxed border-l-2 border-slate-600 pl-2">{dialogue}</div>'

                    cards.append(f"""<div class="bg-slate-800/50 rounded-lg border border-slate-700 p-3">
<div class="flex items-center justify-between mb-1.5">
<div class="flex items-center gap-2">
<span class="text-lg font-bold text-slate-200">#{shot_num}</span>
<code class="text-xs text-slate-400">{shot_id}</code>
</div>
<div class="flex gap-1.5">{dur_badge}<span class="badge {badge_class}">{mode}</span></div>
</div>
<div class="flex flex-wrap gap-x-3 gap-y-0.5 text-xs text-slate-400 mb-1.5">
<span>📍 {scene}</span><span>🎭 {shot_type}</span><span>📷 {camera}</span>
</div>
{f'<div class="text-sm text-slate-200 mb-1">{visual}</div>' if visual else ''}
{dialogue_html}
</div>""")

                    i += 1

                result.append(f'<div class="shot-cards grid grid-cols-1 gap-2 my-4">{"".join(cards)}</div>')
                continue
            else:
                # 普通表格，原样保留（后续 render_md 会加 table-wrap）
                result.append(lines[i])
                i += 1
                continue

        result.append(lines[i])
        i += 1

    return '\n'.join(result)


def render_md(text):
    # 先在 markdown 层转换宽表格为卡片
    text = _convert_wide_tables_in_md(text)
    _md.reset()
    html = _md.convert(text)
    # 剩余普通表格包裹在可横滚容器中
    html = re.sub(r'<table>', '<div class="table-wrap"><table>', html)
    html = re.sub(r'</table>', '</table></div>', html)
    return html


# ---------------------------------------------------------------------------
# 扫描函数
# ---------------------------------------------------------------------------

def scan_dramas():
    """扫描所有剧目，返回列表"""
    dramas = []
    if not DRAMAS_DIR.is_dir():
        return dramas
    for d in sorted(DRAMAS_DIR.iterdir()):
        if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("_"):
            dramas.append(d)
    return dramas


def find_md_files(d):
    """递归查找目录下所有 .md 文件"""
    result = []
    if not d.is_dir():
        return result
    for p in sorted(d.rglob("*.md")):
        if "/." in str(p) or "/_" in str(p):
            continue
        result.append(p)
    return result


def find_images(d):
    """递归查找目录下所有图片"""
    result = []
    if not d.is_dir():
        return result
    for p in sorted(d.rglob("*")):
        if p.suffix.lower() in IMAGE_EXTS and not any(x in str(p) for x in ["/.", "/_", "node_modules"]):
            result.append(p)
    return result


def find_videos(d):
    """递归查找目录下所有视频"""
    result = []
    if not d.is_dir():
        return result
    for p in sorted(d.rglob("*")):
        if p.suffix.lower() in VIDEO_EXTS:
            result.append(p)
    return result


def scan_docs():
    """扫描 docs/ 目录"""
    result = []
    if not DOCS_DIR.is_dir():
        return result
    for p in sorted(DOCS_DIR.rglob("*.md")):
        result.append(p)
    return result


def scan_videos_global():
    """扫描 video/ 和 videos_*/ 目录"""
    results = []
    for base in [VIDEO_DIR, VIDEOS_DIR]:
        if base.is_dir():
            for p in sorted(base.rglob("*")):
                if p.suffix.lower() in VIDEO_EXTS:
                    results.append(p)
    return results


# ---------------------------------------------------------------------------
# 生成页面
# ---------------------------------------------------------------------------

def build_home(out_dir, dramas, docs, global_videos):
    """首页 — 剧目列表 + 搜索"""
    cards = []
    for d in dramas:
        # 找大纲文件
        outline = None
        for f in d.glob("短剧剧本_*.md"):
            outline = f.name
            break
        # 统计
        md_count = len(find_md_files(d))
        img_count = len(find_images(d))
        vid_count = len(find_videos(d))

        rel = d.name
        badges = []
        if md_count:
            badges.append(f'<span class="badge bg-indigo-900 text-indigo-300">{md_count} 文档</span>')
        if img_count:
            badges.append(f'<span class="badge bg-emerald-900 text-emerald-300">{img_count} 图片</span>')
        if vid_count:
            badges.append(f'<span class="badge bg-amber-900 text-amber-300">{vid_count} 视频</span>')

        cards.append(f"""
<a href="dramas/{rel}/" class="card block bg-slate-800 rounded-xl p-4 border border-slate-700">
  <h3 class="text-lg font-bold text-slate-100 mb-1">{d.name}</h3>
  {"<p class='text-sm text-slate-400 mb-2 line-clamp-2'>" + outline + "</p>" if outline else ""}
  <div class="flex flex-wrap gap-1.5">{" ".join(badges)}</div>
</a>""")

    body = f"""
<h1 class="text-2xl font-bold text-slate-100 mb-1">AI 短剧制作</h1>
<p class="text-slate-400 mb-4">共 {len(dramas)} 部剧目</p>

<input type="text" id="search" class="search-box mb-4" placeholder="搜索剧目..." oninput="filterCards(this.value)">

<div id="drama-grid" class="grid grid-cols-1 sm:grid-cols-2 gap-3">
{"".join(cards)}
</div>

<div class="mt-6 border-t border-slate-700 pt-4">
  <div class="flex gap-3 flex-wrap">
    <a href="docs/" class="card block bg-slate-800 rounded-lg px-4 py-3 border border-slate-700 flex-1 min-w-[120px] text-center">
      <div class="text-2xl mb-1">📚</div>
      <div class="text-sm font-medium text-slate-200">资料库</div>
      <div class="text-xs text-slate-400">{len(docs)} 篇</div>
    </a>
    <a href="videos/" class="card block bg-slate-800 rounded-lg px-4 py-3 border border-slate-700 flex-1 min-w-[120px] text-center">
      <div class="text-2xl mb-1">🎬</div>
      <div class="text-sm font-medium text-slate-200">视频素材</div>
      <div class="text-xs text-slate-400">{len(global_videos)} 个</div>
    </a>
  </div>
</div>

<script>
function filterCards(q) {{
  q = q.toLowerCase();
  document.querySelectorAll('#drama-grid > a').forEach(c => {{
    c.style.display = c.textContent.toLowerCase().includes(q) ? '' : 'none';
  }});
}}
</script>
"""
    write_page(out_dir, "index.html", page("首页", body))


def build_drama_page(out_dir, drama_dir):
    """剧目详情页 — tabs: 大纲/剧本/资产/图片/视频"""
    name = drama_dir.name
    md_files = find_md_files(drama_dir)
    images = find_images(drama_dir)
    videos = find_videos(drama_dir)

    # 分类 markdown
    outline_files = [f for f in md_files if "剧本" in f.name and "36集" in f.name]
    script_files = [f for f in md_files if "EP" in f.name.upper() and f.name not in [x.name for x in outline_files]]
    asset_files = [f for f in md_files if any(k in f.name for k in ["卡片", "索引", "规范", "计划", "角色", "形象", "场景", "道具", "声音", "年代"])]
    other_md = [f for f in md_files if f not in outline_files and f not in script_files and f not in asset_files]

    # 分类图片
    char_imgs = [i for i in images if any(k in str(i).lower() for k in ["char", "character", "look"])]
    prop_imgs = [i for i in images if "prop" in str(i).lower()]
    scene_imgs = [i for i in images if any(k in str(i).lower() for k in ["scene", "场景"])]
    other_imgs = [i for i in images if i not in char_imgs and i not in prop_imgs and i not in scene_imgs]

    rel = name

    def md_list(files, category):
        if not files:
            return '<p class="text-slate-500 text-sm">暂无内容</p>'
        items = []
        for f in files:
            link = f"docs/{category}/{f.relative_to(drama_dir).with_suffix('')}.html"
            icon = "📝"
            if "剧本" in f.name or "EP" in f.name.upper():
                icon = "🎬"
            elif "卡片" in f.name:
                icon = "🎭"
            elif "规范" in f.name or "计划" in f.name:
                icon = "📋"
            items.append(f'<a href="{link}" class="card block bg-slate-800 rounded-lg px-3 py-2.5 border border-slate-700"><span class="mr-1.5">{icon}</span>{f.stem}</a>')
        return f'<div class="grid grid-cols-1 gap-2">{"".join(items)}</div>'

    def img_gallery(imgs, label):
        if not imgs:
            return ""
        items = []
        for img in imgs:
            img_link = f"images/{img.relative_to(drama_dir)}"
            items.append(f'<img src="{img_link}" alt="{img.name}" class="gallery-img rounded-lg border border-slate-700" loading="lazy" onclick="showModal(this.src)">')
        return f'<h3 class="text-sm font-medium text-slate-400 mb-2 mt-4">{label} ({len(imgs)})</h3><div class="grid grid-cols-3 sm:grid-cols-4 gap-2">{"".join(items)}</div>'

    # Tab 内容
    tab_outline = md_list(outline_files, "outline")
    tab_scripts = md_list(script_files, "scripts")
    tab_assets = md_list(asset_files, "assets")
    tab_other = md_list(other_md, "other")

    all_imgs = char_imgs + prop_imgs + scene_imgs + other_imgs
    tab_images = ""
    if all_imgs:
        tab_images += img_gallery(char_imgs, "角色形象")
        tab_images += img_gallery(prop_imgs, "道具")
        tab_images += img_gallery(scene_imgs, "场景")
        tab_images += img_gallery(other_imgs, "其他图片")
    else:
        tab_images = '<p class="text-slate-500 text-sm">暂无图片</p>'

    tab_videos = ""
    if videos:
        items = []
        for v in videos:
            v_link = f"video_files/{v.relative_to(drama_dir)}"
            items.append(f"""
<div class="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
  <video controls preload="none" class="w-full" style="max-height:300px">
    <source src="{v_link}" type="video/mp4">
  </video>
  <div class="px-3 py-2 text-sm text-slate-300">{v.name}</div>
</div>""")
        tab_videos = f'<div class="grid grid-cols-1 gap-3">{"".join(items)}</div>'
    else:
        tab_videos = '<p class="text-slate-500 text-sm">暂无视频</p>'

    body = f"""
<h1 class="text-2xl font-bold text-slate-100 mb-4">{name}</h1>

<div class="flex gap-1 overflow-x-auto mb-4 border-b border-slate-700 -mx-1 px-1">
  <button class="tab-btn active whitespace-nowrap" onclick="switchTab('outline',this)">📋 大纲</button>
  <button class="tab-btn whitespace-nowrap" onclick="switchTab('scripts',this)">🎬 剧本</button>
  <button class="tab-btn whitespace-nowrap" onclick="switchTab('assets',this)">🎭 资产</button>
  <button class="tab-btn whitespace-nowrap" onclick="switchTab('images',this)">🖼️ 图片 ({len(all_imgs)})</button>
  <button class="tab-btn whitespace-nowrap" onclick="switchTab('videos',this)">🎥 视频 ({len(videos)})</button>
  <button class="tab-btn whitespace-nowrap" onclick="switchTab('other',this)">📄 其他</button>
</div>

<div id="tab-outline" class="tab-content">{tab_outline}</div>
<div id="tab-scripts" class="tab-content hidden">{tab_scripts}</div>
<div id="tab-assets" class="tab-content hidden">{tab_assets}</div>
<div id="tab-images" class="tab-content hidden">{tab_images}</div>
<div id="tab-videos" class="tab-content hidden">{tab_videos}</div>
<div id="tab-other" class="tab-content hidden">{tab_other}</div>

<div class="modal" id="imgModal" onclick="this.classList.remove('active')">
  <img id="modalImg" src="" alt="">
</div>

<script>
function switchTab(name, btn) {{
  document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-'+name).classList.remove('hidden');
  btn.classList.add('active');
}}
function showModal(src) {{
  document.getElementById('modalImg').src = src;
  document.getElementById('imgModal').classList.add('active');
}}
</script>
"""
    breadcrumbs = [("../../../", "首页")]
    write_page(out_dir, f"dramas/{rel}/index.html", page(name, body, breadcrumbs))


def build_md_page(out_dir, md_path, drama_dir, category):
    """单个 markdown 文档页面"""
    rel_to_drama = md_path.relative_to(drama_dir)
    out_rel = f"dramas/{drama_dir.name}/docs/{category}/{rel_to_drama.with_suffix('.html')}"
    text = md_path.read_text(encoding="utf-8", errors="replace")
    html = render_md(text)

    body = f"""
<a href="../../" class="back-link">← 返回 {drama_dir.name}</a>
<div class="prose text-slate-300 mt-2">
{html}
</div>
"""
    breadcrumbs = [
        ("../../../", "首页"),
        ("../../", drama_dir.name),
        ("#", md_path.stem),
    ]
    write_page(out_dir, out_rel, page(md_path.stem, body, breadcrumbs))


def build_docs_page(out_dir, docs_files):
    """资料库页面"""
    items = []
    for f in docs_files:
        link = f"pages/{f.stem}.html"
        items.append(f'<a href="{link}" class="card block bg-slate-800 rounded-lg px-3 py-2.5 border border-slate-700">📚 {f.stem}</a>')

    body = f"""
<a href="../" class="back-link">← 首页</a>
<h1 class="text-2xl font-bold text-slate-100 mb-4">📚 资料库</h1>
<input type="text" id="search" class="search-box mb-4" placeholder="搜索文档..." oninput="filterDocs(this.value)">
<div id="doc-list" class="grid grid-cols-1 gap-2">
{"".join(items)}
</div>
<script>
function filterDocs(q) {{
  q = q.toLowerCase();
  document.querySelectorAll('#doc-list > a').forEach(c => {{
    c.style.display = c.textContent.toLowerCase().includes(q) ? '' : 'none';
  }});
}}
</script>
"""
    breadcrumbs = [("../", "首页"), ("#", "资料库")]
    write_page(out_dir, "docs/index.html", page("资料库", body, breadcrumbs))


def build_doc_detail(out_dir, md_path):
    """单个资料文档"""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    html = render_md(text)

    body = f"""
<a href="../" class="back-link">← 资料库</a>
<div class="prose text-slate-300 mt-2">
{html}
</div>
"""
    breadcrumbs = [("../../", "首页"), ("../", "资料库"), ("#", md_path.stem)]
    write_page(out_dir, f"docs/pages/{md_path.stem}.html", page(md_path.stem, body, breadcrumbs))


def build_videos_page(out_dir, videos):
    """全局视频页面"""
    if not videos:
        items = '<p class="text-slate-500">暂无视频文件</p>'
    else:
        cards = []
        for v in videos:
            rel = v.relative_to(ROOT)
            size_mb = v.stat().st_size / 1024 / 1024
            cards.append(f"""
<div class="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
  <video controls preload="none" class="w-full" style="max-height:250px">
    <source src="../{rel}" type="video/mp4">
  </video>
  <div class="px-3 py-2">
    <div class="text-sm text-slate-300 truncate">{v.name}</div>
    <div class="text-xs text-slate-500">{rel.parent.name} · {size_mb:.1f} MB</div>
  </div>
</div>""")
        items = f'<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">{"".join(cards)}</div>'

    p_class = "text-sm text-slate-400 mb-4"
    if not any((out_dir / "dramas").rglob("video_files")):
        note = '<p class="text-sm text-amber-400 mb-4 bg-amber-950 rounded-lg px-3 py-2 border border-amber-800">⚠️ 视频未包含在站点中。使用 --copy-videos 参数重新生成可包含视频文件。</p>'
    else:
        note = ""

    body = f"""
<a href="../" class="back-link">← 首页</a>
<h1 class="text-2xl font-bold text-slate-100 mb-4">🎬 视频素材</h1>
<p class="{p_class}">共 {len(videos)} 个视频</p>
{note}
{items}
"""
    breadcrumbs = [("../", "首页"), ("#", "视频素材")]
    write_page(out_dir, "videos/index.html", page("视频素材", body, breadcrumbs))


# ---------------------------------------------------------------------------
# 复制静态资源（图片/视频用符号链接或直接引用）
# ---------------------------------------------------------------------------

def copy_assets(out_dir, drama_dir, copy_images=True, copy_videos=False):
    """复制图片到站点目录（可部署），视频默认不复制（太大）"""
    # 图片
    if copy_images:
        img_out = out_dir / "dramas" / drama_dir.name / "images"
        if img_out.exists():
            shutil.rmtree(img_out)
        img_out.mkdir(parents=True, exist_ok=True)

        for img in find_images(drama_dir):
            rel = img.relative_to(drama_dir)
            target = img_out / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(img, target)

    # 视频（默认跳过，体积太大）
    if copy_videos:
        vid_out = out_dir / "dramas" / drama_dir.name / "video_files"
        if vid_out.exists():
            shutil.rmtree(vid_out)
        vid_out.mkdir(parents=True, exist_ok=True)

        for vid in find_videos(drama_dir):
            rel = vid.relative_to(drama_dir)
            target = vid_out / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(vid, target)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def build(output_dir, copy_videos=False):
    out = Path(output_dir).resolve()
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    print("扫描项目...")
    dramas = scan_dramas()
    docs = scan_docs()
    global_videos = scan_videos_global()

    print(f"  剧目: {len(dramas)}")
    print(f"  资料: {len(docs)}")
    print(f"  视频: {len(global_videos)}")

    # 首页
    print("生成首页...")
    build_home(out, dramas, docs, global_videos)

    # 每个剧目
    for d in dramas:
        print(f"  生成剧目: {d.name}")
        build_drama_page(out, d)
        copy_assets(out, d, copy_videos=copy_videos)

        md_files = find_md_files(d)
        for md in md_files:
            if "剧本" in md.name and "36集" in md.name:
                build_md_page(out, md, d, "outline")
            elif "EP" in md.name.upper():
                build_md_page(out, md, d, "scripts")
            elif any(k in md.name for k in ["卡片", "索引", "规范", "计划", "角色", "形象", "场景", "道具", "声音", "年代"]):
                build_md_page(out, md, d, "assets")
            else:
                build_md_page(out, md, d, "other")

    # 资料库
    print("生成资料库...")
    build_docs_page(out, docs)
    for md in docs:
        build_doc_detail(out, md)

    # 全局视频
    print("生成视频页面...")
    build_videos_page(out, global_videos)

    # 统计
    total_files = sum(1 for _ in out.rglob("*"))
    print(f"\n完成! 共生成 {total_files} 个文件")
    print(f"输出目录: {out}")
    print(f"\n本地预览:")
    print(f"  cd {out} && python3 -m http.server 8080")
    print(f"\n部署:")
    print(f"  - GitHub Pages: 推送 {out.name}/ 到 gh-pages 分支")
    print(f"  - Netlify: 拖拽 {out.name}/ 到 netlify.com/drop")


def main():
    parser = argparse.ArgumentParser(description="AI 短剧项目静态站点生成器")
    parser.add_argument("--output", "-o", default=str(ROOT / "site"), help="输出目录 (默认: site/)")
    parser.add_argument("--copy-videos", action="store_true", help="也复制视频文件（体积大）")
    args = parser.parse_args()
    build(args.output, copy_videos=args.copy_videos)


if __name__ == "__main__":
    main()
