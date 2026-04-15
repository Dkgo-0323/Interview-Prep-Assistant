"""
页面 2: 分析报告
展示匹配度分析结果，生成面试题
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
    render_match_score_card,
    render_radar_chart,
    render_skill_comparison,
    render_loading_spinner
)
from services.llm_service import LLMService
from core.analyzers import analyze_jd, analyze_resume, analyze_gap
from core.generators import generate_questions
from core.analyzers.exceptions import AnalyzerError
import config

# ── 页面配置 ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="分析报告 - AI 面试助手",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

apply_apple_style()

# ── 进度指示器 ───────────────────────────────────────────────────
render_progress_indicator(current_step=2)

# ── 检查前置条件 ─────────────────────────────────────────────────
if 'jd_text' not in st.session_state or 'resume_text' not in st.session_state:
    st.error("请先上传 JD 和简历文件")
    if st.button("返回上传页面"):
        st.switch_page("pages/01_upload.py")
    st.stop()

# ── 页面标题 ─────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; margin: 2rem 0 2.5rem;">
    <h1 style="font-size: 2rem; font-weight: 600; color: #1C1C1E;">匹配度分析</h1>
    <p style="color: #6C6C70; font-size: 1rem;">基于 AI 的多维度能力评估</p>
</div>
""", unsafe_allow_html=True)

# ── 初始化 Session State ────────────────────────────────────────
if 'jd_info' not in st.session_state:
    st.session_state.jd_info = None
if 'resume_info' not in st.session_state:
    st.session_state.resume_info = None
if 'gap_analysis' not in st.session_state:
    st.session_state.gap_analysis = None
if 'num_questions' not in st.session_state:
    st.session_state.num_questions = config.DEFAULT_NUM_QUESTIONS

# ── 执行分析（仅首次加载）──────────────────────────────────────
if st.session_state.gap_analysis is None:
    try:
        with st.spinner('正在分析 JD 信息...'):
            llm = LLMService()
            jd_info = analyze_jd(st.session_state.jd_text, llm)
            st.session_state.jd_info = jd_info
        
        with st.spinner('正在分析简历信息...'):
            resume_info = analyze_resume(st.session_state.resume_text, llm)
            st.session_state.resume_info = resume_info
        
        with st.spinner('正在计算匹配度...'):
            gap_analysis = analyze_gap(jd_info, resume_info, llm)
            st.session_state.gap_analysis = gap_analysis
        
        st.success("分析完成")
        st.rerun()
        
    except AnalyzerError as e:
        st.error(f"分析失败：{str(e)}")
        if st.button("返回上传页面"):
            st.switch_page("pages/01_upload.py")
        st.stop()
    except Exception as e:
        st.error(f"系统错误：{str(e)}")
        if st.button("返回上传页面"):
            st.switch_page("pages/01_upload.py")
        st.stop()

# ── 展示分析结果 ─────────────────────────────────────────────────
gap = st.session_state.gap_analysis

# 匹配度卡片
render_match_score_card(gap.overall_match_score, gap.recommendations)

st.markdown("<br>", unsafe_allow_html=True)

# 雷达图
st.markdown("### 能力雷达图")
render_radar_chart(gap)

st.markdown("<br>", unsafe_allow_html=True)

# 技能对比
st.markdown("### 技能对比分析")
render_skill_comparison(gap.matched_skills, gap.missing_skills)

st.markdown("<br>", unsafe_allow_html=True)

# 优势与劣势
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 核心优势")
    for strength in gap.strengths:
        st.markdown(f"• {strength}")

with col2:
    st.markdown("### 待提升项")
    for weakness in gap.weaknesses:
        st.markdown(f"• {weakness}")

st.markdown("<br><br>", unsafe_allow_html=True)

# ── 生成面试题控制 ──────────────────────────────────────────────
st.markdown("---")
st.markdown("### 生成个性化面试题")

col1, col2 = st.columns([2, 1])

with col1:
    num_questions = st.selectbox(
        "选择题目数量",
        options=[10, 15, 20, 30],
        index=0,
        key='num_questions_selector'
    )
    st.session_state.num_questions = num_questions

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("生成题目", use_container_width=True, type="primary"):
        try:
            with st.spinner(f'正在生成 {num_questions} 道面试题...'):
                llm = LLMService()
                questions = generate_questions(
                    gap=st.session_state.gap_analysis,
                    resume=st.session_state.resume_info,
                    jd=st.session_state.jd_info,
                    llm=llm,
                    num_questions=num_questions
                )
                st.session_state.questions = questions
            st.success(f"成功生成 {len(questions.questions)} 道面试题")
            st.switch_page("pages/03_questions.py")
        except Exception as e:
            st.error(f"题目生成失败：{str(e)}")

# ── 底部导航 ─────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("重新上传", use_container_width=True):
        for key in ['jd_text', 'resume_text', 'jd_info', 'resume_info', 'gap_analysis', 'questions']:
            if key in st.session_state:
                del st.session_state[key]
        st.switch_page("pages/01_upload.py")
