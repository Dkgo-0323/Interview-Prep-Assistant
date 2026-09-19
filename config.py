# config.py
# 全局配置文件 - 集中管理所有常量和设置

# ============================================================
# 第一步：导入必要的模块
# ============================================================
# 导入 os 模块，用于读取环境变量
# 导入 pathlib 的 Path 类，用于处理文件路径
# 导入 dotenv 的 load_dotenv 函数，用于加载 .env 文件
import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# 第二步：加载环境变量
# ============================================================
# 调用 load_dotenv() 函数，从 .env 文件加载环境变量到系统环境中
load_dotenv()

# ============================================================
# 第三步：定义项目路径常量
# ============================================================
# PROJECT_ROOT: 使用 Path(__file__) 获取当前文件路径，再用 .parent 获取项目根目录
# UPLOAD_DIR: 拼接 PROJECT_ROOT 和 "data/uploads"，指向上传文件目录
PROJECT_ROOT = Path(__file__).parent
UPLOAD_DIR = PROJECT_ROOT / "data/uploads"

# ============================================================
# 第四步：定义 LLM 相关配置
# ============================================================
# 百炼提供 OpenAI-compatible API。本项目仍使用 OpenAI Python SDK 作为协议
# 客户端，但认证、服务地址和默认模型全部来自 Qwen/DashScope 配置。
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
LLM_BASE_URL = (
    os.getenv("LLM_BASE_URL")
    or os.getenv("DASHSCOPE_BASE_URL")
)
LLM_DEFAULT_MODEL = (
    os.getenv("LLM_DEFAULT_MODEL")
    or "qwen3.7-plus"
)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "qwen")
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "120"))
LLM_ENABLE_THINKING = os.getenv("LLM_ENABLE_THINKING", "false").lower() == "true"

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))


def _optional_float(name: str) -> float | None:
    value = os.getenv(name)
    return float(value) if value else None


LLM_INPUT_COST_USD_PER_MILLION_TOKENS = _optional_float(
    "LLM_INPUT_COST_USD_PER_MILLION_TOKENS"
)
LLM_OUTPUT_COST_USD_PER_MILLION_TOKENS = _optional_float(
    "LLM_OUTPUT_COST_USD_PER_MILLION_TOKENS"
)

# Backward-compatible aliases for modules and local scripts that import the
# original names. New provider code uses the neutral/DashScope names above.
OPENAI_API_KEY = DASHSCOPE_API_KEY
OPENAI_BASE_URL = LLM_BASE_URL
MODEL_NAME = LLM_DEFAULT_MODEL

# ============================================================
# 第五步：定义文件上传限制
# ============================================================
# UPLOAD_MAX_SIZE_MB: 定义最大文件大小，值为 10（单位：MB）
# ALLOWED_EXTENSIONS: 定义允许的文件扩展名，值为包含 ".pdf", ".docx", ".txt" 的集合(set)
UPLOAD_MAX_SIZE_MB = 10
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# ============================================================
# 第六步：定义日志配置
# ============================================================
# LOG_LEVEL: 从环境变量读取 "LOG_LEVEL"，默认值为 "INFO"
# DEBUG: 从环境变量读取 "DEBUG"，默认值为 "False"，需要将字符串转换为布尔值
#        提示：可以用 .lower() == "true" 来判断
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ============================================================
# 第七步：定义问题生成配置
# ============================================================
# DEFAULT_NUM_QUESTIONS: 默认生成的问题数量，值为 10
DEFAULT_NUM_QUESTIONS = 10

# ============================================================
# 第八步：确保必要目录存在
# ============================================================
# 调用 UPLOAD_DIR.mkdir()，设置 parents=True 和 exist_ok=True
# parents=True: 如果父目录不存在，自动创建
# exist_ok=True: 如果目录已存在，不报错
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
