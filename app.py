import random
import streamlit as st

st.set_page_config(
    page_title="クリック迷路ゲーム",
    layout="centered",
)

# =========================================================
# レベル設定
# cell_rows, cell_cols は「迷路の部屋数」
# 実際に表示されるブロック迷路サイズは
# (cell_rows*2+1) × (cell_cols*2+1)
# =========================================================

LEVEL_SETTINGS = {
    1: {"cell_rows": 4, "cell_cols": 4, "name": "かんたん"},
    2: {"cell_rows": 5, "cell_cols": 5, "name": "初級"},
    3: {"cell_rows": 6, "cell_cols": 6, "name": "中級"},
    4: {"cell_rows": 7, "cell_cols": 7, "name": "上級"},
    5: {"cell_rows": 8, "cell_cols": 8, "name": "最難関"},
}


# =========================================================
# 迷路生成
# 0 = 通路
# 1 = 壁
# DFS風に通路を掘る方法で生成
# =========================================================

def generate_maze(cell_rows, cell_cols):
    rows = cell_rows * 2 + 1
    cols = cell_cols * 2 + 1

    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    # 奇数マスを部屋候補として使用
    start_r, start_c = 1, 1
    maze[start_r][start_c] = 0

    stack = [(start_r, start_c)]
    visited = {(start_r, start_c)}

    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        r, c = stack[-1]

        candidates = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1:
                if (nr, nc) not in visited:
                    candidates.append((nr, nc, dr, dc))

        if candidates:
            nr, nc, dr, dc = random.choice(candidates)

            # 間の壁を壊す
            wall_r = r + dr // 2
            wall_c = c + dc // 2

            maze[wall_r][wall_c] = 0
            maze[nr][nc] = 0

            visited.add((nr, nc))
            stack.append((nr, nc))
        else:
            stack.pop()

    # 上端にスタート入口、下端にゴール出口を作る
    odd_cols = [c for c in range(1, cols - 1, 2)]
    start_col = random.choice(odd_cols)
    goal_col = random.choice(odd_cols)

    maze[0][start_col] = 0
    maze[rows - 1][goal_col] = 0

    start_pos = [1, start_col]          # プレイヤー開始位置（迷路内）
    goal_pos = [rows - 2, goal_col]     # ゴール位置（迷路内）

    return maze, start_pos, goal_pos, start_col, goal_col


# =========================================================
# 初期化
# =========================================================

def initialize_game(level):
    setting = LEVEL_SETTINGS[level]
    maze, start_pos, goal_pos, start_gate_col, goal_gate_col = generate_maze(
        setting["cell_rows"],
        setting["cell_cols"],
    )

    st.session_state.level = level
    st.session_state.maze = maze
    st.session_state.player = start_pos.copy()
    st.session_state.start = start_pos.copy()
    st.session_state.goal = goal_pos.copy()
    st.session_state.start_gate_col = start_gate_col
    st.session_state.goal_gate_col = goal_gate_col
    st.session_state.steps = 0
    st.session_state.cleared = False
    st.session_state.message = "上側の入口からスタートして、下側の出口を目指してください。"
    st.session_state.visited = {tuple(start_pos)}


if "level" not in st.session_state:
    initialize_game(1)


# =========================================================
# 移動処理
# =========================================================

def move_player(dr, dc):
    if st.session_state.cleared:
        return

    r, c = st.session_state.player
    nr, nc = r + dr, c + dc
    maze = st.session_state.maze

    if not (0 <= nr < len(maze) and 0 <= nc < len(maze[0])):
        st.session_state.message = "迷路の外には進めません。"
        return

    if maze[nr][nc] == 1:
        st.session_state.message = "そこには壁があります。"
        return

    st.session_state.player = [nr, nc]
    st.session_state.steps += 1
    st.session_state.visited.add((nr, nc))
    st.session_state.message = "移動しました。"

    if st.session_state.player == st.session_state.goal:
        st.session_state.cleared = True
        st.session_state.message = (
            f"レベル{st.session_state.level}クリア！ "
            f"移動回数は {st.session_state.steps} 回です。"
        )


# =========================================================
# 迷路表示
# 「見える範囲だけ表示」で答えが見えにくくなる
# =========================================================

