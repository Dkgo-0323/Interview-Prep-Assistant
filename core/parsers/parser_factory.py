"""
统一文件解析入口。

根据文件后缀自动路由到对应的解析器。
"""

from pathlib import Path
from typing import Callable

from core.parsers.exceptions import UnsupportedFileError
from core.parsers.txt_parser import parse_txt
from core.parsers.pdf_parser import parse_pdf
from core.parsers.docx_parser import parse_docx
from utils.logger import get_logger

logger = get_logger(__name__)

# 后缀 → 解析器映射（实现细节，不对外暴露）
_PARSER_MAP: dict[str, Callable[[str | Path], str]] = {
    ".txt": parse_txt,
    ".pdf": parse_pdf,
    ".docx": parse_docx,
}


def parse_file(file_path: str | Path) -> str:
    """
    统一文件解析入口。根据文件后缀自动选择解析器。
    
    Args:
        file_path: 文件路径
        
    Returns:
        清洗后的文本内容
        
    Raises:
        UnsupportedFileError: 不支持的文件格式
        FileParseError: 解析失败（含文件不存在、损坏、加密等）
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    parser_fn = _PARSER_MAP.get(suffix)
    
    if parser_fn is None:
        supported = ", ".join(sorted(_PARSER_MAP.keys()))
        raise UnsupportedFileError(
            f"不支持的文件格式: '{suffix}'。支持的格式: {supported}"
        )
    
    logger.info(f"解析文件: {file_path.name} (格式: {suffix})")
    
    return parser_fn(file_path)