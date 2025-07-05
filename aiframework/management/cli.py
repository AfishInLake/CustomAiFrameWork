#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 12:23
# @Author  : afish
# @File    : cli.py
import os
import sys
from pathlib import Path

from aiframework.management.registry import CommandRegistry


def execute_from_command_line(argv=None):
    """命令行入口函数"""
    if argv is None:
        argv = sys.argv

    # 获取命令工作目录
    command_work_path = Path(__file__).resolve().parent.parent.parent
    project_path = command_work_path / command_work_path.name  # 项目路径
    argv += ['--project-path', str(project_path)]

    # 创建命令注册表
    registry = CommandRegistry()

    # 自动发现框架内置命令
    framework_dir = os.path.dirname(__file__)
    framework_commands = os.path.join(framework_dir, 'commands', 'builtins')
    registry.autodiscover([framework_commands])

    # 发现项目级命令
    project_commands = os.path.join(os.getcwd(), 'project_commands')
    if os.path.exists(project_commands):
        registry.autodiscover([project_commands])

    # 应用命令目录
    for path in sys.path:
        apps_dir = os.path.join(path, 'apps')
        if os.path.exists(apps_dir):
            for app_name in os.listdir(apps_dir):
                app_path = os.path.join(apps_dir, app_name)
                commands_path = os.path.join(app_path, 'commands')
                if os.path.exists(commands_path):
                    registry.autodiscover([commands_path])

    # 如果没有提供命令，显示帮助信息
    if len(argv) == 1:
        registry.print_help()
        return

    command_name = argv[1]

    if command_name in ('-h', '--help'):
        registry.print_help()
        return

    # 获取并执行命令
    command = registry.get_command(command_name)
    if command:
        try:
            command.execute(argv[2:])
        except SystemExit as e:
            # 防止argparse退出导致程序结束
            if e.code != 0:
                print(f"命令执行错误: {e}")
                sys.exit(e.code)
    else:
        print(f"未知命令: {command_name}")
        registry.print_help()
        sys.exit(1)
