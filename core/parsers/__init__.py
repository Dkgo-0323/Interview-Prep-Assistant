"""
文件解析器模块

支持 TXT、PDF、DOCX 格式的文本提取。
"""

from core.parsers.exceptions import FileParseError, UnsupportedFileError
from core.parsers.txt_parser import parse_txt
from core.parsers.pdf_parser import parse_pdf
from core.parsers.docx_parser import parse_docx

__all__ = [
    # 异常
    "FileParseError",
    "UnsupportedFileError",
    # 解析器
    "parse_txt",
    "parse_pdf",
    "parse_docx",
]