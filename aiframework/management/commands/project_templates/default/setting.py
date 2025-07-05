import os

# 项目路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


from RosAi.action import *

__all__ = [
    'CommandAction',
]

from RosAi.client import *

DEFAULTS = {
    'NAME': 'windows',
    'LLM': WindowsAIAssistant,
    'ACTIONS': __all__,
    'NEED_RECOGNIZER': False,  # 禁止语音
    'COMMAND_MODE': True  # 命令模式

}
