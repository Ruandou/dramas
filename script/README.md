# 视频自动化 · 通用脚本说明

**资产安全（必读）**：即梦分镜目录与禁止占位覆盖等约定见根目录 **`AGENTS.md`**；Cursor Agent 同步遵守 `.cursor/rules/video-generated-safety.mdc`。

## 能做什么

| 步骤 | 工具 | 费用 |
|------|------|------|
| 多段 MP4 按序拼接 | `pipeline/local_pipeline.py` + ffmpeg | 0 |
| 铺 BGM（循环、与成片对齐） | 同上，config 里填 `bgm` | 0 |
| 封装字幕（SRT→mov_text 软轨） | 同上，config 里填 `srt` | 0 |
| 批量念对白（可选） | `pipeline/tts_batch_edge.py` + edge-tts | 0（个人轻量使用） |
| 按字幕时间叠配音 | `pipeline/mix_tts_from_srt.py` + ffmpeg | 0 |
| 方舟近 7 天任务列表 / 批量下载 | `pipeline/ark_generation_tasks.py`（需 `ARK_API_KEY`） | 0 |

不含：云端剪辑 API，商用配乐版权购买——需自行准备**可商用 BGM 文件**。对白时间轴由 SRT 驱动叠音，**单句时长仍以 TTS 为准**，可能与字幕结束时间略有出入。

方舟与 MCP 说明见**`AGENTS.md`**、`mcp/volc-jimeng/README.md`。

## 生成字幕（SRT）

按**每镜 MP4 真实时长**（ffprobe）累加时间轴，对白与镜号一一对应；空行表示该镜不出字。

```bash
python3 script/pipeline/gen_srt_from_clips.py \
  --clips 短剧/错嫁后我改写了王朝/素材/configs/ep01_clip_list.txt \
  --lines 短剧/错嫁后我改写了王朝/素材/configs/ep01_lines.txt \
  --out 短剧/错嫁后我改写了王朝/素材/configs/第01集_即梦14镜_对白参考.srt
```

编辑 `ep01_lines.txt` 后重新运行即可。

## 依赖

- macOS：`brew install ffmpeg`
- Python 3.9+（系统自带即可）

## 成片拼接（必做）

在仓库根目录下执行：

```bash
python3 script/pipeline/local_pipeline.py \
  --config 短剧/错嫁后我改写了王朝/素材/configs/config_ep01.json
```

输出见 `config_ep01.json` 的 `output` 字段；当前默认带 SRT 时为**`素材/output/`**下文件。

**听不到声音、看不到字**：若分镜/成片本身**无音轨**，流水线默认会注入**静音 AAC**（`silent_audio_if_missing`）；要听 BGM 请在 config 里填 `bgm`。**QuickTime 常不显示 mov_text**，请用**VLC / IINA**，或依赖同目录自动复制的**旁路 `.srt`**（`sidecar_srt`）。

若某条 `clips` 路径不存在会报错。

**仅有整条成片，要按约 5 秒拆成 14 镜素材**：可用 `split_video_segments.py`（从成片只抽视频轨切段），例如：

```bash
python3 script/pipeline/split_video_segments.py \
  --input 短剧/错嫁后我改写了王朝/素材/output/第01集_软字幕.mp4 \
  --out-dir 短剧/错嫁后我改写了王朝/素材/output/ep01_5s_split \
  --segment-time 5 \
  --install-ep01
```

`--install-ep01` 会把 `slice_000…013` 复制为 `generated/` 下与 `config_ep01.json` 一致的文件名；切段为流复制，单段时长会随关键帧略长于 5 秒（常见约 5.04s）。

**成片几乎没画面、只有字幕轨能看**：多半是 `generated/` 里单镜只有几 KB（占位或损坏），拼出来码率极低。请先 `ls -lh 短剧/错嫁后我改写了王朝/素材/generated/*.mp4`：**正常即梦导出一般是数 MB 级**；确认后再跑 `gen_srt_from_clips` 与 `local_pipeline`。

## BGM

1. 将 `xxx.mp3` 放到例如 `短剧/错嫁后我改写了王朝/素材/assets/bgm.mp3`（目录需自建）。
2. 编辑 `config_ep01.json`：`"bgm": "短剧/错嫁后我改写了王朝/素材/assets/bgm.mp3"`，可调 `bgm_volume`（0～1）。

## 字幕

1. 准备 UTF-8 的 `.srt`（时间轴需与成片一致；可从剪映导出再改路径）。
2. 在 config 里设 `"srt": "路径/xxx.srt"`。

## 配音（可选）

```bash
pip install -r script/requirements.txt
# 编辑 configs/ep01_lines.txt 一行一句
python3 script/pipeline/tts_batch_edge.py \
  --lines 短剧/错嫁后我改写了王朝/素材/configs/ep01_lines.txt \
  --out-dir 短剧/错嫁后我改写了王朝/素材/automation/tts_out_ep01
```

得到 `001.mp3`…（行号命名，空行不生成）后，可用**`mix_tts_from_srt.py`**按**同一条 SRT**的起始时间叠到成片上：

```bash
python3 script/pipeline/mix_tts_from_srt.py \
  --video 短剧/错嫁后我改写了王朝/素材/output/第01集_全14镜_软字幕.mp4 \
  --srt 短剧/错嫁后我改写了王朝/素材/configs/第01集_即梦14镜_对白参考.srt \
  --tts-dir 短剧/错嫁后我改写了王朝/素材/automation/tts_out_ep01 \
  --output 短剧/错嫁后我改写了王朝/素材/output/第01集_带配音.mp4
```

可选 `--original-volume 0.3` 压低原片/BGM。也可用 Cursor MCP 工具 **`local_mix_tts_srt`**。

## dry-run

```bash
python3 script/pipeline/local_pipeline.py \
  --config 短剧/错嫁后我改写了王朝/素材/configs/config_ep01.json --dry-run
```
