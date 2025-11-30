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
        # 信号连接 - 使用lambda包装器防止异常传播
        self.current_password_input.textChanged.connect(
            lambda: self.safe_on_password_changed()
        )
        self.new_password_input.textChanged.connect(
            lambda: self.safe_on_password_changed()
        )
        self.confirm_password_input.textChanged.connect(
            lambda: self.safe_on_password_changed()
        )
        self.change_button.clicked.connect(self.on_change_password)
        self.cancel_button.clicked.connect(self.reject)

        # 初始禁用修改按钮
        self.change_button.setEnabled(False)

    def safe_on_password_changed(self):
        """安全的密码变化处理，防止异常崩溃"""
        try:
            self.on_password_changed()
        except Exception as e:
            print(f"密码变化处理异常: {e}")
            # 出错时禁用按钮
            try:
                self.change_button.setEnabled(False)
            except:
                pass


    def on_password_changed(self):
        """密码输入变化时更新界面"""
        try:
            # 获取输入值
            current_password = self.current_password_input.text().strip()
            new_password = self.new_password_input.text().strip()
            confirm_password = self.confirm_password_input.text().strip()

            # 检查密码强度
            if new_password:
                try:
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
                except Exception as e:
                    print(f"检查密码强度错误: {e}")
                    self.password_strength_label.setText("")
                    self.password_strength_label.setStyleSheet("color: gray; font-size: 12px;")
            else:
                self.password_strength_label.setText("")
                self.password_strength_label.setStyleSheet("color: gray; font-size: 12px;")

            # 启用/禁用修改按钮 - 明确转换为布尔值
            has_current_password = bool(current_password)
            has_new_password = bool(new_password)
            has_confirm_password = bool(confirm_password)
            passwords_match = (new_password == confirm_password)
            password_length_ok = (len(new_password) >= 8)

            # 所有条件都必须满足
            enable_button = (has_current_password and
                             has_new_password and
                             has_confirm_password and
                             passwords_match and
                             password_length_ok)

            # 确保是布尔值
            enable_button = bool(enable_button)

            # 设置按钮状态
            self.change_button.setEnabled(enable_button)

        except Exception as e:
            print(f"密码输入变化处理错误: {e}")
            import traceback
            traceback.print_exc()
            # 出错时安全地禁用按钮
            try:
                self.change_button.setEnabled(False)
            except:
                pass  # 如果设置按钮状态也失败，忽略错误



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
        """修改主密码 - 修复版本"""
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
            else:
                # 如果没有条目，直接创建验证令牌
                print("没有密码条目，直接创建验证令牌")
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
                        print(f"成功重新加密条目: {entry.website_name}")

                except Exception as e:
                    logger.error(f"重新加密条目 {entry.website_name} 失败: {e}")
                    print(f"重新加密条目失败: {e}")
                    continue

            # 关键修复：更新验证令牌和会话管理器
            print("开始更新验证令牌和会话管理器...")

            # 1. 首先更新数据库中的验证令牌
            if hasattr(self.database_manager, 'create_auth_token'):
                token_success = self.database_manager.create_auth_token(new_password, self.encryption_manager)
                print(f"验证令牌更新: {'成功' if token_success else '失败'}")
            else:
                print("数据库管理器没有 create_auth_token 方法")
                token_success = False

            # 2. 更新会话管理器的主密码
            if hasattr(self.session_manager, 'update_master_password'):
                session_success = self.session_manager.update_master_password(new_password)
            else:
                # 回退方法
                print("使用回退方法更新会话管理器")
                self.session_manager.master_password = new_password
                self.session_manager.is_locked = False
                self.session_manager.update_activity()
                session_success = True

            print(f"会话管理器更新: {'成功' if session_success else '失败'}")

            # 3. 立即验证新密码是否有效
            verification_success = False
            if success_count > 0 and session_success:
                try:
                    # 获取一个条目验证新密码
                    test_entries = self.database_manager.search_entries(limit=1)
                    if test_entries:
                        test_entry = test_entries[0]
                        # 使用新密码解密验证
                        decrypted = self.encryption_manager.decrypt(
                            test_entry.encrypted_password, new_password
                        )
                        verification_success = bool(decrypted)
                        print(f"新密码验证: {'成功' if verification_success else '失败'}")
                except Exception as e:
                    print(f"新密码验证失败: {e}")
                    verification_success = False

            # 显示结果
            progress.setValue(100)

            if success_count == total_entries and session_success and verification_success:
                QMessageBox.information(self, "成功",
                                        f"主密码修改成功！\n"
                                        f"已重新加密 {success_count} 个密码记录。\n"
                                        "现在请使用新密码进行解锁和操作。")
                self.accept()
            elif success_count > 0 and session_success:
                QMessageBox.warning(self, "部分成功",
                                    f"主密码已修改，但部分记录重新加密失败。\n"
                                    f"成功: {success_count}/{total_entries}\n"
                                    "请使用新密码进行后续操作。")
                self.accept()
            else:
                QMessageBox.critical(self, "错误",
                                     f"主密码修改失败！\n"
                                     f"重新加密: {success_count}/{total_entries}\n"
                                     f"会话更新: {'成功' if session_success else '失败'}\n"
                                     f"密码验证: {'成功' if verification_success else '失败'}\n"
                                     "请重新登录并重试。")
                # 强制重新登录
                if hasattr(self, 'parent') and hasattr(self.parent(), 'lock_application'):
                    QTimer.singleShot(0, self.parent().lock_application)

        except Exception as e:
            logger.error(f"修改主密码失败: {e}")
            print(f"修改主密码失败: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"修改主密码失败: {str(e)}")
        finally:
            progress.close()