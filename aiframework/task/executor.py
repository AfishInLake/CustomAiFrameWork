#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/15 18:25
# @Author  : afish
# @File    : executor.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable

class ITaskExecutor(ABC):
    """
    任务执行器接口，用于解耦 TaskController 与具体任务逻辑。
    支持多种任务执行方式（如本地线程池、RabbitMQ、Redis 队列等），并通过依赖注入实现解耦。
    """

    @abstractmethod
    def execute_task(self, task: 'Task') -> None:
        """
        执行指定任务。
        :param task: Task 对象
        """
        pass

    @abstractmethod
    def add_task(self, task: 'Task') -> None:
        """
        添加任务到队列中
        :param task: Task 对象
        """
        pass

    @abstractmethod
    def get_result(self, task_id: str) -> Any:
        """
        获取任务执行结果
        :param task_id: 任务唯一标识符
        :return: 任务结果
        """
        pass

    # @abstractmethod
    # def cancel_task(self, task_id: str) -> bool:
    #     """
    #     取消一个正在执行的任务
    #     :param task_id: 任务唯一标识符
    #     :return: 是否成功取消
    #     """
    #     pass
    #
    # @abstractmethod
    # def flush(self) -> None:
    #     """
    #     强制同步执行所有排队任务（适用于本地线程池模式）
    #     """
    #     pass

    @abstractmethod
    def start_async_processing(self) -> None:
        """
        启动异步任务处理线程
        """
        pass

    @abstractmethod
    def stop_processing(self) -> None:
        """
        停止异步任务处理
        """
        pass
