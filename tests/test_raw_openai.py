# test_raw_openai.py
import os
from openai import OpenAI

# 直接把你的 key 写在这里测试（测完删掉）
client = OpenAI(api_key="")

try:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "user", "content": "Hello!"}
      ]
    )
    print("原生调用成功！AI回复：", completion.choices[0].message.content)
except Exception as e:
    print("原生调用也失败了，错误是：", e)