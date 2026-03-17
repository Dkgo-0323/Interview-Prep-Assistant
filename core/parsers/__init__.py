"""
文件解析器模块

提供多种文件格式的解析功能。
"""

from core.parsers.exceptions import FileParseError, UnsupportedFileError
from core.parsers.txt_parser import parse_txt
from core.parsers.pdf_parser import parse_pdf

__all__ = [
    "FileParseError",
    "UnsupportedFileError",
    "parse_txt",
    "parse_pdf",
]