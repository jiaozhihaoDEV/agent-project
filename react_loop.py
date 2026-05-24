# react_loop.py (第五天最终版：支持多 session 隔离和清除记忆)
import os
import datetime
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from react_parser import parse_react_output
from memory import ShortTermMemory

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    model="deepseek-v4-flash",
    temperature=0
)

def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate(expression: str):
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误: {str(e)}"

tools = {
    "get_current_time": get_current_time,
    "calculate": calculate,
}

tool_descriptions = """
- calculate: 执行数学计算，参数为表达式字符串，例如 "2+2"。
- get_current_time: 获取当前时间，无需参数。
"""

system_prompt = """你是一个智能助手，可以调用工具回答问题。

可用工具：
- calculate: 执行数学计算，参数为表达式字符串。
- get_current_time: 获取当前时间，无需参数。

规则：
1. 如果用户只是打招呼、自我介绍或问不需要工具的问题，请直接回复 Final Answer。
2. 如果需要计算或获取时间，按以下格式：
   Thought: 思考过程
   Action: 工具名
   Action Input: 参数（无参数则留空）
3. 得到观察结果后，如果还需要继续，重复步骤2；否则输出：
   Final Answer: 最终答案
4. 只输出上面的内容，不要输出多余的解释。

现在开始。"""

# 全局记忆对象（支持多 session）
memory = ShortTermMemory(max_history=5)

def build_messages(user_input, history, session_id):
    messages = [("system", system_prompt)]
    recent = memory.get_recent(session_id)
    if recent:
        messages.append(("system", f"之前的对话：\n{recent}"))
    limited_history = history[-5:] if history else []
    messages.extend(limited_history)
    messages.append(("user", user_input))
    return messages

def call_llm(messages):
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    lc_messages = []
    for role, content in messages:
        if role == "system":
            lc_messages.append(SystemMessage(content=content))
        elif role == "user":
            lc_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
    return llm.invoke(lc_messages).content

def execute_tool(action, action_input):
    if action not in tools:
        return f"错误：未找到工具 '{action}'"
    try:
        if action_input:
            return tools[action](action_input)
        else:
            return tools[action]()
    except Exception as e:
        return f"工具执行错误: {str(e)}"

def react_loop(user_input, session_id="default", max_steps=3):
    history = []
    current_step = 0
    tool_called = False

    while current_step < max_steps:
        messages = build_messages(user_input if current_step == 0 else "", history, session_id)
        response = call_llm(messages)
        print(f"\n--- Step {current_step+1} ---\n{response}\n")

        parsed = parse_react_output(response)

        if "final_answer" in parsed:
            memory.add(session_id, user_input, parsed["final_answer"])
            return parsed["final_answer"]

        action = parsed.get("action", "")
        action_input = parsed.get("action_input", "")

        if not action_input and "Action Input:" in response:
            match = re.search(r"Action Input:\s*(.+?)(?:\n|$)", response)
            if match:
                raw = match.group(1).strip()
                if raw.startswith('"') and raw.endswith('"'):
                    raw = raw[1:-1]
                if raw.startswith("'") and raw.endswith("'"):
                    raw = raw[1:-1]
                action_input = raw

        if not action and tool_called:
            history.append(("assistant", response))
            history.append(("user", "请根据上一步的观察结果直接输出 Final Answer。"))
            current_step += 1
            continue

        if not action:
            history.append(("assistant", response))
            history.append(("user", "请按照格式输出 Thought, Action, Action Input。"))
            current_step += 1
            continue

        observation = execute_tool(action, action_input)
        print(f"工具结果: {observation}")
        tool_called = True
        history.append(("assistant", response))
        history.append(("user", f"Observation: {observation}"))
        current_step += 1

    return "超出最大步数，未得到最终答案。"

if __name__ == "__main__":
    print("Agent 启动。输入 exit 退出。")
    # 让用户输入自己的会话ID（可以任意字符串，不同ID的记忆完全隔离）
    session_id = input("请输入你的用户ID（例如 zhihao, 或直接回车使用 default）：").strip()
    if not session_id:
        session_id = "default"
    print(f"当前用户ID：{session_id}，你的记忆将独立保存。输入 /clear 可清除你的对话记忆。")
    while True:
        user_input = input("\n你问：")
        if user_input.lower() in ["exit", "quit"]:
            break
        if user_input.lower() == "/clear":
            memory.clear(session_id)
            print("你的对话记忆已清除。")
            continue
        answer = react_loop(user_input, session_id=session_id)
        print("AI答：", answer)
