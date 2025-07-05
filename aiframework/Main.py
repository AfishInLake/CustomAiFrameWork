import threading

from aiframework.conf.PackageSettingsLoader import SettingsLoader
from aiframework.logger import logger


class MainController:
    """
    主控制类

    :params package_name 自定义项目的路径
    """

    def __init__(
            self,
            settings: SettingsLoader,
    ):
        self.package = settings  # 读取自定义app的配置
        self.action = self.package.settings.ACTION_REGISTRY  # 工具注册表
        # 大语言模型
        self.llm_client = self.package.settings.AIFRAMEWORK_DEFAULTS.LLM(
            system_prompt=self.package.settings.AIFRAMEWORK_DEFAULTS.SYSTEM_PROMPT,
            MessageManager=self.package.settings.AIFRAMEWORK_DEFAULTS.MESSAGE_MANAGER()
        )
        self.llm_client.set(
            model=self.package.Model,
            api_key=self.package.API_KEY,
            tool=self.action
        )
        self.running = False
        self.main_thread = None

    def start(self):
        """启动任务"""
        if not self.running:
            self.running = True
            # 启动主线程
            self.main_thread = threading.Thread(
                target=self._main_loop,
                daemon=True
            )
            self.main_thread.start()
            logger.info("已启动")

    def stop(self):
        """停止任务"""
        if self.running:
            self.running = False
            if self.main_thread:
                self.main_thread.join()
            logger.info("AI已停止")

    def _main_loop(self):
        """主控制循环 - 简化为处理用户输入并调用大语言模型"""
        while self.running:
            try:
                user_input = input("\n请输入指令: ").strip()
                if user_input.lower() == "exit":
                    self.stop()
                    break
                else:
                    self._process_command(user_input)
            except KeyboardInterrupt:
                self.stop()

    def _process_command(self, command: str):
        """处理AI指令"""
        self.llm_client.response(command)
