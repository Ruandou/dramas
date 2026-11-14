# BytePlus 宣布 Dreamina Seedance 2.5 Flash，官方 API 将于 11-15 在 ModelArk 上线（并首次给出旗舰版 480p/720p/1080p 官方单价）

- 抓取时间：2026-11-12 14:40（Asia/Shanghai）
- 层：国外层
- 主体：BytePlus ModelArk（字节跳动企业云；与即梦短剧工作室不是同一产品窗）
- 过门：成本／产能 —— 官方公布更快、更便宜的迭代档，以及旗舰档官方单价；4K 官方 API 仍未开价。
- 信源等级：A 级（官方 X 长帖 + 同期更新的官方价目页 + 官方对照卡）；独立媒体核述未见，**待补第 2 信源**。
- 本地附件：`01_byteplus_seedance25_flash_对照卡.jpg`（官方线程配图）；`byteplus-model-pricing-excerpt.md`（官方价目页视频生成节摘录，源文件 Last-Modified: 2026-11-12 06:06:41 GMT）

## 官方原文要点（已打开）

### 1. BytePlus 官方 X 主帖全文（note_tweet，2026-11-12 06:09:32Z / 14:09 CST）

来源：https://x.com/BytePlusGlobal/status/2120760891344036304  
账号：@BytePlusGlobal（BytePlus）

> More ideas to try. Less time waiting. ⚡
>
> Introducing Dreamina Seedance 2.5 Flash: results close to flagship Seedance 2.5, with nearly twice the generation speed.
>
> For 720p text-to-video and image-to-video generation, pricing is USD 0.152 per second, approximately 34% lower than Seedance 2.5.
>
> The API will launch on BytePlus’s ModelArk platform on Sunday, November 15.
>
> Watch the video below.

同一线程后续官方说明（已打开）：

- 联系页（非价目正文）：https://www.byteplus.com/en/contact-us/ai-seedance2-5-official
- 参考输入与分辨率：https://x.com/BytePlusGlobal/status/2120760902236700929  
  “Use up to 10 images, 5 videos and 5 audio clips as references per request / Generate videos up to 30 seconds long / Create in 480p or 720p”
- 定位：面向频繁迭代与规模化内容，帮助团队在预算和周期内多试镜头。https://x.com/BytePlusGlobal/status/2120760904774201766

### 2. 官方对照卡（线程配图，已保存）

图中将 Flagship Model「Seedance 2.5」与 Cost-Effective Model「Seedance 2.5 Flash」并列，关键数字如下（按图面逐项抄录，未推算）：

| 项 | Seedance 2.5（旗舰） | Seedance 2.5 Flash |
|---|---|---|
| Resolution | 480p / 720p / 1080p / 4K | 480p / 720p（initial release） |
| Pricing（Text-to-Video / Image-to-Video） | 480p: $0.103/sec；720p: $0.231/sec；1080p: $0.569/sec；4K: API coming soon | 480p: $0.070/sec；720p: $0.152/sec |
| Draft Mode | Supported（Draft at 480p, then render at 1080p，4K coming soon） | Not supported |
| Reference Inputs | Up to 30 images, 10 videos, and 10 audio clips | Up to 10 images, 5 videos, and 5 audio clips |

720p：$0.152 ÷ $0.231 ≈ 34.2%，与主帖「approximately 34% lower」一致。

### 3. 官方价目页（与 X 帖几乎同时更新）

- 页面：https://docs.byteplus.com/en/docs/ModelArk/model-pricing  
- 可抓取的 Markdown：https://docs.byteplus.com/docs/en/modelark/model-pricing.md  
- HTTP Last-Modified：2026-11-12 06:06:41 GMT（14:06 CST），早于官方 X 主帖约 3 分钟。
- 文首计价单位：Token prices are **USD per million tokens**（除非另有说明）。
- 新模型 ID：`dreamina-seedance-2-5-flash-261115`（编号与 11-15 上线日一致）。旗舰仍为 `dreamina-seedance-2-5-260628`。
- Token 单价表（官方原表，480p and 720p 列）：
  - 无视频输入、在线推理：Flash $7.0 / 旗舰 $10.70；Flash 的 1080p、4K、离线推理均为 Not supported。旗舰 1080p 为 $11.7，4K 为 Not supported。
  - 有视频输入、在线推理：Flash $4.3 / 旗舰 $6.40；Flash 同样不支持 1080p/4K/离线。旗舰 1080p 为 $7.0，4K 为 Not supported。
- 计费示例（无视频输入、16:9、输出 5 秒）把 Flash 写成 480p $0.34/条（$0.07/秒）、720p $0.76/条（$0.15/秒）；旗舰为 480p $0.514/条（$0.103/秒）、720p $1.156/条（$0.231/秒）、1080p $2.843/条（$0.569/秒）。**对外海报/推文用三位小数 $0.070 与 $0.152；价目页示例对 Flash 做了四舍五入。写稿以推文+对照卡为准，并注明文档示例有圆整。**
- 有视频输入时，官方示例给出的是区间价（随参考视频时长 2–30 秒变化），不能把「无视频输入的每秒单价」直接套到带参考视频的请求上。
- Draft：价目页写明旗舰 Draft 按固定 480p 计 token，与常规 480p 同价；对照卡写明 Flash **不支持** Draft。
- 4K：对照卡写「API coming soon」；价目页 2.5 系列（含旗舰与 Flash）4K 列均为 Not supported。这与此前「10-27 企业试用、官方 4K 价未公布」一致，**不得写成 4K 已官方 GA**。

## 写稿必须写明

- API **将于 2026-11-15（周日）** 在 BytePlus ModelArk 上线，本条采集日（11-12）尚未可调用；不得写成「今天已经能用」。
- 这是 **ModelArk 官方 API 价目**，不是即梦短剧工作室（044）积分价，也不是 Krea / Picsart / Runway / Pika / Luma 等托管通道价。
- Flash 首发只有 480p/720p，无 1080p、无 4K、无 Draft；参考输入上限低于旗舰（10 图 / 5 视频 / 5 音频，对不上「最多 50 路参考」的旗舰口径）。
- 官方自称「效果接近旗舰、生成速度接近两倍」是营销表述，本轮未实测，不得写成已验证。
- LibTV 等第三方托管/转售页出现的「每秒 ¥0.10、最低 5 折」不是 BytePlus 官方价，不要混写进报价。
- 火山方舟／即梦国内官方是否同步上线 Flash，本轮未见对应公告，不得自行写成国内同步 GA。

## 来源链接

- https://x.com/BytePlusGlobal/status/2120760891344036304
- https://x.com/BytePlusGlobal/status/2120760902236700929
- https://docs.byteplus.com/en/docs/ModelArk/model-pricing
- https://docs.byteplus.com/docs/en/modelark/model-pricing.md
- https://www.byteplus.com/en/contact-us/ai-seedance2-5-official
