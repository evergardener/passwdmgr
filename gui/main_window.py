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
                             QToolBar, QMessageBox, QSplitter, QLabel, QApplication, QDialog)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QAction

from core.database_manager import DatabaseManager
from core.encryption_manager import EncryptionManager
from core.config_manager import ConfigManager
from core.session_manager import SessionManager
from core.password_generator import PasswordGenerator
from core.resource_manager import get_resource_manager
from gui.login_dialog import LoginDialog
from gui.settings_dialog import SettingsDialog
from gui.add_edit_dialog import AddEditDialog
from gui.icon_manager import get_icon_manager
from gui.menu_manager import MenuManager

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


        # 资源管理器
        self.resource_manager = get_resource_manager()
        # 图标管理器
        self.icon_manager = get_icon_manager()

        # 菜单管理器
        self.menu_manager = MenuManager(self.icon_manager)

        # 当前选中的条目
        self.current_entry = None

        # 加载模板
        self.detail_template = self.load_detail_template()

        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_signals()

        # 设置窗口图标
        self.setup_icons()

        # 检查菜单图标可用性
        self.check_menu_icon_availability()

        # 自动锁定定时器
        self.auto_lock_timer = QTimer()
        self.auto_lock_timer.timeout.connect(self.check_auto_lock)
        self.auto_lock_timer.start(30000)  # 每30秒检查一次

        # 初始状态为锁定
        self.session_manager.lock()
        self.update_lock_action_text()

        # 尝试连接数据库
        self.connect_to_database()

    def load_detail_template(self):
        """加载详情模板"""
        template = self.resource_manager.get_template("detail_template.html")
        if template is None:
            # 如果模板文件不存在，使用内联的默认模板
            template = self.get_default_detail_template()
            print("使用默认详情模板")
        else:
            print("详情模板加载成功")
        return template

    def get_default_detail_template(self):
        """获取默认的详情模板（备用）"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .card {
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                overflow: hidden;
                margin-bottom: 20px;
            }
            .card-header {
                background: linear-gradient(135deg, #007bff, #0056b3);
                color: white;
                padding: 15px 20px;
                font-weight: 600;
                font-size: 16px;
            }
            .card-body {
                padding: 20px;
            }
            .detail-row {
                display: flex;
                margin-bottom: 12px;
                align-items: flex-start;
            }
            .detail-label {
                flex: 0 0 120px;
                font-weight: 600;
                color: #495057;
                margin-right: 10px;
            }
            .detail-value {
                flex: 1;
                color: #212529;
                word-break: break-word;
            }
            .empty-field {
                color: #6c757d;
                font-style: italic;
            }
            .notes-card .card-header {
                background: linear-gradient(135deg, #17a2b8, #138496);
            }
            .notes-content {
                white-space: pre-wrap;
                line-height: 1.5;
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #17a2b8;
            }
            .icon {
                margin-right: 8px;
                font-size: 14px;
            }
            .category-badge {
                background: #e9ecef;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                display: inline-block;
            }
            .no-selection {
                text-align: center;
                color: #6c757d;
                padding: 50px;
            }
        </style>
        </head>
        <body>
            <div id="no-selection" class="no-selection">
                <h3>📋 密码详情</h3>
                <p>请从左侧列表选择一个密码条目查看详情</p>
            </div>
            <div id="detail-content" style="display: none;">
                <div class="card">
                    <div class="card-header">
                        <span class="icon">🔐</span> 基本信息
                    </div>
                    <div class="card-body">
                        <div class="detail-row">
                            <div class="detail-label">网站名称</div>
                            <div class="detail-value" id="website-name"></div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">URL</div>
                            <div class="detail-value" id="url"></div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">用户名</div>
                            <div class="detail-value" id="username"></div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">分类</div>
                            <div class="detail-value">
                                <span class="category-badge" id="category"></span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">
                        <span class="icon">⏰</span> 时间信息
                    </div>
                    <div class="card-body">
                        <div class="detail-row">
                            <div class="detail-label">创建时间</div>
                            <div class="detail-value" id="created-at"></div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">更新时间</div>
                            <div class="detail-value" id="updated-at"></div>
                        </div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header notes-card">
                        <span class="icon">📝</span> 备注
                    </div>
                    <div class="card-body">
                        <div class="notes-content" id="notes"></div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    def setup_icons(self):
        """设置图标"""
        # 设置窗口图标
        success = self.icon_manager.set_window_icon(self, "favicon")

        if not success:
            # 如果 favicon 失败，尝试其他可能的图标名称
            alternative_names = ["icon", "app", "logo", "password", "lock"]
            for name in alternative_names:
                if self.icon_manager.set_window_icon(self, name):
                    print(f"使用备选图标: {name}")
                    break
            else:
                print("警告: 无法设置任何窗口图标")

        # 设置应用程序图标（影响任务栏等）
        app_icon = self.icon_manager.get_icon("favicon")
        if not app_icon.isNull():
            QApplication.setWindowIcon(app_icon)

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

    def setup_menu_without_icons(self):
        """设置菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        self.lock_action = QAction("锁定", self)  # 初始状态为"锁定"
        self.sync_action = QAction("同步", self)
        self.exit_action = QAction("退出", self)

        # 为菜单项设置图标
        self.lock_action.setIcon(self.icon_manager.get_icon("lock"))
        self.sync_action.setIcon(self.icon_manager.get_icon("sync"))

        file_menu.addAction(self.sync_action)
        file_menu.addAction(self.lock_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")

        self.add_action = QAction("添加", self)
        self.edit_action = QAction("编辑", self)
        self.delete_action = QAction("删除", self)

        # 为编辑菜单项设置图标
        self.add_action.setIcon(self.icon_manager.get_icon("add"))
        self.edit_action.setIcon(self.icon_manager.get_icon("edit"))
        self.delete_action.setIcon(self.icon_manager.get_icon("delete"))

        edit_menu.addAction(self.add_action)
        edit_menu.addAction(self.edit_action)
        edit_menu.addAction(self.delete_action)

        # 工具菜单
        tools_menu = menubar.addMenu("工具")

        self.generate_password_action = QAction("生成密码", self)
        self.manage_categories_action = QAction("管理分类", self)
        self.change_password_action = QAction("修改主密码", self)
        self.settings_action = QAction("设置", self)

        # 为工具菜单项设置图标
        self.generate_password_action.setIcon(self.icon_manager.get_icon("key"))
        self.manage_categories_action.setIcon(self.icon_manager.get_icon("category"))
        self.change_password_action.setIcon(self.icon_manager.get_icon("admin_password"))
        self.settings_action.setIcon(self.icon_manager.get_icon("settings"))

        tools_menu.addAction(self.generate_password_action)
        tools_menu.addAction(self.manage_categories_action)
        tools_menu.addAction(self.change_password_action)
        tools_menu.addAction(self.settings_action)

        # 根据初始锁定状态更新菜单文本
        self.update_lock_action_text()

    def setup_menu_old(self):
        """设置菜单栏 - 修复对齐和图标重复问题"""
        menubar = self.menuBar()

        # 设置菜单栏样式
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                spacing: 8px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 1px;
                font-weight: 500;
            }
            QMenuBar::item:selected {
                background-color: #e3f2fd;
                color: #1565c0;
            }
            QMenuBar::item:pressed {
                background-color: #bbdefb;
            }
            QMenu {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                margin: 2px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #1565c0;
            }
            QMenu::separator {
                height: 1px;
                background: #dee2e6;
                margin: 4px 8px;
            }
        """)

        # 文件菜单
        file_menu = menubar.addMenu("📁 文件")


        # 同步动作
        self.sync_action = QAction("同步", self)
        self.icon_manager.setup_menu_action(self.sync_action, "sync", "同步")

        # 锁定/解锁动作
        self.lock_action = QAction("解锁", self)
        # 初始状态为锁定，所以显示解锁图标
        if self.session_manager.is_locked:
            self.icon_manager.setup_menu_action(self.lock_action, "unlock", "解锁")
        else:
            self.icon_manager.setup_menu_action(self.lock_action, "lock", "锁定")

        # 退出动作 - 确保有图标
        self.exit_action = QAction("退出", self)
        self.icon_manager.setup_menu_action(self.exit_action, "exit", "退出")
        # 如果退出图标不存在，使用默认图标
        exit_icon = self.icon_manager.get_icon("exit")
        if exit_icon.isNull():
            # 尝试其他可能的退出图标名称
            exit_icon = self.icon_manager.get_icon("quit")
            if exit_icon.isNull():
                exit_icon = self.icon_manager.get_icon("close")
                if exit_icon.isNull():
                    # 如果都没有，使用系统标准图标
                    from PyQt6.QtGui import QIcon
                    from PyQt6.QtWidgets import QStyle
                    exit_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton)

        if not exit_icon.isNull():
            self.exit_action.setIcon(exit_icon)

        file_menu.addAction(self.sync_action)
        file_menu.addAction(self.lock_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("✏️ 编辑")

        self.add_action = QAction("添加", self)
        self.edit_action = QAction("编辑", self)
        self.delete_action = QAction("删除", self)

        # 为编辑菜单项设置图标
        self.icon_manager.setup_menu_action(self.add_action, "add", "添加")
        self.icon_manager.setup_menu_action(self.edit_action, "edit", "编辑")
        self.icon_manager.setup_menu_action(self.delete_action, "delete", "删除")

        edit_menu.addAction(self.add_action)
        edit_menu.addAction(self.edit_action)
        edit_menu.addAction(self.delete_action)

        # 工具菜单
        tools_menu = menubar.addMenu("🛠️ 工具")

        self.generate_password_action = QAction("生成密码", self)
        self.manage_categories_action = QAction("管理分类", self)
        self.change_password_action = QAction("修改主密码", self)
        self.settings_action = QAction("设置", self)

        # 为工具菜单项设置图标
        self.icon_manager.setup_menu_action(self.generate_password_action, "key", "生成密码")
        self.icon_manager.setup_menu_action(self.manage_categories_action, "category", "管理分类")
        self.icon_manager.setup_menu_action(self.change_password_action, "admin_password", "修改主密码")
        self.icon_manager.setup_menu_action(self.settings_action, "settings", "设置")

        tools_menu.addAction(self.generate_password_action)
        tools_menu.addAction(self.manage_categories_action)
        tools_menu.addAction(self.change_password_action)
        tools_menu.addAction(self.settings_action)

        # 初始状态为锁定，所以编辑功能应该禁用
        self.add_action.setEnabled(False)
        self.edit_action.setEnabled(False)
        self.delete_action.setEnabled(False)

    def setup_menu(self):
        """设置菜单栏 - 使用菜单管理器"""
        menubar = self.menuBar()

        # 设置菜单栏样式（同上）
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                spacing: 8px;
                font-weight: 500;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 1px;
            }
            QMenuBar::item:selected {
                background-color: #e3f2fd;
                color: #1565c0;
            }
            QMenuBar::item:pressed {
                background-color: #bbdefb;
            }
        """)

        # 文件菜单
        file_menu_data = [
            {
                'text': '同步',
                'icon': 'sync',
                'enabled': True
            },
            {
                'text': '解锁' if self.session_manager.is_locked else '锁定',
                'icon': 'unlock' if self.session_manager.is_locked else 'lock',
                'enabled': True
            },
            {'separator': True},
            {
                'text': '退出',
                'icon': 'exit',
                'enabled': True
            }
        ]

        file_menu = self.menu_manager.create_menu(self, "📁 文件", file_menu_data)
        menubar.addMenu(file_menu)

        # 获取文件菜单中的动作
        self.sync_action = file_menu.actions()[0]
        self.lock_action = file_menu.actions()[1]
        self.exit_action = file_menu.actions()[3]  # 跳过分隔符

        # 编辑菜单
        edit_menu_data = [
            {
                'text': '添加',
                'icon': 'add',
                'enabled': not self.session_manager.is_locked
            },
            {
                'text': '编辑',
                'icon': 'edit',
                'enabled': not self.session_manager.is_locked
            },
            {
                'text': '删除',
                'icon': 'delete',
                'enabled': not self.session_manager.is_locked
            }
        ]

        edit_menu = self.menu_manager.create_menu(self, "✏️ 编辑", edit_menu_data)
        menubar.addMenu(edit_menu)

        # 获取编辑菜单中的动作
        self.add_action = edit_menu.actions()[0]
        self.edit_action = edit_menu.actions()[1]
        self.delete_action = edit_menu.actions()[2]

        # 工具菜单
        tools_menu_data = [
            {
                'text': '生成密码',
                'icon': 'key',
                'enabled': True
            },
            {
                'text': '管理分类',
                'icon': 'category',
                'enabled': True
            },
            {
                'text': '修改主密码',
                'icon': 'admin_password',
                'enabled': True
            },
            {
                'text': '设置',
                'icon': 'settings',
                'enabled': True
            }
        ]

        tools_menu = self.menu_manager.create_menu(self, "🛠️ 工具", tools_menu_data)
        menubar.addMenu(tools_menu)

        # 获取工具菜单中的动作
        self.generate_password_action = tools_menu.actions()[0]
        self.manage_categories_action = tools_menu.actions()[1]
        self.change_password_action = tools_menu.actions()[2]
        self.settings_action = tools_menu.actions()[3]

    def update_lock_action_text(self):
        """根据锁定状态更新锁定/解锁菜单项文本和图标"""
        if self.session_manager.is_locked:
            # 当前已锁定，显示解锁
            self.lock_action.setText("解锁")
            self.icon_manager.setup_menu_action(self.lock_action, "unlock", "解锁")
            # 禁用编辑功能
            self.add_action.setEnabled(False)
            self.edit_action.setEnabled(False)
            self.delete_action.setEnabled(False)
        else:
            # 当前未锁定，显示锁定
            self.lock_action.setText("锁定")
            self.icon_manager.setup_menu_action(self.lock_action, "lock", "锁定")
            # 启用编辑功能
            self.add_action.setEnabled(True)
            self.edit_action.setEnabled(True)
            self.delete_action.setEnabled(True)

            # 更新工具栏按钮的状态
        self.update_toolbar_lock_state()

    def update_toolbar_lock_state(self):
        """更新工具栏锁定状态"""
        # 根据锁定状态启用/禁用相关功能
        is_locked = self.session_manager.is_locked

        # 更新编辑相关按钮的状态
        self.add_action.setEnabled(not is_locked)
        self.edit_action.setEnabled(not is_locked)
        self.delete_action.setEnabled(not is_locked)
        self.copy_username_button.setEnabled(not is_locked)
        self.copy_password_button.setEnabled(not is_locked)
        self.show_password_button.setEnabled(not is_locked)

        # 更新状态栏提示
        if is_locked:
            self.status_bar.showMessage("应用程序已锁定")
        else:
            self.status_bar.showMessage("应用程序已解锁")

    def setup_toolbar_without_icons(self):
        """设置工具栏"""
        toolbar = QToolBar("主工具栏")
        self.addToolBar(toolbar)

        # 为工具栏按钮设置图标
        self.add_action.setIcon(self.icon_manager.get_icon("add"))
        self.edit_action.setIcon(self.icon_manager.get_icon("edit"))
        self.delete_action.setIcon(self.icon_manager.get_icon("delete"))
        toolbar.addAction(self.add_action)
        toolbar.addAction(self.edit_action)
        toolbar.addAction(self.delete_action)

        toolbar.addSeparator()

        self.sync_action.setIcon(self.icon_manager.get_icon("sync"))
        self.lock_action.setIcon(self.icon_manager.get_icon("lock"))

        toolbar.addAction(self.sync_action)
        toolbar.addAction(self.lock_action)  # 工具栏按钮也会自动更新文本

    def setup_toolbar(self):
        """设置工具栏 - 修复图标重复问题"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        # 为工具栏按钮设置图标
        self.icon_manager.setup_menu_action(self.add_action, "add", "添加")
        self.icon_manager.setup_menu_action(self.edit_action, "edit", "编辑")
        self.icon_manager.setup_menu_action(self.delete_action, "delete", "删除")

        toolbar.addAction(self.add_action)
        toolbar.addAction(self.edit_action)
        toolbar.addAction(self.delete_action)

        toolbar.addSeparator()

        # 同步动作
        self.icon_manager.setup_menu_action(self.sync_action, "sync", "同步")
        toolbar.addAction(self.sync_action)

        # 锁定/解锁动作
        if self.session_manager.is_locked:
            self.icon_manager.setup_menu_action(self.lock_action, "unlock", "解锁")
        else:
            self.icon_manager.setup_menu_action(self.lock_action, "lock", "锁定")
        toolbar.addAction(self.lock_action)

        # 设置工具栏样式
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #dee2e6;
                spacing: 3px;
                padding: 3px;
            }
            QToolButton {
                padding: 6px 8px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #e9ecef;
            }
            QToolButton:pressed {
                background-color: #dee2e6;
            }
        """)

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
        self.manage_categories_action.triggered.connect(self.on_manage_categories)
        self.change_password_action.triggered.connect(self.on_change_password)
        self.settings_action.triggered.connect(self.on_settings)

    def connect_to_database(self):
        """连接到数据库"""
        db_config = self.config_manager.get_database_config()

        # 调试信息
        print(f"主窗口获取的数据库配置: use_sqlite={db_config.get('use_sqlite')}")

        # 如果配置了使用 SQLite，直接连接
        if db_config.get('use_sqlite', True):
            print("使用 SQLite 数据库")
            if self.database_manager.connect(db_config):
                self.status_bar.showMessage("SQLite 数据库连接成功")
                # 数据库连接成功后显示登录对话框
                self.show_login_dialog()
            else:
                self.status_bar.showMessage("SQLite 数据库连接失败")
        else:
            # 使用 MySQL
            if db_config.get('username') and db_config.get('password'):
                if self.database_manager.connect(db_config):
                    self.status_bar.showMessage("MySQL 数据库连接成功")
                    # 数据库连接成功后显示登录对话框
                    self.show_login_dialog()
                else:
                    self.show_database_settings()
            else:
                self.show_database_settings()

    def check_auto_lock(self):
        """检查自动锁定"""
        if not self.session_manager.is_locked and self.session_manager.check_auto_lock():
            # 只有在未锁定的情况下才执行自动锁定
            self.lock_application()
            QMessageBox.information(self, "自动锁定", "由于长时间无操作，应用程序已自动锁定")

    def lock_application(self):
        """锁定应用程序"""
        self.session_manager.lock()
        self.update_lock_action_text()
        self.status_bar.showMessage("应用程序已锁定")
        # 清空当前选择
        self.current_entry = None
        self.details_text.clear()
        self.entries_table.clearSelection()

    def show_login_dialog(self):
        """显示登录对话框"""
        dialog = LoginDialog(
            self.session_manager,
            self.encryption_manager,
            self.database_manager,  # 新增参数
            self
        )

        if dialog.exec():
            self.status_bar.showMessage("已解锁")
            self.update_lock_action_text()
            self.load_entries()
        else:
            # 如果取消登录，保持锁定状态
            self.update_lock_action_text()

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

    def update_details_display_with_template(self):
        """更新详情显示 - 使用模板"""
        if not self.current_entry:
            # 显示无选择状态
            html = self.detail_template
            # 确保显示无选择状态，隐藏详情内容
            html = self.ensure_no_selection_display(html)
            self.details_text.setHtml(html)
            return

        # 准备数据
        website_name = self.escape_html(self.current_entry.website_name)

        # URL处理：如果是空URL，显示"未设置"，否则创建可点击链接
        if self.current_entry.url and self.current_entry.url.strip():
            url_text = self.current_entry.url.strip()
            # 确保URL有协议前缀
            if not url_text.startswith(('http://', 'https://')):
                url_text = 'https://' + url_text
            url = f'<a href="{url_text}" target="_blank" class="info-value url">{self.escape_html(self.current_entry.url)}</a>'
        else:
            url = '<span style="color: #6c757d; font-style: italic;">未设置</span>'

        username = self.escape_html(self.current_entry.username)
        category = self.escape_html(self.current_entry.category) if self.current_entry.category else '默认'
        created_at = self.current_entry.created_at.strftime(
            '%Y-%m-%d %H:%M') if self.current_entry.created_at else '<span style="color: #6c757d; font-style: italic;">未知</span>'
        updated_at = self.current_entry.updated_at.strftime(
            '%Y-%m-%d %H:%M') if self.current_entry.updated_at else '<span style="color: #6c757d; font-style: italic;">未知</span>'

        # 备注处理：如果是空备注，显示特定提示
        if self.current_entry.notes and self.current_entry.notes.strip():
            notes = self.escape_html(self.current_entry.notes)
        else:
            notes = '<div class="empty-note">暂无备注信息</div>'

        # 使用直接HTML替换的方法
        html = self.detail_template

        # 替换显示状态
        html = html.replace('id="no-selection"', 'id="no-selection" style="display: none;"')
        html = html.replace('id="detail-content" style="display: none;"', 'id="detail-content"')

        # 直接替换数据占位符
        html = html.replace('id="website-name"></div>', f'id="website-name">{website_name}</div>')
        html = html.replace('id="url"></div>', f'id="url">{url}</div>')
        html = html.replace('id="username"></div>', f'id="username">{username}</div>')
        html = html.replace('id="category"></span>', f'id="category">{category}</span>')
        html = html.replace('id="created-at"></div>', f'id="created-at">{created_at}</div>')
        html = html.replace('id="updated-at"></div>', f'id="updated-at">{updated_at}</div>')
        html = html.replace('id="notes"></div>', f'id="notes">{notes}</div>')

        self.details_text.setHtml(html)
        print("详情数据填充完成")

    def update_details_display(self):
        """更新详情显示 - 使用纯文本美化格式"""
        if not self.current_entry:
            # 显示无选择状态
            self.details_text.setPlainText("""
    ╔═══════════════════════════════════════
    ║           🔐 密码管理器                
    ╠═══════════════════════════════════════
    ║                                      
    ║   请从左侧列表选择一个密码条目         
    ║   查看详细信息                        
    ║                                      
    ╚═══════════════════════════════════════
            """)
            return

        # 准备数据
        website_name = self.current_entry.website_name
        url = self.current_entry.url if self.current_entry.url else "未设置"
        username = self.current_entry.username
        category = self.current_entry.category if self.current_entry.category else "默认"

        created_at = self.current_entry.created_at.strftime('%Y-%m-%d %H:%M') if self.current_entry.created_at else "未知"
        updated_at = self.current_entry.updated_at.strftime('%Y-%m-%d %H:%M') if self.current_entry.updated_at else "未知"

        notes = self.current_entry.notes if self.current_entry.notes else "无备注信息"

        # 创建格式化的纯文本显示
        details = f"""
    ╔═══════════════════════════════════════
    ║           🔐 密码管理器                
    ╠═══════════════════════════════════════

    📋 基本信息
    ─────────────────────────────────────
    🌐 网站名称: {website_name}

    🔗 网站地址: {url}

    👤 用户名: {username}

    📁 分类: {category}


    ⏰ 时间信息  
    ─────────────────────────────────────
    📅 创建时间: {created_at}

    🔄 更新时间: {updated_at}


    📝 备注信息
    ─────────────────────────────────────
    {notes}

    ╚═══════════════════════════════════════
        """

        self.details_text.setPlainText(details)


    def ensure_no_selection_display(self, html):
        """确保显示无选择状态"""
        # 隐藏详情内容，显示无选择提示
        html = html.replace('id="no-selection"', 'id="no-selection"')
        html = html.replace('id="detail-content"', 'id="detail-content" style="display: none;"')
        return html

    def escape_html(self, text):
        """转义HTML特殊字符"""
        if not text:
            return ""
        return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;')
                .replace('\n', '<br>'))

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
            # 传递 config_manager 参数
            dialog = AddEditDialog(
                database_manager=self.database_manager,
                encryption_manager=self.encryption_manager,
                session_manager=self.session_manager,
                password_generator=self.password_generator,
                config_manager=self.config_manager,  # 传递 config_manager
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

        # 传递 config_manager 参数
        dialog = AddEditDialog(
            database_manager=self.database_manager,
            encryption_manager=self.encryption_manager,
            session_manager=self.session_manager,
            password_generator=self.password_generator,
            config_manager=self.config_manager,  # 传递 config_manager
            parent=self,
            entry=self.current_entry
        )
        if dialog.exec():
            self.load_entries()
            self.status_bar.showMessage("成功更新记录")

    def safe_show_dialog(self, dialog):
        """安全显示对话框"""
        try:
            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted:
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

    def on_edit_entry(self):
        """编辑选中条目"""
        if self.session_manager.is_locked:
            QMessageBox.warning(self, "警告", "请先解锁应用程序")
            return

        if not self.current_entry:
            QMessageBox.warning(self, "警告", "请先选择一个记录")
            return

            # 传递 config_manager 参数
        dialog = AddEditDialog(self.database_manager, self.encryption_manager,
                               self.session_manager, self.password_generator,
                               self.config_manager, self,  # 新增 config_manager
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
        if self.session_manager.is_locked:
            # 当前已锁定，执行解锁操作
            self.show_login_dialog()
        else:
            # 当前未锁定，执行锁定操作
            self.lock_application()

        # 更新锁定/解锁状态显示
        self.update_lock_action_text()

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

    def show_database_settings(self):
        """显示数据库设置对话框"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            # 重新连接数据库
            self.connect_to_database()

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

    def on_manage_categories(self):
        """管理分类"""
        from .categories_dialog import CategoriesDialog
        dialog = CategoriesDialog(self.config_manager, self)
        dialog.exec()

    def on_change_password(self):
        """修改主密码 - 强制重新验证"""
        if self.session_manager.is_locked:
            QMessageBox.warning(self, "警告", "请先解锁应用程序")
            return

        from .change_master_password_dialog import ChangeMasterPasswordDialog

        dialog = ChangeMasterPasswordDialog(
            self.database_manager,
            self.encryption_manager,
            self.session_manager,
            self
        )

        if dialog.exec():
            # 修改成功后，强制重新登录以确保一致性
            reply = QMessageBox.question(
                self, "重新登录",
                "主密码修改成功！为了确保安全性，建议立即重新登录。\n是否现在重新登录？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.lock_application()
                self.show_login_dialog()
            else:
                QMessageBox.information(self, "成功",
                                        "主密码修改成功！\n"
                                        "请注意：某些操作可能需要重新登录后才能正常工作。")

    def check_menu_icon_availability(self):
        """检查菜单图标可用性"""
        print("=== 菜单图标可用性检查 ===")

        # 定义需要的图标
        required_icons = {
            "lock": "锁定",
            "sync": "同步",
            "add": "添加",
            "edit": "编辑",
            "delete": "删除",
            "key": "生成密码",
            "category": "管理分类",
            "admin_password": "修改密码",
            "settings": "设置"
        }

        available = []
        missing = []

        for icon_name, description in required_icons.items():
            icon = self.icon_manager.get_icon(icon_name)
            if not icon.isNull():
                available.append(f"✅ {description} [{icon_name}]")
            else:
                missing.append(f"❌ {description} [{icon_name}]")

        print("可用的图标:")
        for item in available:
            print(f"  {item}")

        if missing:
            print("\n缺失的图标:")
            for item in missing:
                print(f"  {item}")
            print("\n建议: 使用Unicode字符作为备选方案")
        else:
            print("\n所有图标都可用!")