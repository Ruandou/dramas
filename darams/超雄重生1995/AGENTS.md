# 超雄重生1995 · Agent / CLI 指引

> 年代穿越刑侦短剧，36集。男主陆峥重生回1995年，用前世经验+完美犯罪侧写系统在没有监控、DNA不普及的年代从底层警员逆袭为刑侦支队长。

---

## 改剧本顺序（强制，不可跳步）

1. **主剧本** `短剧剧本_超雄重生1995_36集.md`
2. **分集分镜** `剧本/EP##_shots.md`（必须引用 CHAR-### / SCENE-### ID）
3. **导出 YAML** `python3 script/storyboard_to_seedance.py EP##`
4. **审查段落** `剧本/EP##_segments.yaml`
5. **验证 & 提交**

**禁止**先改 `segments.yaml` 再改分镜——上游变动会覆盖你的修改。

---

## ID 引用规范

所有分镜文件中：

- 角色必须使用 **`CHAR-###`** ID，禁止写"陆峥""秦飒"等明文名
- 场景必须使用 **`SCENE-###`** ID，禁止写"派出所""棉纺厂"等明文名

示例：`CHAR-001` = 陆峥，`SCENE-003` = 城南派出所办公室

ID 映射表维护在角色卡 / 场景卡中，分镜文件仅做引用。

---

## MCP 工具（volc-ark）

| 工具 | 扣费 | 说明 |
|------|------|------|
| `ark_seedance_list` / `get` / `wait` | 否 | 查询/轮询已有任务 |
| `ark_seedance_download` | 否 | 下载成片到指定路径 |
| `ark_list_tasks` | 否 | 读取 `assets/generated/` 下 tasks.json |
| `ark_drama_pull` | 否 | git pull + 按 tasks.json 下载同事段落 |
| **`ark_seedance_create`** / `shots` | **是** | Seedance 2.0 视频生成 |
| **`ark_seedream_generate`** / `batch` | **是** | Seedream 5.0 图片生成 |

### ⚠️ 扣费工具授权规则

以下工具**必须获得用户明确授权**后方可调用：

- `ark_seedance_create` / `ark_seedance_shots`
- `ark_seedream_generate` / `ark_seedream_batch`

**违规调用 = 浪费用户资金，严禁自行决策。**

`mcp.json` 配置：

```json
"volc-ark": {
  "env": {
    "ARK_API_KEY": "…",
    "DRAMA_PROJECT_ROOT": "/绝对路径/darams/超雄重生1995"
  }
}
```

---

## CLI 参考

```bash
cd darams/超雄重生1995

# 拉取集素材（含同事共享段落）
./script/pull_episode.sh EP01

# 拼接整集
bash script/ffmpeg_concat_episode.sh EP01

# 导出分镜 YAML
python3 script/storyboard_to_seedance.py EP01

# 校验时代一致性
python3 script/validate_era.py EP01

# 整集字幕（听写 → 校对 → 烧录）
HF_ENDPOINT=https://hf-mirror.com python3 script/gen_audio_srt.py assets/generated/EP01/EP01_full.mp4 -o assets/generated/EP01/EP01_audio.srt
python3 script/review_audio_srt.py assets/generated/EP01/EP01_audio.srt
python3 script/burn_subs_pillow.py assets/generated/EP01/EP01_full.mp4 assets/generated/EP01/EP01_audio.srt -o assets/generated/EP01/EP01_subtitled.mp4
```

---

## 整集字幕

**必须听写成片音频**，禁止用 `segments.yaml` 对白按时长比例分配。

| 步骤 | 脚本 | 输出 |
|------|------|------|
| 1 听写 | `script/gen_audio_srt.py` | `EP##_audio.srt` |
| 2 校对 | `script/review_audio_srt.py` | 同文件 in-place（修同音错字） |
| 3 烧录 | `script/burn_subs_pillow.py` | `EP##_subtitled.mp4` |

- **样式**：白字 + 黑描边、底部居中、**无黑底条**（对齐 EP04）
- **镜像**：`HF_ENDPOINT=https://hf-mirror.com`（Whisper 模型下载）
- **纠错**：改 `EP##_audio.srt` 后只重跑第 3 步；Agent 听写后须自动跑 `review_audio_srt.py`

Cursor 规则：仓库根 `.cursor/rules/chao-xiong-subtitles.mdc`

---

## 素材安全规则

| 规则 | 说明 |
|------|------|
| **禁止覆盖** | `assets/generated/` 下的正式 MP4 不可用占位/测试条覆盖 |
| **占位输出** | 必须写到 `assets/generated/_placeholders/`，文件名不得占用正式命名 |
| **gitignore** | `generated/` 被忽略，Cursor 搜索不可见；判断文件存在请用终端 `ls -lh` |
| **体积检查** | 正式即梦/方舟导出为数 MB 级；数 KB = 占位/损坏，不可继续流水线 |

```bash
# 检查素材状态
ls -lh assets/generated/EP01/*.mp4
```

### 引用图片提交规则

- **TOS 优先**：提交 Seedance 段落时，优先使用 TOS 永久链接（`tos_url`），可支持 4-6 张引用图/段
- **base64 兜底**：TOS 未上传时回退本地 base64，限制 ≤3 张/段
- **cdn_urls.json**：上传 TOS 后更新 `assets/looks/cdn_urls.json` 和 `assets/scenes/cdn_urls.json`，`tos_url` 为首选字段

---

## 团队协作

1. 同事 push `assets/generated/EP##/tasks.json` 后，**24 小时内**拉取
2. 超过 24h 视频直链可能过期，需重新生成
3. `ark_drama_pull` 自动处理 git pull + 按 tasks.json 下载
4. **勿覆盖**他人已上传的正式 `EP##-SEG*.mp4`

---

## 项目结构（规划）

```
darams/超雄重生1995/
├── AGENTS.md              ← 本文件
├── 短剧剧本_超雄重生1995_36集.md
├── 人物小传_超雄重生1995.md
├── 剧本/
│   ├── EP01/EP01_shots.md
│   ├── EP01/EP01_segments.yaml
│   └── …
├── assets/
│   ├── generated/         ← 正式视频（gitignored）
│   ├── keyframes/
│   ├── looks/
│   └── scenes/
└── script/
    ├── storyboard_to_seedance.py
    ├── gen_audio_srt.py       ← Whisper 听写 SRT
    ├── review_audio_srt.py    ← 听写后校对同音错字
    ├── burn_subs_pillow.py    ← Pillow 硬字幕（EP04 样式）
    ├── ffmpeg_concat_episode.sh
    ├── pull_episode.sh
    └── validate_era.py
```
