#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/6 17:29
# @Author  : afish
# @File    : init.py
from aiframework.logger import logger

from aiframework.conf.PackageSettingsLoader import SettingsLoader
from aiframework.infrastructure.Factory import InputFactory
from aiframework.main import MainController


def init_controllers(settings):
    """初始化所有控制器"""
    logger.info("开始创建控制器")
    
    # 在这里获取MCP工具，确保事件循环正确处理
    try:
        action_registry = settings.settings.ACTION_REGISTRY
        if action_registry and action_registry.initialized:
            logger.info("开始获取MCP工具列表")
            tools = action_registry.get_all_tools()
            logger.info(f"成功获取到 {len(tools)} 个工具")
            logger.debug(f"工具列表: {tools}")
    except Exception as e:
        logger.error(f"获取MCP工具列表失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 初始化主控制器
    main_controller = MainController(settings)
    logger.success("控制器创建完成")
    return main_controller


def create_controller(settings: SettingsLoader):
    """创建控制器实例"""
    # 初始化输入处理器
    defaults = getattr(settings.settings, 'AIFRAMEWORK_DEFAULTS')
    input_type = getattr(defaults, 'INPUT_TYPE')
    api_key = getattr(settings, 'API_KEY', None)
    
    input_handler = InputFactory.get_handler(
        input_type=input_type,
        api_key=api_key
    )

    # 创建主控制器
    controller = MainController(
        settings=settings,
        input_handler=input_handler,
        llm_client=getattr(defaults, 'LLM')(
            system_prompt=getattr(defaults, 'SYSTEM_PROMPT'),
            MessageManager=getattr(defaults, 'MESSAGE_MANAGER')()
        )
    )

    return controller