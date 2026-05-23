# Seedance 2.0 分镜格式与 API 映射 · 超雄重生1995

> **适用剧目**：《超雄重生1995》· 现代刑侦 · 年代：1995 年中国城市  
> **版本**：v1.0 · 2026-05-23  
> **模型（默认）**：`doubao-seedance-2-0-fast-260128`  
> **Base URL**：`https://ark.cn-beijing.volces.com/api/v3`  
> **默认分辨率**：1080×1920（竖屏 9:16）  
> **默认含音频**：`generate_audio: true`（有声段落为主线）

---

## 官方文档入口

| 文档 | 链接 | 用途 |
|------|------|------|
| Doubao Seedance 2.0 系列教程 | [2291680](https://www.volcengine.com/docs/82379/2291680?lang=zh) | 调用方式、多模态入参示例 |
| Seedance 2.0 提示词指南 | [2222480](https://www.volcengine.com/docs/82379/2222480?lang=zh) | 主体/风格/运镜/规格五要素 |
| Seedream 助力 Seedance 最佳实践 | [1951250](https://www.volcengine.com/docs/82379/1951250?lang=zh) | Seedream 出分镜关键帧 → 再喂 Seedance |
| API 参考 | [1393047](https://www.volcengine.com/docs/82379/1393047?lang=zh) | 字段说明 |
| 输出格式 / 裁剪规则 | [1366799](https://www.volcengine.com/docs/82379/1366799?lang=zh) | 分辨率、ratio、图片约束 |

---

## 一、整体流水线

```
角色卡 / 场景卡片（CHAR-### / SCENE-###）
    ↓ ① 定妆图（Seedream 生成）
assets/looks/CHAR-###-L##.png     assets/scenes/SCENE-###.png
    ↓ ② 合首帧（可选，场景底图 + 人物融图）
assets/keyframes/EP##/EP##-S##_first.png
    ↓ ③ 分镜 YAML（storyboard_to_seedance.py 导出）
剧本/EP##/EP##_shots.yaml
    ↓ ④ 段落 YAML（手工切段，合并对白/旁白）
剧本/EP##/EP##_segments.yaml
    ↓ ⑤ API 提交（每段 generate_audio: true）
assets/generated/EP##/EP##-SEG*.mp4
    ↓ ⑥ ffmpeg 顺接（可选）
EP##_full.mp4（本地成片）
```

**原则**：`segments.yaml` 是 API 提交单位（约 4–12 秒）；`shots.yaml` 是分镜参考，不直接提交。

---

## 二、API 真实形态

Seedance 2.0 使用 **`content[]` 多模态数组** + 异步任务。

```http
POST https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
```

要点：

- **`content`**：`text` + 多张 `image_url`（带 `role`）+ 可选 `audio_url`
- **`role`**：`first_frame` | `last_frame` | `reference_image` | `reference_audio`
- **参考上限**：图 ≤9、音频 ≤3；提示词中用 **`[图1][图2]`** 对应 content_roles 顺序
- **轮询**：`GET …/tasks/{id}` → `succeeded` → `content.video_url`（**24h 内转存**）
- **模型 id**：以控制台为准，默认 `doubao-seedance-2-0-fast-260128`

本剧推荐 `mode`：

| mode | 含义 | 适用场景 |
|------|------|----------|
| `skip` | 黑屏/字卡/画外：并入相邻 segment | 字幕镜、场次切换 |
| `t2v` | 纯文本生成（仅 `content.text`） | 无参考图、环境空镜 |
| `i2v` | 首帧图 + 文本 | 有场景/人物首帧图时 |
| `i2v_ref` | 定妆/场景 reference_image + 首帧 | 人物一致性要求高时（**推荐**） |

---

## 三、分镜表格列与 API 映射

### 3.1 分镜表格格式

```markdown
| shot_id | 镜号 | 场景 | 角色 | 形象 | 景别 | 时长 | 模式 | 画面 | 运镜 | 对白/备注 |
```

| 表格列 | API / 资产 | 说明 |
|--------|-----------|------|
| `shot_id` | `shot_id`（如 `EP01-S02`） | 稳定 ID，脚本自动生成 |
| `场景` | `SCENE-###` → 背景图 / Prompt | `assets/scenes/SCENE-###.png` |
| `形象` | `CHAR-###-L##` → 定妆图 | `assets/looks/CHAR-###-L##.png` |
| `景别` | 写入 `api.text` | 见景别映射表 |
| `时长` | `duration_sec` | 单段 4–12 秒（API 硬限制） |
| `模式` | `mode` 枚举 | `t2v` / `i2v` / `i2v_ref` / `skip` |
| `画面` | `api.text` 主体 | 用 ID，不写人名 |
| `运镜` | 拼入 `api.text` 头部 | 见运镜映射表 |
| `对白/备注` | `dialogue[]` + segments 对白 | 不进单镜 API，进 segments |

### 3.2 景别映射

| 景别 | 写入 Prompt |
|------|------------|
| 特写 | 镜头特写 |
| 近景 | 镜头近景 |
| 中景 | 镜头中景 |
| 全景 | 镜头全景 |
| 主观 | 主观镜头 |
| 跟拍 | 镜头跟随 |
| 慢镜 | 慢动作 |

---

## 四、推荐双层结构

### 4.1 `EP##_shots.yaml`（脚本导出，仅参考）

```yaml
episode_id: EP01
source_md: 剧本/EP01/EP01_醒来.md
defaults:
  endpoint: https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks
  model: doubao-seedance-2-0-fast-260128
  ratio: "9:16"
  resolution: 1080x1920
  duration: 10
  generate_audio: true
  watermark: false
  prompt_suffix: "1995年中国城市，写实电影风格，竖屏9比16，无智能手机，无平板，无LED广告屏，无现代车型，无清晰广告文字"
  negative_prompt: "smartphone, flat screen TV, LED lights, modern car, laptop, tablet, QR code, delivery box, power bank, glass curtain wall, LED billboard, Nike logo, Adidas logo, wireless earbuds, bubble tea cup, neon RGB lighting"

shots:
  - shot_id: EP01-S01
    shot_no: 1
    mode: skip
    note: "字幕：1995年，南城市。"

  - shot_id: EP01-S02
    shot_no: 2
    mode: i2v_ref
    duration_sec: 8
    refs:
      scene_id: SCENE-001
      look_ids: [CHAR-001-L01]
    assets:
      look_urls:
        CHAR-001-L01: assets/looks/CHAR-001-L01.png
      scene_urls:
        SCENE-001: assets/scenes/SCENE-001.png
      first_frame: assets/keyframes/EP01/EP01-S02_first.png
    api:
      text: "【图1】CHAR-001（89式警服，大盖帽）【图2】SCENE-001（城南派出所走廊，老式日光灯管）。镜头近景，CHAR-001猛然睁眼，坐起身，目光锐利，喘气声。1995年中国城市，写实电影风格，竖屏9比16，无智能手机，无LED广告屏"
      content_roles:
        - {file: CHAR-001-L01, role: reference_image, label: 图1}
        - {file: SCENE-001, role: reference_image, label: 图2}
        - {file: first_frame, role: first_frame}
      return_last_frame: true
      seed: 2001
    dialogue: []

  - shot_id: EP01-S03
    shot_no: 3
    mode: t2v
    duration_sec: 5
    api:
      text: "空镜。城南派出所院落，1995年清晨，212吉普停靠，自行车排，水泥砖墙，无广告牌。竖屏9比16，写实电影风格"
```

### 4.2 JSON 形态（API 提交展开后）

```json
{
  "model": "doubao-seedance-2-0-fast-260128",
  "content": [
    {"type": "text", "text": "【图1】CHAR-001……【图2】SCENE-001……"},
    {
      "type": "image_url",
      "image_url": {"url": "data:image/png;base64,…"},
      "role": "reference_image"
    },
    {
      "type": "image_url",
      "image_url": {"url": "data:image/png;base64,…"},
      "role": "first_frame"
    }
  ],
  "ratio": "9:16",
  "resolution": "1080x1920",
  "duration": 8,
  "generate_audio": true,
  "return_last_frame": true
}
```

---

## 五、素材清单（生成视频前必做）

### 5.1 定妆图（角色一致性锚点）

| 目录 | 命名 | 来源 |
|------|------|------|
| `assets/looks/` | `CHAR-###-L##.png` | Seedream 生成（Character Sheet，白底正面全身） |
| `assets/scenes/` | `SCENE-###.png` | Seedream 生成（空景，无人，1995 年代） |
| `assets/props/` | `PROP-###-*.png` | 道具参考图（五四手枪、老式手铐等） |

**L01 为唯一面部锚点**：L02+ 必须 `based_on: CHAR-###-L01`，以 L01 为 reference_image 生图。

### 5.2 镜头首帧（i2v / i2v_ref 用）

| 目录 | 命名 | 合成方式 |
|------|------|----------|
| `assets/keyframes/EP##/` | `EP##-S##_first.png` | 场景图 + 人物定妆（融图 / ControlNet / 手动合成） |

`return_last_frame: true` 时，镜 N 尾帧另存为 `EP##-S##_last.png` 供下一镜首帧使用。

### 5.3 不必每镜单独出场景图

同一 `SCENE-###` 多镜可复用底图，仅更换人物 pose 的首帧合成。

---

## 六、Prompt 拼装规则（1995 年代）

### 6.1 Prompt 结构

```
[运镜词] + [景别] + [画面] + [1995年代后缀] + negative 另字段
```

**1995 年代后缀（所有镜默认）**：
```
1995年中国城市，写实电影风格，竖屏9比16，无智能手机，无平板，无LED广告屏，无现代车型，无清晰广告文字
```

**Negative Prompt（所有生成任务必加）**：
```
smartphone, flat screen TV, LED lights, modern car, laptop, tablet,
QR code, delivery box, power bank, glass curtain wall, subway station,
LED billboard, Nike logo, Adidas logo, wireless earbuds, bubble tea cup,
modern minimalist interior, neon RGB lighting
```

> 完整年代禁忌列表见 [`制片规范.md §5.3`](../制片规范.md)。

### 6.2 有首帧图时的 Prompt 原则

- 有 `first_frame` 时：**不写**五官细节，只写动作、光影、运镜
- 无图 `t2v` 时：拼接角色卡 L01 外貌简述 + 场景卡片环境描述

### 6.3 道具镜写法（强制）

追逃、缴枪、搏斗等涉及道具动作的镜头：

1. 段首写「角色分工」：谁可碰道具、谁禁止
2. 每句动作绑定 `图N`（不用明文人名）
3. 具体描述道具（五四手枪，木质枪套，标准尺寸）
4. 因果链叙事，非清单

---

## 七、有声段落（segments.yaml 主线）

| 字段 | 说明 |
|------|------|
| `segment_id` | 如 `EP01-SEG01`，一段约 4–12 秒 |
| `shot_ids` | 此段合并的镜号列表 |
| `api.text` | 对白 + 动作 + voice_prompt |
| `generate_audio` | 固定 `true` |
| `voice_prompt` | 说话人音色描述（跨段保持全文一致） |
| `duration_sec` | 4–12（API 硬限制） |

**音色模板**（跨段不变）：
- 陆峥：`"成年男性，25岁，沉稳低沉，语速偏慢，有阅历感"`
- 秦飒：`"成年女性，28岁，冷静干练，语速中等，不带感情色彩"`

---

## 八、EP01 体量估算

| 项目 | 数量 |
|------|------|
| 分镜行（含 skip） | 约 20–25 |
| 需 API（非 skip） | 约 18–22 |
| segments（合并后） | 约 6–8 |
| 定妆图需求 | looks 4–5 张 + scenes 3–4 张 |
| 首帧图（i2v 用） | 约 10–15 张 |

---

## 九、脚本命令速查

```bash
cd darams/超雄重生1995

# 导出分镜 YAML（EP01）
python3 script/storyboard_to_seedance.py EP01

# 导出多集
python3 script/storyboard_to_seedance.py EP01 EP02 EP03

# 同时生成 segments 骨架
python3 script/storyboard_to_seedance.py EP01 --with-segments

# 年代合规校验
python3 script/validate_era.py EP01

# 拼接成片
bash script/ffmpeg_concat_episode.sh EP01
```

---

## 十、与仓库其他剧目对比

| 项目 | 天工开物（参考） | 超雄重生1995 |
|------|----------------|--------------|
| 年代 | 明代苏州（天启） | 1995 年中国城市 |
| 分辨率 | 720p | 1080×1920 |
| generate_audio 默认 | false | **true** |
| 闪回处理 | SCENE-004 特殊后缀 | 无（全剧为 1995 年代） |
| Negative | 无现代物品 | smartphone/LED/laptop… |

---

## 修订记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-05-23 | 初版；基于天工开物版本适配 1995 刑侦剧 |
