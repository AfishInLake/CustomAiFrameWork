from importlib import import_module
from typing import Optional, Dict, List, Type, Any

from aiframework.utils.decorate import singleton


@singleton
class ActionRegistry:
    def __init__(self, module_path: str):
        """
        :param module_path: 完整模块路径，如 "package.setting"
        """
        self.actions_map: Dict[str, Any] = {}
        self.tools: List[Any] = []
        self.tools_name: List[str] = []
        self.module_path = module_path

    def register_action(self, action_class: Type):
        """注册动作类"""
        instance = action_class()
        self.actions_map[action_class.__name__] = instance
        self.tools.append(instance.tools())
        self.tools_name.append(action_class.__name__)

    def auto_discover(self):
        """自动发现并注册所有动作（延迟导入避免循环依赖）"""
        try:
            module = import_module(self.module_path)
            for action_name in getattr(module, "__all__", []):
                action_class = getattr(module, action_name)
                self.register_action(action_class)
        except ImportError as e:
            raise ValueError(f"无法加载模块 {self.module_path}: {e}")
        except AttributeError:
            raise AttributeError(f"模块 {self.module_path} 缺少 __all__ 属性")

    def get_action(self, action_name: str) -> Optional[Any]:
        return self.actions_map.get(action_name)

    def get_tools(self) -> List[Any]:
        """获取所有工具的 Arguments 数据"""
        return self.tools

    def get_tools_name(self) -> List[str]:
        return self.tools_name
