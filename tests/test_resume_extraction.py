"""
Tests for Resume Extraction Prompts
测试简历信息提取的准确性和边界情况
"""

import pytest
from unittest.mock import Mock, patch
from models.schemas import ResumeInfo, WorkExperience, Project, Education
from prompts.resume_extraction import (
    RESUME_SYSTEM_PROMPT,
    get_resume_extraction_prompt,
)
from services.llm_service import LLMService


# ========== Fixtures: 测试数据 ==========

@pytest.fixture
def standard_resume_text():
    """标准软件工程师简历"""
    return """
John Doe
Software Engineer

SUMMARY
Experienced full-stack developer with 5 years of expertise in building scalable web applications.
Passionate about clean code and agile methodologies.

SKILLS
- Programming Languages: Python (Expert), JavaScript (Proficient), Go (Familiar)
- Frameworks: Django, React, Node.js
- Tools: Docker, Kubernetes, AWS
- Languages: English (Native), Spanish (Intermediate)

EXPERIENCE

Senior Software Engineer | Tech Corp | Jan 2021 - Present
- Led migration of monolithic application to microservices architecture, reducing deployment time by 60%
- Designed and implemented RESTful APIs serving 1M+ daily requests
- Mentored team of 3 junior developers
- Conducted code reviews and established CI/CD pipeline

Software Developer | StartupXYZ | Jun 2019 - Dec 2020
- Developed e-commerce platform using Django and React
- Optimized database queries, improving page load time by 40%
- Collaborated with product team to define technical requirements

PROJECTS

Open Source Contribution - FastAPI Helper Library
- Created utility library for FastAPI with 500+ GitHub stars
- Technologies: Python, FastAPI, pytest
- Role: Lead Developer
- Link: https://github.com/johndoe/fastapi-helper

Personal Portfolio Website
- Built responsive portfolio site with blog functionality
- Technologies: Next.js, TailwindCSS, Vercel
- Link: https://johndoe.com

EDUCATION

Bachelor of Science in Computer Science | MIT | Sep 2015 - May 2019
- GPA: 3.8/4.0
- Relevant Coursework: Algorithms, Distributed Systems

CERTIFICATIONS
- AWS Certified Solutions Architect - Associate (2022)
- Certified Kubernetes Administrator (2021)
"""


@pytest.fixture
def fresh_graduate_resume():
    """应届生简历（无工作经验）"""
    return """
Jane Smith
Computer Science Graduate

EDUCATION
University of California, Berkeley
Bachelor of Science in Computer Science
Graduated: May 2024
GPA: 3.9/4.0

SKILLS
Python, Java, C++, SQL, React, Git

PROJECTS

Student Management System (Capstone Project)
Developed full-stack web application for managing student records
- Built RESTful API using Spring Boot
- Implemented frontend with React and Redux
- Designed MySQL database schema
- Deployed on AWS EC2

Machine Learning Image Classifier
- Built CNN model for image classification with 92% accuracy
- Technologies: Python, TensorFlow, Keras
- Dataset: CIFAR-10

CERTIFICATIONS
Google Data Analytics Professional Certificate
"""


@pytest.fixture
def minimal_resume():
    """最简简历（仅核心信息）"""
    return """
Alex Johnson
alexj@email.com

EDUCATION
State University - BS Computer Science (2020)

EXPERIENCE
Software Intern, ABC Company (Summer 2019)
- Assisted in web development tasks using React and JavaScript
- Fixed bugs in existing Python codebase
"""


@pytest.fixture
def unstructured_resume():
    """非标准格式简历"""
    return """
I'm a developer with experience in Python and JavaScript.
Worked at CompanyA from 2020 to 2022 doing backend stuff.
Built some projects with React and Node.
Graduated from SomeCollege in 2019 with a CS degree.
Also know AWS and Docker pretty well.
"""


