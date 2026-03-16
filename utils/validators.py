"""
Input Validators
文件上传和文本内容的验证工具

统一返回格式: Tuple[bool, str] — (是否通过, 描述信息)
聚合验证返回: Tuple[bool, List[str]] — (是否通过, 错误列表)
"""

from typing import Tuple, List
from pathlib import Path
from config import ALLOWED_EXTENSIONS, UPLOAD_MAX_SIZE_MB
from utils.logger import get_logger

logger = get_logger(__name__)

# ── 内部常量 ──
MIN_LENGTH = {
    "jd": 100,
    "resume": 50,
    "general": 50,
}


def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """
    验证文件扩展名是否在允许列表中
    
    Args:
        filename: 文件名（可包含路径）
        
    Returns:
        (是否通过, 描述信息)
        
    Examples:
        >>> validate_file_extension("report.pdf")
        (True, "文件格式有效: .pdf")
        
        >>> validate_file_extension("malware.exe")
        (False, "不支持的文件格式: .exe, 允许: .pdf, .docx, .txt")
    """
    if not filename:
        logger.warning("文件名为空")
        return False, "文件名为空"
    
    # 提取扩展名（统一转小写）
    ext = Path(filename).suffix.lower()
    
    if not ext:
        logger.warning(f"文件无扩展名: {filename}")
        return False, f"文件无扩展名: {filename}"
    
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        logger.warning(f"不支持的文件格式: {ext}, 文件: {filename}")
        return False, f"不支持的文件格式: {ext}, 允许: {allowed}"
    
    logger.debug(f"文件格式验证通过: {ext}")
    return True, f"文件格式有效: {ext}"


def validate_file_size(file_size: int) -> Tuple[bool, str]:
    """
    验证文件大小是否在限制内
    
    Args:
        file_size: 文件大小（单位: bytes）
        
    Returns:
        (是否通过, 描述信息)
        
    Examples:
        >>> validate_file_size(2 * 1024 * 1024)  # 2MB
        (True, "文件大小有效: 2.0MB")
        
        >>> validate_file_size(15 * 1024 * 1024)  # 15MB
        (False, "文件过大: 15.0MB, 上限: 10MB")
    """
    # 检查无效大小
    if file_size < 0:
        logger.warning(f"无效的文件大小: {file_size}")
        return False, f"无效的文件大小: {file_size}"
    
    # 检查空文件
    if file_size == 0:
        logger.warning("文件为空（0字节）")
        return False, "文件为空"
    
    # 转换为 MB
    size_mb = file_size / (1024 * 1024)
    
    # 检查上限
    if size_mb > UPLOAD_MAX_SIZE_MB:
        logger.warning(f"文件过大: {size_mb:.1f}MB > {UPLOAD_MAX_SIZE_MB}MB")
        return False, f"文件过大: {size_mb:.1f}MB, 上限: {UPLOAD_MAX_SIZE_MB}MB"
    
    logger.debug(f"文件大小验证通过: {size_mb:.1f}MB")
    return True, f"文件大小有效: {size_mb:.1f}MB"


def validate_text_content(
    text: str, 
    content_type: str = "general"
) -> Tuple[bool, str]:
    """
    验证文本内容的有效性
    
    Args:
        text: 待验证的文本
        content_type: 内容类型 ("jd" | "resume" | "general")
            - "jd": 职位描述，最小长度 100
            - "resume": 简历，最小长度 50
            - "general": 通用文本，最小长度 50
            
    Returns:
        (是否通过, 描述信息)
        
    Examples:
        >>> validate_text_content("Python Developer with 5 years...", "jd")
        (True, "文本内容有效（长度: 120）")
        
        >>> validate_text_content("   ", "resume")
        (False, "文本内容为空或仅包含空白字符")
    """
    # 检查 None
    if text is None:
        logger.warning("文本为 None")
        return False, "文本为空（None）"
    
    # 检查空字符串
    if not text:
        logger.warning("文本为空字符串")
        return False, "文本为空字符串"
    
    # 检查纯空白
    if not text.strip():
        logger.warning("文本仅包含空白字符")
        return False, "文本内容为空或仅包含空白字符"
    
    # 获取最小长度要求
    min_length = MIN_LENGTH.get(content_type, MIN_LENGTH["general"])
    text_length = len(text.strip())
    
    # 检查长度
    if text_length < min_length:
        logger.warning(
            f"文本过短: {text_length} < {min_length} ({content_type})"
        )
        return False, (
            f"文本过短: 当前 {text_length} 字符, "
            f"{content_type} 类型至少需要 {min_length} 字符"
        )
    
    logger.debug(f"文本内容验证通过: {text_length} 字符 ({content_type})")
    return True, f"文本内容有效（长度: {text_length}）"


