"""
Token计数和管理工具模块

功能：
- 在请求前粗略估算文本 token 数量
- 截断超长文本到指定token限制
- 根据供应商返回的实际 token 数估算API调用成本

依赖：
- tiktoken: OpenAI官方token计数库
- config: 获取默认模型配置
- utils.logger: 日志记录
"""

import math
from typing import Optional, Dict
from functools import lru_cache

import tiktoken

import config
from utils.logger import get_logger

MODEL_NAME = config.MODEL_NAME

# ============================================
# 配置
# ============================================

logger = get_logger(__name__)

# 单位：美元/1M tokens。Qwen 价格不写死在仓库中，而是读取本地环境配置。
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o-mini": {
        "input": 0.150,   # $0.150 per 1M input tokens
        "output": 0.600,  # $0.600 per 1M output tokens
    },
    "gpt-4o": {
        "input": 2.50,
        "output": 10.00,
    },
    "gpt-4": {
        "input": 30.00,
        "output": 60.00,
    },
    "gpt-3.5-turbo": {
        "input": 0.50,
        "output": 1.50,
    },
}

if (
    config.LLM_INPUT_COST_USD_PER_MILLION_TOKENS is not None
    and config.LLM_OUTPUT_COST_USD_PER_MILLION_TOKENS is not None
):
    MODEL_PRICING[config.LLM_DEFAULT_MODEL] = {
        "input": config.LLM_INPUT_COST_USD_PER_MILLION_TOKENS,
        "output": config.LLM_OUTPUT_COST_USD_PER_MILLION_TOKENS,
    }

# 默认使用输入价格进行估算（保守估计）
DEFAULT_COST_TYPE = "input"


# ============================================
# 编码器缓存
# ============================================

