"""Tests for gap analysis prompt templates."""

import json
import pytest

from models.schemas import (
    JDInfo,
    ResumeInfo,
    WorkExperience,
    Project,
    Education,
)
from prompts.gap_analysis import GAP_SYSTEM_PROMPT, get_gap_analysis_prompt


# === Fixtures ===


@pytest.fixture
def sample_jd() -> JDInfo:
    """Create a sample JD for testing."""
    return JDInfo(
        job_title="Senior Python Developer",
        company="Tech Corp",
        required_skills=["Python", "Django", "PostgreSQL", "REST APIs"],
        preferred_skills=["AWS", "Docker", "Kubernetes"],
        responsibilities=[
            "Design and implement backend services",
            "Lead code reviews",
            "Mentor junior developers",
        ],
        experience_required="5+ years",
        education_required="Bachelor's degree in Computer Science or related field",
    )


@pytest.fixture
def sample_resume() -> ResumeInfo:
    """Create a sample resume for testing."""
    return ResumeInfo(
        skills=["Python", "Flask", "MySQL", "REST APIs", "Docker"],
        experiences=[
            WorkExperience(
                company="Startup Inc",
                title="Python Developer",
                start_date="2020-01",
                end_date="Present",
                responsibilities=["Developed REST APIs", "Maintained databases"],
                achievements=["Improved API response time by 40%"],
            ),
            WorkExperience(
                company="Tech Solutions",
                title="Junior Developer",
                start_date="2018-06",
                end_date="2019-12",
                responsibilities=["Bug fixes", "Unit testing"],
                achievements=[],
            ),
        ],
        projects=[
            Project(
                name="E-commerce Platform",
                description="Built a scalable e-commerce backend",
                technologies=["Python", "Django", "PostgreSQL"],
                role="Lead Developer",
            ),
        ],
        education=[
            Education(
                institution="State University",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                graduation_date="2018-05",
                gpa="3.7/4.0",
            ),
        ],
        summary="Python developer with 5 years of experience",
        certifications=["AWS Certified Developer"],
        languages=["English", "Spanish"],
        years_of_experience=5,
    )


@pytest.fixture
def minimal_jd() -> JDInfo:
    """Create a minimal JD for edge case testing."""
    return JDInfo(
        job_title="Software Engineer",
        required_skills=["Programming"],
        responsibilities=["Write code"],
    )


@pytest.fixture
def minimal_resume() -> ResumeInfo:
    """Create a minimal resume for edge case testing."""
    return ResumeInfo(
        skills=["Python"],
        experiences=[],
        education=[
            Education(
                institution="University",
                degree="BS",
            ),
        ],
    )


# === GAP_SYSTEM_PROMPT Tests ===


class TestGapSystemPrompt:
    """Tests for GAP_SYSTEM_PROMPT constant."""

    def test_is_non_empty_string(self):
        """System prompt should be a non-empty string."""
        assert isinstance(GAP_SYSTEM_PROMPT, str)
        assert len(GAP_SYSTEM_PROMPT) > 0

    def test_defines_role(self):
        """System prompt should define the LLM's role."""
        prompt_lower = GAP_SYSTEM_PROMPT.lower()
        assert any(
            term in prompt_lower
            for term in ["career", "advisor", "analyst", "hr", "expert"]
        )

    def test_mentions_normalization(self):
        """System prompt should mention skill normalization."""
        prompt_lower = GAP_SYSTEM_PROMPT.lower()
        assert "synonym" in prompt_lower or "abbreviation" in prompt_lower

    def test_mentions_objectivity(self):
        """System prompt should emphasize objective assessment."""
        prompt_lower = GAP_SYSTEM_PROMPT.lower()
        assert "objective" in prompt_lower or "constructive" in prompt_lower


# === get_gap_analysis_prompt Tests ===


