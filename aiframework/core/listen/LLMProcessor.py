#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/6 17:20
# @Author  : afish
# @File    : LLMProcessor.py.py
from aiframework.core.seek import LLMClientBase
from aiframework.message.EventBus import EventBus


def handle_command(command: str, llm_client: LLMClientBase):
    llm_client.response(command)


def register_llm_processor(event_bus: EventBus, llm_client: LLMClientBase):
    event_bus.subscribe(lambda cmd: handle_command(cmd, llm_client))