def create_maze_html(show_fog=True, vision_radius=2):
    maze = st.session_state.maze
    player_r, player_c = st.session_state.player
    goal_r, goal_c = st.session_state.goal
    start_gate_col = st.session_state.start_gate_col
    goal_gate_col = st.session_state.goal_gate_col
    visited = st.session_state.visited

    rows = len(maze)
    cols = len(maze[0])

    # 迷路が大きくなっても収まりやすいようにセルサイズを少し可変に
    if cols <= 9:
        cell_size = 34
    elif cols <= 13:
        cell_size = 28
    else:
        cell_size = 24

    cells = []

    for r in range(rows):
        for c in range(cols):
            # 見えるかどうか
            distance = abs(r - player_r) + abs(c - player_c)
            visible_now = distance <= vision_radius
            already_seen = (r, c) in visited

            if show_fog and not visible_now and not already_seen:
                cell_class = "unknown"
                content = ""
            else:
                if maze[r][c] == 1:
                    cell_class = "wall"
                    content = ""
                else:
                    cell_class = "path"
                    content = ""

                    if show_fog and not visible_now and already_seen:
                        cell_class = "seen-path"

            # スタート入口とゴール出口の見た目
            if r == 0 and c == start_gate_col:
                if not (show_fog and not visible_now and not already_seen):
                    cell_class = "start-gate"

            if r == rows - 1 and c == goal_gate_col:
                if not (show_fog and not visible_now and not already_seen):
                    cell_class = "goal-gate"

            # ゴール
            if [r, c] == [goal_r, goal_c]:
                if not (show_fog and not visible_now and not already_seen):
                    cell_class = "goal"
                    content = '<div class="goal-dot"></div>'

            # プレイヤー
            if [r, c] == [player_r, player_c]:
                cell_class = "player-cell"
                content = '<div class="player-dot"></div>'

            cells.append(f'<div class="cell {cell_class}">{content}</div>')

    html = f"""
    <style>
        .maze-wrapper {{
            width: 100%;
            overflow-x: auto;
            display: flex;
            justify-content: center;
            margin-top: 18px;
            margin-bottom: 18px;
        }}

        .maze-board {{
            display: grid;
            grid-template-columns: repeat({cols}, {cell_size}px);
            gap: 2px;
            background: #d1d5db;
            padding: 6px;
            border-radius: 10px;
        }}

        .cell {{
            width: {cell_size}px;
            height: {cell_size}px;
            box-sizing: border-box;
            border-radius: 3px;
        }}

        .wall {{
            background: #111827;
        }}

        .path {{
            background: #f9fafb;
        }}

        .seen-path {{
            background: #e5e7eb;
        }}

        .unknown {{
            background: #9ca3af;
        }}

        .start-gate {{
            background: #bfdbfe;
        }}

        .goal-gate {{
            background: #bbf7d0;
        }}

        .goal {{
            background: #dcfce7;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .goal-dot {{
            width: 40%;
            height: 40%;
            border-radius: 50%;
            border: 3px solid #15803d;
            background: transparent;
        }}

        .player-cell {{
            background: #dbeafe;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .player-dot {{
            width: 52%;
            height: 52%;
            border-radius: 50%;
            background: #2563eb;
            border: 2px solid white;
        }}

        .maze-label {{
            text-align: center;
            font-size: 14px;
            color: #374151;
            margin-bottom: 6px;
        }}
    </style>

    <div class="maze-label">上がスタート入口 / 下がゴール出口</div>
    <div class="maze-wrapper">
        <div class="maze-board">
            {''.join(cells)}
        </div>
    </div>
    """
    return html


# =========================================================
# 画面
# =========================================================

st.title("クリック迷路ゲーム")

level = st.session_state.level
setting = LEVEL_SETTINGS[level]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("レベル", f"{level} / 5")
with col2:
    st.metric("難易度", setting["name"])
with col3:
    st.metric("移動回数", st.session_state.steps)

selected_level = st.select_slider(
    "挑戦するレベル",
    options=[1, 2, 3, 4, 5],
    value=level,
)

if selected_level != level:
    initialize_game(selected_level)
    st.rerun()

show_fog = st.checkbox("見える範囲だけ表示にする", value=True)

st.markdown(
    create_maze_html(show_fog=show_fog, vision_radius=2),
    unsafe_allow_html=True,
)

if st.session_state.cleared:
    st.success(st.session_state.message)
else:
    st.info(st.session_state.message)


# =========================================================
# 操作ボタン
# =========================================================

space_left, up_col, space_right = st.columns(3)

with up_col:
    st.button(
        "↑",
        use_container_width=True,
        on_click=move_player,
        args=(-1, 0),
        disabled=st.session_state.cleared,
    )

left_col, down_col, right_col = st.columns(3)

with left_col:
    st.button(
        "←",
        use_container_width=True,
        on_click=move_player,
        args=(0, -1),
        disabled=st.session_state.cleared,
    )

with down_col:
    st.button(
        "↓",
        use_container_width=True,
        on_click=move_player,
        args=(1, 0),
        disabled=st.session_state.cleared,
    )

with right_col:
    st.button(
        "→",
        use_container_width=True,
        on_click=move_player,
        args=(0, 1),
        disabled=st.session_state.cleared,
    )


# =========================================================
# 管理ボタン
# =========================================================

st.divider()

reset_col, next_col = st.columns(2)

with reset_col:
    if st.button("同じレベルを作り直す", use_container_width=True):
        initialize_game(st.session_state.level)
        st.rerun()

with next_col:
    can_next = st.session_state.cleared and st.session_state.level < 5
    if st.button(
        "次のレベルへ",
        use_container_width=True,
        disabled=not can_next,
    ):
        initialize_game(st.session_state.level + 1)
        st.rerun()

if st.session_state.cleared and st.session_state.level == 5:
    st.balloons()
    st.success("全5レベルをクリアしました！")