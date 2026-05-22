from func_timeout import func_timeout, FunctionTimedOut
# react_loop.py (带调试输出的改进版)
import os
import datetime
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from react_parser import parse_react_output

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=api_key,
    model="deepseek-chat",
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

def slow_tool():
    """一个测试超时的慢速工具"""
    time.sleep(6)
    return "慢速工具执行完成"

tools = {
    "get_current_time": get_current_time,
    "calculate": calculate,
}

tool_descriptions = """
- calculate: 执行数学计算，参数为表达式字符串，例如 "2+2"。
- get_current_time: 获取当前时间，无需参数。
"""

system_prompt = f"""你是一个能够调用工具来回答问题的智能体。你有以下工具可用：

{tool_descriptions}

请严格按照以下格式输出，**不要直接给出最终答案，除非你已经通过工具获得了所有信息**。每一步必须包含 Thought 和 Action（或 Final Answer）。例如：

Thought: 我需要获取当前时间。
Action: get_current_time
Action Input: 

然后你会得到观察结果。如果需要继续，再重复上述格式。当你已经获得了足够的信息，可以输出：
Final Answer: 你的最终答案

现在开始！

**特别重要**：如果用户的问题中包含多个任务（例如“先...再...”或“然后...”），你必须依次调用所需的工具，**完成全部任务之后**才能输出 Final Answer。千万不要在只完成部分任务后就提前结束。
"""

def build_messages(user_input, history):
    messages = [("system", system_prompt)]
    messages.extend(history)
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
    response = llm.invoke(lc_messages)
    return response.content

from func_timeout import func_timeout, FunctionTimedOut

def execute_tool(action, action_input, timeout=5):
    if action not in tools:
        return f"错误：未找到工具 '{action}'，可用工具：{', '.join(tools.keys())}"
    tool_func = tools[action]
    try:
        # 使用 func_timeout 限制执行时间
        if action_input:
            result = func_timeout(timeout, tool_func, args=(action_input,))
        else:
            result = func_timeout(timeout, tool_func)
        return result
    except FunctionTimedOut:
        return f"工具 '{action}' 执行超时（超过 {timeout} 秒）"
    except Exception as e:
        return f"工具执行错误: {str(e)}"
def react_loop(user_input, max_steps=5):
    history = []
    current_step = 0
    tool_called = False

    while current_step < max_steps:
        messages = build_messages(user_input if current_step == 0 else "", history)
        response = call_llm(messages)

        # ========== 调试输出 ==========
        print(f"\n--- Step {current_step+1} 模型原始输出 ---")
        print(response)
        print("--------------------------------\n")
        # ================================

        parsed = parse_react_output(response)
        print("解析结果:", parsed)

        if "final_answer" in parsed:
            if tool_called or current_step == max_steps - 1:
                return parsed["final_answer"]
            else:
                history.append(("assistant", response))
                history.append(("user", "你还没有调用任何工具。请先调用工具获取信息，再给出最终答案。"))
                current_step += 1
                continue

        action = parsed.get("action", "")
        action_input = parsed.get("action_input", "")
        # ===== 手动修复：如果解析出的 action_input 为空，直接从原始响应中提取 =====
        if not action_input and "Action Input:" in response:
            import re
            match = re.search(r"Action Input:\s*(.+?)(?:\n|$)", response)
            if match:
                raw = match.group(1).strip()
                # 去掉首尾的引号（如果有）
                if raw.startswith('"') and raw.endswith('"'):
                    raw = raw[1:-1]
                if raw.startswith("'") and raw.endswith("'"):
                    raw = raw[1:-1]
                action_input = raw
                print(f"手动提取的 action_input: {action_input}")   # 调试输出
        # ====================================================================

        if not action:
            history.append(("assistant", response))
            history.append(("user", "请按照格式输出 Thought, Action, Action Input。"))
            current_step += 1
            continue

        observation = execute_tool(action, action_input)
        tool_called = True
        history.append(("assistant", response))
        history.append(("user", f"Observation: {observation}"))
        current_step += 1

    return "超出最大迭代次数，未能得到最终答案。"

if __name__ == "__main__":
    print("手动 ReAct Agent 启动。输入 exit 退出。")
    while True:
        user_input = input("\n你问：")
        if user_input.lower() in ["exit", "quit"]:
            break
        answer = react_loop(user_input)
        print("AI答：", answer)
