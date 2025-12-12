import threading

from aiframework.conf.PackageSettingsLoader import SettingsLoader
from aiframework.core.listen.LLMProcessor import register_llm_processor
from aiframework.core.mcp.client import MCPClientManager
from aiframework.core.seek.seek import LLMClientBase
from aiframework.infrastructure.Input.InputHandler import InputHandlerBase
from aiframework.logger import logger
from aiframework.message.EventBus import event_bus


class MainController:
    def __init__(
            self,
            settings: SettingsLoader,
            input_handler: InputHandlerBase,
            llm_client: LLMClientBase
    ):
        self.package = settings
        self.input_handler = input_handler
        self.llm_client = llm_client
        self.event_bus = event_bus
        self.running = False
        self.main_thread = None
        self.manager = MCPClientManager(self.package.settings.MCP_CONFIG)
        self.llm_client.set(
            api_key=self.package.API_KEY,
            baseurl=self.package.LLM_MODEL,
            mcp=self.manager,
            model=self.package.MODEL
        )
        register_llm_processor(self.event_bus, self.llm_client)

        logger.info("当前启用模型:\n"
                    f"model:{self.package.MODEL}\n"
                    f"baseurl:{self.package.LLM_MODEL}")
    def start(self):
        if not self.running:
            self.running = True
            self.main_thread = threading.Thread(target=self._main_loop, daemon=True)
            self.main_thread.start()
            logger.info("已启动")

    def stop(self):
        """停止任务"""
        if self.running:
            self.running = False
            if self.main_thread and self.main_thread != threading.current_thread():
                self.main_thread.join()
            self.manager.disconnect_all()
            self.manager.stop()
            logger.info("AI已停止")

    def _main_loop(self):
        while self.running:
            try:
                logger.debug("等待用户输入...")
                user_input = self.input_handler.process()

                if not user_input:
                    continue

                logger.info(f"用户输入：{user_input}")
                processed_input = user_input.strip()

                if processed_input.lower() == "exit":
                    logger.debug("接收到退出指令")
                    self.stop()
                    break
                else:
                    self.event_bus.publish(processed_input)
            except KeyboardInterrupt:
                logger.debug("捕获到键盘中断")
                self.stop()
