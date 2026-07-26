from pathlib import Path

code = r'''import csv
import html
import os
import uuid
from collections import Counter
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# 基本設定
# =========================================================

st.set_page_config(
    page_title="Music Personality",
    page_icon="🎵",
    layout="wide",
)

DATA_FILE = "music_records_v2.csv"

CSV_COLUMNS = [
    "id",
    "title",
    "artist",
    "category",
    "themes",
    "vibes",
    "favorite",
    "main_color",
    "sub_color",
    "created_at",
]


# =========================================================
# 曲の登録項目
# =========================================================

MUSIC_CATEGORIES = [
    "J-POP・邦楽",
    "K-POP",
    "洋楽ポップ",
    "ロック",
    "ヒップホップ・ラップ",
    "R&B・ソウル",
    "EDM・ダンス",
    "ジャズ",
    "クラシック",
    "アニソン",
    "ボーカロイド",
    "インディーズ",
    "映画・ドラマ音楽",
    "ゲーム音楽",
    "その他",
]

THEMES = [
    "恋愛",
    "失恋",
    "片思い",
    "友情",
    "応援・ファイトソング",
    "青春",
    "自己肯定",
    "夢・希望",
    "人生",
    "別れ",
    "家族",
    "孤独",
    "自由",
    "社会・メッセージ",
    "パーティー",
    "ドライブ",
    "作業・勉強",
    "睡眠・リラックス",
    "季節",
    "物語・世界観",
    "特にない・分からない",
]

VIBES = [
    "明るい",
    "楽しい",
    "爽やか",
    "元気が出る",
    "力強い",
    "かっこいい",
    "おしゃれ",
    "かわいい",
    "落ち着く",
    "チル",
    "ゆったり",
    "癒やされる",
    "エモい",
    "切ない",
    "感傷的",
    "泣ける",
    "懐かしい",
    "ロマンチック",
    "幻想的",
    "神秘的",
    "ダーク",
    "不穏",
    "激しい",
    "疾走感がある",
    "重い",
    "静か",
]


# =========================================================
# 音楽MBTI風診断ルール
# =========================================================

CATEGORY_SCORES = {
    "J-POP・邦楽": {"E": 1, "S": 1, "F": 1, "J": 1},
    "K-POP": {"E": 2, "S": 1, "F": 1, "P": 1},
    "洋楽ポップ": {"E": 2, "S": 1, "P": 1},
    "ロック": {"E": 1, "N": 1, "T": 1, "P": 1},
    "ヒップホップ・ラップ": {"E": 2, "S": 1, "T": 1, "P": 2},
    "R&B・ソウル": {"I": 1, "N": 1, "F": 2, "P": 1},
    "EDM・ダンス": {"E": 2, "S": 2, "T": 1, "P": 2},
    "ジャズ": {"I": 1, "N": 2, "T": 1, "P": 2},
    "クラシック": {"I": 2, "N": 1, "T": 2, "J": 2},
    "アニソン": {"E": 1, "N": 2, "F": 2, "P": 1},
    "ボーカロイド": {"I": 1, "N": 2, "T": 1, "P": 2},
    "インディーズ": {"I": 2, "N": 2, "F": 1, "P": 2},
    "映画・ドラマ音楽": {"I": 2, "N": 2, "F": 2, "J": 1},
    "ゲーム音楽": {"I": 1, "N": 2, "T": 1, "P": 1},
    "その他": {"I": 1, "N": 1, "F": 1, "P": 1},
}

THEME_SCORES = {
    "恋愛": {"F": 2, "N": 1},
    "失恋": {"I": 1, "F": 2, "N": 1},
    "片思い": {"I": 1, "F": 2, "N": 1},
    "友情": {"E": 1, "F": 2},
    "応援・ファイトソング": {"E": 2, "S": 1, "J": 1},
    "青春": {"E": 1, "F": 1, "P": 1},
    "自己肯定": {"E": 1, "F": 1, "J": 1},
    "夢・希望": {"N": 2, "F": 1, "J": 1},
    "人生": {"I": 1, "N": 2, "F": 1},
    "別れ": {"I": 2, "F": 2},
    "家族": {"F": 2, "J": 1},
    "孤独": {"I": 2, "N": 1},
    "自由": {"N": 1, "P": 2},
    "社会・メッセージ": {"N": 1, "T": 2, "J": 1},
    "パーティー": {"E": 2, "S": 1, "P": 2},
    "ドライブ": {"E": 1, "S": 1, "P": 1},
    "作業・勉強": {"I": 1, "T": 1, "J": 2},
    "睡眠・リラックス": {"I": 2, "F": 1, "P": 1},
    "季節": {"S": 2, "F": 1},
    "物語・世界観": {"I": 1, "N": 2, "F": 1},
    "特にない・分からない": {},
}

VIBE_SCORES = {
    "明るい": {"E": 2, "S": 1},
    "楽しい": {"E": 2, "P": 1},
    "爽やか": {"E": 1, "S": 2, "J": 1},
    "元気が出る": {"E": 2, "J": 1},
    "力強い": {"E": 1, "S": 1, "T": 2},
    "かっこいい": {"S": 1, "T": 2},
    "おしゃれ": {"N": 1, "T": 1, "P": 2},
    "かわいい": {"E": 1, "F": 2},
    "落ち着く": {"I": 2, "J": 1},
    "チル": {"I": 1, "P": 2},
    "ゆったり": {"I": 2, "P": 1},
    "癒やされる": {"I": 1, "F": 2},
    "エモい": {"I": 1, "N": 1, "F": 2},
    "切ない": {"I": 1, "N": 1, "F": 2},
    "感傷的": {"I": 2, "N": 1, "F": 2},
    "泣ける": {"I": 1, "F": 2},
    "懐かしい": {"I": 1, "S": 1, "F": 2},
    "ロマンチック": {"I": 1, "N": 1, "F": 2},
    "幻想的": {"I": 1, "N": 2, "F": 1},
    "神秘的": {"I": 1, "N": 2},
    "ダーク": {"I": 2, "N": 1, "T": 1},
    "不穏": {"I": 1, "N": 2, "T": 1},
    "激しい": {"E": 2, "S": 1, "P": 1},
    "疾走感がある": {"E": 2, "S": 2, "P": 1},
    "重い": {"I": 1, "T": 2, "J": 1},
    "静か": {"I": 2, "J": 1},
}


# =========================================================
# MBTI名称・説明・色
# =========================================================

TYPE_INFORMATION = {
    "INTJ": {
        "name": "建築家",
        "description": "曲の構成や世界観を深く味わい、自分なりの基準で音楽を選ぶタイプです。",
    },
    "INTP": {
        "name": "論理学者",
        "description": "独特な音や新しい表現に惹かれ、ジャンルを越えて音楽を探索するタイプです。",
    },
    "ENTJ": {
        "name": "指揮官",
        "description": "力強い音楽を好み、目的や場面に合わせて選曲するタイプです。",
    },
    "ENTP": {
        "name": "討論者",
        "description": "意外な曲や新しい組み合わせを楽しみ、幅広い音楽を試すタイプです。",
    },
    "INFJ": {
        "name": "提唱者",
        "description": "曲の物語や感情の流れを大切にし、深く共感できる音楽を選ぶタイプです。",
    },
    "INFP": {
        "name": "仲介者",
        "description": "切なさや幻想性など、心を動かす音楽を自分の思い出として大切にするタイプです。",
    },
    "ENFJ": {
        "name": "主人公",
        "description": "人と気持ちを共有できる音楽を好み、好きな曲を周囲にも紹介するタイプです。",
    },
    "ENFP": {
        "name": "運動家",
        "description": "新鮮な曲を積極的に探し、気分に合わせて多彩な音楽を楽しむタイプです。",
    },
    "ISTJ": {
        "name": "管理者",
        "description": "安心して聴ける定番曲を大切にし、目的別に音楽を整理するタイプです。",
    },
    "ISFJ": {
        "name": "擁護者",
        "description": "懐かしさや安心感のある曲を好み、音楽と思い出を結び付けるタイプです。",
    },
    "ESTJ": {
        "name": "幹部",
        "description": "分かりやすく力強い音楽を、作業や移動などの目的に合わせて選ぶタイプです。",
    },
    "ESFJ": {
        "name": "領事",
        "description": "親しみやすく明るい音楽を好み、人と共有して楽しむタイプです。",
    },
    "ISTP": {
        "name": "巨匠",
        "description": "音の質感やリズムの格好よさに注目し、音そのものを楽しむタイプです。",
    },
    "ISFP": {
        "name": "冒険家",
        "description": "曲の雰囲気や色彩を直感的に捉え、その時の感情に合う音楽を選ぶタイプです。",
    },
    "ESTP": {
        "name": "起業家",
        "description": "勢いやリズムを身体で感じ、ライブ映えする音楽を楽しむタイプです。",
    },
    "ESFP": {
        "name": "エンターテイナー",
        "description": "明るく盛り上がる曲を好み、音楽を通してその場の空気を楽しくするタイプです。",
    },
}

MBTI_COLORS = {
    "INTJ": "#6D4F63",
    "INTP": "#896A7A",
    "ENTJ": "#A57C92",
    "ENTP": "#8D79A6",
    "INFJ": "#66A287",
    "INFP": "#A7C876",
    "ENFJ": "#92AF6D",
    "ENFP": "#88C8AE",
    "ISTJ": "#5E9EB7",
    "ISFJ": "#7FBEC7",
    "ESTJ": "#7AB7CF",
    "ESFJ": "#66A8C1",
    "ISTP": "#B29339",
    "ISFP": "#DDCB5A",
    "ESTP": "#D38D4C",
    "ESFP": "#D98582",
}

INITIAL_HEADPHONE_COLOR = "#9CA3AF"


# =========================================================
# 画面CSS
# =========================================================

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1460px;
            padding-top: 1.4rem;
            padding-bottom: 3rem;
        }

        .main-title {
            font-size: clamp(38px, 4.3vw, 68px);
            font-weight: 800;
            line-height: 1.12;
            color: #444957;
            margin: 0 0 10px 0;
        }

        .main-sub {
            color: #6b7280;
            margin-bottom: 18px;
            line-height: 1.5;
        }

        .section-title {
            font-size: 26px;
            font-weight: 760;
            color: #2f3440;
            margin-bottom: 8px;
        }

        .helper-text {
            color: #6b7280;
            margin-bottom: 12px;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #ececec;
            padding: 10px;
            border-radius: 14px;
        }

        div[data-testid="stFeedback"] button {
            transform: scale(1.3);
            margin-right: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# セッション状態
# =========================================================

if "input_version" not in st.session_state:
    st.session_state.input_version = 0


# =========================================================
# CSV処理
# =========================================================

def ensure_data_file():
    if os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()


def load_records():
    ensure_data_file()
    records = []

    try:
        with open(DATA_FILE, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if not row.get("id"):
                    continue

                try:
                    row["favorite"] = int(row.get("favorite", 1))
                except ValueError:
                    row["favorite"] = 1

                row["themes"] = [
                    value
                    for value in row.get("themes", "").split("|")
                    if value
                ]

                row["vibes"] = [
                    value
                    for value in row.get("vibes", "").split("|")
                    if value
                ]

                records.append(row)

    except OSError:
        st.error("保存データの読み込みに失敗しました。")

    return records


def save_records(records):
    try:
        with open(DATA_FILE, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
            writer.writeheader()

            for record in records:
                row = record.copy()
                row["themes"] = "|".join(row.get("themes", []))
                row["vibes"] = "|".join(row.get("vibes", []))
                writer.writerow(row)

    except OSError:
        st.error("データを保存できませんでした。")


def add_record(
    title,
    artist,
    category,
    themes,
    vibes,
    favorite,
    main_color,
    sub_color,
):
    records = load_records()

    records.append(
        {
            "id": uuid.uuid4().hex,
            "title": title.strip(),
            "artist": artist.strip(),
            "category": category,
            "themes": list(themes),
            "vibes": list(vibes),
            "favorite": int(favorite),
            "main_color": main_color,
            "sub_color": sub_color,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
    )

    save_records(records)


def delete_record(record_id):
    records = load_records()
    records = [
        record
        for record in records
        if record["id"] != record_id
    ]
    save_records(records)


# =========================================================
# 配色処理
# =========================================================

def get_contrast_text_color(hex_color):
    color = hex_color.lstrip("#")

    if len(color) != 6:
        return "#FFFFFF"

    try:
        red = int(color[0:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:6], 16)
    except ValueError:
        return "#FFFFFF"

    brightness = (
        red * 299
        + green * 587
        + blue * 114
    ) / 1000

    return "#171717" if brightness >= 155 else "#FFFFFF"


def hex_to_rgba(hex_color, alpha):
    color = hex_color.lstrip("#")

    if len(color) != 6:
        return f"rgba(255,255,255,{alpha})"

    try:
        red = int(color[0:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:6], 16)
    except ValueError:
        return f"rgba(255,255,255,{alpha})"

    return f"rgba({red},{green},{blue},{alpha})"


# =========================================================
# レコードカード
# =========================================================

def create_record_card(record):
    title = html.escape(record["title"])
    artist = html.escape(record["artist"])
    category = html.escape(record["category"])

    themes = [
        html.escape(value)
        for value in record.get("themes", [])
    ]

    vibes = [
        html.escape(value)
        for value in record.get("vibes", [])
    ]

    main_color = record.get("main_color", "#F4C542")
    sub_color = record.get("sub_color", "#1A1A1A")

    main_text_color = get_contrast_text_color(main_color)
    sub_text_color = get_contrast_text_color(sub_color)

    favorite = max(1, min(5, int(record.get("favorite", 1))))
    stars = "★" * favorite + "☆" * (5 - favorite)

    visible_tags = [category] + themes[:2] + vibes[:2]

    tags_html = "".join(
        f'<span class="tag">{tag}</span>'
        for tag in visible_tags
    )

    if sub_text_color == "#171717":
        tag_background = "rgba(255,255,255,0.34)"
        tag_border = "rgba(0,0,0,0.28)"
    else:
        tag_background = "rgba(255,255,255,0.18)"
        tag_border = "rgba(255,255,255,0.42)"

    tonearm_color = (
        "#171717"
        if main_text_color == "#171717"
        else "#FFFFFF"
    )

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    * {{
        box-sizing: border-box;
        font-family: Arial, sans-serif;
    }}

    body {{
        margin: 0;
        padding: 0;
        background: transparent;
    }}

    .card-wrap {{
        width: 100%;
        height: 440px;
    }}

    .record-card {{
        width: 100%;
        height: 100%;
        position: relative;
        overflow: hidden;
        border-radius: 24px;
        background: {main_color};
        border: 1px solid rgba(0, 0, 0, 0.10);
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.14);
    }}

    .top-area {{
        position: absolute;
        inset: 0 0 42% 0;
        background: {main_color};
        overflow: hidden;
    }}

    .disc {{
        position: absolute;
        width: 72%;
        aspect-ratio: 1 / 1;
        left: 6%;
        top: 4%;
        border-radius: 50%;
        background:
            repeating-radial-gradient(
                circle,
                #141414 0,
                #141414 5px,
                #282828 6px,
                #282828 11px
            );
        border: 5px solid rgba(255, 255, 255, 0.82);
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.25);
    }}

    .label {{
        position: absolute;
        width: 31%;
        aspect-ratio: 1 / 1;
        left: 34.5%;
        top: 34.5%;
        border-radius: 50%;
        background: {sub_color};
        border: 4px solid rgba(255, 255, 255, 0.84);
    }}

    .hole {{
        position: absolute;
        width: 8%;
        aspect-ratio: 1 / 1;
        left: 46%;
        top: 46%;
        border-radius: 50%;
        background: {sub_text_color};
        z-index: 2;
    }}

    .tonearm-base {{
        position: absolute;
        width: 12%;
        aspect-ratio: 1 / 1;
        right: 4%;
        top: 4%;
        border-radius: 50%;
        background: {sub_color};
        border: 5px solid {hex_to_rgba(tonearm_color, 0.72)};
    }}

    .tonearm {{
        position: absolute;
        width: 8px;
        height: 48%;
        right: 14%;
        top: 12%;
        background: {tonearm_color};
        border-radius: 20px;
        transform: rotate(29deg);
        transform-origin: top center;
    }}

    .tonearm-head {{
        position: absolute;
        width: 12%;
        height: 7%;
        right: 21%;
        top: 49%;
        background: {tonearm_color};
        border-radius: 8px;
        transform: rotate(29deg);
    }}

    .info {{
        position: absolute;
        inset: 58% 0 0 0;
        background: {sub_color};
        padding: 15px 17px 14px;
        color: {sub_text_color};
        display: flex;
        flex-direction: column;
    }}

    .title {{
        font-size: 21px;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .artist {{
        font-size: 14px;
        opacity: 0.82;
        margin-bottom: 9px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .tags {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        max-height: 62px;
        overflow: hidden;
    }}

    .tag {{
        padding: 5px 9px;
        border-radius: 999px;
        font-size: 11px;
        line-height: 1;
        border: 1px solid {tag_border};
        background: {tag_background};
        color: {sub_text_color};
        white-space: nowrap;
    }}

    .stars {{
        margin-top: auto;
        font-size: 16px;
        letter-spacing: 2px;
        color: {sub_text_color};
    }}
</style>
</head>

<body>
    <div class="card-wrap">
        <div class="record-card">
            <div class="top-area">
                <div class="disc">
                    <div class="label"></div>
                    <div class="hole"></div>
                </div>

                <div class="tonearm-base"></div>
                <div class="tonearm"></div>
                <div class="tonearm-head"></div>
            </div>

            <div class="info">
                <div class="title">{title}</div>
                <div class="artist">{artist}</div>
                <div class="tags">{tags_html}</div>
                <div class="stars">{stars}</div>
            </div>
        </div>
    </div>
</body>
</html>
"""


def show_record_card(record):
    components.html(
        create_record_card(record),
        height=455,
        scrolling=False,
    )


# =========================================================
# 診断処理
# =========================================================

def add_scores(total_scores, source_scores, weight):
    for key, value in source_scores.items():
        total_scores[key] += value * weight


def calculate_music_type(records):
    scores = {
        "E": 0,
        "I": 0,
        "S": 0,
        "N": 0,
        "T": 0,
        "F": 0,
        "J": 0,
        "P": 0,
    }

    for record in records:
        weight = 0.6 + int(record["favorite"]) * 0.4

        add_scores(
            scores,
            CATEGORY_SCORES.get(record["category"], {}),
            weight,
        )

        for theme in record["themes"]:
            add_scores(
                scores,
                THEME_SCORES.get(theme, {}),
                weight,
            )

        for vibe in record["vibes"]:
            add_scores(
                scores,
                VIBE_SCORES.get(vibe, {}),
                weight,
            )

    type_code = (
        ("E" if scores["E"] >= scores["I"] else "I")
        + ("S" if scores["S"] >= scores["N"] else "N")
        + ("T" if scores["T"] >= scores["F"] else "F")
        + ("J" if scores["J"] >= scores["P"] else "P")
    )

    return type_code, scores


def calculate_axis_percentage(scores, left_key, right_key):
    left_score = scores[left_key]
    right_score = scores[right_key]
    total = left_score + right_score

    if total == 0:
        return 50, 50

    left_percentage = round(left_score / total * 100)
    return left_percentage, 100 - left_percentage


# =========================================================
# MBTIヘッドホン
# =========================================================

def create_mbti_hero(type_code, color):
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        margin: 0;
        padding: 0;
        background: transparent;
        font-family: Arial, sans-serif;
    }}

    .hero {{
        width: 100%;
        background: transparent;
    }}

    .title {{
        margin: 0 0 8px;
        color: #2f3440;
        font-size: 29px;
        font-weight: 800;
        line-height: 1.25;
    }}

    .sub {{
        margin-bottom: 8px;
        color: #6b7280;
        font-size: 14px;
    }}

    .icon-wrap {{
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
    }}

    svg {{
        width: 100%;
        max-width: 330px;
        height: auto;
        display: block;
    }}

    .type-text {{
        font-size: 38px;
        font-weight: 800;
        fill: {color};
    }}
</style>
</head>

<body>
    <div class="hero">
        <div class="title">あなたの音楽MBTI</div>
        <div class="sub">音楽の傾向からタイプを表示します</div>

        <div class="icon-wrap">
            <svg viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg">
                <path
                    d="M92 150 A88 88 0 0 1 268 150"
                    fill="none"
                    stroke="{color}"
                    stroke-width="18"
                    stroke-linecap="round"
                />

                <rect x="48" y="108" width="46" height="88" rx="18" fill="{color}" />
                <rect x="86" y="100" width="38" height="104" rx="16" fill="{color}" />
                <rect x="266" y="108" width="46" height="88" rx="18" fill="{color}" />
                <rect x="236" y="100" width="38" height="104" rx="16" fill="{color}" />

                <text
                    x="180"
                    y="152"
                    text-anchor="middle"
                    class="type-text"
                >
                    {type_code}
                </text>
            </svg>
        </div>
    </div>
</body>
</html>
"""


# =========================================================
# 左側：診断結果
# =========================================================

def show_mbti_panel(records):
    if not records:
        components.html(
            create_mbti_hero(
                "----",
                INITIAL_HEADPHONE_COLOR,
            ),
            height=280,
            scrolling=False,
        )

        st.info(
            "曲を登録すると、音楽の傾向から"
            "MBTI風のタイプが表示されます。"
        )
        return

    type_code, scores = calculate_music_type(records)
    type_info = TYPE_INFORMATION[type_code]
    type_color = MBTI_COLORS[type_code]

    components.html(
        create_mbti_hero(type_code, type_color),
        height=280,
        scrolling=False,
    )

    category_counter = Counter(
        record["category"]
        for record in records
    )

    theme_counter = Counter(
        theme
        for record in records
        for theme in record["themes"]
    )

    vibe_counter = Counter(
        vibe
        for record in records
        for vibe in record["vibes"]
    )

    top_category = category_counter.most_common(1)[0][0]

    top_theme = (
        theme_counter.most_common(1)[0][0]
        if theme_counter
        else "未登録"
    )

    top_vibe = (
        vibe_counter.most_common(1)[0][0]
        if vibe_counter
        else "未登録"
    )

    average_favorite = (
        sum(record["favorite"] for record in records)
        / len(records)
    )

    result_html = (
        f'<div style="border-left:7px solid {type_color};'
        f'padding-left:16px;margin-bottom:16px;">'
        f'<div style="color:{type_color};font-size:42px;'
        f'font-weight:800;line-height:1.1;">'
        f'{html.escape(type_code)}</div>'
        f'<div style="color:{type_color};font-size:21px;'
        f'font-weight:700;margin-top:7px;">'
        f'{html.escape(type_info["name"])}</div>'
        f'</div>'
    )

    st.markdown(result_html, unsafe_allow_html=True)
    st.write(type_info["description"])

    if len(records) < 5:
        st.caption(
            "※ 登録曲が5曲未満のため、現在は仮診断です。"
        )

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric("登録曲数", f"{len(records)}曲")

    with metric2:
        st.metric("最多区分", top_category)

    with metric3:
        st.metric("平均★", f"{average_favorite:.1f}")

    st.write("### 4つの音楽傾向")

    for left_key, right_key in [
        ("E", "I"),
        ("S", "N"),
        ("T", "F"),
        ("J", "P"),
    ]:
        left_percentage, right_percentage = calculate_axis_percentage(
            scores,
            left_key,
            right_key,
        )

        left_col, right_col = st.columns(2)

        with left_col:
            st.write(f"**{left_key} {left_percentage}%**")

        with right_col:
            st.markdown(
                (
                    '<div style="text-align:right;font-weight:700;">'
                    f'{right_percentage}% {right_key}'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

        st.progress(left_percentage / 100)

    st.write("### 音楽の傾向")
    st.write(f"**よく選ぶ区分**：{top_category}")
    st.write(f"**多いテーマ**：{top_theme}")
    st.write(f"**多い雰囲気**：{top_vibe}")

    st.caption(
        "この結果は、登録した音楽の区分・テーマ・雰囲気・"
        "お気に入り度を使ったアプリ独自のエンタメ診断です。"
    )


# =========================================================
# 星入力
# =========================================================

def show_star_input(version):
    if hasattr(st, "feedback"):
        selected_star = st.feedback(
            "stars",
            key=f"favorite_{version}",
        )

        if selected_star is None:
            return None

        return selected_star + 1

    selected = st.radio(
        "お気に入り度",
        options=[1, 2, 3, 4, 5],
        format_func=lambda value: "★" * value,
        horizontal=True,
        index=None,
        key=f"favorite_fallback_{version}",
    )

    return selected


# =========================================================
# 右側：曲登録フォーム
# =========================================================

def show_add_form():
    version = st.session_state.input_version

    st.markdown(
        '<div class="section-title">曲を登録する</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        (
            '<div class="helper-text">'
            "曲の内容や印象を選び、"
            "オリジナルのレコードカードを作成します。"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    # 入力欄は空欄
    # 「恋」「星野源」は入力例としてだけ表示
    title = st.text_input(
        "曲名",
        placeholder="例：恋",
        key=f"title_{version}",
    )

    artist = st.text_input(
        "アーティスト名",
        placeholder="例：星野源",
        key=f"artist_{version}",
    )

    category = st.selectbox(
        "音楽の区分",
        MUSIC_CATEGORIES,
        index=MUSIC_CATEGORIES.index("J-POP・邦楽"),
        key=f"category_{version}",
    )

    if hasattr(st, "pills"):
        themes = st.pills(
            "曲のテーマ（最大2つ）",
            THEMES,
            default=["恋愛"],
            selection_mode="multi",
            key=f"themes_{version}",
            width="stretch",
        )

        vibes = st.pills(
            "曲の雰囲気（最大3つ）",
            VIBES,
            default=["明るい", "楽しい"],
            selection_mode="multi",
            key=f"vibes_{version}",
            width="stretch",
        )
    else:
        themes = st.multiselect(
            "曲のテーマ（最大2つ）",
            THEMES,
            default=["恋愛"],
            key=f"themes_{version}",
        )

        vibes = st.multiselect(
            "曲の雰囲気（最大3つ）",
            VIBES,
            default=["明るい", "楽しい"],
            key=f"vibes_{version}",
        )

    st.write("#### お気に入り度")

    favorite = show_star_input(version)

    if favorite is None:
        st.caption(
            "星を押してお気に入り度を選択してください。"
        )
    else:
        st.caption(f"お気に入り度：{favorite} / 5")

    st.write("#### カードの配色")

    color_col1, color_col2 = st.columns(2)

    with color_col1:
        main_color = st.color_picker(
            "メインカラー",
            "#F4C542",
            key=f"main_color_{version}",
        )

    with color_col2:
        sub_color = st.color_picker(
            "サブカラー",
            "#1A1A1A",
            key=f"sub_color_{version}",
        )

    if st.button(
        "カードを追加する",
        type="primary",
        use_container_width=True,
        key=f"submit_{version}",
    ):
        errors = []

        if not title.strip():
            errors.append("曲名を入力してください。")

        if not artist.strip():
            errors.append("アーティスト名を入力してください。")

        if len(themes) == 0:
            errors.append(
                "曲のテーマを1つ以上選択してください。"
            )

        if len(themes) > 2:
            errors.append(
                "曲のテーマは最大2つまでです。"
            )

        if len(vibes) == 0:
            errors.append(
                "曲の雰囲気を1つ以上選択してください。"
            )

        if len(vibes) > 3:
            errors.append(
                "曲の雰囲気は最大3つまでです。"
            )

        if favorite is None:
            errors.append(
                "お気に入り度の星を選択してください。"
            )

        if errors:
            for error in errors:
                st.error(error)
        else:
            add_record(
                title=title,
                artist=artist,
                category=category,
                themes=themes,
                vibes=vibes,
                favorite=favorite,
                main_color=main_color,
                sub_color=sub_color,
            )

            st.session_state.input_version += 1
            st.rerun()


# =========================================================
# 右側：コレクション
# =========================================================

def show_collection(records):
    st.markdown(
        '<div class="section-title">コレクション</div>',
        unsafe_allow_html=True,
    )

    if not records:
        st.info(
            "まだ曲が登録されていません。"
            "上の入力欄から最初の1曲を追加してください。"
        )
        return

    category_filter = st.selectbox(
        "音楽の区分で絞り込む",
        ["すべて"] + MUSIC_CATEGORIES,
    )

    if category_filter == "すべて":
        filtered_records = records
    else:
        filtered_records = [
            record
            for record in records
            if record["category"] == category_filter
        ]

    filtered_records = list(reversed(filtered_records))

    st.caption(
        f"{len(filtered_records)}曲を表示しています。"
    )

    for start_index in range(
        0,
        len(filtered_records),
        2,
    ):
        row_records = filtered_records[
            start_index:start_index + 2
        ]

        columns = st.columns(2)

        for column, record in zip(columns, row_records):
            with column:
                show_record_card(record)

                if st.button(
                    "削除",
                    key=f"delete_{record['id']}",
                    use_container_width=True,
                ):
                    delete_record(record["id"])
                    st.rerun()


# =========================================================
# アプリ本体
# =========================================================

ensure_data_file()

st.markdown(
    '<div class="main-title">Music Personality</div>',
    unsafe_allow_html=True,
)

st.markdown(
    (
        '<div class="main-sub">'
        "好きな曲をレコードカードとして集めながら、"
        "音楽の傾向からMBTI風タイプを楽しむアプリ"
        "</div>"
    ),
    unsafe_allow_html=True,
)

with st.expander("MBTIとは？"):
    st.write(
        """
MBTIは、人の考え方や行動の傾向を、
4つの指標の組み合わせによって16タイプに分類する考え方です。

- **E / I**：外向型・内向型
- **S / N**：感覚型・直観型
- **T / F**：思考型・感情型
- **J / P**：判断型・知覚型

例えば「ESFP」は、E・S・F・Pの
4つの傾向を組み合わせたタイプを表します。

このアプリでは、通常の質問式診断ではなく、
登録した曲の区分・テーマ・雰囲気・お気に入り度をもとに、
音楽の好みを16タイプ風に分類します。
        """
    )

    st.caption(
        "この結果は性格や能力を医学的・心理学的に"
        "判定するものではなく、音楽の好みを楽しむための"
        "エンタメ診断です。"
    )

records = load_records()

left_column, right_column = st.columns(
    [1.05, 1.95],
    gap="large",
)

with left_column:
    show_mbti_panel(records)

with right_column:
    show_add_form()

    records = load_records()

    st.divider()
    show_collection(records)
'''

path = Path("/mnt/data/test.py")
path.write_text(code, encoding="utf-8")
print(path)
