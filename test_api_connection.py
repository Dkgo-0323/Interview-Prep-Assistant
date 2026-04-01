import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. 加载环境变量
load_dotenv()

def test_connection():
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")

    print("--- 🔍 开始 API 连接测试 ---")
    print(f"📍 Base URL: {base_url}")
    print(f"🤖 Model: {model_name}")
    print(f"🔑 Key 长度: {len(api_key) if api_key else 0} 字符")
    print("-" * 30)

    # 2. 初始化客户端
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    try:
        # 测试 1: 尝试列出模型 (验证 API Key 和 Base URL 是否匹配)
        print("🧪 测试 1: 正在尝试获取模型列表...")
        client.models.list()
        print("✅ 身份验证成功！")

        # 测试 2: 尝试一次简单的对话 (验证模型权限和额度)
        print(f"🧪 测试 2: 正在发送测试指令到 {model_name}...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Say 'Connection Successful' in 3 words."}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ 模型响应成功: '{result}'")
        print("\n🎉 恭喜！你的 API 配置完全可用。")

    except Exception as e:
        print("\n❌ 测试失败！")
        # 针对常见错误的友好提示
        error_msg = str(e)
        if "Authentication" in error_msg:
            print("💡 提示: API Key 错误，请检查 .env 中的 key 是否填写正确。")
        elif "Connection" in error_msg or "Failed to connect" in error_msg:
            print("💡 提示: 无法连接到服务器。请检查 Base URL 是否填写正确，或者是否需要开启/关闭代理。")
        elif "404" in error_msg:
            print("💡 提示: 404 错误。通常是 Base URL 路径不对，确保结尾是否有 /v1。")
        else:
            print(f"💡 错误详情: {error_msg}")

if __name__ == "__main__":
    test_connection()