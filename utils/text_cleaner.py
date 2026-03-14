# utils/text_cleaner.py
"""
文本清洗工具模块
功能：对从PDF/DOCX/TXT解析出的原始文本进行标准化清洗
依赖：config.py（配置项）, utils.logger（日志记录）
"""

# ============================================================================
# 导入依赖模块
# ============================================================================

import re
import unicodedata
from typing import Optional

from utils.logger import get_logger

# 创建当前模块的logger实例
logger = get_logger(__name__)


# ============================================================================
# 主函数：clean_text
# ============================================================================

def clean_text(
    text: str,
    remove_extra_whitespace: bool = True,
    normalize_line_breaks: bool = True,
    remove_special_chars: bool = False,
    lowercase: bool = False
) -> str:
    """
    清洗和标准化文本内容
    
    Args:
        text: 待清洗的原始文本
        remove_extra_whitespace: 是否去除多余空白（默认True）
        normalize_line_breaks: 是否统一换行符（默认True）
        remove_special_chars: 是否去除特殊字符（默认False）
        lowercase: 是否转小写（默认False）
    
    Returns:
        清洗后的文本字符串
    
    Examples:
        >>> clean_text("  Hello\\r\\nWorld  ")
        'Hello\\nWorld'
        >>> clean_text("HELLO WORLD", lowercase=True)
        'hello world'
    """
    
    # ------------------------------------------------------------------------
    # 第一步：输入验证
    # ------------------------------------------------------------------------
    
    # 1.1 检查输入text是否为None
    if text is None:
        logger.warning("输入文本为None，返回空字符串")
        return ""
    
    # 1.2 检查输入text是否为空字符串
    if text == "":
        logger.debug("输入文本为空字符串，直接返回")
        return ""
    
    # 1.3 记录调试日志：开始清洗文本，记录原始文本长度
    original_length = len(text)
    logger.debug(f"开始清洗文本，原始长度: {original_length} 字符")
    
    # 1.4 创建一个临时变量cleaned_text，赋值为原始text
    cleaned_text = text
    
    
    # ------------------------------------------------------------------------
    # 第二步：统一换行符（如果normalize_line_breaks=True）
    # ------------------------------------------------------------------------
    
    # 2.1 检查normalize_line_breaks参数是否为True
    if normalize_line_breaks:
        # 2.2 记录调试日志：正在统一换行符
        logger.debug("正在统一换行符...")
        
        # 2.3 将Windows风格的换行符\r\n替换为Unix风格的\n
        cleaned_text = cleaned_text.replace('\r\n', '\n')
        
        # 2.4 将Mac旧版本的换行符\r替换为\n
        cleaned_text = cleaned_text.replace('\r', '\n')
        
        # 2.5 记录调试日志：换行符统一完成
        logger.debug("换行符统一完成")
    
    
    # ------------------------------------------------------------------------
    # 第三步：去除多余空白（如果remove_extra_whitespace=True）
    # ------------------------------------------------------------------------
    
    # 3.1 检查remove_extra_whitespace参数是否为True
    if remove_extra_whitespace:
        # 3.2 记录调试日志：正在去除多余空白
        logger.debug("正在去除多余空白...")
        
        # 3.3 使用正则表达式将多个连续空格替换为单个空格
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        
        # 3.4 使用正则表达式将多个连续制表符\t替换为单个空格
        cleaned_text = re.sub(r'\t+', ' ', cleaned_text)
        
        # 3.5 使用正则表达式将3个或更多连续换行符替换为2个换行符
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        
        # 3.6 去除每行首尾的空白字符
        lines = cleaned_text.split('\n')
        lines = [line.strip() for line in lines]
        cleaned_text = '\n'.join(lines)
        
        # 3.7 记录调试日志：多余空白去除完成
        logger.debug("多余空白去除完成")
    
    
    # ------------------------------------------------------------------------
    # 第四步：去除特殊字符（如果remove_special_chars=True）
    # ------------------------------------------------------------------------
    
    # 4.1 检查remove_special_chars参数是否为True
    if remove_special_chars:
        # 4.2 记录调试日志：正在去除特殊字符
        logger.debug("正在去除特殊字符...")
        
        # 4.3 定义要保留的字符范围
        # 保留：字母、数字、基本标点符号、空格、换行符、中文字符
        pattern = r'[^a-zA-Z0-9\s\.\,\!\?\;\:\-\(\)\[\]\{\}\'\"/\n\u4e00-\u9fff]'
        
        # 4.4 使用re.sub将匹配到的特殊字符替换为空字符串
        cleaned_text = re.sub(pattern, '', cleaned_text)
        
        # 4.5 记录调试日志：特殊字符去除完成
        logger.debug("特殊字符去除完成")
    
    
    # ------------------------------------------------------------------------
    # 第五步：转小写（如果lowercase=True）
    # ------------------------------------------------------------------------
    
    # 5.1 检查lowercase参数是否为True
    if lowercase:
        # 5.2 记录调试日志：正在转换为小写
        logger.debug("正在转换为小写...")
        
        # 5.3 调用字符串的lower()方法
        cleaned_text = cleaned_text.lower()
        
        # 5.4 记录调试日志：小写转换完成
        logger.debug("小写转换完成")
    
    
    # ------------------------------------------------------------------------
    # 第六步：最终处理
    # ------------------------------------------------------------------------
    
    # 6.1 对整个文本执行首尾空白裁剪
    cleaned_text = cleaned_text.strip()
    
    # 6.2 记录信息日志：文本清洗完成，记录清洗前后的长度
    cleaned_length = len(cleaned_text)
    logger.info(f"文本清洗完成: {original_length} -> {cleaned_length} 字符")
    
    # 6.3 如果清洗后文本为空，记录警告日志
    if not cleaned_text:
        logger.warning("清洗后文本为空，可能输入内容全为空白或特殊字符")
    
    # 6.4 返回清洗后的文本
    return cleaned_text


