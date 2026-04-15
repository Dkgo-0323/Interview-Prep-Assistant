"""
UI Components Library - Apple Style Design

提供统一的 UI 组件，实现 Apple 风格的视觉设计。
"""

import streamlit as st
import plotly.graph_objects as go
from typing import List, Optional
from models.schemas import GapAnalysis, Question, QuestionType, DifficultyLevel


def apply_apple_style():
    """注入全局 Apple 风格 CSS"""
    st.markdown("""
    <style>
    /* 全局样式变量 */
    :root {
        --primary-blue: #007AFF;
        --secondary-gray: #8E8E93;
        --background: #F2F2F7;
        --card-bg: #FFFFFF;
        --text-primary: #000000;
        --text-secondary: #6C6C70;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --shadow-sm: 0 2px 8px rgba(0,0,0,0.08);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
        --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    /* 主容器样式 */
    .main {
        background-color: #FFFFFF;
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
    
    /* Streamlit 默认背景 */
    .stApp {
        background-color: #FAFAFA;
    }
    
    /* 卡片样式 */
    .stCard {
        background: var(--card-bg);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background-color: var(--primary-blue);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 500;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #0051D5;
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    /* 文件上传器样式 */
    .uploadedFile {
        border-radius: var(--radius-md);
        border: 2px dashed var(--secondary-gray);
        padding: 2rem;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .uploadedFile:hover {
        border-color: var(--primary-blue);
        background-color: rgba(0, 122, 255, 0.05);
    }
    
    /* 进度指示器样式 */
    .progress-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .progress-step {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .progress-step.active {
        background-color: var(--primary-blue);
        color: white;
        box-shadow: var(--shadow-md);
    }
    
    .progress-step.inactive {
        background-color: #E5E5EA;
        color: var(--secondary-gray);
    }
    
    .progress-line {
        width: 60px;
        height: 2px;
        background-color: #E5E5EA;
    }
    
    .progress-line.active {
        background-color: var(--primary-blue);
    }
    
    /* 标题样式 */
    h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    h2 {
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    
    h3 {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
    }
    
    /* 副标题样式 */
    .subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
    }
    
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def render_progress_indicator(current_step: int):
    """
    渲染顶部进度指示器 (1→2→3)
    
    Args:
        current_step: 当前步骤 (1=上传, 2=分析, 3=题目)
    """
    steps = ["上传文档", "分析报告", "面试题库"]
    
    html = '<div class="progress-indicator">'
    
    for i in range(1, 4):
        # 步骤圆圈
        active_class = "active" if i <= current_step else "inactive"
        html += f'<div class="progress-step {active_class}">{i}</div>'
        
        # 连接线（最后一个步骤后不显示）
        if i < 3:
            line_class = "active" if i < current_step else ""
            html += f'<div class="progress-line {line_class}"></div>'
    
    html += '</div>'
    
    # 步骤标签
    html += '<div style="display: flex; justify-content: center; gap: 6rem; margin-top: 0.5rem;">'
    for i, label in enumerate(steps, 1):
        color = "var(--primary-blue)" if i <= current_step else "var(--secondary-gray)"
        html += f'<div style="color: {color}; font-size: 0.9rem; font-weight: 500;">{label}</div>'
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)


def render_document_preview(text: str, max_chars: int = 200, title: str = "文档预览"):
    """
    渲染文档预览卡片
    
    Args:
        text: 文档文本内容
        max_chars: 最大显示字符数
        title: 预览标题
    """
    preview_text = text[:max_chars] + "..." if len(text) > max_chars else text
    
    with st.expander(f"▼ {title}", expanded=False):
        st.text(preview_text)
        st.caption(f"总字符数: {len(text)}")


def render_match_score_card(score: int, recommendations: List[str]):
    """
    渲染匹配度展示卡片
    
    Args:
        score: 总体匹配度分数 (0-100)
        recommendations: 核心建议列表
    """
    # 分数颜色映射
    if score >= 80:
        color = "#34C759"  # 绿色
        level = "优秀"
    elif score >= 60:
        color = "#FF9500"  # 橙色
        level = "良好"
    else:
        color = "#FF3B30"  # 红色
        level = "待提升"
    
    st.markdown(f"""
    <div style="background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">
        <h2 style="text-align: center; margin-bottom: 1rem; font-weight: 600;">总体匹配度</h2>
        <div style="text-align: center;">
            <div style="font-size: 4rem; font-weight: 700; color: {color}; margin: 1rem 0;">
                {score}
            </div>
            <div style="font-size: 1.2rem; color: #6C6C70; margin-bottom: 1rem;">
                {level} ({score}/100)
            </div>
            <div style="background: #F2F2F7; border-radius: 12px; height: 12px; overflow: hidden;">
                <div style="background: {color}; height: 100%; width: {score}%; transition: width 0.5s ease;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 核心建议
    if recommendations:
        st.markdown("### 核心建议")
        for rec in recommendations[:5]:  # 最多显示5条
            st.markdown(f"• {rec}")


def render_radar_chart(gap: GapAnalysis):
    """
    渲染能力雷达图 (Plotly)
    
    Args:
        gap: 差距分析结果
    """
    categories = ['技能匹配', '经验匹配', '学历匹配', '项目相关']
    values = [
        gap.skill_score,
        gap.experience_score,
        gap.education_score,
        gap.project_score
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='候选人水平',
        line=dict(color='#007AFF', width=2),
        fillcolor='rgba(0, 122, 255, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10),
                gridcolor='#E5E5EA'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#000000')
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=80, r=80, t=40, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_skill_comparison(matched: List[str], missing: List[str]):
    """
    渲染技能对比表
    
    Args:
        matched: 已掌握技能列表
        missing: 缺失技能列表
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 已掌握技能")
        if matched:
            for skill in matched:
                st.markdown(f"• {skill}")
        else:
            st.info("暂无匹配技能")
    
    with col2:
        st.markdown("### 缺失技能")
        if missing:
            for skill in missing:
                st.markdown(f"• {skill}")
        else:
            st.success("无缺失技能")


def render_flashcard(question: Question, is_flipped: bool, card_key: str):
    """
    渲染闪卡组件 (HTML/CSS 翻转动画)
    
    Args:
        question: 面试题对象
        is_flipped: 是否已翻转
        card_key: 唯一标识符（用于状态管理）
    """
    difficulty_colors = {
        DifficultyLevel.BASIC: "#34C759",
        DifficultyLevel.INTERMEDIATE: "#FF9500",
        DifficultyLevel.ADVANCED: "#FF3B30"
    }
    color = difficulty_colors.get(question.difficulty, "#8E8E93")
    flip_class = "flipped" if is_flipped else ""
    
    st.markdown(f"""
    <style>
    .flashcard_{card_key} {{
        perspective: 1000px;
        width: 100%;
        height: 380px;
        margin: 1.5rem 0;
    }}
    .flashcard_{card_key} .fc-inner {{
        position: relative;
        width: 100%;
        height: 100%;
        transition: transform 0.55s cubic-bezier(0.4, 0, 0.2, 1);
        transform-style: preserve-3d;
    }}
    .flashcard_{card_key}.flipped .fc-inner {{
        transform: rotateY(180deg);
    }}
    .fc-front, .fc-back {{
        position: absolute;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        -webkit-backface-visibility: hidden;
        border-radius: 14px;
        padding: 2.5rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-sizing: border-box;
    }}
    .fc-front {{
        background: #FFFFFF;
        border: 1px solid #E8E8ED;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }}
    .fc-back {{
        background: #F8F9FA;
        border: 1px solid #E8E8ED;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        transform: rotateY(180deg);
        justify-content: flex-start;
        padding-top: 2rem;
    }}
    .fc-question {{
        font-size: 1.35rem;
        font-weight: 600;
        text-align: center;
        color: #1C1C1E;
        line-height: 1.65;
        margin-bottom: 2rem;
    }}
    .fc-meta {{
        display: flex;
        gap: 0.75rem;
        font-size: 0.8rem;
        color: #8E8E93;
        margin-top: auto;
    }}
    .fc-tag {{
        background: #F2F2F7;
        border-radius: 6px;
        padding: 3px 10px;
    }}
    .fc-difficulty {{
        background: {color}1A;
        color: {color};
        border-radius: 6px;
        padding: 3px 10px;
        font-weight: 500;
    }}
    .fc-hint {{
        font-size: 0.8rem;
        color: #C7C7CC;
        margin-bottom: 1.5rem;
    }}
    .fc-answer-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: #007AFF;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.75rem;
        align-self: flex-start;
    }}
    .fc-answer {{
        font-size: 1rem;
        color: #3A3A3C;
        line-height: 1.75;
        text-align: left;
        width: 100%;
        overflow-y: auto;
        max-height: 160px;
        margin-bottom: 1rem;
    }}
    .fc-detail {{
        width: 100%;
        background: #FFFFFF;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        font-size: 0.85rem;
        color: #6C6C70;
        line-height: 1.6;
        border: 1px solid #E8E8ED;
    }}
    </style>

    <div class="flashcard_{card_key} {flip_class}">
        <div class="fc-inner">
            <div class="fc-front">
                <div class="fc-question">{question.question_text}</div>
                <div class="fc-hint">点击下方按钮查看参考答案</div>
                <div class="fc-meta">
                    <span class="fc-tag">{question.question_type.value}</span>
                    <span class="fc-difficulty">{question.difficulty.value}</span>
                </div>
            </div>
            <div class="fc-back">
                <div class="fc-answer-label">参考答案</div>
                <div class="fc-answer">{question.reference_answer}</div>
                <div class="fc-detail">
                    <strong>考察意图：</strong>{question.intent}<br>
                    <strong>关注点：</strong>{question.focus_area}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    label = "查看答案" if not is_flipped else "返回题目"
    if st.button(label, key=f"flip_{card_key}", use_container_width=True):
        return not is_flipped
    
    return is_flipped


def render_loading_spinner(message: str = "加载中..."):
    """
    渲染加载动画
    
    Args:
        message: 加载提示文本
    """
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem;">
        <div style="font-size: 1.2rem; color: #6C6C70;">{message}</div>
    </div>
    """, unsafe_allow_html=True)