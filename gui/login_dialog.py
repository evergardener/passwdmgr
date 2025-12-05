#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:05
# @Updated: 2025/11/27 8:05
# @Python:  3.12
# @Description:
# 完整的 gui/login_dialog.py

try:
    from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QWidget)
    from PyQt6.QtCore import Qt
except ImportError:
    from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QWidget)
    from PyQt5.QtCore import Qt
from gui.icon_manager import get_icon_manager
import logging

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    """登录对话框"""

    def __init__(self, session_manager, encryption_manager, database_manager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.encryption_manager = encryption_manager
        self.database_manager = database_manager
        self.icon_manager = get_icon_manager()
        self.is_first_use = False
        self.is_processing = False
        self.setup_ui()
        self.check_first_use()

    def setup_ui(self):
        """初始化UI - 简洁现代版本"""
        self.setWindowTitle("解锁密码管理器")
        self.setFixedSize(800, 600)
        self.setModal(True)

        # 设置窗口样式
        self.setStyleSheet("""
            QDialog {
                background: white;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)

        # 图标和标题
        icon_label = QLabel("🔒")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 64px;
                text-align: center;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("密码管理器")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2d3748;
                text-align: center;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("安全访问您的密码库")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #718096;
                text-align: center;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 密码输入
        password_label = QLabel("主密码")
        password_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #4a5568;
                margin-bottom: 5px;
            }
        """)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("输入主密码...")
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 12px 15px;
                font-size: 14px;
                background: #f7fafc;
            }
            QLineEdit:focus {
                border-color: #4299e1;
                background: white;
            }
        """)
        self.password_input.returnPressed.connect(self.on_login)

        # 首次使用提示
        self.first_use_label = QLabel("首次使用，请设置主密码（至少8位字符）")
        self.first_use_label.setStyleSheet("""
            QLabel {
                color: #ed8936;
                font-size: 12px;
                background: #fef5eb;
                padding: 8px 12px;
                border-radius: 4px;
                border-left: 3px solid #ed8936;
            }
        """)
        self.first_use_label.setVisible(False)
        self.first_use_label.setWordWrap(True)

        # 按钮
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("取消")
        self.login_button = QPushButton("解锁")

        # 按钮样式
        button_style = """
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 80px;
            }
        """

        self.cancel_button.setStyleSheet(button_style + """
            QPushButton {
                background: #edf2f7;
                color: #4a5568;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)

        self.login_button.setStyleSheet(button_style + """
            QPushButton {
                background: #4299e1;
                color: white;
            }
            QPushButton:hover {
                background: #3182ce;
            }
            QPushButton:pressed {
                background: #2b6cb0;
            }
        """)

        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.login_button)

        # 组装布局
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(20)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.first_use_label)
        layout.addStretch()
        layout.addLayout(button_layout)

        # 信号连接
        self.login_button.clicked.connect(self.on_login)
        self.cancel_button.clicked.connect(self.reject)

        # 根据首次使用状态调整界面
        self.adjust_ui_for_first_use()

    def check_first_use(self):
        """检查是否是首次使用"""
        try:
            # 检查验证令牌是否存在
            if hasattr(self.database_manager, 'check_auth_token_exists'):
                token_exists = self.database_manager.check_auth_token_exists()
                self.is_first_use = not token_exists
            else:
                # 如果方法不存在，回退到检查密码条目
                entries = self.database_manager.search_entries(limit=1)
                self.is_first_use = (len(entries) == 0)

            if self.is_first_use:
                self.first_use_label.setVisible(True)
                self.setWindowTitle("设置主密码")
                self.login_button.setText("设置密码")
                print("检测到首次使用")
            else:
                print("检测到已有验证令牌，需要验证主密码")

        except Exception as e:
            print(f"检查首次使用状态错误: {e}")
            # 如果出错，假设是首次使用
            self.is_first_use = True
            self.first_use_label.setVisible(True)
            self.setWindowTitle("设置主密码")
            self.login_button.setText("设置密码")

    def on_login(self):
        """登录/设置密码处理"""

        # 防止重复点击
        if self.is_processing:
            return
        self.is_processing = True

        # 禁用按钮防止重复点击
        self.login_button.setEnabled(False)

        try:
            password = self.password_input.text().strip()
            if self.is_first_use:
                # 首次使用，设置主密码
                self.setup_master_password(password)
            else:
                # 正常登录，验证主密码
                self.verify_master_password(password)
            if not password:
                QMessageBox.warning(self, "错误", "请输入主密码")
                return

            if len(password) < 8:
                QMessageBox.warning(self, "错误", "密码长度至少8位")
                return


        finally:
            # 重新启用按钮
            self.is_processing = False
            self.login_button.setEnabled(True)

    def setup_master_password(self, password: str):
        """设置主密码（首次使用）"""
        try:
            # 创建验证令牌
            if hasattr(self.database_manager, 'create_auth_token'):
                if self.database_manager.create_auth_token(password, self.encryption_manager):
                    # 解锁会话
                    if self.session_manager.unlock(password):
                        QMessageBox.information(self, "成功", "主密码设置成功！")
                        print("首次使用主密码设置成功")
                        self.accept()
                    else:
                        QMessageBox.critical(self, "错误", "设置主密码失败")
                        print("首次使用主密码设置失败")
                else:
                    QMessageBox.critical(self, "错误", "创建验证令牌失败")
            else:
                # 如果方法不存在，使用简单方式
                if self.session_manager.unlock(password):
                    QMessageBox.information(self, "成功", "主密码设置成功！")
                    self.accept()
                else:
                    QMessageBox.critical(self, "错误", "设置主密码失败")

        except Exception as e:
            logger.error(f"设置主密码失败: {e}")
            print(f"设置主密码失败: {e}")
            QMessageBox.critical(self, "错误", f"设置主密码失败: {str(e)}")

    def verify_master_password(self, password: str):
        """验证主密码"""
        try:
            # 使用完整的验证方法
            if hasattr(self.database_manager, 'validate_master_password'):
                if self.database_manager.validate_master_password(password, self.encryption_manager):
                    # 解锁会话
                    if self.session_manager.unlock(password):
                        print("主密码验证成功，解锁成功")
                        self.accept()
                        return
                    else:
                        print("解锁失败")
                        QMessageBox.critical(self, "错误", "解锁失败，请重试")
                        return
                else:
                    print("主密码不正确")
                    QMessageBox.warning(self, "错误", "主密码不正确")
            else:
                # 如果完整验证方法不存在，回退到简单验证
                print("使用备用验证方法")
                entries = self.database_manager.search_entries(limit=1)
                if entries:
                    try:
                        test_entry = entries[0]
                        decrypted_password = self.encryption_manager.decrypt(
                            test_entry.encrypted_password, password
                        )
                        if self.session_manager.unlock(password):
                            self.accept()
                            return
                        else:
                            QMessageBox.critical(self, "错误", "解锁失败")
                            return
                    except Exception as e:
                        logger.error(f"验证密码失败: {e}")
                        QMessageBox.warning(self, "错误", "主密码不正确")
                else:
                    # 如果没有条目，接受任何密码
                    if self.session_manager.unlock(password):
                        self.accept()
                        return
                    else:
                        QMessageBox.critical(self, "错误", "解锁失败")
                        return

        except Exception as e:
            logger.error(f"验证主密码失败: {e}")
            print(f"验证主密码失败: {e}")
            QMessageBox.critical(self, "错误", f"验证密码失败: {str(e)}")

    def on_password_changed(self):
        """密码输入变化时的动画效果"""
        if self.password_input.text():
            # 输入时有内容，可以添加一些视觉反馈
            pass

    def adjust_ui_for_first_use(self):
        """根据首次使用状态调整UI - 增强版本"""
        if self.is_first_use:
            self.first_use_label.setVisible(True)
            self.setWindowTitle("设置主密码")
            self.login_button.setText("设置密码")

            # 首次使用时可以添加欢迎动画
            self.show_welcome_animation()
        else:
            self.first_use_label.setVisible(False)

    def show_welcome_animation(self):
        """显示欢迎动画（简单实现）"""
        # 可以在这里添加一些简单的动画效果
        original_style = self.first_use_label.styleSheet()
        self.first_use_label.setStyleSheet(original_style + """
            QLabel {
                animation: pulse 2s infinite;
            }
        """)