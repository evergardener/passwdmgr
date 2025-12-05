#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:05
# @Updated: 2025/11/27 8:05
# @Python:  3.12
# @Description:
try:
    from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QSpinBox,
                             QCheckBox, QTabWidget, QWidget, QFormLayout,
                             QGroupBox, QTextEdit)  # 添加 QTextEdit 导入
except:
    from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QSpinBox,
                             QCheckBox, QTabWidget, QWidget, QFormLayout,
                             QGroupBox, QTextEdit)

from gui.categories_dialog import CategoriesDialog
from gui.change_master_password_dialog import ChangeMasterPasswordDialog


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """初始化UI"""
        self.setWindowTitle("设置")
        self.setFixedSize(500, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 选项卡
        self.tabs = QTabWidget()

        # 数据库设置
        self.db_tab = QWidget()
        self.setup_database_tab()

        # 安全设置
        self.security_tab = QWidget()
        self.setup_security_tab()

        # 界面设置
        self.ui_tab = QWidget()
        self.setup_ui_tab()

        # 分类设置
        self.categories_tab = QWidget()
        self.setup_categories_tab()

        self.tabs.addTab(self.db_tab, "数据库")
        self.tabs.addTab(self.security_tab, "安全")
        self.tabs.addTab(self.ui_tab, "界面")
        self.tabs.addTab(self.categories_tab, "分类")

        layout.addWidget(self.tabs)

        # 按钮
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.test_button = QPushButton("测试连接")
        self.cancel_button = QPushButton("取消")

        button_layout.addWidget(self.test_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # 信号连接
        self.save_button.clicked.connect(self.on_save)
        self.test_button.clicked.connect(self.on_test_connection)
        self.cancel_button.clicked.connect(self.reject)

    def setup_database_tab(self):
        """设置数据库选项卡"""
        # 使用垂直布局作为主布局
        main_layout = QVBoxLayout(self.db_tab)

        # 数据库类型选择
        type_group = QGroupBox("数据库类型")
        type_layout = QVBoxLayout(type_group)

        self.use_sqlite_check = QCheckBox("使用 SQLite 数据库")
        self.use_sqlite_check.setChecked(True)
        self.use_sqlite_check.toggled.connect(self.on_database_type_changed)
        type_layout.addWidget(self.use_sqlite_check)

        main_layout.addWidget(type_group)

        # SQLite配置
        self.sqlite_group = QGroupBox("SQLite 配置")
        sqlite_layout = QFormLayout(self.sqlite_group)
        self.sqlite_path = QLineEdit()
        sqlite_layout.addRow("数据库文件路径:", self.sqlite_path)
        main_layout.addWidget(self.sqlite_group)

        # MySQL配置
        self.mysql_group = QGroupBox("MySQL 配置")
        mysql_layout = QFormLayout(self.mysql_group)

        self.db_host = QLineEdit()
        self.db_port = QSpinBox()
        self.db_port.setRange(1, 65535)
        self.db_name = QLineEdit()
        self.db_username = QLineEdit()
        self.db_password = QLineEdit()
        self.db_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_ssl = QCheckBox()

        mysql_layout.addRow("主机:", self.db_host)
        mysql_layout.addRow("端口:", self.db_port)
        mysql_layout.addRow("数据库名:", self.db_name)
        mysql_layout.addRow("用户名:", self.db_username)
        mysql_layout.addRow("密码:", self.db_password)
        mysql_layout.addRow("使用SSL:", self.db_ssl)

        main_layout.addWidget(self.mysql_group)

        # 添加弹性空间
        main_layout.addStretch()

        # 初始隐藏MySQL配置
        self.mysql_group.setVisible(False)

    def setup_security_tab(self):
        """设置安全选项卡"""
        layout = QVBoxLayout(self.security_tab)

        # 自动锁定设置
        auto_lock_group = QGroupBox("自动锁定设置")
        auto_lock_layout = QFormLayout(auto_lock_group)

        self.auto_lock_minutes = QSpinBox()
        self.auto_lock_minutes.setRange(1, 120)
        self.auto_lock_minutes.setSuffix(" 分钟")

        self.clear_clipboard_seconds = QSpinBox()
        self.clear_clipboard_seconds.setRange(0, 300)
        self.clear_clipboard_seconds.setSuffix(" 秒")

        auto_lock_layout.addRow("自动锁定时间:", self.auto_lock_minutes)
        auto_lock_layout.addRow("清除剪贴板时间:", self.clear_clipboard_seconds)

        # 说明
        note_label = QLabel("设置为0表示不清除剪贴板")
        note_label.setStyleSheet("color: gray;")
        auto_lock_layout.addRow("", note_label)

        layout.addWidget(auto_lock_group)

        # 修改主密码区域
        password_group = QGroupBox("主密码设置")
        password_layout = QVBoxLayout(password_group)

        password_info = QLabel(
            "修改主密码将重新加密所有密码记录。请确保您记得当前主密码。"
        )
        password_info.setWordWrap(True)
        password_info.setStyleSheet("color: gray; font-size: 12px;")
        password_layout.addWidget(password_info)

        self.change_password_button = QPushButton("修改主密码...")
        password_layout.addWidget(self.change_password_button)

        layout.addWidget(password_group)
        layout.addStretch()

        # 信号连接
        self.change_password_button.clicked.connect(self.on_change_password)

    def setup_ui_tab(self):
        """设置界面选项卡"""
        layout = QFormLayout(self.ui_tab)

        self.window_width = QSpinBox()
        self.window_width.setRange(600, 2000)
        self.window_height = QSpinBox()
        self.window_height.setRange(400, 1500)

        layout.addRow("窗口默认宽度:", self.window_width)
        layout.addRow("窗口默认高度:", self.window_height)

    def setup_categories_tab(self):
        """设置分类选项卡"""
        layout = QVBoxLayout(self.categories_tab)

        # 说明标签
        info_label = QLabel("管理密码分类：")
        layout.addWidget(info_label)

        # 当前分类列表预览
        preview_label = QLabel("当前分类列表：")
        layout.addWidget(preview_label)

        self.categories_preview = QTextEdit()
        self.categories_preview.setReadOnly(True)
        self.categories_preview.setMaximumHeight(150)
        layout.addWidget(self.categories_preview)

        # 管理分类按钮
        self.manage_categories_button = QPushButton("管理分类...")
        layout.addWidget(self.manage_categories_button)

        layout.addStretch()

        # 信号连接
        self.manage_categories_button.clicked.connect(self.on_manage_categories)

    def on_manage_categories(self):
        """打开分类管理对话框"""
        dialog = CategoriesDialog(self.config_manager, self)
        if dialog.exec():
            # 更新预览
            self.update_categories_preview()

    def update_categories_preview(self):
        """更新分类预览"""
        categories = self.config_manager.get_categories_config()
        self.categories_preview.setText("\n".join(categories))

    def load_settings(self):
        """加载当前设置"""
        # 数据库设置
        db_config = self.config_manager.get_database_config()

        # 数据库类型
        self.use_sqlite_check.setChecked(db_config.get('use_sqlite', True))
        self.on_database_type_changed(db_config.get('use_sqlite', True))

        # SQLite 配置
        self.sqlite_path.setText(db_config.get('sqlite_path', 'password_manager.db'))

        # MySQL 配置
        self.db_host.setText(db_config.get('host', 'localhost'))
        self.db_port.setValue(db_config.get('port', 3306))
        self.db_name.setText(db_config.get('database', 'password_manager'))
        self.db_username.setText(db_config.get('username', ''))
        self.db_password.setText(db_config.get('password', ''))
        self.db_ssl.setChecked(db_config.get('use_ssl', False))

        # 安全设置
        security_config = self.config_manager.get_security_config()
        self.auto_lock_minutes.setValue(security_config.get('auto_lock_minutes', 15))
        self.clear_clipboard_seconds.setValue(security_config.get('clear_clipboard_seconds', 30))

        # 界面设置
        ui_config = self.config_manager.get_ui_config()
        self.window_width.setValue(ui_config.get('window_width', 1000))
        self.window_height.setValue(ui_config.get('window_height', 600))

        # 分类设置（新增）
        self.update_categories_preview()

    def on_save(self):
        """保存设置"""
        # 验证数据库设置
        if self.use_sqlite_check.isChecked():
            # SQLite模式，验证文件路径
            if not self.sqlite_path.text().strip():
                QMessageBox.warning(self, "错误", "请填写SQLite数据库文件路径")
                return
        else:
            # MySQL模式，验证必要字段
            if not all([
                self.db_host.text().strip(),
                self.db_name.text().strip(),
                self.db_username.text().strip()
            ]):
                QMessageBox.warning(self, "错误", "请填写完整的MySQL配置")
                return

        # 保存数据库配置
        db_config = {
            'use_sqlite': self.use_sqlite_check.isChecked(),
            'sqlite_path': self.sqlite_path.text().strip(),
            'host': self.db_host.text().strip(),
            'port': self.db_port.value(),
            'database': self.db_name.text().strip(),
            'username': self.db_username.text().strip(),
            'password': self.db_password.text(),
            'use_ssl': self.db_ssl.isChecked()
        }
        self.config_manager.update_database_config(db_config)

        # 保存安全配置
        security_config = {
            'auto_lock_minutes': self.auto_lock_minutes.value(),
            'clear_clipboard_seconds': self.clear_clipboard_seconds.value()
        }
        self.config_manager.update_security_config(security_config)

        # 保存界面配置
        ui_config = {
            'window_width': self.window_width.value(),
            'window_height': self.window_height.value()
        }
        self.config_manager.update_ui_config(ui_config)

        QMessageBox.information(self, "成功", "设置已保存，重启程序后生效")
        self.accept()

    def on_test_connection(self):
        """测试数据库连接"""
        from core.database_manager import DatabaseManager

        # 根据当前选择的数据库类型构建配置
        if self.use_sqlite_check.isChecked():
            db_config = {
                'use_sqlite': True,
                'sqlite_path': self.sqlite_path.text().strip(),
                'host': 'localhost',  # SQLite不需要这些，但保持结构一致
                'port': 3306,
                'database': 'password_manager',
                'username': '',
                'password': '',
                'use_ssl': False
            }
        else:
            db_config = {
                'use_sqlite': False,
                'sqlite_path': '',
                'host': self.db_host.text().strip(),
                'port': self.db_port.value(),
                'database': self.db_name.text().strip(),
                'username': self.db_username.text().strip(),
                'password': self.db_password.text(),
                'use_ssl': self.db_ssl.isChecked()
            }

        db_manager = DatabaseManager()
        if db_manager.test_connection(db_config):
            QMessageBox.information(self, "成功", "数据库连接测试成功")
        else:
            QMessageBox.critical(self, "错误", "数据库连接测试失败")

    def on_change_password(self):
        """打开修改主密码对话框"""
        from core.database_manager import DatabaseManager
        from core.encryption_manager import EncryptionManager
        from core.session_manager import SessionManager

        # 创建必要的管理器实例
        db_manager = DatabaseManager()
        encryption_manager = EncryptionManager()
        session_manager = SessionManager()

        # 连接到数据库（使用当前配置）
        db_config = self.config_manager.get_database_config()
        if not db_manager.connect(db_config):
            QMessageBox.critical(self, "错误", "无法连接数据库")
            return

        # 设置会话管理器（使用当前会话的主密码）
        # 注意：这里需要从父窗口获取当前会话
        parent = self.parent()
        if hasattr(parent, 'session_manager'):
            session_manager = parent.session_manager

        dialog = ChangeMasterPasswordDialog(
            db_manager, encryption_manager, session_manager, self
        )

        if dialog.exec():
            QMessageBox.information(self, "成功", "主密码修改成功")

        # 关闭数据库连接
        db_manager.close()

    def on_database_type_changed(self, checked):
        """数据库类型切换"""
        if checked:  # 使用SQLite
            self.sqlite_group.setVisible(True)
            self.mysql_group.setVisible(False)
        else:  # 使用MySQL
            self.sqlite_group.setVisible(False)
            self.mysql_group.setVisible(True)