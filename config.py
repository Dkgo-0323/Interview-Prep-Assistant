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
# OPENAI_API_KEY: 从环境变量读取 "OPENAI_API_KEY"，无默认值（必填项）
# OPENAI_BASE_URL: 从环境变量读取 "OPENAI_BASE_URL"，默认值为 "https://api.openai.com/v1"
# MODEL_NAME: 从环境变量读取 "MODEL_NAME"，默认值为 "gpt-4o-mini"
# TEMPERATURE: 从环境变量读取 "TEMPERATURE"，默认值为 0.7，注意要转换为 float 类型
# MAX_TOKENS: 从环境变量读取 "MAX_TOKENS"，默认值为 2000，注意要转换为 int 类型
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))

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