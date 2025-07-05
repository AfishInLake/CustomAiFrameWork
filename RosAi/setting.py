#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/5/5 10:58
# @Author  : afish
# @File    : setting.py
import os

from aiframework.message.message import MessageManager

# 项目路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from RosAi.action import *

__all__ = [
    'CommandAction',
    'NetworkPingAction',
    'HTTPDownloadAction',
    'ArchiveCompressAction',
    'TextSearchAction',
    'PythonPackageAction',
    'ProcessMonitorAction',
    'DiskUsageAction',
    'FileHashAction'
]

from RosAi.client import *

AIFRAMEWORK_DEFAULTS = {
    # 基础配置
    'NAME': 'windows',
    'LLM': WindowsAIAssistant,
    'MESSAGE_MANAGER': MessageManager,
    'ACTIONS': __all__,
    'NEED_RECOGNIZER': False,  # 禁止语音
    'COMMAND_MODE': True,  # 命令模式
    'SYSTEM_PROMPT': "你是叫小胖的AI助手，请使用中文进行对话。",
}
# 日志配置
LOGGING = {
    'ENABLED': True,
    'LOG_DIR': os.path.join(BASE_DIR, 'logs'),
    'LOG_FILE': os.path.join(BASE_DIR, 'logs', 'app.log'),
    'LOG_FORMAT': "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    'DATE_FORMAT': "%Y-%m-%d %H:%M:%S",
    'MAX_BYTES': 10 * 1024 * 1024,  # 10MB
    'BACKUP_COUNT': 5,
    'WHEN': 'midnight',
    'ENCODING': 'utf-8',
    'LEVEL': 'INFO',  # 可选 DEBUG/INFO/WARNING/ERROR
}
