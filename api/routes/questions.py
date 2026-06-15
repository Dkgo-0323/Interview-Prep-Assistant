# api/routes/questions.py
import asyncio
import logging

from fastapi import APIRouter, HTTPException

from api.main import get_session
from api.schemas import QuestionRequest, QuestionResponse
from core.generators.question_generator import generate_questions
from services.llm_service import LLMService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=QuestionResponse, summary="生成个性化面试题")
async def generate(request: QuestionRequest):
    """
    根据差距分析结果生成面试题。
    必须先调用 /api/analyze/stream 完成分析。

    - num_questions: 10~50，默认 10
    """
    session = get_session()

    # ── 前置检查 ─────────────────────────────────────────────────
    missing = []
    if "gap" not in session:
        missing.append("差距分析结果（请先完成智能分析）")
    if "jd" not in session:
        missing.append("JD 分析结果")
    if "resume" not in session:
        missing.append("简历分析结果")

    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"缺少数据：{'、'.join(missing)}",
        )

    logger.info(f"开始生成 {request.num_questions} 道面试题")

    try:
        llm = await asyncio.to_thread(LLMService)

        question_list = await asyncio.to_thread(
            generate_questions,
            session["gap"],
            session["resume"],
            session["jd"],
            llm,
            request.num_questions,
        )

        session["questions"] = question_list

        # 序列化为 dict 列表
        questions_data = [q.model_dump() for q in question_list.questions]

        logger.info(f"题目生成成功，共 {len(questions_data)} 道")
        return QuestionResponse(
            total=len(questions_data),
            questions=questions_data,
        )

    except Exception as e:
        logger.error(f"题目生成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"题目生成失败：{str(e)}")


@router.get("/cached", summary="获取缓存的面试题")
async def get_cached():
    """
    获取已生成的题目，无需重新调用 LLM。
    用于页面刷新后数据恢复。
    """
    session = get_session()
    if "questions" not in session:
        raise HTTPException(status_code=404, detail="暂无题目，请先生成")

    questions_data = [q.model_dump() for q in session["questions"].questions]
    return QuestionResponse(total=len(questions_data), questions=questions_data)