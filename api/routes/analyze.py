# api/routes/analyze.py
import asyncio
import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.main import get_session
from core.analyzers.jd_analyzer import analyze_jd
from core.analyzers.resume_analyzer import analyze_resume
from core.analyzers.gap_analyzer import analyze_gap
from services.llm_service import LLMService

logger = logging.getLogger(__name__)
router = APIRouter()


def _sse(step: str, message: str, data: dict = None) -> str:
    """
    格式化一条 SSE 消息。
    SSE 协议：每条消息 'data: <json>\\n\\n'
    """
    payload = {"step": step, "message": message}
    if data is not None:
        payload["data"] = data
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def _stream_analysis():
    """
    核心分析流程，每步完成后 yield 一个 SSE 事件。

    用 asyncio.to_thread() 把同步 LLM 调用转为异步，
    防止阻塞 FastAPI 事件循环，确保 SSE 事件能实时推送。
    """
    session = get_session()

    # ── 前置检查 ─────────────────────────────────────────────────
    if "jd_text" not in session:
        yield _sse("error", "请先上传职位描述 (JD) 文件")
        return
    if "resume_text" not in session:
        yield _sse("error", "请先上传简历文件")
        return

    jd_text = session["jd_text"]
    resume_text = session["resume_text"]

    # LLMService 创建一次，三步复用（节省初始化开销）
    # ⚠️ LLMService.__init__ 是同步的，放到线程里初始化
    try:
        llm = await asyncio.to_thread(LLMService)
    except Exception as e:
        logger.error(f"LLMService 初始化失败: {e}")
        yield _sse("error", f"LLM 服务初始化失败，请检查 API Key 配置：{str(e)}")
        return

    # ── Step 1: 分析 JD ──────────────────────────────────────────
    yield _sse("jd_start", "正在解析职位描述... (1/3)")
    await asyncio.sleep(0)  # 让事件循环刷新，确保事件立即发出

    try:
        jd_result = await asyncio.to_thread(analyze_jd, jd_text, llm)
        session["jd"] = jd_result

        yield _sse(
            "jd_done",
            f"职位描述解析完成：{jd_result.job_title}",
            data={
                "job_title": jd_result.job_title,
                "company": jd_result.company,
                "required_skills_count": len(jd_result.required_skills),
            },
        )
    except Exception as e:
        logger.error(f"JD 分析失败: {e}", exc_info=True)
        yield _sse("error", f"职位描述解析失败：{str(e)}")
        return

    # ── Step 2: 分析简历 ─────────────────────────────────────────
    yield _sse("resume_start", "正在解析简历... (2/3)")
    await asyncio.sleep(0)

    try:
        resume_result = await asyncio.to_thread(analyze_resume, resume_text, llm)
        session["resume"] = resume_result

        yield _sse(
            "resume_done",
            "简历解析完成",
            data={
                "skills_count": len(resume_result.skills),
                "experiences_count": len(resume_result.experiences),
                "projects_count": len(resume_result.projects),
            },
        )
    except Exception as e:
        logger.error(f"简历分析失败: {e}", exc_info=True)
        yield _sse("error", f"简历解析失败：{str(e)}")
        return

    # ── Step 3: 差距分析 ─────────────────────────────────────────
    yield _sse("gap_start", "正在计算匹配度，请稍候... (3/3)")
    await asyncio.sleep(0)

    try:
        gap_result = await asyncio.to_thread(
            analyze_gap, session["jd"], session["resume"], llm
        )
        session["gap"] = gap_result

        yield _sse(
            "complete",
            "分析完成！",
            data=gap_result.model_dump(),  # Pydantic v2
        )
    except Exception as e:
        logger.error(f"差距分析失败: {e}", exc_info=True)
        yield _sse("error", f"匹配度计算失败：{str(e)}")
        return


@router.get("/stream", summary="流式分析 (SSE)")
async def analyze_stream():
    """
    启动三步智能分析，通过 SSE 实时推送进度。

    事件顺序：
      jd_start → jd_done → resume_start → resume_done → gap_start → complete

    前端接入示例：
    ```js
    const es = new EventSource('http://localhost:8000/api/analyze/stream');
    es.onmessage = (e) => {
      const { step, message, data } = JSON.parse(e.data);
      console.log(step, message);
      if (step === 'complete') { es.close(); }
    };
    ```
    """
    return StreamingResponse(
        _stream_analysis(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # 禁止 Nginx 缓冲，保证实时性
            "Connection": "keep-alive",
        },
    )


@router.get("/result", summary="获取缓存的分析结果（非流式）")
async def get_result():
    """
    获取已完成的分析结果，用于页面刷新后数据恢复。
    如果尚未分析，返回 404。
    """
    session = get_session()
    if "gap" not in session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="暂无分析结果，请先进行分析")

    return {
        "success": True,
        "data": session["gap"].model_dump(),
    }