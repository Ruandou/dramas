# 可复制片段与接口字段

所有片段在页面上下文执行（chrome-devtools `evaluate_script`）。`TID` = 当前 token，`N` = 稿件号。

## 1. 粘贴正文

```js
const html = await (await fetch('http://127.0.0.1:8791/_tmp_body_0NN.html')).text();
const ed = document.querySelectorAll('.ProseMirror')[1];
const dt = new DataTransfer();
dt.setData('text/html', html);
dt.setData('text/plain', html.replace(/<[^>]+>/g, ''));
ed.focus();
ed.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }));
// 校验：ed.querySelectorAll('h2/table/strong') 与锚点数量
```

## 2. 按锚点插图

```js
const name = '0NN_图1_xxx_1080.png';
const p = [...ed.querySelectorAll('p')].find(e => e.innerText.includes('【图 1'));
const r = document.createRange(); r.selectNodeContents(p);
const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
const b = await (await fetch('http://127.0.0.1:8791/' + encodeURIComponent(name))).blob();
const dt = new DataTransfer(); dt.items.add(new File([b], name, { type: 'image/png' }));
p.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }));
// 等 5—6s；img.naturalWidth > 10
```

## 3. 标题与摘要

```js
const t = document.querySelectorAll('.ProseMirror')[0];
t.focus(); document.execCommand('selectAll');
document.execCommand('insertText', false, '标题');
const d = document.querySelector('#js_description');
Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(d, '摘要');
d.dispatchEvent(new Event('input', { bubbles: true }));
d.dispatchEvent(new Event('change', { bubbles: true }));
```

校验：`document.querySelector('textarea#title').value`。

## 4. 原创作者（关键：补键盘事件）

```js
document.querySelector('#js_original .js_original_apply').click();
const dlg = [...document.querySelectorAll('.weui-desktop-dialog')]
  .find(d => d.offsetParent !== null && /原创/.test(d.innerText));
const inp = [...dlg.querySelectorAll('input.js_author')]
  .find(i => i.offsetParent !== null && i.placeholder === '请输入作者');
inp.value = '一人短剧厂牌'; inp.focus();
for (const type of ['keydown','keypress','input','keyup','change']) {
  const E = type.startsWith('key') ? KeyboardEvent : Event;
  inp.dispatchEvent(new E(type, { bubbles: true, cancelable: true, key: '牌' }));
}
// 计数应为 6/8；再点「确定」
```

## 5. 封面上传

```js
document.querySelector('.select-cover__btn').click();
await new Promise(r => setTimeout(r, 600));
document.querySelector('#js_cover_null .js_imagedialog').click();
await new Promise(r => setTimeout(r, 1200));
const name = '封面_0NN_xxx_900x383.png';
const b = await (await fetch('http://127.0.0.1:8791/' + encodeURIComponent(name))).blob();
const input = [...document.querySelectorAll('input[type=file]')].find(i => i.accept.includes('bmp'));
const dt = new DataTransfer(); dt.items.add(new File([b], name, { type: 'image/png' }));
input.files = dt.files; input.dispatchEvent(new Event('change', { bubbles: true }));
// 等首项 .weui-desktop-img-picker__item.selected → 下一步 → 确认
```

校验：`.js_cover_preview_new` 的 `background-image` 含 `mmbiz.qpic.cn`。

## 6. 定时与群发

```js
const d = [...document.querySelectorAll('.weui-desktop-dialog')]
  .find(x => x.offsetParent !== null && /定时发表/.test(x.innerText));

// 开定时
const sws = [...d.querySelectorAll('.weui-desktop-switch')];
const lbl = sws[sws.length - 1];
lbl.querySelector('.weui-desktop-switch__box')?.click();
await new Promise(r => setTimeout(r, 400));
if (!d.querySelector('.mass-send__timer')) lbl.click();
await new Promise(r => setTimeout(r, 400));
const inpSw = lbl.querySelector('input');
inpSw.checked = true;
inpSw.dispatchEvent(new Event('input', { bubbles: true }));
inpSw.dispatchEvent(new Event('change', { bubbles: true }));
await new Promise(r => setTimeout(r, 1200));

// 日期
d.querySelector('.mass-send__timer .weui-desktop-form__dropdown__dt').click();
await new Promise(r => setTimeout(r, 600));
[...d.querySelectorAll('.mass-send__timer .weui-desktop-dropdown__list-ele')]
  .filter(e => e.getBoundingClientRect().height > 0)
  .find(e => e.innerText.trim() === '明天')?.click();
await new Promise(r => setTimeout(r, 1500));

// 时间：必须点选择器
const tin = [...d.querySelectorAll('input[type=text]')].find(e => e.getBoundingClientRect().height > 0);
tin.click();
await new Promise(r => setTimeout(r, 900));
const picker = [...d.querySelectorAll('.weui-desktop-picker__time')].find(p => p.getBoundingClientRect().height > 0);
const hours = [...picker.querySelectorAll('.weui-desktop-picker__time__hour li')];
const mins  = [...picker.querySelectorAll('.weui-desktop-picker__time__minute li')];
hours[8].click(); await new Promise(r => setTimeout(r, 400));
mins[0].click();  await new Promise(r => setTimeout(r, 700));
// 校验：tin.value === '08:00'，且 hours/mins 选中索引为 8/0
```

