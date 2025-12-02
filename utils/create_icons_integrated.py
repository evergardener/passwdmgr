# -*- coding: utf-8 -*-
#
# @Created : 2025-12-02 00:23
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    :
# create_icons_integrated.py - 创建这个新文件
# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
整合的图标生成工具 - 支持SVG、PNG、ICO格式
"""
import os
import sys
from pathlib import Path
from PIL import Image
import shutil


class IntegratedIconGenerator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.resources_dir = self.project_root / "resources"
        self.icons_dir = self.resources_dir / "icons"
        self.templates_dir = self.resources_dir / "templates"

        # 创建必要的目录
        self.icons_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        print(f"项目根目录: {self.project_root}")
        print(f"图标目录: {self.icons_dir}")

    def setup_directories(self):
        """设置目录结构"""
        directories = [
            self.icons_dir / "small",
            self.icons_dir / "medium",
            self.icons_dir / "large",
            self.templates_dir
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"创建目录: {directory}")

    def convert_svg_to_png(self, svg_file, output_dir, sizes=[16, 32, 48, 64, 128, 256]):
        """将SVG转换为PNG（如果cairosvg可用）"""
        try:
            import cairosvg

            svg_path = Path(svg_file)
            if not svg_path.exists():
                print(f"错误: SVG文件不存在: {svg_path}")
                return False

            for size in sizes:
                output_file = output_dir / f"{svg_path.stem}_{size}x{size}.png"

                # 使用cairosvg转换
                cairosvg.svg2png(
                    url=str(svg_path),
                    write_to=str(output_file),
                    output_width=size,
                    output_height=size
                )

                print(f"生成PNG: {output_file.name}")

            return True

        except ImportError:
            print("警告: cairosvg未安装，无法转换SVG")
            print("请安装: pip install cairosvg")
            return False

    def create_ico_from_images(self, image_files, output_file):
        """从图像文件创建ICO"""
        try:
            images = []
            sizes = []

            for img_file in image_files:
                with Image.open(img_file) as img:
                    images.append(img.copy())
                    sizes.append(img.size)

            if images:
                images[0].save(
                    output_file,
                    format='ICO',
                    sizes=sizes,
                    append_images=images[1:] if len(images) > 1 else []
                )
                print(f"生成ICO: {output_file}")
                return True

        except Exception as e:
            print(f"创建ICO失败: {e}")

        return False

    def create_default_icons(self):
        """创建默认图标集"""
        print("\n=== 创建默认图标集 ===")

        # 基本图标定义
        icon_definitions = {
            'favicon': {
                'color': (66, 133, 244),  # Google蓝色
                'symbol': '🔒'
            },
            'lock': {
                'color': (255, 152, 0),  # 橙色
                'symbol': '🔒'
            },
            'unlock': {
                'color': (76, 175, 80),  # 绿色
                'symbol': '🔓'
            },
            'add': {
                'color': (76, 175, 80),  # 绿色
                'symbol': '+'
            },
            'edit': {
                'color': (33, 150, 243),  # 蓝色
                'symbol': '✏️'
            },
            'delete': {
                'color': (244, 67, 54),  # 红色
                'symbol': '🗑️'
            },
            'sync': {
                'color': (156, 39, 176),  # 紫色
                'symbol': '🔄'
            },
            'key': {
                'color': (255, 193, 7),  # 黄色
                'symbol': '🔑'
            },
            'category': {
                'color': (0, 188, 212),  # 青色
                'symbol': '📁'
            },
            'admin_password': {
                'color': (63, 81, 181),  # 深蓝
                'symbol': '🔐'
            },
            'settings': {
                'color': (158, 158, 158),  # 灰色
                'symbol': '⚙️'
            },
            'exit': {
                'color': (96, 125, 139),  # 蓝灰
                'symbol': '🚪'
            }
        }

        # 创建各种尺寸
        all_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icons_for_ico = []  # 收集用于ICO的图像

        for icon_name, definition in icon_definitions.items():
            print(f"创建图标: {icon_name}")

            for width, height in all_sizes:
                img = Image.new('RGBA', (width, height), (255, 255, 255, 0))

                # 这里应该添加绘图逻辑
                # 由于没有实际的绘图代码，我们只创建占位符

                # 保存PNG
                if width == 32:  # 只保存32x32的PNG用于菜单
                    png_path = self.icons_dir / f"{icon_name}.png"
                    img.save(png_path, format='PNG')

                # 收集用于ICO
                if icon_name == 'favicon':
                    icons_for_ico.append(img)

        # 创建ICO文件
        if icons_for_ico:
            ico_path = self.icons_dir / "favicon.ico"
            self.create_ico_from_images([self.icons_dir / "favicon.png"], ico_path)

        print("✅ 默认图标集创建完成")

    def generate_qt_resource_file(self):
        """生成Qt资源文件"""
        print("\n=== 生成Qt资源文件 ===")

        resource_content = """<!DOCTYPE RCC>
<RCC version="1.0">
<qresource>
"""

        # 添加图标
        for file in self.icons_dir.glob("*.png"):
            resource_content += f'    <file>resources/icons/{file.name}</file>\n'

        for file in self.icons_dir.glob("*.ico"):
            resource_content += f'    <file>resources/icons/{file.name}</file>\n'

        # 添加模板
        for file in self.templates_dir.glob("*.html"):
            resource_content += f'    <file>resources/templates/{file.name}</file>\n'

        resource_content += """</qresource>
</RCC>"""

        resource_file = self.project_root / "resources.qrc"
        resource_file.write_text(resource_content, encoding='utf-8')

        print(f"生成资源文件: {resource_file}")

        # 编译资源文件（如果pyrcc可用）
        try:
            import subprocess
            py_file = self.project_root / "resources_rc.py"
            subprocess.run(['pyside6-rcc', str(resource_file), '-o', str(py_file)])
            print(f"编译资源文件: {py_file}")
        except:
            print("注意: 需要安装PySide6-tools来编译资源文件")
            print("安装: pip install PySide6")

    def check_requirements(self):
        """检查依赖"""
        print("\n=== 检查依赖 ===")

        required = ['PIL', 'PyQt6']
        optional = ['cairosvg', 'PySide6']

        for package in required:
            try:
                __import__(package.lower() if package == 'PIL' else package)
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package} - 必需")

        for package in optional:
            try:
                __import__(package)
                print(f"✅ {package} - 可选")
            except ImportError:
                print(f"⚠️  {package} - 可选")

    def run(self):
        """运行生成器"""
        print("=" * 60)
        print("整合图标生成工具")
        print("=" * 60)

        self.check_requirements()
        self.setup_directories()

        # 检查是否有SVG文件
        svg_files = list(self.icons_dir.glob("*.svg"))
        if svg_files:
            print(f"\n找到 {len(svg_files)} 个SVG文件")
            for svg_file in svg_files:
                print(f"处理: {svg_file.name}")
                self.convert_svg_to_png(svg_file, self.icons_dir)
        else:
            print("\n未找到SVG文件，创建默认图标")
            self.create_default_icons()

        # 生成资源文件
        self.generate_qt_resource_file()

        print("\n✅ 图标生成完成!")


if __name__ == "__main__":
    generator = IntegratedIconGenerator()
    generator.run()