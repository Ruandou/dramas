# AI 短剧制作资源总结（中英文资料）

## 目的

这个文档同时整理中英文参考资料，帮助你把“AI 短剧制作”从流程框架、脚本/分镜规范、视觉 prompt、人物连续性、到国内落地实践，形成一个可直接落地的资料包。

## 1. 英文资源：生产流程与模板库

### 1.1 clipcurator/ai-short-drama-production-workflows
- 链接：https://github.com/clipcurator/ai-short-drama-production-workflows
- 核心价值：把 AI 短剧制作视为一个完整流水线，而不是单次 text-to-video。
- 关键内容：
  - Workflow 阶段：Idea → Concept → Worldbuilding → Character system → Outline → Script → Visual assets → Storyboard → Camera movement → Short drama video
  - Guides：Idea to Concept、Worldbuilding Workflow、Character System Design、Script to Assets、Storyboard to Video
  - Templates：Short Drama Project Bible、Episode Planning Template
- 适用场景：建立项目级别的制作流程、统一团队协作、标准化角色与镜头输出。

### 1.2 clipcurator/vertical-drama-script-formats
- 链接：https://github.com/clipcurator/vertical-drama-script-formats
- 核心价值：竖屏短剧脚本的标准结构与写作格式。
- 关键内容：
  - 竖屏剧集结构：Cold hook、Setup、Escalation、Turn、Cliffhanger
  - 脚本格式字段：Episode number、Scene number、Location/time、Character list、Visual beat、Dialogue、Camera note、Continuity note、Next-episode hook
  - 模板与 schema：Episode Structure Guide、Hook and Cliffhanger Patterns、Vertical Drama Script Template、Script Format Schema
  - 说明：此仓库有中文 companion README（README.zh-CN.md），适合中英文团队同时参考。
- 适用场景：在进入 storyboard 之前，先把剧本写成可落地的生产输入。

### 1.3 clipcurator/ai-storyboard-prompts
- 链接：https://github.com/clipcurator/ai-storyboard-prompts
- 核心价值：分镜 prompt 体系，覆盖角色、场景、分镜、镜头运动四个层面。
- 关键内容：
  - Prompt packs：Character design prompts、Scene design prompts、Storyboard prompts、Camera movement prompts
  - Bilingual support：English / 简体中文 prompts
  - 模板：Storyboard Shot List Template
- 适用场景：从剧本转到画面描述时，把“故事意图 + 角色关系 + 画面语言”统一表达给 AI。

### 1.4 clipcurator/ai-character-continuity-kit
- 链接：https://github.com/clipcurator/ai-character-continuity-kit
- 核心价值：解决 AI 生成中最常见的“角色漂移”与“性格不一致”问题。
- 关键内容：
  - 连续性维度：Identity、Visual design、Personality、Relationship map、Episode memory
  - 流程：先做角色 bible，再做视觉锚点，再复审 storyboard/scene
  - 模板：Character Bible Template、Visual Consistency Checklist、Character Card、Continuity Dimensions Schema
  - 说明：该仓库同样有中文 companion README（README.zh-CN.md）。
- 适用场景：所有需要多集、多镜头、多场景角色一致性的短剧项目。

### 1.5 clipcurator/ai-short-drama-storyboard-shot-packs
- 链接：https://github.com/clipcurator/ai-short-drama-storyboard-shot-packs
- 核心价值：把分镜转成可执行的“镜头包”模板，包含项目级复用要素。
- 关键内容：
  - Shot Pack 类型：Cold-open tension、Dialogue power shift、Reveal and reaction、Romance close-up、Cliffhanger ending
  - 结构字段：Scene objective、Frame composition、Character emotion、Camera movement、Continuity risk、Generation prompt
  - Review checklist：Vertical-safe framing、Character continuity、Readable emotion、Clear object focus、Episode continuity
- 适用场景：当你需要把单个场景的分镜方案交给 AI 或后端制作时。

## 2. 中文资源：国内短剧制作与 AI 视觉落地参考

### 2.1 已抓取的中文实践参考链接
- CSDN: https://blog.csdn.net/weixin_42715724/article/details/161287568
  - 标题：中文短剧制作全流程详解
  - 内容方向：短剧制作的“剧本先行、分镜明确、角色统一、素材稳定、剪辑流畅”思想。
- 百度 B2B Wiki: https://b2bwiki.baidu.com/article/6941651387799977
  - 主题：短剧写作结构与三幕式设计。
