# Runway Kling 4.0 限时折扣（App 25% / Dev API 20%）

抓取时间：2026-11-03 19:36（Asia/Shanghai）
层：国外
过门：成本（短剧制作模型计价）

## 要点

- Runway 消费端（Standard / Pro / Max）：Kling 4.0 生成按 credits **少收 25%**，至 **2026-11-30**；定价页示例：5 秒 1080p 由 **118 → 89 credits**。
- Runway Dev API：`kling_4` **20% off through November 30, 2026 UTC**。无 input video 时：720p list 15.7 → promo **12.56** credits/sec；1080p list 23.5 → promo **18.8** credits/sec。有 input video：720p 7.52 / 1080p 11.28 credits/sec（list 9.4 / 14.1）。1 credit = $0.01。
- Docs 计费细节：先按 list 上取整，再打 20% 再上取整；例：5s 720p 无 input = **64 credits**。List 价自 **2026-12-01 UTC** 恢复。Kling 4.0 含音频、无音频开关；时长 3–30s；竖屏可用 `720:1280` / `1080:1920`。
- 对独立短剧制作方：若流水线走 Runway（App 或 Dev API）出可灵 4.0 镜头，11 月底前批次渲染可按上述比例压单镜成本；App 与 Dev 积分池不互通，须分开算。免费档未列 Kling 4.0。

## 来源

1. [Runway Pricing（消费端）](https://runway.com/pricing) — 「25% off Kling 4.0 generations until November 30」；5s 1080p 118→89 credits
2. [Runway Dev API Pricing](https://dev.runway.com/pricing) — Kling 4.0「20% off through November 30, 2026」及 720p/1080p promo 价
3. [Runway Dev docs · API Pricing](https://docs.dev.runwayml.com/guides/pricing/) — `kling_4` 折扣公式与 5s/720p=64 credits 例；注明 list 自 2026-12-01 UTC
4. [Kling 4.0 API 学习页](https://dev.runway.com/learn/kling-4-0-api) — 模型能力与（list）单价；页脚「Prices current as of November 3, 2026」
5. [PromoClock 对照](https://promoclock.co/en/deals/runway-kling-4-25-off-2026/) — 2026-10-27 起跟踪消费端 25%；2026-11-02 仍 live（第三方，作时间轴对照）

## 摘录备查

- App：Kling 4.0 1080p「118 credits/5s → 89 credits/5s · 25% off … until November 30」
- Dev pricing 表：720p List 15.7 / Promo 12.56；1080p List 23.5 / Promo 18.8；「20% off through November 30, 2026」
- Docs：`Through November 30, 2026 UTC, the list-price charge is rounded up, then discounted 20% and rounded up again — a 5 second 720p video without an input video is 64 credits. List prices apply from December 1, 2026 UTC.`

## 过门备注

≥2 独立官方面（runway.com/pricing + dev.runway.com/pricing/docs）；成本向；促销窗口至 11-30，写稿/拍片排期有截止日。PromoClock 显示消费端折扣约 10-27 已可核，本条首次入库双通道精确价；若只写「旧闻促销」可降权，但对制作方仍可执行至月底。
