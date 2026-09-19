"""LLM Service — 通过 OpenAI-compatible 协议调用 Qwen。

提供结构化的 LLM 调用接口，处理所有与模型供应商相关的细节：
- 自动重试（网络错误、限流）
- 解析失败重试
- 错误处理和日志记录
- Token 使用追踪

典型用法：
    llm = LLMService()
    jd_info = llm.call(
        prompt=f"Extract job description:\\n{text}",
        response_model=JDInfo,
        system_prompt="You are an expert HR analyst.",
    )
"""

import time
from typing import Type, TypeVar
from urllib.parse import urlparse

from openai import OpenAI
from pydantic import BaseModel

import config
from utils.logger import get_logger
from utils.token_counter import count_tokens, estimate_cost

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMServiceError(Exception):
    """LLM 服务调用失败（网络/认证/解析等）"""


class LLMService:
    """LLM 服务封装类
    
    线程安全，可在应用启动时创建单例复用。
    
    Attributes:
        client: OpenAI-compatible 客户端（自动重试网络错误和限流）
        model: 使用的模型名称
        default_temperature: 默认温度
        default_max_tokens: 默认最大 token 数
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        max_retries: int = 3,
        timeout: float | None = None,
    ):
        """初始化 LLM 服务"""
        self.model = model or config.MODEL_NAME
        self.default_temperature = temperature if temperature is not None else config.TEMPERATURE
        self.default_max_tokens = max_tokens or config.MAX_TOKENS

        _api_key = api_key or config.DASHSCOPE_API_KEY
        _base_url = config.LLM_BASE_URL

        if not _api_key:
            raise LLMServiceError(
                "DashScope API Key is required. Set DASHSCOPE_API_KEY in .env."
            )
        if not _base_url:
            raise LLMServiceError(
                "Qwen base URL is required. Set LLM_BASE_URL or "
                "DASHSCOPE_BASE_URL in .env."
            )

        try:
            self.client = OpenAI(
                api_key=_api_key,
                base_url=_base_url,
                max_retries=max_retries,
                timeout=timeout or config.LLM_TIMEOUT_SECONDS,
            )

            logger.info(
                "LLMService initialized: provider=%s, model=%s, "
                "base_url_host=%s, thinking=%s",
                config.LLM_PROVIDER,
                self.model,
                urlparse(_base_url).hostname or "invalid",
                config.LLM_ENABLE_THINKING,
            )
        except Exception as e:
            raise LLMServiceError(f"Failed to initialize Qwen client: {e}") from e

    def call(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: str = "You are a helpful assistant.",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> T:
        """调用 LLM 并返回结构化数据
        
        Args:
            prompt: 用户 prompt
            response_model: 期望的 Pydantic 模型类
            system_prompt: 系统 prompt（定义助手角色）
            temperature: 采样温度（None = 使用默认值）
            max_tokens: 最大生成 token 数（None = 使用默认值）
        
        Returns:
            response_model 的实例
        
        Raises:
            LLMServiceError: 调用失败（网络/解析/认证等）
        
        Example:
            >>> llm = LLMService()
            >>> jd = llm.call(
            ...     prompt="Extract: Software Engineer, Python, 3 years",
            ...     response_model=JDInfo,
            ...     temperature=0.3,
            ... )
            >>> print(jd.position)
            'Software Engineer'
        """
        _temperature = temperature if temperature is not None else self.default_temperature
        # 估算输入 token（仅用于日志）
        estimated_input_tokens = count_tokens(system_prompt + prompt, self.model)
        logger.info(
            "LLM call starting: model=%s, estimated_input_tokens=%d, temperature=%.2f",
            self.model,
            estimated_input_tokens,
            _temperature,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        # 尝试两次：首次失败后重试一次（仅解析失败）
        for attempt in range(1, 3):
            try:
                start_time = time.time()

                # Qwen JSON Schema structured output should not be constrained
                # with max_tokens: a truncated response is invalid JSON. Keep the
                # public max_tokens argument for backward compatibility, but do
                # not send it for structured calls.
                if max_tokens is not None:
                    logger.debug(
                        "Ignoring max_tokens=%d for structured output to avoid "
                        "truncated JSON",
                        max_tokens,
                    )

                response = self.client.chat.completions.parse(
                    model=self.model,
                    messages=messages,
                    response_format=response_model,
                    temperature=_temperature,
                    extra_body={"enable_thinking": config.LLM_ENABLE_THINKING},
                )

                elapsed = time.time() - start_time

                # 提取解析后的对象
                if not response.choices:
                    raise LLMServiceError("No choices in response")

                parsed = response.choices[0].message.parsed
                if parsed is None:
                    raise LLMServiceError("Failed to parse response into expected model")

                # 记录使用情况
                usage = response.usage
                prompt_tokens, completion_tokens, total_tokens = _usage_counts(usage)
                cost = _usage_cost(prompt_tokens, completion_tokens, self.model)

                logger.info(
                    "LLM call succeeded: prompt_tokens=%d, completion_tokens=%d, "
                    "total_tokens=%d, cost_usd=%s, time=%.2fs, attempt=%d",
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    _format_cost(cost),
                    elapsed,
                    attempt,
                )

                return parsed

            except Exception as e:
                # 仅在首次失败时重试
                if attempt < 2:
                    logger.warning(
                        "LLM call failed (attempt %d/2), retrying: %s",
                        attempt,
                        str(e),
                    )
                    time.sleep(1)  # 简单延迟 1 秒
                    continue
                else:
                    logger.error("LLM call failed after 2 attempts: %s", str(e))
                    raise LLMServiceError(f"LLM call failed: {e}") from e

        # 理论上不会到这里
        raise LLMServiceError("LLM call failed: unexpected error")

    def call_simple(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """调用 LLM 并返回纯文本响应（不使用结构化输出）
        
        用于不需要结构化解析的场景（如生成面试建议文本）。
        
        Args:
            prompt: 用户 prompt
            system_prompt: 系统 prompt
            temperature: 采样温度（None = 使用默认值）
            max_tokens: 最大生成 token 数（None = 使用默认值）
        
        Returns:
            LLM 生成的文本内容
        
        Raises:
            LLMServiceError: 调用失败
        """
        _temperature = temperature if temperature is not None else self.default_temperature
        _max_tokens = max_tokens or self.default_max_tokens

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        try:
            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=_temperature,
                max_completion_tokens=_max_tokens,
                extra_body={"enable_thinking": config.LLM_ENABLE_THINKING},
            )

            elapsed = time.time() - start_time

            if not response.choices:
                raise LLMServiceError("No choices in response")

            content = response.choices[0].message.content
            if not content:
                raise LLMServiceError("Empty content in response")

            # 记录使用情况
            usage = response.usage
            prompt_tokens, completion_tokens, total_tokens = _usage_counts(usage)
            cost = _usage_cost(prompt_tokens, completion_tokens, self.model)

            logger.info(
                "LLM simple call succeeded: prompt_tokens=%d, completion_tokens=%d, "
                "total_tokens=%d, cost_usd=%s, time=%.2fs",
                prompt_tokens,
                completion_tokens,
                total_tokens,
                _format_cost(cost),
                elapsed,
            )

            return content

        except Exception as e:
            logger.error("LLM simple call failed: %s", str(e))
            raise LLMServiceError(f"LLM simple call failed: {e}") from e


def _usage_counts(usage: object | None) -> tuple[int, int, int]:
    """Return provider-reported token counts without estimating them."""
    if usage is None:
        return 0, 0, 0

    prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
    completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
    total_tokens = int(
        getattr(usage, "total_tokens", prompt_tokens + completion_tokens)
        or prompt_tokens + completion_tokens
    )
    return prompt_tokens, completion_tokens, total_tokens


def _usage_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str,
) -> float | None:
    input_cost = estimate_cost(prompt_tokens, model, "input")
    output_cost = estimate_cost(completion_tokens, model, "output")
    if input_cost is None or output_cost is None:
        return None
    return input_cost + output_cost


def _format_cost(cost: float | None) -> str:
    return f"{cost:.6f}" if cost is not None else "unknown"
