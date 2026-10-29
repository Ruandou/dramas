# 微短剧扶持台账 · 构建与部署规则

线上：https://duanju-policy.pages.dev （Cloudflare Pages 项目 `duanju-policy`，生产分支 `main`）

## 一、源码只有一个地方

- **唯一源码 = 本目录**（`公众号/扶持政策/`）：改 `data/policy.yaml`，跑 `build.py` 出 `dist/`。
- 小仓库 `~/Movies/duanju-policy`（GitHub `Ruandou/duanju-policy`）**只放部署产物**：`dist/`、`vercel.json`、`.gitignore`。不要把 `build.py` 或 `data/` 放回去，两份源码必然漂移。
- 部署读的是小仓库的 `dist/`，所以「重建」和「部署」之间必须有一次显式拷贝。

## 二、数据字段

| 字段 | 作用 | 注意 |
|---|---|---|
| `short` | 时间轴上的短标签 | 不填则回退到 `title`，会太长 |
| `start` | 开窗日，可省略 | 与 `deadline` 一起生成时间轴节点 |
| `deadline` | 截止日，`null` 表示滚动 | 卡片倒计时、排序、过期判断都靠它 |
| `updated` | 台账数据日期 | 顶部「更新于」与陈旧提示用它，**不要用 `date.today()`** |

## 三、四步部署（每步一个卡口）

```bash
# 1. 改数据：只改本目录 data/policy.yaml
# 2. 重建 + 校验（产物与数据逐字节比对，不一致会报错退出）
cd 公众号/扶持政策
python3 build.py
python3 build.py --check

# 3. 拷产物到小仓库并比对（三个文件全同才继续）
cp dist/index.html dist/404.html dist/_headers ~/Movies/duanju-policy/dist/
for f in index.html 404.html _headers; do
  cmp -s "dist/$f" "$HOME/Movies/duanju-policy/dist/$f" || { echo "DIFF $f"; exit 1; }
done

# 4. 部署（token 只从本机 600 权限文件读，不入库）
cd ~/Movies/duanju-policy
CLOUDFLARE_API_TOKEN=$(cat ~/.config/duanju-policy/cf_token) \
CLOUDFLARE_ACCOUNT_ID=66e4284ea93f7d90a59b90e6879c36d0 \
npx wrangler@latest pages deploy dist --project-name duanju-policy --branch main --commit-dirty=true
```

跳过第 2 步的 `--check` 或第 3 步的 `cmp`，就可能把旧版发上线（2026-10-29 已发生过一次：小仓库停在旧快照）。

## 四、部署后核验

```bash
curl -sS -o /tmp/live.html -w '%{http_code}\n' "https://duanju-policy.pages.dev/?v=$(date +%s)"
cmp -s /tmp/live.html dist/index.html && echo "线上与本地逐字节一致"
curl -sS -o /dev/null -w '%{http_code}\n' "https://duanju-policy.pages.dev/nope-123"   # 期望 404
curl -sSI "https://duanju-policy.pages.dev/" | grep -Ei 'x-content-type|referrer-policy'
```

再在浏览器看 1440 与 390 两个宽度、控制台 0 报错。`/404.html` 直连返回 308 是 Pages 的正常行为，验 404 用不存在的路径。

## 五、容易踩的坑

- **`date.today()` 不进产物**：`--check` 是逐字节比对，SSR 的倒计时必须用 `updated` 算，实时天数交给前端 JS，否则每天都会判「产物过期」。
- **过期天数取绝对值**：前端 `daysFrom()` 返回「距目标还有几天」，对过去的 `updated` 是负数。
- **线上不是 git 自动构建**：commit/push 不会更新站点，改了必须重新 deploy。
- **token 不落库**：`~/.config/duanju-policy/cf_token` 仅本机可读；`.env*`、`.vercel`、`.wrangler` 已在小仓库 `.gitignore`。
- **Vercel 仅备用**：`https://duanju-policy.vercel.app` 大陆 DNS 污染，打不开属正常。
