# AI 短剧中英文资料包

## 目标

这个文件是一个可直接使用的资料包索引，帮助你把“AI 短剧制作”从战略、流程、脚本、分镜、视觉 prompt、角色连续性，到国内落地实践，一起组织成中英文对照参考。

## 1. 英文资源汇总

### 1.1 clipcurator/ai-short-drama-production-workflows
- 链接：https://github.com/clipcurator/ai-short-drama-production-workflows
- 核心作用：把 AI 短剧做成完整生产流水线，不是单次 text-to-video。
- 关键内容：
  - 全量流程：Idea → Concept → Worldbuilding → Character system → Outline → Script → Visual assets → Storyboard → Camera movement → Short drama video
  - 生产原则：
    - 先验证概念，再生成素材
    - 先建立人物一致性，再做分镜
    - 分阶段处理世界观、剧本、视觉资产
    - 把分镜当成生产计划而不是纯预览
    - 关键阶段之间保持人工审核
  - 重要文档：Idea to Concept、Worldbuilding Workflow、Character System Design、Script to Assets、Storyboard to Video
  - 重要模板：Short Drama Project Bible、Episode Planning Template

### 1.2 clipcurator/vertical-drama-script-formats
- 链接：https://github.com/clipcurator/vertical-drama-script-formats
- 核心作用：提供竖屏短剧剧本格式与写作标准。
- 关键内容：
  - 竖屏剧集结构：Cold hook、Setup、Escalation、Turn、Cliffhanger
  - 剧本字段：Episode、Scene、Location、Characters、Visual beat、Dialogue、Camera note、Continuity note、Next-episode hook
  - 模板：Vertical Drama Script Template、Episode Structure Guide、Hook and Cliffhanger Patterns
  - 中文 companion：README.zh-CN.md

### 1.3 clipcurator/ai-storyboard-prompts
- 链接：https://github.com/clipcurator/ai-storyboard-prompts
- 核心作用：构建分镜 prompt 体系，覆盖角色、场景、分镜、镜头运动。
- 关键内容：
  - Prompt 包：Character design prompts、Scene design prompts、Storyboard prompts、Camera movement prompts
  - 中文支持：简体中文 prompt 文档
  - 模板：Storyboard Shot List Template

### 1.4 clipcurator/ai-character-continuity-kit
- 链接：https://github.com/clipcurator/ai-character-continuity-kit
- 核心作用：解决角色漂移和人物一致性问题。
- 关键内容：
  - 连续性维度：Identity、Visual design、Personality、Relationship map、Episode memory
  - 生产流程：先做角色 bible，再做视觉锚点，再复审 storyboard/scene
  - 模板：Character Bible Template、Visual Consistency Checklist、Character Card
  - 中文 companion：README.zh-CN.md

### 1.5 clipcurator/ai-short-drama-storyboard-shot-packs
- 链接：https://github.com/clipcurator/ai-short-drama-storyboard-shot-packs
- 核心作用：把分镜转为可执行的镜头包模板。
- 关键内容：
  - 类型：Cold-open tension、Dialogue power shift、Reveal and reaction、Romance close-up、Cliffhanger ending
  - 字段：Scene objective、Frame composition、Character emotion、Camera movement、Continuity risk、Generation prompt
  - 复审：Vertical-safe framing、Character continuity、Readable emotion、Clear object focus、Episode continuity

## 2. 中文资料汇总

### 2.1 国内短剧制作参考
- CSDN：中文短剧制作全流程详解（短剧制作的“剧本先行、分镜明确、角色统一、素材稳定、剪辑流畅”）
- 百度 B2B Wiki：短剧写作结构与三幕式设计
- 知乎专栏：分镜设计与视觉节奏，适合从剧本过渡到画面规划
- ArcLoop 中文手册：AI 短剧制作工具和流程指南，适合国内视觉 AI 工具实践

