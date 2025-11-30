#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/28 8:11
# @Updated: 2025/11/28 8:11
# @Python:  3.12
# @Description:
# test_encryption.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.encryption_manager import EncryptionManager


def test_encryption():
    """测试加密解密功能"""
    encryption_manager = EncryptionManager()

    test_password = "my_test_password_123"
    master_password = "my_master_password"

    print("测试加密解密功能...")
    print(f"测试密码: {test_password}")
    print(f"主密码: {master_password}")

    try:
        # 加密
        encrypted = encryption_manager.encrypt(test_password, master_password)
        print(f"加密成功: {encrypted[:50]}...")

        # 解密
        decrypted = encryption_manager.decrypt(encrypted, master_password)
        print(f"解密成功: {decrypted}")

        # 验证
        if test_password == decrypted:
            print("✓ 测试通过: 加密解密功能正常")
        else:
            print("✗ 测试失败: 解密结果与原始密码不匹配")

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_encryption()