#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:03
# @Updated: 2025/11/27 8:03
# @Python:  3.12
# @Description:
# core/database_manager.py
# 完整的 core/database_manager.py
import sqlite3
import mysql.connector
from mysql.connector import Error
from typing import List, Optional, Dict, Any
import logging
import os
from models.password_entry import PasswordEntry

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.config = None

    def connect(self, config: Dict[str, Any]) -> bool:
        """连接到数据库"""
        self.config = config

        # 调试信息
        print(f"数据库配置: use_sqlite={config.get('use_sqlite')}")

        if config.get('use_sqlite', True):  # 默认使用 SQLite
            return self._connect_sqlite(config)
        else:
            return self._connect_mysql(config)

    def _connect_sqlite(self, config: Dict[str, Any]) -> bool:
        """连接到 SQLite 数据库"""
        try:
            db_path = config.get('sqlite_path', 'password_manager.db')
            print(f"正在连接 SQLite 数据库: {db_path}")

            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row

            # 启用外键约束
            self.connection.execute("PRAGMA foreign_keys = ON")

            logger.info(f"成功连接到SQLite数据库: {db_path}")
            self._initialize_database()
            return True

        except sqlite3.Error as e:
            logger.error(f"SQLite连接错误: {e}")
            print(f"SQLite连接错误: {e}")
            return False

    def _connect_mysql(self, config: Dict[str, Any]) -> bool:
        """连接到 MySQL 数据库"""
        try:
            print("正在连接 MySQL 数据库")

            self.connection = mysql.connector.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 3306),
                database=config.get('database', 'password_manager'),
                user=config.get('username', ''),
                password=config.get('password', ''),
                ssl_disabled=not config.get('use_ssl', False)
            )

            if self.connection.is_connected():
                logger.info("成功连接到MySQL数据库")
                self._initialize_database()
                return True
            else:
                logger.error("MySQL数据库连接失败")
                return False

        except Error as e:
            logger.error(f"MySQL连接错误: {e}")
            print(f"MySQL连接错误: {e}")
            return False

    def _initialize_database(self):
        """初始化数据库表结构"""
        try:
            cursor = self.connection.cursor()

            if self.config.get('use_sqlite', True):
                # SQLite 建表语句
                create_table_sql = """
                    CREATE TABLE IF NOT EXISTS password_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        website_name TEXT NOT NULL,
                        url TEXT,
                        username TEXT NOT NULL,
                        encrypted_password TEXT NOT NULL,
                        notes TEXT,
                        category TEXT DEFAULT '默认',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
            else:
                # MySQL 建表语句
                create_table_sql = """
                    CREATE TABLE IF NOT EXISTS password_entries (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        website_name VARCHAR(255) NOT NULL,
                        url VARCHAR(500),
                        username VARCHAR(255) NOT NULL,
                        encrypted_password TEXT NOT NULL,
                        notes TEXT,
                        category VARCHAR(100) DEFAULT '默认',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """

            # 执行建表语句
            cursor.execute(create_table_sql)

            if hasattr(self.connection, 'commit'):
                self.connection.commit()

            cursor.close()
            logger.info("数据库表初始化完成")
            print("数据库表初始化完成")

        except Exception as e:
            logger.error(f"数据库初始化错误: {e}")
            print(f"数据库初始化错误: {e}")
            if self.connection and hasattr(self.connection, 'rollback'):
                self.connection.rollback()

    def test_connection(self, config: Dict[str, Any]) -> bool:
        """测试数据库连接"""
        print(f"测试连接: use_sqlite={config.get('use_sqlite')}")

        if config.get('use_sqlite', True):
            # 测试 SQLite 连接
            db_path = config.get('sqlite_path', 'password_manager.db')
            try:
                test_conn = sqlite3.connect(db_path)
                test_conn.close()
                print("SQLite 连接测试成功")
                return True
            except sqlite3.Error as e:
                print(f"SQLite 连接测试失败: {e}")
                return False
        else:
            # 测试 MySQL 连接
            try:
                temp_conn = mysql.connector.connect(
                    host=config.get('host', 'localhost'),
                    port=config.get('port', 3306),
                    database=config.get('database', 'password_manager'),
                    user=config.get('username', ''),
                    password=config.get('password', ''),
                    ssl_disabled=not config.get('use_ssl', False)
                )

                if temp_conn.is_connected():
                    temp_conn.close()
                    print("MySQL 连接测试成功")
                    return True
                return False
            except Error as e:
                print(f"MySQL 连接测试失败: {e}")
                return False

    def search_entries(self, keyword: str = "") -> List[PasswordEntry]:
        """搜索密码记录"""
        entries = []
        try:
            cursor = self.connection.cursor()

            if keyword:
                if self.config.get('use_sqlite', True):
                    # SQLite 版本
                    query = """
                            SELECT * FROM password_entries 
                            WHERE website_name LIKE ? OR url LIKE ? OR notes LIKE ? OR category LIKE ?
                            ORDER BY website_name
                        """
                else:
                    # MySQL 版本
                    query = """
                            SELECT * FROM password_entries 
                            WHERE website_name LIKE %s OR url LIKE %s OR notes LIKE %s OR category LIKE %s
                            ORDER BY website_name
                        """
                search_pattern = f"%{keyword}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            else:
                query = "SELECT * FROM password_entries ORDER BY website_name"
                cursor.execute(query)

            # 处理结果集
            for row in cursor:
                if self.config.get('use_sqlite', True):
                    # SQLite 结果处理
                    entry_dict = dict(row)
                    # SQLite 返回的时间是字符串，需要转换为 datetime
                    # 这个转换现在在 PasswordEntry.from_dict 中处理
                else:
                    # MySQL 结果处理
                    entry_dict = row

                entries.append(PasswordEntry.from_dict(entry_dict))

            cursor.close()

        except Exception as e:
            logger.error(f"搜索记录错误: {e}")
            print(f"搜索记录错误: {e}")

        return entries

    def get_all_entries(self) -> List[PasswordEntry]:
        """获取所有密码记录"""
        return self.search_entries()

    def add_entry(self, entry: PasswordEntry) -> bool:
        """添加新记录"""
        try:
            cursor = self.connection.cursor()

            if self.config.get('use_sqlite', True):
                # SQLite 版本
                query = """
                    INSERT INTO password_entries 
                    (website_name, url, username, encrypted_password, notes, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
            else:
                # MySQL 版本
                query = """
                    INSERT INTO password_entries 
                    (website_name, url, username, encrypted_password, notes, category)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

            values = (
                entry.website_name,
                entry.url,
                entry.username,
                entry.encrypted_password,
                entry.notes,
                entry.category
            )

            cursor.execute(query, values)

            if hasattr(self.connection, 'commit'):
                self.connection.commit()

            cursor.close()

            logger.info(f"成功添加记录: {entry.website_name}")
            return True

        except Exception as e:
            logger.error(f"添加记录错误: {e}")
            print(f"添加记录错误: {e}")
            if self.connection and hasattr(self.connection, 'rollback'):
                self.connection.rollback()
            return False

    def update_entry(self, entry: PasswordEntry) -> bool:
        """更新记录"""
        try:
            cursor = self.connection.cursor()

            if self.config.get('use_sqlite', True):
                # SQLite 版本
                query = """
                    UPDATE password_entries 
                    SET website_name = ?, url = ?, username = ?, 
                        encrypted_password = ?, notes = ?, category = ?
                    WHERE id = ?
                """
            else:
                # MySQL 版本
                query = """
                    UPDATE password_entries 
                    SET website_name = %s, url = %s, username = %s, 
                        encrypted_password = %s, notes = %s, category = %s
                    WHERE id = %s
                """

            values = (
                entry.website_name,
                entry.url,
                entry.username,
                entry.encrypted_password,
                entry.notes,
                entry.category,
                entry.id
            )

            cursor.execute(query, values)

            if hasattr(self.connection, 'commit'):
                self.connection.commit()

            cursor.close()

            logger.info(f"成功更新记录: {entry.website_name}")
            return True

        except Exception as e:
            logger.error(f"更新记录错误: {e}")
            print(f"更新记录错误: {e}")
            if self.connection and hasattr(self.connection, 'rollback'):
                self.connection.rollback()
            return False

    def delete_entry(self, entry_id: int) -> bool:
        """删除记录"""
        try:
            cursor = self.connection.cursor()

            if self.config.get('use_sqlite', True):
                # SQLite 版本
                query = "DELETE FROM password_entries WHERE id = ?"
            else:
                # MySQL 版本
                query = "DELETE FROM password_entries WHERE id = %s"

            cursor.execute(query, (entry_id,))

            if hasattr(self.connection, 'commit'):
                self.connection.commit()

            cursor.close()

            logger.info(f"成功删除记录 ID: {entry_id}")
            return True

        except Exception as e:
            logger.error(f"删除记录错误: {e}")
            print(f"删除记录错误: {e}")
            if self.connection and hasattr(self.connection, 'rollback'):
                self.connection.rollback()
            return False

    def get_categories(self, config_manager=None) -> List[str]:
        """获取所有分类（结合数据库中的分类和配置文件中的分类）"""
        # 从配置文件中获取默认分类
        config_categories = []
        if config_manager and hasattr(config_manager, 'get_categories_config'):
            config_categories = config_manager.get_categories_config()

        db_categories = []
        try:
            cursor = self.connection.cursor()

            if self.config.get('use_sqlite', True):
                # SQLite 版本
                query = "SELECT DISTINCT category FROM password_entries ORDER BY category"
                cursor.execute(query)
            else:
                # MySQL 版本
                query = "SELECT DISTINCT category FROM password_entries ORDER BY category"
                cursor.execute(query)

            # 处理结果
            for row in cursor:
                if self.config.get('use_sqlite', True):
                    # SQLite 返回的是元组
                    category = row[0]
                else:
                    # MySQL connector 返回的是字典
                    category = row['category']

                if category and category not in db_categories:
                    db_categories.append(category)

            cursor.close()

        except Exception as e:
            logger.error(f"获取数据库分类错误: {e}")
            print(f"获取数据库分类错误: {e}")

        # 合并分类：配置分类 + 数据库中的分类（去重）
        all_categories = list(set(config_categories + db_categories))
        all_categories.sort()

        # 确保"默认"分类在第一位
        if "默认" in all_categories:
            all_categories.remove("默认")
            all_categories.insert(0, "默认")

        return all_categories

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("数据库连接已关闭")
            except Exception as e:
                logger.error(f"关闭数据库连接时出错: {e}")

    def search_entries(self, keyword: str = "", limit: int = None) -> List[PasswordEntry]:
        """搜索密码记录"""
        entries = []
        try:
            cursor = self.connection.cursor()

            if keyword:
                if self.config.get('use_sqlite', True):
                    # SQLite 版本
                    query = """
                        SELECT * FROM password_entries 
                        WHERE website_name LIKE ? OR url LIKE ? OR notes LIKE ? OR category LIKE ?
                        ORDER BY website_name
                    """
                    if limit:
                        query += " LIMIT ?"
                else:
                    # MySQL 版本
                    query = """
                        SELECT * FROM password_entries 
                        WHERE website_name LIKE %s OR url LIKE %s OR notes LIKE %s OR category LIKE %s
                        ORDER BY website_name
                    """
                    if limit:
                        query += " LIMIT %s"

                search_pattern = f"%{keyword}%"
                params = (search_pattern, search_pattern, search_pattern, search_pattern)
                if limit:
                    params = params + (limit,)

                cursor.execute(query, params)
            else:
                query = "SELECT * FROM password_entries ORDER BY website_name"
                if limit:
                    query += " LIMIT ?" if self.config.get('use_sqlite', True) else " LIMIT %s"
                    cursor.execute(query, (limit,))
                else:
                    cursor.execute(query)

            # 处理结果集
            for row in cursor:
                if self.config.get('use_sqlite', True):
                    # SQLite 结果处理
                    entry_dict = dict(row)
                else:
                    # MySQL 结果处理
                    entry_dict = row

                entries.append(PasswordEntry.from_dict(entry_dict))

            cursor.close()

        except Exception as e:
            logger.error(f"搜索记录错误: {e}")
            print(f"搜索记录错误: {e}")

        return entries