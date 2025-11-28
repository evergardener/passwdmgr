#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:04
# @Updated: 2025/11/27 8:04
# @Python:  3.12
# @Description:
import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QTextEdit, QStatusBar,
                             QToolBar, QMessageBox, QSplitter, QLabel, QApplication, QDialog)  # 添加 QApplication 和 QDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

from core.database_manager import DatabaseManager
from core.encryption_manager import EncryptionManager
from core.config_manager import ConfigManager
from core.session_manager import SessionManager
from core.password_generator import PasswordGenerator
from gui.login_dialog import LoginDialog
from gui.settings_dialog import SettingsDialog
from gui.add_edit_dialog import AddEditDialog

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self, config_manager: ConfigManager, session_manager: SessionManager):
        super().__init__()
        self.config_manager = config_manager
        self.session_manager = session_manager
        self.database_manager = DatabaseManager()
        self.encryption_manager = EncryptionManager()
        self.password_generator = PasswordGenerator()

        # 当前选中的条目
        self.current_entry = None

        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_signals()

        # 自动锁定定时器
        self.auto_lock_timer = QTimer()
        self.auto_lock_timer.timeout.connect(self.check_auto_lock)
        self.auto_lock_timer.start(30000)  # 每30秒检查一次

        # 尝试连接数据库
        self.connect_to_database()

    def setup_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("密码管理器")

        # 设置窗口大小
        ui_config = self.config_manager.get_ui_config()
        self.resize(ui_config.get('window_width', 1000),
                    ui_config.get('window_height', 600))

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        layout = QVBoxLayout(central_widget)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索网站名、URL、备注或分类...")
        self.search_button = QPushButton("搜索")
        self.clear_search_button = QPushButton("清除")

        search_layout.addWidget(QLabel("搜索:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_search_button)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：密码列表
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(4)
        self.entries_table.setHorizontalHeaderLabels(["网站名称", "用户名", "分类", "更新时间"])
        self.entries_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.entries_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.entries_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # 右侧：详情面板
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)

        # 操作按钮
        button_layout = QHBoxLayout()
        self.copy_username_button = QPushButton("复制用户名")
        self.copy_password_button = QPushButton("复制密码")
        self.show_password_button = QPushButton("显示密码")

        button_layout.addWidget(self.copy_username_button)
        button_layout.addWidget(self.copy_password_button)
        button_layout.addWidget(self.show_password_button)

        details_layout.addWidget(QLabel("详情:"))
        details_layout.addWidget(self.details_text)
        details_layout.addLayout(button_layout)

        splitter.addWidget(self.entries_table)
        splitter.addWidget(details_widget)
        splitter.setSizes([400, 300])

        # 添加到主布局
        layout.addLayout(search_layout)
        layout.addWidget(splitter)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        self.sync_action = QAction("同步", self)
        self.lock_action = QAction("解锁", self)
        self.exit_action = QAction("退出", self)

        file_menu.addAction(self.sync_action)
        file_menu.addAction(self.lock_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")

        self.add_action = QAction("添加", self)
        self.edit_action = QAction("编辑", self)
        self.delete_action = QAction("删除", self)

        edit_menu.addAction(self.add_action)
        edit_menu.addAction(self.edit_action)
        edit_menu.addAction(self.delete_action)

        # 工具菜单
        tools_menu = menubar.addMenu("工具")

        self.generate_password_action = QAction("生成密码", self)
        self.settings_action = QAction("设置", self)

        tools_menu.addAction(self.generate_password_action)
        tools_menu.addAction(self.settings_action)

    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)

        toolbar.addAction(self.add_action)
        toolbar.addAction(self.edit_action)
        toolbar.addAction(self.delete_action)
        toolbar.addSeparator()
        toolbar.addAction(self.sync_action)
        toolbar.addAction(self.lock_action)

    def setup_signals(self):
        """设置信号连接"""
        # 搜索相关
        self.search_button.clicked.connect(self.on_search)
        self.clear_search_button.clicked.connect(self.on_clear_search)
        self.search_input.returnPressed.connect(self.on_search)

        # 表格选择
        self.entries_table.itemSelectionChanged.connect(self.on_selection_changed)

        # 按钮操作
        self.copy_username_button.clicked.connect(self.on_copy_username)
        self.copy_password_button.clicked.connect(self.on_copy_password)
        self.show_password_button.clicked.connect(self.on_show_password)

        # 菜单操作
        self.add_action.triggered.connect(self.on_add_entry)
        self.edit_action.triggered.connect(self.on_edit_entry)
        self.delete_action.triggered.connect(self.on_delete_entry)
        self.sync_action.triggered.connect(self.on_sync)
        self.lock_action.triggered.connect(self.on_lock)
        self.exit_action.triggered.connect(self.close)
        self.generate_password_action.triggered.connect(self.on_generate_password)
        self.settings_action.triggered.connect(self.on_settings)

    def connect_to_database(self):
        """连接到数据库"""
        db_config = self.config_manager.get_database_config()
        if db_config.get('username') and db_config.get('password'):
            if self.database_manager.connect(db_config):
                self.status_bar.showMessage("数据库连接成功")
                self.load_entries()
            else:
                self.show_database_settings()
        else:
            self.show_database_settings()

    def show_database_settings(self):
        """显示数据库设置对话框"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            # 重新连接数据库
            self.connect_to_database()

    def check_auto_lock(self):
        """检查自动锁定"""
        if self.session_manager.check_auto_lock():
            self.lock_application()

    def lock_application(self):
        """锁定应用程序"""
        self.session_manager.lock()
        self.show_login_dialog()

    def show_login_dialog(self):
        """显示登录对话框"""
        dialog = LoginDialog(self.session_manager, self.encryption_manager, self)
        if dialog.exec():
            self.status_bar.showMessage("已解锁")
            self.load_entries()
        else:
            self.close()

    def load_entries(self, keyword: str = ""):
        """加载密码条目"""
        if self.session_manager.is_locked:
            return

        try:
            entries = self.database_manager.search_entries(keyword)
            self.populate_table(entries)
            self.status_bar.showMessage(f"加载了 {len(entries)} 条记录")
        except Exception as e:
            logger.error(f"加载条目错误: {e}")
            self.status_bar.showMessage("加载记录失败")

    def populate_table(self, entries: list):
        """填充表格数据"""
        self.entries_table.setRowCount(len(entries))

        for row, entry in enumerate(entries):
            self.entries_table.setItem(row, 0, QTableWidgetItem(entry.website_name))
            self.entries_table.setItem(row, 1, QTableWidgetItem(entry.username))
            self.entries_table.setItem(row, 2, QTableWidgetItem(entry.category))

            updated_at = entry.updated_at.strftime("%Y-%m-%d %H:%M") if entry.updated_at else ""
            self.entries_table.setItem(row, 3, QTableWidgetItem(updated_at))

            # 存储条目ID
            self.entries_table.setItem(row, 0, QTableWidgetItem(entry.website_name))
            self.entries_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, entry.id)

    def on_selection_changed(self):
        """选中项改变"""
        selected_items = self.entries_table.selectedItems()
        if not selected_items:
            self.current_entry = None
            self.details_text.clear()
            return

        row = selected_items[0].row()
        entry_id = self.entries_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

        # 查找条目详情
        entries = self.database_manager.search_entries()
        for entry in entries:
            if entry.id == entry_id:
                self.current_entry = entry
                self.update_details_display()
                break

    def update_details_display(self):
        """更新详情显示"""
        if not self.current_entry:
            return

        details = f"""
网站名称: {self.current_entry.website_name}
URL: {self.current_entry.url}
用户名: {self.current_entry.username}
分类: {self.current_entry.category}
创建时间: {self.current_entry.created_at.strftime('%Y-%m-%d %H:%M') if self.current_entry.created_at else ''}
更新时间: {self.current_entry.updated_at.strftime('%Y-%m-%d %H:%M') if self.current_entry.updated_at else ''}

备注:
{self.current_entry.notes}
        """
        self.details_text.setText(details)

    def on_search(self):
        """搜索处理"""
        keyword = self.search_input.text().strip()
        self.load_entries(keyword)

    def on_clear_search(self):
        """清除搜索"""
        self.search_input.clear()
        self.load_entries()

    def on_add_entry(self):
        """添加新条目"""
        try:
            print("开始添加新条目...")

            if self.session_manager.is_locked:
                QMessageBox.warning(self, "警告", "请先解锁应用程序")
                return

            print("创建 AddEditDialog...")
            # 使用局部变量，避免成员变量冲突
            dialog = AddEditDialog(
                database_manager=self.database_manager,
                encryption_manager=self.encryption_manager,
                session_manager=self.session_manager,
                password_generator=self.password_generator,
                parent=self
            )

            print("显示对话框...")
            # 使用 QTimer 单次定时器来延迟对话框显示，避免栈问题
            QTimer.singleShot(0, lambda: self.safe_show_dialog(dialog))

        except Exception as e:
            print(f"添加条目时出错: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"打开添加对话框失败: {e}")

    def on_edit_entry(self):
        """编辑选中条目"""
        if self.session_manager.is_locked:
            QMessageBox.warning(self, "警告", "请先解锁应用程序")
            return

        if not self.current_entry:
            QMessageBox.warning(self, "警告", "请先选择一个记录")
            return

        dialog = AddEditDialog(self.database_manager, self.encryption_manager,
                               self.session_manager, self.password_generator, self,
                               self.current_entry)
        if dialog.exec():
            self.load_entries()
            self.status_bar.showMessage("成功更新记录")

    def on_delete_entry(self):
        """删除选中条目"""
        if self.session_manager.is_locked:
            QMessageBox.warning(self, "警告", "请先解锁应用程序")
            return

        if not self.current_entry:
            QMessageBox.warning(self, "警告", "请先选择一个记录")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 '{self.current_entry.website_name}' 的记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.database_manager.delete_entry(self.current_entry.id):
                self.load_entries()
                self.status_bar.showMessage("成功删除记录")
            else:
                QMessageBox.critical(self, "错误", "删除记录失败")

    def on_copy_username(self):
        """复制用户名"""
        try:
            if not self.current_entry:
                QMessageBox.warning(self, "警告", "请先选择一个记录")
                return

            # 获取剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_entry.username)
            self.status_bar.showMessage("用户名已复制到剪贴板")

        except Exception as e:
            logger.error(f"复制用户名错误: {e}")
            print(f"复制用户名详细错误: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"复制用户名失败: {str(e)}")

    def on_copy_password(self):
        """复制密码"""
        if not self.current_entry:
            QMessageBox.warning(self, "警告", "请先选择一个记录")
            return

        if self.session_manager.is_locked:
            QMessageBox.warning(self, "警告", "请先解锁应用程序")
            return

        try:
            master_password = self.session_manager.get_master_password()
            if not master_password:
                QMessageBox.warning(self, "警告", "无法获取主密码，请重新登录")
                return

            print(f"尝试解密密码，加密数据长度: {len(self.current_entry.encrypted_password)}")

            # 解密密码
            decrypted_password = self.encryption_manager.decrypt(
                self.current_entry.encrypted_password, master_password
            )

            # 复制到剪贴板
            clipboard = QApplication.clipboard()
            clipboard.setText(decrypted_password)
            self.status_bar.showMessage("密码已复制到剪贴板")

            # 设置定时清除剪贴板
            security_config = self.config_manager.get_security_config()
            clear_seconds = security_config.get('clear_clipboard_seconds', 30)
            if clear_seconds > 0:
                QTimer.singleShot(clear_seconds * 1000, self.clear_clipboard)

        except Exception as e:
            logger.error(f"复制密码错误: {e}")
            print(f"复制密码详细错误: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"解密密码失败: {str(e)}")

    def clear_clipboard(self):
        """清除剪贴板"""
        try:
            clipboard = QApplication.clipboard()
            clipboard.clear()
            self.status_bar.showMessage("剪贴板已清除")
        except Exception as e:
            logger.error(f"清除剪贴板错误: {e}")
            print(f"清除剪贴板错误: {e}")

    def on_show_password(self):
        """显示密码"""
        if not self.current_entry:
            QMessageBox.warning(self, "警告", "请先选择一个记录")
            return

        if self.session_manager.is_locked:
            QMessageBox.warning(self, "警告", "请先解锁应用程序")
            return

        try:
            master_password = self.session_manager.get_master_password()
            if not master_password:
                QMessageBox.warning(self, "警告", "无法获取主密码，请重新登录")
                return

            print(f"尝试显示密码，加密数据长度: {len(self.current_entry.encrypted_password)}")

            # 解密密码
            decrypted_password = self.encryption_manager.decrypt(
                self.current_entry.encrypted_password, master_password
            )

            # 显示密码对话框
            QMessageBox.information(self, "密码",
                                    f"{self.current_entry.website_name} 的密码是:\n\n{decrypted_password}")

        except Exception as e:
            logger.error(f"显示密码错误: {e}")
            print(f"显示密码详细错误: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"解密密码失败: {str(e)}")

    def on_sync(self):
        """同步数据"""
        self.load_entries()
        self.status_bar.showMessage("数据已同步")

    def on_lock(self):
        """锁定应用程序"""
        self.lock_application()

    def on_generate_password(self):
        """生成密码"""
        password = self.password_generator.generate_password()
        QMessageBox.information(self, "生成的密码", f"新密码:\n\n{password}")

    def on_settings(self):
        """打开设置"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            # 应用新设置
            ui_config = self.config_manager.get_ui_config()
            self.resize(ui_config.get('window_width', 1000),
                        ui_config.get('window_height', 600))

            security_config = self.config_manager.get_security_config()
            self.session_manager.auto_lock_minutes = security_config.get('auto_lock_minutes', 15)

    def closeEvent(self, event):
        """关闭事件处理"""
        if self.database_manager:
            self.database_manager.close()

        # 保存窗口大小
        ui_config = self.config_manager.get_ui_config()
        ui_config['window_width'] = self.width()
        ui_config['window_height'] = self.height()
        self.config_manager.update_ui_config(ui_config)

        event.accept()

    def safe_show_dialog(self, dialog):
        """安全显示对话框"""
        try:
            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted:  # 确保使用正确的枚举
                print("对话框接受，重新加载条目...")
                self.load_entries()
                self.status_bar.showMessage("成功添加新记录")
            else:
                print("对话框取消")
            # 显式删除对话框
            dialog.deleteLater()
        except Exception as e:
            print(f"显示对话框时出错: {e}")
            import traceback
            traceback.print_exc()