#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/4/1 9:14
# @Author  : afish
# @File    : task.py
import time
from collections import deque
from threading import Lock, Thread

from aiframework.backend.ResultBackendABC import ResultBackend
from aiframework.core.observer.observer import SafetyObserver
from aiframework.logger import logger
from aiframework.message.message import MessageManager
from aiframework.task.executor import *

message_manager = MessageManager()


class Task:
    """任务对象封装"""

    def __init__(
            self,
            function_name: str,
            arguments: Dict[str, Any],
            task_id: str,
            priority: int = 0,  # 默认优先级为 0
            max_retries: int = 3
    ):
        self.task_id = task_id  # 用于标识任务的唯一ID
        self.function_name = function_name  # 函数名称
        self.arguments = arguments  # 函数参数
        self.retries = 0  # 重试次数
        self.priority = priority  # 优先级
        self.max_retries = max_retries  # 最大重试次数
        self.status = "pending"  # pending, running, completed, failed
        self.result_callback = None  # 回调函数
        self.tool_call_id = None

    def set_callback(self, callback: Callable[[Any], None]):
        self.result_callback = callback


class TaskController(ITaskExecutor):
    """任务控制中心"""

    def __init__(self, resultbackend: ResultBackend, observer: SafetyObserver):
        self.task_queue = deque()
        self.lock = Lock()
        self._running = False
        self.worker_thread = None
        self.observer: SafetyObserver = observer
        self.result_backend: ResultBackend = resultbackend

    def add_task(self, task: Task) -> None:
        """线程安全的任务添加"""
        with self.lock:
            self.result_backend.init_task(task.task_id)  # 初始化任务状态
            self.task_queue.append(task.task_id)  # 发布任务到队列
        self.execute_task(task)

    def start_async_processing(self) -> None:
        """启动异步处理线程"""
        if not self._running:
            self._running = True
            self.worker_thread = Thread(target=self._process_queue, daemon=True)
            self.worker_thread.start()
            logger.info("Started async task processing")

    def stop_processing(self) -> None:
        """停止异步处理"""
        self._running = False
        if self.worker_thread:
            self.worker_thread.join()
        logger.info("Stopped async task processing")

    def _process_queue(self) -> None:
        """队列处理核心逻辑"""
        while self._running:
            task = self._get_next_task()
            if task:
                self.execute_task(task)
            else:
                # 无任务时降低CPU占用
                time.sleep(0.1)

    def _get_next_task(self) -> Optional[Task]:
        """线程安全获取下一个任务"""
        with self.lock:
            return self.task_queue.popleft() if self.task_queue else None

    def execute_task(self, task: Task) -> None:
        """执行单个任务并处理结果"""
        try:
            task.status = "running"
            # 执行实际函数调用
            result = self.run(task.function_name, task.arguments)
            if task.result_callback:
                task.result_callback(result)
            # 记录成功消息
            self._record_success(task.task_id)
            task.status = "completed"
            logger.info(f"Task succeeded: {task.function_name}")
        except Exception as e:
            self._handle_failure(task, e)

    def run(self, *args, **kwargs) -> str:
        try:
            function, *args = args  # 分离函数和参数
            return function(*args, **kwargs)  # 向函数传参并执行
        except AttributeError as e:
            logger.error(str(e))
            return f"执行错误：{str(e)}"

    def _record_success(self, tool_call_id: str) -> None:
        """记录执行成功的系统消息"""
        message_manager.add_tool_message("执行成功", tool_call_id)

    def _handle_failure(self, task: Task, error: Exception) -> None:
        """失败处理逻辑"""
        task.retries += 1
        if task.retries < task.max_retries:
            with self.lock:
                self.task_queue.appendleft(task)  # 重新放回队列头部
            logger.warning(f"Retrying task: {task.function_name} (attempt {task.retries})")
        else:
            task.status = "failed"
            logger.error(f"Task failed after {task.max_retries} attempts: {task.function_name}")
            # 记录错误信息到系统消息
            message_manager.add_tool_message(f"执行失败: {str(error)}", task.tool_call_id)

    def flush_queue(self) -> None:
        """立即同步处理所有任务"""
        while self.task_queue:
            task = self.task_queue.popleft()
            self.execute_task(task)

    def get_result(self, task_id):
        return self.result_backend.get_result(task_id)


taskcontroller = TaskController()
if __name__ == '__main__':
    pass
