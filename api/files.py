"""Shared upload parser; no routing, identity, model or database dependency."""
import logging
import os
import tempfile
from pathlib import Path

from fastapi import HTTPException, UploadFile
from core.parsers.parser_factory import parse_file
from core.parsers.exceptions import UnsupportedFileError

logger = logging.getLogger(__name__)


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
