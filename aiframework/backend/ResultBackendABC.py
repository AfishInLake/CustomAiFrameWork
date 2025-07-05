#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/15 17:32
# @Author  : afish
# @File    : ResultBackendABC.py
from abc import ABC, abstractmethod
from typing import Any

from aiframework.utils.decorate import SingletonABCMeta


class ResultBackend(ABC, metaclass=SingletonABCMeta):
    """
    任务结果存储的抽象接口
    """

    @abstractmethod
    def init_task(self, task_id: str) -> None:
        """
        初始化任务状态存储
        """
        pass

    @abstractmethod
    def save_result(self, task_id: str, result: Any) -> None:
        """
        保存任务执行结果
        """
        pass

    @abstractmethod
    def get_result(self, task_id: str) -> Any:
        """
        获取任务执行结果
        """
        pass

    @abstractmethod
    def set_status(self, task_id: str, status: str) -> None:
        """
        设置任务状态（pending/running/completed/failed）
        """
        pass

    @abstractmethod
    def get_status(self, task_id: str) -> str:
        """
        获取任务当前状态
        """
        pass
