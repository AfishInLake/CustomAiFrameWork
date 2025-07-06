#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 12:24
# @Author  : afish
# @File    : discovery.py
import importlib.util
import inspect
from pathlib import Path

from .base import Command


def find_commands(path):
    """在指定目录中查找命令模块"""
    commands = {}
    cmd_dir = Path(path)

    if not cmd_dir.exists():
        return commands

    for entry in cmd_dir.iterdir():
        if entry.is_file() and entry.name.endswith('.py') and not entry.name.startswith('__'):
            module_name = entry.stem
            commands[module_name] = entry.absolute()

        elif entry.is_dir() and (entry / '__init__.py').exists():
            commands.update(find_commands(entry))

    return commands


def load_command_class(module_path):
    """从Python模块加载命令类"""
    try:
        spec = importlib.util.spec_from_file_location("cmd_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name in dir(module):
            obj = getattr(module, name)
            if (
                    inspect.isclass(obj)
                    and issubclass(obj, Command)
                    and obj is not Command
            ):
                return obj()
        return None
    except Exception as e:
        print(f"加载命令失败: {e}")
        raise e
