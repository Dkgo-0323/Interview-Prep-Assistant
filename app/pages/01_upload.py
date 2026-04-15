"""
页面 1: 文件上传
上传 JD 和简历文件，提取文本内容
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
    render_document_preview
)
from core.parsers.parser_factory import parse_file
from core.parsers.exceptions import FileParseError, UnsupportedFileError
import config

# ── 页面配置 ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="上传文档 - AI 面试助手",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed",
)

apply_apple_style()

# ── 进度指示器 ───────────────────────────────────────────────────
render_progress_indicator(current_step=1)

# ── 页面标题 ─────────────────────────────────────────────────────
st.markdown("""
<div style="text-align: center; margin: 2rem 0 2.5rem;">
    <h1 style="font-size: 2rem; font-weight: 600; color: #1C1C1E;">上传文档</h1>
    <p style="color: #6C6C70; font-size: 1rem;">上传职位描述 (JD) 和个人简历，开始智能分析</p>
</div>
""", unsafe_allow_html=True)

# ── 初始化 Session State ────────────────────────────────────────
if 'jd_text' not in st.session_state:
    st.session_state.jd_text = None
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'jd_filename' not in st.session_state:
    st.session_state.jd_filename = None
if 'resume_filename' not in st.session_state:
    st.session_state.resume_filename = None

# ── 文件上传区域 ─────────────────────────────────────────────────
st.markdown("**职位描述 (JD)**")
jd_file = st.file_uploader(
    "支持 PDF、DOCX、TXT 格式，最大 10MB",
    type=['pdf', 'docx', 'txt'],
    key='jd_uploader',
    help=f"最大文件大小: {config.UPLOAD_MAX_SIZE_MB}MB"
)

if jd_file:
    file_size_mb = jd_file.size / (1024 * 1024)
    if file_size_mb > config.UPLOAD_MAX_SIZE_MB:
        st.error(f"文件过大，最大支持 {config.UPLOAD_MAX_SIZE_MB}MB，当前 {file_size_mb:.2f}MB")
    else:
        try:
            temp_path = config.UPLOAD_DIR / jd_file.name
            with open(temp_path, 'wb') as f:
                f.write(jd_file.getbuffer())
            with st.spinner('正在解析 JD 文件...'):
                jd_text = parse_file(temp_path)
                st.session_state.jd_text = jd_text
                st.session_state.jd_filename = jd_file.name
            st.success(f"解析成功：{jd_file.name}")
            render_document_preview(jd_text, max_chars=200, title="JD 预览")
        except (FileParseError, UnsupportedFileError) as e:
            st.error(f"文件解析失败：{str(e)}")
        except Exception as e:
            st.error(f"上传失败：{str(e)}")

st.markdown("<br>", unsafe_allow_html=True)

# ── 简历上传 ─────────────────────────────────────────────────────
st.markdown("**个人简历**")
resume_file = st.file_uploader(
    "支持 PDF、DOCX、TXT 格式，最大 10MB",
    type=['pdf', 'docx', 'txt'],
    key='resume_uploader',
    help=f"最大文件大小: {config.UPLOAD_MAX_SIZE_MB}MB"
)

if resume_file:
    file_size_mb = resume_file.size / (1024 * 1024)
    if file_size_mb > config.UPLOAD_MAX_SIZE_MB:
        st.error(f"文件过大，最大支持 {config.UPLOAD_MAX_SIZE_MB}MB，当前 {file_size_mb:.2f}MB")
    else:
        try:
            temp_path = config.UPLOAD_DIR / resume_file.name
            with open(temp_path, 'wb') as f:
                f.write(resume_file.getbuffer())
            with st.spinner('正在解析简历文件...'):
                resume_text = parse_file(temp_path)
                st.session_state.resume_text = resume_text
                st.session_state.resume_filename = resume_file.name
            st.success(f"解析成功：{resume_file.name}")
            render_document_preview(resume_text, max_chars=200, title="简历预览")
        except (FileParseError, UnsupportedFileError) as e:
            st.error(f"文件解析失败：{str(e)}")
        except Exception as e:
            st.error(f"上传失败：{str(e)}")

# ── 底部导航按钮 ─────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    both_uploaded = (
        st.session_state.jd_text is not None and
        st.session_state.resume_text is not None
    )

    if st.button(
        "开始分析",
        disabled=not both_uploaded,
        use_container_width=True,
        type="primary"
    ):
        st.switch_page("pages/02_analysis.py")

    if not both_uploaded:
        st.caption("请先上传 JD 和简历文件后继续")
