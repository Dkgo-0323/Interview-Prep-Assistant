# api/routes/questions.py
import logging

from fastapi import APIRouter, Depends, HTTPException

from api.main import get_session
from api.session import Session
from api.schemas import QuestionRequest, QuestionResponse
from core.generators.question_generator import generate_questions
from services.llm_service import LLMService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=QuestionResponse, summary="生成个性化面试题")
async def generate(request: QuestionRequest, session: Session = Depends(get_session)):
    """
    根据差距分析结果生成面试题。
    必须先调用 /api/analyze/stream 完成分析。

    - num_questions: 10~50，默认 10
    """
    operation = session.begin("questions")

    logger.info(f"开始生成 {request.num_questions} 道面试题")

    try:
        llm = await operation.run(LLMService)

        question_list = await operation.run(
            generate_questions,
            operation.inputs["gap"],
            operation.inputs["resume"],
            operation.inputs["jd"],
            llm,
            request.num_questions,
        )

        operation.publish("questions", question_list)

        # 序列化为 dict 列表
        questions_data = [q.model_dump() for q in question_list.questions]

        logger.info(f"题目生成成功，共 {len(questions_data)} 道")
        return QuestionResponse(
            total=len(questions_data),
            questions=questions_data,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"题目生成失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="题目生成失败，请稍后重试")
    finally:
        operation.finish()


@router.get("/cached", summary="获取缓存的面试题")
async def get_cached(current: Session = Depends(get_session)):
    """
    获取已生成的题目，无需重新调用 LLM。
    用于页面刷新后数据恢复。
    """
    session = current.snapshot()
    if "questions" not in session:
        raise HTTPException(status_code=404, detail="暂无题目，请先生成")

    questions_data = [q.model_dump() for q in session["questions"].questions]
    return QuestionResponse(total=len(questions_data), questions=questions_data)
