"""
PDF 文件解析模块

使用 pdfplumber 提取 PDF 文本内容，处理加密、损坏、扫描件等边缘情况。
"""

from pathlib import Path

import pdfplumber
from pdfplumber.pdf import PDF

from core.parsers.exceptions import FileParseError
from utils.logger import get_logger
from utils.text_cleaner import clean_text

logger = get_logger(__name__)

# 配置常量
MAX_PAGES = 20
SCANNED_PAGE_TEXT_THRESHOLD = 50  # 少于此字符数且有图片 → 判定为扫描页


def parse_pdf(file_path: str | Path) -> str:
    """
    解析 PDF 文件，提取纯文本内容
    
    Args:
        file_path: PDF 文件路径
        
    Returns:
        str: 清洗后的纯文本
        
    Raises:
        FileParseError: 
            - 文件不存在
            - PDF 已加密
            - PDF 文件损坏
            - 检测到扫描件（所有页均为扫描页）
            - 无有效文本内容
    """
    # 转换为 Path 对象
    path = Path(file_path)
    logger.info(f"开始解析 PDF 文件: {path.name}")
    
    # 检查文件存在性
    if not path.exists():
        logger.error(f"文件不存在: {path}")
        raise FileParseError(f"文件不存在: {path}")
    
    # 打开并解析 PDF
    pdf = _open_pdf(path)
    
    try:
        # 提取文本
        extracted_text = _extract_text_from_pdf(pdf, path.name)
    finally:
        pdf.close()
    
    # 清洗文本
    cleaned = clean_text(extracted_text)
    
    # 检查清洗后是否为空
    if not cleaned:
        logger.error(f"PDF 清洗后无有效文本: {path.name}")
        raise FileParseError("PDF 无有效文本内容")
    
    logger.info(f"PDF 解析完成: {path.name}, 提取 {len(cleaned)} 字符")
    return cleaned


def _open_pdf(path: Path) -> PDF:
    """
    打开 PDF 文件，处理各种异常情况
    
    Args:
        path: PDF 文件路径
        
    Returns:
        PDF: pdfplumber PDF 对象
        
    Raises:
        FileParseError: 加密/损坏/无法解析
    """
    try:
        return pdfplumber.open(path)
    
    except pdfplumber.pdfminer.pdfparser.PDFSyntaxError as e:
        logger.error(f"PDF 文件损坏: {path.name}, 错误: {e}")
        raise FileParseError("PDF 文件损坏，请检查文件完整性")
    
    except pdfplumber.pdfminer.pdfdocument.PDFPasswordIncorrect as e:
        logger.error(f"PDF 已加密: {path.name}")
        raise FileParseError("PDF 已加密，请解除密码保护后重试")
    
    except pdfplumber.pdfminer.pdfdocument.PDFEncryptionError as e:
        logger.error(f"PDF 加密错误: {path.name}, 错误: {e}")
        raise FileParseError("PDF 已加密，请解除密码保护后重试")
    
    except Exception as e:
        logger.error(f"PDF 解析失败: {path.name}, 错误类型: {type(e).__name__}, 错误: {e}")
        raise FileParseError(f"PDF 解析失败: {str(e)}")


def _extract_text_from_pdf(pdf: PDF, filename: str) -> str:
    """
    从 PDF 中提取文本，处理页数限制和扫描件检测
    
    Args:
        pdf: pdfplumber PDF 对象
        filename: 文件名（用于日志）
        
    Returns:
        str: 提取的原始文本
        
    Raises:
        FileParseError: 检测到扫描件
    """
    total_pages = len(pdf.pages)
    
    # 页数限制
    if total_pages > MAX_PAGES:
        logger.warning(
            f"PDF 页数超限: {filename}, 共 {total_pages} 页, "
            f"只处理前 {MAX_PAGES} 页"
        )
        pages_to_process = pdf.pages[:MAX_PAGES]
    else:
        pages_to_process = pdf.pages
    
    logger.debug(f"处理 {len(pages_to_process)} 页")
    
    # 逐页提取
    text_parts: list[str] = []
    scanned_page_count = 0
    
    for i, page in enumerate(pages_to_process, start=1):
        page_text = page.extract_text() or ""
        page_text = page_text.strip()
        
        # 扫描件检测：文本极少 + 有图片
        has_images = bool(page.images)
        is_scanned_page = len(page_text) < SCANNED_PAGE_TEXT_THRESHOLD and has_images
        
        if is_scanned_page:
            scanned_page_count += 1
            logger.debug(f"第 {i} 页疑似扫描页: 文本长度={len(page_text)}, 有图片={has_images}")
        
        # 跳过空白页
        if page_text:
            text_parts.append(page_text)
            logger.debug(f"第 {i} 页提取 {len(page_text)} 字符")
        else:
            logger.debug(f"第 {i} 页为空白页，跳过")
    
    # 判断是否所有页都是扫描页
    processed_count = len(pages_to_process)
    if scanned_page_count == processed_count and processed_count > 0:
        logger.error(
            f"检测到扫描件 PDF: {filename}, "
            f"全部 {processed_count} 页均为扫描页"
        )
        raise FileParseError(
            "检测到扫描件 PDF，无法提取文本。"
            "请使用 OCR 工具转换后重试，或上传文本型 PDF"
        )
    
    # 拼接所有页
    return "\n\n".join(text_parts)