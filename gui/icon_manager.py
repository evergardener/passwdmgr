# -*- coding: utf-8 -*-
#
# @Created : 2025-11-30 13:12
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    :
import os
import sys
from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication


class IconManager:
    """图标管理器"""

    def __init__(self, base_path=None):
        self.base_path = base_path or self.get_base_path()
        self.icon_cache = {}
        print(f"图标管理器初始化，基础路径: {self.base_path}")

    def get_base_path(self):
        """获取项目根目录路径"""
        # 尝试多种方式获取项目根目录
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            base_dir = Path(sys.executable).parent
        else:
            # 开发环境
            base_dir = Path(__file__).parent.parent

        return str(base_dir)

    def find_icon_file(self, icon_name):
        """获取图标文件路径"""
        # 支持的图标格式和可能的文件名
        possible_paths = [
            f"resources/icons/{icon_name}.ico",  # 新的首选路径
            f"resources/icons/{icon_name}.png",
            f"resources/icons/{icon_name}.svg",
            f"img/{icon_name}.ico",
            f"img/{icon_name}.png",
            f"img/{icon_name}.svg",
            f"resources/{icon_name}.ico",
            f"resources/{icon_name}.png",
            f"icons/{icon_name}.ico",
            f"{icon_name}.ico",
            f"{icon_name}.png",
        ]

        for file_path in possible_paths:
            full_path = os.path.join(self.base_path, file_path)
            if os.path.exists(full_path):
                print(f"找到图标文件: {full_path}")
                return full_path

        # 如果找不到文件，返回None
        print(f"警告: 未找到图标文件: {icon_name}")
        print("搜索路径:")
        for relative_path in possible_paths:
            full_path = os.path.join(self.base_path, relative_path)
            print(f"  {full_path} - 存在: {os.path.exists(full_path)}")

            # 列出基础目录内容
        print(f"\n基础目录内容 ({self.base_path}):")
        try:
            for item in os.listdir(self.base_path):
                print(f"  {item}")
        except Exception as e:
            print(f"无法列出目录: {e}")

        return None

    def get_icon(self, icon_name):
        """获取图标"""
        if icon_name in self.icon_cache:
            return self.icon_cache[icon_name]

        icon_path = self.find_icon_file(icon_name)
        if icon_path:
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.icon_cache[icon_name] = icon
                    print(f"图标加载成功: {icon_name}")
                    return icon
                else:
                    print(f"图标加载失败（空图标）: {icon_name}")
            except Exception as e:
                print(f"图标加载异常: {icon_name}, 错误: {e}")
        else:
            print(f"无法找到图标文件: {icon_name}")

            # 返回空图标
        return QIcon()

    def get_pixmap(self, icon_name, size=(32, 32)):
        """获取像素图"""
        icon_path = self.find_icon_file(icon_name)
        if icon_path:
            try:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    return pixmap.scaled(size[0], size[1])
            except Exception as e:
                print(f"像素图加载失败: {icon_name}, 错误: {e}")
        return QPixmap()

    def set_window_icon(self, window, icon_name="favicon"):
        """设置窗口图标"""
        icon = self.get_icon(icon_name)
        if not icon.isNull():
            window.setWindowIcon(icon)
            print(f"窗口图标设置成功: {icon_name}")
            return True
        else:
            print(f"窗口图标设置失败: {icon_name}")
            return False

    def get_icon_with_fallback(self, icon_name, fallback_text=""):
        """获取图标，如果不存在则使用备选文本"""
        icon = self.get_icon(icon_name)
        if not icon.isNull():
            return icon, ""
        else:
            # 返回空图标和备选文本
            return QIcon(), fallback_text

    def set_action_icon(self, action, icon_name, fallback_text=""):
        """为动作设置图标，如果图标不存在则使用备选文本"""
        icon, fallback = self.get_icon_with_fallback(icon_name, fallback_text)
        if not icon.isNull():
            action.setIcon(icon)
            action.setIconText("")  # 清除图标文本
        elif fallback:
            action.setIconText(fallback)
        else:
            # 既没有图标也没有备选文本，清空图标
            action.setIcon(QIcon())

    def setup_menu_action(self, action, icon_name, default_text=""):
        """为菜单动作设置图标，确保不重复显示"""
        # 首先尝试获取图标文件
        icon = self.get_icon(icon_name)

        if not icon.isNull():
            # 如果有图标文件，使用图标
            action.setIcon(icon)
            # 清除可能存在的图标文本，避免重复
            action.setIconText("")
            # 设置纯文本（不带图标字符）
            if default_text:
                # 移除文本中的图标字符
                clean_text = self.remove_icon_chars(default_text)
                action.setText(clean_text)
            return True
        else:
            # 如果没有图标文件，使用Unicode字符作为文本的一部分
            action.setIcon(QIcon())  # 清除图标
            if default_text:
                clean_text = self.remove_icon_chars(default_text)
                action.setText(clean_text)
            return False

    def remove_icon_chars(self, text):
        """移除文本中的图标字符"""
        # 常见的图标Unicode字符
        # icon_chars = ["📁", "✏️", "🛠️", "🔒", "🔓", "🔄", "🚪", "➕", "🗑️",
        #               "🔑", "📂", "🔐", "⚙️", "🌐", "🔗", "👤", "📅", "📝"]
        icon_chars = ["🔒", "🔓", "🔄", "🚪", "➕", "🗑️",
                      "🔑", "📂", "🔐", "⚙️", "🌐", "🔗",
                      "👤", "📅", "📝"]
        clean_text = text
        for char in icon_chars:
            clean_text = clean_text.replace(char, "")
        return clean_text.strip()

# 全局图标管理器实例
_icon_manager = None


def get_icon_manager():
    """获取全局图标管理器实例"""
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager()
    return _icon_manager


