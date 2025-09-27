#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/6 17:20
# @Author  : afish
# @File    : LLMProcessor.py.py
from aiframework.core.seek import LLMClientBase
from aiframework.message.EventBus import EventBus
from aiframework.logger import logger


def handle_command(command: str, llm_client: LLMClientBase):
    logger.info(f"开始处理命令: {command}")
    try:
        llm_client.response(command)
        logger.info("命令处理完成")
    except Exception as e:
        logger.error(f"处理命令时出错: {e}")
        import traceback
        traceback.print_exc()


def register_llm_processor(event_bus: EventBus, llm_client: LLMClientBase):
    event_bus.subscribe(lambda cmd: handle_command(cmd, llm_client))