@pytest.fixture
def multilingual_resume():
    """多语言能力简历"""
    return """
PROFESSIONAL SUMMARY
Multilingual software engineer with international experience

TECHNICAL SKILLS
Python (Advanced), JavaScript, SQL

LANGUAGES
- English (Native)
- Mandarin Chinese (Fluent - HSK 6)
- French (Conversational - B2)
- Spanish (Basic - A2)

WORK EXPERIENCE
International Developer, GlobalTech Inc | 2020 - 2023
- Developed localization features for multi-language platform
- Collaborated with distributed teams across 4 countries

EDUCATION
BS Computer Science, University of Washington, 2019
"""


# ========== Test Cases: Prompt Generation ==========

class TestPromptGeneration:
    """测试 Prompt 生成逻辑"""
    
    def test_prompt_contains_resume_text(self, standard_resume_text):
        """验证 prompt 包含简历文本"""
        prompt = get_resume_extraction_prompt(standard_resume_text)
        assert "John Doe" in prompt
        assert "Tech Corp" in prompt
        assert "MIT" in prompt
    
    def test_prompt_includes_field_instructions(self, standard_resume_text):
        """验证 prompt 包含字段提取指令"""
        prompt = get_resume_extraction_prompt(standard_resume_text)
        assert "skills" in prompt.lower()
        assert "experiences" in prompt.lower()
        assert "projects" in prompt.lower()
        assert "education" in prompt.lower()
        assert "certifications" in prompt.lower()
    
    def test_prompt_emphasizes_format_preservation(self, standard_resume_text):
        """验证 prompt 强调格式保留"""
        prompt = get_resume_extraction_prompt(standard_resume_text)
        assert "preserve" in prompt.lower() or "keep" in prompt.lower()
        assert "original format" in prompt.lower() or "as-is" in prompt.lower()
    
    def test_system_prompt_defines_role(self):
        """验证 system prompt 定义角色和规则"""
        assert "resume parser" in RESUME_SYSTEM_PROMPT.lower()
        assert "skills" in RESUME_SYSTEM_PROMPT.lower()
        assert "experience" in RESUME_SYSTEM_PROMPT.lower()


# ========== Test Cases: LLM Integration ==========

