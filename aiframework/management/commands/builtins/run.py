#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 12:25
# @Author  : afish
# @File    : run.py
from __future__ import annotations

import os
import time

from dotenv import load_dotenv

load_dotenv()

from aiframework.conf.PackageSettingsLoader import SettingsLoader
from aiframework.logger import logger
from aiframework.management.base import Command


class RunCommand(Command):
    help = '启动开发服务器'
    aliases = ['runserver', 'run']
    category = 'server'

    def add_arguments(self, parser):
        parser.add_argument('--reload', action='store_true', help='热重载')
        parser.add_argument('--project-path', type=str, default=None, help='项目路径')

    def handle(self, reload, project_path):
        if project_path:
            # 加载项目配置
            print("当前项目路径: %s" % project_path)
            settings = SettingsLoader(project_path)  # 读取自定义app的配置
            settings.Model = os.getenv("LLM_MODEL")
            settings.API_KEY = os.getenv("DASHSCOPE_API_KEY")
            logger.load_settings(settings)
            logger.info(f"📁 使用项目路径: {project_path}")
            # 使用统一初始化方法
            from aiframework.controller.init import create_controller
            controller = create_controller(settings)

            try:
                controller.start()
                logger.info("已启动")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                controller.stop()
                logger.info("已关闭")
