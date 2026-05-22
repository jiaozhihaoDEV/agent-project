# react_parser.py
import re

def parse_react_output(text: str):
    """
    从模型的文本输出中解析出 Thought, Action, Action Input。
    如果包含 Final Answer，则返回 final_answer。
    """
    # 先检查是否包含 Final Answer
    final_match = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL)
    if final_match:
        return {"final_answer": final_match.group(1).strip()}
    
    # 提取 Thought（从 "Thought:" 到下一个 "Action:" 或结尾）
    thought_match = re.search(r"Thought:\s*(.*?)\n\s*(?:Action:|$)", text, re.DOTALL)
    thought = thought_match.group(1).strip() if thought_match else ""
    
    # 提取 Action
    action_match = re.search(r"Action:\s*(\w+)", text)
    action = action_match.group(1).strip() if action_match else ""
    
    # 提取 Action Input：匹配 Action Input: 后面的所有字符，直到换行（但可能包含引号、空格等）
    input_match = re.search(r"Action Input:\s*(.*?)\n", text, re.DOTALL)
    action_input = input_match.group(1).strip() if input_match else ""
    
    # 如果 action_input 是带引号的字符串（如 "123+456"），去掉引号（保留内容）
    if action_input and action_input[0] in ['"', "'"] and action_input[-1] in ['"', "'"]:
        action_input = action_input[1:-1]
    
    return {"thought": thought, "action": action, "action_input": action_input}
