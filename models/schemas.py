# models/schemas.py
# 数据模型定义模块 - 定义项目中所有数据结构的契约

# ============================================================
# 第一部分：导入依赖
# ============================================================

# 第1步：从 enum 模块导入 Enum 类，用于创建枚举类型
from enum import Enum
# 第2步：从 typing 模块导入 List 和 Optional，用于类型注解
from typing import List,Optional
# 第3步：从 pydantic 模块导入 BaseModel 和 Field
#        - BaseModel: 所有数据模型的基类
#        - Field: 用于字段约束（如数值范围、默认值）
from pydantic import BaseModel,Field


# ============================================================
# 第二部分：枚举类型定义
# ============================================================

# ------------------------------------------------------------
# 枚举1: QuestionType - 面试问题类型
# ------------------------------------------------------------

# 第4步：定义 QuestionType 类，继承自 str 和 Enum
#        继承 str 是为了让枚举值可以直接序列化为 JSON 字符串

    # 第5步：定义枚举值 TECHNICAL，值为 "technical"
    #        技术类问题（考察硬技能）

    # 第6步：定义枚举值 BEHAVIORAL，值为 "behavioral"
    #        行为类问题（考察软技能、过往经历）

    # 第7步：定义枚举值 SCENARIO，值为 "scenario"
    #        情景类问题（假设性场景应对）

    # 第8步：定义枚举值 PROJECT，值为 "project"
    #        项目类问题（深挖简历中的项目经验）
class QuestionType(str,Enum):
    TECHNICAL = "tehnical"
    BEHAVIORAL = "behavioral"
    SCENARIO = "scenario"
    PROJECT = "project"
    

# ------------------------------------------------------------
# 枚举2: DifficultyLevel - 问题难度等级
# ------------------------------------------------------------

# 第9步：定义 DifficultyLevel 类，继承自 str 和 Enum

    # 第10步：定义枚举值 JUNIOR，值为 "junior"
    #         初级难度（0-2年经验）

    # 第11步：定义枚举值 MID，值为 "mid"
    #         中级难度（3-5年经验）

    # 第12步：定义枚举值 SENIOR，值为 "senior"
    #         高级难度（5年以上经验）
class DifficultyLevel(str,Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"

# ============================================================
# 第三部分：简历子模型（用于组成 ResumeInfo）
# ============================================================

# ------------------------------------------------------------
# 子模型1: WorkExperience - 工作经历
# ------------------------------------------------------------

# 第13步：定义 WorkExperience 类，继承自 BaseModel

    # 第14步：定义字段 company，类型为 str
    #         公司名称

    # 第15步：定义字段 role，类型为 str
    #         职位/角色

    # 第16步：定义字段 duration，类型为 str
    #         工作时长（如 "2021.06 - 2023.08" 或 "2年3个月"）

    # 第17步：定义字段 achievements，类型为 List[str]
    #         工作成就/职责列表
class WorkExperience(BaseModel):
    company: str
    role: str
    duration: str
    achivements: List[str]

# ------------------------------------------------------------
# 子模型2: Project - 项目经历
# ------------------------------------------------------------

# 第18步：定义 Project 类，继承自 BaseModel

    # 第19步：定义字段 name，类型为 str
    #         项目名称

    # 第20步：定义字段 description，类型为 str
    #         项目描述

    # 第21步：定义字段 technologies，类型为 List[str]
    #         使用的技术栈

    # 第22步：定义字段 role，类型为 str
    #         在项目中的角色
class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]
    role: str

# ------------------------------------------------------------
# 子模型3: Education - 教育背景
# ------------------------------------------------------------

# 第23步：定义 Education 类，继承自 BaseModel

    # 第24步：定义字段 degree，类型为 str
    #         学位（如 "本科"、"硕士"、"Bachelor's"）

    # 第25步：定义字段 institution，类型为 str
    #         学校/机构名称

    # 第26步：定义字段 graduation_year，类型为 Optional[int]，默认值为 None
    #         毕业年份（可选，因为有些简历不写）
class Education(BaseModel):
    degree: str
    institution: str
    graduation_year: Optional[int] = None

# ============================================================
# 第四部分：主数据模型
# ============================================================

# ------------------------------------------------------------
# 主模型1: JDInfo - 职位描述结构化信息
# ------------------------------------------------------------

