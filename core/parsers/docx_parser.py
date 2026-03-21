"""
DOCX 文件解析器

提取 DOCX 文档的纯文本内容，保持段落和表格的原始顺序。
"""

from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from core.parsers.exceptions import FileParseError
from utils.logger import get_logger
from utils.text_cleaner import clean_text

logger = get_logger(__name__)

# 最大字符数限制（约等于20页A4文档）
MAX_CHARACTERS = 50000


def parse_docx(file_path: str | Path) -> str:
    """
    解析 DOCX 文件，提取纯文本。

    保持段落和表格在文档中的原始顺序。
    表格单元格用制表符分隔，行用换行分隔。
    忽略页眉、页脚、文本框、图片和嵌套表格。

    参数:
        file_path: 文件路径，接受 str 或 Path 对象

    返回:
        经过 clean_text 处理的纯文本内容

    异常:
        FileParseError: 文件不存在、损坏、加密或没有可提取的有效文本
    """
    file_path = Path(file_path)

    # 1. 文件存在性检查
    if not file_path.exists():
        logger.error(f"文件不存在: {file_path}")
        raise FileParseError(f"文件不存在: {file_path}")

    # 2. 打开文档
    try:
        doc = Document(file_path)
    except ValueError as e:
        # python-docx 对加密文件抛出 ValueError: "File is not a zip file"
        error_msg = str(e).lower()
        if "zip" in error_msg:
            logger.error(f"DOCX 文件已加密或不是有效的 DOCX 文件: {file_path}")
            raise FileParseError(f"无法打开文件，可能已加密或不是有效的 DOCX 文件: {file_path}")
        raise FileParseError(f"解析 DOCX 文件失败: {file_path} - {e}")
    except Exception as e:
        logger.error(f"打开 DOCX 文件失败: {file_path} - {e}")
        raise FileParseError(f"解析 DOCX 文件失败: {file_path} - {e}")

    # 3. 按原始顺序提取内容
    content_parts = []
    raw_char_count = 0
    truncated = False

    for element in doc.element.body:
        # 检查字符数限制
        if raw_char_count >= MAX_CHARACTERS:
            truncated = True
            break

        # 段落元素
        if element.tag == qn("w:p"):
            paragraph = Paragraph(element, doc)
            text = paragraph.text.strip()
            if text:
                content_parts.append(text)
                raw_char_count += len(text)

        # 表格元素
        elif element.tag == qn("w:tbl"):
            table = Table(element, doc)
            table_text = _extract_table_text(table)
            if table_text:
                content_parts.append(table_text)
                raw_char_count += len(table_text)

    if truncated:
        logger.warning(
            f"文档超过 {MAX_CHARACTERS} 字符限制，已截断: {file_path}"
        )

    # 4. 合并文本
    raw_text = "\n\n".join(content_parts)

    # 5. 清理文本
    cleaned = clean_text(raw_text)

    # 6. 空文本检查
    if not cleaned:
        logger.error(f"DOCX 文件无有效文本内容: {file_path}")
        raise FileParseError(f"DOCX 文件无有效文本内容: {file_path}")

    logger.info(
        f"成功解析 DOCX: {file_path.name}, "
        f"提取 {len(content_parts)} 个内容块, "
        f"{len(cleaned)} 字符"
    )

    return cleaned


def _extract_table_text(table: Table) -> str:
    """
    提取表格文本。

    单元格用制表符分隔，行用换行分隔。
    跳过完全空白的行，折叠连续的制表符。

    参数:
        table: python-docx 的 Table 对象

    返回:
        格式化的表格文本
    """
    rows_text = []

    for row in table.rows:
        cells_text = []
        for cell in row.cells:
            # 获取单元格文本，合并多段落
            cell_content = " ".join(
                p.text.strip() for p in cell.paragraphs if p.text.strip()
            )
            cells_text.append(cell_content)

        # 用制表符连接单元格
        row_text = "\t".join(cells_text)

        # 折叠连续制表符，去除首尾空白
        row_text = "\t".join(part for part in row_text.split("\t") if part)

        # 跳过空行
        if row_text:
            rows_text.append(row_text)

    return "\n".join(rows_text)