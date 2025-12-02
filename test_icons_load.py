#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试图标加载
"""
import sys
import os

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar

# 临时添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.icon_manager import get_icon_manager

def test_icons():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("图标测试")
    window.resize(400, 300)

    # 获取图标管理器
    icon_manager = get_icon_manager()

    # 创建菜单栏
    menubar = window.menuBar()

    # 文件菜单
    file_menu = menubar.addMenu("文件")

    # 测试所有菜单项
    menu_items = [
        ("同步", "sync"),
        ("锁定", "lock"),
        ("解锁", "unlock"),
        ("退出", "exit"),
    ]

    for text, icon_name in menu_items:
        action = QAction(text, window)
        icon_manager.setup_menu_action(action, icon_name, text)
        file_menu.addAction(action)

    # 编辑菜单
    edit_menu = menubar.addMenu("编辑")

    edit_items = [
        ("添加", "add"),
        ("编辑", "edit"),
        ("删除", "delete"),
    ]

    for text, icon_name in edit_items:
        action = QAction(text, window)
        icon_manager.setup_menu_action(action, icon_name, text)
        edit_menu.addAction(action)

    # 工具菜单
    tools_menu = menubar.addMenu("工具")

    tools_items = [
        ("生成密码", "key"),
        ("管理分类", "category"),
        ("修改密码", "admin_password"),
        ("设置", "settings"),
    ]

    for text, icon_name in tools_items:
        action = QAction(text, window)
        icon_manager.setup_menu_action(action, icon_name, text)
        tools_menu.addAction(action)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    test_icons()