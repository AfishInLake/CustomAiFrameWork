import json
from pathlib import Path
from typing import Any

from aiframework.backend.ResultBackendABC import ResultBackend


class FileBackend(ResultBackend):
    def __init__(self, cache_dir='task_cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_filepath(self, task_id: str):
        return self.cache_dir / f'task_{task_id}.json'

    def init_task(self, task_id: str) -> None:
        filepath = self._get_filepath(task_id)
        default_data = {
            "status": "pending",
            "result": None
        }
        with open(filepath, 'w') as f:
            json.dump(default_data, f)

    def save_result(self, task_id: str, result: Any) -> None:
        filepath = self._get_filepath(task_id)
        with open(filepath, 'r+') as f:
            data = json.load(f)
            data["result"] = result
            data["status"] = "completed"
            f.seek(0)
            f.truncate()
            json.dump(data, f)

    def get_result(self, task_id: str) -> Any:
        data = self._load_task_data(task_id)
        if data:
            return data.get("result")
        return None

    def set_status(self, task_id: str, status: str) -> None:
        filepath = self._get_filepath(task_id)
        if not filepath.exists():
            raise FileNotFoundError(f"Task file for {task_id} does not exist.")

        with open(filepath, 'r+') as f:
            data = json.load(f)
            data["status"] = status
            f.seek(0)
            f.truncate()
            json.dump(data, f)

    def get_status(self, task_id: str) -> str:
        data = self._load_task_data(task_id)
        return data.get("status", "unknown") if data else "unknown"

    def cleanup(self, task_id=None):
        """清理任务缓存"""
        if task_id:
            self._get_filepath(task_id).unlink(missing_ok=True)
        else:
            for f in self.cache_dir.glob('task_*.json'):
                f.unlink()

    def _load_task_data(self, task_id: str):
        filepath = self._get_filepath(task_id)
        if not filepath.exists():
            return None
        with open(filepath, 'r') as f:
            return json.load(f)
