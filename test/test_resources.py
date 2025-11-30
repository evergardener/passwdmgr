# -*- coding: utf-8 -*-
#
# @Created : 2025-11-30 13:43
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    :
# debug_resources.py
import os
import sys
from pathlib import Path


def debug_resources():
    """调试资源文件"""
    # 获取项目根目录
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent.parent
    else:
        base_dir = Path(__file__).parent.parent

    print(f"项目根目录: {base_dir}")
    print("\n目录结构:")

    # 列出重要目录
    important_dirs = ['', 'resources', 'resources/icons', 'resources/templates', 'resources/css', 'imgs']

    for dir_name in important_dirs:
        dir_path = base_dir / dir_name if dir_name else base_dir
        print(f"\n{dir_path}:")
        if dir_path.exists():
            try:
                items = os.listdir(dir_path)
                # for item in items[:20]:  # 只显示前20个
                for item in items:
                    full_path = dir_path / item
                    if full_path.is_file():
                        size = full_path.stat().st_size
                        file_type = "图标" if item.lower().endswith(('.ico', '.png', '.svg')) else "文件"
                        print(f"  📄 {item} ({size} bytes) - {file_type}")
                    else:
                        print(f"  📁 {item}/")
                if len(items) > 20:
                    print(f"  ... 还有 {len(items) - 20} 个文件")
            except Exception as e:
                print(f"  无法访问: {e}")
        else:
            print("  目录不存在")

        # 检查常见的图标文件
        print("\n查找特定图标文件:")
        icon_names = ['favicon', 'icon', 'app', 'logo', 'lock', 'unlock', 'add', 'edit', 'delete']
        found_icons = []

        for name in icon_names:
            # 在 resources/icons 中查找
            for ext in ['.ico', '.png', '.svg']:
                icon_path = base_dir / "resources" / "icons" / f"{name}{ext}"
                if icon_path.exists():
                    found_icons.append((name, icon_path))
                    print(f"  ✅ 找到: {icon_path.relative_to(base_dir)}")
                    break
            else:
                # 在其他位置查找
                for check_dir in ['img', 'resources', '']:
                    for ext in ['.ico', '.png', '.svg']:
                        check_path = base_dir / check_dir / f"{name}{ext}"
                        if check_path.exists():
                            found_icons.append((name, check_path))
                            print(f"  ✅ 找到: {check_path.relative_to(base_dir)}")
                            break

        if not found_icons:
            print("  ❌ 未找到任何图标文件")

        # 测试图标管理器
        print("\n=== 图标管理器测试 ===")
        try:
            from gui.icon_manager import IconManager
            icon_manager = IconManager()

            test_icons = ['favicon', 'icon']
            for test_icon in test_icons:
                icon_path = icon_manager.find_icon_file(test_icon)
                if icon_path:
                    print(f"  ✅ 图标管理器找到: {test_icon} -> {icon_path}")
                else:
                    print(f"  ❌ 图标管理器未找到: {test_icon}")

        except Exception as e:
            print(f"  图标管理器测试失败: {e}")


if __name__ == "__main__":
    debug_resources()