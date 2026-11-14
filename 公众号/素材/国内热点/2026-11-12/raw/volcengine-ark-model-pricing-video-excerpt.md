# 视频生成模型

> **价格说明**

> 视频价格由 **token 单价** 和 **token 用量** 共同决定。一般来说同等条件下：

* > 高分辨率的单条视频价格 \\> 低分辨率

* > 含输入视频的单条视频价格 \\> 不含输入视频

> 每条视频的价格可使用 [Seedance 2.0 系列价格计算器](https://bytedance.larkoffice.com/share/base/form/shrcnP1Bl0mqCP9OHCbjpe1oBkf) 、[Seedance 2.5 系列价格计算器](https://bytedance.larkoffice.com/share/base/form/shrcnhVCMxKxcwW1QML5r9u8nvh) 估算，也可参考下方 [价格示例](https://ark.volcengine.com/region:cn-beijing/docs/model-pricing#2653dbb3) 了解典型场景的视频价格。

## 按token单价

|模型 |在线推理<br><br>元/M token |离线推理<br><br>元/M token |
|---|---|---|
|doubao\-seedance\-2.5<br><br>> 按输出视频分辨率和输入是否包含视频区分定价 |* 输出视频分辨率为 480p，720p<br><br>   * 输入不含视频：70.00<br><br>   * 输入包含视频：42.00<br><br>* 输出视频分辨率为 1080p<br><br>   * 输入不含视频：77.00<br><br>   * 输入包含视频：46.00 |暂不支持 |
|doubao\-seedance\-2.5\-flash<br><br>> 按输入是否包含视频区分定价 |* 输出视频分辨率为 480p，720p<br><br>   * 输入不含视频：46.00<br><br>   * 输入包含视频：28.00 |暂不支持 |
|doubao\-seedance\-2.0<br><br>> 按输出视频分辨率和输入是否包含视频区分定价 |* 输出视频分辨率为 480p，720p<br><br>   * 输入不含视频：46.00<br><br>   * 输入包含视频：28.00<br><br>* 输出视频分辨率为 1080p<br><br>   * 输入不含视频：51.00<br><br>   * 输入包含视频：31.00<br><br>* 输出视频分辨率为 4K<br><br>   * 输入不含视频：26.00<br><br>   * 输入包含视频：16.00 |暂不支持 |
|doubao\-seedance\-2.0\-fast<br><br>> 按输入是否包含视频区分定价 |* 输出视频分辨率为 480p，720p<br><br>   * 输入不含视频：37.00<br><br>   * 输入包含视频：22.00 |暂不支持 |
|doubao\-seedance\-2.0\-mini<br><br>> 按输入是否包含视频区分定价 |* 输出视频分辨率为 480p，720p<br><br>   * 输入不含视频：23.00<br><br>   * 输入包含视频：14.00 |暂不支持 |
|doubao\-seedance\-1.0\-pro |15.00 |7.50 |
|doubao\-seedance\-1.0\-pro\-fast |4.20 |2.10 |

> * 仅对成功生成的视频计费。因审核等原因导致生成失败的，不收取费用。

> * 视频价格估算公式：`token 单价 × token 用量`

> * token 用量估算公式：`(输入视频时长+输出视频时长) × 输出视频的宽 × 输出视频的高 × 输出视频的帧率/1024`，该计算结果为估算值，准确 token 用量以调用 API 后返回的 usage.**completion_tokens** 字段为准。

> * [Seedance 2.5 样片（Draft）模式](https://ark.volcengine.com/region:cn-beijing/docs/seedance-2-5#2.5_draft_mode) 包含两步任务，每个任务独立计费：

>    * Step 1：生成 Draft 视频，按 480p 视频计费。

>    * Step 2：基于 Draft 生成正式视频，按目标分辨率计费：

>       * token 单价**根据 Step 1 是否包含输入视频确定**。

>       * 计算 token 用量时，**输入视频时长按 Step 1 的输入视频计算，Draft 视频不计入**。

## 价格示例

基于 token 用量公式估算的视频单价，方便您直观了解不同规格的视频成本。更多价格示例请参见 [火山方舟视频生成模型价格快查表](https://bytedance.larkoffice.com/wiki/FXaYwxzJ5i5Zdik32ipcWzt7nxd?table=tblns3WjGMNbR8sL&view=vewPa39Do4#CategoryScheduledTask)。

> **最低 token 用量限制说明**

> 对于 Seedance 2.0 系列、Seedance 2.5 系列模型，当输入包含视频时，存在最低 token 用量限制：

* > 如果估算 token 用量 ＜ 最低 token 用量，则按最低 token 用量计算视频价格。

* > 最低 token 用量与分辨率、宽高比、视频输出时长有关，可查询 [Seedance 2.0 系列最低 token 用量表格（估算值）](https://bytedance.larkoffice.com/wiki/FXaYwxzJ5i5Zdik32ipcWzt7nxd?table=tblheIYDXXwYM43b&view=vew2CR2JYM#CategoryScheduledTask) 、[Seedance 2.5 系列最低 token 用量表格（估算值）](https://bytedance.larkoffice.com/wiki/FXaYwxzJ5i5Zdik32ipcWzt7nxd?table=tblheIYDXXwYM43b&view=vew2CR2JYM#CategoryScheduledTask) 或使用 [Seedance 2.0 系列价格计算器](https://bytedance.larkoffice.com/share/base/form/shrcnP1Bl0mqCP9OHCbjpe1oBkf) 、[Seedance 2.5 系列价格计算器](https://bytedance.larkoffice.com/share/base/form/shrcnhVCMxKxcwW1QML5r9u8nvh) 估算视频任务的最低 token 用量，准确用量以调用 API 后返回的 usage.**completion_tokens** 字段为准。

### doubao\-seedance\-2.5 系列

* **输入不含视频**

|分辨率 |宽高比 |输出视频时长（秒） |doubao\-seedance\-2.5 视频价格 ||doubao\-seedance\-2.5\-flash 视频价格 ||
|---|---|---|---|---|---|---|
||||（元/个） |（元/s） |（元/个） |（元/s） |
|480p |16:9 |5 |3.36 |0.67 |2.21 |0.44 |
|720p |16:9 |5 |7.56 |1.51 |4.97 |0.99 |
|1080p |16:9 |5 |18.71 |3.74 |不支持 |不支持 |

* **输入包含视频**

|分辨率 |宽高比 |输入视频时长（秒） |输出视频时长（秒） |doubao\-seedance\-2.5<br><br>视频价格（元/个） |doubao\-seedance\-2.5\-flash<br><br>视频价格（元/个） |
|---|---|---|---|---|---|
|480p |16:9 |2~30 |5 |3.63~14.12<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入30秒 |2.42~9.42<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入30秒 |
|720p |16:9 |2~30 |5 |8.16~31.75<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入30秒 |5.44~21.17<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入30秒 |
|1080p |16:9 |2~30 |5 |20.12~78.25<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入30秒 |不支持 |

### doubao\-seedance\-2.0 系列

* **输入不含视频**

|分辨率 |宽高比 |输出视频时长（秒） |doubao\-seedance\-2.0 视频价格 ||doubao\-seedance\-2.0\-fast 视频价格 ||doubao\-seedance\-2.0\-mini 视频价格 ||
|---|---|---|---|---|---|---|---|---|
||||（元/个） |（元/s） |（元/个） |（元/s） |（元/个） |（元/s） |
|480p |16:9 |5 |2.31 |0.46 |1.86 |0.37 |1.16 |0.23 |
|720p |16:9 |5 |4.97 |0.99 |4.00 |0.80 |2.48 |0.50 |
|1080p |16:9 |5 |12.39 |2.48 |不支持 |不支持 |不支持 |不支持 |
|4K |16:9 |5 |25.27 |5.05 |不支持 |不支持 |不支持 |不支持 |

* **输入包含视频**

|分辨率 |宽高比 |输入视频时长（秒） |输出视频时长（秒） |doubao\-seedance\-2.0<br><br>视频价格（元/个） |doubao\-seedance\-2.0\-fast<br><br>视频价格（元/个） |doubao\-seedance\-2.0\-mini<br><br>视频价格（元/个） |
|---|---|---|---|---|---|---|
|480p |16:9 |2~15 |5 |2.53~5.62<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入15秒 |1.99~4.42<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入15秒 |1.27~2.81<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入15秒 |
|720p |16:9 |2~15 |5 |5.44~12.10<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入15秒 |4.28~9.50<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入15秒 |2.72~6.05<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入15秒 |
|1080p |16:9 |2~15 |5 |13.56~30.13<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入15秒 |不支持 |不支持 |
|4K |16:9 |2~15 |5 |27.99~62.21<br><br>> 最低价对应输入2~4秒<br><br>> 最高价对应输入15秒 |不支持 |不支持 |

## 版权 IP

使用版权 IP 生成视频时，不同版权单价不同。具体价格信息请在 [体验中心](https://ark.volcengine.com/region:cn-beijing/experience/gen_video?model=doubao-seedance-2-0-260128) 查看。

版权视频生成费用按各输入 IP 的单价和视频时长（秒）求和：

`单条视频版权费用 = Σ（每个输入 IP 的单价 × 视频时长（秒））`
