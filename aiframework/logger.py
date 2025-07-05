#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path

from aiframework.conf.PackageSettingsLoader import SettingsLoader, FrozenJSON as _FrozenJSON

# 默认日志配置
DEFAULT_LOGGING_CONFIG = {
    'ENABLED': True,
    'LOG_DIR': None,  # 默认不保存到文件
    'LOG_FORMAT': "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    'DATE_FORMAT': "%Y-%m-%d %H:%M:%S",
    'ENCODING': 'utf-8',
    'LEVEL': 'INFO',
    'MAX_BYTES': 10 * 1024 * 1024,  # 10MB
    'BACKUP_COUNT': 5,  # 保留5个备份文件
    'WHEN': 'midnight',  # 每天午夜滚动日志
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

        # 创建根日志记录器
        self._logger = logging.getLogger("aiframework")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False  # 防止传播到根日志记录器

        # 应用默认配置
        self._config = _FrozenJSON(DEFAULT_LOGGING_CONFIG)
        self._setup_handlers()

        self._initialized = True

    def configure(self, config: dict):
        """配置日志系统"""
        if config is None:
            config = {}
        merged_config = {**DEFAULT_LOGGING_CONFIG, **config}
        self._config = _FrozenJSON(merged_config)

    def load_settings(self, settings: SettingsLoader):
        """从设置加载器加载配置"""
        config = getattr(settings.settings, "LOGGING", {})
        self.configure(config.to_dict())

    def _setup_handlers(self):
        """配置日志处理器"""
        # 清除现有处理器
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)

        # 如果日志被禁用，直接返回
        if not self._config.ENABLED:
            return

        # 控制台处理器
        if self._config.CONSOLE:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self._logger.level)

            # 使用彩色格式化器
            if self._config.COLORED:
                formatter = ColoredFormatter(
                    self._config.LOG_FORMAT,
                    self._config.DATE_FORMAT
                )
            else:
                formatter = logging.Formatter(
                    self._config.LOG_FORMAT,
                    self._config.DATE_FORMAT
                )

            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

        # 文件处理器
        if self._config.FILE and self._config.LOG_DIR:
            log_dir = Path(self._config.LOG_DIR)
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                log_file = log_dir / "app.log"

                # 文件处理器（按大小滚动）
                file_handler = RotatingFileHandler(
                    filename=log_file,
                    maxBytes=self._config.MAX_BYTES,
                    backupCount=self._config.BACKUP_COUNT,
                    encoding=self._config.ENCODING
                )
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter(
                    self._config.LOG_FORMAT,
                    self._config.DATE_FORMAT
                )
                file_handler.setFormatter(file_formatter)
                self._logger.addHandler(file_handler)

                # 错误日志处理器（按时间滚动）
                if self._config.ERROR_FILE:
                    error_handler = TimedRotatingFileHandler(
                        filename=log_dir / "error.log",
                        when=self._config.WHEN,
                        backupCount=self._config.BACKUP_COUNT,
                        encoding=self._config.ENCODING
                    )
                    error_handler.setLevel(logging.ERROR)
                    error_handler.setFormatter(file_formatter)
                    self._logger.addHandler(error_handler)

            except Exception as e:
                # 回退到控制台输出错误
                sys.stderr.write(f"无法创建日志文件: {str(e)}\n")

    def __getattr__(self, name):
        """将日志方法委托给内部日志记录器"""
        return getattr(self._logger, name)


class ColoredFormatter(logging.Formatter):
    """带颜色的控制台日志格式化器"""

    COLORS = {
        'DEBUG': '\033[94m',  # 蓝色
        'INFO': '\033[92m',  # 绿色
        'WARNING': '\033[93m',  # 黄色
        'ERROR': '\033[91m',  # 红色
        'CRITICAL': '\033[95m'  # 紫色
    }
    RESET = '\033[0m'

    def format(self, record):
        """格式化日志记录并添加颜色"""
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, '')}{log_message}{self.RESET}"


# 创建全局日志实例
logger = ProjectLogger()
