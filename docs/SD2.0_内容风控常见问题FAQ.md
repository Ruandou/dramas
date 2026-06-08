# Seedance 2.0 内容风控常见问题 FAQ

## 🔥 SD2.0专题

#### **Seedance 2.0 审核什么**

> 审核策略
> 类型
> 国内
> 海外
> 通用内容安全
> 审核策略
> ```
> ```
> ```
> ```
> 审核位置
> ```
> ```
> ```
> ```
> 版权
> 【sd2.0新增策略】
> 审核策略
> ```
> 
> 
> ```
> ```
> ```
> 审核位置
> ```
> ```
> ```
> ```
> ```
> ```
> ```
> ```
> 人脸
> 【sd2.0新增策略】
> 审核策略
> ```
> 
> ```
> 审核位置
> 输入图片、视频

#### 被审核命中的表现

在模型推理和自定义素材库均可根据[错误码](https%3A%2F%2Fwww.volcengine.com%2Fdocs%2F82379%2F1299023%3Flang%3Dzh)来对应命中的审核策略

```


```

```

```

#### 命中审核怎么办

```


```

```


```

```


```

```

```

#### 为什么输入没问题，输出还会命中版权

模型推理过程中，可能会自我发挥，拟合到明星脸，因此导致输出被审核拦截

#### 为什么上传到私域素材库的素材，输出端还是会被拦截

在审核机制上，私域素材库只豁免输入端审核，输出端不豁免。被拦截会有两种情况：



#### 为什么即梦输入放过真人/没拦截版权

版权上，集团合规要求是一致的，经过多次内部沟通确认，即梦没有与方舟不一致的策略。

#### 总结：为客户建立安全创作的环境【应用场景看这里】


#### 方舟内容风控拦截哪些内容

```


[小部分走协议可下]**涉敏**：领导人、国旗国徽、敏感地标（天安门等）
[不能下]**违禁**：毒品
[可走协议下]**涉黄**：色情、低俗
[可走协议下]**引人不适**：自残、血腥
[不能下]**版权**： 如奥特曼等IP生图生视频
```

#### 为什么方舟拦截了但是即梦/豆包等没有


```
```

```
```


#### 能否调整默认策略或自定义策略

不支持，方舟提供的服务为合规底线服务，不支持用户自定义

#### 方舟调整风控策略的原因和目的

```


```

```

```

#### 模型在安全围栏都做了哪些事

可公开对外版本：

豆包大模型生成的内容依照法律法规的要求，对于违规内容严格管控。通过在准入阶段安全机制、模型生成阶段以及用户输入输出文本展示阶段进行建立安全机制，包括利用智能文本检测引擎，接入多种风险模型，对用户输入和输出文本进行风险识别，在生成阶段引入高质量标注数据进行安全对齐训练，采用红蓝对抗等方式保证生成阶段模型价值观得到正确引导。

### 误伤漏杀

#### 什么是误伤

```
```

```
```

#### 为什么会产生误伤，误伤了怎么办？

```
```

#### 为什么会拦截一些看起来无风险的内容，例如正常的天安门、中国地图

**为保风险召回率，目前对于高危地标和旗帜无正负向差别拦截**

地图则由于生成存在行业普遍问题，不一定遵循客观事实，所以风控会拦截中国地图

#### 为什么会产生漏杀，漏杀了怎么办？

```
```

```
```

```


```

#### **生图/生视频模型，高危版权拦截的原因和对客沟通建议**

```
```

```
```

## 使用问题

#### 是否有错误区分是什么原因命中审核？

暂无，由于合规要求不能对外暴露详细拦截原因

#### 被风控命中的内容是否收费

不收费

#### 被风控命中长什么样

finish_reason="content_filter"

错误码如下：

> HTTP
> 状态码
> 错误类型
> Type
> 错误码
> Code
> 错误信息
> Message
> 含义
> 400
> BadRequest
> SensitiveContentDetected
> The request failed because the input text may contain sensitive information.
> 输入文本可能包含敏感信息，请您使用其他 prompt。
> 400
> BadRequest
> SensitiveContentDetected.SevereViolation
> The request failed because the input text may contain severe violation information.
> 输入文本可能包含严重违规相关信息，请您使用其他 prompt
> 400
> BadRequest
> SensitiveContentDetected.Violence
> The request failed because the input text may contain violence information.
> 输入文本可能包含激进行为相关信息，请您使用其他 prompt
> 400
> BadRequest
> InputTextSensitiveContentDetected
> The request failed because the input text may contain sensitive information.Request ID:
> 输入文本可能包含敏感信息，请您更换后重试。
> 400
> BadRequest
> InputImageSensitiveContentDetected
> The request failed because the input image may contain sensitive information.Request ID:
> 输入图像可能包含敏感信息，请您更换后重试。
> 400
> BadRequest
> InputVideoSensitiveContentDetected
> The request failed because the input video may contain sensitive information.
> 输入视频可能包含敏感信息，请您更换后重试。
> 400
> BadRequest
> InputAudioSensitiveContentDetected
> The request failed because the input audio may contain sensitive information.Request ID:
> 输入音频可能包含敏感信息，请您更换后重试
> 400
> BadRequest
> OutputTextSensitiveContentDetected
> The request failed because the output may contain sensitive information.
> 生成的文字可能包含敏感信息，请您更换输入内容后重试
> 400
> BadRequest
> OutputImageSensitiveContentDetected
> The request failed because the output image may contain sensitive information.
> 生成的图像可能包含敏感信息，请您更换输入内容后重试。
> 400
> BadRequest
> OutputVideoSensitiveContentDetected
> The request failed because the output video may contain sensitive information.Request ID:
> 生成的视频可能包含敏感信息，请您更换输入内容后重试。
> 400
> BadRequest
> OutputAudioSensitiveContentDetected
> The request failed because the output audio may contain sensitive information.Request ID:
> 生成的音频可能包含敏感信息，请您更换输入内容后重试。
> 400
> BadRequest
> InputTextSensitiveContentDetected.PolicyViolation
> The request failed because the input text may violate platform rules.Request ID:
> 输入文本可能违反平台规定，请您更换后重试。
> 400
> BadRequest
> InputImageSensitiveContentDetected.PolicyViolation
> The request failed because the input image may violate platform rules.Request ID:
> 输入图片可能违反平台规定，请您更换后重试。
> 400
> BadRequest
> InputVideoSensitiveContentDetected.PolicyViolation
> The request failed because the input video may violate platform rules.Request ID:
> 输入视频可能违反平台规定，请您更换后重试。
> 400
> BadRequest
> InputAudioSensitiveContentDetected.PolicyViolation
> The request failed because the input audio may violate platform rules.Request ID:
> 输入音频可能违反平台规定，请您更换后重试。
> 400
> BadRequest
> InputImageSensitiveContentDetected.PrivacyInformation
> The request failed because the input image may contain real person.Request ID:
> 输入图片可能包含真人，请您更换后重试。
> 400
> BadRequest
> InputVideoSensitiveContentDetected.PrivacyInformation
> The request failed because the input video may contain real person.Request ID:
> 输入视频可能包含真人，请您更换后重试。
