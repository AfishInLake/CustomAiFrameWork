#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/6 17:29
# @Author  : afish
# @File    : init.py
from aiframework.conf.PackageSettingsLoader import SettingsLoader
from aiframework.infrastructure.Factory import InputFactory
from aiframework.main import MainController


def create_controller(settings: SettingsLoader):
    """创建控制器实例"""
    # 初始化输入处理器
    input_handler = InputFactory.get_handler(
        input_type=settings.settings.AIFRAMEWORK_DEFAULTS.INPUT_TYPE,
        api_key=settings.API_KEY
    )

    # 创建主控制器
    controller = MainController(
        settings=settings,
        input_handler=input_handler,
        llm_client=settings.settings.AIFRAMEWORK_DEFAULTS.LLM(
            system_prompt=settings.settings.AIFRAMEWORK_DEFAULTS.SYSTEM_PROMPT,
            MessageManager=settings.settings.AIFRAMEWORK_DEFAULTS.MESSAGE_MANAGER()
        )
    )

    return controller