@lru_cache(maxsize=10)
def _get_encoding(model: str) -> tiktoken.Encoding:
    """
    获取模型对应的tiktoken编码器（带缓存）
    
    Args:
        model: 模型名称（如 "gpt-4o-mini"）
        
    Returns:
        tiktoken.Encoding对象
        
    Note:
        - 使用lru_cache避免重复创建编码器
        - Qwen 不使用 tiktoken；未知模型只使用 cl100k_base 做请求前粗略估算
        - 实际计费与日志以供应商响应中的 usage 为准
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        logger.debug(f"获取编码器成功: {model} -> {encoding.name}")
        return encoding
    except KeyError:
        logger.warning(
            f"模型 '{model}' 无精确的本地编码器，使用 'cl100k_base' 粗略估算；"
            "实际用量以供应商 usage 为准"
        )
        return tiktoken.get_encoding("cl100k_base")


# ============================================
# 核心功能函数
# ============================================

def count_tokens(text: str, model: str = MODEL_NAME) -> int:
    """
    计算文本的token数量
    
    Args:
        text: 待计算的文本
        model: 模型名称（默认从config.py读取）
        
    Returns:
        token数量（整数）
        
    Examples:
        >>> count_tokens("Hello, world!")
        4
        >>> count_tokens("你好世界", model="gpt-4o-mini")
        4
        
    Note:
        - 空字符串返回0
        - 不同模型的编码方式可能不同
        - 中文字符通常1个字=1-2个token
    """
    # 输入验证
    if not isinstance(text, str):
        logger.error(f"输入必须是字符串，收到类型: {type(text)}")
        raise TypeError(f"Expected str, got {type(text)}")
    
    if not text:
        logger.debug("空文本，返回0 tokens")
        return 0

    if model.lower().startswith("qwen"):
        # Qwen does not use an OpenAI tiktoken vocabulary. This intentionally
        # avoids downloading an unrelated tokenizer and is used only for
        # pre-request logging; provider-reported usage remains authoritative.
        token_count = max(1, math.ceil(len(text.encode("utf-8")) / 3))
        logger.debug(
            "Qwen token粗略估算: %d tokens (模型: %s); 实际用量以 usage 为准",
            token_count,
            model,
        )
        return token_count
    
    # 获取编码器并计算
    encoding = _get_encoding(model)
    tokens = encoding.encode(text)
    token_count = len(tokens)
    
    logger.debug(
        f"Token计数完成: {token_count} tokens "
        f"(文本长度: {len(text)} 字符, 模型: {model})"
    )
    
    return token_count


def truncate_text(
    text: str,
    max_tokens: int,
    model: str = MODEL_NAME,
    suffix: str = "..."
) -> str:
    """
    截断文本到指定token数量
    
    Args:
        text: 原始文本
        max_tokens: 最大允许的token数量
        model: 模型名称
        suffix: 截断后添加的后缀（会计入token）
        
    Returns:
        截断后的文本
        
    Examples:
        >>> long_text = "a" * 10000
        >>> truncated = truncate_text(long_text, max_tokens=100)
        >>> count_tokens(truncated) <= 100
        True
        
    Note:
        - 如果文本本身<=max_tokens，直接返回原文
        - suffix的token数会从max_tokens中扣除
        - 截断发生时会记录warning日志
    """
    # 输入验证
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text)}")
    
    if max_tokens <= 0:
        logger.error(f"max_tokens必须>0，收到: {max_tokens}")
        raise ValueError(f"max_tokens must be positive, got {max_tokens}")
    
    if not text:
        return text

    if model.lower().startswith("qwen"):
        # Conservative character-based fallback for a tokenizer that is not
        # available locally. Business inputs also have their own length guards.
        available_chars = max_tokens - len(suffix)
        if available_chars <= 0:
            raise ValueError(
                f"Suffix占用 {len(suffix)} 字符，超过限制 {max_tokens}"
            )
        if len(text) <= max_tokens:
            return text
        logger.warning(
            "Qwen 文本按字符保守截断: %d -> %d; token限制为粗略值",
            len(text),
            available_chars,
        )
        return text[:available_chars] + suffix
    
    # 获取编码器
    encoding = _get_encoding(model)
    
    # 计算原始token数
    tokens = encoding.encode(text)
    original_count = len(tokens)
    
    # 如果不超限，直接返回
    if original_count <= max_tokens:
        logger.debug(
            f"文本未超限 ({original_count}/{max_tokens} tokens)，无需截断"
        )
        return text
    
    # 计算suffix占用的token
    suffix_tokens = encoding.encode(suffix) if suffix else []
    available_tokens = max_tokens - len(suffix_tokens)
    
    if available_tokens <= 0:
        logger.error(
            f"suffix太长 ({len(suffix_tokens)} tokens)，"
            f"超过max_tokens ({max_tokens})"
        )
        raise ValueError(
            f"Suffix占用 {len(suffix_tokens)} tokens，"
            f"超过限制 {max_tokens}"
        )
    
    # 截断并解码
    truncated_tokens = tokens[:available_tokens]
    truncated_text = encoding.decode(truncated_tokens)
    
    # 添加后缀
    result = truncated_text + suffix
    
    # 记录日志
    logger.warning(
        f"文本已截断: {original_count} → {len(truncated_tokens)} tokens "
        f"(减少 {original_count - len(truncated_tokens)} tokens, "
        f"约 {(1 - len(truncated_tokens)/original_count)*100:.1f}%)"
    )
    
    return result


def estimate_cost(
    num_tokens: int,
    model: str = MODEL_NAME,
    cost_type: str = DEFAULT_COST_TYPE
) -> float | None:
    """
    估算API调用成本
    
    Args:
        num_tokens: token数量
        model: 模型名称
        cost_type: 价格类型（"input" 或 "output"）
        
    Returns:
        预估成本（美元）；没有对应价格配置时返回 None
        
    Examples:
        >>> estimate_cost(1000, model="gpt-4o-mini")  # 1k tokens
        0.00015  # $0.00015
        
        >>> estimate_cost(1_000_000, model="gpt-4o-mini")  # 1M tokens
        0.15  # $0.15
        
    Note:
        - 返回值单位为美元（USD）
        - 未知模型不会套用其他模型价格
        - cost_type默认为"input"（通常input更便宜）
    """
    # 输入验证
    if num_tokens < 0:
        raise ValueError(f"num_tokens不能为负数，收到: {num_tokens}")
    
    if cost_type not in ["input", "output"]:
        raise ValueError(f"cost_type必须是'input'或'output'，收到: {cost_type}")
    
    # 获取定价
    if model in MODEL_PRICING:
        price_per_million = MODEL_PRICING[model][cost_type]
    else:
        logger.warning("模型 '%s' 未配置价格，成本记为 unknown", model)
        return None
    
    # 计算成本（tokens / 1,000,000 * 单价）
    cost = (num_tokens / 1_000_000) * price_per_million
    
    logger.debug(
        f"成本估算: {num_tokens:,} tokens × "
        f"${price_per_million:.3f}/M ({cost_type}) = ${cost:.6f}"
    )
    
    return cost


# ============================================
# 便捷函数
# ============================================

def get_token_info(text: str, model: str = MODEL_NAME) -> Dict:
    """
    获取文本的完整token信息（便捷函数）
    
    Args:
        text: 待分析文本
        model: 模型名称
        
    Returns:
        包含以下键的字典：
        - token_count: token数量
        - char_count: 字符数量
        - estimated_cost_input: 输入成本估算
        - estimated_cost_output: 输出成本估算
        - model: 使用的模型
        
    Examples:
        >>> info = get_token_info("Hello world")
        >>> print(info)
        {
            'token_count': 2,
            'char_count': 11,
            'estimated_cost_input': 0.0000003,
            'estimated_cost_output': 0.0000012,
            'model': 'gpt-4o-mini'
        }
    """
    token_count = count_tokens(text, model)
    
    return {
        "token_count": token_count,
        "char_count": len(text),
        "estimated_cost_input": estimate_cost(token_count, model, "input"),
        "estimated_cost_output": estimate_cost(token_count, model, "output"),
        "model": model,
    }


# ============================================
# 测试代码
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Token Counter 模块测试")
    print("=" * 60)
    
    # 测试1: 基础计数
    print("\n[测试1] 基础Token计数")
    test_texts = [
        "Hello, world!",
        "你好，世界！",
        "This is a longer text with multiple words and punctuation marks.",
        "",
    ]
    
    for text in test_texts:
        count = count_tokens(text)
        print(f"  文本: '{text[:50]}...' → {count} tokens")
    
    # 测试2: 文本截断
    print("\n[测试2] 文本截断")
    long_text = "This is a test. " * 100  # 重复100次
    original_count = count_tokens(long_text)
    print(f"  原始文本: {original_count} tokens")
    
    for limit in [50, 100, 200]:
        truncated = truncate_text(long_text, max_tokens=limit)
        new_count = count_tokens(truncated)
        print(f"  截断到 {limit} tokens: 实际 {new_count} tokens")
        print(f"    预览: {truncated[:80]}...")
    
    # 测试3: 成本估算
    print("\n[测试3] 成本估算")
    token_amounts = [1_000, 10_000, 100_000, 1_000_000]
    
    for amount in token_amounts:
        cost_in = estimate_cost(amount, model="gpt-4o-mini", cost_type="input")
        cost_out = estimate_cost(amount, model="gpt-4o-mini", cost_type="output")
        print(f"  {amount:,} tokens:")
        print(f"    输入成本: ${cost_in:.6f}")
        print(f"    输出成本: ${cost_out:.6f}")
    
    # 测试4: 完整信息
    print("\n[测试4] 获取完整Token信息")
    sample_text = "这是一个测试文本，用于演示token信息获取功能。" * 5
    info = get_token_info(sample_text)
    
    print(f"  模型: {info['model']}")
    print(f"  字符数: {info['char_count']}")
    print(f"  Token数: {info['token_count']}")
    print(f"  输入成本: ${info['estimated_cost_input']:.8f}")
    print(f"  输出成本: ${info['estimated_cost_output']:.8f}")
    
    # 测试5: 不同模型对比
    print("\n[测试5] 不同模型Token计数对比")
    test_text = "Artificial Intelligence is transforming the world."
    models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    
    for model in models:
        count = count_tokens(test_text, model=model)
        print(f"  {model}: {count} tokens")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)
