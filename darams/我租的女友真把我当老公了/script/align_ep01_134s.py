#!/usr/bin/env python3
"""Align EP01 to 超雄 EP01: 32 shots, 134s API, 13 segments."""
from __future__ import annotations

import copy
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EP_DIR = ROOT / "剧本" / "EP01"
SUFFIX = (
    "2020年代中国都市/小城，写实短剧，竖屏9比16，"
    "对白时画面底部居中简体白字字幕与语音同步；禁止其它乱字"
)

# old shot_id -> new shot_id (S01-S07 unchanged)
RENUM = {}
for i in range(1, 8):
    RENUM[f"EP01-S{i:02d}"] = f"EP01-S{i:02d}"
for old, new in [
    (8, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (12, 14),
    (13, 15),
    (14, 16),
    (15, 17),
    (16, 18),
    (17, 19),
    (18, 21),
    (19, 22),
    (20, 23),
    (21, 24),
    (22, 25),
    (23, 26),
    (24, 28),
    (25, 29),
    (26, 30),
    (27, 31),
    (28, 32),
]:
    RENUM[f"EP01-S{old:02d}"] = f"EP01-S{new:02d}"


def renum_id(sid: str) -> str:
    return RENUM.get(sid, sid)


NEW_SHOTS = [
    {
        "after_old": "EP01-S07",
        "new_id": "EP01-S08",
        "shot_no": 8,
        "duration_sec": 7,
        "seg_comment": "SEG03 失眠刷资料",
        "scene_id": "SCENE-001",
        "characters": ["CHAR-001"],
        "look_ids": ["CHAR-001-L01"],
        "api_text": (
            "【图1】CHAR-001-L01【图2】SCENE-001。固定镜头，近景，程野关灯后手机又亮起，"
            "刷年伴APP沈听主页：五星评价与用户留言「很体贴」；台灯暖光映脸。\n"
            "对白（程野，内心，29岁略疲惫）：「她照片……笑得太标准了。」「真人上门，会不会更假？」\n"
            + SUFFIX
        ),
        "dialogue": [
            {"speaker": "CHAR-001", "text": "她照片……笑得太标准了。", "note": "内心"},
            {"speaker": "CHAR-001", "text": "真人上门，会不会更假？", "note": "内心"},
        ],
    },
    {
        "after_old": "EP01-S11",
        "new_id": "EP01-S13",
        "shot_no": 13,
        "duration_sec": 7,
        "seg_comment": "SEG05 进门换鞋",
        "scene_id": "SCENE-002",
        "characters": ["CHAR-001", "CHAR-002"],
        "look_ids": ["CHAR-001-L02", "CHAR-002-L01"],
        "api_text": (
            "【图1】CHAR-001-L02【图2】CHAR-002-L01【图3】SCENE-002。跟拍，中景，"
            "沈听换好鞋套迈进门，目光扫过整洁玄关与略乱客厅；程野侧身让路。\n"
            "对白（沈听，26岁温柔专业）：「照片和实景一致，我记下了。」\n"
            "对白（程野，内心）：「她连乱不乱都要评估？」\n" + SUFFIX
        ),
        "dialogue": [
            {"speaker": "CHAR-002", "text": "照片和实景一致，我记下了。"},
            {"speaker": "CHAR-001", "text": "她连乱不乱都要评估？", "note": "内心"},
        ],
    },
    {
        "after_old": "EP01-S17",
        "new_id": "EP01-S20",
        "shot_no": 20,
        "duration_sec": 7,
        "seg_comment": "SEG08 合同存档",
        "scene_id": "SCENE-003",
        "characters": ["CHAR-001", "CHAR-002"],
        "look_ids": ["CHAR-001-L02", "CHAR-002-L01"],
        "api_text": (
            "【图1】CHAR-002-L01【图2】CHAR-001-L02【图3】SCENE-003。固定镜头，中景，"
            "沈听用手机拍合同签字页，屏幕闪光；程野签字笔还停在半空。\n"
            "对白（沈听）：「平台存档，对您也有保障。」\n"
            "对白（程野，内心）：「……你连这个都专业。」\n" + SUFFIX
        ),
        "dialogue": [
            {"speaker": "CHAR-002", "text": "平台存档，对您也有保障。"},
            {"speaker": "CHAR-001", "text": "……你连这个都专业。", "note": "内心"},
        ],
    },
    {
        "after_old": "EP01-S23",
        "new_id": "EP01-S27",
        "shot_no": 27,
        "duration_sec": 6,
        "seg_comment": "SEG11 六点前奏",
        "scene_id": "SCENE-003",
        "characters": ["CHAR-001"],
        "look_ids": ["CHAR-001-L02"],
        "api_text": (
            "【图1】CHAR-001-L02【图2】SCENE-003。固定镜头，中景，程野走到厨房门口，"
            "墙上挂钟五点五十分；空电饭煲放在台面上。\n"
            "对白（程野，内心）：「六点熬粥……她当真？」「我竟一句反驳都没说出口。」\n"
            + SUFFIX
        ),
        "dialogue": [
            {"speaker": "CHAR-001", "text": "六点熬粥……她当真？", "note": "内心"},
            {"speaker": "CHAR-001", "text": "我竟一句反驳都没说出口。", "note": "内心"},
        ],
    },
]


def make_shot(spec: dict) -> dict:
    chars = spec["characters"]
    looks = spec["look_ids"]
    scene = spec["scene_id"]
    assets: dict = {"scene_urls": {scene: f"assets/scenes/{scene}.png"}}
    if len(chars) == 1 and len(looks) == 1:
        assets["look_urls"] = {looks[0]: f"assets/looks/{looks[0]}.png"}
    else:
        assets["look_urls"] = {lid: f"assets/looks/{lid}.png" for lid in looks}
    roles = []
    for idx, lid in enumerate(looks, 1):
        roles.append({"file": lid, "role": "reference_image", "label": f"图{idx}"})
    roles.append({"file": scene, "role": "reference_image", "label": f"图{len(roles)}"})

    shot = {
        "shot_id": spec["new_id"],
        "shot_no": spec["shot_no"],
        "mode": "i2v_ref",
        "duration_sec": spec["duration_sec"],
        "scene_id": scene,
        "characters": chars,
        "look_ids": looks,
        "refs": {"scene_id": scene, "look_ids": looks},
        "assets": assets,
        "api": {
            "text": spec["api_text"],
            "content_roles": roles,
            "return_last_frame": True,
        },
        "dialogue": spec["dialogue"],
    }
    return shot


def transform_shots(data: dict) -> dict:
    old_shots = data["shots"]
    new_list: list[dict] = []

    for old in old_shots:
        oid = old["shot_id"]
        if oid == "EP01-S08":
            s = copy.deepcopy(old)
            s["shot_id"] = "EP01-S09"
            s["shot_no"] = 9
            new_list.append(s)
            continue
        if oid == "EP01-S09":
            s = copy.deepcopy(old)
            s["shot_id"] = "EP01-S10"
            s["shot_no"] = 10
            new_list.append(s)
            continue

        shot = copy.deepcopy(old)
        shot["shot_id"] = renum_id(oid)
        shot["shot_no"] = int(shot["shot_id"].split("-S")[1])
        if shot.get("mode") == "skip" and "note" in shot:
            shot["note"] = shot["note"].replace("EP01-SEG11", "EP01-SEG13")
        if "api" in shot and shot.get("mode") != "skip":
            shot["api"]["return_last_frame"] = True
        new_list.append(shot)
        for spec in NEW_SHOTS:
            if spec["after_old"] == oid:
                new_list.append(make_shot(spec))

    data["shots"] = new_list
    return data


SEGMENTS_SPEC = [
    ("EP01-SEG01", "催婚夜", [f"EP01-S{i:02d}" for i in range(1, 4)], 12),
    ("EP01-SEG02", "下单备注", ["EP01-S04", "EP01-S05", "EP01-S06"], 12),
    ("EP01-SEG03", "订单不安", ["EP01-S07", "EP01-S08"], 11),
    ("EP01-SEG04", "次日门铃", ["EP01-S09", "EP01-S10", "EP01-S11", "EP01-S12"], 10),
    ("EP01-SEG05", "进门换鞋", ["EP01-S13", "EP01-S14"], 11),
    ("EP01-SEG06", "箱子对峙", ["EP01-S15", "EP01-S16"], 8),
    ("EP01-SEG07", "签合同", ["EP01-S17", "EP01-S18", "EP01-S19"], 12),
    ("EP01-SEG08", "合同存档", ["EP01-S20"], 7),
    ("EP01-SEG09", "人物设定", ["EP01-S21", "EP01-S22", "EP01-S23"], 12),
    ("EP01-SEG10", "问卷背调", ["EP01-S24", "EP01-S25", "EP01-S26"], 12),
    ("EP01-SEG11", "睡沙发", ["EP01-S27", "EP01-S28"], 11),
    ("EP01-SEG12", "熬粥体验分", ["EP01-S29", "EP01-S30", "EP01-S31"], 12),
    ("EP01-SEG13", "下集预告", ["EP01-S32"], 4),
]


def build_segments(old_segs: list, shot_map: dict) -> list:
    """Merge old segment api text; patch shot_ids and add new segments."""
    old_by_title = {s["title"]: s for s in old_segs}
    title_map = {
        "催婚夜": "催婚夜",
        "下单备注": "下单备注",
        "订单不安": "订单不安",
        "次日门铃": "次日门铃",
        "进门换鞋": None,
        "箱子对峙": "箱子对峙",
        "签合同": "签合同",
        "合同存档": None,
        "人物设定": "人物设定",
        "问卷背调": "问卷背调",
        "睡沙发": "睡沙发",
        "熬粥体验分": "熬粥体验分",
        "下集预告": "下集预告",
    }
    new_segments = []
    for seg_id, title, shot_ids, dur in SEGMENTS_SPEC:
        base = None
        if title == "进门换鞋":
            base = copy.deepcopy(old_by_title["箱子对峙"])
            base["title"] = "进门换鞋"
            base["dialogue_lines"] = [
                {"speaker": "CHAR-002", "emotion": "专业", "text": "照片和实景一致，我记下了。"},
                {"speaker": "CHAR-001", "emotion": "内心", "text": "她连乱不乱都要评估？"},
                {"speaker": "CHAR-001", "emotion": "嘴硬", "text": "就七天……不用真搬。"},
                {"speaker": "CHAR-002", "emotion": "笃定", "text": "合同写全程陪同，我专业。"},
            ]
            base["api"]["text"] = (
                "【图1】程野【图2】沈听【图3】玄关 SCENE-002。\n"
                "镜头1（7秒）跟拍：沈听换鞋套进门，目光扫玄关与客厅；程野侧身。\n"
                "对白（沈听）：「照片和实景一致，我记下了。」\n"
                "对白（程野，内心）：「她连乱不乱都要评估？」\n"
                "镜头2（4秒）中景：两人隔门槛，箱轮压地，走廊日光。\n"
                "对白（程野）：「就七天……不用真搬。」\n"
                "对白（沈听）：「合同写全程陪同，我专业。」\n" + SUFFIX
            )
        elif title == "合同存档":
            base = copy.deepcopy(old_by_title["签合同"])
            base["title"] = "合同存档"
            base["characters"] = ["CHAR-001", "CHAR-002"]
            base["dialogue_lines"] = [
                {"speaker": "CHAR-002", "emotion": "公事", "text": "平台存档，对您也有保障。"},
                {"speaker": "CHAR-001", "emotion": "内心", "text": "……你连这个都专业。"},
            ]
            base["api"]["text"] = (
                "【图1】沈听【图2】程野【图3】客厅 SCENE-003。\n"
                "镜头（7秒）中景：沈听用手机拍合同签字页，屏幕闪光；程野签字笔停在半空。\n"
                "对白（沈听）：「平台存档，对您也有保障。」\n"
                "对白（程野，内心）：「……你连这个都专业。」\n" + SUFFIX
            )
        elif title == "睡沙发" and dur == 11:
            base = copy.deepcopy(old_by_title["睡沙发"])
            base["title"] = "睡沙发"
            base["characters"] = ["CHAR-001", "CHAR-002"]
            base["looks"] = ["CHAR-001-L02", "CHAR-002-L01"]
            base["dialogue_lines"] = [
                {"speaker": "CHAR-001", "emotion": "内心", "text": "六点熬粥……她当真？"},
                {"speaker": "CHAR-001", "emotion": "内心", "text": "我竟一句反驳都没说出口。"},
                {"speaker": "CHAR-002", "emotion": "利落", "text": "今晚我睡沙发。行李不动，方便明天出发。"},
            ]
            base["api"]["text"] = (
                "【图1】程野【图2】沈听【图3】客厅 SCENE-003。\n"
                "镜头1（6秒）中景：程野站厨房门口，挂钟五点五十分，空电饭煲。\n"
                "对白（程野，内心）：「六点熬粥……她当真？」「我竟一句反驳都没说出口。」\n"
                "镜头2（5秒）中景：沈听合上本子，在沙发铺薄毯，动作利落。\n"
                "对白（沈听）：「今晚我睡沙发。行李不动，方便明天出发。」\n" + SUFFIX
            )
            base["assets"]["look_urls"] = {
                "CHAR-001-L02": "assets/looks/CHAR-001-L02.png",
                "CHAR-002-L01": "assets/looks/CHAR-002-L01.png",
            }
        elif title == "订单不安":
            base = copy.deepcopy(old_by_title["订单不安"])
            base["dialogue_lines"] = list(base["dialogue_lines"]) + [
                {"speaker": "CHAR-001", "emotion": "疑虑", "text": "她照片……笑得太标准了。"},
                {"speaker": "CHAR-001", "emotion": "自我安慰", "text": "真人上门，会不会更假？"},
            ]
            base["api"]["text"] = (
                "【图1】程野【图2】出租屋 SCENE-001。\n"
                "镜头1（4秒）近景：订单详情沈听头像、高评分、标签「全程陪同」「擅长家宴」。\n"
                "对白（程野，内心）：「全程陪同……别是打算住我家吧。」「算了，反正只七天。」\n"
                "镜头2（7秒）近景：关灯后手机又亮，刷沈听主页五星与留言「很体贴」。\n"
                "对白（程野，内心）：「她照片……笑得太标准了。」「真人上门，会不会更假？」\n"
                + SUFFIX
            )
        elif title == "箱子对峙":
            base = copy.deepcopy(old_by_title["箱子对峙"])
            base["dialogue_lines"] = [
                {"speaker": "CHAR-002", "emotion": "体贴", "text": "玄关我看过照片，先换鞋套，不给您添乱。"},
                {"speaker": "CHAR-001", "emotion": "狐疑", "text": "这箱子……像真搬家。"},
                {"speaker": "CHAR-001", "emotion": "警惕", "text": "别是打算赖七天不走吧。"},
            ]
            base["api"]["text"] = (
                "【图1】沈听【图2】程野【图3】玄关 SCENE-002。\n"
                "镜头1（4秒）特写：沈听递鞋套袋，目光温和笃定。\n"
                "对白（沈听）：「玄关我看过照片，先换鞋套，不给您添乱。」\n"
                "镜头2（4秒）近景：程野侧身让路，眼神打量行李箱。\n"
                "对白（程野，内心）：「这箱子……像真搬家。」「别是打算赖七天不走吧。」\n"
                + SUFFIX
            )
        elif title == "下集预告":
            base = copy.deepcopy(old_by_title["下集预告"])
            base["api"]["text"] = base["api"]["text"].replace("EP01-S28", "EP01-S32")
        else:
            src_title = title_map.get(title, title)
            if src_title and src_title in old_by_title:
                base = copy.deepcopy(old_by_title[src_title])
            else:
                raise KeyError(title)
        base["segment_id"] = seg_id
        base["title"] = title
        base["shot_ids"] = shot_ids
        base["duration_sec"] = dur
        new_segments.append(base)
    return new_segments


def main() -> None:
    shots_path = EP_DIR / "EP01_shots.yaml"
    segs_path = EP_DIR / "EP01_segments.yaml"
    shots_data = yaml.safe_load(shots_path.read_text(encoding="utf-8"))
    segs_data = yaml.safe_load(segs_path.read_text(encoding="utf-8"))

    shots_data = transform_shots(shots_data)
    shot_map = {s["shot_id"]: s for s in shots_data["shots"]}

    # rewrite yaml header comment
    text = shots_path.read_text(encoding="utf-8")
    header = "# EP01 shots — 29 effective + 3 skip, 13 API segments · 134s\n"
    body = yaml.dump(
        {k: v for k, v in shots_data.items() if k != "shots"},
        allow_unicode=True,
        sort_keys=False,
    )
    shots_yaml = header + body + "shots:\n"
    for shot in shots_data["shots"]:
        shots_yaml += yaml.dump([shot], allow_unicode=True, sort_keys=False).replace("- ", "  - ", 1)
        # fix: dump as list item under shots
    # simpler: full dump
    out_shots = {
        "episode_id": "EP01",
        "source_md": "剧本/EP01/EP01_下单.md",
        **{k: v for k, v in shots_data.items() if k not in ("episode_id", "source_md", "shots")},
        "shots": shots_data["shots"],
    }
    shots_content = "# EP01 shots — 29 effective + 3 skip, 13 API segments · 134s\n"
    shots_content += yaml.dump(out_shots, allow_unicode=True, sort_keys=False, width=1000)

    shots_path.write_text(shots_content, encoding="utf-8")

    new_segs = build_segments(segs_data["segments"], shot_map)
    segs_out = {
        k: v
        for k, v in segs_data.items()
        if k != "segments"
    }
    segs_out["segments"] = new_segs
    seg_header = (
        "# EP01 segments — 13 submissions (4–12s each); 有效镜29 + skip3 · 134s\n"
        "# submit: 按 segment_id 顺序；duration_sec 须与 shot 时长之和一致（skip 镜=0）\n"
    )
    segs_content = seg_header + yaml.dump(segs_out, allow_unicode=True, sort_keys=False)
    segs_path.write_text(segs_content, encoding="utf-8")

    total = sum(s["duration_sec"] for s in new_segs)
    print(f"shots: {len(shots_data['shots'])}, segments: {len(new_segs)}, total {total}s")


if __name__ == "__main__":
    main()
