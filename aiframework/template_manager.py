#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 18:07
# @Author  : afish
# @File    : template_manager.py
import importlib.resources
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, BaseLoader


class TemplateManager:
    def __init__(self):
        self.env = self._create_environment()

    def _create_environment(self):
        # 尝试加载内置模板
        try:
            templates_dir = importlib.resources.files('myframework.templates')
            return Environment(loader=FileSystemLoader(templates_dir))
        except ImportError:
            # 开发模式下使用文件系统路径
            dev_templates = Path(__file__).parent.parent / 'templates'
            return Environment(loader=FileSystemLoader(dev_templates))

    def get_template(self, template_name):
        return self.env.get_template(template_name)

    def render_template(self, template_name, context):
        template = self.get_template(template_name)
        return template.render(context)

    def render_and_write(self, template_name, context, output_path):
        content = self.render_template(template_name, context)
        output_path.write_text(content, encoding='utf-8')