### 2.2 国内落地要点
- 明确创意点，优先提炼 3-5 个强冲突场景。
- 采用三幕式结构：20% 建立关系、60% 冲突升级、20% 反转或钩子。
- 每集解决一个小冲突、留下一个新悬念。
- 角色具体化：年龄、外形、服装、性格、声音、关系状态。
- 分镜要素：场景、光线、角色动作、镜头语言、时长控制。
- 素材生成前优先准备角色图、场景图、道具图，并做好多镜头一致性。
- 剪辑与合成要控制节奏：前 3 秒钩子，中段紧促，结尾留钩子。
- 必须加字幕，适应静音观看。

## 3. 本地仓库内部文档清单

### 3.1 直接可用文档
- docs/SD2.0_漫剧提示词指南.md
- docs/SD2.0_影视制作提示词指南.md
- docs/references/platform-review-gate.md
- docs/制片规范模板.md
- docs/AI_MediaKit_画质增强工具.md
- docs/AI_MediaKit_视频工具.md
- docs/SD2.0_短剧出海翻译配音解决方案.md
- docs/SD2.0_人物站位问题最优实践.md
- docs/SD2.0_视频字幕擦除文档.md

### 3.2 生产脚本与流水线
- script/pipeline_episode.py
- script/local_pipeline.py
- script/download_jimeng_from_tasks.py
- script/tts_batch_edge.py
- script/gen_srt_from_clips.py

### 3.3 项目结构参考
- dramas/错嫁后我改写了王朝/
- dramas/天工开物/

## 4. 操作建议

### 4.1 立即可执行的步骤
1. 建议先把英文 repo 的 `README.md` 和中文 companion `README.zh-CN.md` 保存到本地。
2. 拷贝 `vertical-drama-script-template.md`、`storyboard-shot-list-template.md`、`character-bible-template.md` 这类模板。
3. 用 `Short Drama Project Bible` 创建项目页，用 `Episode Planning Template` 做短剧集计划。
4. 结合本地 `docs/` 文档补充中文实施细则。

### 4.2 建议生成的落地文件
- `短剧制作流程概览.md`
- `AI短剧Prompt模板资料包.md`
- `AI 短剧 prompt 模板汇总.md`
- `国内短剧制作参考链接.md`
- `中英对照 AI 短剧手册.md`

## 5. 当前进展

- 已生成：`short_drama_production_resources_summary.md`
- 已生成：`short_drama_bilingual_resource_package.md`
- 已生成：`短剧制作流程概览.md`
- 已生成：`AI短剧Prompt模板资料包.md`
- 已补充：中英文资源目录与国内短剧制作落地要点
- 已下载本地资源：`short_drama_resources/clipcurator/`
- 仍可继续：生成单独中文手册、整理 prompt 模板、提取核心模板为中文落地表单

## 6. 已保存本地文件

以下已保存到 `short_drama_resources/clipcurator/`：

- ai-short-drama-production-workflows:
  - `README.md`
  - `README.zh-CN.md`
  - `docs/idea-to-concept.md`
  - `docs/worldbuilding-workflow.md`
  - `docs/character-system-design.md`
  - `docs/script-to-assets.md`
  - `docs/storyboard-to-video.md`
- vertical-drama-script-formats:
  - `README.md`
  - `README.zh-CN.md`
  - `templates/vertical-drama-script-template.md`
- ai-storyboard-prompts:
  - `README.md`
  - `README.zh-CN.md`
  - `prompts/zh-cn/character-design-prompts.md`
  - `prompts/zh-cn/scene-design-prompts.md`
  - `prompts/zh-cn/storyboard-prompts.md`
  - `prompts/zh-cn/camera-movement-prompts.md`
  - `templates/storyboard-shot-list-template.md`
- ai-character-continuity-kit:
  - `README.md`
  - `README.zh-CN.md`
  - `docs/character-bible-template.md`
  - `docs/visual-consistency-checklist.md`
  - `templates/character-card.md`
- ai-short-drama-storyboard-shot-packs:
  - `README.md`
