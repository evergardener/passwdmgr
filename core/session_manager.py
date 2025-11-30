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
        try:
            self.master_password = master_password
            self.last_activity = time.time()
            self.is_locked = False
            print(f"会话已解锁，主密码长度: {len(master_password)}")
            return True
        except Exception as e:
            print(f"解锁会话失败: {e}")
            self.lock()
            return False

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

    def get_master_password(self) -> str:
        """获取主密码 - 添加调试信息"""
        if self.is_locked:
            print("会话已锁定，无法获取主密码")
            return None

        password = self.master_password
        print(f"获取主密码，长度: {len(password) if password else 0}")
        return password

    def set_auto_lock_minutes(self, minutes: int):
        """设置自动锁定时间"""
        self.auto_lock_minutes = minutes

    def update_master_password(self, new_password: str) -> bool:
        """安全地更新主密码"""
        try:
            # 验证新密码
            if not new_password or len(new_password) < 8:
                print("新密码无效")
                return False

            print(f"正在更新会话管理器的主密码，新密码长度: {len(new_password)}")

            # 更新主密码
            self.master_password = new_password
            self.update_activity()

            print("会话管理器主密码更新成功")
            return True

        except Exception as e:
            print(f"更新主密码失败: {e}")
            return False
