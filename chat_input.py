import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

# 获取用户输入
user_question = input("你问：")

# 发送问题
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": user_question}]
)

# 打印回答
print("AI答：", response.choices[0].message.content)
