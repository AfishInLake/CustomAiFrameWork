#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/5/5 10:25
# @Author  : afish
# @File    : action.py
import os
import shutil
import subprocess

from aiframework.core.action import Action
from aiframework.utils.decorate import Arguments
from aiframework.logger import logger


@Arguments(
    parameters={
        "command": {
            "type": "string",
            "description": "执行系统命令，例如：查看内存使用情况、运行脚本、查询系统信息等（危险操作需谨慎）",
            "name": "command"
        },
        "timeout": {
            "type": "number",
            "description": "命令超时时间（秒），默认 10 秒",
            "name": "timeout",
            "default": 60
        }
    },
    required=["command"]
)
class CommandAction(Action):
    """执行系统命令动作（危险！需谨慎使用）"""

    def perform(self, *args, **kwargs):
        command = kwargs["command"]
        timeout = kwargs.get("timeout", 60)

        logger.warning(f"⚠️ 正在执行系统命令: {command}")

        try:
            # 执行命令并捕获输出
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                timeout=timeout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output = f"✅ 命令执行成功:\n{result.stdout}"
            if result.stderr:
                output += f"\n⚠️ 错误输出:\n{result.stderr}"
            return output

        except subprocess.TimeoutExpired:
            error_msg = f"❌ 命令执行超时（{timeout}秒）: {command}"
            logger.error(error_msg)
            return error_msg

        except subprocess.CalledProcessError as e:
            error_msg = f"❌ 命令执行失败（返回值 {e.returncode}）:\n{e.stderr}"
            logger.error(error_msg)
            return error_msg


@Arguments(
    parameters={
        "target": {
            "type": "string",
            "description": "目标IP或域名",
            "required": True
        },
        "count": {
            "type": "number",
            "description": "探测次数",
            "default": 4
        }
    }
)
class NetworkPingAction(Action):
    """执行Ping网络探测"""

    def perform(self, *args, **kwargs):
        target = kwargs["target"]
        count = kwargs.get("count", 4)

        cmd = f"ping -n {count} {target}"
        try:
            result = subprocess.run(cmd, shell=True, check=True,
                                    stdout=subprocess.PIPE, text=True)
            return f"Ping结果:\n{result.stdout}"
        except subprocess.CalledProcessError as e:
            return f"Ping失败: {e.stderr}"


@Arguments(
    parameters={
        "url": {
            "type": "string",
            "description": "下载URL地址",
            "required": True
        },
        "output": {
            "type": "string",
            "description": "本地保存路径",
            "default": "./download.tmp"
        }
    }
)
class HTTPDownloadAction(Action):
    """通过HTTP下载文件"""

    def perform(self, *args, **kwargs):
        try:
            import requests
            response = requests.get(kwargs["url"], stream=True)
            with open(kwargs["output"], 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return f"文件已保存至: {kwargs['output']}"
        except Exception as e:
            return f"下载失败: {str(e)}"


@Arguments(
    parameters={
        "files": {
            "type": "string",
            "description": "要压缩的文件路径（多个用逗号分隔）",
            "required": True
        },
        "output": {
            "type": "string",
            "description": "压缩包输出路径",
            "default": "./archive.zip"
        },
        "password": {
            "type": "string",
            "description": "加密密码（可选）"
        }
    }
)
class ArchiveCompressAction(Action):
    """创建加密压缩包"""

    def perform(self, *args, **kwargs):
        files = kwargs["files"].split(',')
        cmd = f'7z a "{kwargs["output"]}" {" ".join(files)}'
        if kwargs.get("password"):
            cmd += f' -p{kwargs["password"]}'

        try:
            subprocess.run(cmd, check=True, shell=True)
            return f"压缩包创建成功: {kwargs['output']}"
        except subprocess.CalledProcessError as e:
            return f"压缩失败: {e.stderr}"


@Arguments(
    parameters={
        "path": {
            "type": "string",
            "description": "搜索目录路径",
            "default": "."
        },
        "pattern": {
            "type": "string",
            "description": "搜索的正则表达式",
            "required": True
        }
    }
)
class TextSearchAction(Action):
    """递归搜索文件内容"""

    def perform(self, *args, **kwargs):
        try:
            import re
            matches = []
            for root, _, files in os.walk(kwargs["path"]):
                for file in files:
                    path = os.path.join(root, file)
                    with open(path, 'r', errors='ignore') as f:
                        if re.search(kwargs["pattern"], f.read()):
                            matches.append(path)
            return f"匹配文件:\n" + "\n".join(matches) if matches else "未找到匹配内容"
        except Exception as e:
            return f"搜索出错: {str(e)}"


@Arguments(
    parameters={
        "operation": {
            "type": "string",
            "description": "操作类型(install/uninstall/upgrade)",
            "required": True
        },
        "package": {
            "type": "string",
            "description": "包名称",
            "required": True
        }
    }
)
class PythonPackageAction(Action):
    """Python包管理工具"""

    def perform(self, *args, **kwargs):
        op = kwargs["operation"].lower()
        valid_ops = ["install", "uninstall", "upgrade"]
        if op not in valid_ops:
            return f"无效操作，可选: {', '.join(valid_ops)}"

        cmd = f"pip {op} {kwargs['package']} -y"
        try:
            subprocess.run(cmd, check=True, shell=True)
            return f"成功: pip {op} {kwargs['package']}"
        except subprocess.CalledProcessError as e:
            return f"操作失败: {e.stderr}"


@Arguments(
    parameters={
        "name": {
            "type": "string",
            "description": "进程名称（支持通配符）"
        },
        "kill": {
            "type": "boolean",
            "description": "是否结束进程",
            "default": False
        }
    }
)
class ProcessMonitorAction(Action):
    """Windows进程管理"""

    def perform(self, *args, **kwargs):
        cmd = f'tasklist /FI "IMAGENAME eq {kwargs["name"]}"' if kwargs.get("name") else "tasklist"
        if kwargs.get("kill"):
            cmd = f'taskkill /F /IM {kwargs["name"]}'

        try:
            result = subprocess.run(cmd, shell=True, check=True,
                                    stdout=subprocess.PIPE, text=True)
            return result.stdout or "操作成功"
        except subprocess.CalledProcessError as e:
            return f"操作失败: {e.stderr}"


@Arguments(
    parameters={
        "drive": {
            "type": "string",
            "description": "盘符（如C:）",
            "default": "C:"
        }
    }
)
class DiskUsageAction(Action):
    """磁盘空间分析"""

    def perform(self, *args, **kwargs):
        try:
            total, used, free = shutil.disk_usage(kwargs["drive"])
            return (
                f"磁盘 {kwargs['drive']} 使用情况:\n"
                f"总空间: {total // (1024**3)}GB\n"
                f"已用: {used // (1024**3)}GB\n"
                f"剩余: {free // (1024**3)}GB"
            )
        except Exception as e:
            return f"获取磁盘信息失败: {str(e)}"


@Arguments(
    parameters={
        "path": {
            "type": "string",
            "description": "文件路径",
            "required": True
        },
        "algorithm": {
            "type": "string",
            "description": "哈希算法(md5/sha1/sha256)",
            "default": "sha256"
        }
    }
)
class FileHashAction(Action):
    """计算文件哈希值"""

    def perform(self, *args, **kwargs):
        import hashlib
        try:
            with open(kwargs["path"], "rb") as f:
                hash_obj = getattr(hashlib, kwargs["algorithm"])()
                while chunk := f.read(8192):
                    hash_obj.update(chunk)
            return f"{kwargs['algorithm'].upper()}: {hash_obj.hexdigest()}"
        except Exception as e:
            return f"计算失败: {str(e)}"


