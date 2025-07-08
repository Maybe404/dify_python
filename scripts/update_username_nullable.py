#!/usr/bin/env python3
"""
数据库迁移脚本：更新用户名字段为可空
用于将用户名从必填字段改为可选字段
"""

import os
import sys
import pymysql
from dotenv import load_dotenv

# 添加父目录到路径，以便可以导入app模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_username_nullable():
    """更新用户名字段为可空"""
    # 加载环境变量
    load_dotenv()
    
    # 获取数据库配置
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USERNAME', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'user_system'),
        'charset': 'utf8mb4'
    }
    
    print("🔄 开始数据库迁移：更新用户名字段为可空")
    print("=" * 50)
    print(f"数据库: {config['host']}:{config['port']}/{config['database']}")
    
    try:
        # 连接数据库
        connection = pymysql.connect(**config)
        print("✅ 数据库连接成功")
        
        with connection.cursor() as cursor:
            # 检查users表是否存在
            cursor.execute("SHOW TABLES LIKE 'users'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("❌ users表不存在，请先运行数据库初始化")
                return False
            
            # 检查当前字段信息
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            username_column = next((col for col in columns if col[0] == 'username'), None)
            
            if not username_column:
                print("❌ username字段不存在")
                return False
            
            print(f"📋 当前username字段: {username_column[1]} {username_column[2]}")
            
            # 检查是否已经是可空的
            if username_column[2] == 'YES':
                print("✅ username字段已经是可空的，无需更新")
                return True
            
            # 更新字段为可空
            print("🔄 更新username字段为可空...")
            alter_sql = "ALTER TABLE users MODIFY COLUMN username VARCHAR(80) NULL COMMENT '用户名（可选）'"
            cursor.execute(alter_sql)
            connection.commit()
            
            # 验证修改结果
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            username_column = next((col for col in columns if col[0] == 'username'), None)
            
            if username_column[2] == 'YES':
                print("✅ 字段更新成功！username现在是可空的")
                print(f"📋 更新后的字段: {username_column[1]} {username_column[2]}")
                
                # 检查现有数据
                cursor.execute("SELECT COUNT(*) FROM users WHERE username IS NULL OR username = ''")
                null_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM users")
                total_count = cursor.fetchone()[0]
                
                print(f"📊 数据统计:")
                print(f"   总用户数: {total_count}")
                print(f"   无用户名的用户: {null_count}")
                
                return True
            else:
                print("❌ 字段更新失败")
                return False
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False
    
    finally:
        if 'connection' in locals():
            connection.close()
            print("📪 数据库连接已关闭")

def main():
    """主函数"""
    print("🛠️  数据库迁移工具")
    print("任务：将username字段从NOT NULL改为NULL")
    print()
    
    # 检查环境变量文件
    if not os.path.exists('.env'):
        print("⚠️  未找到.env文件")
        print("请复制env_example.txt为.env并配置数据库连接信息")
        return
    
    # 执行迁移
    success = update_username_nullable()
    
    print("=" * 50)
    if success:
        print("🎉 迁移完成！")
        print("现在用户可以在注册时不提供用户名")
        print()
        print("💡 提示:")
        print("   - 用户名现在是可选的")
        print("   - 邮箱仍然是必填的")
        print("   - 密码必须是16位，包含大小写字母、数字和符号")
    else:
        print("❌ 迁移失败！请检查错误信息并重试")
    print("=" * 50)

if __name__ == '__main__':
    main() 