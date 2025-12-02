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
验证图标文件
"""
import os
import sys
from pathlib import Path
from PIL import Image


def verify_icon_file(filepath):
    """验证单个图标文件"""
    if not os.path.exists(filepath):
        return False, "文件不存在"

    try:
        with Image.open(filepath) as img:
            info = {
                'exists': True,
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'filesize': os.path.getsize(filepath),
            }

            # 检查多帧（ICO文件）
            if hasattr(img, 'n_frames') and img.n_frames > 1:
                info['frames'] = img.n_frames
                info['sizes'] = []

                for i in range(img.n_frames):
                    try:
                        img.seek(i)
                        info['sizes'].append(img.size)
                    except EOFError:
                        break
            else:
                info['frames'] = 1

            return True, info

    except Exception as e:
        return False, str(e)


def main():
    project_root = Path(__file__).parent.parent
    icons_dir = project_root / "resources" / "icons"

    if not icons_dir.exists():
        print(f"❌ 图标目录不存在: {icons_dir}")
        return

    print("=== 图标文件验证 ===")
    print(f"图标目录: {icons_dir}")

    # 检查所有图标文件
    icon_files = list(icons_dir.glob("*.*"))

    if not icon_files:
        print("❌ 没有找到图标文件")
        return

    for icon_file in icon_files:
        if icon_file.is_file():
            print(f"\n📄 {icon_file.name}:")

            success, result = verify_icon_file(icon_file)

            if success:
                info = result
                print(f"  ✅ 格式: {info['format']}")
                print(f"     模式: {info['mode']}")
                print(f"     尺寸: {info['size']}")
                print(f"     大小: {info['filesize']:,} 字节")

                if 'frames' in info and info['frames'] > 1:
                    print(f"     帧数: {info['frames']}")
                    if 'sizes' in info:
                        print(f"     包含尺寸: {', '.join(f'{w}x{h}' for w, h in info['sizes'])}")
            else:
                print(f"  ❌ 错误: {result}")

    # 检查必需的图标
    print("\n=== 必需图标检查 ===")

    required = [
        'favicon.ico',
        'sync.png',
        'lock.png',
        'unlock.png',
        'add.png',
        'edit.png',
        'delete.png',
    ]

    for req in required:
        req_path = icons_dir / req
        if req_path.exists():
            print(f"✅ {req}")
        else:
            print(f"❌ {req} - 缺失")


if __name__ == "__main__":
    main()