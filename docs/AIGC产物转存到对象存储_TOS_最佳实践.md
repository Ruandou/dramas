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
