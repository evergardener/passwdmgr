#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/28 8:31
# @Updated: 2025/11/28 8:31
# @Python:  3.12
# @Description:

try:
    from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QListWidget, QListWidgetItem, QPushButton,
                            QMessageBox, QLineEdit, QInputDialog)

except ImportError:
    from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QListWidget, QListWidgetItem, QPushButton,
                            QMessageBox, QLineEdit, QInputDialog)


class CategoriesDialog(QDialog):
    """分类管理对话框"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setup_ui()
        self.load_categories()

    def setup_ui(self):
        """初始化UI"""
        self.setWindowTitle("管理分类")
        self.setFixedSize(400, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # 说明标签
        info_label = QLabel("管理密码分类列表：")
        layout.addWidget(info_label)

        # 分类列表
        self.categories_list = QListWidget()
        layout.addWidget(self.categories_list)

        # 添加分类区域
        add_layout = QHBoxLayout()
        self.new_category_input = QLineEdit()
        self.new_category_input.setPlaceholderText("输入新分类名称")
        self.new_category_input.returnPressed.connect(self.on_add_category)
        add_button = QPushButton("添加")
        add_button.clicked.connect(self.on_add_category)

        add_layout.addWidget(self.new_category_input)
        add_layout.addWidget(add_button)
        layout.addLayout(add_layout)

        # 操作按钮
        button_layout = QHBoxLayout()
        self.edit_button = QPushButton("编辑")
        self.delete_button = QPushButton("删除")
        self.reset_button = QPushButton("重置为默认")
        self.save_button = QPushButton("保存")
        self.cancel_button = QPushButton("取消")

        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # 信号连接
        self.categories_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.edit_button.clicked.connect(self.on_edit_category)
        self.delete_button.clicked.connect(self.on_delete_category)
        self.reset_button.clicked.connect(self.on_reset_categories)
        self.save_button.clicked.connect(self.on_save)
        self.cancel_button.clicked.connect(self.reject)

        # 初始禁用编辑和删除按钮
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def load_categories(self):
        """加载分类列表"""
        categories = self.config_manager.get_categories_config()
        self.categories_list.clear()
        self.categories_list.addItems(categories)

        # 备份原始分类用于取消时恢复
        self.original_categories = categories.copy()

    def on_selection_changed(self):
        """选中项改变"""
        has_selection = len(self.categories_list.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def on_add_category(self):
        """添加新分类"""
        new_category = self.new_category_input.text().strip()
        if not new_category:
            QMessageBox.warning(self, "警告", "请输入分类名称")
            return

        # 检查是否已存在
        existing_categories = [self.categories_list.item(i).text()
                               for i in range(self.categories_list.count())]
        if new_category in existing_categories:
            QMessageBox.warning(self, "警告", f"分类 '{new_category}' 已存在")
            return

        # 添加到列表
        self.categories_list.addItem(new_category)
        self.new_category_input.clear()

        # 自动选中新添加的项
        new_item = self.categories_list.item(self.categories_list.count() - 1)
        new_item.setSelected(True)
        self.categories_list.scrollToItem(new_item)

    def on_edit_category(self):
        """编辑选中的分类"""
        selected_items = self.categories_list.selectedItems()
        if not selected_items:
            return

        old_category = selected_items[0].text()

        # 获取新分类名称
        new_category, ok = QInputDialog.getText(
            self, "编辑分类", "输入新的分类名称:", text=old_category
        )

        if ok and new_category.strip():
            new_category = new_category.strip()

            # 检查是否已存在（排除自身）
            existing_categories = [self.categories_list.item(i).text()
                                   for i in range(self.categories_list.count())]
            if new_category in existing_categories and new_category != old_category:
                QMessageBox.warning(self, "警告", f"分类 '{new_category}' 已存在")
                return

            # 更新项
            selected_items[0].setText(new_category)

    def on_delete_category(self):
        """删除选中的分类"""
        selected_items = self.categories_list.selectedItems()
        if not selected_items:
            return

        category = selected_items[0].text()

        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除分类 '{category}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 不能删除"默认"分类
            if category == "默认":
                QMessageBox.warning(self, "警告", "不能删除'默认'分类")
                return

            row = self.categories_list.row(selected_items[0])
            self.categories_list.takeItem(row)

    def on_reset_categories(self):
        """重置为默认分类"""
        reply = QMessageBox.question(
            self, "确认重置",
            "确定要重置为默认分类列表吗？当前自定义分类将丢失。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            default_categories = [
                "默认", "工作", "个人", "金融", "社交",
                "邮箱", "购物", "娱乐", "教育", "其他"
            ]
            self.categories_list.clear()
            self.categories_list.addItems(default_categories)

    def on_save(self):
        """保存分类配置"""
        # 收集所有分类
        categories = []
        for i in range(self.categories_list.count()):
            category = self.categories_list.item(i).text().strip()
            if category and category not in categories:
                categories.append(category)

        # 确保有分类
        if not categories:
            QMessageBox.warning(self, "警告", "至少需要一个分类")
            return

        # 确保有"默认"分类
        if "默认" not in categories:
            categories.insert(0, "默认")

        # 保存配置
        self.config_manager.update_categories_config(categories)
        QMessageBox.information(self, "成功", "分类配置已保存")
        self.accept()

    def closeEvent(self, event):
        """关闭事件处理"""
        # 如果取消，恢复原始分类
        if not self.result():
            self.config_manager.update_categories_config(self.original_categories)
        event.accept()