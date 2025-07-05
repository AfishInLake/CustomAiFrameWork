#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/18 18:14
# @Author  : afish
# @File    : DataResult.py
from dataclasses import dataclass
from typing import Any


@dataclass
class ActionResult:
    success: bool
    data: Any = None
    error: str = None
    timestamp: str = None
    execution_time: str = None