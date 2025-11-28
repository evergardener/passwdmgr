#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:00
# @Updated: 2025/11/27 8:00
# @Python:  3.12
# @Description:

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re


@dataclass
class PasswordEntry:
    """密码条目数据模型"""
    id: Optional[int] = None
    website_name: str = ""
    url: str = ""
    username: str = ""
    encrypted_password: str = ""
    decrypted_password: str = ""  # 临时字段，不存储到数据库
    notes: str = ""
    category: str = "默认"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'website_name': self.website_name,
            'url': self.url,
            'username': self.username,
            'encrypted_password': self.encrypted_password,
            'notes': self.notes,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PasswordEntry':
        """从字典创建实例"""
        # 处理时间字段转换
        created_at = cls._parse_datetime(data.get('created_at'))
        updated_at = cls._parse_datetime(data.get('updated_at'))

        return cls(
            id=data.get('id'),
            website_name=data.get('website_name', ''),
            url=data.get('url', ''),
            username=data.get('username', ''),
            encrypted_password=data.get('encrypted_password', ''),
            notes=data.get('notes', ''),
            category=data.get('category', '默认'),
            created_at=created_at,
            updated_at=updated_at
        )

    @staticmethod
    def _parse_datetime(dt_str):
        """解析日期时间字符串"""
        if dt_str is None:
            return None

        if isinstance(dt_str, datetime):
            return dt_str

        try:
            # 尝试解析 ISO 格式
            if 'T' in str(dt_str):
                return datetime.fromisoformat(str(dt_str).replace('Z', '+00:00'))
            # 尝试解析 SQLite 的格式
            elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(dt_str)):
                return datetime.strptime(str(dt_str), '%Y-%m-%d %H:%M:%S')
            # 其他格式
            else:
                return datetime.fromisoformat(str(dt_str))
        except (ValueError, TypeError) as e:
            print(f"解析日期时间错误: {e}, 原始值: {dt_str}")
            return None