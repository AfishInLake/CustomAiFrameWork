#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/18 12:36
# @Author  : afish
# @File    : decorate.py
import abc


def singleton(cls):
    """
    单例模式装饰器
    确保一个类只有一个实例，并提供全局访问点

    Args:
        cls: 要装饰的类

    Returns:
        function: 返回一个函数，该函数负责管理类的单例实例
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls.__name__] = cls(*args, **kwargs)
        return instances[cls.__name__]
    return get_instance


class SingletonABCMeta(abc.ABCMeta):
    """
    需要与抽象类ABC结合使用

    示例：
    class ResultBackend(ABC, metaclass=SingletonABCMeta):
        pass
    """

    def __init_subclass__(cls, **kwargs):
        # 自动给子类添加 @singleton
        return singleton(super().__init_subclass__(**kwargs))


def Arguments(parameters=None, required=None):
    """
    动作参数装饰器，用于为动作类添加参数定义和描述信息

    该装饰器会为被装饰的类添加一个tools方法，该方法返回该动作的参数定义，
    供AI模型理解如何调用该动作。

    Args:
        parameters (dict, optional): 参数定义字典，键为参数名，值为参数描述信息
            每个参数描述信息通常包含:
                - type: 参数类型（如 "string", "number", "boolean" 等）
                - description: 参数描述
                - default: 默认值（可选）
        required (list, optional): 必需参数列表，包含所有必需参数的名称

    Returns:
        function: 装饰器函数

    Example:
        @Arguments(
            parameters={
                "url": {"type": "string", "description": "要访问的网站URL"},
                "timeout": {"type": "number", "description": "超时时间（秒）", "default": 30}
            },
            required=["url"]
        )
        class WebVisitAction(Action):
            '''访问指定网页的动作'''

            def perform(self, arguments):
                # 动作实现
                pass
    """
    def decorator(cls):
        # 提取类的文档字符串作为动作描述
        doc = cls.__doc__ or ""
        description = doc.strip().split('\n')[0] if doc else ""

        # 复制参数和必需参数列表，避免修改原始数据
        params = parameters.copy() if parameters else {}
        req = required.copy() if required else []

        def tools(self, *args, **kwargs):
            """
            生成动作工具定义，供AI模型调用

            Returns:
                dict: 包含动作定义的字典，格式符合OpenAI函数调用规范
            """
            return {
                "type": "function",
                "function": {
                    "name": cls.__name__,           # 动作类名作为函数名
                    "description": description,     # 动作描述
                    "parameters": params,           # 参数定义
                    "required": req                 # 必需参数列表
                }
            }

        # 为类添加tools方法
        cls.tools = tools
        return cls

    return decorator
