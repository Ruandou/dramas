## Investigation Report: High-Quality Resources for AI Short Drama (微短剧) Production

### Objective
Identify and evaluate resources covering short drama scriptwriting methodology, AI-assisted production pipelines, industry standards, communities, and academic/professional frameworks -- all aimed at iterating and optimizing AI short drama production agents.

---

## 1. Short Drama Scriptwriting Tutorials (微短剧编剧教程)

### 1.1 Red Fruit (红果) Official "Short Drama Screenwriting First Lesson" Series

**The single most authoritative and actionable resource found.** This is a 10-episode interview series produced by the Red Fruit Short Drama Creation Service Platform (字节跳动/ByteDance's free drama platform), featuring practitioners with multiple dramas earning 10M+ in revenue sharing.

| Episode | Title | URL |
|---------|-------|-----|
| 01 | New Entrant's Guide | https://www.juben.pro/a/9-1750.html |
| 02 | Genre & IP Selection Logic | https://www.juben.pro/a/1-1780.html |
| 03 | Golden Opening Design | https://www.juben.pro/a/1-1781.html |
| 04 | Main Plot Structure Logic | https://www.juben.pro/a/1-1782.html |
| 05 | Rhythm & Pacing Design Secrets | https://www.juben.pro/a/1-1783.html |
| 06 | Suspense & Hook Design Logic | https://www.juben.pro/a/1-1784.html |
| 07 | Emotional Beat Design Techniques | https://www.juben.pro/a/1-1785.html |
| 08 | Getting Scripts Approved & Produced | https://www.juben.pro/a/1-1787.html |
| 09 | Dialogue Polishing Methods | https://www.juben.pro/a/1-1788.html |
| 10 | Web Novel Author Transition Guide | https://www.juben.pro/a/2-1790.html |

**Key frameworks extracted from Episode 05 (Rhythm Design):**
- Three-phase macro rhythm: "Golden Window Period" (Ep 1-10) / "Stable Development" (Ep 11-30) / "Climax & Resolution" (Ep 31-80)
- Single-episode micro rhythm: First 30s (hook/stop the scroll) / Middle 60s (story advancement "dry content") / Last 30s (cliffhanger for next episode)
- Genre-specific pacing: Revenge = "fast, ruthless, precise"; Sweet romance = "tension-release cycles"; Slow-paced premium = "quality over speed but requires stronger writing skills"
- "3-5 episodes per minor climax, 10 episodes per major climax" rule

**Quality Assessment:** 9/10 -- First-party platform producing the content, featuring top-tier practitioners with proven track records (multiple dramas earning 10M+ RMB). Extremely specific to the 微短剧 format. Published Jan-Feb 2026. Directly actionable for training AI agents.

**Also available as podcast:** "短剧编剧第一课" on 小宇宙 (Xiaoyuzhou FM) -- https://www.xiaoyuzhoufm.com/episode/6969d8fcef1cf272a7b1b17b

---

### 1.2 Zhihu Guides & Structured How-Tos

| Resource | URL | Focus |
|----------|-----|-------|
| "How to Become a Short Drama Screenwriter in One Month" | https://zhuanlan.zhihu.com/p/1961206505077453233 | Weekly study plan: daily watch 10 dramas analyzing "golden 30-second hooks" and episode-end suspense |
| "From 0 to 1 Short Drama Screenwriter - Complete Guide" | https://zhuanlan.zhihu.com/p/4614310492 | Structured methodology covering vertical screen characteristics: fast rhythm, dense plot, multiple reversals, frequent "shuang" (satisfaction) points |
| CBNData "Short Drama Hit Formula Revealed" | https://www.cbndata.com/information/288845 | Three principles: visual stimulation, mindless plot, fast pacing. Two major formulas: male-audience war god, female-audience revenge |

**Quality Assessment:** 6-7/10 -- Useful for extracting audience-facing heuristics and "folk wisdom" from practitioners. Less rigorous than the Red Fruit series but broader coverage.

---

## 2. AI-Assisted Scriptwriting & Production Resources

### 2.1 GitHub: 0xsline/short-drama (AI Screenwriting Skill Pack)

- **URL:** https://github.com/0xsline/short-drama
- **Description:** A comprehensive AI skill package (pure Markdown rules, 9 files, ~93KB) designed as a plug-in for AI coding assistants (Claude Code, Codex CLI, Gemini CLI). Covers the entire short drama pipeline from topic selection to export.
- **Key components:**
  - 13 genre templates with rhythm curves
  - 5 hook types (suspense, reversal, emotional, information, crisis) with frequency distributions
  - 4-layer villain system (minor villain -> mid-boss -> big boss -> hidden villain)
  - Rhythm curve system: Rising (15%) -> Climbing (30%) -> Storm (35%) -> Final Battle (20%)
  - Paywall card-point design (10-15% of episodes)
  - 8-type "satisfaction matrix" for different genres
  - 5-dimension quality scoring system (rhythm, satisfaction, dialogue, format, continuity)
  - Built-in compliance checker (NRTA regulations)
  - 8 reference knowledge base files (genre-guide, opening-rules, rhythm-curve, hook-design, paywall-design, satisfaction-matrix, villain-design, compliance-checklist)
- **Why useful:** Directly applicable as reference rules or even competitor analysis for your own agent system. The structured knowledge base files could be used as training data or rule sets. MIT licensed.
- **Quality Assessment:** 8/10 -- Well-structured, comprehensive, directly machine-readable. Published 2025-2026.

---

### 2.2 Cnblogs: "Short Drama Script Creation" Skill by Peng Zixiao

- **URL:** https://www.cnblogs.com/VisionGo/p/19822785
- **Description:** A complete AI skill specification for short drama creation, even more detailed than the GitHub project above. Includes:
  - Complete macro structure (100-episode breakdown with percentage-based phase allocation)
  - Single-episode three-part formula (15s hook / 60-120s conflict / 15s cliffhanger)
  - Character archetype library (6 protagonist types, 5 supporting role functions)
  - 6 hook types with example dialogue
  - 5 reversal pattern templates
  - "Face-slap satisfaction" 4-step method (humiliation -> endurance -> counterattack -> release, with 40%/30%/30% time allocation)
  - Dialogue rules (max 30 characters per line, no filler)
  - Complete quality gates (per-episode and whole-series checklists)
  - Common trap diagnosis (rhythm traps, character traps, logic traps)
  - 8 companion files specification (genre guides, patterns library, production guide, templates, examples, CP chemistry, suspense chain, market trends)
- **Why useful:** This is essentially a complete "system prompt" for an AI drama agent. It can be directly compared against and merged into your existing agent prompts.
- **Quality Assessment:** 8/10 -- Extremely structured and machine-friendly. Published April 2026. Covers both methodology and execution format.

---

### 2.3 ViMax: Agentic Video Generation (HKU)

- **URL:** https://github.com/HKUDS/ViMax
- **Paper:** https://arxiv.org/html/2606.07649v1
- **Description:** A state-of-the-art multi-agent video framework from HKU that transforms raw ideas into complete video stories. Features:
  - Director, Screenwriter, Producer, and Video Generator roles
  - Idea2Video, Novel2Video, Script2Video, AutoCameo modes
  - RAG-based long script generation
  - Expressive storyboard design with cinematography language
  - Multi-camera filming simulation for spatial consistency
  - Intelligent reference image selection and consistency validation
  - End-to-end audio-video binding
- **Why useful:** Represents the academic state-of-the-art for multi-agent video generation. Architecture patterns (agent role decomposition, consistency checking, review loops) are directly applicable to your own pipeline design.
- **Quality Assessment:** 9/10 -- Academic paper with open-source code, from a top research university. Published June 2026.

---

### 2.4 "One Sentence, One Drama" (NTU Hierarchical Agent Framework)

- **URL:** https://hub.baai.ac.cn/view/55015
- **Paper:** https://arxiv.org/abs/2605.22144
- **Description:** A hierarchical agent framework from Nanyang Technological University. Key innovations:
  - Story generation via retrieval + multi-agent debate
  - Rhythm pattern library extracted from ~300 high-quality short dramas
  - Causal logic library for narrative unit assembly
  - 3D scene anchoring for cross-shot spatial consistency
  - Multi-stage review system throughout the pipeline
  - Post-production agent for transitions, BGM, and voice stitching
  - Purpose-built benchmark "Short-Drama-Bench" covering 7 genres, 17 sub-categories
  - 8 drama-specific evaluation metrics (opening/ending hooks, escalation, narrative coherence, spatial continuity, BGM/transition quality)
- **Why useful:** The most directly relevant academic work to your project. Their multi-agent debate for story generation, rhythm pattern library from real dramas, and drama-specific evaluation metrics could significantly improve your agents.
- **Quality Assessment:** 9/10 -- Cutting-edge research, May 2026. Outperforms commercial products like Toonflow.

---

### 2.5 Open-AI-Micro-Drama-Generator

- **URL:** https://github.com/Anil-matcha/Open-AI-Micro-Drama-Generator
- **Description:** Open-source multi-agent pipeline: screenwriter -> storyboard -> frames -> video. Turns ideas into complete micro-dramas.
- **Quality Assessment:** 7/10 -- Useful reference implementation, simpler than ViMax but more accessible.

---

### 2.6 StoryAgent (Multi-Agent Storytelling Video)

- **URL:** https://arxiv.org/abs/2411.04925
- **Description:** Multi-agent framework that decomposes customized storytelling video generation into subtasks assigned to specialized agents, mirroring professional production processes.
- **Quality Assessment:** 7/10 -- Published Nov 2024, slightly older but foundational for the field.

---

### 2.7 AI Short Drama Technical Stack (Blog Post)

- **URL:** https://www.cnblogs.com/ljbguanli/p/19929928
- **Description:** Practical end-to-end system architecture covering:
  - LLM fine-tuning with short drama corpus (hot scripts, hit dialogue)
  - Structured prompts with "golden 3 seconds", "strong conflict", "reversal" templates
  - Character consistency via LoRA/IP-Adapter (90%+ similarity)
  - Video generation with AnimateDiff/SVD/Runway Gen-2
  - Lip-sync with Wav2Lip
  - Tech stack: Vue3/React frontend, FastAPI backend, LangChain/Diffusers/FFmpeg AI layer, PostgreSQL+OSS storage
- **Quality Assessment:** 6/10 -- Good overview of tech stack options, less depth on individual components.

---

### 2.8 Commercial Platforms

| Platform | URL | Description |
|----------|-----|-------------|
| Alibaba Cloud Short Drama AI | https://www.aliyun.com/benefit/scene/playlet | Script, storyboard, video generation with Wan2.6 model |
| Alibaba "万镜一刻" | (via aliyun) | Full-chain: script parsing -> storyboard -> synthesis -> post-production |
| SkyReels (Kunlun) | Open-source model | First China vertical-drama video generation model, 33 micro-expressions, 400+ action combinations |
| Feishu DeepSeek Template | https://www.feishu.cn/template/deepseek-short-drama-script-generation | DeepSeek R1-based script generator on Feishu multitable |

---

## 3. Industry Best Practices & Standards

### 3.1 Regulatory Framework

| Document | URL | Key Points |
|----------|-----|------------|
| NRTA Micro-Drama Classification Update (2026) | https://www.nrta.gov.cn/art/2025/2/5/art_113_70148.html | New thresholds: 300M for "key" dramas, 100M for "standard" dramas (up from 100M/30M). "先备案后上线" (register before going online) enforcement |
| NRTA "Badass CEO" Genre Management Notice (Nov 2024) | (via PDF reports) | Guidance against negative tendencies in "霸总" genre |
| Shanghai AI Micro-Drama "沪8条" (2026) | Referenced in multiple sources | 8 policy measures for AI-assisted micro-drama production |

### 3.2 Industry Research Reports

| Report | URL | Focus |
|--------|-----|-------|
| 2025 China Micro-Drama Industry & Employment (PKU) | https://www.nsd.pku.edu.cn/docs/2026-02/48accc85b74f4939b8f4c4b612e610ec.pdf | Industry structure, regional distribution, 133.3M jobs created |
| 2024 China Micro-Drama Industry Research (iResearch) | https://pdf.dfcfw.com/pdf/H3_AP202407071637643449_1.pdf | Full industry chain analysis, user insights, business models |
| 2025 Micro-Drama Data Report (ADX) | https://pdf.dfcfw.com/pdf/H3_AP202601211818183880_1.pdf | Market heat values, platform comparisons |
| 2026 China Short Drama Overseas Market | https://pdf.dfcfw.com/pdf/H3_AP202604261821586569_1.pdf | ReelShort/DramaBox overseas dominance, market segmentation |

### 3.3 Academic Analysis

- **"竖屏微短剧的叙事策略与精品化路径"** (China Higher Education Film Association) -- https://www.ccava.cn/newsinfo/10777810.html
  - Analysis of vertical-screen narrative strategies and quality improvement paths
  - Male-frequency vs female-frequency drama differentiation
  
- **普罗普功能理论视角下出海微短剧的叙事研究** -- https://pdf.hanspub.org/jc_3041105.pdf
  - Applying Propp's narrative functions to overseas micro-dramas

**Quality Assessment:** 7-8/10 -- Authoritative government and academic sources providing market context and regulatory constraints your agents must respect.

---

## 4. Chinese Scriptwriting Communities & Resources

### 4.1 Platforms

| Platform | URL | Description |
|----------|-----|-------------|
| 华语剧本网 (juben.pro) | https://www.juben.pro/ | Premier Chinese script marketplace. Hosts Red Fruit tutorial series. Training courses, script marketplace, formatting tools |
| 万众编剧网 | https://www.wzbj1616.com/ | Professional script services platform with training, tools, resources |
| 剧本网 (juben98) | https://www.juben98.com/ | Script trading portal, active short drama section |
| 抖几句 (doujiju) | https://www.doujiju.com/ | Script creation/trading platform specializing in short video/drama scripts |
| 编剧帮 (on Douban) | https://m.douban.com/group/bianjubang/ | 1121-member group, active for AI drama scripts and hiring |

### 4.2 WeChat Public Accounts (微信公众号)

- **红果短剧创作服务平台** -- Source of the "短剧编剧第一课" series
- **编剧帮** -- Full AI filmmaking courses, script creation techniques
- **数英网 (digitaling.com)** -- "100+ Micro-Drama Hit Formulas" analysis: https://www.digitaling.com/articles/1290694.html

### 4.3 Courses & Structured Learning

| Resource | URL | Description |
|----------|-----|-------------|
| 华语剧本网 编剧培训班 | https://www.juben.pro/edu/ | Zero-foundation screenwriting training |
| 上海开放大学 AI短视频创作速成班 (2026) | https://www.shou.org.cn/2026/0610/c10021a154706/page.htm | Formal university program on AI short video creation |
| 中国传媒大学《影视编剧教程》 | Referenced at sinobook.com.cn | New textbook covering micro-dramas, interactive dramas, new media narratives |
| 中国传媒大学 "影像叙事语言" MOOC | https://www.icourse163.org/learn/CUC-1461815176 | Visual narrative language fundamentals |

---

## 5. Academic & Professional Frameworks

### 5.1 Adapted Three-Act Structure for Micro-Dramas

From the collected resources, the industry has evolved the classic three-act structure into several micro-drama specific frameworks:

**A) Red Fruit 3-Phase Model (80-100 episodes):**
- Window Period (Ep 1-10): Hook audience, establish core premise
- Development Period (Ep 11-30): Deepen relationships, escalate conflicts
- Climax-Resolution (Ep 31-80): Dense climaxes, resolution of all threads

