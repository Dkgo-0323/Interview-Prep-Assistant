# api/routes/upload.py
import logging

from fastapi import APIRouter, Depends, UploadFile, File

from api.main import get_session
from api.session import Session
from api.schemas import UploadResponse
from api.files import _read_and_parse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/jd", response_model=UploadResponse, summary="上传职位描述 (JD)")
async def upload_jd(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """
    上传 JD 文件（PDF / DOCX / TXT），解析后存入 session。
    重复上传会覆盖，并自动清除下游的分析缓存。
    """
    logger.info(f"收到 JD 上传请求: {file.filename}")

    ticket = session.upload_ticket("jd_text")
    text = await _read_and_parse(file)
    session.replace_input("jd_text", text, ticket)

    logger.info(f"JD 解析成功，字符数: {len(text)}")
    return UploadResponse(
        filename=file.filename,
        char_count=len(text),
        preview=text[:200] + ("..." if len(text) > 200 else ""),
    )


@router.post("/resume", response_model=UploadResponse, summary="上传简历")
async def upload_resume(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """
    上传简历文件（PDF / DOCX / TXT），解析后存入 session。
    重复上传会覆盖，并自动清除下游的分析缓存。
    """
    logger.info(f"收到简历上传请求: {file.filename}")

    ticket = session.upload_ticket("resume_text")
    text = await _read_and_parse(file)
    session.replace_input("resume_text", text, ticket)

    logger.info(f"简历解析成功，字符数: {len(text)}")
    return UploadResponse(
        filename=file.filename,
        char_count=len(text),
        preview=text[:200] + ("..." if len(text) > 200 else ""),
    )


@router.get("/status", summary="查看上传状态")
async def upload_status(current: Session = Depends(get_session)):
    """检查哪些文件已上传，前端用于判断是否可以开始分析"""
    session = current.snapshot()
    return {
        "jd_uploaded": "jd_text" in session,
        "resume_uploaded": "resume_text" in session,
        "ready_to_analyze": "jd_text" in session and "resume_text" in session,
        "jd_char_count": len(session["jd_text"]) if "jd_text" in session else 0,
        "resume_char_count": len(session["resume_text"]) if "resume_text" in session else 0,
    }


@router.delete("/clear", summary="清空 session（重新开始）")
async def clear_session(session: Session = Depends(get_session)):
    """清空所有上传文件和分析缓存，用于演示重置"""
    session.clear()
    logger.info("Session 已清空")
    return {"success": True, "message": "已重置，可重新上传文件"}