class TestGetGapAnalysisPrompt:
    """Tests for get_gap_analysis_prompt function."""

    def test_returns_string(self, sample_jd, sample_resume):
        """Function should return a string."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        assert isinstance(result, str)

    def test_returns_non_empty(self, sample_jd, sample_resume):
        """Function should return non-empty string."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        assert len(result) > 0

    def test_contains_jd_json(self, sample_jd, sample_resume):
        """Prompt should contain JD as JSON."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        # Check that key JD fields appear in the prompt
        assert "Senior Python Developer" in result
        assert "Tech Corp" in result
        assert "Django" in result

    def test_contains_resume_json(self, sample_jd, sample_resume):
        """Prompt should contain resume as JSON."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        # Check that key resume fields appear in the prompt
        assert "Startup Inc" in result
        assert "Flask" in result
        assert "E-commerce Platform" in result

    def test_contains_valid_json_blocks(self, sample_jd, sample_resume):
        """Prompt should contain parseable JSON blocks."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        
        # Extract JSON blocks (between ```json and ```)
        import re
        json_blocks = re.findall(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        
        assert len(json_blocks) == 2, "Should have exactly 2 JSON blocks (JD and Resume)"
        
        # Verify both are valid JSON
        for block in json_blocks:
            parsed = json.loads(block)
            assert isinstance(parsed, dict)

    def test_contains_scoring_weights(self, sample_jd, sample_resume):
        """Prompt should mention scoring weights."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        assert "40%" in result  # Skill weight
        assert "30%" in result  # Experience weight
        assert "20%" in result  # Education weight
        assert "10%" in result  # Project weight

    def test_contains_all_output_fields(self, sample_jd, sample_resume):
        """Prompt should list all required output fields."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        result_lower = result.lower()

        required_fields = [
            "matched_skills",
            "missing_skills",
            "skill_score",
            "experience_match",
            "experience_score",
            "education_match",
            "education_score",
            "project_relevance",
            "project_score",
            "strengths",
            "weaknesses",
            "recommendations",
        ]

        for field in required_fields:
            assert field in result_lower, f"Missing field: {field}"

    def test_excludes_overall_match_score_instruction(self, sample_jd, sample_resume):
        """Prompt should instruct LLM NOT to output overall_match_score."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        assert "overall_match_score" in result.lower()
        assert "not include" in result.lower() or "do not" in result.lower()

    def test_mentions_normalization_requirement(self, sample_jd, sample_resume):
        """Prompt should require skill normalization."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        result_lower = result.lower()
        assert "normalize" in result_lower or "synonym" in result_lower

    def test_mentions_list_length_guidance(self, sample_jd, sample_resume):
        """Prompt should specify 3-5 items for lists."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        assert "3-5" in result or "3 to 5" in result.lower()


class TestGetGapAnalysisPromptEdgeCases:
    """Edge case tests for get_gap_analysis_prompt."""

    def test_minimal_inputs(self, minimal_jd, minimal_resume):
        """Should handle minimal JD and resume."""
        result = get_gap_analysis_prompt(minimal_jd, minimal_resume)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Software Engineer" in result
        assert "Python" in result

    def test_empty_optional_fields(self, minimal_jd, minimal_resume):
        """Should handle empty optional fields gracefully."""
        result = get_gap_analysis_prompt(minimal_jd, minimal_resume)
        
        # Should still produce valid JSON blocks
        import re
        json_blocks = re.findall(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        assert len(json_blocks) == 2

    def test_special_characters_in_content(self, sample_resume):
        """Should handle special characters in JD/resume content."""
        jd_with_special = JDInfo(
            job_title="C++ Developer (Senior)",
            required_skills=["C++", "C#", "Objective-C"],
            responsibilities=["Work with C++ & C#", 'Handle "edge cases"'],
        )
        
        result = get_gap_analysis_prompt(jd_with_special, sample_resume)
        assert "C++" in result
        assert isinstance(result, str)

    def test_unicode_content(self, sample_jd):
        """Should handle unicode characters."""
        resume_with_unicode = ResumeInfo(
            skills=["Python", "日本語", "中文"],
            experiences=[],
            education=[
                Education(
                    institution="北京大学",
                    degree="Bachelor's",
                ),
            ],
        )
        
        result = get_gap_analysis_prompt(sample_jd, resume_with_unicode)
        assert "日本語" in result
        assert "北京大学" in result

    def test_long_content(self, sample_jd):
        """Should handle long resume content."""
        long_resume = ResumeInfo(
            skills=["Skill" + str(i) for i in range(50)],
            experiences=[
                WorkExperience(
                    company=f"Company {i}",
                    title=f"Title {i}",
                    responsibilities=[f"Responsibility {j}" for j in range(10)],
                )
                for i in range(10)
            ],
            education=[
                Education(
                    institution="University",
                    degree="PhD",
                ),
            ],
        )
        
        result = get_gap_analysis_prompt(sample_jd, long_resume)
        assert isinstance(result, str)
        assert "Skill49" in result
        assert "Company 9" in result


class TestPromptStructure:
    """Tests for overall prompt structure."""

    def test_has_clear_sections(self, sample_jd, sample_resume):
        """Prompt should have clear section headers."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        
        assert "## Job Description" in result or "Job Description" in result
        assert "## Resume" in result or "Resume" in result

    def test_scoring_guidelines_present(self, sample_jd, sample_resume):
        """Prompt should include scoring guidelines section."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        result_lower = result.lower()
        
        assert "scoring" in result_lower or "score" in result_lower
        assert "0-100" in result or "0 to 100" in result.lower()

    def test_output_fields_section_present(self, sample_jd, sample_resume):
        """Prompt should have an output fields section."""
        result = get_gap_analysis_prompt(sample_jd, sample_resume)
        result_lower = result.lower()
        
        assert "output" in result_lower or "extract" in result_lower or "required" in result_lower