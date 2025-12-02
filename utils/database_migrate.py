# -*- coding: utf-8 -*-
#
# @Created : 2025-12-02 09:33
# @Author  : Evergarden
# @Email   : violet20160719@163.com
# @Python  : 3.12
# @Desc    :
"""
数据库迁移工具 - 从SQLite迁移到MySQL
"""
import sqlite3
import mysql.connector
from mysql.connector import Error
import json
import os
from pathlib import Path


class DatabaseMigrator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / "config.json"
        self.sqlite_path = self.project_root / "password_manager.db"

        # 加载配置
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件"""
        if not self.config_file.exists():
            return {}

        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def connect_sqlite(self):
        """连接SQLite数据库"""
        if not self.sqlite_path.exists():
            print(f"错误: SQLite数据库文件不存在: {self.sqlite_path}")
            return None

        try:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            print("成功连接到SQLite数据库")
            return conn
        except sqlite3.Error as e:
            print(f"连接SQLite失败: {e}")
            return None

    def connect_mysql(self, config):
        """连接MySQL数据库"""
        try:
            conn = mysql.connector.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 3306),
                database=config.get('database', 'password_manager'),
                user=config.get('username', ''),
                password=config.get('password', ''),
                ssl_disabled=not config.get('use_ssl', False)
            )

            if conn.is_connected():
                print("成功连接到MySQL数据库")
                return conn
            else:
                print("MySQL连接失败")
                return None
        except Error as e:
            print(f"连接MySQL失败: {e}")
            return None

    def get_sqlite_tables(self, conn):
        """获取SQLite中的所有表"""
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def migrate_table(self, sqlite_conn, mysql_conn, table_name):
        """迁移单个表"""
        print(f"迁移表: {table_name}")

        # 获取SQLite表结构
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
        columns = sqlite_cursor.fetchall()

        # 构建创建表的SQL
        column_defs = []
        for col in columns:
            col_id, col_name, col_type, notnull, default_val, pk = col
            # 转换SQLite类型到MySQL类型
            if 'INT' in col_type.upper():
                mysql_type = 'INT'
            elif 'TEXT' in col_type.upper():
                mysql_type = 'TEXT'
            elif 'REAL' in col_type.upper():
                mysql_type = 'DOUBLE'
            elif 'BLOB' in col_type.upper():
                mysql_type = 'BLOB'
            else:
                mysql_type = 'TEXT'

            column_def = f"`{col_name}` {mysql_type}"
            if notnull:
                column_def += " NOT NULL"
            if default_val is not None:
                column_def += f" DEFAULT '{default_val}'"
            if pk:
                column_def += " PRIMARY KEY AUTO_INCREMENT"

            column_defs.append(column_def)

        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    "
        create_sql += ",\n    ".join(column_defs)
        create_sql += "\n)"

        # 在MySQL中创建表
        mysql_cursor = mysql_conn.cursor()
        try:
            mysql_cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            mysql_cursor.execute(create_sql)
            print(f"表 {table_name} 创建成功")
        except Error as e:
            print(f"创建表失败: {e}")
            mysql_cursor.close()
            return False

        # 迁移数据
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()

        if rows:
            # 获取列名
            column_names = [col[1] for col in columns]
            placeholders = ', '.join(['%s'] * len(column_names))
            insert_sql = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"

            for row in rows:
                try:
                    mysql_cursor.execute(insert_sql, row)
                except Error as e:
                    print(f"插入数据失败: {e}")
                    continue

            mysql_conn.commit()
            print(f"迁移了 {len(rows)} 条记录")

        sqlite_cursor.close()
        mysql_cursor.close()
        return True

    def migrate(self):
        """执行数据库迁移"""
        print("=" * 60)
        print("数据库迁移工具 - SQLite 到 MySQL")
        print("=" * 60)

        # 检查配置
        if 'database' not in self.config:
            print("错误: 未找到数据库配置")
            return False

        db_config = self.config['database']

        if db_config.get('use_sqlite', True):
            print("当前配置使用SQLite，请先在设置中切换到MySQL")
            return False

        # 连接到源数据库（SQLite）
        sqlite_conn = self.connect_sqlite()
        if not sqlite_conn:
            return False

        # 连接到目标数据库（MySQL）
        mysql_conn = self.connect_mysql(db_config)
        if not mysql_conn:
            sqlite_conn.close()
            return False

        try:
            # 获取所有表
            tables = self.get_sqlite_tables(sqlite_conn)
            print(f"找到 {len(tables)} 个表: {', '.join(tables)}")

            # 迁移每个表
            success_count = 0
            for table in tables:
                if self.migrate_table(sqlite_conn, mysql_conn, table):
                    success_count += 1

            print(f"\n迁移完成: {success_count}/{len(tables)} 个表迁移成功")

            # 更新配置
            if success_count > 0:
                # 备份SQLite文件
                backup_path = self.sqlite_path.with_suffix('.db.backup')
                import shutil
                shutil.copy2(self.sqlite_path, backup_path)
                print(f"SQLite数据库已备份到: {backup_path}")

                print("\n✅ 迁移完成!")
                print("注意: 请重新启动应用程序使用新的MySQL数据库")

        finally:
            sqlite_conn.close()
            mysql_conn.close()

        return True


def main():
    migrator = DatabaseMigrator()

    print("警告: 此操作会将数据从SQLite迁移到MySQL")
    print("请确保:")
    print("1. MySQL服务正在运行")
    print("2. 已在设置中配置正确的MySQL连接信息")
    print("3. 已备份重要数据")

    confirm = input("\n是否继续? (y/N): ").strip().lower()
    if confirm != 'y':
        print("取消迁移")
        return

    migrator.migrate()


if __name__ == "__main__":
    main()