from aiframework.message.EventBus import EventBus


def log_command(message: str):
    print(f"[LOG] 用户输入：{message}")


def register_logger(event_bus: EventBus):
    event_bus.subscribe(log_command)
