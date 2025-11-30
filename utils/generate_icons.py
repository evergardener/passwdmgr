# -*- coding: utf-8 -*-
#
# @Created : 2025-11-30 13:18
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    : 图标格式转换工具
import os
import shutil
from pathlib import Path
from PIL import Image


class IconManagerTool:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.icons_dir = self.project_root / "resources" / "icons"
        self.icons_dir.mkdir(parents=True, exist_ok=True)

    def setup_icon_structure(self):
        """设置图标目录结构"""
        print("设置图标目录结构...")

        # 创建标准图标目录
        (self.icons_dir / "small").mkdir(exist_ok=True)  # 小图标 (16x16, 32x32)
        (self.icons_dir / "medium").mkdir(exist_ok=True)  # 中等图标 (48x48, 64x64)
        (self.icons_dir / "large").mkdir(exist_ok=True)  # 大图标 (128x128, 256x256)

        print(f"图标目录已创建: {self.icons_dir}")

        # 列出当前图标
        self.list_current_icons()

    def list_current_icons(self):
        """列出当前图标"""
        print("\n当前图标文件:")
        icon_files = list(self.icons_dir.glob("*.*"))
        if not icon_files:
            print("  没有找到图标文件")
            return

        for icon_file in icon_files:
            if icon_file.is_file():
                size = icon_file.stat().st_size
                print(f"  📄 {icon_file.name} ({size} bytes)")

    def generate_icon_sizes(self, source_image, icon_name):
        """从源图像生成多种尺寸的图标"""
        if not source_image.exists():
            print(f"错误: 源图像不存在: {source_image}")
            return

        try:
            with Image.open(source_image) as img:
                # 生成不同尺寸
                sizes = {
                    "small": [(16, 16), (32, 32)],
                    "medium": [(48, 48), (64, 64)],
                    "large": [(128, 128), (256, 256)]
                }

                for size_category, dimensions in sizes.items():
                    for width, height in dimensions:
                        # 调整尺寸
                        resized = img.resize((width, height), Image.Resampling.LANCZOS)

                        # 保存为PNG
                        png_path = self.icons_dir / size_category / f"{icon_name}_{width}x{height}.png"
                        resized.save(png_path, format='PNG')
                        print(f"生成: {png_path.relative_to(self.project_root)}")

                # 生成ICO格式（Windows图标）
                ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
                ico_images = [img.resize(size, Image.Resampling.LANCZOS) for size in ico_sizes]

                ico_path = self.icons_dir / f"{icon_name}.ico"
                ico_images[0].save(ico_path, format='ICO', sizes=ico_sizes)
                print(f"生成: {ico_path.relative_to(self.project_root)}")

        except Exception as e:
            print(f"图标生成失败: {e}")

    def check_required_icons(self):
        """检查必需的图标"""
        required_icons = [
            "favicon.ico",
            "lock.png",
            "unlock.png",
            "add.png",
            "edit.png",
            "delete.png"
        ]

        print("\n必需图标检查:")
        missing_icons = []

        for icon_file in required_icons:
            icon_path = self.icons_dir / icon_file
            if icon_path.exists():
                print(f"  ✅ {icon_file}")
            else:
                print(f"  ❌ {icon_file}")
                missing_icons.append(icon_file)

        if missing_icons:
            print(f"\n缺少 {len(missing_icons)} 个图标:")
            for missing in missing_icons:
                print(f"  - {missing}")
        else:
            print("\n所有必需图标都已存在!")


def main():
    tool = IconManagerTool()

    print("=== 图标管理工具 ===")
    print("1. 设置图标目录结构")
    print("2. 列出当前图标")
    print("3. 检查必需图标")
    print("4. 从源图像生成图标")

    choice = input("请选择操作 (1-4): ").strip()

    if choice == "1":
        tool.setup_icon_structure()
    elif choice == "2":
        tool.list_current_icons()
    elif choice == "3":
        tool.check_required_icons()
    elif choice == "4":
        source_path = input("输入源图像路径: ").strip()
        icon_name = input("输入图标名称: ").strip()
        tool.generate_icon_sizes(Path(source_path), icon_name)
    else:
        print("无效选择")


if __name__ == "__main__":
    main()