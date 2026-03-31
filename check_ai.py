# check_ai.py
import os
from services.llm_service import LLMService
from pydantic import BaseModel

# 1. 确保环境变量在这里能打印出来
print(f"API KEY: {os.getenv('OPENAI_API_KEY')[:10]}...") 

class TestModel(BaseModel):
    message: str

try:
    llm = LLMService()
    res = llm.call(prompt="Hi", response_model=TestModel)
    print("成功了！AI 说:", res.message)
except Exception as e:
    print("还是不行，报错是:", e)