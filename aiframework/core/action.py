#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/3/16 20:49
# @Author  : afish
# @File    : action.py
from abc import ABC, abstractmethod

from aiframework.message.DataResult import ActionResult


class Action(ABC):
    """动作接口"""

    @abstractmethod
    def perform(self, arguments) -> ActionResult:
        pass




