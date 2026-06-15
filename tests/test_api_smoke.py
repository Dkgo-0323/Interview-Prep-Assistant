# tests/test_api_smoke.py
"""
冒烟测试 - 验证所有接口能正常响应（不调用真实 LLM）
运行：python -m pytest tests/test_api_smoke.py -v -s
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def setup_function():
    """每个测试前清空 session"""
    client.delete("/api/upload/clear")


# ── 系统接口 ─────────────────────────────────────────────────────

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    print("✅ 根路由正常")


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "session_keys" in body
    print(f"✅ 健康检查通过，session keys: {body['session_keys']}")


def test_docs():
    r = client.get("/docs")
    assert r.status_code == 200
    print("✅ Swagger 文档可访问")


# ── 上传接口 ─────────────────────────────────────────────────────

def test_upload_status_empty():
    r = client.get("/api/upload/status")
    assert r.status_code == 200
    body = r.json()
    assert body["jd_uploaded"] is False
    assert body["resume_uploaded"] is False
    assert body["ready_to_analyze"] is False
    print("✅ 空 session 状态检查正常")


def test_upload_invalid_extension():
    r = client.post(
        "/api/upload/jd",
        files={"file": ("resume.exe", b"fake binary", "application/octet-stream")},
    )
    assert r.status_code == 400
    assert "不支持" in r.json()["detail"]
    print("✅ 非法格式拦截正常")


def test_upload_empty_file():
    r = client.post(
        "/api/upload/jd",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert r.status_code == 400
    print("✅ 空文件拦截正常")


def test_upload_txt_jd():
    """上传真实 TXT 文件测试解析"""
    fake_jd = b"""
    Software Engineer - Backend
    Requirements:
    - Python 3+ years experience
    - FastAPI or Django
    - SQL databases
    Responsibilities:
    - Build REST APIs
    - Code review
    """
    r = client.post(
        "/api/upload/jd",
        files={"file": ("jd.txt", fake_jd, "text/plain")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["char_count"] > 0
    assert len(body["preview"]) > 0
    print(f"✅ JD 上传解析成功，字符数: {body['char_count']}")


def test_upload_txt_resume():
    fake_resume = b"""
    John Doe
    Skills: Python, FastAPI, PostgreSQL, Docker
    Experience:
    - Backend Engineer at TechCorp (2021-2024)
      - Built REST APIs with FastAPI
      - Managed PostgreSQL databases
    Education:
    - B.S. Computer Science, MIT, 2021
    """
    r = client.post(
        "/api/upload/resume",
        files={"file": ("resume.txt", fake_resume, "text/plain")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    print(f"✅ 简历上传解析成功，字符数: {body['char_count']}")


def test_upload_status_after_upload():
    """上传文件后状态应更新"""
    # 先上传两个文件
    client.post("/api/upload/jd",
                files={"file": ("jd.txt", b"Python Engineer needed, requires Python skills and REST API experience", "text/plain")})
    client.post("/api/upload/resume",
                files={"file": ("resume.txt", b"John Doe, Python developer, 3 years experience with REST API and databases", "text/plain")})

    r = client.get("/api/upload/status")
    body = r.json()
    assert body["jd_uploaded"] is True
    assert body["resume_uploaded"] is True
    assert body["ready_to_analyze"] is True
    print("✅ 上传后状态更新正常")


def test_clear_session():
    # 先上传
    client.post("/api/upload/jd",
                files={"file": ("jd.txt", b"Some job description content here", "text/plain")})
    # 再清空
    r = client.delete("/api/upload/clear")
    assert r.status_code == 200

    # 验证清空
    status = client.get("/api/upload/status").json()
    assert status["jd_uploaded"] is False
    print("✅ Session 清空正常")


# ── 分析接口 ─────────────────────────────────────────────────────

def test_analyze_without_upload():
    """未上传文件时，SSE 应推送 error 事件"""
    with client.stream("GET", "/api/analyze/stream") as r:
        assert r.status_code == 200  # SSE 本身返回 200
        content = "".join(r.iter_lines())

    assert "error" in content
    print(f"✅ 未上传文件保护正常，收到: {content[:100]}")


def test_analyze_result_not_found():
    r = client.get("/api/analyze/result")
    assert r.status_code == 404
    print("✅ 无分析结果时 404 正常")


# ── 题目接口 ─────────────────────────────────────────────────────

def test_questions_without_analysis():
    r = client.post("/api/questions/generate", json={"num_questions": 10})
    assert r.status_code == 400
    print("✅ 未分析时题目生成保护正常")


def test_questions_invalid_num():
    """题目数量超出范围应被 Pydantic 拦截"""
    r = client.post("/api/questions/generate", json={"num_questions": 5})
    assert r.status_code == 422  # Pydantic validation error
    print("✅ 题目数量校验正常（小于10被拦截）")

    r = client.post("/api/questions/generate", json={"num_questions": 100})
    assert r.status_code == 422  # Pydantic validation error
    print("✅ 题目数量校验正常（大于50被拦截）")


def test_questions_cached_not_found():
    r = client.get("/api/questions/cached")
    assert r.status_code == 404
    print("✅ 无缓存题目时 404 正常")


# ── 画像接口 ─────────────────────────────────────────────────────

def test_profile_without_resume():
    r = client.post("/api/profile/generate")
    assert r.status_code == 400
    print("✅ 未上传简历时画像生成保护正常")


def test_profile_with_resume():
    client.post("/api/upload/resume",
                files={"file": ("resume.txt", b"John Doe, Python developer with 3 years experience in REST API and databases", "text/plain")})
    r = client.post("/api/profile/generate")
    assert r.status_code == 200
    assert r.json()["success"] is True
    print("✅ 画像接口（占位）正常")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])