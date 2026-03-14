# ==============================================================================
# utils/logger.py
# 项目统一日志工具模块
# ==============================================================================

# ------------------------------------------------------------------------------
# 第一步：导入标准库
# ------------------------------------------------------------------------------
import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path
from typing import Dict

# ------------------------------------------------------------------------------
# 第二步：导入项目配置
# ------------------------------------------------------------------------------
from config import LOG_LEVEL, DEBUG, PROJECT_ROOT

# ------------------------------------------------------------------------------
# 第三步：定义日志目录常量
# ------------------------------------------------------------------------------
LOG_DIR = PROJECT_ROOT / "logs"

# ------------------------------------------------------------------------------
# 第四步：定义日志格式常量
# ------------------------------------------------------------------------------
CONSOLE_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
FILE_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ------------------------------------------------------------------------------
# 第五步：定义日志文件配置常量
# ------------------------------------------------------------------------------
LOG_FILE_NAME = "app.log"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 3

# ------------------------------------------------------------------------------
# 第六步：定义日志级别颜色映射（用于控制台彩色输出）
# ------------------------------------------------------------------------------
LEVEL_COLORS = {
    "DEBUG": "\033[36m",      # 青色
    "INFO": "\033[32m",       # 绿色
    "WARNING": "\033[33m",    # 黄色
    "ERROR": "\033[31m",      # 红色
    "CRITICAL": "\033[1;31m"  # 红色加粗
}
RESET_COLOR = "\033[0m"

# ------------------------------------------------------------------------------
# 第七步：定义 _ensure_log_dir() 私有函数
# 功能：确保日志目录存在，不存在则创建
# ------------------------------------------------------------------------------
def _ensure_log_dir() -> None:
    """确保日志目录存在"""
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------
# 第八步：定义 ColoredFormatter 类（自定义彩色格式化器）
# 继承自 logging.Formatter
# ------------------------------------------------------------------------------
class ColoredFormatter(logging.Formatter):
    """控制台彩色日志格式化器"""
    
    def __init__(self, fmt: str, datefmt: str):
        super().__init__(fmt=fmt, datefmt=datefmt)
    
    def format(self, record: logging.LogRecord) -> str:
        # 保存原始 levelname
        original_levelname = record.levelname
        
        # 获取颜色码
        color = LEVEL_COLORS.get(record.levelname, "")
        
        # 给 levelname 添加颜色
        record.levelname = f"{color}{record.levelname}{RESET_COLOR}"
        
        # 调用父类格式化
        result = super().format(record)
        
        # 恢复原始 levelname
        record.levelname = original_levelname
        
        return result

# ------------------------------------------------------------------------------
# 第九步：定义 _create_console_handler() 私有函数
# 功能：创建控制台日志处理器
# ------------------------------------------------------------------------------
def _create_console_handler() -> logging.StreamHandler:
    """创建控制台处理器（带颜色）"""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    formatter = ColoredFormatter(fmt=CONSOLE_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(formatter)
    return console_handler

# ------------------------------------------------------------------------------
# 第十步：定义 _create_file_handler() 私有函数
# 功能：创建文件日志处理器（带轮转）
# ------------------------------------------------------------------------------
def _create_file_handler() -> RotatingFileHandler:
    """创建文件处理器（带轮转）"""
    _ensure_log_dir()
    log_file_path = LOG_DIR / LOG_FILE_NAME
    
    file_handler = RotatingFileHandler(
        filename=str(log_file_path),
        maxBytes=MAX_FILE_SIZE,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    
    file_handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    formatter = logging.Formatter(fmt=FILE_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(formatter)
    
    return file_handler

# ------------------------------------------------------------------------------
# 第十一步：定义 _logger_cache 模块级变量
# 功能：缓存已创建的 logger，避免重复配置
# ------------------------------------------------------------------------------
_logger_cache: Dict[str, logging.Logger] = {}

# ------------------------------------------------------------------------------
# 第十二步：定义 get_logger() 公开函数（核心导出函数）
# 功能：获取或创建指定名称的 logger
# ------------------------------------------------------------------------------
def get_logger(name: str) -> logging.Logger:
    """
    获取 logger 实例
    
    Args:
        name: logger 名称，建议使用 __name__
    
    Returns:
        配置好的 Logger 实例
    
    Usage:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("这是一条信息")
    """
    # 检查缓存
    if name in _logger_cache:
        return _logger_cache[name]
    
    # 创建新 logger
    logger = logging.getLogger(name)
    
    # 设置日志级别
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    
    # 清空已有 handlers
    logger.handlers.clear()
    
    # 添加控制台 handler
    console_handler = _create_console_handler()
    logger.addHandler(console_handler)
    
    # 非 DEBUG 模式添加文件 handler
    if not DEBUG:
        file_handler = _create_file_handler()
        logger.addHandler(file_handler)
    
    # 防止日志向上传递
    logger.propagate = False
    
    # 缓存 logger
    _logger_cache[name] = logger
    
    return logger

# ------------------------------------------------------------------------------
# 第十三步：定义模块级便捷 logger（可选）
# 功能：提供一个默认的 logger 实例，方便简单场景使用
# ------------------------------------------------------------------------------
default_logger = get_logger("interview_prep")

# ------------------------------------------------------------------------------
# 第十四步：模块自测试代码（仅在直接运行时执行）
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # 获取测试用 logger
    test_logger = get_logger("test_module")
    
    # 输出各级别日志测试
    test_logger.debug("这是 DEBUG 消息")
    test_logger.info("这是 INFO 消息")
    test_logger.warning("这是 WARNING 消息")
    test_logger.error("这是 ERROR 消息")
    test_logger.critical("这是 CRITICAL 消息")
    
    # 打印测试完成提示
    print("\n日志测试完成，请检查:")
    print("1. 控制台输出（应该有彩色日志）")
    print(f"2. 日志文件: {LOG_DIR / LOG_FILE_NAME}")

# ==============================================================================
# 模块导出清单
# ==============================================================================
# 公开导出:
#   - get_logger(name: str) -> logging.Logger  （主要导出函数）
#   - default_logger: logging.Logger           （默认 logger 实例）
#
# 私有（不导出）:
#   - _ensure_log_dir()
#   - _create_console_handler()
#   - _create_file_handler()
#   - _logger_cache
#   - ColoredFormatter
#   - 所有常量
# ==============================================================================