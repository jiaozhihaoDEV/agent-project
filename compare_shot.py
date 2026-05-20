import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, FewShotPromptTemplate, PromptTemplate

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
llm = ChatOpenAI(base_url="https://api.deepseek.com/v1", api_key=api_key, model="deepseek-chat", temperature=0.7)

# Zero-shot
zero_prompt = ChatPromptTemplate.from_messages([
    ("user", "请为“辞职旅行”写一条朋友圈文案。")
])
zero_chain = zero_prompt | llm
zero_result = zero_chain.invoke({})
print("=== Zero-shot 结果 ===\n", zero_result.content)

# Few-shot（使用之前的例子）
examples = [
    {"topic": "拿到offer", "copy": "终于等到你，还好我没放弃。#offer"},
    {"topic": "失恋", "copy": "感谢相遇，各自安好。再见。"}
]
example_prompt = PromptTemplate(input_variables=["topic","copy"], template="主题: {topic}\n文案: {copy}")
few_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="请模仿下面的例子写一条朋友圈文案：",
    suffix="主题: {input}\n文案:",
    input_variables=["input"]
)
formatted = few_prompt.format(input="辞职旅行")
few_result = llm.invoke(formatted)
print("\n=== Few-shot 结果 ===\n", few_result.content)
