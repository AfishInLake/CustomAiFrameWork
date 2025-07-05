#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/5 13:32
# @Author  : afish
# @File    : SystemInfo.py
import platform
import subprocess
import psutil


def detect_and_get_system_info():
    """自动检测系统类型并返回相应的系统信息"""
    system = platform.system().lower()

    if system == "windows":
        return get_windows_system_info()
    elif system == "linux":
        return get_linux_system_info()
    elif system == "darwin":  # macOS
        return get_mac_system_info()
    else:
        return {"错误": "不支持的操作系统"}


def get_windows_system_info():
    """Windows系统信息获取"""
    try:
        # 获取系统型号
        manufacturer = subprocess.check_output(
            'wmic csproduct get vendor', shell=True, stderr=subprocess.DEVNULL
        ).decode().split('\n')[1].strip()

        model = subprocess.check_output(
            'wmic csproduct get name', shell=True, stderr=subprocess.DEVNULL
        ).decode().split('\n')[1].strip()
    except Exception:
        manufacturer = model = "未知"

    # 获取硬件信息
    cpu_info = platform.processor()
    mem_info = psutil.virtual_memory()

    return {
        "系统类型": "Windows",
        "系统版本": platform.version(),
        "计算机名": platform.node(),
        "制造商": manufacturer,
        "型号": model,
        "处理器": cpu_info,
        "物理核心数": psutil.cpu_count(logical=False),
        "逻辑核心数": psutil.cpu_count(logical=True),
        "总内存(GB)": round(mem_info.total / (1024 ** 3), 2),
        "可用内存(GB)": round(mem_info.available / (1024 ** 3), 2)
    }


def get_linux_system_info():
    """Linux系统信息获取"""
    try:
        # 获取主板信息
        with open('/sys/devices/virtual/dmi/id/board_vendor', 'r') as f:
            vendor = f.read().strip()

        with open('/sys/devices/virtual/dmi/id/board_name', 'r') as f:
            model = f.read().strip()
    except Exception:
        vendor = model = "未知"

    # 获取CPU信息
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = [line.split(':')[1].strip()
                        for line in f.readlines()
                        if 'model name' in line][0]
    except Exception:
        cpu_info = "未知"

    # 内存信息
    mem_info = psutil.virtual_memory()

    return {
        "系统类型": "Linux",
        "发行版": platform.platform(),
        "主机名": platform.node(),
        "主板厂商": vendor,
        "主板型号": model,
        "处理器": cpu_info,
        "物理核心数": psutil.cpu_count(logical=False),
        "逻辑核心数": psutil.cpu_count(logical=True),
        "总内存(GB)": round(mem_info.total / (1024 ** 3), 2),
        "可用内存(GB)": round(mem_info.available / (1024 ** 3), 2)
    }


def get_mac_system_info():
    """macOS系统信息获取"""
    try:
        model_info = subprocess.check_output(
            'system_profiler SPHardwareDataType', shell=True, stderr=subprocess.DEVNULL
        ).decode()

        model = [line.split(': ')[1].strip()
                 for line in model_info.split('\n')
                 if 'Model Identifier' in line][0]

        chip = [line.split(': ')[1].strip()
                for line in model_info.split('\n')
                if 'Chip' in line][0]
    except Exception:
        model = chip = "未知"

    # 内存信息
    mem_info = psutil.virtual_memory()

    return {
        "系统类型": "macOS",
        "系统版本": platform.mac_ver()[0],
        "硬件型号": model,
        "处理器芯片": chip,
        "物理核心数": psutil.cpu_count(logical=False),
        "逻辑核心数": psutil.cpu_count(logical=True),
        "总内存(GB)": round(mem_info.total / (1024 ** 3), 2),
        "可用内存(GB)": round(mem_info.available / (1024 ** 3), 2)
    }


def print_system_info(info_dict):
    """格式化打印系统信息"""
    print("\n=== 系统信息 ===")
    for key, value in info_dict.items():
        print(f"{key:>15}: {value}")
    print("================\n")


# 使用示例
if __name__ == "__main__":
    system_info = detect_and_get_system_info()
    print_system_info(system_info)