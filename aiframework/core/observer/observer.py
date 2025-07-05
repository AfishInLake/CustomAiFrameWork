from abc import ABC, abstractmethod
from typing import Dict


class SafetyObserver(ABC):
    @abstractmethod
    def update(self, task_data: Dict) -> bool:
        """返回True表示任务安全"""
        pass