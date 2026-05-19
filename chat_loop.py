import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1"
)

print("开始对话！输入 exit 或 quit 退出程序。")

while True:
    user_question = input()
    print("你输入了：" + user_question)
    
    if user_question.lower() in ["exit", "quit"]:
        print("再见！")
        break
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": user_question}],
        temperature=1.2     )

    print("AI答：", response.choices[0].message.content)
