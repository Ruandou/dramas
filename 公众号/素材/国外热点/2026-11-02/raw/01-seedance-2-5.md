# Seedance 2.5 写实 AI 视频刷屏

- 抓取时间：2026-11-02 16:25（Asia/Shanghai）
- X 故事：https://x.com/i/trending/2116543202001838333 （updated_at ≈ 2026-11-01T10:48:43Z）
- 一手/官方：https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5 （2026-07-31）
- 产品页：https://seed.bytedance.com/en/seedance2_5
- 第三方接入说明：https://help.runwayml.com/hc/en-us/articles/53542207042323-Creating-with-Seedance-2-5
- 抓取说明：X trending 页为动态摘要（WebFetch 难取全文）；以下保存 X search_news 摘要 + Seed 官方博客可见全文摘录。

## X 故事摘要（search_news）

- 标题：Seedance 2.5 Delivers Stunningly Realistic AI Videos
- Hook：A young woman sips coffee, steam rising from intricate latte art, her eyes flickering with lifelike subtlety—all generated in one seamless clip.
- Summary：Seedance 2.5, launched by ByteDance’s Seed team in July 2026, creates up to 30 seconds of video with native audio from text prompts, images, video clips, or audio files. Examples range from boys in tall grass under clouds to a girl sprinting across a rooftop bridge, with smooth motion, realistic physics, and synced dialogue drawing praise for their cinematic quality. Users highlight the tool's precise control and consistency, fueling excitement about easier storytelling for short-form content and independent films.

## 官方博客摘录（ByteDance Seed，2026-07-31）

Today, we are officially launching Seedance 2.5, the new-generation video creation model… Seedance 2.5 centers on foundational generation and reference-based generation, delivering major breakthroughs in long-form storytelling, multimodal reference, and editing.

Key highlights include:

- Up to 30 seconds per generation, with multi-round extensions: high-quality 30-second audio-video clips in a single pass; multi-round extension for multi-minute content.
- Fully upgraded multimodal referencing: up to 30 images, 10 video clips, and 10 audio clips as references in a single pass.
- More precise and stable editing: timestamp-level control; green screen, camera perspective, reference-based editing.

Access (per blog): Jimeng AI, Doubao Pro; API via BytePlus ModelArk coming soon. Project homepage: https://seed.bytedance.com/seedance2_5

## Runway 接入规格摘录（第三方）

- Duration: 4s to 30s; inputs text/image/video/audio; up to 50 references (30 images, 10 videos, 10 audio).
- Resolutions: 480p / 720p / 1080p.
- Credit cost examples (Runway help): 1080p 68 credits/sec; 720p 30; 480p 20.
