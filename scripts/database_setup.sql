-- =====================================================
-- 用户管理系统 - MySQL数据库建表脚本
-- =====================================================
-- 说明：请在您的远程MySQL数据库中执行此脚本
-- 执行前请确保：
-- 1. 已连接到您的MySQL数据库
-- 2. 已选择正确的数据库（USE your_database_name;）
-- 3. 当前用户有CREATE、INDEX等权限
-- =====================================================

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    -- 主键字段 - 使用UUID格式
    id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '用户唯一标识符（UUID格式）',
    
    -- 用户基本信息
    username VARCHAR(80) NOT NULL UNIQUE COMMENT '用户名，3-20字符，唯一',
    email VARCHAR(120) NOT NULL UNIQUE COMMENT '邮箱地址，唯一',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值（bcrypt加密）',
    
    -- 密码重置相关字段
    reset_token VARCHAR(255) NULL COMMENT '密码重置令牌',
    reset_token_expires DATETIME NULL COMMENT '重置令牌过期时间',
    
    -- 用户状态
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '用户状态：TRUE=激活，FALSE=禁用',
    
    -- 时间戳字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '用户创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    last_login DATETIME NULL COMMENT '最后登录时间',
    
    -- 创建索引以提高查询性能
    INDEX idx_username (username) COMMENT '用户名索引',
    INDEX idx_email (email) COMMENT '邮箱索引',
    INDEX idx_is_active (is_active) COMMENT '用户状态索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引',
    INDEX idx_last_login (last_login) COMMENT '最后登录时间索引',
    INDEX idx_reset_token (reset_token) COMMENT '重置令牌索引',
    INDEX idx_username_active (username, is_active) COMMENT '用户名+状态复合索引',
    INDEX idx_email_active (email, is_active) COMMENT '邮箱+状态复合索引'
    
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='用户信息表';

-- =====================================================
-- 验证表创建结果
-- =====================================================

-- 查看表结构
DESCRIBE users;

-- 查看表的详细创建信息
SHOW CREATE TABLE users;

-- 查看表的索引信息
SHOW INDEX FROM users;

-- 验证表是否创建成功
SELECT 
    TABLE_NAME as '表名',
    TABLE_COMMENT as '表注释',
    ENGINE as '存储引擎',
    TABLE_COLLATION as '字符集'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_NAME = 'users';

-- =====================================================
-- 可选：插入测试数据
-- =====================================================
-- 如果需要测试数据，可以取消下面的注释并执行

/*
-- 插入测试管理员用户
-- 用户名: admin
-- 邮箱: admin@example.com  
-- 密码: Admin123456
INSERT IGNORE INTO users (id, username, email, password_hash, is_active) VALUES 
(UUID(), 'admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Txjyvq', TRUE);

-- 插入测试普通用户
-- 用户名: testuser
-- 邮箱: test@example.com
-- 密码: TestPass123
INSERT IGNORE INTO users (id, username, email, password_hash, is_active) VALUES 
(UUID(), 'testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Txjyvq', TRUE);

-- 查看插入的测试数据
SELECT id, username, email, is_active, created_at FROM users;
*/

-- =====================================================
-- 脚本执行完成
-- =====================================================
SELECT 'users表创建完成！' as message;
SELECT COUNT(*) as current_user_count FROM users; 