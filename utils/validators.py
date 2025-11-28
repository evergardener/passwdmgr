#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:06
# @Updated: 2025/11/27 8:06
# @Python:  3.12
# @Description:
import re


def validate_url(url: str) -> bool:
    """验证URL格式"""
    if not url:
        return True

    pattern = re.compile(
        r'^(https?://)?'  # http:// or https://
        r'(([A-Z0-9]([A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(pattern, url) is not None


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password_strength(password: str) -> dict:
    """验证密码强度"""
    checks = {
        'length': len(password) >= 8,
        'lowercase': any(c.islower() for c in password),
        'uppercase': any(c.isupper() for c in password),
        'digit': any(c.isdigit() for c in password),
        'symbol': any(not c.isalnum() for c in password)
    }

    score = sum(checks.values())
    if score == 5:
        level = "非常强"
    elif score >= 3:
        level = "强"
    elif score >= 2:
        level = "中等"
    else:
        level = "弱"

    return {
        'score': score,
        'level': level,
        'checks': checks
    }