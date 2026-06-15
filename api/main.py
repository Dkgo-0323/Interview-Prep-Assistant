# api/main.py
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── 日志配置（最先执行）────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ── Session 存储（单用户演示版）─────────────────────────────────
# 存储结构：
#   jd_text: str              原始JD文本
#   resume_text: str          原始简历文本
#   jd: JDInfo                结构化JD
#   resume: ResumeInfo        结构化简历
#   gap: GapAnalysis          差距分析结果
#   questions: QuestionList   生成的题目
#   profile: UserProfile      求职画像
# ⚠️ 生产环境替换为 Redis
_session_store: dict = {}


def get_session() -> dict:
    """全局 session 访问入口"""
    return _session_store


# ── 生命周期 ────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Interview Prep Assistant API 启动成功")
    logger.info("📖 Swagger 文档: http://localhost:8000/docs")
    yield
    logger.info("👋 API 服务已关闭")


# ── 创建应用 ────────────────────────────────────────────────────
app = FastAPI(
    title="Interview Prep Assistant API",
    description="AI 面试准备助手 - FastAPI 后端",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 注册路由（在应用创建后导入，避免循环依赖）────────────────────
from api.routes import upload, analyze, questions, profile  # noqa: E402

app.include_router(upload.router,    prefix="/api/upload",    tags=["文件上传"])
app.include_router(analyze.router,   prefix="/api/analyze",   tags=["智能分析"])
app.include_router(questions.router, prefix="/api/questions", tags=["面试题生成"])
app.include_router(profile.router,   prefix="/api/profile",   tags=["求职画像"])


# ── 系统路由 ────────────────────────────────────────────────────
@app.get("/api/health", tags=["系统"])
async def health_check():
    """服务健康检查 + session 状态查看"""
    session = get_session()
    return {
        "status": "ok",
        "session_keys": list(session.keys()),
    }


@app.get("/", tags=["系统"])
async def root():
    return {
        "message": "Interview Prep Assistant API v1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }