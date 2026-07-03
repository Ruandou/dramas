#!/usr/bin/env bash
# init_drama_project.sh — 创建新短剧项目的标准脚本
#
# 为什么需要它（不靠 agent 自觉）：
#   仓库根目录名是 `dramas`，子目录装各短剧项目的子目录也叫 `dramas/`。模型建项目时
#   极易把"项目根 dramas/<剧名>"与"仓库根 dramas"搞混，要么写到仓库根、要么写到错的
#   上层目录，污染 assets/、产生孤儿文件、下游找不到归属导致重复扣费。让 agent 用这
#   个脚本（而非手写 mkdir），路径完全由脚本控制、模型无决定空间。
#
# 用法：
#   script/init_drama_project.sh <剧名>            # 在仓库根的 dramas/ 下创建 dramas/<剧名>/
#   script/init_drama_project.sh <剧名> --dry-run  # 只打印将要创建的路径不写盘
#
# 守门规则（脚本内置）：
#   1. 必须从仓库根调用（脚本自动按自身位置回溯）；若不在仓库根、或仓库根下找不到 dramas/
#      子目录 → 退出。
#   2. 剧名不得为空、不得含 `/` 或 `..`（防路径穿越）、不得与现存项目重名（防覆盖）。
#   3. 创建位置永远是 <repo_root>/dramas/<剧名>/，不受当前工作目录影响。
#   4. 仅生成空目录骨架 + 一个 制片规范.md 占位 + 一个 工作计划.md 占位，后续内容由
#      production-planner 填充。
set -euo pipefail

DRY_RUN=0
TITLE=""
for a in "$@"; do
  case "$a" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help)
      sed -n '1,30p' "$0"; exit 0 ;;
    *) TITLE="$a" ;;
  esac
done

# 1. 定位仓库根：脚本位于 <repo>/script/init_drama_project.sh
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRAMAS_DIR="$REPO_ROOT/dramas"

# 守门：仓库根下必须有 dramas/ 子目录（确认是本项目仓库）
if [ ! -d "$DRAMAS_DIR" ]; then
  echo "❌ 未在仓库根下找到 dramas/ 子目录：$DRAMAS_DIR" >&2
  echo "   请确认脚本位于本项目仓库的 script/ 下、且仓库根下有 dramas/ 装各短剧项目。" >&2
  exit 2
fi

# 2. 校验剧名
if [ -z "$TITLE" ]; then
  echo "用法: $(basename "$0") <剧名> [--dry-run]" >&2
  echo "例:   $(basename "$0") 三个闺蜜一台戏" >&2
  exit 2
fi
case "$TITLE" in
  */*|*..*|*)
    if [[ "$TITLE" == *"/"* || "$TITLE" == *".."* ]]; then
      echo "❌ 剧名含非法字符（/ 或 ..）：$TITLE" >&2
      exit 2
    fi
    ;;
esac
if [ "$TITLE" = "dramas" ] || [ "$TITLE" = "script" ] || [ "$TITLE" = "mcps" ] || [ "$TITLE" = "assets" ]; then
  echo "❌ 剧名 '$TITLE' 与仓库顶层目录同名，会造成路径混淆，请换名。" >&2
  exit 2
fi

PROJ_ROOT="$DRAMAS_DIR/$TITLE"

# 3. 重名保护
if [ -e "$PROJ_ROOT" ]; then
  echo "❌ 项目已存在：$PROJ_ROOT" >&2
  echo "   如要重建请先手动移走/删除旧目录，再跑本脚本。" >&2
  exit 2
fi

# 4. 目录骨架（与 drama-director.md「创建项目目录」对齐）
# 注：守门段已用 explicit exit 2 报错退出；这里 set -e 退出码 = 1。两段均故意，
# 非空退出码即可让调用方/agent 知道失败。
DIRS=(
  "剧本"
  "资产"
  "assets/looks"
  "assets/scenes"
  "assets/props"
  "assets/generated"
)

# 5. 执行（或 dry-run 打印）
if [ "$DRY_RUN" -eq 1 ]; then
  echo "dry-run: 将创建 $PROJ_ROOT 含以下子目录："
  for d in "${DIRS[@]}"; do echo "  $PROJ_ROOT/$d"; done
  echo "dry-run: 将创建占位文件 制片规范.md、工作计划.md"
  exit 0
fi

mkdir -p "$PROJ_ROOT"
for d in "${DIRS[@]}"; do
  mkdir -p "$PROJ_ROOT/$d"
done

# 复制格式模板到新项目
TEMPLATE_SRC="script/模板_剧本.md"
if [ -f "$TEMPLATE_SRC" ]; then
  cp "$TEMPLATE_SRC" "$PROJ_ROOT/资产/_模板_剧本.md"
  echo "  已复制格式模板 -> $PROJ_ROOT/资产/_模板_剧本.md"
else
  echo "  ⚠️ 未找到模板文件: $TEMPLATE_SRC" >&2
fi

# 复制 YAML 格式模板到新项目
for yaml_tmpl in "_模板_shots.yaml" "_模板_segments.yaml"; do
  SRC="script/$yaml_tmpl"
  if [ -f "$SRC" ]; then
    cp "$SRC" "$PROJ_ROOT/资产/$yaml_tmpl"
    echo "  已复制 $yaml_tmpl -> $PROJ_ROOT/资产/$yaml_tmpl"
  else
    echo "  ⚠️ 未找到 YAML 模板: $SRC" >&2
  fi
done

# 占位文件（让存在性校验通过：--project-root 下要含 制片规范.md 才不软警告）
cat > "$PROJ_ROOT/制片规范.md" <<EOF
# 制片规范 — $TITLE

> 占位文件。由 \`production-planner\` 在 Stage 2 填充：ID 系统、资产骨架、分段规则。
> 创建时间：$(date "+%Y-%m-%d %H:%M:%S")
EOF

cat > "$PROJ_ROOT/工作计划.md" <<EOF
# 工作计划 — $TITLE

> 流水线状态追踪文件。由 \`drama-director\` 在项目初始化后填充、各阶段推进时更新。
> 创建时间：$(date "+%Y-%m-%d %H:%M:%S")

## 流水线状态

| Stage | Agent | 状态 | 备注 |
|-------|-------|------|------|
| 0 项目初始化 | drama-director | ✅ 已初始化 | $(date "+%Y-%m-%d") |
| 1 故事架构 | story-architect | ⏳ 待启动 | |
| 2 制片规范 | production-planner | ⏳ 待启动 | |
| 3a 道具设计 | prop-designer | ⏳ 待启动 | |
| 3b 角色设计 | character-designer | ⏳ 待启动 | |
| 3c 场景设计 | scene-designer | ⏳ 待启动 | |
| 4 分集剧本 | scene-writer | ⏳ 待启动 | |
| 5 分镜构建 | segment-builder | ⏳ 待启动 | |
| 6 合规审查 | drama-director | ⏳ 待启动 | |
EOF

chmod +x "$PROJ_ROOT/assets" 2>/dev/null || true

echo "✅ 已创建项目：$PROJ_ROOT"
echo "骨架:"
( cd "$PROJ_ROOT" && find . -type f -o -type d | sort | sed 's/^/  /' )
echo ""
echo "下一步：用 \`drama-director\` 推进 Stage 1。CLI 调用以此根："
echo "  python3 mcps/volc-ark/scripts/ark_*.py <cmd> --project-root '$PROJ_ROOT' ..."