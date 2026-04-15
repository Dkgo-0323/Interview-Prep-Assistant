"""
AI 面试助手 - 主入口
Streamlit 多页面应用入口
"""

import streamlit as st
import sys
from pathlib import Path

# 将项目根目录加入 sys.path，确保所有模块可导入
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.utils.ui_components import apply_apple_style

# ── 页面基础配置（必须是第一个 st 调用）──────────────────────────
st.set_page_config(
    page_title="AI 面试助手",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

apply_apple_style()

# ── 欢迎首页内容 ─────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; padding: 4rem 2rem; background: white; border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin: 2rem 0;">
    <h1 style="font-size: 2.5rem; font-weight: 600; margin-bottom: 1rem; color: #1C1C1E;">AI 面试助手</h1>
    <p style="font-size: 1.1rem; color: #6C6C70; max-width: 500px; margin: 0 auto 2rem; line-height: 1.6;">
        智能分析职位匹配度，生成个性化面试题，助你拿下心仪 Offer
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("开始使用", use_container_width=True, type="primary"):
        st.switch_page("pages/01_upload.py")

# ── 功能介绍 ─────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

feat1, feat2, feat3 = st.columns(3)

with feat1:
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; border: 1px solid #E8E8ED;">
        <div style="font-weight: 600; margin-bottom: 0.5rem; color: #1C1C1E;">智能解析</div>
        <div style="color: #6C6C70; font-size: 0.9rem; line-height: 1.5;">
            上传 JD 和简历，自动提取关键信息
        </div>
    </div>
    """, unsafe_allow_html=True)

with feat2:
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; border: 1px solid #E8E8ED;">
        <div style="font-weight: 600; margin-bottom: 0.5rem; color: #1C1C1E;">匹配分析</div>
        <div style="color: #6C6C70; font-size: 0.9rem; line-height: 1.5;">
            多维度评估，精准定位差距
        </div>
    </div>
    """, unsafe_allow_html=True)

with feat3:
    st.markdown("""
    <div style="background: white; border-radius: 12px; padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; border: 1px solid #E8E8ED;">
        <div style="font-weight: 600; margin-bottom: 0.5rem; color: #1C1C1E;">面试题库</div>
        <div style="color: #6C6C70; font-size: 0.9rem; line-height: 1.5;">
            AI 生成个性化面试题，含参考答案
        </div>
    </div>
    """, unsafe_allow_html=True)
