
# 🎨 Interview Prep Assistant - 前端设计文档

**版本**: 1.0.0  
**日期**: 2025-01-XX  
**状态**: MVP 设计定稿  
**目标**: 快速上线，用户评测

---

## 📋 1. 项目概述

### 1.1 产品定位
AI 驱动的个性化面试准备工具，帮助求职者：
1. 上传 JD（职位描述）和个人简历
2. 自动分析匹配度和能力差距
3. 生成针对性的面试题目进行练习

### 1.2 技术栈
- **框架**: Streamlit 1.28+
- **语言**: Python 3.9+
- **后端**: 已实现的 Analyzer + Generator 管道
- **可视化**: Plotly（雷达图）
- **动画**: HTML/CSS（闪卡翻转）

### 1.3 MVP 范围
✅ 核心流程：上传 → 分析 → 题目  
✅ 关键体验：多页导航、状态保持、闪卡交互  
❌ 暂缓功能：PDF 报告、历史记录、题目筛选、复杂动画

---

## 🗺️ 2. 页面架构设计

### 2.1 三页导航流程

```
┌─────────────────────────────────────────────────────────────┐
│                        用户流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📤 1_Upload.py  ──(点击下一步)──>  📊 2_Analysis.py       │
│    上传文件                     分析匹配度 + 可视化           │
│                                                             │
│  📊 2_Analysis.py  ──(点击下一步)──>  ❓ 3_Questions.py    │
│    查看结果                     生成题目 + 闪卡练习           │
│                                                             │
│  ❓ 3_Questions.py  ──(下载)─────>  📥 JSON 导出            │
│    练习题目                     保存题目数据                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 页面跳转逻辑
- **前进**: 用户主动点击"下一步"按钮（`st.switch_page()`）
- **后退**: 提供"返回"或"重新上传"按钮
- **前置检查**: 跳转前验证必要状态，缺失则提示并阻止

---

## 💾 3. 状态管理策略

### 3.1 Session State 数据结构

```python
st.session_state = {
    # 原始输入
    'jd_text': str,                    # JD 全文
    'resume_text': str,                # 简历全文
    'jd_file_name': str,               # JD 文件名
    'resume_file_name': str,           # 简历文件名
    
    # 分析结果（Analysis 页生成）
    'jd_info': JDInfo,                 # JD 结构化信息
    'resume_info': ResumeInfo,         # 简历结构化信息
    'gap_analysis': GapAnalysis,       # 差距分析结果
    
    # 题目生成（Questions 页生成）
    'questions': QuestionList,         # 题目列表
    'num_questions': int,              # 用户选择的题目数量
    'current_question': int,           # 当前显示的题目索引
    
    # UI 状态
    'analysis_done': bool,             # 分析是否完成
    'questions_generated': bool,       # 题目是否已生成
}
```

### 3.2 状态生命周期
1. **Upload 页**: 初始化 `jd_text`/`resume_text`
2. **Analysis 页**: 生成 `jd_info`/`resume_info`/`gap_analysis`，设置 `analysis_done=True`
3. **Questions 页**: 生成 `questions`，设置 `questions_generated=True`
4. **页面切换**: 状态自动保持，无需手动传递

### 3.3 重置机制
- **重新上传**: 清除所有状态（`st.session_state.clear()`）并跳转 Upload 页
- **刷新页面**: 状态丢失（Streamlit 默认），需重新上传（可接受，MVP 阶段）

---

## 🎨 4. 核心组件设计

### 4.1 雷达图组件 (`render_radar_chart`)

**输入**: `GapAnalysis` 对象  
**输出**: Plotly 雷达图

```python
def render_radar_chart(gap: GapAnalysis):
    """
    渲染 4 维度匹配度雷达图
    维度: 技能匹配、经验匹配、学历匹配、项目相关
    范围: 0-100
    """
    fig = go.Figure(go.Scatterpolar(
        r=[
            gap.skill_score,
            gap.experience_score,
            gap.education_score,
            gap.project_score
        ],
        theta=['技能匹配', '经验匹配', '学历匹配', '项目相关'],
        fill='toself',
        line=dict(color='#FF4B4B'),
        fillcolor='rgba(255, 75, 75, 0.2)'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                ticksuffix='%'
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return fig
```

### 4.2 技能对比组件 (`render_skill_comparison`)

**输入**: `GapAnalysis` 对象  
**输出**: 两列布局（已匹配 vs 缺失）

```python
def render_skill_comparison(gap: GapAnalysis):
    """渲染技能对比表"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"✅ 已匹配技能 ({len(gap.matched_skills)})")
        if gap.matched_skills:
            for skill in gap.matched_skills:
                st.write(f"- {skill}")
        else:
            st.caption("暂无匹配技能")
    
    with col2:
        st.error(f"❌ 缺失技能 ({len(gap.missing_skills)})")
        if gap.missing_skills:
            for skill in gap.missing_skills:
                st.write(f"- {skill}")
        else:
            st.caption("无缺失技能")
```

### 4.3 闪卡组件 (`render_flashcard`) - MVP 重点

**输入**: `Question` 对象, `card_id` (int)  
**输出**: HTML/CSS 翻转卡片

#### 设计原则
- **轻量**: 单文件 HTML 内嵌，无外部依赖
- **流畅**: CSS 3D 翻转动画（0.6s）
- **独立**: 每张卡片独立状态，互不干扰
- **响应式**: 移动端友好（自适应宽度）

#### 实现方案（HTML/CSS + JavaScript）

```python
import streamlit.components.v1 as components

def render_flashcard(question: Question, card_id: int):
    """
    渲染可翻转的面试题闪卡
    
    正面: 问题文本 + 提示
    背面: 参考答案
    
    点击卡片触发翻转（前端 JS 实现）
    """
    
    # 提取题目类型和难度标签
    type_label = {
        "技术深度": "🔧 技术深度",
        "项目经验": "🚀 项目经验", 
        "情景模拟": "🎭 情景模拟",
        "行为面试": "👥 行为面试"
    }.get(question.question_type.value, question.question_type.value)
    
    difficulty_label = {
        "基础": "🟢 基础",
        "进阶": "🟡 进阶",
        "高级": "🔴 高级"
    }.get(question.difficulty.value, question.difficulty.value)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* 卡片容器 */
            .flip-card {{
                background-color: transparent;
                width: 100%;
                height: 400px;
                perspective: 1000px;
                margin-bottom: 20px;
            }}
            
            /* 翻转内部容器 */
            .flip-card-inner {{
                position: relative;
                width: 100%;
                height: 100%;
                text-align: center;
                transition: transform 0.6s;
                transform-style: preserve-3d;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                border-radius: 12px;
            }}
            
            /* 翻转状态 */
            .flip-card.flipped .flip-card-inner {{
                transform: rotateY(180deg);
            }}
            
            /* 正面和背面公共样式 */
            .flip-card-front, .flip-card-back {{
                position: absolute;
                width: 100%;
                height: 100%;
                -webkit-backface-visibility: hidden;
                backface-visibility: hidden;
                border-radius: 12px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 30px;
                box-sizing: border-box;
            }}
            
            /* 正面样式 */
            .flip-card-front {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                cursor: pointer;
            }}
            
            .flip-card-front h3 {{
                font-size: 1.3em;
                margin-bottom: 20px;
                line-height: 1.5;
            }}
            
            .flip-card-front .hint {{
                font-size: 0.9em;
                opacity: 0.8;
                margin-top: 30px;
            }}
            
            .flip-card-front .tags {{
                margin-top: 20px;
                display: flex;
                gap: 10px;
            }}
            
            .tag {{
                background: rgba(255,255,255,0.2);
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.85em;
            }}
            
            /* 背面样式 */
            .flip-card-back {{
                background-color: #f8f9fa;
                color: #262730;
                transform: rotateY(180deg);
                overflow-y: auto;
                text-align: left;
                align-items: flex-start;
                justify-content: flex-start;
            }}
            
            .flip-card-back h4 {{
                color: #FF4B4B;
                margin-bottom: 15px;
                font-size: 1.1em;
                border-bottom: 2px solid #FF4B4B;
                padding-bottom: 10px;
                width: 100%;
            }}
            
            .flip-card-back .answer {{
                line-height: 1.6;
                font-size: 1em;
            }}
            
            .flip-card-back .tags {{
                margin-top: 20px;
                width: 100%;
            }}
            
            /* 响应式 */
            @media (max-width: 768px) {{
                .flip-card {{
                    height: 350px;
                }}
                .flip-card-front h3 {{
                    font-size: 1.1em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="flip-card" onclick="this.classList.toggle('flipped')">
            <div class="flip-card-inner">
                <!-- 正面 -->
                <div class="flip-card-front">
                    <div class="tags">
                        <span class="tag">{type_label}</span>
                        <span class="tag">{difficulty_label}</span>
                    </div>
                    <h3>{question.question_text}</h3>
                    <div class="hint">👆 点击查看参考答案</div>
                </div>
                <!-- 背面 -->
                <div class="flip-card-back">
                    <div class="tags">
                        <span class="tag" style="background: #667eea; color: white;">{type_label}</span>
                        <span class="tag" style="background: #667eea; color: white;">{difficulty_label}</span>
                    </div>
                    <h4>💡 参考答案</h4>
                    <div class="answer">{question.reference_answer}</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # 渲染 HTML 组件
    components.html(
        html_code,
        height=420,  # 卡片高度 + 边距
        scrolling=False
    )
```

#### 技术要点
1. **CSS 3D Transform**: `rotateY(180deg)` 实现翻转
2. **独立状态**: 每张卡片有独立的 `flipped` class，互不影响
3. **点击事件**: `onclick="this.classList.toggle('flipped')"` 直接操作 DOM
4. **无 Streamlit 交互**: 纯前端翻转，不触发 Python 回调（MVP 可接受）

#### 备选方案（如 HTML 方案失败）
```python
def render_flashcard_fallback(question: Question, card_id: int):
    """纯 Streamlit 备选方案（无动画）"""
    state_key = f"card_{card_id}_flipped"
    if state_key not in st.session_state:
        st.session_state[state_key] = False
    
    if st.button("🔄 翻转卡片", key=f"flip_{card_id}"):
        st.session_state[state_key] = not st.session_state[state_key]
    
    if st.session_state[state_key]:
        st.info(f"**参考答案**\n\n{question.reference_answer}")
    else:
        st.success(f"**{question.question_text}**")
```

---

## 📁 5. 目录结构

```
interview-prep/
├── app/
│   ├── Home.py                      # 占位或删除，直接进入 1_Upload
│   ├── pages/
│   │   ├── 1_📤_Upload.py           # 文件上传页
│   │   ├── 2_📊_Analysis.py         # 分析结果页
│   │   └── 3_❓_Questions.py        # 题目练习页
│   └── utils/
│       ├── __init__.py
│       └── ui_components.py         # 共享 UI 组件（雷达图、闪卡等）
├── .streamlit/
│   └── config.toml                  # Streamlit 配置
├── config.py                        # 应用配置
├── models/
│   └── schemas.py                   # Pydantic 模型
├── services/
│   └── llm_service.py               # LLM 服务
├── core/
│   ├── parsers/
│   ├── analyzers/
│   └── generators/
├── prompts/
├── tests/
├── .env.example                     # 环境变量模板
├── .gitignore
├── requirements.txt
├── README.md
└── ARCHITECTURE.md                  # 本文档
```

---

## 📦 6. 依赖清单

### 6.1 `requirements.txt`

```txt
# 核心框架
streamlit>=1.28.0
python-dotenv>=1.0.0

# LLM 服务
openai>=1.0.0

# 数据验证
pydantic>=2.0.0

# 文档解析
python-docx>=0.8.11
pypdf2>=3.0.0

# 可视化
plotly>=5.17.0

# 工具库
numpy>=1.24.0
```

### 6.2 环境变量 (`.env`)

```bash
# OpenAI 配置
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=4000

# 应用配置
APP_ENV=production
LOG_LEVEL=INFO
```

---

## 🛠️ 7. 实施计划（MVP 开发顺序）

### Phase 1: 基础设施（Day 1）
- [ ] 创建 `app/utils/ui_components.py`（雷达图 + 闪卡）
- [ ] 配置 `.streamlit/config.toml`
- [ ] 验证后端服务（LLMService 可用性）

### Phase 2: 页面开发（Day 2-3）
- [ ] `1_📤_Upload.py`（文件上传 + 预览 + 状态保存）
- [ ] `2_📊_Analysis.py`（分析流程 + 进度条 + 可视化）
- [ ] `3_❓_Questions.py`（题目生成 + 闪卡展示 + 导航）

### Phase 3: 集成测试（Day 4）
- [ ] 端到端流程测试（上传 → 分析 → 题目）
- [ ] 错误场景测试（文件格式错误、API 失败等）
- [ ] 移动端适配测试（响应式布局）

### Phase 4: 部署准备（Day 5）
- [ ] 配置 `requirements.txt`
- [ ] 编写 `README.md`（部署说明）
- [ ] 准备测试数据（可选）
- [ ] 部署到 Streamlit Cloud / 自托管

---

## ⚠️ 8. 错误处理策略

### 8.1 文件上传错误
```python
try:
    text = parse_document(file)
except UnsupportedFileTypeError:
    st.error("❌ 不支持的文件格式，请上传 PDF/DOCX/TXT")
except FileTooLargeError:
    st.error("❌ 文件过大，请上传 < 10MB 的文件")
except Exception as e:
    st.error(f"❌ 文件解析失败：{str(e)}")
```

### 8.2 分析过程错误
```python
try:
    gap = analyze_gap(jd_info, resume_info, llm)
except AnalyzerError as e:
    st.error(f"❌ 分析失败：{str(e)}")
    st.info("💡 建议：检查简历是否包含完整的工作经历")
    if st.button("返回重新上传"):
        st.session_state.clear()
        st.switch_page("pages/1_📤_Upload.py")
    st.stop()
```

### 8.3 题目生成错误
```python
try:
    questions = generate_questions(...)
except QuestionGenerationError as e:
    st.error(f"❌ {str(e)}")
    if st.button("重试"):
        st.rerun()
```

### 8.4 通用错误页面
- **缺少前置状态**: `st.error("❌ 请先完成上一步")` + 跳转按钮
- **API 限流**: `st.warning("⏳ API 繁忙，请稍后重试")` + 重试按钮
- **未知错误**: `st.error("❌ 系统错误，请联系技术支持")` + 日志记录

---

## 🎯 9. MVP 验收标准

### 9.1 功能完整性
- [x] 可上传 JD 和简历（PDF/DOCX/TXT）
- [x] 显示文本预览（前 500 字）
- [x] 执行完整分析流程（JD → Resume → Gap）
- [x] 显示进度指示（3 步骤）
- [x] 渲染雷达图（4 维度）
- [x] 显示技能对比表（匹配/缺失）
- [x] 列出优劣势（strengths/weaknesses）
- [x] 选择题目数量（10-50）
- [x] 生成面试题（调用 Generator）
- [x] 闪卡展示（HTML/CSS 翻转）
- [x] 题目导航（上一题/下一题）
- [x] 下载题目（JSON 格式）

### 9.2 用户体验
- [x] 页面跳转流畅，无状态丢失
- [x] 错误提示友好，可恢复
- [x] 移动端基本可用（响应式）
- [x] 加载状态清晰（spinner + 进度条）
- [x] 操作按钮明确（下一步/返回）

### 9.3 技术质量
- [x] 无内存泄漏（Session State 合理使用）
- [x] 异常捕获完整（不崩溃）
- [x] 代码结构清晰（组件化）
- [x] 可部署（依赖明确）

---

## 🔮 10. 未来扩展（Post-MVP）

### 10.1 Phase 2: 体验优化
- [ ] 下载 PDF 报告（包含分析结果 + 题目）
- [ ] 题目筛选器（按类型/难度）
- [ ] 题目进度保存（刷新不丢失）
- [ ] 示例数据快速体验
- [ ] 闪卡键盘导航（左右键切换）

### 10.2 Phase 3: 高级功能
- [ ] 历史记录（SQLite 存储）
- [ ] 题目收藏/标记
- [ ] 模拟面试模式（计时 + 评分）
- [ ] 多语言支持（中英文）
- [ ] 自定义题目数量上限（>50）

---

## 📝 11. 开发备忘录

### 11.1 关键决策回顾
1. **多页导航**: 3 页分离，用户手动跳转，状态清晰
2. **Session State**: 原生方案，简单够用，暂不引入数据库
3. **雷达图**: Plotly 实现，4 维度直观展示
4. **闪卡**: HTML/CSS 翻转，轻量流畅，优先尝试
5. **MVP 优先**: 不做 PDF 导出、历史记录等复杂功能

### 11.2 技术风险
| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| HTML 闪卡在 Streamlit 中渲染异常 | 高 | 准备纯 Streamlit 备选方案 |
| LLM API 响应慢（>30s） | 中 | 进度条 + 超时提示 |
| 大文件解析内存占用 | 低 | 限制文件大小（10MB） |
| 移动端布局错乱 | 中 | 测试 + CSS 媒体查询 |

### 11.3 性能预期
- **文件解析**: < 5s（PDF/DOCX < 10MB）
- **JD 分析**: 5-10s（LLM API）
- **Resume 分析**: 5-10s（LLM API）
- **Gap 分析**: 3-5s（LLM API）
- **题目生成**: 10-15s（LLM API，10 题）
- **总计**: 约 30-50s（用户感知时间）

---

## ✅ 12. 设计确认清单

- [x] 页面架构（3 页导航）
- [x] 状态管理方案（Session State）
- [x] 核心组件设计（雷达图、技能对比、闪卡）
- [x] 目录结构规划
- [x] 依赖清单
- [x] 实施计划（4 个 Phase）
- [x] 错误处理策略
- [x] MVP 验收标准
- [x] 未来扩展路线

---

**文档状态**: ✅ 设计完成，进入开发阶段  
**下一步**: 按照 Phase 1 开始编码实现  
**预计完成时间**: 5 个工作日

---

> **设计原则**: 简单优先、用户体验至上、快速验证  
> **技术底线**: 不引入不必要的复杂性，保持 MVP 可部署性