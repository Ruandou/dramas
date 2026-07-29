# AIGC产物转存到对象存储（TOS）-最佳实践

## 产物转存场景

```
```

```
```

```
```

```
```

大模型生成的所有文件类产物（视频/音频/图片/文档等），建议客户写入到自有TOS Bucket进行留存和归档，便于后续的内容分发/内容处理/内容检索/数据集构建等。

## 转存TOS方法

### 方案一（已上线）：数据订阅自动转存（For方舟）



[图片: LZZybcra5oznldxsIDPcPLxdn6e]

[图片: JkrHbYCbyorShQxAcr9ceZwtnWe]


在TOS控制台配置“数据订阅”规则

[图片: NSxWbZFigoBNbdxV5FDcgdvlnyh]

[图片: Gpl3bRjkbonWQbxZGI2cjh4dnOC]

[图片: GyoLbM5ASo3zTmxgMfIcb4o1nQb]

效果示意图：

[图片: Q0flbECWtoZQu0xcqHsc6yb2nkd]

[图片: QOZRbMbP0ojnUyx45AOcWrBrnxd]

数据订阅规则创建完成之后，方舟生成的产物将会自动同步到租户账号的目标Bucket。业务在调用方舟API获取成功响应后，可直接访问（Get请求）目标Bucket中的产物文件。

### 方案二（已支持）：使用对象级镜像回源功能（通用）

当前该功能需要by Bucket做调度，预计5月份全量放开。开白可联系 @ou_315823bedbf169367b38921e4ab574ab@ou_f032e5c7ffac12d3430be29a80827f33


操作步骤：


---

> [图片: U7cOb4YjnoYtkAxA799ctGmSnZd]
> ---

### 方案三（已支持）：使用抓取对象FetchObject功能（通用）

FetchObject API：https://www.volcengine.com/docs/6349/1257670?lang=zh


示例代码（TOS Python SDK）：

---

## 本仓库 TOS 路径约定（项目规范，2026-07-29 补录）

> 背景：此前约定只存在于 `mcps/volc-ark/scripts/tos_upload.py` 的 sync_dirs 代码中，文档未载明，导致 2026-07-29 误开 `videos/` 自定义前缀（孤儿副本待控制台清理）。现将事实标准补录为规范。

### 前缀表（Bucket: drama-reference-images）

| 产物 | 本地目录 | TOS 前缀 | 递归 | 扩展名 |
|------|---------|---------|------|--------|
| 角色形象图 | `assets/looks/` | `looks/<剧名>/` | 否 | png/jpg/jpeg/webp |
| 场景图 | `assets/scenes/` | `scenes/<剧名>/` | 否 | 同上 |
| 道具图 | `assets/props/` | `props/<剧名>/` | 否 | 同上 |
| **生成视频（段+成片）** | `assets/generated/` | `generated/<剧名>/EP##/` | **是** | mp4/mov/avi/webm |

### 唯一正确姿势

```bash
python3 mcps/volc-ark/scripts/tos_upload.py sync --project-root "dramas/<剧名>"
```

- sync 自动：上传四类目录 + 写 `cdn_urls.json` 登记（generated 的键为相对路径如 `EP01/EP01-SEG01.mp4`，值含 `{local, tos_url, size}`）
- **禁止**手工 `upload --key` 自创前缀（如 `videos/`）——会绕过登记产生孤儿对象；单文件补传也须沿用上表前缀并随后 `update-registry`
- 道具/角色/场景图路径中**不含** `assets/` 段（事故复盘：`props/<剧名>/assets/props/PROP-###.png` 系错误拼接 → 400 resource not found，见 2026-07-29 边荒盐妇 EP01）
- 验收：上传后对 `cdn_urls.json` 登记的 tos_url 抽样 `curl -I` 验 HEAD 200 + Content-Length 与本地一致
- ⚠️ **sync 不覆盖同名对象**（只判 object_exists，不比内容）：重烧成片/重生成同名素材后，必须对变更文件单独 `upload --key <同前缀同名>` 强制覆盖，并用 Content-Length 比对验收（事故复盘：2026-07-29 边荒盐妇 EP01 补烧出场卡后 sync 全部 SKIP，TOS 上仍是旧版）

