#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:01
# @Updated: 2025/11/27 8:01
# @Python:  3.12
# @Description:
import json
import os
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "database": {
                "use_sqlite": True,
                "sqlite_path": "password_manager.db",
                "host": "localhost",
                "port": 3306,
                "database": "password_manager",
                "username": "",
                "password": "",
                "use_ssl": False
            },
            "security": {
                "auto_lock_minutes": 15,
                "clear_clipboard_seconds": 30
            },
            "ui": {
                "theme": "light",
                "window_width": 1000,
                "window_height": 600
            },
            "categories": [  # 新增分类配置
                "默认",
                "工作",
                "个人",
                "金融",
                "社交",
                "邮箱",
                "购物",
                "娱乐",
                "教育",
                "其他"
            ]
        }

        try:
            if os.path.exists(self.config_file):
                print(f"正在读取配置文件: {self.config_file}")
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    print(f"读取到的配置: {json.dumps(loaded_config, indent=2)}")

                    # 确保数据库配置有 use_sqlite 字段
                    if 'database' in loaded_config and 'use_sqlite' not in loaded_config['database']:
                        loaded_config['database']['use_sqlite'] = True

                    # 合并配置，确保新字段有默认值
                    self._merge_config(default_config, loaded_config)

                    print(f"合并后的配置: {json.dumps(default_config, indent=2)}")
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            logger.error(f"加载配置文件失败: {e}")

        return default_config

    def _merge_config(self, default: Dict, loaded: Dict):
        """递归合并配置"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info("配置保存成功")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.config.get("database", {})

    def update_database_config(self, config: Dict[str, Any]):
        """更新数据库配置"""
        self.config["database"] = config
        self.save_config()

    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self.config.get("security", {})

    def update_security_config(self, config: Dict[str, Any]):
        """更新安全配置"""
        self.config["security"] = config
        self.save_config()

    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        return self.config.get("ui", {})

    def update_ui_config(self, config: Dict[str, Any]):
        """更新UI配置"""
        self.config["ui"] = config
        self.save_config()

    def get_categories_config(self) -> List[str]:
        """获取分类配置"""
        return self.config.get("categories", [])

    def update_categories_config(self, categories: List[str]):
        """更新分类配置"""
        self.config["categories"] = categories
        self.save_config()

