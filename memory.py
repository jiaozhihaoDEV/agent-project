# memory.py
class ShortTermMemory:
    def __init__(self, max_history=5):
        """
        初始化短期记忆
        :param max_history: 每个 session 最多保留多少轮对话（默认5轮）
        """
        self.max_history = max_history
        # sessions 字典：key = session_id (字符串), value = 列表，每个元素是 (user_msg, ai_msg) 元组
        self.sessions = {}

    def add(self, session_id, user_message, ai_message):
        """
        添加一轮对话到指定 session 的记忆中。
        如果超过 max_history，则移除最早的对话。
        """
        # 如果该 session 还没有对话列表，先创建一个空列表
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        # 将本轮对话追加到列表末尾
        self.sessions[session_id].append((user_message, ai_message))
        # 如果列表长度超过最大限制，移除最早的一条（索引0）
        if len(self.sessions[session_id]) > self.max_history:
            self.sessions[session_id].pop(0)

    def get_recent(self, session_id, k=None):
        """
        获取指定 session 中最近 k 条对话（默认 k = max_history）。
        返回格式：字符串，例如 "User: 我叫小明\nAI: 你好小明\n"
        """
        if session_id not in self.sessions:
            return ""  # 没有记忆则返回空字符串
        history = self.sessions[session_id]
        if k is None:
            k = self.max_history
        # 取最后 k 条（即最近的 k 条对话）
        recent = history[-k:] if k <= len(history) else history
        # 格式化成字符串
        formatted = ""
        for user_msg, ai_msg in recent:
            formatted += f"User: {user_msg}\nAI: {ai_msg}\n"
        return formatted

    def clear(self, session_id):
        """清除指定 session 的所有记忆"""
        if session_id in self.sessions:
            del self.sessions[session_id]

