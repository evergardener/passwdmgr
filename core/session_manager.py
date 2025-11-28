#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:04
# @Updated: 2025/11/27 8:04
# @Python:  3.12
# @Description:
import time
from typing import Optional


class SessionManager:
    """会话管理器"""

    def __init__(self):
        self.master_password = None
        self.last_activity = None
        self.auto_lock_minutes = 15
        self.is_locked = True  # 初始状态为锁定

    def unlock(self, master_password: str) -> bool:
        """解锁会话"""
        self.master_password = master_password
        self.last_activity = time.time()
        self.is_locked = False
        return True

    def lock(self):
        """锁定会话"""
        self.master_password = None
        self.last_activity = None
        self.is_locked = True

    def update_activity(self):
        """更新最后活动时间"""
        if not self.is_locked:
            self.last_activity = time.time()

    def check_auto_lock(self) -> bool:
        """检查是否需要自动锁定"""
        if self.is_locked or not self.last_activity:
            return True

        idle_minutes = (time.time() - self.last_activity) / 60
        if idle_minutes >= self.auto_lock_minutes:
            self.lock()
            return True

        return False

    def get_master_password(self) -> Optional[str]:
        """获取主密码"""
        if self.is_locked:
            return None
        return self.master_password

    def set_auto_lock_minutes(self, minutes: int):
        """设置自动锁定时间"""
        self.auto_lock_minutes = minutes