# 第27步：定义 JDInfo 类，继承自 BaseModel
#         用于存储从 JD 文本中提取的结构化信息

    # 第28步：定义字段 job_title，类型为 str
    #         职位名称

    # 第29步：定义字段 required_skills，类型为 List[str]
    #         必需技能列表

    # 第30步：定义字段 nice_to_have_skills，类型为 List[str]，默认值为空列表
    #         加分技能列表（可选）

    # 第31步：定义字段 responsibilities，类型为 List[str]
    #         岗位职责列表

    # 第32步：定义字段 industry，类型为 Optional[str]，默认值为 None
    #         行业领域（可选）

    # 第33步：定义字段 seniority_level，类型为 Optional[str]，默认值为 None
    #         资历级别（如 "Junior"、"Senior"、"Lead"）
class JDInfo(BaseModel):
    job_title: str
    required_skills: List[str]
    nice_to_have_skills: List[str] = Field(default_factory=list)
    responsibilities = List[str]
    industry = Optional[str] = None
    seniority_level = Optional[str] = None
    


# ------------------------------------------------------------
# 主模型2: ResumeInfo - 简历结构化信息
# ------------------------------------------------------------

# 第34步：定义 ResumeInfo 类，继承自 BaseModel
#         用于存储从简历文本中提取的结构化信息

    # 第35步：定义字段 skills，类型为 List[str]
    #         技能列表

    # 第36步：定义字段 experiences，类型为 List[WorkExperience]
    #         工作经历列表（使用子模型）

    # 第37步：定义字段 projects，类型为 List[Project]
    #         项目经历列表（使用子模型）

    # 第38步：定义字段 education，类型为 List[Education]
    #         教育背景列表（使用子模型）

    # 第39步：定义字段 years_of_experience，类型为 Optional[int]，默认值为 None
    #         总工作年限（可选，可由 LLM 推断）
class ResumeInfo(BaseModel):
    skills: List[str]
    experiences: List[WorkExperience]
    projects: List[Project]
    education: List[Education]
    years_of_experience: Optional[int] = None

# ------------------------------------------------------------
# 主模型3: GapAnalysis - 差距分析结果
# ------------------------------------------------------------

# 第40步：定义 GapAnalysis 类，继承自 BaseModel
#         用于存储 JD 与简历的匹配分析结果

    # 第41步：定义字段 overall_match_score，类型为 float
    #         使用 Field 约束范围 ge=0, le=100
    #         总体匹配分数（0-100）

    # 第42步：定义字段 matched_skills，类型为 List[str]
    #         匹配的技能（简历中有且 JD 要求的）

    # 第43步：定义字段 missing_skills，类型为 List[str]
    #         缺失的技能（JD 要求但简历中没有的）

    # 第44步：定义字段 strengths，类型为 List[str]
    #         候选人的优势点

    # 第45步：定义字段 weaknesses，类型为 List[str]
    #         候选人的弱势点

    # 第46步：定义字段 focus_areas，类型为 List[str]
    #         面试应重点关注的领域
class GapAnalysis(BaseModel):
    overall_match_score: float = Field(...,ge=0,le=100)
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    focus_areas: List[str]

# ------------------------------------------------------------
# 主模型4: Question - 面试问题
# ------------------------------------------------------------

# 第47步：定义 Question 类，继承自 BaseModel
#         用于存储生成的面试问题及其元信息

    # 第48步：定义字段 question_text，类型为 str
    #         问题文本内容

    # 第49步：定义字段 question_type，类型为 QuestionType
    #         问题类型（使用枚举）

    # 第50步：定义字段 difficulty，类型为 DifficultyLevel
    #         难度等级（使用枚举）

    # 第51步：定义字段 focus_area，类型为 str
    #         问题针对的能力/技能领域

    # 第52步：定义字段 reference_answer，类型为 str
    #         参考答案

    # 第53步：定义字段 evaluation_criteria，类型为 List[str]
    #         评估标准列表（用于评判回答质量）
class Question(BaseModel):
    question_text: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    focus_area: str
    reference_answer: str
    evaluation_criteria: List[str]

# ============================================================
# 第五部分：模块导出（可选，用于 __init__.py）
# ============================================================

# 第54步：定义 __all__ 列表，列出所有对外公开的类
#         包含: QuestionType, DifficultyLevel, WorkExperience, 
#               Project, Education, JDInfo, ResumeInfo, 
#               GapAnalysis, Question
__all__ = [
    "QuestionType",
    "DifficultyLevel",
    "WorkExperience",
    "Project",
    "Education",
    "JDInfo",
    "ResumeInfo",
    "GapAnalysis",
    "Question",
]
