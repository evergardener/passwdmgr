-- 创建数据库和用户（在MySQL中执行）
CREATE DATABASE IF NOT EXISTS password_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建专用用户（可选）
CREATE USER IF NOT EXISTS 'pm_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON password_manager.* TO 'pm_user'@'localhost';
FLUSH PRIVILEGES;

-- 使用数据库
USE password_manager;

-- 创建密码记录表
CREATE TABLE IF NOT EXISTS password_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    website_name VARCHAR(255) NOT NULL,
    url VARCHAR(500),
    username VARCHAR(255) NOT NULL,
    encrypted_password TEXT NOT NULL,
    notes TEXT,
    category VARCHAR(100) DEFAULT '默认',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_website_name (website_name),
    INDEX idx_url (url(255)),
    INDEX idx_notes (notes(255)),
    INDEX idx_category (category)
);

-- 创建用户配置表
CREATE TABLE IF NOT EXISTS user_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(255) NOT NULL UNIQUE,
    config_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 插入初始配置（可选）
INSERT INTO user_config (config_key, config_value) VALUES
('app_version', '1.0.0'),
('default_category', '默认')
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value);