**B) VisionGo 6-Phase Model (60-100 episodes):**
- Opening (Ep 1-10): Setup + first major reversal by Ep 3
- Warming (Ep 11-30): Escalation, side characters enter, 5-ep mini-climaxes
- Climax (Ep 31-50): Core conflict eruption, identity reveals
- Turning (Ep 51-70): Major reversals, villain exposure
- Sprint (Ep 71-85): Final confrontation, all threads converge
- Ending (Ep 86-100): Resolution of all storylines

**C) 0xsline 4-Segment Rhythm Curve:**
- Rising (15%): Setup and initial hook
- Climbing (30%): Escalation
- Storm (35%): Peak conflicts
- Final Battle (20%): Resolution

### 5.2 "Save the Cat" Adaptation

While no published Chinese-language adaptation specifically for micro-dramas was found, the structural elements have been absorbed into Chinese practice:
- "黄金30秒" (Golden 30 Seconds) = Opening Image + Theme Stated (compressed)
- "付费卡点" (Paywall Card Points) at ~10-15% of episodes = "Break into Two" equivalent
- "每10集一个大高潮" = Act break equivalent at micro scale

### 5.3 Patent: Multi-Agent Micro-Drama Automated Generation

- **Patent:** CN119383413A
- **URL:** https://patents.google.com/patent/CN119383413A/zh
- **Description:** Formal invention patent for automated micro-drama generation using multiple specialized AI agents, covering story generation, storyboard design, audio-visual synthesis, and final composition.
- **Why useful:** Provides formal system architecture claims that can inform your own pipeline design without infringement concerns (patent describes the problem space and solution approaches).

