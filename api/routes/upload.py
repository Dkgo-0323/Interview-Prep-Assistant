# api/routes/upload.py
import logging
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from api.main import get_session
from api.schemas import UploadResponse
from core.parsers.parser_factory import parse_file
from core.parsers.exceptions import UnsupportedFileError

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def _validate_extension(filename: str) -> str:
    """校验并返回文件后缀，不合法则抛 400"""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式 '{suffix}'，请上传 PDF / DOCX / TXT 文件",
        )
    return suffix


async def _read_and_parse(file: UploadFile) -> str:
    """
    读取上传文件 → 写临时文件 → 调用 parse_file() → 删除临时文件 → 返回文本
    """
    suffix = _validate_extension(file.filename)

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过 10MB 限制")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="上传的文件为空")

    # 写入临时文件（parse_file 需要文件路径）
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        text = parse_file(tmp_path)

        if not text or len(text.strip()) < 10:
            raise HTTPException(
                status_code=422,
                detail="文件内容无法解析，请确认文件不是空文件或图片扫描件",
            )

        return text.strip()

    except HTTPException:
        raise  # 直接透传，不包装
    except UnsupportedFileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"文件解析失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"文件解析失败：{str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
            logger.debug(f"临时文件已清理: {tmp_path}")


@router.post("/jd", response_model=UploadResponse, summary="上传职位描述 (JD)")
async def upload_jd(file: UploadFile = File(...)):
    """
    上传 JD 文件（PDF / DOCX / TXT），解析后存入 session。
    重复上传会覆盖，并自动清除下游的分析缓存。
    """
    logger.info(f"收到 JD 上传请求: {file.filename}")

    text = await _read_and_parse(file)

    session = get_session()
    session["jd_text"] = text
    # 清除依赖 JD 的下游缓存，防止数据不一致
    for key in ("jd", "gap", "questions"):
        session.pop(key, None)

    logger.info(f"JD 解析成功，字符数: {len(text)}")
    return UploadResponse(
        filename=file.filename,
        char_count=len(text),
        preview=text[:200] + ("..." if len(text) > 200 else ""),
    )


@router.post("/resume", response_model=UploadResponse, summary="上传简历")
async def upload_resume(file: UploadFile = File(...)):
    """
    上传简历文件（PDF / DOCX / TXT），解析后存入 session。
    重复上传会覆盖，并自动清除下游的分析缓存。
    """
    logger.info(f"收到简历上传请求: {file.filename}")

    text = await _read_and_parse(file)

    session = get_session()
    session["resume_text"] = text
    # 清除依赖简历的下游缓存
    for key in ("resume", "gap", "questions", "profile"):
        session.pop(key, None)

    logger.info(f"简历解析成功，字符数: {len(text)}")
    return UploadResponse(
        filename=file.filename,
        char_count=len(text),
        preview=text[:200] + ("..." if len(text) > 200 else ""),
    )


@router.get("/status", summary="查看上传状态")
async def upload_status():
    """检查哪些文件已上传，前端用于判断是否可以开始分析"""
    session = get_session()
    return {
        "jd_uploaded": "jd_text" in session,
        "resume_uploaded": "resume_text" in session,
        "ready_to_analyze": "jd_text" in session and "resume_text" in session,
        "jd_char_count": len(session["jd_text"]) if "jd_text" in session else 0,
        "resume_char_count": len(session["resume_text"]) if "resume_text" in session else 0,
    }


@router.delete("/clear", summary="清空 session（重新开始）")
async def clear_session():
    """清空所有上传文件和分析缓存，用于演示重置"""
    session = get_session()
    session.clear()
    logger.info("Session 已清空")
    return {"success": True, "message": "已重置，可重新上传文件"}