class TestResumeExtraction:
    """测试实际 LLM 提取效果（需要 API Key）"""
    
    @pytest.mark.integration
    def test_extract_standard_resume(self, standard_resume_text):
        """测试标准简历提取"""
        llm = LLMService()
        prompt = get_resume_extraction_prompt(standard_resume_text)
        
        result = llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT,
            temperature=0.2,
        )
        
        # 验证核心字段
        assert len(result.skills) > 0
        assert any("Python" in skill for skill in result.skills)
        assert len(result.experiences) == 2
        assert len(result.projects) == 2
        assert len(result.education) == 1
        
        # 验证熟练度标记保留
        python_skill = next((s for s in result.skills if "Python" in s), None)
        assert python_skill is not None
        assert "Expert" in python_skill or "python" in python_skill.lower()
        
        # 验证扩展字段
        assert result.summary is not None
        assert "full-stack" in result.summary.lower() or "developer" in result.summary.lower()
        assert len(result.certifications) == 2
        assert len(result.languages) >= 2
        assert result.years_of_experience == 5
        
        # 验证工作经验细节
        current_job = result.experiences[0]
        assert current_job.company == "Tech Corp"
        assert current_job.title == "Senior Software Engineer"
        assert "Jan 2021" in current_job.start_date or "2021" in current_job.start_date
        assert "Present" in current_job.end_date or current_job.end_date is None
        assert len(current_job.achievements) > 0  # 应包含量化成果
        assert any("60%" in ach or "1M" in ach for ach in current_job.achievements)
        
        # 验证项目信息
        fastapi_project = next((p for p in result.projects if "FastAPI" in p.name), None)
        assert fastapi_project is not None
        assert fastapi_project.link == "https://github.com/johndoe/fastapi-helper"
        assert "Python" in fastapi_project.technologies
        
        # 验证教育信息
        edu = result.education[0]
        assert edu.institution == "MIT"
        assert "Computer Science" in edu.degree or "Computer Science" in edu.field_of_study
        assert edu.gpa == "3.8/4.0" or "3.8" in edu.gpa
    
    @pytest.mark.integration
    def test_extract_fresh_graduate_resume(self, fresh_graduate_resume):
        """测试应届生简历（无工作经验）"""
        llm = LLMService()
        prompt = get_resume_extraction_prompt(fresh_graduate_resume)
        
        result = llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT,
            temperature=0.2,
        )
        
        # 验证空工作经验
        assert result.experiences == []
        
        # 验证从项目推断技能
        assert len(result.skills) > 0
        assert any("Python" in s or "Java" in s for s in result.skills)
        
        # 验证项目提取
        assert len(result.projects) >= 2
        assert any("Student Management" in p.name for p in result.projects)
        
        # 验证教育信息
        assert len(result.education) == 1
        assert "Berkeley" in result.education[0].institution
        
        # 验证工作年限
        assert result.years_of_experience == 0 or result.years_of_experience is None
    
    @pytest.mark.integration
    def test_extract_minimal_resume(self, minimal_resume):
        """测试最简简历"""
        llm = LLMService()
        prompt = get_resume_extraction_prompt(minimal_resume)
        
        result = llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT,
            temperature=0.2,
        )
        
        # 验证核心字段必填
        assert len(result.education) >= 1
        assert "Computer Science" in result.education[0].degree or \
               "Computer Science" in str(result.education[0].field_of_study)
        
        # 验证技能推断（即使没有技能部分）
        assert len(result.skills) > 0  # 应从"web development"推断
        
        # 验证可选字段为空
        assert result.summary is None or result.summary == ""
        assert result.certifications == []
        assert result.languages == []
    
    @pytest.mark.integration
    def test_extract_unstructured_resume(self, unstructured_resume):
        """测试非标准格式简历"""
        llm = LLMService()
        prompt = get_resume_extraction_prompt(unstructured_resume)
        
        result = llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT,
            temperature=0.3,  # 稍高温度以应对非结构化文本
        )
        
        # 验证能从自然语言提取结构化信息
        assert any("Python" in s or "JavaScript" in s for s in result.skills)
        assert len(result.experiences) >= 1
        assert result.experiences[0].company == "CompanyA"
        assert len(result.education) >= 1
    
    @pytest.mark.integration
    def test_multilingual_extraction(self, multilingual_resume):
        """测试多语言能力提取"""
        llm = LLMService()
        prompt = get_resume_extraction_prompt(multilingual_resume)
        
        result = llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT,
            temperature=0.2,
        )
        
        # 验证语言字段提取
        assert len(result.languages) >= 4
        assert any("English" in lang and "Native" in lang for lang in result.languages)
        assert any("Mandarin" in lang or "Chinese" in lang for lang in result.languages)
        assert any("Fluent" in lang or "HSK 6" in lang for lang in result.languages)


# ========== Test Cases: Edge Cases ==========

