#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 7:59
# @Updated: 2025/11/27 7:59
# @Python:  3.12
# @Description:

import sys
import os
import ctypes
import logging
try:
    from PyQt6.QtWidgets import QApplication
except:
    from PyQt5.QtWidgets import QApplication
import traceback
sys.excepthook = lambda exctype, value, tb: (
    print(''.join(traceback.format_exception(exctype, value, tb))),
    sys.__excepthook__(exctype, value, tb)
)

# 添加项目路径
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from core.config_manager import ConfigManager
from core.session_manager import SessionManager

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('password_manager.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def excepthook(exc_type, exc_value, exc_tb):
    """全局异常处理"""
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.critical(f"未处理的异常:\n{tb_str}")
    print(f"严重错误:\n{tb_str}")


sys.excepthook = excepthook


class PasswordManagerApp:
    def __init__(self):
        try:
            print("初始化应用程序...")
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Password Manager")
            self.app.setApplicationVersion("1.0.0")

            # 设置高 DPI 支持
            # self.app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            # self.app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

            # 初始化管理器
            self.config_manager = ConfigManager()
            self.session_manager = SessionManager()

            # 创建主窗口
            self.main_window = MainWindow(
                config_manager=self.config_manager,
                session_manager=self.session_manager
            )
            print("应用程序初始化完成")

        except Exception as e:
            print(f"应用程序初始化失败: {e}")
            traceback.print_exc()
            raise

    def run(self):
        """运行应用程序"""
        try:
            print("显示主窗口...")
            self.main_window.show()
            print("进入应用程序事件循环...")
            return self.app.exec()
        except Exception as e:
            logger.error(f"应用程序运行错误: {e}")
            traceback.print_exc()
            return 1


def main():
    """主函数"""
    try:
        # 检查资源路径
        if not os.path.exists('resources'):
            print("警告: resources 目录不存在")
        app = PasswordManagerApp()
        sys.exit(app.run())
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        traceback.print_exc()
        if sys.platform == "win32":
            ctypes.windll.user32.MessageBoxW(0, f"应用程序启动失败:\n{e}", "错误", 0)
        return 1


if __name__ == "__main__":
    main()
