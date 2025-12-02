# -*- coding: utf-8 -*-
#
# @Created : 2025-11-30 13:12
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    :
# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复版图标管理器 - 包含所有必要的方法
"""
import os
import sys
from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtWidgets import QStyle, QApplication
from PyQt6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)


class IconManager:
    """图标管理器 - 兼容单文件打包和开发环境"""

    def __init__(self):
        self.icon_cache = {}
        self.resource_base = self.get_resource_base()
        print(f"图标管理器初始化，资源基础路径: {self.resource_base}")
        self.test_all_icons()

    def get_resource_base(self):
        """获取资源基础路径"""
        if getattr(sys, 'frozen', False):
            # 打包环境
            if hasattr(sys, '_MEIPASS'):
                # 临时解压目录（单文件模式）
                base = sys._MEIPASS
                print(f"单文件模式，临时目录: {base}")
            else:
                # 文件夹模式
                base = os.path.dirname(sys.executable)
                print(f"文件夹模式，可执行文件目录: {base}")
        else:
            # 开发环境
            base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            print(f"开发环境，项目根目录: {base}")

        return base

    def get_icon_path(self, icon_name):
        """获取图标文件路径"""
        # 尝试不同的扩展名
        extensions = ['.svg', '.png', '.ico', '.jpg', '.jpeg']

        # 尝试不同的路径
        possible_paths = []

        # 1. 在打包资源的临时目录中查找
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base = sys._MEIPASS
            for ext in extensions:
                path = os.path.join(base, 'resources', 'icons', f"{icon_name}{ext}")
                possible_paths.append(path)

        # 2. 在可执行文件所在目录的资源中查找
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
            for ext in extensions:
                path = os.path.join(base, 'resources', 'icons', f"{icon_name}{ext}")
                possible_paths.append(path)

        # 3. 在当前工作目录中查找
        for ext in extensions:
            path = os.path.join(os.getcwd(), 'resources', 'icons', f"{icon_name}{ext}")
            possible_paths.append(path)

        # 4. 在项目根目录中查找（开发环境）
        for ext in extensions:
            path = os.path.join(self.resource_base, 'resources', 'icons', f"{icon_name}{ext}")
            possible_paths.append(path)

        # 5. 直接查找（可能图标文件就在根目录）
        for ext in extensions:
            path = os.path.join(self.resource_base, f"{icon_name}{ext}")
            possible_paths.append(path)

        # 去重
        possible_paths = list(dict.fromkeys(possible_paths))

        # 查找存在的文件
        for path in possible_paths:
            if os.path.exists(path):
                logger.debug(f"找到图标: {icon_name} -> {path}")
                return path

        logger.warning(f"未找到图标文件: {icon_name}")
        return None

    def get_icon(self, icon_name):
        """获取图标"""
        # 检查缓存
        if icon_name in self.icon_cache:
            return self.icon_cache[icon_name]

        # 1. 首先尝试从文件加载
        icon_path = self.get_icon_path(icon_name)
        if icon_path:
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.icon_cache[icon_name] = icon
                    return icon
            except Exception as e:
                logger.error(f"加载图标文件失败: {icon_name}, 错误: {e}")

        # 2. 使用系统标准图标作为备选
        system_icon = self.get_system_icon(icon_name)
        if system_icon and not system_icon.isNull():
            self.icon_cache[icon_name] = system_icon
            return system_icon

        # 3. 创建简单的彩色图标
        fallback_icon = self.create_simple_icon(icon_name)
        self.icon_cache[icon_name] = fallback_icon
        return fallback_icon

    def get_system_icon(self, icon_name):
        """获取系统标准图标"""
        try:
            app = QApplication.instance()
            if not app:
                return QIcon()

            style = app.style()

            # 图标名称到系统标准图标的映射
            system_icon_map = {
                'add': QStyle.StandardPixmap.SP_FileIcon,
                'edit': QStyle.StandardPixmap.SP_FileDialogDetailedView,
                'delete': QStyle.StandardPixmap.SP_TrashIcon,
                'save': QStyle.StandardPixmap.SP_DialogSaveButton,
                'sync': QStyle.StandardPixmap.SP_BrowserReload,
                'lock': QStyle.StandardPixmap.SP_DialogNoButton,
                'unlock': QStyle.StandardPixmap.SP_DialogYesButton,
                'exit': QStyle.StandardPixmap.SP_DialogCloseButton,
                'settings': QStyle.StandardPixmap.SP_FileDialogListView,
                'key': QStyle.StandardPixmap.SP_FileDialogContentsView,
                'category': QStyle.StandardPixmap.SP_DirIcon,
                'admin_password': QStyle.StandardPixmap.SP_ComputerIcon,
                'favicon': QStyle.StandardPixmap.SP_ComputerIcon,
            }

            if icon_name in system_icon_map:
                return style.standardIcon(system_icon_map[icon_name])

        except Exception as e:
            logger.error(f"获取系统图标失败: {icon_name}, 错误: {e}")

        return QIcon()

    def create_simple_icon(self, icon_name):
        """创建简单的彩色图标作为最后备选"""
        try:
            # 创建32x32的图标
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.transparent)

            # 根据图标名称选择颜色
            color_map = {
                'add': QColor(76, 175, 80),  # 绿色
                'edit': QColor(33, 150, 243),  # 蓝色
                'delete': QColor(244, 67, 54),  # 红色
                'sync': QColor(156, 39, 176),  # 紫色
                'lock': QColor(255, 152, 0),  # 橙色
                'unlock': QColor(76, 175, 80),  # 绿色
                'exit': QColor(96, 125, 139),  # 蓝灰
                'settings': QColor(158, 158, 158),  # 灰色
                'key': QColor(255, 193, 7),  # 黄色
                'category': QColor(0, 188, 212),  # 青色
                'admin_password': QColor(63, 81, 181),  # 深蓝
                'favicon': QColor(103, 58, 183),  # 紫色
            }

            color = color_map.get(icon_name, QColor(96, 125, 139))

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 绘制圆形
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(4, 4, 24, 24)

            # 添加首字母
            if icon_name:
                painter.setPen(QColor(255, 255, 255))
                painter.setFont(QFont("Arial", 14))
                letter = icon_name[0].upper()
                painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, letter)

            painter.end()

            return QIcon(pixmap)

        except Exception as e:
            logger.error(f"创建简单图标失败: {icon_name}, 错误: {e}")
            return QIcon()

    def setup_menu_action(self, action, icon_name, default_text=""):
        """设置菜单动作图标"""
        icon = self.get_icon(icon_name)
        action.setIcon(icon)

        # 如果图标加载失败，在文本中添加Unicode字符
        if icon.isNull() and default_text:
            unicode_map = {
                'add': '➕ ',
                'edit': '✏️ ',
                'delete': '🗑️ ',
                'sync': '🔄 ',
                'lock': '🔒 ',
                'unlock': '🔓 ',
                'exit': '🚪 ',
                'settings': '⚙️ ',
                'key': '🔑 ',
                'category': '📁 ',
                'admin_password': '🔐 ',
            }

            if icon_name in unicode_map:
                action.setText(f"{unicode_map[icon_name]}{default_text}")
            else:
                action.setText(default_text)

    def set_window_icon(self, window, icon_name="favicon"):
        """设置窗口图标"""
        try:
            icon = self.get_icon(icon_name)
            if not icon.isNull():
                window.setWindowIcon(icon)
                print(f"窗口图标设置成功: {icon_name}")
                return True
            else:
                print(f"窗口图标设置失败，图标为空: {icon_name}")
                return False
        except Exception as e:
            print(f"设置窗口图标时出错: {e}")
            return False

    def set_action_icon(self, action, icon_name, fallback_text=""):
        """为动作设置图标，如果图标不存在则使用备选文本"""
        icon = self.get_icon(icon_name)
        if not icon.isNull():
            action.setIcon(icon)
            action.setIconText("")  # 清除图标文本
        elif fallback_text:
            action.setIconText(fallback_text)
        else:
            # 既没有图标也没有备选文本，清空图标
            action.setIcon(QIcon())

    def get_icon_with_fallback(self, icon_name, fallback_text=""):
        """获取图标，如果不存在则使用备选文本"""
        icon = self.get_icon(icon_name)
        if not icon.isNull():
            return icon, ""
        else:
            # 返回空图标和备选文本
            return QIcon(), fallback_text

    def get_pixmap(self, icon_name, size=(32, 32)):
        """获取像素图"""
        icon_path = self.get_icon_path(icon_name)
        if icon_path and os.path.exists(icon_path):
            try:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    return pixmap.scaled(size[0], size[1])
            except Exception as e:
                logger.error(f"像素图加载失败: {icon_name}, 错误: {e}")
        return QPixmap()

    def remove_icon_chars(self, text):
        """移除文本中的图标字符"""
        # 常见的图标Unicode字符
        icon_chars = ["🔒", "🔓", "🔄", "🚪", "➕", "🗑️",
                      "🔑", "📂", "🔐", "⚙️", "🌐", "🔗",
                      "👤", "📅", "📝"]
        clean_text = text
        for char in icon_chars:
            clean_text = clean_text.replace(char, "")
        return clean_text.strip()

    def test_all_icons(self):
        """测试所有图标"""
        print("\n=== 图标测试 ===")

        test_icons = [
            ('sync', '同步'),
            ('lock', '锁定'),
            ('unlock', '解锁'),
            ('exit', '退出'),
            ('add', '添加'),
            ('edit', '编辑'),
            ('delete', '删除'),
            ('key', '生成密码'),
            ('category', '管理分类'),
            ('admin_password', '修改密码'),
            ('settings', '设置'),
            ('favicon', '程序图标'),
        ]

        for icon_name, description in test_icons:
            icon_path = self.get_icon_path(icon_name)
            if icon_path and os.path.exists(icon_path):
                print(f"✅ {description} [{icon_name}] - 文件: {os.path.basename(icon_path)}")
            else:
                print(f"⚠️ {description} [{icon_name}] - 使用备用图标")

    def load_svg_icon(self, icon_name, default_size=(32, 32)):
        """加载SVG图标并将其转换为QIcon"""
        try:
            # 尝试获取SVG文件路径
            svg_path = self.get_icon_path(f"{icon_name}.svg")
            if svg_path and os.path.exists(svg_path):
                # 使用PIL将SVG转换为PNG
                from PIL import Image
                import cairosvg  # 需要安装 cairosvg: pip install cairosvg

                # 创建内存中的SVG转PNG
                png_data = cairosvg.svg2png(url=svg_path)

                # 创建QPixmap
                pixmap = QPixmap()
                pixmap.loadFromData(png_data)

                if not pixmap.isNull():
                    icon = QIcon(pixmap)
                    self.icon_cache[icon_name] = icon
                    return icon
        except ImportError:
            print("cairosvg 未安装，无法处理SVG图标")
        except Exception as e:
            print(f"SVG图标加载失败: {icon_name}, 错误: {e}")

        return QIcon()

    def get_icon_enhanced(self, icon_name, prefer_svg=False):
        """获取图标 - 增强版本，支持SVG优先"""
        # 检查缓存
        if icon_name in self.icon_cache:
            return self.icon_cache[icon_name]

        # 根据偏好选择加载方式
        if prefer_svg:
            # 优先尝试SVG
            icon = self.load_svg_icon(icon_name)
            if not icon.isNull():
                return icon

        # 回退到原来的图标加载逻辑
        return self.get_icon(icon_name)

    def create_icon_from_svg(self, icon_name, svg_content=None, size=(32, 32)):
        """从SVG内容创建图标"""
        try:
            if svg_content:
                # 使用cairosvg转换SVG内容
                import cairosvg
                png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))

                pixmap = QPixmap()
                pixmap.loadFromData(png_data)

                if not pixmap.isNull():
                    # 缩放
                    scaled_pixmap = pixmap.scaled(size[0], size[1],
                                                  Qt.AspectRatioMode.KeepAspectRatio,
                                                  Qt.TransformationMode.SmoothTransformation)
                    icon = QIcon(scaled_pixmap)
                    self.icon_cache[icon_name] = icon
                    return icon
        except Exception as e:
            print(f"从SVG创建图标失败: {e}")

        return self.create_simple_icon(icon_name)

    def verify_all_icons_with_svg(self):
        """验证所有图标，包括SVG支持"""
        print("\n=== 图标系统状态报告 ===")

        # 检查PIL和cairosvg支持
        try:
            from PIL import Image
            print("✅ PIL (Pillow) 已安装")
        except ImportError:
            print("❌ PIL (Pillow) 未安装，部分图标功能可能受限")

        try:
            import cairosvg
            print("✅ cairosvg 已安装")
        except ImportError:
            print("⚠️  cairosvg 未安装，SVG图标支持受限")

        # 测试关键图标
        key_icons = [
            ('favicon', '程序图标'),
            ('lock', '锁定'),
            ('unlock', '解锁'),
            ('add', '添加'),
            ('edit', '编辑'),
            ('delete', '删除'),
        ]

        for icon_name, description in key_icons:
            # 尝试不同格式
            formats = ['svg', 'ico', 'png']
            found = False

            for fmt in formats:
                path = self.get_icon_path(f"{icon_name}.{fmt}")
                if path and os.path.exists(path):
                    print(f"✅ {description} - 找到 .{fmt} 格式")
                    found = True
                    break

            if not found:
                print(f"❌ {description} - 未找到任何格式")

        # 检查图标缓存状态
        print(f"\n图标缓存: {len(self.icon_cache)} 个图标已缓存")

        return True


# 全局图标管理器实例
_icon_manager = None


def get_icon_manager():
    """获取全局图标管理器实例"""
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager()
    return _icon_manager