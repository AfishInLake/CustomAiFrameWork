#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 18:07
# @Author  : afish
# @File    : code_generator.py
import ast
import astor
from aiframework.template_manager import TemplateManager


class FunctionGenerator:
    def __init__(self):
        self.template_mgr = TemplateManager()

    def generate_from_template(self, function_name, params, return_type=None, body=""):
        """使用模板生成函数"""
        context = {
            'function': function_name,
            'params': params,
            'return_type': return_type,
            'body': body
        }
        return self.template_mgr.render_template('function.py.jinja', context)

    def generate_with_ast(self, base_function_name, new_function_name, modifications=None):
        """使用AST修改生成新函数"""
        # 1. 获取基础函数模板
        base_code = self._get_base_code(base_function_name)

        # 2. 解析为AST
        base_ast = ast.parse(base_code)

        # 3. 创建AST修改器
        transformer = FunctionModifier(new_function_name, modifications)
        modified_ast = transformer.visit(base_ast)

        # 4. 生成新代码
        return astor.to_source(modified_ast)

    def _get_base_code(self, function_name):
        """获取基础函数代码（可以是内置或用户定义）"""
        # 实际实现可能从数据库或文件系统加载
        if function_name == 'base':
            return """
def base_function(data, config=None):
    \"\"\"基础处理函数\"\"\"
    # 数据处理逻辑
    processed = data * 2
    return processed
            """
        # ... 其他基础函数


class FunctionModifier(ast.NodeTransformer):
    def __init__(self, new_name, modifications):
        self.new_name = new_name
        self.modifications = modifications or {}

    def visit_FunctionDef(self, node):
        # 修改函数名
        node.name = self.new_name

        # 修改参数
        if 'parameters' in self.modifications:
            node.args = self._create_arguments(self.modifications['parameters'])

        # 修改文档字符串
        if 'docstring' in self.modifications:
            docstring = ast.Expr(value=ast.Constant(value=self.modifications['docstring']))
            node.body = [docstring] + node.body[1:]

        # 添加额外语句
        if 'extra_statements' in self.modifications:
            new_body = [ast.parse(s).body[0] for s in self.modifications['extra_statements']]
            node.body = node.body[:1] + new_body + node.body[1:]

        return node

    def _create_arguments(self, params):
        """从参数字符串创建AST参数对象"""
        # 简单实现 - 实际需要更复杂的参数处理
        args = [ast.arg(arg=param.strip(), annotation=None) for param in params.split(',')]
        return ast.arguments(
            args=args,
            defaults=[],
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            vararg=None
        )