def validate_upload(
    filename: str, 
    file_size: int
) -> Tuple[bool, List[str]]:
    """
    聚合验证函数：一次性验证文件名和大小
    
    Args:
        filename: 文件名
        file_size: 文件大小（bytes）
        
    Returns:
        (是否全部通过, 错误信息列表)
        
    Examples:
        >>> validate_upload("report.pdf", 2_000_000)
        (True, [])
        
        >>> validate_upload("file.exe", 20_000_000)
        (False, ["不支持的文件格式: .exe, 允许: .pdf, .docx, .txt", 
                 "文件过大: 19.1MB, 上限: 10MB"])
    """
    errors = []
    
    # 验证扩展名
    ext_valid, ext_msg = validate_file_extension(filename)
    if not ext_valid:
        errors.append(ext_msg)
    
    # 验证大小
    size_valid, size_msg = validate_file_size(file_size)
    if not size_valid:
        errors.append(size_msg)
    
    # 返回结果
    all_valid = len(errors) == 0
    
    if all_valid:
        logger.info(f"文件验证通过: {filename} ({file_size} bytes)")
    else:
        logger.warning(f"文件验证失败: {filename}, 错误: {errors}")
    
    return all_valid, errors


# ── 测试代码 ──
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 validators.py 测试")
    print("=" * 60)
    
    # 测试 1: 文件扩展名
    print("\n【测试 1: validate_file_extension】")
    test_files = [
        "report.pdf",
        "resume.DOCX",
        "notes.txt",
        "malware.exe",
        "no_extension",
        "",
        ".hidden.pdf",
        "archive.tar.gz"
    ]
    for file in test_files:
        valid, msg = validate_file_extension(file)
        status = "✅" if valid else "❌"
        print(f"{status} {file:20s} → {msg}")
    
    # 测试 2: 文件大小
    print("\n【测试 2: validate_file_size】")
    test_sizes = [
        (0, "0 bytes"),
        (1024, "1KB"),
        (2 * 1024 * 1024, "2MB"),
        (10 * 1024 * 1024, "10MB (边界)"),
        (10 * 1024 * 1024 + 1, "10MB + 1 byte"),
        (15 * 1024 * 1024, "15MB"),
        (-1, "负数")
    ]
    for size, desc in test_sizes:
        valid, msg = validate_file_size(size)
        status = "✅" if valid else "❌"
        print(f"{status} {desc:20s} → {msg}")
    
    # 测试 3: 文本内容
    print("\n【测试 3: validate_text_content】")
    test_texts = [
        (None, "general", "None"),
        ("", "general", "空字符串"),
        ("   \n\t  ", "general", "纯空白"),
        ("短文本", "jd", "短文本 + JD类型"),
        ("a" * 50, "resume", "50字符 + resume"),
        ("a" * 99, "jd", "99字符 + JD"),
        ("a" * 100, "jd", "100字符 + JD (边界)"),
        ("Python Developer with 5+ years experience in backend development...", "jd", "正常JD文本")
    ]
    for text, ctype, desc in test_texts:
        valid, msg = validate_text_content(text, ctype)
        status = "✅" if valid else "❌"
        text_preview = str(text)[:20] if text else "None/Empty"
        print(f"{status} {desc:30s} → {msg}")
    
    # 测试 4: 聚合验证
    print("\n【测试 4: validate_upload】")
    test_uploads = [
        ("report.pdf", 2_000_000, "正常PDF 2MB"),
        ("resume.docx", 5_000_000, "正常DOCX 5MB"),
        ("file.exe", 1_000_000, "不支持格式"),
        ("report.pdf", 15_000_000, "文件过大"),
        ("bad.exe", 20_000_000, "格式+大小都错"),
        ("", 0, "空文件名+0字节")
    ]
    for filename, size, desc in test_uploads:
        valid, errors = validate_upload(filename, size)
        status = "✅" if valid else "❌"
        print(f"\n{status} {desc}")
        if errors:
            for err in errors:
                print(f"   ⚠️  {err}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！检查 logs/ 目录查看详细日志")
    print("=" * 60)