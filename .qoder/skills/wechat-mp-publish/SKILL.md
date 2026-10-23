---
name: wechat-mp-publish
description: 微信公众号「一人短剧厂牌」的文章与贴图发布全流程：正文导入、按锚点插图、标题摘要、原创声明、封面、存草稿、定时发表、群发通知、管理员扫码验证、线上核验，以及登录过期、二维码过期、上传重复、定时时间错位等故障恢复。当需要把 Markdown 稿导入公众号后台、设置定时/群发、核验发布结果，或处理上述异常时使用。
---

# 公众号发布流程与故障处理

## 适用边界

- 只操作公众号「一人短剧厂牌」（`mp.weixin.qq.com`）。视频号、抖音等其他账号一律不读、不回、不发。
- 发布/群发/修改/删除的微信验证二维码，必须由管理员本人扫；助手只负责把二维码截图交出去。
- 不调用任何付费生成 API；配图用本地 Pillow。发布环节不产生 API 费用。
- 仓库是 public：登录 token、密码、邮箱不写入仓库文件。

## 前置检查

1. 确认浏览器当前页是已登录的公众号后台，且账号名为「一人短剧厂牌」。登录过期（页面出现「请重新登录」「登录超时」）立即停止，走「登录过期」流程。
2. 只用一个标签页操作；填写表单中途不导航离开。浏览器里其它标签（抖音、视频号等）不碰。
3. 记录当前 URL 里的 `token`；每次登录后 token 会变，后续所有后台 URL 都要用新 token。
4. 本地图片先起静态服务：`python3 公众号/榜单/serve_assets.py 公众号/素材 8791`，页面内用 `fetch` 取图。
5. 稿件三件套齐了再进后台：`文章/0NN_发布版.md`、`素材/0NN_增量卡.md`、`素材/_gen_0NN.py`（图与封面）。

## 一、文章发布

### 1. 生成正文 HTML

```bash
python3 公众号/素材/_md2html.py 公众号/文章/0NN_发布版.md 公众号/素材/_tmp_body_0NN.html
```

检查输出：`h2` 数、`table` 数、`strong` 数、图锚点 3 个、无 `**` 残留。图锚点形如 `【图 1：…】`，必须独立成段。

### 2. 打开编辑器

```
https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token=<TOKEN>&lang=zh_CN&timestamp=<毫秒>
```

等到页面出现两个 `.ProseMirror`。`[0]` 是标题，`[1]` 是正文。

### 3. 粘贴正文并即时校验

对 `.ProseMirror[1]` 派发 `ClipboardEvent('paste')`，`text/html` 放 HTML、`text/plain` 放去标签文本。粘贴后立刻核对：h2、p、table、strong、图锚点数量与 HTML 一致。

### 4. 按锚点插图

逐个锚点：定位包含「【图 N」的 `<p>` → `Range.selectNodeContents(p)` → 选中 → 派发带图片 File 的 `paste`。每张等 5—6 秒，确认 `img.naturalWidth > 10` 且锚点减少。三张插完锚点应为 0。

图片 File 用 `fetch('http://127.0.0.1:8791/'+encodeURIComponent(name))` 取 blob 构造，不要依赖 MCP 的本地文件上传（workspace 限制会拒绝仓内路径）。

### 5. 标题与摘要

- 标题：`.ProseMirror[0]` 聚焦 → `selectAll` → `execCommand('insertText', …, title)`。校验 `textarea#title` 的值。
- 摘要：`#js_description` 用原生 setter 赋值，再派发 `input`/`change`；目标 ≤120 字，后台计数以实际为准。

### 6. 原创声明

1. 点 `#js_original .js_original_apply` 打开弹窗；「文字原创」默认选中。
2. 作者框：可见的 `input.js_author[placeholder="请输入作者"]`。
3. **只赋值不会更新计数**：赋值后依次派发 `keydown`、`keypress`、`input`、`keyup`、`change`，看到计数变成 `6/8` 且「作者不能为空」消失，再点「确定」。
4. 成功后校验 `span.js_type_explicit` 为「文字原创」、`span.js_author_explicit` 含作者名。

### 7. 封面

`.select-cover__btn` → `#js_cover_null .js_imagedialog` → 找到 `input[type=file][accept*=bmp]`，塞 File 并派发 `change` → 等图片库首项出现且 `selected` → 「下一步」→「确认」→ 校验 `.js_cover_preview_new` 的 background-image 是 `https://mmbiz.qpic.cn/…`。

### 8. 存草稿与重载复核

点「保存为草稿」，URL 会变成 `type=77&appmsgid=<DRAFT_ID>`。重载后逐项核对：标题、摘要、h2、表格、加粗、三张图尺寸、图锚点 0、原创、封面。任何一项不符，先修再往下。

### 9. 定时与群发

