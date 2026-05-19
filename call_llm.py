import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. 读取 .env 文件里的密钥
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 2. 创建客户端（相当于拿起电话）
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

# 3. 发送一条消息（相当于拨号并说话）
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好，请简单介绍一下你自己"}]
)

# 4. 打印 AI 的回答
print(response.choices[0].message.content)
