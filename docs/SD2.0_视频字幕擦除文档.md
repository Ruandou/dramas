# Seedance 2.0 视频字幕擦除文档

使用 Seedance 2.0 / Seedance 2.0 fast 模型生成的视频可能包含字幕，本文为您介绍如何通过 API 对视频进行字幕擦除。

字幕擦除为方舟平台提供的免费功能，暂不收费。

### 使用流程


#### 流程简介

字幕擦除任务接口是异步接口，流程如下：



#### 调用示例


video_url 即待擦除字幕的视频 URL，从方舟[查询视频生成任务 API](https%3A%2F%2Fwww.volcengine.com%2Fdocs%2F82379%2F1521309%3Flang%3Dzh)返回的`content.`**`video_url`** 字段获取。

注意：仅支持使用原始 URL，转存后无效。原始 URL 存在 24h 有效期，请及时处理。

---

成功后返回以下信息，复制 task_id 备用。

---


---

任务执行成功后，可通过`result.video_url` 获取擦除字幕后的视频链接。

---


### API参考

#### 发起字幕擦除任务

POST https://amk.cn-beijing.volces.com/api/v1/ark-tools/ark-erase-video-subtitle-pro

本接口用于提交一个异步的精细化字幕擦除任务。它利用 AI 算法针对视频字幕提供精细化检测与擦除功能，实现高质量无痕擦除效果，最大程度还原视频画面。

任务提交成功后，您需要保存返回的 task_id，并通过轮询查询任务信息接口获取最终结果。

#### 使用说明

```
```

```


```


#### 请求参数

#### Header 参数

> 参数
> 类型
> 是否必选
> 示例值
> 描述
> Authorization
> String
> 是
> Bearer {Your_API_Key}
> 格式为 Bearer {Your_API_Key}。方舟API Key

#### Body 参数

> 参数
> 类型
> 是否必选
> 示例值
> 描述
> video_url
> String
> 是
> "https://example.com/source.mp4"
> 待擦除字幕的视频 URL。
> ```
> ```

#### 响应参数

> 参数
> 类型
> 描述
> success
> Boolean
> 任务是否提交成功。
> ```
> ```
> ```
> ```
> task_id
> String
> 任务的唯一标识，用于后续查询任务进度和结果。
> request_id
> String
> 本次请求的唯一标识，可用于问题排查。

示例：

---


### 错误处理

当请求的参数或鉴权信息不正确时，任务将不会被创建，接口会返回一个同步的错误响应。详见[错误码](https%3A%2F%2Fwww.volcengine.com%2Fdocs%2F6448%2F2300662%3Flang%3Dzh)。示例如下：

---

## 查询字幕擦除任务结果

GET https://amk.cn-beijing.volces.com/api/v1/ark-tasks/{task_id}

### 请求参数

#### Path 参数

> 参数
> 类型
> 是否必选
> 示例值
> 描述
> task_id
> String
> 是
> amk-tool-ark-erase-video-subtitle-pro-14***24
> 任务的唯一标识。在提交异步任务时，从响应体中获取。

#### Header 参数

> 参数
> 类型
> 是否必选
> 示例值
> 描述
> Authorization
> String
> 是
> Bearer {Your_API_Key}
> 格式为 Bearer {Your_API_Key}。请参考基础概念及准备工作获取 API Key。

### 响应参数

接口的响应体为一个 JSON 对象，包含了任务的详细信息。

> 参数
> 类型
> 描述
> success
> Boolean
> 标识本次 API 请求是否被成功处理。
> ```
> ```
> ```
> ```
> 说明
> 此字段仅代表查询操作本身是否成功，不代表任务的执行状态。
> task_id
> String
> 所查询任务的唯一标识。
> task_type
> String
> 任务类型。例如 ark-erase-video-subtitle-pro（精细化字幕擦除）等。
> status
> String
> 任务当前的状态。枚举值：
> ```
> ```
> ```
> ```
> ```
> ```
> result
> Object
> **任务成功时**返回的结果对象。仅当 status 为 completed 时出现。其内容结构请参见下文Result 对象。
> error
> Object
> **任务失败时**返回的错误详情对象，或在任务成功时为 null。其内容结构请参见下文 Error 对象。
> expires_at
> String
> 任务结果的过期时间戳（Unix Time，单位：秒）。仅当任务成功且有结果时返回。
> created_at
> String
> 任务创建时间戳（Unix Time，单位：秒）。
> finished_at
> String
> 任务完成（成功或失败）的时间戳（Unix Time，单位：秒）。仅当 status 为 completed 或 failed 时出现。
> request_id
> String
> 本次 API 请求的唯一标识符，可用于问题排查。

#### Result 对象

当 status 为 completed 时，响应会包含 result 对象。

> **参数**
> **类型**
> **示例**
> **描述**
> video_url
> String
> "https://example.volcvideo.com/output.mp4?auth_key=..."
> 输出视频的 URL。有效期为 24 小时。

#### Error 对象

当 success 为 false 或 status 为 failed 时，会返回 error 对象，包含错误详情。

> 参数
> 类型
> 描述
> code
> String
> 错误码。详见[错误码](https%3A%2F%2Fwww.volcengine.com%2Fdocs%2F6448%2F2300662%3Flang%3Dzh)。
> message
> String
> 错误描述信息，用于展示或记录日志。
> param
> String
> (可选) 指示导致错误的具体参数名。
> type
> String
> 错误类型，如 TaskError 表示任务执行出错，ApiError 表示 API 调用出错。

### 响应示例

#### 示例 1：任务正在运行

---

#### 示例 2：任务运行成功

---

#### 示例 3：任务执行失败

---
