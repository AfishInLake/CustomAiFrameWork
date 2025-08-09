# ... existing code ...

from aiframework.core.action import Action
from aiframework.utils.decorate import Arguments
from aiframework.message.DataResult import ActionResult
from playwright.sync_api import sync_playwright
import time
import importlib.util


@Arguments(
    parameters={
        "url": {"type": "string", "description": "要访问的网站URL"},
        "script_path": {"type": "string", "description": "自定义操作脚本的路径"},
        "function_name": {"type": "string", "description": "要执行的函数名"}
    },
    required=["url", "script_path", "function_name"]
)
class BrowserControlAction(Action):
    """浏览器控制动作类，使用Playwright执行用户自定义的浏览器操作脚本"""

    def perform(self, arguments) -> ActionResult:
        try:
            url = arguments.get("url")
            script_path = arguments.get("script_path")
            function_name = arguments.get("function_name")

            # 使用Playwright启动浏览器并访问指定网站
            with sync_playwright() as p:
                # 启动浏览器（默认使用chromium）
                browser = p.chromium.launch(headless=False)  # 可视化模式便于调试
                page = browser.new_page()

                # 访问指定网站
                page.goto(url)

                # 加载并执行用户自定义脚本
                result = self._execute_user_script(page, script_path, function_name)

                # 关闭浏览器
                browser.close()

                return ActionResult(
                    success=True,
                    data={"message": f"成功执行脚本 {script_path} 中的函数 {function_name}", "result": result},
                    error_code=0
                )

        except Exception as e:
            return ActionResult(
                success=False,
                data=None,
                error_code=1,
                error_message=str(e)
            )

    def _execute_user_script(self, page, script_path, function_name):
        """
        加载并执行用户自定义脚本
        :param page: Playwright页面对象
        :param script_path: 脚本文件路径
        :param function_name: 要执行的函数名
        :return: 函数执行结果
        """
        try:
            # 动态加载脚本模块
            spec = importlib.util.spec_from_file_location("user_script", script_path)
            module = importlib.util.module_from_spec(spec)

            # 将playwright页面对象和其他工具添加到模块的全局命名空间
            module.page = page
            module.sync_playwright = sync_playwright

            spec.loader.exec_module(module)

            # 获取并执行指定函数
            if hasattr(module, function_name):
                func = getattr(module, function_name)
                return func()
            else:
                raise ValueError(f"函数 {function_name} 在脚本 {script_path} 中未找到")

        except Exception as e:
            raise RuntimeError(f"执行用户脚本时出错: {str(e)}")


# ... existing code ...
