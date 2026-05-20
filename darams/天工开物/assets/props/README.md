# 道具参考图（PROP-*）

视频模型在 C 段常见两类错误，需用 prompt + 参考图约束：

1. **尺度漂移**：墙角远景锤小，贴身抄起锤变大。  
2. **角色绑错**：上一镜打手对白后，模型让**打手**去抄锤；剧本是**男主（宋知行）**抄锤挥向打手。

## PROP-001 · 精铁大锤

| 字段 | 说明 |
|------|------|
| 比例 | 锤头 ≈ **成年人头围**，木柄约 **齐腰**；禁止巨型战锤 |
| 文件 | `PROP-001-hammer.png`（建议白底或院落角落实拍感） |
| 用法 | `EP01_segments.yaml` 的 `prop_urls` + `content_roles` 作 `reference_image` |

### Seedream 出图 Prompt 示例

```
Single Chinese Ming dynasty blacksmith sledgehammer, square iron head about the size of an adult human head, wooden handle waist height, carved marks on handle, no person, studio white background, photorealistic, 8k, prop reference sheet
```

出图后写入本目录，重跑 `EP01-SEG05` 即可。

完整制片清单见 [`制片规范.md` §7.10](../../制片规范.md#710-道具转移与肢体动作防错清单)。
