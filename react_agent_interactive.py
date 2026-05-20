import os
import datetime
import re
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

@tool
def calculate(expression: str) -> str:
    """执行数学计算"""
    try:
        return f"计算结果: {eval(expression)}"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def get_current_time() -> str:
    """获取当前日期和时间"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"当前时间: {now}"

@tool
def word_count(text: str) -> str:
    """统计输入文本的字数"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    total = chinese_chars + english_words
    return f"字数统计: 中文字符 {chinese_chars}，英文单词 {english_words}，总计 {total}"

tools = [calculate, get_current_time, word_count]
agent = create_react_agent(llm, tools)

if __name__ == "__main__":
    print("ReAct Agent 已启动，输入问题（输入 exit 退出）")
    while True:
        user_input = input("\n你问：")
        if user_input.lower() in ["exit", "quit"]:
            print("再见！")
            break
        result = agent.invoke({"messages": [("user", user_input)]})
        # 提取最后一条 AI 回复的内容（简单打印整个 result 可看到完整过程）
        # 这里只打印最终回复
        messages = result.get("messages", [])
        for msg in reversed(messages):
            if hasattr(msg, "content") and msg.content and msg.type == "ai":
                print("AI答：", msg.content)
                break
