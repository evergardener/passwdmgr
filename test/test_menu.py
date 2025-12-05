# -*- coding: utf-8 -*-
#
# @Created : 2025-11-30 15:32
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    :
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit
except:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit
from gui.icon_manager import get_icon_manager
from gui.menu_manager import MenuManager


class TestMenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.icon_manager = get_icon_manager()
        self.menu_manager = MenuManager(self.icon_manager)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("菜单图标测试")
        self.setGeometry(100, 100, 600, 400)

        # 设置中心文本区域
        text_edit = QTextEdit()
        text_edit.setPlainText("""菜单图标测试窗口

请检查以下内容：
1. 文件、编辑、工具菜单标题前是否有图标
2. 菜单项是否有图标（如果有图标文件）
3. 菜单项是否对齐
4. 没有重复的图标显示""")
        self.setCentralWidget(text_edit)

        # 设置菜单
        self.setup_test_menu()

    def setup_test_menu(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu_data = [
            {'text': '同步', 'icon': 'sync'},
            {'text': '锁定', 'icon': 'lock'},
            {'separator': True},
            {'text': '退出', 'icon': 'exit'}
        ]

        file_menu = self.menu_manager.create_menu(self, "📁 文件", file_menu_data)
        menubar.addMenu(file_menu)

        # 编辑菜单
        edit_menu_data = [
            {'text': '添加', 'icon': 'add'},
            {'text': '编辑', 'icon': 'edit'},
            {'text': '删除', 'icon': 'delete'}
        ]

        edit_menu = self.menu_manager.create_menu(self, "✏️ 编辑", edit_menu_data)
        menubar.addMenu(edit_menu)

        # 工具菜单
        tools_menu_data = [
            {'text': '生成密码', 'icon': 'key'},
            {'text': '管理分类', 'icon': 'category'},
            {'text': '修改密码', 'icon': 'admin'},
            {'text': '设置', 'icon': 'settings'}
        ]

        tools_menu = self.menu_manager.create_menu(self, "🛠️ 工具", tools_menu_data)
        menubar.addMenu(tools_menu)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestMenuWindow()
    window.show()
    sys.exit(app.exec())