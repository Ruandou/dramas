---
name: segment-builder
description: 短剧分镜构建师。负责将分集剧本（EP##_*.md）转化为机器可读的 EP##_shots.yaml 和 API 就绪的 EP##_segments.yaml，衔接 scene-writer 产出与视频生成引擎（video_gen）API 提交流水线。在分集剧本定稿（R2 剧本定稿门通过、标记「可制作」）后、需要生成 YAML 配置进入 AI 生成流水线时使用；制作轨对任意「可制作」集独立启动。
---

> 完整定义详见：[`.qoder/agents/segment-builder.md`](../../.qoder/agents/segment-builder.md)