# ============================================================================
# 辅助函数（可选）：remove_html_tags
# ============================================================================

def remove_html_tags(text: str) -> str:
    """
    去除文本中的HTML标签
    
    使用场景：如果未来需要处理网页爬取的职位描述
    
    Args:
        text: 包含HTML标签的文本
    
    Returns:
        去除HTML标签后的纯文本
    
    Examples:
        >>> remove_html_tags("<p>Hello <b>World</b></p>")
        'Hello World'
        >>> remove_html_tags("Text with &nbsp; spaces")
        'Text with   spaces'
    """
    
    # 7.1 检查输入text是否为None或空字符串
    if not text:
        return ""
    
    # 7.2 记录调试日志：正在去除HTML标签
    logger.debug("正在去除HTML标签...")
    
    # 7.3 定义HTML标签的正则表达式模式
    pattern = r'<[^>]+>'
    
    # 7.4 使用re.sub将匹配到的标签替换为空字符串
    cleaned = re.sub(pattern, '', text)
    
    # 7.5 去除HTML实体（如&nbsp; &lt; &gt;等）
    entity_pattern = r'&[a-zA-Z]+;'
    cleaned = re.sub(entity_pattern, ' ', cleaned)
    
    # 7.6 记录调试日志：HTML标签去除完成
    logger.debug("HTML标签去除完成")
    
    # 7.7 返回清洗后的文本
    return cleaned


# ============================================================================
# 辅助函数（可选）：normalize_unicode
# ============================================================================

def normalize_unicode(text: str) -> str:
    """
    统一Unicode字符编码
    
    使用场景：处理从不同系统复制的文本（Mac/Windows）
    
    Args:
        text: 待规范化的文本
    
    Returns:
        规范化后的文本
    
    Examples:
        >>> # 组合字符é（e + ´）会被统一为单个字符é
        >>> normalize_unicode("café")  # 假设输入是组合字符
        'café'
    """
    
    # 8.1 检查输入text是否为None或空字符串
    if not text:
        return ""
    
    # 8.3 使用unicodedata.normalize进行NFC规范化
    # NFC：组合字符（如é）统一为单个字符
    normalized = unicodedata.normalize('NFC', text)
    
    # 8.4 返回规范化后的文本
    return normalized


