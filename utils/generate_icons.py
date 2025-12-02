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
        """从源图像生成多种尺寸的图标 - 修复版"""
        if not source_image.exists():
            print(f"错误: 源图像不存在: {source_image}")
            return

        try:
            with Image.open(source_image) as img:
                # 确保源图像是RGBA模式（支持透明）
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                print(f"源图像: {img.size}, 模式: {img.mode}")

                # 生成不同尺寸的PNG
                sizes = {
                    "small": [(16, 16), (32, 32)],
                    "medium": [(48, 48), (64, 64)],
                    "large": [(128, 128), (256, 256)]
                }

                for size_category, dimensions in sizes.items():
                    category_dir = self.icons_dir / size_category
                    category_dir.mkdir(exist_ok=True)

                    for width, height in dimensions:
                        # 调整尺寸
                        resized = img.resize((width, height), Image.Resampling.LANCZOS)

                        # 保存为PNG
                        png_path = category_dir / f"{icon_name}_{width}x{height}.png"
                        resized.save(png_path, format='PNG')
                        print(f"生成PNG: {png_path.relative_to(self.project_root)}")

                # 生成ICO格式（Windows图标）- 修复版
                ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

                # 创建一个列表保存所有尺寸的图像
                ico_images = []
                for size in ico_sizes:
                    # 调整尺寸，确保高质量
                    resized = img.resize(size, Image.Resampling.LANCZOS)
                    ico_images.append(resized)

                # 保存ICO文件 - 使用第一张图作为基础，附加其他尺寸
                ico_path = self.icons_dir / f"{icon_name}.ico"

                if ico_images:
                    # 方法1：保存所有尺寸到同一个ICO
                    ico_images[0].save(
                        ico_path,
                        format='ICO',
                        sizes=ico_sizes,
                        append_images=ico_images[1:] if len(ico_images) > 1 else []
                    )
                    print(f"生成ICO: {ico_path.relative_to(self.project_root)}")

                    # 验证ICO文件
                    self.verify_ico_file(ico_path, icon_name)

        except Exception as e:
            print(f"图标生成失败: {e}")
            import traceback
            traceback.print_exc()

    def verify_ico_file(self, ico_path, icon_name):
        """验证ICO文件"""
        if not ico_path.exists():
            print(f"警告: ICO文件不存在: {ico_path}")
            return

        try:
            with Image.open(ico_path) as img:
                print(f"验证 {icon_name}.ico:")
                print(f"  格式: {img.format}")
                print(f"  模式: {img.mode}")
                print(f"  文件大小: {ico_path.stat().st_size} 字节")

                # 检查是否包含多个尺寸
                if hasattr(img, 'n_frames') and img.n_frames > 1:
                    print(f"  包含 {img.n_frames} 个尺寸")
                else:
                    print("  警告: 可能只包含一个尺寸")
        except Exception as e:
            print(f"验证ICO文件失败: {e}")

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