# Kling AI API 调用参数参考

## 模型模式

| 参数 | 值 | 说明 |
|------|-----|------|
| `model_mode` | `std` | 标准模式 |
| `kling_version` | `3.0-omni` | Kling 3.0 Omni 模型 |

## 基础参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `duration` | `5` | 视频时长（秒） |
| `aspect_ratio` | `9:16` | 竖屏比例 |
| `imageCount` | `1` | 图片数量 |

## 提示词

| 参数 | 值 |
|------|-----|
| `prompt` | 主体1送外卖是，骂道：他妈的这么远，时间又少，快超时了。 |
| `rich_prompt` | <<<object_1>>>送外卖是，骂道：他妈的这么远，时间又少，快超时了。 |

## 其他参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `enable_audio` | `true` | 启用音频 |
| `prefer_multi_shots` | `true` | 偏好多镜头 |
| `customize_multi_shots` | `false` | 自定义多镜头关闭 |
| `showPrice` | `3600` | 价格（积分） |
| `offerType` | `3` | 套餐类型 |

## 完整原始 JSON

```json
{
  "type": "m2v_omni_video",
  "inputs": [
    {
      "name": "object_1",
      "inputType": "URL",
      "resourceType": "ELEMENT",
      "url": "https://p4-fdl.klingai.com/bs2/upload-ylab-stunt/kling/element/暴躁小孩-主要参考.jpeg?...",
      "cover": "https://p4-fdl.klingai.com/bs2/upload-ylab-stunt/kling/element/暴躁小孩-主要参考.jpeg?...",
      "elementVersion": 0
    }
  ],
  "arguments": [
    {"name": "skill", "value": ""},
    {"name": "biz", "value": "klingai"},
    {"name": "kling_version", "value": "3.0-omni"},
    {"name": "model_mode", "value": "std"},
    {"name": "duration", "value": "5"},
    {"name": "aspect_ratio", "value": "9:16"},
    {"name": "imageCount", "value": "1"},
    {"name": "customize_multi_shots", "value": "false"},
    {"name": "prefer_multi_shots", "value": "true"},
    {"name": "prompt", "value": "主体1送外卖是，骂道：他妈的这么远，时间又少，快超时了。"},
    {"name": "rich_prompt", "value": "<<<object_1>>>送外卖是，骂道：他妈的这么远，时间又少，快超时了。"},
    {"name": "enable_audio", "value": "true"},
    {"name": "omniRecognition", "value": "..."},
    {"name": "creationEntrance", "value": "base"},
    {"name": "showPrice", "value": "3600"},
    {"name": "offerType", "value": "3"}
  ],
  "scene": "NORMAL_CREATION"
}
```