# ============================================================================
# 测试代码块
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("文本清洗模块测试")
    print("=" * 70)
    
    # 测试用例1：基本清洗
    # -----------------------------------------------------------------------
    print("\n【测试用例1：基本清洗】")
    print("-" * 70)
    
    # 9.1 定义测试文本test_text_1
    test_text_1 = "\r\n  这是   一段\r\n测试  文本。  \n\n\n\n有很多   空白。  \n"
    
    # 9.2 调用clean_text函数，使用默认参数
    result_1 = clean_text(test_text_1)
    
    # 9.3 打印原始文本和清洗后文本，用repr()显示隐藏字符
    print("原始文本:", repr(test_text_1))
    print("清洗后:", repr(result_1))
    
    # 9.4 打印分隔线
    print()
    
    
    # 测试用例2：去除特殊字符
    # -----------------------------------------------------------------------
    print("\n【测试用例2：去除特殊字符】")
    print("-" * 70)
    
    # 10.1 定义测试文本test_text_2
    test_text_2 = "这是★测试©文本™，包含emoji😊和特殊字符！"
    
    # 10.2 调用clean_text，设置remove_special_chars=True
    result_2 = clean_text(test_text_2, remove_special_chars=True)
    
    # 10.3 打印结果
    print("原始文本:", test_text_2)
    print("清洗后:", result_2)
    
    # 10.4 打印分隔线
    print()
    
    
    # 测试用例3：转小写
    # -----------------------------------------------------------------------
    print("\n【测试用例3：转小写】")
    print("-" * 70)
    
    # 11.1 定义测试文本test_text_3
    test_text_3 = "Python Developer with Django Experience"
    
    # 11.2 调用clean_text，设置lowercase=True
    result_3 = clean_text(test_text_3, lowercase=True)
    
    # 11.3 打印结果
    print("原始文本:", test_text_3)
    print("清洗后:", result_3)
    
    # 11.4 打印分隔线
    print()
    
    
    # 测试用例4：所有选项开启
    # -----------------------------------------------------------------------
    print("\n【测试用例4：所有选项开启】")
    print("-" * 70)
    
    # 12.1 定义测试文本test_text_4
    test_text_4 = "\r\n  PYTHON★Developer  \r\n\r\n需要  Django©经验！！  \n\n\n\t\t 熟悉PostgreSQL™  \n"
    
    # 12.2 调用clean_text，所有参数设为True
    result_4 = clean_text(
        test_text_4,
        remove_extra_whitespace=True,
        normalize_line_breaks=True,
        remove_special_chars=True,
        lowercase=True
    )
    
    # 12.3 打印结果
    print("原始文本:", repr(test_text_4))
    print("清洗后:", repr(result_4))
    
    # 12.4 打印分隔线
    print()
    
    
    # 测试用例5：边界情况
    # -----------------------------------------------------------------------
    print("\n【测试用例5：边界情况】")
    print("-" * 70)
    
    # 13.1 测试None输入
    result_none = clean_text(None)
    print("None输入结果:", repr(result_none), f"(期望: '')")
    
    # 13.2 测试空字符串输入
    result_empty = clean_text("")
    print("空字符串输入结果:", repr(result_empty), f"(期望: '')")
    
    # 13.3 测试仅包含空白的字符串
    result_whitespace = clean_text("   \n\n\t\t   ")
    print("纯空白输入结果:", repr(result_whitespace), f"(期望: '')")
    
    print()
    
    
    # 测试用例6：HTML标签去除
    # -----------------------------------------------------------------------
    print("\n【测试用例6：HTML标签去除】")
    print("-" * 70)
    
    html_text = "<p>这是<b>加粗</b>的文本，包含&nbsp;空格&lt;符号&gt;</p>"
    result_html = remove_html_tags(html_text)
    print("原始HTML:", html_text)
    print("去除标签后:", result_html)
    
    print()
    
    
    # 测试用例7：Unicode规范化
    # -----------------------------------------------------------------------
    print("\n【测试用例7：Unicode规范化】")
    print("-" * 70)
    
    # 创建组合字符示例（e + 组合重音符）
    combined = "café"  # 这里可能是组合字符
    normalized = normalize_unicode(combined)
    print("原始文本:", repr(combined))
    print("规范化后:", repr(normalized))
    
    print()
    
    # 13.4 打印测试完成信息
    print("=" * 70)
    print("所有测试用例执行完成！")
    print("=" * 70)