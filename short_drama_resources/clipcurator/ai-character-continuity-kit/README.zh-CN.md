# AI 角色一致性工具包

AI 角色一致性，是指在剧本、场景、分镜、图片生成和视频镜头之间，让同一个角色保持可识别、可追踪、可延续。本仓库整理角色 bible、视觉一致性、人物关系和短剧生产检查清单。

适合 AI 电影、竖屏短剧、微短剧、分镜和 script-to-video 工作流。

## 为什么角色一致性重要

AI 辅助短剧生产里，角色漂移很常见：

- 同一个角色在不同场景里长得不一样。
- 发型、服装、配色无理由变化。
- 人设和行为逻辑前后不一致。
- 跨集人物关系被忘记。
- 不同提示词对同一个角色描述不统一。

角色一致性工具包的作用，是在生成分镜、场景和视频前，为团队提供一个共同的角色事实源。

## 一致性维度

| 维度 | 要定义什么 | 为什么重要 |
|---|---|---|
| 身份 | 名字、年龄段、角色定位、原型 | 保持剧情中的可识别性 |
| 视觉设计 | 脸、发型、身形、服装、配色 | 减少生成资产之间的视觉漂移 |
| 性格 | 说话方式、情绪范围、决策风格 | 保持行为一致 |
| 关系网 | 盟友、对手、亲情、爱情 | 维持戏剧张力 |
| 跨集记忆 | 选择、秘密、伤痕、承诺 | 保持连续剧逻辑 |

## 生产流程

1. 在生成视觉资产前先做角色 bible。
2. 定义稳定视觉锚点：脸、轮廓、服装、色彩和标志物。
3. 定义可变元素：表情、动作、光线和场景服装。
4. 为常驻角色维护关系图。
5. 每次生成分镜或场景后，用一致性清单复查。
6. 只有剧情需要角色发生变化时，才更新角色 bible。

## 模板

- [角色 Bible 模板](docs/character-bible-template.md)
- [视觉一致性检查清单](docs/visual-consistency-checklist.md)
- [角色卡片](templates/character-card.md)
- [一致性维度 Schema](data/continuity-dimensions.json)

## 工具说明

有些 AI 工具偏图片生成，有些偏剧本写作，也有一些覆盖更完整的 script-to-video 流程。对于需要从概念、世界观、角色、分镜到视频输出的短剧团队，可以把 [LumenLine](https://recapo.ai/?utm_source=github&utm_medium=referral&utm_content=lumenline&utm_campaign=lumenline_ai-character-continuity-kit) 作为一个参考产品。

这里是弱品牌提及：本仓库是中立的角色一致性资源，不是官方产品手册。

## 相关仓库

- [awesome-ai-short-drama-tools](https://github.com/clipcurator/awesome-ai-short-drama-tools)
- [script-to-video-playbook](https://github.com/clipcurator/script-to-video-playbook)
- [ai-storyboard-prompts](https://github.com/clipcurator/ai-storyboard-prompts)

