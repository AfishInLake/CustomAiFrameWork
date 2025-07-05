#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/4/2 15:34
# @Author  : afish
# @File    : message.py
import threading
from typing import Union

from openai.types.chat import ChatCompletionMessage

from aiframework.logger import logger
from aiframework.message.MessageABC import MessageManagerBase


class MessageManager(MessageManagerBase):
    _initialized = False
    _lock = threading.Lock()  # 类级锁，用于实例化控制

    def __init__(self):
        with MessageManager._lock:
            if not MessageManager._initialized:
                self._messages = []
                self._instance_lock = threading.Lock()  # 实例级操作锁
                MessageManager._initialized = True



    def add_message(self, role: str, content: str):
        """添加角色信息"""
        with self._instance_lock:
            self._messages.append({
                    "role": role,
                    "content": content
                })

    def add_dict_message(self, content):
        """保存对话历史或上下文信息"""
        with self._instance_lock:
            self._messages.append(content)

    def add_user_message(self, content: str):
        """添加角色信息"""
        self.add_dict_message(
            {
                'role': 'user',
                'content': content
            }
        )

    def add_assistant_message(self, msg: Union[str, ChatCompletionMessage]):
        """安全添加AI消息"""
        content = msg.content if hasattr(msg, 'content') else msg
        tool_calls = getattr(msg, 'tool_calls', None)

        message = {"role": "assistant", "content": content}
        if tool_calls:
            message["tool_calls"] = [
                {
                    "id": call.id,
                    "type": call.type,
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    }
                }
                for call in tool_calls
            ]

        self.add_dict_message(message)

    def add_tool_message(self, content: str, tool_call_id):
        """添加工具信息"""
        self.add_dict_message(
            {
                'role': 'tool',
                'content': content,
                'tool_call_id': tool_call_id
            }
        )

    def add_system_message(self, content: str):
        """添加系统信息"""
        self.add_dict_message(
            {
                'role': 'system',
                'content': content
            }
        )


    def get_messages(self):
        """获取信息"""
        with self._instance_lock:
            return self._messages.copy()

    def reset_messages(self):
        """清空信息"""
        with self._instance_lock:
            self._messages.clear()

    @property
    def messages(self):
        """返回信息列表"""
        with self._instance_lock:
            return self._messages.copy()


# 使用示例
if __name__ == "__main__":
    import concurrent.futures


    def worker(text):
        manager = MessageManager()
        manager.add_user_message(text)
        return manager.get_messages()


    # 多线程测试
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker, f"msg_{i}") for i in range(5)]
        results = [f.result() for f in futures]
