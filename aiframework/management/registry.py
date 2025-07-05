#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 12:24
# @Author  : afish
# @File    : registry.py
from aiframework.management.discovery import find_commands, load_command_class


class CommandRegistry:
    def __init__(self):
        self.commands = {}
        self.aliases = {}
        self.categories = {}

    def autodiscover(self, paths=None):
        """自动发现并注册命令"""
        if not paths:
            paths = []

        for path in paths:
            # 查找所有命令模块
            commands_map = find_commands(path)

            for name, mod_path in commands_map.items():
                command = load_command_class(mod_path)
                if command:
                    self.register(name, command)

    def register(self, name, command):
        """注册单个命令"""
        # 主命令名
        self.commands[name] = command

        # 处理命令别名
        for alias in (command.aliases or []):
            self.aliases[alias] = name

        # 按类别分组
        category = command.category or 'general'
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(name)

    def get_command(self, name):
        """获取命令实例"""
        # 首先检查别名
        actual_name = self.aliases.get(name, name)
        return self.commands.get(actual_name, None)

    def print_help(self):
        """打印帮助信息"""
        print("可用命令:\n")
        for category, commands in self.categories.items():
            print(f"{category.title()} 命令:")
            for cmd in commands:
                desc = self.commands[cmd].help.split('\n')[0]
                aliases = ', '.join(self.commands[cmd].aliases)
                if aliases:
                    print(f"  {cmd:<15} ({aliases}) {desc}")
                else:
                    print(f"  {cmd:<15} {desc}")
            print()