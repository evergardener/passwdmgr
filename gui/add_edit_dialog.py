#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:05
# @Updated: 2025/11/27 8:05
# @Python:  3.12
# @Description:
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QTextEdit,
                             QComboBox, QCheckBox, QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt

from ..models.password_entry import PasswordEntry


class AddEditDialog(QDialog):
    """添加/编辑对话框"""

    def __init__(self, database_manager, encryption_manager, session_manager,
                 password_generator, config_manager=None, parent=None, entry=None):
        super().__init__(parent)
        self.database_manager = database_manager
        self.encryption_manager = encryption_manager
        self.session_manager = session_manager
        self.password_generator = password_generator
        self.config_manager = config_manager
        self.entry = entry
        self.is_edit = entry is not None

        # 初始化成员变量
        self.website_input = None
        self.url_input = None
        self.username_input = None
        self.password_input = None
        self.show_password_check = None
        self.generate_password_button = None
        self.category_combo = None
        self.notes_text = None
        self.save_button = None
        self.cancel_button = None

        self.setup_ui()
        self.load_categories()

        if self.is_edit:
            self.load_entry_data()

        print("AddEditDialog 初始化完成")

    def setup_ui(self):
        """初始化UI"""
        title = "编辑记录" if self.is_edit else "添加新记录"
        self.setWindowTitle(title)
        self.setFixedSize(500, 600)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QVBoxLayout(basic_group)

        form_layout = QVBoxLayout()

        # 网站名称
        website_layout = QHBoxLayout()
        website_layout.addWidget(QLabel("网站名称:"))
        self.website_input = QLineEdit()
        website_layout.addWidget(self.website_input)

        # URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        url_layout.addWidget(self.url_input)

        # 用户名
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("用户名:"))
        self.username_input = QLineEdit()
        username_layout.addWidget(self.username_input)

        # 密码
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密码:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_password_check = QCheckBox("显示")
        self.generate_password_button = QPushButton("生成")

        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.show_password_check)
        password_layout.addWidget(self.generate_password_button)

        # 分类
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("分类:"))
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        category_layout.addWidget(self.category_combo)

        form_layout.addLayout(website_layout)
        form_layout.addLayout(url_layout)
        form_layout.addLayout(username_layout)
        form_layout.addLayout(password_layout)
        form_layout.addLayout(category_layout)

        basic_layout.addLayout(form_layout)

        # 密码生成组
        generate_group = QGroupBox("密码生成器")
        generate_layout = QVBoxLayout(generate_group)

        # 密码长度
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("长度:"))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 64)
        self.length_spin.setValue(16)
        length_layout.addWidget(self.length_spin)

        # 字符类型
        self.uppercase_check = QCheckBox("大写字母")
        self.uppercase_check.setChecked(True)
        self.digits_check = QCheckBox("数字")
        self.digits_check.setChecked(True)
        self.symbols_check = QCheckBox("符号")
        self.symbols_check.setChecked(True)

        type_layout = QHBoxLayout()
        type_layout.addWidget(self.uppercase_check)
        type_layout.addWidget(self.digits_check)
        type_layout.addWidget(self.symbols_check)

        generate_layout.addLayout(length_layout)
        generate_layout.addLayout(type_layout)

        # 备注
        notes_group = QGroupBox("备注")
        notes_layout = QVBoxLayout(notes_group)
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(100)
        notes_layout.addWidget(self.notes_text)

        # 按钮
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.cancel_button = QPushButton("取消")

        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        # 添加到主布局
        layout.addWidget(basic_group)
        layout.addWidget(generate_group)
        layout.addWidget(notes_group)
        layout.addLayout(button_layout)

        # 信号连接
        self.show_password_check.toggled.connect(self.on_show_password)
        self.generate_password_button.clicked.connect(self.on_generate_password)
        self.save_button.clicked.connect(self.on_save)
        self.cancel_button.clicked.connect(self.reject)

    def load_categories(self):
        """加载分类列表"""
        try:
            # 获取分类列表（结合配置和数据库）
            if self.config_manager and hasattr(self.database_manager, 'get_categories'):
                # 使用新的 get_categories 方法，传递 config_manager
                categories = self.database_manager.get_categories(self.config_manager)
            elif hasattr(self.database_manager, 'get_categories'):
                categories = self.database_manager.get_categories()
            else:
                # 使用默认分类
                categories = ["默认", "工作", "个人", "金融", "社交"]
                print("使用默认分类列表")

            # 清空并添加分类
            self.category_combo.clear()
            self.category_combo.addItems(categories)

            # 确保有"默认"分类
            if "默认" not in categories:
                self.category_combo.addItem("默认")

            self.category_combo.setCurrentText("默认")

        except Exception as e:
            print(f"加载分类错误: {e}")
            # 使用默认分类
            self.category_combo.clear()
            default_categories = ["默认", "工作", "个人", "金融", "社交"]
            self.category_combo.addItems(default_categories)
            self.category_combo.setCurrentText("默认")

    def load_entry_data(self):
        """加载条目数据到编辑表单"""
        if not self.entry:
            return

        try:
            # 设置基本字段
            self.website_input.setText(self.entry.website_name)
            self.url_input.setText(self.entry.url)
            self.username_input.setText(self.entry.username)

            # 设置分类
            category_text = self.entry.category if self.entry.category else "默认"
            index = self.category_combo.findText(category_text)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                # 如果分类不在列表中，添加到组合框并选中
                self.category_combo.addItem(category_text)
                self.category_combo.setCurrentText(category_text)

            # 设置备注
            self.notes_text.setPlainText(self.entry.notes if self.entry.notes else "")

            # 解密并设置密码
            if not self.session_manager.is_locked:
                try:
                    master_password = self.session_manager.get_master_password()
                    if master_password and self.entry.encrypted_password:
                        decrypted_password = self.encryption_manager.decrypt(
                            self.entry.encrypted_password, master_password
                        )
                        self.password_input.setText(decrypted_password)
                    else:
                        print("无法获取主密码或加密密码为空")
                except Exception as e:
                    print(f"解密密码错误: {e}")
                    QMessageBox.warning(self, "警告", "无法解密密码，请检查主密码是否正确")
            else:
                print("会话已锁定，无法解密密码")

        except Exception as e:
            print(f"加载条目数据错误: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"加载条目数据失败: {str(e)}")

    def on_show_password(self, checked):
        """显示/隐藏密码"""
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def on_generate_password(self):
        """生成密码"""
        length = self.length_spin.value()
        use_uppercase = self.uppercase_check.isChecked()
        use_digits = self.digits_check.isChecked()
        use_symbols = self.symbols_check.isChecked()

        password = self.password_generator.generate_password(
            length, use_uppercase, use_digits, use_symbols
        )

        self.password_input.setText(password)
        self.show_password_check.setChecked(True)

        # 检查密码强度
        strength = self.password_generator.check_password_strength(password)
        QMessageBox.information(self, "密码生成",
                                f"新密码已生成!\n\n强度: {strength['level']}")

    def on_save(self):
        """保存记录"""
        # 验证输入
        if not all([
            self.website_input.text().strip(),
            self.username_input.text().strip(),
            self.password_input.text().strip()
        ]):
            QMessageBox.warning(self, "错误", "请填写网站名称、用户名和密码")
            return

        # 加密密码
        try:
            master_password = self.session_manager.get_master_password()
            if not master_password:
                QMessageBox.critical(self, "错误", "无法获取主密码，请重新登录")
                return

            print(f"开始加密密码，密码长度: {len(self.password_input.text())}")

            encrypted_password = self.encryption_manager.encrypt(
                self.password_input.text(), master_password
            )

            print(f"密码加密成功，加密后长度: {len(encrypted_password)}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加密密码失败: {e}")
            print(f"加密密码详细错误: {e}")
            import traceback
            traceback.print_exc()
            return

        # 创建或更新条目
        if self.is_edit:
            self.entry.website_name = self.website_input.text().strip()
            self.entry.url = self.url_input.text().strip()
            self.entry.username = self.username_input.text().strip()
            self.entry.encrypted_password = encrypted_password
            self.entry.notes = self.notes_text.toPlainText().strip()
            self.entry.category = self.category_combo.currentText().strip()

            success = self.database_manager.update_entry(self.entry)
        else:
            new_entry = PasswordEntry(
                website_name=self.website_input.text().strip(),
                url=self.url_input.text().strip(),
                username=self.username_input.text().strip(),
                encrypted_password=encrypted_password,
                notes=self.notes_text.toPlainText().strip(),
                category=self.category_combo.currentText().strip()
            )
            success = self.database_manager.add_entry(new_entry)

        if success:
            print("记录保存成功")
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "保存记录失败")