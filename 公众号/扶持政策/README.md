# 短剧资料库 · 数据维护、构建与部署

线上：https://duanju-policy.pages.dev （Cloudflare Pages 项目 `duanju-policy`，生产分支 `main`）。本地构建不等于已上线。

## 一、唯一底库与生成物

唯一源码在本目录 `公众号/扶持政策/`。当前用结构化 JSON + Git 管理资料，不增加业务数据库或远程后台。

- `data/catalog.json`：唯一权威底库，包含稳定 ID、实体关联、字段、来源、日期窗口、逐字段核验证据、修改历史、原始迁移档案。
- `catalog.py`：校验、人工核验入口、Markdown 导出。
- `maintain.py`：公开来源正文巡检、私有快照、待审队列、覆盖率报告；不修改事实。
- `data/maintenance.json`：程序显式导出的计数/时间摘要，可公开，不含正文快照、来源 URL 或待审记录 ID。
- `web.py`、`static/catalog.js`、`static/catalog.css`：页面与交互源码。
- `build.py`：生成 `dist/` 七个文件和素材目录五份 Markdown 阅读版。站点数据统一输出为 `dist/catalog.json`，不再生成 YAML；不要手改生成物。

当前数据文件统一为 JSON，不另建扶持专题数据副本。底库的 `migration_archive.policy_yaml` 仅保存首次迁移的原始文本，历史来源中的 YAML 路径也只作溯源记录；两者不是现行数据入口，不改写或删除。

首次迁移为 330 条资料记录：15 条扶持项目/历史批次、71 条地方资料、73 条分发平台、91 条模型、80 条工具用途。它们不是 330 个独立产品或可参与机会；同产品不同用途通过 `entity_id` 关联。后续数量由底库计算，不再手工维护标题里的数字。

首页以搜索、四类入口、内容变更和日期提醒组织资源；分类页分别按地区与主体条件、市场与接入、模型能力、制作环节与环境筛选。`?view=policies|platforms|models|tools` 进入分类，附 `id` 进入独立详情页，完整展示字段、来源、核验证据、历史和关联条目。旧 `?category=`、`/policies.html` 与 Cloudflare 的 `/policies` 入口继续有效；搜索、筛选和详情状态写入 URL，便于分享和回退。

## 二、数据与证据规则

| 信息 | 维护规则 |
|---|---|
| `id` | 稳定记录身份；改标题不改 ID，不使用表格行号作身份 |
| `entity_id` / `related_ids` | 同一产品的不同用途、政策与地方条目之间建立关联 |
| `fields` / `source_ids` | 事实文本关联记录内的来源；一个官网链接不自动证明整行参数 |
| 来源 A / B / C | 来源权威程度，不等于事实已经核验；来源须写清适用范围 |
| `reported_as_of` | 原资料声明截至日期，不自动刷新成今天 |
| `imported_at` | 导入时间，不是事实核验时间 |
| `updated_at` | 内容实际变化的时间，不是例行抓取时间 |
| `verified_at` / `verification` | 保存被核字段当前值、来源、原文摘录、时间及备注；值变了须重新核验或清除旧标记 |
| `metadata_verification` | 标题、参与方式、生命周期、窗口类型/起止日也需各自核验 |
| `last_verified_at` | 所有字段及适用元数据均有证据才可设置；取最旧证据时间，不将部分核验包装成整条已核 |
| `window.kind` | 区分申报、激励、签约、政策有效期；期限按北京时间日期计算，截止日当天仍在期内 |
| 空日期 / 无窗口 | 表示未记录或待核，不代表滚动申报，也不能据此认定开放 |
| `access` | 公开、邀约、商务、未知、不适用；名单邀约不等于公开报名 |
| `lifecycle` | 在列、历史、未知；老模型版本不等于整个厂商停服 |
| `history` / `provenance` | 保留原始迁移档案与修订沿革；公开页面只输出简要原文件/行号，不输出整份迁移原文 |

