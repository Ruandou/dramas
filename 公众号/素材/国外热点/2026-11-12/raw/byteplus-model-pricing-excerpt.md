Features and unit prices vary with model services. This topic introduces the billing formulas and unit prices for each model to help you check and compare model prices.

> **Tip**

> To learn about the billing method and detailed billing rules, see [Model service billing](https://ai.byteplus.com/ark/region:ap-southeast-1/docs/model-service-pricing).

> **Pricing notes**

* > Unless otherwise specified, prices use the following units:

   * > Token prices are **USD per million tokens**. Cache\-storage prices are **USD per million tokens per hour**.

   * > Image generation prices are **per image**.

   * > 3D generation prices are **per call**.

* > The peak and off\-peak hours for DeepSeek V4.1 Flash series models are as follows:

   * > **Peak hours**: (UTC+8) Monday to Friday, 09:00\-12:00 and 14:00\-18:00.


……（中略：大语言模型等与本条无关的价目）……

## Video generation models

### Pricing

> **Tip**

> Video pricing is determined by both the **token rate** and **token consumption**. Under otherwise identical conditions:

* > A video generated at a higher resolution costs more than one generated at a lower resolution.

* > A video generated with video input costs more than one generated without video input.

> You can use the [Seedance 2.0 Series Pricing Calculator](https://bytedance.larkoffice.com/share/base/form/shrcnIHSU1yg0GtzCX4pyW3g3yb) and [Seedance 2.5 Series Pricing Calculator](https://bytedance.larkoffice.com/share/base/form/shrcnIYBa28VajWRTpAPEwR4icf) to estimate the cost of each video.

**Input without video**

|Model |Online inference |||Offline inference |
|---|---|---|---|---|
| |480p and 720p |1080p |4K | |
|dreamina\-seedance\-2\-5\-flash\-261115 |$7.0 |Not supported |Not supported |Not supported |
|dreamina\-seedance\-2\-5\-260628 |$10.70 |$11.7 |Not supported |Not supported |
|dreamina\-seedance\-2\-0\-260128 |$7.0 |$7.7 |$4.0 |Not supported |
|dreamina\-seedance\-2\-0\-fast\-260128 |$5.6 |Not supported |Not supported |Not supported |
|dreamina\-seedance\-2\-0\-mini\-260615 |$3.5 |Not supported |Not supported |Not supported |
|seedance\-1\-0\-pro\-250528 |$2.5 |||$1.25 |
|seedance\-1\-0\-pro\-fast\-251015 |$1 |||$0.5 |

**Input with video**

|Model |Online inference |||Offline inference |
|---|---|---|---|---|
| |480p and 720p |1080p |4K | |
|dreamina\-seedance\-2\-5\-flash\-261115 |$4.3 |Not supported |Not supported |Not supported |
|dreamina\-seedance\-2\-5\-260628 |$6.40 |$7.0 |Not supported |Not supported |
|dreamina\-seedance\-2\-0\-260128 |$4.3 |$4.7 |$2.4 |Not supported |
|dreamina\-seedance\-2\-0\-fast\-260128 |$3.3 |Not supported |Not supported |Not supported |
|dreamina\-seedance\-2\-0\-mini\-260615 |$2.1 |Not supported |Not supported |Not supported |

### Billing rules

* You are only charged for successfully generated videos. No fee is charged if generation fails due to reasons such as content moderation.

* **Estimated video price:**  `Token unit price × token consumption`

* **Estimated token consumption:**  `(Input video duration + output video duration) × output video width × output video height × output video frame rate / 1024`

* Some models support Draft mode:

   * Dreamina Seedance 2.5 generates Draft videos at a fixed 480p resolution. The token consumption and token rate are the same as normal 480p videos.

   * Seedance 1.5 Pro uses the following formula: `Draft video token consumption = Estimated normal video token consumption × conversion factor`. The conversion factor is 0.7 for silent videos and 0.6 for videos with audio.

* Token consumption values are estimates. Actual consumption is determined by `usage.completion_tokens` in the API response.

> **Minimum token consumption**

> For the Dreamina Seedance 2.0 series and Dreamina Seedance 2.5 series, minimum token consumption applies when the input includes video:

* > If estimated token consumption is below the minimum, the video is billed at the minimum token consumption.

* > The minimum depends on resolution, aspect ratio, and output duration. Check the [Dreamina Seedance 2.0 series minimum token consumption table](https://bytedance.larkoffice.com/wiki/H0fUwHPxtiHayOk6CVpcZzKqnHJ?table=tblnV1KjhYJO12Zh&view=vewWPcN5zJ) or [Dreamina Seedance 2.5 minimum token consumption table](https://bytedance.larkoffice.com/wiki/H0fUwHPxtiHayOk6CVpcZzKqnHJ?table=tblTUnmKaxBSqpU7&view=vewpCgsiHf).

### Billing examples

The following estimated prices illustrate typical input and output specifications.

#### Dreamina Seedance 2.5 series

**Input without video**

|Resolution |480p |720p |1080p |
|---|---|---|---|
|Aspect ratio |16:9 |16:9 |16:9 |
|Output video duration (seconds) |5 |5 |5 |
|Dreamina Seedance 2.5 |* $0.514 per video<br><br>* $0.103 per second |* $1.156 per video<br><br>* $0.231 per second |* $2.843 per video<br><br>* $0.569 per second |
|Dreamina Seedance 2.5 Flash |* $0.34 per video<br><br>* $0.07 per second |* $0.76 per video<br><br>* $0.15 per second |Not supported |

**Input with video**

|Resolution |480p |720p |1080p |
|---|---|---|---|
|Aspect ratio |16:9 |16:9 |16:9 |
|Input duration (seconds) |2\-30 |2\-30 |2\-30 |
|Output duration (seconds) |5 |5 |5 |
|Dreamina Seedance 2.5 |$0.553\-$2.152<br><br><br>* Lowest price: 2\-4 seconds input<br><br>* Highest price: 30 seconds input |$1.244\-$4.838<br><br><br>* Lowest price: 2\-4 seconds input<br><br>* Highest price: 30 seconds input |$3.062\-$11.907<br><br><br>* Lowest price: 2\-4 seconds input<br><br>* Highest price: 30 seconds input |
|Dreamina Seedance 2.5 Flash |$0.37\-$1.45<br><br><br>* Lowest price: 2\-4 seconds input<br><br>* Highest price: 30 seconds input |$0.84\-$3.25<br><br><br>* Lowest price: 2\-4 seconds input<br><br>* Highest price: 30 seconds input |Not supported |
