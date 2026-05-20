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

@tool
def calculate(expression: str) -> str:
    """执行数学计算，例如 '2+2' 或 '(3*4)/2'"""
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def get_current_time() -> str:
    """获取当前日期和时间（年-月-日 时:分:秒）"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"当前时间: {now}"
@tool
def word_count(text: str) -> str:
    """统计输入文本的字数（中文按字符数，英文按单词数）"""
    # 简单实现：统计字符数（含空格）
    char_count = len(text)
    word_count = len(text.split())
    return f"字符数(含空格): {char_count}, 单词数: {word_count}"

tools = [calculate, get_current_time, word_count]
agent = create_react_agent(llm, tools)

if __name__ == "__main__":
    result = agent.invoke({"messages": [("user", "请统计这句话有多少个字：Hello world 你好世界")]})
    print(result)
