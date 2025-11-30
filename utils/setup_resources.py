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
        resources_dir / 'icons'
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


if __name__ == "__main__":
    setup_resources()