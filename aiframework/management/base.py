#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 12:17
# @Author  : afish
# @File    : base.py
import argparse
from abc import ABC, abstractmethod


class Command(ABC):
    help = 'Command description'
    aliases = []
    category = 'general'

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description=self.help,
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.add_arguments(self.parser)

    def add_arguments(self, parser):
        """子类重写此方法添加自定义参数"""
        pass

    @abstractmethod
    def handle(self, *args, **kwargs):
        """命令核心逻辑实现"""
        raise NotImplementedError(
            "subclasses of Command must provide a handle() method"
        )

    def execute(self, argv):
        """执行命令的标准流程"""
        # 解析命令行参数
        args = self.parser.parse_args(argv)
        # 调用实际处理函数
        self.handle(**vars(args))
