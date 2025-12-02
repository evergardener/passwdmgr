# -*- coding: utf-8 -*-
#
# @Created : 2025-11-30 13:28
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    :
import os
import sys
from pathlib import Path
class ResourceManager:
    """资源管理器"""

    def __init__(self, base_path=None):
        self.base_path = base_path or self.get_base_path()
        self.resource_cache = {}
        print(f"资源管理器初始化，基础路径: {self.base_path}")

    def get_base_path(self):
        """获取项目根目录路径"""
        # 尝试多种方式获取项目根目录
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            base_dir = Path(sys.executable).parent
        else:
            # 开发环境
            base_dir = Path(__file__).parent.parent

        # 检查是否存在 resources 目录
        resources_dir = base_dir / 'resources'
        if resources_dir.exists():
            return str(resources_dir)
        else:
            # 如果没有 resources 目录，使用项目根目录
            return str(base_dir)

    def get_resource_path(self, relative_path):
        """获取资源文件的绝对路径（兼容打包和开发环境）"""
        # 尝试多种路径方案

        # 方案1: 如果是打包环境
        if getattr(sys, 'frozen', False):
            # 首先尝试从 _MEIPASS 获取
            base_path = getattr(sys, '_MEIPASS', '')
            if base_path:
                path = os.path.join(base_path, relative_path)
                if os.path.exists(path):
                    return path

        # 方案2: 从当前工作目录获取
        cwd_path = os.path.join(os.getcwd(), relative_path)
        if os.path.exists(cwd_path):
            return cwd_path

        # 方案3: 从项目根目录获取
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_path = os.path.join(project_root, relative_path)
        if os.path.exists(project_path):
            return project_path

        # 方案4: 从exe所在目录获取
        if getattr(sys, 'frozen', False) and hasattr(sys, 'executable'):
            exe_dir = os.path.dirname(sys.executable)
            exe_path = os.path.join(exe_dir, relative_path)
            if os.path.exists(exe_path):
                return exe_path

        # 如果都没找到，返回None
        print(f"警告: 未找到资源文件: {relative_path}")
        return None

    def load_resource(self, relative_path):
        """加载资源文件内容"""
        cache_key = relative_path

        if cache_key in self.resource_cache:
            return self.resource_cache[cache_key]

        resource_path = self.get_resource_path(relative_path)
        if resource_path:
            try:
                with open(resource_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.resource_cache[cache_key] = content
                    print(f"资源文件加载成功: {relative_path}")
                    return content
            except Exception as e:
                print(f"加载资源文件失败: {relative_path}, 错误: {e}")
                return None
        else:
            return None

    def get_template(self, template_name):
        """获取模板内容"""
        template_path = f"templates/{template_name}"
        return self.load_resource(template_path)

    def get_style(self, style_name):
        """获取样式内容"""
        style_path = f"styles/{style_name}"
        return self.load_resource(style_path)


# 全局资源管理器实例
_resource_manager = None


def get_resource_manager():
    """获取全局资源管理器实例"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager