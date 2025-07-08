#!/usr/bin/env python3
"""
数据库清理脚本 - 使用项目配置
从项目配置中读取数据库参数
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 确保加载.env文件
load_dotenv()

def get_database_config():
    """获取数据库配置"""
    # 读取数据库配置，与config.py保持一致
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USERNAME = os.getenv('DB_USERNAME', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'user_system')
    
    return DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_NAME

def clean_and_recreate_tables():
    """清理并重新创建表"""
    try:
        DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_NAME = get_database_config()
        
        # 创建数据库连接，使用项目配置
        database_url = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        engine = create_engine(database_url)
        
        print("🔧 开始清理数据库...")
        print(f"数据库配置: {DB_USERNAME}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        with engine.connect() as connection:
            # 1. 禁用外键检查
            print("📋 禁用外键检查...")
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # 2. 删除所有相关表
            tables_to_drop = ['conversations', 'files', 'tasks', 'users']
            for table in tables_to_drop:
                try:
                    connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    print(f"✅ 删除表 {table}")
                except Exception as e:
                    print(f"⚠️  删除表 {table} 时出错: {str(e)}")
            
            # 3. 重新启用外键检查
            print("📋 重新启用外键检查...")
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            # 4. 创建users表
            print("🏗️  创建users表...")
            users_sql = """
            CREATE TABLE users (
                id VARCHAR(36) NOT NULL COMMENT '用户唯一标识符（UUID格式）',
                username VARCHAR(80) UNIQUE COMMENT '用户名（可选）',
                email VARCHAR(120) NOT NULL UNIQUE COMMENT '邮箱地址',
                password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
                reset_token VARCHAR(255) COMMENT '密码重置令牌',
                reset_token_expires DATETIME COMMENT '重置令牌过期时间',
                is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否激活',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                last_login DATETIME COMMENT '最后登录时间',
                PRIMARY KEY (id),
                INDEX idx_username (username),
                INDEX idx_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            connection.execute(text(users_sql))
            print("✅ users表创建成功")
            
            # 5. 创建tasks表
            print("🏗️  创建tasks表...")
            tasks_sql = """
            CREATE TABLE tasks (
                id VARCHAR(36) NOT NULL COMMENT '任务唯一标识符（UUID格式）',
                user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
                title VARCHAR(200) NOT NULL COMMENT '任务标题',
                description TEXT COMMENT '任务描述',
                task_type ENUM('standard_interpretation','standard_recommendation','standard_comparison','standard_international','standard_compliance') NOT NULL COMMENT '任务类型',
                task_number INTEGER NOT NULL COMMENT '任务序号',
                status ENUM('pending','uploading','processing','completed','failed') NOT NULL DEFAULT 'pending' COMMENT '任务状态',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                PRIMARY KEY (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                INDEX idx_user_id (user_id),
                INDEX idx_task_type (task_type),
                INDEX idx_task_number (task_number),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            connection.execute(text(tasks_sql))
            print("✅ tasks表创建成功")
            
            # 6. 创建files表
            print("🏗️  创建files表...")
            files_sql = """
            CREATE TABLE files (
                id VARCHAR(36) NOT NULL COMMENT '文件唯一标识符（UUID格式）',
                task_id VARCHAR(36) NOT NULL COMMENT '任务ID',
                original_filename VARCHAR(255) NOT NULL COMMENT '原始文件名',
                stored_filename VARCHAR(255) NOT NULL COMMENT '存储文件名',
                file_path TEXT NOT NULL COMMENT '文件路径',
                file_size BIGINT NOT NULL COMMENT '文件大小（字节）',
                file_type VARCHAR(100) NOT NULL COMMENT '文件类型',
                file_extension VARCHAR(20) COMMENT '文件扩展名',
                upload_status ENUM('pending','uploading','uploaded','failed') NOT NULL DEFAULT 'pending' COMMENT '上传状态',
                dify_file_id VARCHAR(255) COMMENT 'Dify文件ID',
                dify_response_data JSON COMMENT 'Dify响应数据',
                error_message TEXT COMMENT '错误信息',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                PRIMARY KEY (id),
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                INDEX idx_task_id (task_id),
                INDEX idx_upload_status (upload_status),
                INDEX idx_dify_file_id (dify_file_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            connection.execute(text(files_sql))
            print("✅ files表创建成功")
            
            # 7. 创建conversations表
            print("🏗️  创建conversations表...")
            conversations_sql = """
            CREATE TABLE conversations (
                id VARCHAR(36) NOT NULL COMMENT '对话唯一标识符（UUID格式）',
                task_id VARCHAR(36) NOT NULL COMMENT '任务ID',
                file_id VARCHAR(36) COMMENT '文件ID（可选）',
                user_id VARCHAR(36) NOT NULL COMMENT '用户ID',
                user_message TEXT NOT NULL COMMENT '用户消息',
                dify_response_data JSON COMMENT 'Dify响应数据',
                dify_conversation_id VARCHAR(255) COMMENT 'Dify对话ID',
                dify_message_id VARCHAR(255) COMMENT 'Dify消息ID',
                request_data JSON COMMENT '请求数据',
                response_time FLOAT COMMENT '响应时间（秒）',
                status ENUM('pending','processing','completed','failed') NOT NULL DEFAULT 'pending' COMMENT '状态',
                error_message TEXT COMMENT '错误信息',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                PRIMARY KEY (id),
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (file_id) REFERENCES files (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                INDEX idx_task_id (task_id),
                INDEX idx_file_id (file_id),
                INDEX idx_user_id (user_id),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            connection.execute(text(conversations_sql))
            print("✅ conversations表创建成功")
            
            # 8. 提交事务
            connection.commit()
            
        print("\n🎉 数据库表创建完成！")
        
        # 9. 验证表结构
        print("🔍 验证表结构...")
        with engine.connect() as connection:
            tables_result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in tables_result]
            for table in ['users', 'tasks', 'files', 'conversations']:
                if table in tables:
                    print(f"  ✅ {table} 表已创建")
                else:
                    print(f"  ❌ {table} 表创建失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 数据库清理和重建 - 使用项目配置")
    print("=" * 50)
    
    success = clean_and_recreate_tables()
    if success:
        print("\n📝 下一步操作：")
        print("  1. 数据库已清理，可以重新开始使用")
        print("  2. 运行 python run.py 启动应用")
    else:
        print("\n❌ 数据库清理失败")
    
    sys.exit(0 if success else 1) 