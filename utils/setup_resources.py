# -*- coding: utf-8 -*-
#
# @Created : 2025-11-30 13:31
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    :
import os
import shutil
from pathlib import Path


def setup_resources():
    """设置资源文件结构"""
    project_root = Path(__file__).parent.parent
    resources_dir = project_root / 'resources'

    # 创建目录结构
    directories = [
        resources_dir / 'templates',
        resources_dir / 'css',
        resources_dir / 'icons',
        resources_dir / 'icons/small',
        resources_dir / 'icons/medium',
        resources_dir / 'icons/large',
        resources_dir / 'icons/svg'  # 新增SVG目录
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"创建目录: {directory}")


    # 创建示例文件
    template_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="styles/detail_style.css">
</head>
<body>
    <div id="content">
        <!-- 模板内容 -->
    </div>
</body>
</html>"""

    style_content = """/* 样式文件 */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}"""

    # 写入示例文件
    template_file = resources_dir / 'templates' / 'example_template.html'
    style_file = resources_dir / 'styles' / 'example_style.css'

    template_file.write_text(template_content, encoding='utf-8')
    style_file.write_text(style_content, encoding='utf-8')

    print(f"创建示例模板: {template_file}")
    print(f"创建示例样式: {style_file}")
    print("资源文件结构设置完成！")


def create_default_svg_icons(self):
    """创建默认的SVG图标"""
    svg_dir = self.resources_dir / 'icons' / 'svg'
    svg_dir.mkdir(exist_ok=True)

    # 简单的锁图标SVG
    lock_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
    <rect x="6" y="14" width="20" height="14" rx="3" fill="#2196F3"/>
    <path d="M11 14V9C11 5.68629 13.6863 3 17 3C20.3137 3 23 5.68629 23 9V14" stroke="#1565C0" stroke-width="2"/>
    <circle cx="16" cy="19" r="3" fill="white"/>
</svg>"""

    (svg_dir / "lock.svg").write_text(lock_svg, encoding='utf-8')
    print("创建默认SVG图标")

if __name__ == "__main__":
    setup_resources()