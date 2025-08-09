#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/6 17:17
# @Author  : afish
# @File    : EventBus.py
from typing import Callable, List


class EventBus:
    def __init__(self):
        self._handlers = []

    def subscribe(self, handler: Callable[[str], None]):
        self._handlers.append(handler)

    def publish(self, message: str):
        for handler in self._handlers:
            handler(message)


event_bus = EventBus()