金额必须保留「最高」「不超过」、比例基数、主体和年度等条件。未知价格/分账不外推收益，检索未查到不写成确定不存在。

## 三、每日巡检

从仓库根目录执行：

```bash
python3 公众号/扶持政策/catalog.py check
python3 公众号/扶持政策/maintain.py scan --if-due --limit 20 --timeout 12
python3 公众号/扶持政策/maintain.py report --output 公众号/扶持政策/data/maintenance.json
python3 公众号/扶持政策/build.py
python3 公众号/扶持政策/build.py --check
```

- 每批最多尝试 20 个去重来源，近期窗口与最久未尝试来源轮转；这不是每天全库复核。
- 北京时间当日已有成功批次时 `--if-due` 跳过；全失败或全需人工不满足当日成功，下个触发时段可重试。部分成功必须同时显示失败数、人工项及未覆盖数。
- 读取成功只说明正文读回，不证明政策可申报、产品可用或价格真实。首次正文也进入待审；变化保留前后版本，未经确认不成为比较基线。
- 私有状态默认在 `~/.local/state/yiren-catalog/`：`state.json` 保存队列/运行进度，`snapshots/` 保存按内容哈希命名的原文与规范化正文。不要放到 `dist/`、Git 或部署目录。
- `report` 可在终端查看完整待审 ID、来源键和影响的记录；通过私有 `state.json` 的队列项读取 `before` / `after` 快照。不要把完整输出重定向到公开仓库。
- 403、验证码、账号/API页面、GitHub、PDF、JS空壳、TLS异常等交人工，不判死链、不绕验证、不关 TLS。公开抓取不携带账号凭据，并拒绝私网目标。
- 状态缺失/损坏会停止，保留原证据后恢复备份，禁止通过删除整个状态目录来消除错误。新快照先写临时文件并同步，再以不覆盖方式原子发布；已存在证据不可静默覆盖。

### 本机定时任务

已将现有 Qoder 本地任务扩展为「一人短剧厂牌·资料巡检与选题搜索」，任务 ID `8e43a0c3-ce1d-4e88-a67b-06b670108152`。沿用 `Asia/Shanghai` 每日 10:07、13:07、16:07、19:07（`7 10-19/3 * * *`），模型及权限配置未改。

每次触发先执行上述当日幂等巡检，再保留原关键词选题搜索。选题仍受时效、相关性、独立来源与热度凭据约束；底库事实变化不因「不够热」而丢弃。新条目/疑似纠错先列本轮执行会话的待审建议，不自动入库或核验。自动任务只重建本地页面，不发布站点、不提交或推送 Git。

机器和 Qoder 需要可运行；多时段只增加遇到开机时段的机会，不保证离线时照常执行，也不补造漏跑日期。任务已保存不等于未来运行已完成，可从自动化执行记录查看结果；需全天候运行时另行确认云端迁移。

## 四、人工核验与更新

先读官方原文，核对字段所需条件及时间，确认记录内来源 ID。只有真实摘录可以作为核验证据。以下是命令模板，不能用占位摘录直接核验：

```bash
python3 公众号/扶持政策/catalog.py review \
  --record '<记录ID>' --field '<字段key>' --source '<来源ID>' \
  --quote '<已读原文的实际摘录>' --value '<确认后的完整字段值>' \
  --note '<口径与修改原因>'
python3 公众号/扶持政策/build.py
python3 公众号/扶持政策/build.py --check
```

不改值时省略 `--value`；元数据可使用 `title`、`access`、`lifecycle`、`window.kind`、`window.start`、`window.end`，已有窗口的起止日可用 `--value null` 清空。来源必须属于该字段或记录，摘录和值会进入历史。

新增记录/来源或改变记录结构时编辑底库，保留已有 ID/证据/沿革，给新事实留空核验时间；非扶持项目还需更新相应 `documents[].blocks` 的引用。随后运行 `catalog.py check` 和构建检查。`import_catalog.py` 保留首次迁移逻辑，已有底库会拒绝覆盖，不用于日常更新；迁移测试只在临时目录从归档重建旧输入，不要求现行目录存在 YAML 文件。

