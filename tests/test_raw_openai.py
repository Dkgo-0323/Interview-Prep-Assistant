"""Manual Qwen text-call diagnostic with no import-time network side effects."""

from services.llm_service import LLMService


def main() -> None:
    response = LLMService(max_tokens=64).call_simple(
        prompt="请回复：Qwen 连接成功",
        temperature=0.0,
    )
    print(response)


if __name__ == "__main__":
    main()
