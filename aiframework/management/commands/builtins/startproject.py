#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 12:25
# @Author  : afish
# @File    : startproject.py
import os
import shutil
from pathlib import Path

from aiframework.management.base import Command


class StartProjectCommand(Command):
    help = '创建新项目'
    aliases = ['start', 'createproject']

    def add_arguments(self, parser):
        parser.add_argument('name', help='项目名称')
        parser.add_argument(
            '--template',
            help='自定义项目模板路径'
        )

    def handle(self, name, template=None):
        # 默认模板路径
        templates_dir = Path(__file__).parent.parent / 'project_templates'
        if template:
            template_path = Path(template).absolute()
            if not template_path.exists():
                raise ValueError(f"错误: 模板不存在 {template_path}")
        else:
            template_path = templates_dir / 'default'

        project_path = Path.cwd() / name

        if project_path.exists():
            raise ValueError(f"错误: 目录 {name} 已存在")

        # 复制项目模板
        shutil.copytree(template_path, project_path)

        # 替换项目名称
        for root, _, files in os.walk(project_path):
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                # 只处理文本文件
                if file_path.suffix in ('.py', '.txt', '.md', '.html', '.css', '.js'):
                    # 尝试多种编码读取
                    encodings = ['utf-8', 'gbk', 'latin-1']
                    content = None
                    for enc in encodings:
                        try:
                            content = file_path.read_text(encoding=enc)
                            break
                        except UnicodeDecodeError:
                            continue
                    # 所有编码尝试失败
                    if content is None:
                        print(f"! 无法读取文件: {file_path}")
                        continue
                    # 替换项目名称占位符
                    content = content.replace('{{project_name}}', name)
                    # UTF-8写入
                    try:
                        file_path.write_text(content, encoding='utf-8')
                    except Exception as e:
                        print(f"! 写入文件失败: {file_path} - {str(e)}")
        print(f"✅ 项目创建成功: {project_path}")
        print(f"cd {name}\nmycli run")
