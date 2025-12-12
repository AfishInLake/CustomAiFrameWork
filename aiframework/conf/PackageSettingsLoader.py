#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/5/5 11:04
# @Author  : afish
# @File    : PackageSettingsLoader.py
from __future__ import annotations

import importlib.util
import os
import sys
from collections import abc
from pathlib import Path
from pprint import pformat
from typing import Any, Dict

from aiframework.logger import logger
from aiframework.utils.decorate import singleton

DEFAULTS: Dict[str, Any] = {
    # 默认名称
    'NAME': 'default_robot',
    'LLM': None,
    'ACTIONS': [],
    # 是否需要音频
    'NEED_RECOGNIZER': False,
    # 使用命令模式（默认启用轮询模式）
    'COMMAND_MODE': False
}


@singleton
class SettingsLoader:
    _instances = {}  # 类级别的实例缓存

    def __new__(cls, package_path: str):
        """重写 __new__ 方法实现基于 package_path 的单例"""
        package_path_str = str(package_path)
        if package_path_str not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[package_path_str] = instance
            instance._initialized = False
        return cls._instances[package_path_str]

    def __init__(self, package_path: str):
        """
        初始化配置加载器，支持动态属性访问嵌套数据

        :param package_path: 软件包的路径(可以是目录路径或包含setting.py的路径)
        """
        # 防止重复初始化
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.API_KEY = None
        self.MODEL = None
        self.package_path = Path(package_path)
        self.__settings = {}
        self._original_settings = {}  # 保存原始未处理的数据
        self._frozen_settings = None  # 缓存 FrozenJSON 实例
        self._mcp_unified_manager = None  # 缓存 _mcp_unified_manager

        self.load_settings()
        self._initialized = True

    def load_settings(self) -> Dict[str, Any]:
        """
        加载配置并处理嵌套结构

        :return: 包含所有配置的字典（已处理嵌套结构）
        """
        # 确定setting.py文件的路径
        setting_file = self.package_path / "setting.py" if self.package_path.is_dir() else self.package_path

        if not setting_file.exists():
            raise FileNotFoundError(f"Setting file not found at {setting_file}")

        # 动态加载模块
        module_name = f"dog_settings_{hash(setting_file)}"  # 唯一模块名
        spec = importlib.util.spec_from_file_location(module_name, setting_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load settings from {setting_file}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # 获取模块变量并处理嵌套结构
        raw_settings = {k: v for k, v in vars(module).items() if not k.startswith('_')}

        # 加载MCP配置
        import json
        mcp_config_path = raw_settings.get('MCP_CONFIG_PATH')
        if mcp_config_path and os.path.exists(mcp_config_path):
            try:
                with open(mcp_config_path, 'r', encoding='utf-8') as f:
                    mcp_config = json.load(f)
                raw_settings['MCP_CONFIG'] = mcp_config
                logger.info(f"已加载MCP配置: {mcp_config_path}")
            except Exception as e:
                logger.error(f"加载MCP配置失败: {e}")
        else:
            logger.warning(f"MCP配置文件不存在: {mcp_config_path}")

        # 设置API密钥和模型
        self.API_KEY = raw_settings.get('API_KEY', '')
        self.MODEL = raw_settings.get('MODEL', 'qwen-plus')
        self.LLM_MODEL = raw_settings.get('LLM_MODEL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self.__settings = raw_settings.copy()

        # 清除缓存的 FrozenJSON
        self._frozen_settings = None

        return self.__settings

    @property
    def settings(self) -> FrozenJSON:
        """延迟创建 FrozenJSON 实例"""
        if self._frozen_settings is None:
            self._frozen_settings = FrozenJSON(self.__settings)
        return self._frozen_settings

    def __repr__(self):
        """
        返回开发者友好的字符串表示
        """
        return f"SettingsLoader(package_path={self.package_path}, settings={self.__settings})"

    def __str__(self):
        """
        返回用户友好的格式化字符串
        """
        return f"Settings from {self.package_path}:\n{pformat(self.__settings)}"


class FrozenJSON:
    """
    一个只读接口，该接口使用属性表示法表示JSON类对象
    优化版：减少不必要的递归和转换
    """

    def __init__(self, mapping):
        # 直接存储原始数据，延迟转换
        self.__data = mapping
        self.__cache = {}  # 缓存已转换的属性

    def __getattr__(self, item: str):
        # 先检查缓存
        if item in self.__cache:
            return self.__cache[item]

        # 检查全局变量（仅限大写项）
        item_upper = item.upper()
        if item_upper in globals():
            value = globals()[item_upper]
            self.__cache[item] = value
            return value

        # 检查数据
        if item in self.__data:
            value = self.__build_cached(self.__data[item], item)
            return value

        # 尝试使用大写形式
        if item_upper in self.__data:
            value = self.__build_cached(self.__data[item_upper], item_upper)
            return value

        # 如果找不到，返回自身（保持原有行为）
        return self

    def __getitem__(self, key):
        """
        支持字典式的访问，例如 config['mcpServers']
        """
        if key in self.__data:
            return self.__build_cached(self.__data[key], key)
        raise KeyError(f"Key '{key}' not found in FrozenJSON object")

    def __build_cached(self, obj, key):
        """构建并缓存转换后的对象"""
        result = self.build(obj)
        self.__cache[key] = result
        return result

    def __dir__(self):
        return list(self.__data.keys())

    def __repr__(self):
        return pformat(self.__data)

    def __str__(self):
        return repr(self)

    def to_dict(self) -> dict:
        """递归将 FrozenJSON 对象转换为原生 dict"""
        return self._convert(self.__data)

    @classmethod
    def _convert(cls, obj):
        """
        递归处理嵌套结构
        支持: dict, list, tuple, FrozenJSON
        """
        # 基本类型直接返回
        if not isinstance(obj, (dict, list, tuple, FrozenJSON)):
            return obj

        # 处理字典
        if isinstance(obj, dict):
            return {key: cls._convert(value) for key, value in obj.items()}

        # 处理序列
        if isinstance(obj, (list, tuple)):
            return [cls._convert(item) for item in obj]

        # 处理 FrozenJSON
        if isinstance(obj, FrozenJSON):
            return cls._convert(obj.__data)

        return obj

    @classmethod
    def build(cls, obj):
        """优化后的构建方法，减少不必要的递归"""
        # 基本类型直接返回
        if not isinstance(obj, (abc.Mapping, abc.MutableSequence)):
            return obj

        # 映射类型转换为 FrozenJSON
        if isinstance(obj, abc.Mapping):
            return cls(obj)

        # 序列类型递归处理
        if isinstance(obj, abc.MutableSequence):
            # 只有当元素需要转换时才递归
            for i, item in enumerate(obj):
                if isinstance(item, (abc.Mapping, abc.MutableSequence)):
                    obj[i] = cls.build(item)
            return obj

        return obj


# 使用示例
if __name__ == "__main__":
    # 假设软件包路径是/path/to/dog
    pass
