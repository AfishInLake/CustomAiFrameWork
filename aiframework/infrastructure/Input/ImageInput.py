#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/6 16:53
# @Author  : afish
# @File    : ImageInput.py
import requests

from aiframework.infrastructure.Input.InputHandler import InputHandlerBase


class ImageInputHandler(InputHandlerBase):
    def __init__(self, image_path: str, ocr_api_url: str, headers: dict):
        self.image_path = image_path
        self.ocr_api_url = ocr_api_url
        self.headers = headers
        self.result = ""

    def read_input(self) -> dict:
        with open(self.image_path, "rb") as f:
            files = {"image": f}
            response = requests.post(self.ocr_api_url, headers=self.headers, files=files)
        return response.json()

    def process(self) -> str:
        data = self.read_input()
        self.result = " ".join([item["text"] for item in data.get("words_result", [])])
        return self.result
