# Pika H3 Flex 开源权重上线

- 抓取时间：2026-11-02 16:25（Asia/Shanghai）
- X 故事：https://x.com/i/trending/2116434831865520255 （updated_at ≈ 2026-10-31T19:11:40Z）
- 官方技术博客：https://pika.art/blog/pika-h3-flex-research （2026-10-29）
- Hugging Face：https://huggingface.co/Pika-Labs/Pika-H3-Flex
- 抓取说明：已打开 Pika 博客与 HF 模型卡；X 页保存 search_news 摘要。

## X 故事摘要（search_news）

- 标题：Pika Labs Launches Pika H3 Flex for Fast AI Video Creation
- Summary：Pika H3 Flex tops the open-weight text-to-video leaderboard on DesignArena, ranking #7 overall, and supports up to 4K resolutions with exportable audio stems like dialogue and SFX. Built on MiniMax H3, it distills to six sampling steps for faster-than-real-time performance, with open weights on Hugging Face and GitHub under a community license. Creators praise its precise edits, low costs starting at $0.01 per second, and ComfyUI integration for local runs.

## Pika 官方博客要点（2026-10-29）

- Post-trained on MiniMax H3; six-NFE omni-generator; ranks #1 among open-source T2V in their claim; real-time generation.
- Resolutions 480p–4K; five editable audio stems: dialogue, score, SFX, foley, ambience.
- Available via API, ComfyUI, Diffusers; weights on Hugging Face; code on GitHub.
- Pricing table (blog Table 1): Pika H3 Flex starting $0.01 / output-s; Seedance 2.5 listed at $0.103; MiniMax H3 $0.08.
- Training: SFT → PDMD distillation (50→6 steps) → ReFL + DPO adapters merged.

## Hugging Face 模型卡要点

- Native local: 480p/768p, 24fps, 5–15s, synchronized stereo audio; 1080p/2K/4K and stems via Pika API.
- Adapters: fl2va/ and ref2va/ FP32 LoRA rank/alpha 128; base MiniMax-H3 Diffusers components ~210 GB total.
- Ref2VA: up to 9 images, 3 videos, 3 audio, 12 refs total.
- License: MiniMax H3 Community License (Excluded Territories include EU, UK, Korea, US per LICENSE page).
