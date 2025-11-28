#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:04
# @Updated: 2025/11/27 8:04
# @Python:  3.12
# @Description:
import random
import string
import secrets
from typing import List


class PasswordGenerator:
    """密码生成器"""

    def __init__(self):
        self.character_sets = {
            'lowercase': string.ascii_lowercase,
            'uppercase': string.ascii_uppercase,
            'digits': string.digits,
            'symbols': '!@#$%^&*()_+-=[]{}|;:,.<>?'
        }

    def generate_password(self, length: int = 16,
                          use_uppercase: bool = True,
                          use_digits: bool = True,
                          use_symbols: bool = True) -> str:
        """生成安全密码"""
        characters = self.character_sets['lowercase']

        if use_uppercase:
            characters += self.character_sets['uppercase']
        if use_digits:
            characters += self.character_sets['digits']
        if use_symbols:
            characters += self.character_sets['symbols']

        # 确保每种类型的字符至少有一个
        password_chars = []
        if use_uppercase:
            password_chars.append(secrets.choice(self.character_sets['uppercase']))
        if use_digits:
            password_chars.append(secrets.choice(self.character_sets['digits']))
        if use_symbols:
            password_chars.append(secrets.choice(self.character_sets['symbols']))

        # 填充剩余长度
        remaining_length = length - len(password_chars)
        if remaining_length > 0:
            password_chars.extend(secrets.choice(characters) for _ in range(remaining_length))

        # 随机打乱
        secrets.SystemRandom().shuffle(password_chars)

        return ''.join(password_chars)

    def check_password_strength(self, password: str) -> dict:
        """检查密码强度"""
        strength = {
            'length': len(password) >= 8,
            'uppercase': any(c.isupper() for c in password),
            'lowercase': any(c.islower() for c in password),
            'digit': any(c.isdigit() for c in password),
            'symbol': any(not c.isalnum() for c in password)
        }

        score = sum(strength.values())
        if score == 5:
            level = "非常强"
        elif score == 4:
            level = "强"
        elif score == 3:
            level = "中等"
        else:
            level = "弱"

        return {
            'score': score,
            'level': level,
            'details': strength
        }