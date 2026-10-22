# api/main.py
import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders
from api.session import COOKIE_NAME, Session, SessionExpired, SessionStore

# ── 日志配置（最先执行）────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


session_store = SessionStore(
    ttl=float(os.getenv("SESSION_TTL_SECONDS", "1800")),
    capacity=int(os.getenv("SESSION_MAX_COUNT", "100")),
)


def get_session(request: Request) -> Session:
    return session_store.resolve(request.cookies.get(COOKIE_NAME))


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


class PrivateAPIResponses:
    """Add privacy headers without buffering StreamingResponse bodies."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        async def private_send(message):
            if message["type"] == "http.response.start" and scope["path"].startswith("/api/"):
                MutableHeaders(scope=message)["Cache-Control"] = "no-store"
            await send(message)
        await self.app(scope, receive, private_send)


app.add_middleware(PrivateAPIResponses)


@app.exception_handler(SessionExpired)
async def expired_session(request: Request, exc: SessionExpired):
    response = JSONResponse({"detail": exc.detail}, status_code=410)
    response.delete_cookie(COOKIE_NAME)
    response.headers["Cache-Control"] = "no-store"
    return response


@app.post("/api/session", tags=["会话"])
async def initialize_session(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    session = session_store.resolve(token) if token else session_store.create()
    response = JSONResponse({"success": True, "idle_timeout_seconds": session_store.ttl})
    response.set_cookie(
        COOKIE_NAME, session.token, httponly=True, samesite="lax",
        secure=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
    )
    response.headers["Cache-Control"] = "no-store"
    return response

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
    """不访问或创建访客资料的公共健康检查。"""
    return {
        "status": "ok",
    }


@app.get("/", tags=["系统"])
async def root():
    return {
        "message": "Interview Prep Assistant API v1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
