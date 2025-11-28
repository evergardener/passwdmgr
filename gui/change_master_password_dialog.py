#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/28 10:42
# @Updated: 2025/11/28 10:42
# @Python:  3.12
# @Description:
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QFormLayout,
                             QProgressDialog)
from PyQt6.QtCore import Qt, QTimer
import logging

logger = logging.getLogger(__name__)


class ChangeMasterPasswordDialog(QDialog):
    """修改主密码对话框"""

    def __init__(self, database_manager, encryption_manager, session_manager, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.encryption_manager = encryption_manager
        self.session_manager = session_manager
        self.setup_ui()

    def setup_ui(self):
        """初始化UI"""
        self.setWindowTitle("修改主密码")
        self.setFixedSize(400, 300)
        self.setModal(True)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # 当前密码
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("当前主密码:", self.current_password_input)

        # 新密码
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("新主密码:", self.new_password_input)

        # 确认新密码
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("确认新密码:", self.confirm_password_input)

        # 密码强度提示
        self.password_strength_label = QLabel("")
        self.password_strength_label.setStyleSheet("color: gray; font-size: 12px;")
        form_layout.addRow("", self.password_strength_label)

        layout.addLayout(form_layout)

        # 说明文本
        info_label = QLabel(
            "注意：修改主密码需要重新加密所有密码记录，这可能需要一些时间。"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            "color: orange; font-size: 12px; background-color: #FFF3CD; padding: 8px; border: 1px solid #FFEAA7; border-radius: 4px;")
        layout.addWidget(info_label)

        # 按钮
        button_layout = QHBoxLayout()
        self.change_button = QPushButton("修改密码")
        self.cancel_button = QPushButton("取消")

        button_layout.addStretch()
        button_layout.addWidget(self.change_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # 信号连接
        self.current_password_input.textChanged.connect(self.on_password_changed)
        self.new_password_input.textChanged.connect(self.on_password_changed)
        self.confirm_password_input.textChanged.connect(self.on_password_changed)
        self.change_button.clicked.connect(self.on_change_password)
        self.cancel_button.clicked.connect(self.reject)

        # 初始禁用修改按钮
        self.change_button.setEnabled(False)

    def on_password_changed(self):
        """密码输入变化时更新界面"""
        current_password = self.current_password_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        # 检查密码强度
        if new_password:
            strength = self.check_password_strength(new_password)
            self.password_strength_label.setText(f"密码强度: {strength['level']}")

            # 根据强度设置颜色
            if strength['level'] == "弱":
                self.password_strength_label.setStyleSheet("color: red; font-size: 12px;")
            elif strength['level'] == "中等":
                self.password_strength_label.setStyleSheet("color: orange; font-size: 12px;")
            elif strength['level'] == "强":
                self.password_strength_label.setStyleSheet("color: blue; font-size: 12px;")
            else:
                self.password_strength_label.setStyleSheet("color: green; font-size: 12px;")
        else:
            self.password_strength_label.setText("")
            self.password_strength_label.setStyleSheet("color: gray; font-size: 12px;")

        # 启用/禁用修改按钮
        enable_button = (current_password and
                         new_password and
                         confirm_password and
                         new_password == confirm_password and
                         len(new_password) >= 8)

        self.change_button.setEnabled(enable_button)

    def check_password_strength(self, password: str) -> dict:
        """检查密码强度"""
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
        elif score >= 4:
            level = "强"
        elif score >= 3:
            level = "中等"
        else:
            level = "弱"

        return {
            'score': score,
            'level': level,
            'checks': checks
        }

    def on_change_password(self):
        """修改主密码"""
        current_password = self.current_password_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        # 验证输入
        if not current_password:
            QMessageBox.warning(self, "错误", "请输入当前主密码")
            return

        if not new_password:
            QMessageBox.warning(self, "错误", "请输入新主密码")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "错误", "新密码和确认密码不匹配")
            return

        if len(new_password) < 8:
            QMessageBox.warning(self, "错误", "新密码长度至少8位")
            return

        # 验证当前密码
        try:
            # 获取一个密码条目来验证当前密码
            entries = self.database_manager.search_entries(limit=1)
            if entries:
                test_entry = entries[0]
                if not self.encryption_manager.validate_password(
                        test_entry.encrypted_password, current_password
                ):
                    QMessageBox.warning(self, "错误", "当前主密码不正确")
                    return
        except Exception as e:
            logger.error(f"验证当前密码失败: {e}")
            QMessageBox.critical(self, "错误", f"验证当前密码失败: {str(e)}")
            return

        # 确认操作
        reply = QMessageBox.question(
            self, "确认修改",
            "确定要修改主密码吗？这将重新加密所有密码记录，可能需要一些时间。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 显示进度对话框
        progress = QProgressDialog("正在重新加密密码记录...", "取消", 0, 100, self)
        progress.setWindowTitle("修改主密码")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(True)
        progress.show()

        try:
            # 获取所有密码条目
            all_entries = self.database_manager.search_entries()
            total_entries = len(all_entries)

            if total_entries == 0:
                # 没有密码条目，直接更新会话管理器
                self.session_manager.master_password = new_password
                QMessageBox.information(self, "成功", "主密码修改成功")
                self.accept()
                return

            # 重新加密所有密码条目
            success_count = 0
            for i, entry in enumerate(all_entries):
                # 检查是否取消
                if progress.wasCanceled():
                    break

                # 更新进度
                progress.setValue(int((i / total_entries) * 100))

                try:
                    # 用旧密码解密
                    decrypted_password = self.encryption_manager.decrypt(
                        entry.encrypted_password, current_password
                    )

                    # 用新密码加密
                    new_encrypted_password = self.encryption_manager.encrypt(
                        decrypted_password, new_password
                    )

                    # 更新条目
                    entry.encrypted_password = new_encrypted_password
                    if self.database_manager.update_entry(entry):
                        success_count += 1

                except Exception as e:
                    logger.error(f"重新加密条目 {entry.website_name} 失败: {e}")
                    continue

            # 更新会话管理器中的主密码
            self.session_manager.master_password = new_password

            # 显示结果
            progress.setValue(100)
            if success_count == total_entries:
                QMessageBox.information(self, "成功",
                                        f"主密码修改成功！\n已重新加密 {success_count} 个密码记录。")
                self.accept()
            else:
                QMessageBox.warning(self, "部分成功",
                                    f"主密码已修改，但部分记录重新加密失败。\n"
                                    f"成功: {success_count}/{total_entries}")
                self.accept()

        except Exception as e:
            logger.error(f"修改主密码失败: {e}")
            QMessageBox.critical(self, "错误", f"修改主密码失败: {str(e)}")
        finally:
            progress.close()