1. 点「发表」，等弹窗出现（class 可能是 `.new_mass_send_dialog`，也可能只是 `.weui-desktop-dialog`；按「定时发表」文字找）。
2. 定时开关：取最后一个 `.weui-desktop-switch`；先点 `.weui-desktop-switch__box`，必要时再点 label，然后 `input.checked = true` 并派发 `input` + `change`。出现 `.mass-send__timer` 才算成功。
3. 日期：点 `.mass-send__timer .weui-desktop-form__dropdown__dt`，在可见的 `.weui-desktop-dropdown__list-ele` 里选「今天」或「明天」。切到明天后，若有额度，群发开关会自动变为开启且可用。
4. 时间：输入框只是显示层。点开 `.weui-desktop-picker__time`，在 `.weui-desktop-picker__time__hour li` 和 `__minute li` 里点选目标时/分（索引 0 起）。核对选中索引与输入框值一致，否则会按旧时间提交。
5. 群发通知：第一个开关。显示「今天没有通知次数」时不可开；显示「明天还有 1 次通知次数」时可开。贴图无需群发。
6. 出现「该时刻定时消息过多…」属正常提示，可继续。
7. 点弹窗里的「发表」→ 若弹「已开启群发通知」，点「继续发表」→ 等微信验证二维码。

### 10. 扫码与核验

- 截图二维码交管理员扫；助手绝不代扫。
- 扫码成功后页面会跳回首页。核验首页定时卡文字：`定时发表 明天/今天 HH:MM 已开启群发通知/未开启群发通知`，标题一致。
- 已发表后核验 `publish_list`（见 references）与线上页；贴图再核 `share_imageinfo` 的图片顺序。

## 二、贴图发布

1. 首页「新的创作 → 贴图」会开新标签；URL 含 `type=77&createType=8`。
2. 标题栏留空（线上标题取描述第一行）。描述写入 `.ProseMirror[1]`，段间用全角空格（U+3000）单独成行。
3. **别把标题计数器当图片数**：标题上限 20，会显示 `0/20`；描述上限 1000，显示 `x/1000`。
4. 上传：用 `input[type=file][accept*=bmp]` 塞 3 个 File 并派发 `change`。**每次 change 会把选中的 3 张全部上传**；重复触发会产生重复图。上传后数可见的 `.image-selector__bottom-list-item`，不是 3 就删多余。
5. 删除：选中末尾缩略图 → 点含 `a.comm_del` 的 `.image-selector__edit-bar-item` → 若有确认弹窗点「确定」。保留第一组 1→2→3，避免顺序错乱。
6. 顺序核验：发布后用 `share_imageinfo` 的 `file_id` 顺序，配合本地图 32×32 灰度签名比对，确认与 1→2→3 一致。
7. 发表：弹窗「发表贴图无需开启群发通知」→「发表」→ 扫码。贴图不占群发额度、无原创入口。

## 三、故障处理

| 现象 | 原因 | 处理 |
|---|---|---|
| 页面显示「登录超时/请重新登录」 | 会话过期 | 停手；打开登录页 →「扫码登录」，截图交管理员；登录后 token 会变，重开编辑器 URL |
| 编辑页打不开、提示 not found | token 已失效/换号 | 用新 token 重开；不要复用旧 URL |
| 作者计数一直 0/8、提示不能为空 | 组件只听键盘事件 | 赋值后补发 keydown/keypress/input/keyup/change |
| 时间输入框显示 08:00，但实际按 11:42 提交 | 输入框非模型，选择器才是 | 点开选择器，点选小时/分钟 li，核对选中索引 |
| 定时开关点不动 | 开关是 label + 隐藏 input | 点 `__box`，再点 label，再设 checked + input/change |
| 扫码提示二维码过期 | 二维码有时效 | 关掉验证弹窗（状态会保留）→ 再点「发表」→「继续发表」→ 新码 |
| 扫码后编辑页直接关闭 | 提交成功并跳首页 | 到首页看定时卡；未发表则查 publish_list |
| 贴图里出现 6/9 张重复图 | change 重复触发 | 保留第一组三张，选中末尾逐张删除 |
| 图片上传后页面无变化 | 选错了 file input | 认准 `accept` 含 `bmp` 且位于 webuploader 容器里的那个；优先在页面内 fetch + File |
| 图片顺序不确定 | 列表顺序≠文件顺序 | 下载线上图做 32×32 灰度签名，与本地图比对 |
| 保存后重载内容缺失 | 保存未完成/版本冲突 | 等保存跳转后再重载；冲突时走「查看新草稿 → 最新的草稿」 |

## 四、发布后记账

- 写 `素材/0NN_编辑信息.json`：状态、draft_id、定时/发表时间、URL、群发与否、标题摘要、图、证据分级、验收结果。
- 更新 `整改计划_2026-10-20.md` 的候选池与期号（榜单日更会占用周报期号，需顺延）。
- 账号检测记录按 `公众号/账号检测记录.md` 规则补 D+1/D+2；token 不落库。
- 提交/推送必须获得当次明确授权；提交前扫描 token、密码、邮箱等敏感串。

## 五、红线

- 不代扫二维码；不操作其它账号；不用付费 API；不覆盖已发表内容。
- 表单填写中途不导航离开；每次保存/提交后必须重载或读接口复核，不凭“看起来对”。
- 任何“最高/上限”类数字，正文必须带口径与来源分级，不写成到手价。

## 资源

- `references/mp-selectors.md`：粘贴、插图、原创、封面、定时、上传、发布核验的可复制 JS 片段与接口字段。
