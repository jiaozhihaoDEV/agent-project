import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
llm = ChatOpenAI(base_url="https://api.deepseek.com/v1", api_key=api_key, model="deepseek-chat", temperature=0)

question = "一个房间里有一盏灯。外面有三个开关，只有一个控制这盏灯。你只能进房间一次，如何确定哪个开关控制灯？"

prompt_without = ChatPromptTemplate.from_messages([("user", question)])
prompt_with = ChatPromptTemplate.from_messages([("user", question + " 请一步步思考。")])

print("=== 无 CoT ===\n", (prompt_without | llm).invoke({}).content)
print("\n=== 有 CoT ===\n", (prompt_with | llm).invoke({}).content)
