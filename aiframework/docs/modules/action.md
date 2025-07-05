## 动作装饰器

[Arguments](file://G:\desktop\dog\core\action.py#L18-L39) 是一个装饰器，用于为动作类添加参数和描述。具体定义如下：

```python
def Arguments(parameters=None, required=None):
    def decorator(cls):
        doc = cls.__doc__ or ""
        description = doc.strip().split('\n')[0] if doc else ""
        params = parameters.copy() if parameters else {}
        req = required.copy() if required else []

        def tools(self, *args, **kwargs):
            return {
                "type": "function",
                "function": {
                    "name": cls.__name__,
                    "description": description,
                    "parameters": params,
                    "required": req
                }
            }

        cls.tools = tools
        return cls

    return decorator
```


### 使用示例

以下是一个使用 [Arguments](file://G:\desktop\dog\core\action.py#L18-L39) 装饰器的示例：

```python
@Arguments(
    parameters={
        "param1": {"type": "string", "description": "参数1的描述"},
        "param2": {"type": "int", "description": "参数2的描述"}
    },
    required=["param1"]
)
class MyAction(Action):
    """这是一个示例动作类"""

    def perform(self, arguments):
        # 动作的具体实现
        pass
```
```null


### 解释
1. **动作抽象基类**：增加了 [Action](file://G:\desktop\dog\core\action.py#L9-L14) 类的详细说明。
2. **动作装饰器**：增加了 [Arguments](file://G:\desktop\dog\core\action.py#L18-L39) 装饰器的详细说明，并提供了一个使用示例。

这样可以确保 [action.md](file://G:\desktop\dog\core\docs\modules\action.md) 文件更加详细和有用。```
