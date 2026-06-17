# AI 短剧 Prompt / 模板资料包

## 目的

本文件收集了落地可用的 AI 短剧制作 prompt 与脚本模板，便于快速生成角色、场景、分镜与运镜方案。

## 目录

1. `vertical-drama-script-template.md` — 竖屏短剧脚本模板
2. `character-design-prompts.md` — 角色设计 prompt
3. `scene-design-prompts.md` — 场景设计 prompt
4. `storyboard-prompts.md` — 分镜生成 prompt
5. `camera-movement-prompts.md` — 镜头运动 prompt

## 1. 竖屏短剧脚本模板

文件：`short_drama_resources/clipcurator/vertical-drama-script-formats/templates/vertical-drama-script-template.md`

```text
## Project

- Title:
- Genre:
- Aspect ratio: 9:16
- Target episode length:
- Audience:

## Episode

- Episode number:
- Episode goal:
- Main conflict:
- Cliffhanger question:

## Scene format

EPISODE [number] - SCENE [number]
Location / Time:
Characters:

Visual beat:
[What the viewer sees first.]

Action:
[Short action paragraph.]

Dialogue:
CHARACTER:
"Line."

Camera / framing:
[Close-up, two-shot, over-the-shoulder, handheld, slow push-in.]

Continuity note:
[Character state, prop, costume, injury, relationship change.]

Next beat:
[What this scene pushes into.]
```

本模板补充：
- Hook 在前 3-5 秒出现
- 每个场景必须有视觉动作
- 对白简洁且冲突明确
- 集末留一个开放问题

## 2. 角色设计 Prompt

文件：`short_drama_resources/clipcurator/ai-storyboard-prompts/prompts/zh-cn/character-design-prompts.md`

### Prompt 1：角色设计表

```text
请为一个短剧角色生成角色设计表。

角色信息：
- 姓名：
- 年龄：
- 身份：
- 性格：
- 核心动机：
- 与其他角色关系：
- 视觉风格：[写实 / 日漫 / 3D]

请输出：
1. 基础形象
2. 面部特征
3. 服装设计
4. 色彩风格
5. 三套服装变化
6. 后续场景一致性注意事项
```

### Prompt 2：多角度角色视图

```text
请为这个角色生成多角度角色提示词：

- 正面
- 侧面
- 四分之三角度
- 特写

要求所有视图保持同一身份、服装和情绪基调。
```

## 3. 场景设计 Prompt

文件：`short_drama_resources/clipcurator/ai-storyboard-prompts/prompts/zh-cn/scene-design-prompts.md`

### Prompt 1：场景概念图

```text
请为一个短剧场景生成场景概念图提示词。

场景信息：
- 地点：
- 时间：
- 情绪基调：
- 出场人物：
- 关键动作：
- 视觉风格：[写实 / 日漫 / 3D]

请输出：
1. 全景提示词
2. 特写细节提示词
3. 俯视角提示词
4. 光线说明
5. 连续性注意事项
```

### Prompt 2：场景一致性指南

```text
请为这个场景地点生成一致性指南。

包括：
- 固定空间布局
- 反复出现的道具
- 光线规则
- 色彩风格
- 适合拍摄的角度
```

## 4. 分镜 Prompt

文件：`short_drama_resources/clipcurator/ai-storyboard-prompts/prompts/zh-cn/storyboard-prompts.md`

### Prompt 1：剧本转分镜

```text
请把下面这段剧本场景转换成分镜表。

每个镜头需要包含：
- 镜头编号
- 镜头类型
- 拍摄主体
- 动作
- 机位角度
- 镜头运动
- 画面提示词
- 预计时长

剧本场景：
[粘贴场景]
```

### Prompt 2：剧情节点转分镜

```text
请为下面这个剧情节点生成分镜：

剧情节点：
[描述剧情节点]

目标：
- 保持叙事清晰
- 展示情绪推进
- 避免不必要镜头
```

## 5. 镜头运动 Prompt

文件：`short_drama_resources/clipcurator/ai-storyboard-prompts/prompts/zh-cn/camera-movement-prompts.md`

### Prompt 1：镜头运动设计

```text
请为这个分镜场景设计镜头运动。

场景：
[描述场景]

可选镜头运动：
- 平移
- 推镜
- 拉镜
- 跟拍
- 环绕
- 静态特写

每个镜头运动请说明：
- 为什么适合这个情绪节点
- 从哪里开始，到哪里结束
- 希望观众注意什么
```

### Prompt 2：竖屏短剧运镜指南

```text
请为一集竖屏短剧生成镜头运动指南。

限制：
- 画幅：9:16
- 单集时长：[1 / 1.5 / 2 / 3] 分钟
- 风格：[写实 / 日漫 / 3D]
```

## 6. 快速使用建议

- 先用脚本模板完成一集基本结构。
- 再用角色与场景 prompt 生成视觉参考。
- 最后用分镜 prompt 把脚本拆成镜头。
- 生成镜头运动时，优先考虑 9:16 竖屏视觉空间。
- 所有 prompt 内容需与剧本核心冲突、角色动机、情绪节奏对齐。

## 7. 推荐组合

- `vertical-drama-script-template` + `storyboard-prompts`：从剧本到镜头。
- `character-design-prompts` + `scene-design-prompts`：从角色与场景到视觉资产。
- `camera-movement-prompts` + `storyboard-prompts`：从镜头结构到运动细节。

## 8. 直接入口

本资料包已落地文件：

- `short_drama_resources/clipcurator/vertical-drama-script-formats/templates/vertical-drama-script-template.md`
- `short_drama_resources/clipcurator/ai-storyboard-prompts/prompts/zh-cn/character-design-prompts.md`
- `short_drama_resources/clipcurator/ai-storyboard-prompts/prompts/zh-cn/scene-design-prompts.md`
- `short_drama_resources/clipcurator/ai-storyboard-prompts/prompts/zh-cn/storyboard-prompts.md`
- `short_drama_resources/clipcurator/ai-storyboard-prompts/prompts/zh-cn/camera-movement-prompts.md`
