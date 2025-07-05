#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 9:46
# @Author  : afish
# @File    : setup.py
from setuptools import setup, find_packages

# 读取 README.md 作为 long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='ai-aiframework',
    version='0.1.0',
    author='afish',
    author_email='afish@example.com',
    description='A cross-platform AI assistant aiframework module with speech recognition, task management, and system control.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitee.com/yourusername/dog',  # 替换为你的仓库地址
    packages=find_packages(where='.', include=['aiframework*']),
    package_dir={'': '.'},
    include_package_data=True,
    install_requires=[
        'openai>=1.0.0',
        'speechrecognition>=3.10.0',
        'pyttsx3>=2.90',
        'pyaudio>=0.2.13',
        'dashscope>=1.22.2',
        'python-dotenv>=0.9.9',
        'pika>=1.3.2'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Mulan Permissive Software License, Version 2',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'ai-run=aiframework.main:MainController.start',
        ],
    },
)
