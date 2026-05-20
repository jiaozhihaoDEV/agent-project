# langchain_demo.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 加载 API Key
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 2. 创建模型客户端 (ChatOpenAI 也兼容 DeepSeek API)
llm = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    model="deepseek-chat",
    temperature=0.7
)

# 3. 创建提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{style}风格的朋友圈文案助手。"),
    ("user", "主题：{topic}")
])

# 4. 构建链 (Chain)
chain = prompt | llm | StrOutputParser()

# 5. 执行并打印结果
result = chain.invoke({
    "style": "屌丝",
    "topic": "加班到深夜"
})
print(result)
