import json
from typing import Any

import redis

from aiframework.backend.ResultBackendABC import ResultBackend


class RedisBackend(ResultBackend):
    def __init__(self, expire_time=3600):
        self.r = redis.Redis()
        self.expire_time = expire_time

    def _key(self, task_id: str, field: str) -> str:
        return f"task:{task_id}:{field}"

    def init_task(self, task_id: str) -> None:
        """初始化任务状态和结果存储"""
        pipeline = self.r.pipeline()
        pipeline.set(self._key(task_id, "status"), "pending", ex=self.expire_time)
        pipeline.set(self._key(task_id, "result"), json.dumps(None), ex=self.expire_time)
        pipeline.execute()

    def save_result(self, task_id: str, result: Any) -> None:
        """保存任务执行结果，并将状态设为 completed"""
        pipeline = self.r.pipeline()
        pipeline.set(self._key(task_id, "result"), json.dumps(result), ex=self.expire_time)
        pipeline.set(self._key(task_id, "status"), "completed", ex=self.expire_time)
        pipeline.execute()

    def get_result(self, task_id: str) -> Any:
        """获取任务执行结果"""
        result = self.r.get(self._key(task_id, "result"))
        return json.loads(result) if result else None

    def set_status(self, task_id: str, status: str) -> None:
        """设置任务当前状态（如 running / failed）"""
        self.r.set(self._key(task_id, "status"), status, ex=self.expire_time)

    def get_status(self, task_id: str) -> str:
        """获取任务当前状态"""
        status = self.r.get(self._key(task_id, "status"))
        return status.decode("utf-8") if status else "unknown"

    def cleanup(self, task_id: str = None) -> None:
        """清理任务缓存"""
        if task_id:
            keys = [
                self._key(task_id, "status"),
                self._key(task_id, "result")
            ]
            self.r.delete(*keys)
        else:
            # 扫描并删除所有任务相关键（生产环境建议用游标）
            keys = self.r.keys("task:*")
            if keys:
                self.r.delete(*keys)
