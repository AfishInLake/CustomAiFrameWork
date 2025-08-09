#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/3/16 20:49
# @Author  : afish
# @File    : action.py
from abc import ABC, abstractmethod

from aiframework.message.DataResult import ActionResult


class Action(ABC):
    """
    动作接口基类

    所有具体动作类都必须继承此类并实现perform方法。
    Action是框架中执行具体任务的基本单元，可以是系统命令执行、网络操作、
    文件处理等各种类型的任务。

    子类必须实现:
        perform方法 - 定义动作的具体执行逻辑

    约定:
        1. 动作类应使用@Arguments装饰器进行参数定义
        2. perform方法应返回ActionResult对象或兼容的格式
        3. 动作应尽量保持无状态或自身管理状态
    """

    @abstractmethod
    def perform(self, arguments) -> ActionResult:
        """
        执行动作的具体逻辑

        这是动作类的核心方法，所有具体的动作实现都需要重写此方法。
        方法接收参数字典并返回执行结果。

        Args:
            arguments (dict): 包含动作执行所需参数的字典
                参数的具体结构由@Arguments装饰器定义

        Returns:
            ActionResult: 动作执行结果对象，包含执行状态、数据和错误信息
                也可以返回字符串等其他兼容格式，但推荐使用ActionResult对象

        Example:
            def perform(self, arguments):
                url = arguments.get('url')
                # 执行具体操作
                result_data = do_something(url)
                return ActionResult.success(data=result_data)
        """
        pass




