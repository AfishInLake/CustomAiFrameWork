#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/18 17:41
# @Author  : afish
# @File    : test.py
from collections import abc
from pprint import pformat


class FrozenJSON:
    """
    一个只读接口，该接口使用属性表示法表示JSON类对象
    """

    def __init__(self, mapping):
        self.__data = dict(mapping)

    def __getattr__(self, item: str):
        item = item.upper()
        try:
            return getattr(self.__data, item)
        except AttributeError:
            if item not in self.__data:
                return None
            return FrozenJSON.build(self.__data[item])

    def __dir__(self):
        return self.__data.keys()

    def __repr__(self):
        return pformat(self.__data)

    def __str__(self):
        return repr(self)

    @classmethod
    def build(cls, obj):
        if isinstance(obj, abc.Mapping):
            return cls(obj)
        elif isinstance(obj, abc.MutableSequence):
            return [cls.build(item) for item in obj]
        else:
            return obj


if __name__ == '__main__':
    LOGGING = {
        'ENABLED': True,
        'LOG_FORMAT': "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
        'DATE_FORMAT': "%Y-%m-%d %H:%M:%S",
        'ENCODING': 'utf-8',
        'LEVEL': 'INFO',  # 可选 DEBUG/INFO/WARNING/ERROR
    }
    print(FrozenJSON(LOGGING).LOG_DIR)
