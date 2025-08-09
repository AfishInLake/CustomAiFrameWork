#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

from loguru import logger as _logger
from aiframework.conf.PackageSettingsLoader import SettingsLoader, FrozenJSON as _FrozenJSON

# 默认日志配置
DEFAULT_LOGGING_CONFIG = {
    'ENABLED': True,
    'LOG_DIR': None,  # 默认不保存到文件
    'LOG_FORMAT': "<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <cyan>{name}</cyan> - <level>{level}</level> - <level>{message}</level> [<cyan>{file}</cyan>:<cyan>{line}</cyan>]",
    'LEVEL': 'INFO',
    'MAX_BYTES': "10 MB",  # 10MB
    'BACKUP_COUNT': 5,  # 保留5个备份文件
    'ROTATION_TIME': '00:00',  # 每天午夜滚动日志
    'CONSOLE': True,  # 默认启用控制台输出
    'FILE': False,  # 默认不保存到文件
    'ERROR_FILE': False,  # 默认不单独保存错误日志
    'COLORED': True,  # 默认启用彩色控制台输出
}


class ProjectLogger:
    """全局日志管理器"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 移除默认的日志配置
        _logger.remove()

        # 应用默认配置
        self._config = _FrozenJSON(DEFAULT_LOGGING_CONFIG)
        self._setup_handlers()

        self._initialized = True

    def configure(self, config: dict):
        """配置日志系统"""
        if config is None:
            config = {}
        merged_config = {**DEFAULT_LOGGING_CONFIG, **config}
        # 转换 logging 格式字符串为 loguru 格式字符串
        if 'LOG_FORMAT' in merged_config and '%(asctime)s' in merged_config['LOG_FORMAT']:
            # 简单转换 logging 格式到 loguru 格式
            format_str = merged_config['LOG_FORMAT']
            format_str = format_str.replace('%(asctime)s', '<green>{time:YYYY-MM-DD HH:mm:ss}</green>')
            format_str = format_str.replace('%(name)s', '<cyan>{name}</cyan>')
            format_str = format_str.replace('%(levelname)s', '<level>{level}</level>')
            format_str = format_str.replace('%(message)s', '<level>{message}</level>')
            format_str = format_str.replace('%(filename)s', '<cyan>{file}</cyan>')
            format_str = format_str.replace('%(lineno)d', '<cyan>{line}</cyan>')
            merged_config['LOG_FORMAT'] = format_str

        self._config = _FrozenJSON(merged_config)
        self._setup_handlers()

    def load_settings(self, settings: SettingsLoader):
        """从设置加载器加载配置"""
        config = getattr(settings.settings, "LOGGING", {})
        self.configure(config.to_dict())

    def _setup_handlers(self):
        """配置日志处理器"""
        # 移除所有现有的处理器
        _logger.remove()

        # 如果日志被禁用，添加一个空的sink
        if not self._config.ENABLED:
            _logger.add(sys.stderr, level="CRITICAL")
            return

        # 控制台处理器
        if self._config.CONSOLE:
            _logger.add(
                sys.stdout,
                format=self._config.LOG_FORMAT,
                level=self._config.LEVEL,
                colorize=self._config.COLORED
                )

        # 文件处理器
        if self._config.FILE and self._config.LOG_DIR:
            log_dir = Path(self._config.LOG_DIR)
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                log_file = log_dir / "app.log"

                # 文件处理器（按大小滚动）
                _logger.add(
                    log_file,
                    format=self._config.LOG_FORMAT,
                    level="DEBUG",
                    rotation=self._config.MAX_BYTES,
                    retention=self._config.BACKUP_COUNT,
                    encoding="utf-8"
                )

                # 错误日志处理器（按时间滚动）
                if self._config.ERROR_FILE:
                    error_file = log_dir / "error.log"
                    _logger.add(
                        error_file,
                        format=self._config.LOG_FORMAT,
                        level="ERROR",
                        rotation=self._config.ROTATION_TIME,
                        retention=self._config.BACKUP_COUNT,
                        encoding="utf-8"
                    )

            except Exception as e:
                # 回退到控制台输出错误
                sys.stderr.write(f"无法创建日志文件: {str(e)}\n")

    def __getattr__(self, name):
        """将日志方法委托给loguru logger"""
        return getattr(_logger, name)


# 创建全局日志实例
logger = ProjectLogger()
