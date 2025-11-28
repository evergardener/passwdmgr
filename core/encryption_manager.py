#!/usr/bin/env python
# -*-coding:utf-8 -*-
# @Author:  xx
# @Created: 2025/11/27 8:03
# @Updated: 2025/11/27 8:03
# @Python:  3.12
# @Description:
import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """加密管理器"""

    def __init__(self):
        self.backend = default_backend()

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """从密码派生密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        return kdf.derive(password.encode('utf-8'))

    def encrypt(self, plaintext: str, password: str) -> str:
        """加密文本"""
        try:
            print(f"加密: 明文长度={len(plaintext)}, 密码长度={len(password)}")

            # 生成随机盐和IV
            salt = os.urandom(16)
            iv = os.urandom(16)

            # 派生密钥
            key = self.derive_key(password, salt)

            # 加密
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()

            # 组合盐 + IV + 认证标签 + 密文
            encrypted_data = salt + iv + encryptor.tag + ciphertext

            # Base64编码
            result = base64.b64encode(encrypted_data).decode('utf-8')

            print(f"加密成功: 结果长度={len(result)}")
            return result

        except Exception as e:
            logger.error(f"加密失败: {e}")
            raise

    def decrypt(self, encrypted_data: str, password: str) -> str:
        """解密文本"""
        try:
            print(f"解密: 加密数据长度={len(encrypted_data)}, 密码长度={len(password)}")

            # Base64解码
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))

            # 分离各部分
            salt = encrypted_bytes[:16]
            iv = encrypted_bytes[16:32]
            tag = encrypted_bytes[32:48]
            ciphertext = encrypted_bytes[48:]

            # 派生密钥
            key = self.derive_key(password, salt)

            # 解密
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=self.backend)
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            result = plaintext.decode('utf-8')
            print(f"解密成功: 结果长度={len(result)}")
            return result
        except Exception as e:
            logger.error(f"解密失败: {e}")
            raise

    def validate_password(self, encrypted_data: str, password: str) -> bool:
        """验证密码是否正确"""
        try:
            self.decrypt(encrypted_data, password)
            return True
        except Exception:
            return False