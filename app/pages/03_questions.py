"""
页面 3: 面试题库
展示生成的面试题，支持闪卡翻转查看答案
"""

import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到 sys.path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from app.utils.ui_components import (
    apply_apple_style,
    render_progress_indicator,
    render_flashcard
)
from models.schemas import QuestionType, DifficultyLevel

# ── 页面配置 ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="面试题库 - AI 面试助手",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

apply_apple_style()

# ── 进度指示器 ───────────────────────────────────────────────────
render_progress_indicator(current_step=3)

# ── 检查前置条件 ─────────────────────────────────────────────────
if 'questions' not in st.session_state or st.session_state.questions is None:
    st.error("请先生成面试题")
    if st.button("返回分析页面"):
        st.switch_page("pages/02_analysis.py")
    st.stop()

# ── 页面标题 ─────────────────────────────────────────────────────
questions_list = st.session_state.questions.questions
total_questions = len(questions_list)

st.markdown(f"""
<div style="text-align: center; margin: 2rem 0 2.5rem;">
    <h1 style="font-size: 2rem; font-weight: 600; color: #1C1C1E;">个性化面试题</h1>
    <p style="color: #6C6C70; font-size: 1rem;">共 {total_questions} 题 · 点击按钮翻转查看答案</p>
</div>
""", unsafe_allow_html=True)

# ── 初始化 Session State ────────────────────────────────────────
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'flipped_states' not in st.session_state:
    st.session_state.flipped_states = {}
if 'filter_type' not in st.session_state:
    st.session_state.filter_type = "全部"
if 'filter_difficulty' not in st.session_state:
    st.session_state.filter_difficulty = "全部"

# ── 筛选功能 ─────────────────────────────────────────────────────
st.markdown("### 筛选题目")

col1, col2 = st.columns(2)

with col1:
    type_options = ["全部"] + [t.value for t in QuestionType]
    selected_type = st.selectbox(
        "题目类型",
        options=type_options,
        index=type_options.index(st.session_state.filter_type),
        key='type_filter'
    )
    st.session_state.filter_type = selected_type

with col2:
    difficulty_options = ["全部"] + [d.value for d in DifficultyLevel]
    selected_difficulty = st.selectbox(
        "难度级别",
        options=difficulty_options,
        index=difficulty_options.index(st.session_state.filter_difficulty),
        key='difficulty_filter'
    )
    st.session_state.filter_difficulty = selected_difficulty

# 应用筛选
filtered_questions = questions_list

if st.session_state.filter_type != "全部":
    filtered_questions = [
        q for q in filtered_questions 
        if q.question_type.value == st.session_state.filter_type
    ]

if st.session_state.filter_difficulty != "全部":
    filtered_questions = [
        q for q in filtered_questions 
        if q.difficulty.value == st.session_state.filter_difficulty
    ]

if not filtered_questions:
    st.warning("没有符合筛选条件的题目")
    st.stop()

# 确保当前索引在有效范围内
if st.session_state.current_question_index >= len(filtered_questions):
    st.session_state.current_question_index = 0

filtered_total = len(filtered_questions)
st.caption(f"筛选结果: {filtered_total} 题")

st.markdown("<br>", unsafe_allow_html=True)

# ── 闪卡展示 ─────────────────────────────────────────────────────
current_idx = st.session_state.current_question_index
current_question = filtered_questions[current_idx]
card_key = f"card_{current_idx}"

# 获取当前卡片的翻转状态
is_flipped = st.session_state.flipped_states.get(card_key, False)

# 渲染闪卡
new_flip_state = render_flashcard(current_question, is_flipped, card_key)
st.session_state.flipped_states[card_key] = new_flip_state

# ── 导航控制 ─────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("上一题", disabled=(current_idx == 0), use_container_width=True):
        st.session_state.current_question_index -= 1
        st.rerun()

with col2:
    st.markdown(f"""
    <div style="text-align: center; padding: 0.5rem;">
        <span style="font-size: 1.1rem; font-weight: 600; color: #007AFF;">
            {current_idx + 1} / {filtered_total}
        </span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if st.button("下一题", disabled=(current_idx == filtered_total - 1), use_container_width=True):
        st.session_state.current_question_index += 1
        st.rerun()

# ── 底部导航 ─────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("返回分析", use_container_width=True):
        st.switch_page("pages/02_analysis.py")

with col2:
    if st.button("返回首页", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("app/main.py")
