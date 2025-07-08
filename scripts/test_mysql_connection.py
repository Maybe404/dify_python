#!/usr/bin/env python3
"""
MySQL数据库连接测试脚本
用于验证数据库连接配置是否正确
"""

import pymysql
import os
from dotenv import load_dotenv

def test_mysql_connection():
    """测试MySQL数据库连接"""
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
    
    print("正在测试MySQL连接...")
    print(f"主机: {config['host']}:{config['port']}")
    print(f"用户: {config['user']}")
    print(f"数据库: {config['database']}")
    print("-" * 50)
    
    try:
        # 尝试连接数据库
        connection = pymysql.connect(**config)
        print("✅ 数据库连接成功！")
        
        with connection.cursor() as cursor:
            # 获取MySQL版本
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 MySQL版本: {version[0]}")
            
            # 检查数据库是否存在
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()
            print(f"📁 当前数据库: {current_db[0]}")
            
            # 检查用户表是否存在
            cursor.execute("SHOW TABLES LIKE 'users'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("✅ users表已存在")
                
                # 获取表结构
                cursor.execute("DESCRIBE users")
                columns = cursor.fetchall()
                print("📋 表结构:")
                for column in columns:
                    print(f"   - {column[0]}: {column[1]}")
                
                # 获取记录数
                cursor.execute("SELECT COUNT(*) FROM users")
                count = cursor.fetchone()
                print(f"📈 用户记录数: {count[0]}")
                
                if count[0] > 0:
                    # 显示最近的几个用户
                    cursor.execute("SELECT id, username, email, created_at FROM users ORDER BY created_at DESC LIMIT 3")
                    recent_users = cursor.fetchall()
                    print("👥 最近的用户:")
                    for user in recent_users:
                        print(f"   - ID:{user[0]} {user[1]} ({user[2]}) - {user[3]}")
            else:
                print("⚠️  users表不存在，需要运行数据库初始化")
        
        connection.close()
        print("✅ 连接测试完成！")
        return True
        
    except pymysql.err.OperationalError as e:
        error_code, error_msg = e.args
        print(f"❌ 数据库连接失败 (错误码: {error_code})")
        print(f"   错误信息: {error_msg}")
        
        if error_code == 1045:
            print("💡 建议检查:")
            print("   - 用户名和密码是否正确")
            print("   - 用户是否有访问该数据库的权限")
        elif error_code == 2003:
            print("💡 建议检查:")
            print("   - MySQL服务是否启动")
            print("   - 主机地址和端口是否正确")
            print("   - 防火墙是否阻止连接")
        elif error_code == 1049:
            print("💡 建议检查:")
            print("   - 数据库是否已创建")
            print("   - 数据库名称是否正确")
        
        return False
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 MySQL数据库连接测试")
    print("=" * 60)
    
    # 检查环境变量文件
    if not os.path.exists('.env'):
        print("⚠️  未找到.env文件")
        print("请复制env_example.txt为.env并配置数据库连接信息")
        return
    
    # 执行连接测试
    success = test_mysql_connection()
    
    print("=" * 60)
    if success:
        print("🎉 测试通过！可以启动应用程序")
        print("运行命令: python run.py")
    else:
        print("❌ 测试失败！请检查配置后重试")
        print("参考文档: docs/mysql_setup.md")
    print("=" * 60)

if __name__ == '__main__':
    main() 