- 知乎专栏：https://zhuanlan.zhihu.com/p/2019012486096003434
  - 主题：分镜设计与视觉节奏，适合从剧本过渡到画面规划。
- ArcLoop 中文手册：https://arcloop.ai/handbook/zh-CN/ai-drama-production-hub
  - 主题：AI 短剧制作的落地工具与流程指南，偏向中国市场的视觉 AI 工具实践。

### 2.2 国内短剧制作要点（从搜索结果中提炼）
- 先明确创意点：3-5 个强冲突场景，主打生活化故事或商业悬念。
- 采用三幕式结构：第一幕建立关系（20%）、第二幕展开冲突（60%）、第三幕反转/钩子（20%）。
- 每集拆成小冲突：每集解决一个小问题，并留下下集悬念。
- 角色具体化：年龄、外形、服装、性格、声音、关系状态要明确。
- 分镜要素：场景、光线、角色动作、镜头语言（近中远景、角度）、时长控制。
- 生成素材前要先准备角色图、场景图、道具图，并做好多镜头一致性。
- 剪辑与合成要控制节奏：前3秒钩子、中段紧促、结尾悬念；AI 配音+BGM 要与节奏匹配。
- 必须加字幕，适应无声观看。

## 3. 本地仓库内部资料（推荐作为中文落地参考）

### 3.1 文档类
- `docs/SD2.0_漫剧提示词指南.md`
- `docs/SD2.0_影视制作提示词指南.md`
- `docs/references/platform-review-gate.md`
- `docs/制片规范模板.md`
- `docs/AI_MediaKit_画质增强工具.md`
- `docs/AI_MediaKit_视频工具.md`
- `docs/SD2.0_短剧出海翻译配音解决方案.md`
- `docs/SD2.0_人物站位问题最优实践.md`
- `docs/SD2.0_视频字幕擦除文档.md`

### 3.2 脚本与流水线脚本
- `script/pipeline_episode.py`：单集流水线自动化
- `script/local_pipeline.py`：本地拼接与素材合成流程
- `script/download_jimeng_from_tasks.py`：从即梦任务下载视频素材
- `script/tts_batch_edge.py`：AI 语音批量合成
- `script/gen_srt_from_clips.py`：视频字幕/字幕轨生成

### 3.3 项目示例目录
- `dramas/错嫁后我改写了王朝/`：已存在短剧项目结构，适合参考真实生产目录布局
- `dramas/天工开物/`：另一个项目案例，可对比角色/场景/素材分区

## 4. 中英资料补充建议

### 4.1 立即可落地的操作
- 下载这五个英文 repo 的 README、模板、prompt pack，并存成本地 Markdown。
- 把 `vertical-drama-script-formats` 与 `ai-storyboard-prompts` 的中文 companion README 一起保存，做双语参考。
- 先用 `Short Drama Project Bible` + `Episode Planning Template` 建立项目页，再把国内“剧本先行+分镜要点”加入中文说明。

### 4.2 最值得补全的中文资料
- 国内短剧“剧本创作+分镜设计”实战文章，尤其是“钩子+悬念”写法
- AI 视觉生成相关工具操作文档，如 Seedance、即梦、灵绘AI、Ark、LumenLine 对应用法
- 国内角色一致性与多镜头 prompt 实践（用中文提示词/中文模板读本）

### 4.3 推荐输出形式
- 生成一个“中文短剧制作手册”：模块包括创意、人物、剧本、分镜、视觉资产、生成与剪辑
- 另外生成一个“英文学术/模板库清单”：重点是 workflow repo、prompt pack、character continuity
- 最后生成一个“中英对照落地指南”：把同一阶段的英文模板与中文实践链接对齐，方便两种资料一起用。

## 5. 结论

你现在有：
- 一套英文 production workflow repo（5 个核心仓库）
- 一套中文落地参考链接与写作/分镜要点
- 本地仓库内的中文术语文档和实际短剧项目结构
- 本次生成的中文落地文档：`短剧制作流程概览.md`、`AI短剧Prompt模板资料包.md`

下一步建议：
1. 保存这份“中英文资料包”为基础索引
2. 直接下载 repo 里的 `README`、模板、prompt packs、中文 companion README
3. 结合本地 `docs/` 文档，整理一份“中文 AI 短剧制作落地指南”
4. 需要时我可以继续把内容拆成：
   - `短剧制作流程概览.md`
   - `AI 短剧 prompt 模板汇总.md`
   - `国内短剧制作参考链接.md`
