# Seedance 2.0 企业级权限隔离& 分账方案

公司内不同部门之间不希望看到对方的产物，特别是在内部赛马情况下，可以通过IAM结合项目project以及endpoint来做项目隔离及分账。
注：**权限边界说明**： IAM 主要用于管理用户对火山方舟**管控面**（如资源配置、控制台访问）的权限。 若需管理**数据面**（如模型推理调用）权限，请通过配置 API Key 权限实现。
**企业级权限管控场景实践&分账方案：**
```
```
```
```

## 权限隔离整体思路

企业在一个主账号下创建多个子账号，通过将 IAM 策略与project绑定，实现跨部门的资源与数据强隔离。

*示例：API Key 「apikey-sd1pro1」只能访问 API Key「apikey-sd1pro1」下的「Endpoint1」和「Endpoint2」，不能查看「sd1profast」project中的资源；也不能查看API Key 「apikey-sd1pro2」下的「Endpoint1」和「Endpoint2」*


## **操作步骤**：

## **创建IAM子用户**：

**什么是IAM用户？为什么要创建IAM用户？**

```
```

```
```

```
```

```
```

**操作入口：**

[访问控制（IAM）](https%3A%2F%2Fconsole.volcengine.com%2Fiam%2Fidentitymanage%2Fuser)

[图片: EEWUbqyGyosUXFxEkoWcDz4Nnmb]

**填写基础信息：**

输入姓名、手机号等；访问方式按个人需求勾选（调用API/控制台访问）。点击“下一步”。

[图片: I2EabvvjUoEJxbxftYVcaja7nhd]

## 创建项目（project）

入口：https://console.volcengine.com/iam/resourcemanage/project

[图片: KMwfb28e5oZtrCx6FpPcmDATnUf]

## **IAM权限设置**

为实现控制台级别的项目隔离，需要为 IAM 用户配置两类 Ark 相关的权限策略：

```
```

```
```

### ** 配置全局权限：**

```
```

```
```

```
```

[图片: A1RSbng4DoB6nlx9j9ScTEH4n8e]

### **配置项目业务权限：**

```
```

```
```

```
```

```
```

```
```

[图片: CgjlbCHXloLPPDx0FLucy3gdnRf]

配置完成后，该子用户登录火山方舟控制台时，将只能在 project-A 项目中创建、查看和管理资源，无法访问其他项目的任何内容，从而达到严格的UI隔离效果。

## API Key & endpoint 的项目隔离

顶部导航栏选择该项目-->API key管理开通API key

[图片: E2NXbwmvdoI2KNxPU7pcl0rxn6d]

自定义API key权限范围：通过endpoint来做权限隔离，将API Key与endpint进行绑定

[图片: QuPCbbTwuoxIg9x0YJPci4ukneh]

## 虚拟人像&真人素材资产库的项目隔离

> 注意：在使用seedance2.0上传虚拟人像/真人人像资产时，也可以**上传到特定的project**实现素材资产隔离。
> ```
> ```
> ```
> 
> 
> ```


## 分账账单

支持按照财务托管、项目project、标签、计费单元、子账号、API key多维度分账

参考：https://www.volcengine.com/docs/82379/1884418?lang=zh