状态判读：
- 开关顺序通常为 `[群发通知, 分组通知, 定时发表]`。
- 文案「今天没有通知次数」= 群发不可开；「明天还有 1 次通知次数」= 可开。
- 「该时刻定时消息过多…」可忽略。

## 7. 贴图：描述、上传、去重

```js
// 描述：段间全角空格行
const lines = ['厂牌榜 0NN · 2026-MM-DD', '　', '· …'];
const html = lines.map(l => '<p>' + l.replace(/&/g,'&amp;').replace(/</g,'&lt;') + '</p>').join('');
const ed2 = document.querySelectorAll('.ProseMirror')[1];
const dt2 = new DataTransfer(); dt2.setData('text/html', html); dt2.setData('text/plain', lines.join('\n'));
ed2.focus(); ed2.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt2, bubbles: true, cancelable: true }));

// 上传（只触发一次！）
const names = ['榜0NN_贴图1_…png','榜0NN_贴图2_…png','榜0NN_贴图3_…png'];
const up = new DataTransfer();
for (const n of names) {
  const b = await (await fetch('http://127.0.0.1:8791/' + encodeURIComponent(n))).blob();
  up.items.add(new File([b], n, { type: 'image/png' }));
}
const fin = [...document.querySelectorAll('input[type=file]')].find(i => i.accept.includes('bmp'));
fin.files = up.files; fin.dispatchEvent(new Event('change', { bubbles: true }));

// 去重：保留第一组 3 张，从末尾删
for (let g = 0; g < 8; g++) {
  const items = [...document.querySelectorAll('.image-selector__bottom-list-item')];
  if (items.length <= 3) break;
  items[items.length - 1].click();
  await new Promise(r => setTimeout(r, 400));
  document.querySelector('.image-selector__edit-bar-item a.comm_del')?.click();
  await new Promise(r => setTimeout(r, 700));
  const dlg = [...document.querySelectorAll('.weui-desktop-dialog')]
    .find(x => x.offsetParent !== null && /删除/.test(x.innerText));
  if (dlg) [...dlg.querySelectorAll('button,.weui-desktop-btn')]
    .find(b => /确定|删除/.test(b.innerText))?.click();
  await new Promise(r => setTimeout(r, 700));
}
```

注意：`0/20` 是标题字数，不是图片数。

## 8. 保存、发布核验接口

```js
// 文章/贴图发表记录
const r = await fetch('/cgi-bin/appmsgpublish?sub=list&begin=0&count=5&token=TID&f=json&ajax=1&lang=zh_CN', { credentials: 'include' });
const j = await r.json();
const page = JSON.parse(j.publish_page);          // publish_page 是字符串
const x = page.publish_list[0];
const info = JSON.parse(x.publish_info);          // publish_info 也是字符串
const a = (info.appmsg_info || [])[0];
// 关键字段：info.sent_info.time / is_send_all；info.sent_result.msg_status；
// a.title / a.content_url / a.read_num / a.copyright_status；
// 贴图顺序：a.share_imageinfo[].file_id / cdn_url / width / height
```

```js
// 首页定时卡
const t = document.body.innerText.replace(/\s+/g, ' ');
const i = t.indexOf('定时发表');
t.slice(i, i + 80);
// 期望形如：定时发表 明天 08:00 已开启群发通知 取消发表 <标题>
```

## 9. 登录状态

```js
const t = document.body.innerText;
const loggedOut = /登录超时|请重新登录|扫码登录/.test(t);
const acct = (t.match(/一人短剧厂牌/) || [])[0];
```

## 10. 图片顺序比对（本地）

```python
from PIL import Image
def sig(im): return list(im.convert('L').resize((32, 32)).getdata())
# 对线上下载图与本地图分别求 sig，逐像素绝对差求和；距离 0 即同一张
```
