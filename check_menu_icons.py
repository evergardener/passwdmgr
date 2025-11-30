# -*- coding: utf-8 -*-
#
# @Created : 2025-11-30 14:50
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    : 检查菜单图标状态
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.icon_manager import get_icon_manager


def check_menu_icons_final():
    """检查菜单所需的所有图标"""
    icon_manager = get_icon_manager()

    # 菜单所需的图标列表
    menu_icons = {
        "lock": "锁定",
        "unlock": "解锁",
        "sync": "同步",
        "add": "添加",
        "edit": "编辑",
        "delete": "删除",
        "key": "生成密码",
        "category": "管理分类",
        "admin_password": "修改密码",
        "settings": "设置",
        "exit": "退出",
        "quit": "退出(备选)",
        "close": "关闭(备选)"
    }

    print("=== 最终菜单图标检查 ===")
    print(f"图标目录: {icon_manager.base_path}/resources/icons/")
    print()

    available_icons = []
    missing_icons = []

    for icon_name, description in menu_icons.items():
        icon_path = icon_manager.find_icon_file(icon_name)
        if icon_path:
            status = "✅"
            available_icons.append((icon_name, description, icon_path))
        else:
            status = "❌"
            missing_icons.append((icon_name, description))

        print(f"{status} {description:15} [{icon_name}]")

    print(f"\n总结: {len(available_icons)} 个可用, {len(missing_icons)} 个缺失")

    if missing_icons:
        print("\n缺失的图标:")
        for icon_name, description in missing_icons:
            print(f"  - {description} [{icon_name}.png 或 {icon_name}.ico]")

        print(f"\n建议:")
        print("1. 将图标文件放入 resources/icons/ 目录")
        print("2. 使用 PNG 格式 (推荐 16x16 或 32x32 像素)")
        print("3. 系统将自动使用文本替代缺失的图标")


if __name__ == "__main__":
    check_menu_icons_final()