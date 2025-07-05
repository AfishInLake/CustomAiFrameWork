#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/18 12:36
# @Author  : afish
# @File    : decorate.py
import abc


def singleton(cls):
    """
    单例模式装饰器
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
    def decorator(cls):
        doc = cls.__doc__ or ""
        description = doc.strip().split('\n')[0] if doc else ""
        params = parameters.copy() if parameters else {}
        req = required.copy() if required else []

        def tools(self, *args, **kwargs):
            return {
                "type": "function",
                "function": {
                    "name": cls.__name__,
                    "description": description,
                    "parameters": params,
                    "required": req
                }
            }

        cls.tools = tools
        return cls

    return decorator
