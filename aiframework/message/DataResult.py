#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/18 18:14
# @Author  : afish
# @File    : DataResult.py
from dataclasses import dataclass, field
from typing import Any, Optional
import json
from datetime import datetime


@dataclass
class ActionResult:
    success: bool
    data: Any = None
    error: Optional[str] = None
    error_code: int = 0
    timestamp: Optional[str] = None
    execution_time: Optional[str] = None

    def __post_init__(self):
        """初始化后处理，设置时间戳"""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    @classmethod
    def success(cls, data: Any = None, execution_time: str = None) -> 'ActionResult':
        """创建成功的ActionResult实例"""
        return cls(
            success=True,
            data=data,
            execution_time=execution_time
        )

    @classmethod
    def failure(cls, error: str, error_code: int = 1, data: Any = None) -> 'ActionResult':
        """创建失败的ActionResult实例"""
        return cls(
            success=False,
            data=data,
            error=error,
            error_code=error_code
        )

    def to_dict(self) -> dict:
        """将ActionResult转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "error_code": self.error_code,
            "timestamp": self.timestamp,
            "execution_time": self.execution_time
        }

    def to_json(self) -> str:
        """将ActionResult转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def __str__(self) -> str:
        """字符串表示，提高兼容性"""
        if self.success:
            if self.data is not None:
                # 如果data是字符串，直接返回
                if isinstance(self.data, str):
                    return self.data
                # 如果data是字典或其他对象，转换为JSON字符串
                elif hasattr(self.data, '__dict__'):
                    return json.dumps(self.data.__dict__, ensure_ascii=False)
                else:
                    return json.dumps(self.data, ensure_ascii=False)
            else:
                return "操作成功"
        else:
            error_msg = f"操作失败: {self.error}" if self.error else "操作失败"
            if self.error_code != 0:
                error_msg += f" (错误代码: {self.error_code})"
            return error_msg

    def __bool__(self) -> bool:
        """使ActionResult可以直接用作布尔值"""
        return self.success
