# -*- coding: utf-8 -*-
#
# @Created : 2025-12-01 23:59
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    :
# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建 Windows 兼容的图标
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class WindowsIconCreator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.icons_dir = self.project_root / "resources" / "icons"
        self.icons_dir.mkdir(parents=True, exist_ok=True)

    def create_favicon_ico(self):
        """创建 Windows 兼容的 favicon.ico"""
        print("创建 Windows 兼容的 favicon.ico...")

        # Windows 推荐的尺寸
        sizes = [
            (16, 16),
            (32, 32),
            (48, 48),
            (64, 64),
            (128, 128),
            (256, 256)
        ]

        images = []

        for width, height in sizes:
            # 创建新图像
            img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)

            # 绘制锁图标（简单版本）
            self.draw_lock_icon(draw, width, height)

            images.append(img)
            print(f"  创建 {width}x{height} 图像")

        # 保存为 ICO
        ico_path = self.icons_dir / "favicon.ico"
        images[0].save(
            ico_path,
            format='ICO',
            sizes=sizes,
            append_images=images[1:]
        )

        print(f"\n✅ favicon.ico 已创建: {ico_path}")
        print(f"   文件大小: {ico_path.stat().st_size:,} 字节")

        # 验证
        self.verify_icon(ico_path, "favicon")

        return ico_path

    def draw_lock_icon(self, draw, width, height):
        """绘制锁图标"""
        # 计算位置和大小
        padding = max(2, width // 8)
        lock_width = width - padding * 2
        lock_height = height - padding * 2

        x = padding
        y = padding

        # 锁体颜色
        lock_color = (0, 120, 215, 255)  # Windows 蓝色

        # 绘制锁体（圆角矩形）
        corner_radius = min(lock_width, lock_height) // 4

        # 锁体主体
        draw.rounded_rectangle(
            [x, y + lock_height * 0.3, x + lock_width, y + lock_height],
            radius=corner_radius,
            fill=lock_color
        )

        # 锁顶（弧形）
        draw.ellipse(
            [x, y, x + lock_width, y + lock_height * 0.6],
            fill=lock_color
        )

        # 锁孔
        hole_size = lock_width * 0.3
        hole_x = x + (lock_width - hole_size) / 2
        hole_y = y + lock_height * 0.5

        draw.ellipse(
            [hole_x, hole_y, hole_x + hole_size, hole_y + hole_size],
            fill=(255, 255, 255, 255)
        )

    def create_menu_icons(self):
        """创建菜单图标"""
        print("\n创建菜单图标...")

        menu_icons = {
            'add': '➕',
            'edit': '✏️',
            'delete': '🗑️',
            'sync': '🔄',
            'lock': '🔒',
            'unlock': '🔓',
            'key': '🔑',
            'category': '📁',
            'admin_password': '🔐',
            'settings': '⚙️',
            'exit': '🚪',
        }

        # 图标尺寸
        sizes = [32, 48, 64]

        for icon_name, symbol in menu_icons.items():
            print(f"  创建 {icon_name}.png")

            for size in sizes:
                # 创建图像
                img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img)

                # 绘制彩色背景
                colors = {
                    'add': (76, 175, 80),  # 绿色
                    'edit': (33, 150, 243),  # 蓝色
                    'delete': (244, 67, 54),  # 红色
                    'sync': (156, 39, 176),  # 紫色
                    'lock': (255, 152, 0),  # 橙色
                    'unlock': (76, 175, 80),  # 绿色
                    'key': (255, 193, 7),  # 黄色
                    'category': (0, 188, 212),  # 青色
                    'admin_password': (63, 81, 181),  # 深蓝
                    'settings': (158, 158, 158),  # 灰色
                    'exit': (96, 125, 139),  # 蓝灰
                }

                color = colors.get(icon_name, (96, 125, 139))

                # 绘制圆形背景
                draw.ellipse([0, 0, size, size], fill=color)

                # 添加符号（使用Unicode字符）
                try:
                    # 尝试加载字体
                    font_path = self.find_font()
                    if font_path:
                        font_size = size // 2
                        font = ImageFont.truetype(font_path, font_size)
                    else:
                        font = ImageFont.load_default()
                        font_size = size // 2
                except:
                    font = ImageFont.load_default()
                    font_size = size // 2

                # 绘制符号
                bbox = draw.textbbox((0, 0), symbol, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                text_x = (size - text_width) // 2
                text_y = (size - text_height) // 2

                draw.text((text_x, text_y), symbol, font=font, fill=(255, 255, 255, 255))

                # 保存PNG
                if size == 32:  # 只保存32x32版本
                    png_path = self.icons_dir / f"{icon_name}.png"
                    img.save(png_path, format='PNG')

        print("✅ 菜单图标创建完成")

    def find_font(self):
        """查找可用字体"""
        font_paths = [
            "C:/Windows/Fonts/segoeui.ttf",  # Windows 10/11
            "C:/Windows/Fonts/arial.ttf",  # Arial
            "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        ]

        for path in font_paths:
            if os.path.exists(path):
                return path

        return None

    def verify_icon(self, icon_path, icon_name):
        """验证图标文件"""
        try:
            with Image.open(icon_path) as img:
                print(f"\n验证 {icon_name}:")
                print(f"  格式: {img.format}")
                print(f"  模式: {img.mode}")
                print(f"  尺寸: {img.size}")

                # 检查是否是多帧（多个尺寸）
                if hasattr(img, 'n_frames'):
                    print(f"  帧数: {img.n_frames}")

                    # 查看所有帧的尺寸
                    for i in range(img.n_frames):
                        img.seek(i)
                        print(f"    帧 {i}: {img.size}")
                else:
                    print("  单帧图像")

        except Exception as e:
            print(f"验证失败: {e}")

    def check_existing_icons(self):
        """检查现有图标"""
        print("\n=== 现有图标检查 ===")

        required_icons = [
            ('favicon.ico', '程序图标'),
            ('sync.png', '同步'),
            ('lock.png', '锁定'),
            ('unlock.png', '解锁'),
            ('add.png', '添加'),
            ('edit.png', '编辑'),
            ('delete.png', '删除'),
            ('key.png', '生成密码'),
            ('category.png', '管理分类'),
            ('admin_password.png', '修改密码'),
            ('settings.png', '设置'),
            ('exit.png', '退出'),
        ]

        missing = []

        for filename, description in required_icons:
            icon_path = self.icons_dir / filename
            if icon_path.exists():
                size = icon_path.stat().st_size
                print(f"✅ {description} ({filename}) - {size:,} 字节")
            else:
                print(f"❌ {description} ({filename}) - 缺失")
                missing.append((filename, description))

        return missing

    def run(self):
        """运行图标创建工具"""
        print("=" * 60)
        print("Windows 图标创建工具")
        print("=" * 60)

        # 检查现有图标
        missing = self.check_existing_icons()

        if missing:
            print(f"\n缺失 {len(missing)} 个图标")

            # 创建缺失的图标
            create_all = input("\n是否创建所有缺失的图标？(y/n): ").strip().lower()

            if create_all == 'y':
                # 创建 favicon.ico
                if any('favicon.ico' == filename for filename, _ in missing):
                    self.create_favicon_ico()

                # 创建菜单图标
                if any('.png' in filename for filename, _ in missing):
                    self.create_menu_icons()

                print("\n✅ 图标创建完成！")
            else:
                print("取消创建")
        else:
            print("\n✅ 所有图标都已存在")

            # 仍然可以重新创建
            recreate = input("是否重新创建所有图标？(y/n): ").strip().lower()
            if recreate == 'y':
                self.create_favicon_ico()
                self.create_menu_icons()
                print("\n✅ 图标已重新创建")


if __name__ == "__main__":
    creator = WindowsIconCreator()
    creator.run()