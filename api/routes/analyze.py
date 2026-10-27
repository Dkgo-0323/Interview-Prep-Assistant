"""Snapshot-based SSE analysis: late work cannot restore invalidated input."""
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from api.events import _sse
from api.main import get_session
from api.session import Session
from core.analyzers.jd_analyzer import analyze_jd
from core.analyzers.resume_analyzer import analyze_resume
from core.analyzers.gap_analyzer import analyze_gap
from services.llm_service import LLMService

logger = logging.getLogger(__name__)
router = APIRouter()


async def _stream_analysis(session: Session):
    operation = None
    try:
        operation = session.begin("analysis")
        llm = await operation.run(LLMService)
        yield _sse("jd_start", "正在解析职位描述... (1/3)")
        jd = await operation.run(analyze_jd, operation.inputs["jd_text"], llm)
        operation.publish("jd", jd)
        yield _sse("jd_done", f"职位描述解析完成：{jd.job_title}", {
            "job_title": jd.job_title, "company": jd.company,
            "required_skills_count": len(jd.required_skills),
        })
        yield _sse("resume_start", "正在解析简历... (2/3)")
        resume = await operation.run(analyze_resume, operation.inputs["resume_text"], llm)
        operation.publish("resume", resume)
        yield _sse("resume_done", "简历解析完成", {
            "skills_count": len(resume.skills),
            "experiences_count": len(resume.experiences),
            "projects_count": len(resume.projects),
        })
        yield _sse("gap_start", "正在计算匹配度，请稍候... (3/3)")
        gap = await operation.run(analyze_gap, jd, resume, llm)
        operation.publish("gap", gap)
        yield _sse("complete", "分析完成！", gap.model_dump())
    except HTTPException as exc:
        yield _sse("error", exc.detail, {"status": exc.status_code})
    except Exception:
        logger.exception("分析失败")
        yield _sse("error", "分析失败，请检查服务配置或稍后重试")
    finally:
        if operation:
            operation.finish()


@router.get("/stream", summary="流式分析 (SSE)")
async def analyze_stream(session: Session = Depends(get_session)):
    return StreamingResponse(
        _stream_analysis(session), media_type="text/event-stream",
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
    )


@router.get("/result", summary="获取当前访客的分析结果")
async def get_result(current: Session = Depends(get_session)):
    session = current.snapshot()
    if "gap" not in session:
        raise HTTPException(404, "暂无分析结果，请先进行分析")
    return {"success": True, "data": session["gap"].model_dump()}
