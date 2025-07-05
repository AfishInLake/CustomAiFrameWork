#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/5/5 11:04
# @Author  : afish
# @File    : PackageSettingsLoader.py
from __future__ import annotations

import importlib.util
import sys
from collections import abc
from pathlib import Path
from pprint import pformat
from typing import Any, Dict

from aiframework.conf.register import ActionRegistry
from aiframework.utils.decorate import singleton

DEFAULTS: Dict[str, Any] = {
    # 默认名称
    'NAME': 'default_robot',
    'LLM': None,
    'ACTIONS': [],
    # 是否需要音频
    'NEED_RECOGNIZER': True,
    # 使用命令模式（默认启用轮询模式）
    'COMMAND_MODE': False
}


@singleton
class SettingsLoader:
    def __init__(self, package_path: str):
        """
        初始化配置加载器，支持动态属性访问嵌套数据

        :param package_path: 软件包的路径(可以是目录路径或包含setting.py的路径)
        """
        self.API_KEY = None
        self.Model = None
        self.package_path = Path(package_path)
        self.__settings = {}
        self._original_settings = {}  # 保存原始未处理的数据
        self.load_settings()

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
        action_registry = ActionRegistry(f"{self.package_path.name}.setting")
        action_registry.auto_discover()
        raw_settings['ACTION_REGISTRY'] = action_registry
        self.__settings = raw_settings.copy()
        return self.__settings

    @property
    def settings(self) -> FrozenJSON:
        return FrozenJSON(self.__settings)

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
    """

    def __init__(self, mapping):
        self.__data = dict(mapping)

    def __getattr__(self, item: str):
        item = item.upper()
        if item in globals():
            return globals()[item]
        try:
            return getattr(self.__data, item)
        except AttributeError:
            if item not in self.__data:
                return self
            return FrozenJSON.build(self.__data[item])

    def __dir__(self):
        return self.__data.keys()

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
        if isinstance(obj, dict):
            return {key: cls._convert(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [cls._convert(item) for item in obj]
        elif isinstance(obj, FrozenJSON):
            return cls._convert(obj.__data)
        else:
            return obj

    @classmethod
    def build(cls, obj):
        if isinstance(obj, abc.Mapping):
            return cls(obj)
        elif isinstance(obj, abc.MutableSequence):
            return [cls.build(item) for item in obj]
        else:
            return obj


# 使用示例
if __name__ == "__main__":
    # 假设软件包路径是/path/to/dog
    pass
