#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:06
# @Updated: 2025/11/27 8:06
# @Python:  3.12
# @Description:
import os
import hashlib


def create_directory_if_not_exists(path: str):
    """如果目录不存在则创建"""
    if not os.path.exists(path):
        os.makedirs(path)


def calculate_file_hash(file_path: str) -> str:
    """计算文件哈希值"""
    if not os.path.exists(file_path):
        return ""

    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def sanitize_filename(filename: str) -> str:
    """清理文件名中的非法字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename