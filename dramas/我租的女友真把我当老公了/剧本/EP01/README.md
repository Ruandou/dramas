# EP01《下单》· 试拍清单

> **状态**：v2.2 可试拍 · 对齐超雄 EP01 **134s** · 2026-05-25

## 文件

| 文件 | 用途 |
|------|------|
| `EP01_下单.md` | 人类可读分镜（32 镜 · 13 段） |
| `EP01_shots.yaml` | 逐镜机器可读（api / assets / return_last_frame） |
| `EP01_segments.yaml` | Seedance 提交（13 段 × 4–12s，合计 **134s**） |

## 试拍前（按顺序）

1. **Seedream 定妆** → 见 [`../../assets/seedream_EP01.yaml`](../../assets/seedream_EP01.yaml)  
   - `CHAR-001-L01/L02` · `CHAR-002-L01` · `SCENE-001~003`
2. **终端确认素材**（`.gitignore` 目录须 `ls`）  
   ```bash
   ls -lh assets/looks/CHAR-001-L*.png assets/looks/CHAR-002-L01.png
   ls -lh assets/scenes/SCENE-00{1,2,3}.png
   ```
3. **校验三文件一致**  
   ```bash
   python3 ../../script/validate_rentgf_ep.py EP01
   ```
4. **Seedance 提交**（须用户授权扣费）→ 按 `EP01-SEG01` … `EP01-SEG13` 顺序  
5. **落盘** → `assets/generated/EP01/EP01-SEG##.mp4`
6. **拼接**  
   ```bash
   ffmpeg -f concat -safe 0 -i assets/generated/EP01/concat_list.txt -c copy assets/generated/EP01/EP01_full.mp4
   ```

## API 段一览

| segment_id | 秒 | 钩子/要点 |
|------------|-----|-----------|
| EP01-SEG01 | 12 | 催婚夜·点年伴 |
| EP01-SEG02 | 12 | 纯演戏别越界 |
| EP01-SEG03 | 11 | 失眠刷沈听主页 |
| EP01-SEG04 | 10 | 门铃·沈听上门 |
| EP01-SEG05 | 11 | 进门·照片一致 |
| EP01-SEG06 | 8 | 箱子·鞋套 |
| EP01-SEG07 | 12 | 签合同 |
| EP01-SEG08 | 7 | 平台存档拍照 |
| EP01-SEG09 | 12 | 八个月/十一个月 |
| EP01-SEG10 | 12 | 问卷背调 |
| EP01-SEG11 | 11 | 挂钟六点·睡沙发 |
| EP01-SEG12 | 12 | **体验分·熬粥** |
| EP01-SEG13 | 4 | 下集预告 |

## 注意

- 每段 `duration_sec` = 该段 `shot_ids` 时长之和（**skip 镜计 0 秒**；SEG13 仅黑屏字幕，API 仍报 4s）。
- 现代剧 **允许 smartphone**；负向词禁止 1990 年代物品。
- **禁止**向 `video/generated/` 或正式分镜路径写入占位 MP4。