---

## 6. Prioritized Recommendations for AI Agent Improvement

### Tier 1: Immediate Integration (highest impact)

1. **Red Fruit "短剧编剧第一课" series** -- Extract structured rules for each topic (pacing, hooks, emotion, dialogue) and encode them into your agent system prompts. These represent validated industry best practices from top-earning creators.

2. **0xsline/short-drama GitHub knowledge base** -- The 8 reference files (genre-guide, opening-rules, rhythm-curve, hook-design, etc.) are ready-made rule sets in Markdown that could supplement your `.cursor/rules/` or `.github/prompts/` files.

3. **NTU "One Sentence, One Drama" framework** -- Their rhythm pattern library extracted from 300 real dramas and drama-specific evaluation metrics (8 dimensions) could directly improve your quality gates.

### Tier 2: Architecture Improvement

4. **ViMax architecture** -- Study their multi-agent role decomposition (Director, Screenwriter, Producer, Generator) and review/consistency loops for inspiration on improving your existing agent pipeline.

5. **VisionGo/Peng Zixiao skill spec** -- The quality gates, common trap diagnosis, and companion file specifications are immediately applicable to your `story-architect.prompt.md` and `script-reviewer.prompt.md`.

### Tier 3: Knowledge Base Enrichment

6. **Industry reports (PKU 2025, iResearch 2024)** -- For market context, genre trending data, and audience behavior insights to feed into production planning decisions.

7. **NRTA regulations** -- Ensure your compliance checking reflects the latest 2025-2026 classification thresholds and content requirements.

---

## Risks & Caveats

1. **Rapid evolution**: The micro-drama industry changes quarterly. Resources from early 2024 may already be outdated regarding platform requirements and trending genres.

2. **Platform-specific rules**: Red Fruit, Douyin, Kuaishou, and WeChat mini-programs each have different content guidelines, formatting requirements, and revenue models. The research above is heavily Red Fruit-centric.

3. **AI regulation**: The June 2026 "沪8条" and NRTA's "先备案后上线" requirement for AI-generated dramas means your production pipeline must incorporate compliance checking as a hard gate.

4. **Academic vs. practical gap**: While ViMax and "One Sentence, One Drama" represent cutting-edge research, their cost ($25-27/minute) and generation time (74-90 min per 10-min drama) may not align with production economics at scale.

5. **Chinese-language bias**: Most resources are optimized for Chinese-language content on Chinese platforms. The overseas track (ReelShort, DramaBox) has different narrative conventions that would require separate research.
