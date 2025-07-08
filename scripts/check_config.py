#!/usr/bin/env python3
"""
配置检查脚本
用于诊断环境变量和配置问题
"""

import os
import sys
from dotenv import load_dotenv

# 添加父目录到路径，以便可以导入app模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_config():
    print("🔍 配置检查脚本")
    print("=" * 50)
    
    # 检查.env文件是否存在
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ .env文件存在: {env_file}")
        load_dotenv()
    else:
        print(f"❌ .env文件不存在: {env_file}")
        print("   请复制 env_example.txt 为 .env 文件")
        return False
    
    print("\n📋 环境变量检查:")
    print("-" * 30)
    
    # 检查关键配置
    configs = [
        ('SECRET_KEY', '必须设置'),
        ('JWT_SECRET_KEY', '必须设置'),
        ('DB_HOST', '数据库主机'),
        ('DB_USERNAME', '数据库用户名'),
        ('DB_PASSWORD', '数据库密码'),
        ('DB_NAME', '数据库名称'),
        ('DATABASE_URL', '数据库连接URL'),
    ]
    
    all_good = True
    for key, desc in configs:
        value = os.getenv(key)
        if value:
            if 'your-' in value and '-here' in value:
                print(f"⚠️  {key}: 使用默认值，需要修改")
                all_good = False
            else:
                # 对于敏感信息，只显示前几位
                if 'PASSWORD' in key or 'SECRET' in key:
                    display_value = value[:8] + '...' if len(value) > 8 else value
                else:
                    display_value = value
                print(f"✅ {key}: {display_value}")
        else:
            print(f"❌ {key}: 未设置 ({desc})")
            all_good = False
    
    print("\n🔗 数据库连接测试:")
    print("-" * 30)
    
    try:
        import pymysql
        
        # 测试数据库连接
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ 数据库连接成功")
            print(f"   MySQL版本: {version[0]}")
            
            # 检查users表是否存在
            cursor.execute("SHOW TABLES LIKE 'users'")
            table_exists = cursor.fetchone()
            if table_exists:
                print("✅ users表存在")
                
                # 检查表结构
                cursor.execute("DESCRIBE users")
                columns = cursor.fetchall()
                print(f"   表字段数: {len(columns)}")
                
                # 检查是否有UUID格式的id字段
                id_column = next((col for col in columns if col[0] == 'id'), None)
                if id_column and 'varchar(36)' in id_column[1].lower():
                    print("✅ ID字段使用UUID格式")
                else:
                    print("⚠️  ID字段可能不是UUID格式")
            else:
                print("❌ users表不存在，请执行建表脚本")
                all_good = False
        
        connection.close()
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        all_good = False
    
    print("\n🚀 Flask应用测试:")
    print("-" * 30)
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask应用创建成功")
        
        # 检查JWT配置
        if hasattr(app, 'config'):
            jwt_key = app.config.get('JWT_SECRET_KEY')
            if jwt_key and 'your-' not in jwt_key:
                print("✅ JWT配置正确")
            else:
                print("❌ JWT配置有问题")
                all_good = False
        
    except Exception as e:
        print(f"❌ Flask应用创建失败: {e}")
        all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 所有配置检查通过！可以启动服务了")
        print("   运行命令: python run.py")
    else:
        print("❌ 发现配置问题，请根据上述提示修复")
        print("   参考文档: docs/configuration_checklist.md")
    
    return all_good

if __name__ == '__main__':
    check_config() 