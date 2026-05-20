import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    model="deepseek-chat",
    temperature=0.8
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个鲁迅风格的朋友圈文案助手，用讽刺、简短、带文言味的口吻，像《狂人日记》那样。"),
    ("user", "主题：{topic}")
])

chain = prompt | llm | StrOutputParser()
result = chain.invoke({"topic": "加班到深夜"})
print("鲁迅风格：\n", result)
