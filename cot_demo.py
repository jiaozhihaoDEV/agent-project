import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate   # 新版路径

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    model="deepseek-chat",
    temperature=0
)

# 不使用 CoT
without_cot = ChatPromptTemplate.from_messages([
    ("user", "小明有3个苹果，给了小红1个，又买了2倍于现在数量的苹果，最后有多少个？")
])

# 使用 CoT
with_cot = ChatPromptTemplate.from_messages([
    ("user", "小明有3个苹果，给了小红1个，又买了2倍于现在数量的苹果，最后有多少个？请一步步思考。")
])

chain = without_cot | llm
result_without = chain.invoke({})
print("=== 不使用 CoT 的回答 ===\n", result_without.content)

chain2 = with_cot | llm
result_with = chain2.invoke({})
print("\n=== 使用 CoT 的回答 ===\n", result_with.content)
