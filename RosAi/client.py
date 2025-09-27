import platform

import psutil

from aiframework.core.seek.OpenAI.seek import OpenAIClient


class WindowsAIAssistant(OpenAIClient):
    def __init__(self, system_prompt: str, MessageManager):
        super().__init__(system_prompt, MessageManager)
        # 初始化系统信息
        self.system_info = self._get_system_info()

    def _get_system_info(self):
        """获取系统信息"""
        try:
            # 获取系统信息
            system_info = {
                '系统类型': platform.system(),
                '系统版本': platform.version(),
                '计算机名': platform.node(),
                '制造商': platform.machine(),  # 这里简化处理，实际制造商信息可能需要其他方式获取
                '型号': platform.processor(),  # 这里简化处理，实际型号信息可能需要其他方式获取
                '处理器': platform.processor(),
                '物理核心数': psutil.cpu_count(logical=False),
                '逻辑核心数': psutil.cpu_count(logical=True),
                '总内存(GB)': round(psutil.virtual_memory().total / (1024 ** 3), 2),
                '可用内存(GB)': round(psutil.virtual_memory().available / (1024 ** 3), 2)
            }

            # 格式化为字符串
            return str(system_info)
        except Exception as e:
            return f"获取系统信息失败: {str(e)}"

    def set(self, api_key: str, baseurl: str = None, *args, **kwargs):
        """设置API密钥和基础URL"""
        # 设置系统信息
        self.system_info = self._get_system_info()
        super().set(api_key, baseurl, *args, **kwargs)

