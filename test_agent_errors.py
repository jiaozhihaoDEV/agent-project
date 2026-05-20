# test_agent_errors.py - 专门模拟 Agent 调用失败的场景

import os
import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    model="deepseek-chat",
    temperature=0
)

# 只有一个正确的工具：获取当前时间
@tool
def get_current_time() -> str:
    """获取当前日期和时间"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"当前时间: {now}"

correct_tools = [get_current_time]
agent = create_react_agent(llm, correct_tools)

print("=== 测试场景1：调用不存在的工具 ===")
# 注意：这里 prompt 里要求调用一个不存在的工具 'unknown_tool'
# 新版 LangGraph 可能会自动返回 ToolMessage(status="error") 而不是直接崩溃
result = agent.invoke({"messages": [("user", "请调用 unknown_tool 工具")]})
print(result)

print("\n=== 测试场景2：工具参数错误 ===")
# 工具 get_current_time 不需要参数，但用户强制要求传入参数
result = agent.invoke({"messages": [("user", "请用 get_current_time 工具，参数为 'abc'")]})
print(result)
