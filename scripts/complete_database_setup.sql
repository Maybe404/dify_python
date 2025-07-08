-- =====================================================
-- 完整数据库初始化脚本 - 包含所有数据表
-- =====================================================
-- 说明：请在您的远程MySQL数据库中执行此脚本
-- 执行前请确保：
-- 1. 已连接到您的MySQL数据库
-- 2. 已选择正确的数据库（USE your_database_name;）
-- 3. 当前用户有CREATE、INDEX等权限
-- =====================================================

-- 设置字符集和排序规则
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =====================================================
-- 1. 用户表 (users)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    -- 主键字段 - 使用UUID格式
    id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '用户唯一标识符（UUID格式）',
    
    -- 用户基本信息
    username VARCHAR(80) NULL UNIQUE COMMENT '用户名（可选），3-20字符，唯一',
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
    INDEX idx_reset_token (reset_token) COMMENT '重置令牌索引'
    
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='用户信息表';

-- =====================================================
-- 2. 任务表 (tasks)
-- =====================================================
CREATE TABLE IF NOT EXISTS tasks (
    -- 主键字段
    id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '任务唯一标识符（UUID格式）',
    user_id VARCHAR(36) NOT NULL COMMENT '发起任务的用户ID',
    
    -- 任务信息
    task_type ENUM('standard_interpretation', 'standard_recommendation', 'standard_comparison', 
                   'standard_international', 'standard_compliance') NOT NULL COMMENT '任务类型',
    title VARCHAR(200) NOT NULL COMMENT '任务标题',
    description TEXT NULL COMMENT '任务描述',
    
    -- 任务状态: pending(待处理), uploading(上传中), processing(处理中), completed(已完成), failed(失败)
    status ENUM('pending', 'uploading', 'processing', 'completed', 'failed') 
           NOT NULL DEFAULT 'pending' COMMENT '任务状态',
    
    -- 时间字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_user_id (user_id) COMMENT '用户ID索引',
    INDEX idx_task_type (task_type) COMMENT '任务类型索引',
    INDEX idx_status (status) COMMENT '任务状态索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引',
    INDEX idx_user_status (user_id, status) COMMENT '用户+状态复合索引',
    INDEX idx_user_type (user_id, task_type) COMMENT '用户+类型复合索引'
    
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='任务主表 - 管理五种标准处理任务';

-- =====================================================
-- 3. 任务文件表 (task_files)
-- =====================================================
CREATE TABLE IF NOT EXISTS task_files (
    -- 主键字段
    id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '文件唯一标识符',
    task_id VARCHAR(36) NOT NULL COMMENT '任务ID',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    
    -- 本地文件信息
    original_filename VARCHAR(255) NOT NULL COMMENT '原始文件名',
    stored_filename VARCHAR(255) NOT NULL COMMENT '存储文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '本地存储路径',
    file_size BIGINT NOT NULL COMMENT '文件大小（字节）',
    file_type VARCHAR(100) NOT NULL COMMENT '文件类型/MIME类型',
    file_extension VARCHAR(20) NULL COMMENT '文件扩展名',
    
    -- Dify相关信息
    dify_file_id VARCHAR(100) NULL COMMENT 'Dify返回的文件ID',
    dify_response_data TEXT NULL COMMENT 'Dify返回的完整信息（JSON格式）',
    
    -- 状态信息
    upload_status ENUM('pending', 'uploading', 'uploaded', 'failed') 
                  NOT NULL DEFAULT 'pending' COMMENT '上传状态',
    upload_error TEXT NULL COMMENT '上传错误信息',
    
    -- 时间字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 外键约束
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_task_id (task_id) COMMENT '任务ID索引',
    INDEX idx_user_id (user_id) COMMENT '用户ID索引',
    INDEX idx_dify_file_id (dify_file_id) COMMENT 'Dify文件ID索引',
    INDEX idx_upload_status (upload_status) COMMENT '上传状态索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引'
    
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='任务文件表 - 管理上传到任务的文件';

-- =====================================================
-- 4. 任务结果表 (task_results)
-- =====================================================
CREATE TABLE IF NOT EXISTS task_results (
    -- 主键字段
    id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '结果唯一标识符',
    task_id VARCHAR(36) NOT NULL COMMENT '任务ID',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    
    -- Dify返回的信息
    message_id VARCHAR(100) NULL COMMENT 'Dify消息ID',
    conversation_id VARCHAR(100) NULL COMMENT 'Dify会话ID',
    mode VARCHAR(50) NULL COMMENT 'Dify模式',
    answer TEXT NULL COMMENT 'Dify返回的答案',
    metadata TEXT NULL COMMENT 'Dify返回的元数据（JSON格式）',
    
    -- 完整的Dify响应
    full_response TEXT NULL COMMENT 'Dify返回的完整响应（JSON格式）',
    
    -- 时间字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 外键约束
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_task_id (task_id) COMMENT '任务ID索引',
    INDEX idx_user_id (user_id) COMMENT '用户ID索引',
    INDEX idx_message_id (message_id) COMMENT 'Dify消息ID索引',
    INDEX idx_conversation_id (conversation_id) COMMENT 'Dify会话ID索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引'
    
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='任务结果表 - 存储Dify返回的处理结果';

-- =====================================================
-- 5. 对话表 (conversations)
-- =====================================================
CREATE TABLE IF NOT EXISTS conversations (
    -- 主键字段
    id VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '对话记录唯一标识符（UUID格式）',
    task_id VARCHAR(36) NULL COMMENT '任务ID（可选）',
    file_id VARCHAR(36) NULL COMMENT '关联文件ID（可选）',
    user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
    
    -- 对话信息
    user_message TEXT NOT NULL COMMENT '用户发送的消息',
    dify_response TEXT NULL COMMENT 'Dify返回的响应（JSON格式）',
    
    -- Dify相关ID
    conversation_id VARCHAR(100) NULL COMMENT 'Dify对话ID',
    message_id VARCHAR(100) NULL COMMENT 'Dify消息ID',
    
    -- 状态和元数据
    status ENUM('pending', 'processing', 'completed', 'failed') 
           NOT NULL DEFAULT 'pending' COMMENT '对话状态',
    response_time FLOAT NULL COMMENT '响应时间（秒）',
    error_message TEXT NULL COMMENT '错误信息',
    
    -- 请求参数记录
    request_data TEXT NULL COMMENT '完整请求数据（JSON格式）',
    
    -- 时间字段
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL,
    FOREIGN KEY (file_id) REFERENCES task_files(id) ON DELETE SET NULL,
    
    -- 索引
    INDEX idx_task_id (task_id) COMMENT '任务ID索引',
    INDEX idx_file_id (file_id) COMMENT '文件ID索引',
    INDEX idx_user_id (user_id) COMMENT '用户ID索引',
    INDEX idx_conversation_id (conversation_id) COMMENT 'Dify对话ID索引',
    INDEX idx_message_id (message_id) COMMENT 'Dify消息ID索引',
    INDEX idx_status (status) COMMENT '对话状态索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引'
    
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='对话表 - 存储与Dify的对话记录';

-- =====================================================
-- 重新启用外键检查
-- =====================================================
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- 验证表创建结果
-- =====================================================

-- 查看所有创建的表
SHOW TABLES;

-- 查看每个表的结构
DESCRIBE users;
DESCRIBE tasks;
DESCRIBE task_files;
DESCRIBE task_results;
DESCRIBE conversations;

-- 查看外键关系
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM 
    INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE 
    REFERENCED_TABLE_SCHEMA = DATABASE()
    AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME;

-- 验证表创建成功
SELECT 
    TABLE_NAME as '表名',
    TABLE_COMMENT as '表注释',
    ENGINE as '存储引擎',
    TABLE_COLLATION as '字符集',
    TABLE_ROWS as '当前行数'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- =====================================================
-- 可选：插入测试数据
-- =====================================================
-- 如果需要测试数据，可以取消下面的注释并执行

/*
-- 插入测试管理员用户
INSERT IGNORE INTO users (id, username, email, password_hash, is_active) VALUES 
('550e8400-e29b-41d4-a716-446655440000', 'admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Txjyvq', TRUE);

-- 插入测试普通用户
INSERT IGNORE INTO users (id, username, email, password_hash, is_active) VALUES 
('550e8400-e29b-41d4-a716-446655440001', 'testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3bp.Txjyvq', TRUE);

-- 插入测试任务
INSERT IGNORE INTO tasks (id, user_id, task_type, title, description, status) VALUES 
('task-550e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440001', 'standard_interpretation', '测试标准解读任务', '这是一个测试任务', 'pending');

-- 查看插入的测试数据
SELECT 'users表' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'tasks表' as table_name, COUNT(*) as record_count FROM tasks
UNION ALL
SELECT 'task_files表' as table_name, COUNT(*) as record_count FROM task_files
UNION ALL
SELECT 'task_results表' as table_name, COUNT(*) as record_count FROM task_results
UNION ALL
SELECT 'conversations表' as table_name, COUNT(*) as record_count FROM conversations;
*/

-- =====================================================
-- 脚本执行完成
-- =====================================================
SELECT '🎉 完整数据库初始化完成！' as message;
SELECT '✅ 共创建5个数据表：users, tasks, task_files, task_results, conversations' as details; 