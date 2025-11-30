#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/28 7:57
# @Updated: 2025/11/28 7:57
# @Python:  3.12
# @Description:
# test_add_dialog.py
import sys

# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from core.database_manager import DatabaseManager
from core.encryption_manager import EncryptionManager
from core.session_manager import SessionManager
from core.password_generator import PasswordGenerator
from gui.add_edit_dialog import AddEditDialog


def test_add_dialog():
    """测试添加对话框"""
    app = QApplication(sys.argv)

    # 创建必要的管理器
    db_manager = DatabaseManager()
    encryption_manager = EncryptionManager()
    session_manager = SessionManager()
    password_generator = PasswordGenerator()

    # 连接到 SQLite 数据库
    db_config = {
        "use_sqlite": True,
        "sqlite_path": "test_password_manager.db"
    }

    if db_manager.connect(db_config):
        print("数据库连接成功")

        # 解锁会话
        session_manager.unlock("test_password")

        # 创建对话框
        dialog = AddEditDialog(
            db_manager, encryption_manager, session_manager, password_generator
        )

        print("显示测试对话框...")
        result = dialog.exec()
        print(f"对话框结果: {result}")

    else:
        print("数据库连接失败")

    app.quit()


if __name__ == "__main__":
    test_add_dialog()