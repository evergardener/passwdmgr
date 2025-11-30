# -*- coding: utf-8 -*-
#
# @Created : 2025-11-30 15:40
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    :
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction


class MenuManager:
    """菜单管理器"""

    def __init__(self, icon_manager):
        self.icon_manager = icon_manager

    def create_menu(self, parent, title_with_icon, menu_data):
        """创建带图标的菜单"""
        menu = QMenu(title_with_icon, parent)

        for item_data in menu_data:
            if item_data.get('separator', False):
                menu.addSeparator()
            else:
                action = QAction(item_data['text'], parent)

                # 设置图标（如果有）
                if 'icon' in item_data:
                    self.icon_manager.setup_menu_action(
                        action,
                        item_data['icon'],
                        item_data['text']
                    )

                # 设置其他属性
                if 'enabled' in item_data:
                    action.setEnabled(item_data['enabled'])
                if 'shortcut' in item_data:
                    action.setShortcut(item_data['shortcut'])
                if 'tooltip' in item_data:
                    action.setToolTip(item_data['tooltip'])

                menu.addAction(action)

        return menu