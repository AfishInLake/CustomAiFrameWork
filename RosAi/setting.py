#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/5/5 10:58
# @Author  : afish
# @File    : setting.py
import os

from aiframework.message.message import MessageManager

# 项目路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# MCP配置文件路径
MCP_CONFIG_PATH = os.path.join(BASE_DIR, 'RosAi', 'mcp_config.json')

from RosAi.client import *

# 从环境变量获取API密钥，如果没有则设置为空字符串
API_KEY = os.getenv('API_KEY', '')
Model = os.getenv('MODEL', 'qwen-plus')

AIFRAMEWORK_DEFAULTS = {
    # 基础配置
    'NAME': 'windows',
    'LLM': WindowsAIAssistant,
    'MESSAGE_MANAGER': MessageManager,
    "Model": Model,
    'NEED_RECOGNIZER': False,  # 禁止语音
    'COMMAND_MODE': True,  # 命令模式
    'SYSTEM_PROMPT': """
    """,
    'INPUT_TYPE': 'text',  # 可选类型  text/audio/image
    'MCP_CONFIG_PATH': "G:\desktop\RosAi\RosAi\mcp_config.json"
}
