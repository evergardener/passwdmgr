#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:05
# @Updated: 2025/11/27 8:05
# @Python:  3.12
# @Description:
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt


class LoginDialog(QDialog):
    """登录对话框"""

    def __init__(self, session_manager, encryption_manager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.encryption_manager = encryption_manager
        self.setup_ui()

    def setup_ui(self):
        """初始化UI"""
        self.setWindowTitle("解锁密码管理器")  # 明确表示这是解锁操作
        self.setFixedSize(300, 150)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 密码输入
        password_layout = QVBoxLayout()
        password_label = QLabel("主密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.on_login)

        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        # 按钮
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("解锁")
        self.cancel_button = QPushButton("取消")

        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(password_layout)
        layout.addLayout(button_layout)

        # 信号连接
        self.login_button.clicked.connect(self.on_login)
        self.cancel_button.clicked.connect(self.reject)

    def on_login(self):
        """登录处理"""
        password = self.password_input.text().strip()

        if not password:
            QMessageBox.warning(self, "错误", "请输入主密码")
            return

        # 这里应该验证主密码
        # 由于我们没有存储加密的主密码，这里简单验证非空
        # 在实际应用中，应该使用更安全的验证方式

        if len(password) < 8:
            QMessageBox.warning(self, "错误", "密码长度至少8位")
            return

        # 解锁会话
        if self.session_manager.unlock(password):
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "解锁失败")