class TestEdgeCases:
    """测试边界情况和错误处理"""
    
    @pytest.mark.integration
    def test_date_format_preservation(self):
        """测试日期格式保留"""
        resume_with_varied_dates = """
        EXPERIENCE
        Job1 | Company A | Jan 2020 - Present
        Job2 | Company B | 2018-06 to 2019-12
        Job3 | Company C | March 2017 - May 2018
        
        EDUCATION
        University X, 2016
        """
        
        llm = LLMService()
        prompt = get_resume_extraction_prompt(resume_with_varied_dates)
        result = llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT,
            temperature=0.1,
        )
        
        # 验证各种日期格式都被保留
        dates = [exp.start_date for exp in result.experiences] + \
                [exp.end_date for exp in result.experiences]
        dates = [d for d in dates if d]  # 过滤 None
        
        assert any("Jan 2020" in d for d in dates)
        assert any("2018" in d for d in dates)
        assert any("Present" in d for d in dates)
    
    @pytest.mark.integration
    def test_achievement_vs_responsibility_distinction(self):
        """测试职责与成就的区分"""
        resume_with_mixed_content = """
        EXPERIENCE
        Engineer | TechCo | 2020 - 2023
        - Developed web applications using React and Node.js
        - Improved system performance by 50% through caching optimization
        - Participated in daily standup meetings
        - Reduced bug count by 70% through implementation of automated testing
        - Maintained code documentation
        """
        
        llm = LLMService()
        prompt = get_resume_extraction_prompt(resume_with_mixed_content)
        result = llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT,
            temperature=0.1,
        )
        
        exp = result.experiences[0]
        
        # 验证量化结果进入 achievements
        achievements_text = " ".join(exp.achievements)
        assert "50%" in achievements_text or "70%" in achievements_text
        
        # 验证常规职责进入 responsibilities
        responsibilities_text = " ".join(exp.responsibilities)
        assert "Developed" in responsibilities_text or "Maintained" in responsibilities_text
    
    @pytest.mark.integration
    def test_skill_proficiency_inference(self):
        """测试技能熟练度推断"""
        resume_with_implicit_proficiency = """
        SKILLS
        - Expert in Python and Django
        - Proficient with JavaScript, React
        - Familiar with Go
        - AWS, Docker, Kubernetes
        
        (无明确标注的应保持原样)
        """
        
        llm = LLMService()
        prompt = get_resume_extraction_prompt(resume_with_implicit_proficiency)
        result = llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT,
            temperature=0.1,
        )
        
        skills_text = " ".join(result.skills)
        
        # 验证明确标注的保留
        assert "Expert" in skills_text or "Python" in skills_text
        assert "Proficient" in skills_text or "JavaScript" in skills_text
        
        # 验证未标注的直接列出
        assert "AWS" in skills_text
        assert "Docker" in skills_text


# ========== Test Cases: Error Handling ==========

class TestErrorHandling:
    """测试异常情况"""
    
    @pytest.mark.integration
    def test_empty_resume(self):
        """测试空简历处理"""
        llm = LLMService()
        prompt = get_resume_extraction_prompt("")
        
        # 应该能返回，但可能字段为空
        result = llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT,
            temperature=0.2,
        )
        
        assert isinstance(result, ResumeInfo)
    
    @pytest.mark.integration
    def test_non_resume_text(self):
        """测试非简历文本"""
        random_text = """
        This is a recipe for chocolate cake.
        Ingredients: flour, sugar, cocoa powder.
        Mix everything and bake at 350F.
        """
        
        llm = LLMService()
        prompt = get_resume_extraction_prompt(random_text)
        
        # LLM 应该能识别这不是简历，返回最小结构
        result = llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT,
            temperature=0.2,
        )
        
        # 字段应该大部分为空
        assert len(result.skills) == 0 or len(result.skills) < 3
        assert result.experiences == []


# ========== Performance Tests ==========

class TestPerformance:
    """测试性能指标"""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_token_efficiency(self, standard_resume_text):
        """测试 token 使用效率"""
        from utils.token_counter import count_tokens
        
        prompt = get_resume_extraction_prompt(standard_resume_text)
        total_tokens = count_tokens(RESUME_SYSTEM_PROMPT) + count_tokens(prompt)
        
        # 验证 token 数合理（假设简历 < 2000 tokens）
        assert total_tokens < 3000, f"Token count too high: {total_tokens}"
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_extraction_time(self, standard_resume_text):
        """测试提取速度"""
        import time
        
        llm = LLMService()
        prompt = get_resume_extraction_prompt(standard_resume_text)
        
        start = time.time()
        llm.call(
            prompt=prompt,
            response_model=ResumeInfo,
            system_prompt=RESUME_SYSTEM_PROMPT,
            temperature=0.2,
        )
        duration = time.time() - start
        
        # 验证响应时间 < 30 秒
        assert duration < 30, f"Extraction too slow: {duration:.2f}s"


# ========== Pytest Configuration ==========

def pytest_configure(config):
    """注册自定义 markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests that require OpenAI API"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (> 1s)"
    )