# Seedance 2.0 · 《我租的女友，真把我当老公了》

> 对齐 [`超雄重生1995/docs/Seedance2_分镜与API映射.md`](../../超雄重生1995/docs/Seedance2_分镜与API映射.md)  
> 差异：**现代剧允许 smartphone / 笔记本电脑**；年代负向词改为 **禁止古装、禁止 1990 年代物品**

## 流水线

```
角色卡 / 场景卡片 → Seedream 定妆 → keyframes（可选）
    → EP##_*.md → EP##_shots.yaml → EP##_segments.yaml → API → assets/generated/EP##/
```

## 默认 API

| 项 | 值 |
|----|-----|
| model | `doubao-seedance-2-0-fast-260128` |
| ratio | 9:16 |
| resolution | 1080x1920 |
| generate_audio | true |
| prompt_suffix | 2020年代中国都市，写实短剧，竖屏9比16，对白时画面底部居中简体白字字幕与语音同步；禁止其它乱字 |

## 负向词（本剧）

```
1990s interior, CRT TV, flip phone, ancient costume, palace, horse carriage,
anime style, heavy neon cyberpunk, unreadable gibberish text on signs
```

## 声音提示（voice_prompts）

| ID | 提示 |
|----|------|
| CHAR-001 | 成年男性，29岁，略疲惫但清晰，都市白领口语 |
| CHAR-002 | 成年女性，26岁，温柔专业，语速平稳，像 trained service tone |

## 改稿顺序

1. `短剧剧本_我租的女友真把我当老公了_36集.md`  
2. `剧本/_模板.md` → `剧本/EP##/EP##_*.md`  
3. `EP##_shots.yaml` → `EP##_segments.yaml`  
4. 提交 API（**须用户明确授权扣费**）

## 体量标准（对齐超雄重生1995）

| 项 | 目标 |
|----|------|
| 分镜 md | **180–230 行**；列含 **运镜 / 画面 / 对白** |
| 有效镜 | **24–28**（+1–3 `skip` 字幕/音效） |
| API 段 | **10–12 段**，每段 **4–12 秒** |
| 裸素材 | **~100–120 秒** / 集 → 剪成 **2–2.5 分钟** |
| segments.yaml | 每段 `dialogue_lines` 带 **emotion**；`api.text` 写清 **镜头秒数** |
| shots.yaml | 每镜 `mode` / `dialogue` / `return_last_frame`（`i2v_ref` 连镜） |

EP01–EP06 已按 v2 重写；EP07+ 待续。