正文待审核销是另一件事：明确读过快照、确认仅接受比较基线后，才由人工执行：

```bash
python3 公众号/扶持政策/maintain.py dismiss '<队列ID>' --reason '<人工查看结论>'
```

这只确认该正文版本作为比较基线，不改底库，不核验任何事实，也不关闭同来源的其他待审版本。执行后重新生成巡检摘要与页面；自动任务禁止执行 `review` 或 `dismiss`。

## 五、本地验收

日常维护和构建只需 Python 3.9+ 标准库，不依赖 PyYAML。完整测试中的历史迁移重放仍使用项目已有的 PyYAML；前端纯函数测试使用 Node，不需要安装前端框架。

```bash
python3 -B -m unittest discover -s 公众号/扶持政策/tests
node --check 公众号/扶持政策/static/catalog.js
python3 公众号/扶持政策/build.py
python3 公众号/扶持政策/build.py --check
python3 -m http.server 8766 --bind 127.0.0.1 --directory 公众号/扶持政策/dist
```

浏览器查看 `http://127.0.0.1:8766/`，验收 1440 / 390 两个宽度、四类搜索和筛选、无结果重置、来源/证据展开、深链接及回退。全库核验数与巡检覆盖率分开显示。检查控制台错误；Python 预览服务器不会应用 Cloudflare 的 `_headers`，线上仍需单独验证 CSP。

`tests/browser_acceptance.js` 是真实浏览器回归脚本：在 8767 端口另起上述预览服务器，通过 Playwright MCP 的 `browser_run_code_unsafe` 传入该文件的绝对 `filename` 运行。脚本新建并关闭自己的隔离浏览器上下文，覆盖桌面/手机、筛选与历史导航、证据与异常数据；测试证据只通过浏览器请求拦截注入，不写入底库。

`--check` 对七份站点产物和五份 Markdown 阅读版逐字节比对，共 12 个文件；普通构建只写已知产物，不清空输出目录或删除无关文件。产物不使用构建当天伪造数据更新时间，前端按北京时间实时计算窗口状态。

## 六、经当次授权后部署

小仓库 `~/Movies/duanju-policy`（GitHub `Ruandou/duanju-policy`）只放部署产物 `dist/`、`vercel.json`、`.gitignore`。不要复制源码或私有状态；commit/push 不会自动发布网站。

从仓库根目录依次执行，任一卡口失败即停止：

```bash
python3 公众号/扶持政策/build.py
python3 公众号/扶持政策/build.py --check

for f in index.html policies.html catalog.js catalog.css catalog.json 404.html _headers; do
  cp "公众号/扶持政策/dist/$f" "$HOME/Movies/duanju-policy/dist/$f" || exit 1
  cmp -s "公众号/扶持政策/dist/$f" "$HOME/Movies/duanju-policy/dist/$f" || exit 1
done

CLOUDFLARE_API_TOKEN=$(cat ~/.config/duanju-policy/cf_token) \
CLOUDFLARE_ACCOUNT_ID=66e4284ea93f7d90a59b90e6879c36d0 \
npx wrangler@latest pages deploy "$HOME/Movies/duanju-policy/dist" \
  --project-name duanju-policy --branch main --commit-dirty=true
```

Token 仅从本机权限 600 的文件读取，不入仓库、不打印。发布前确认部署目录没有额外私有文件；七个文件全部比对一致才可部署，防止小仓库旧快照上线。

部署后逐项验证首页、旧扶持入口、CSS/JS/公开 JSON，线上内容与本地产物一致；不存在的路径返回 404，HTTP 响应头含 CSP、nosniff 和 Referrer-Policy。再用桌面和移动端实测交互。`/404.html` 的扩展名重定向不等于缺失路径的 HTTP 404。
