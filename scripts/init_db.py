#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表和初始数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from dotenv import load_dotenv

def init_database():
    """初始化数据库"""
    # 加载环境变量
    load_dotenv()
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 删除所有表（谨慎使用）
            print("正在删除现有表...")
            db.drop_all()
            
            # 创建所有表
            print("正在创建数据库表...")
            db.create_all()
            
            # 创建测试用户（可选）
            create_test_user = input("是否创建测试用户？(y/N): ").lower().strip()
            if create_test_user == 'y':
                test_user = User(
                    username='admin',
                    email='admin@example.com'
                )
                test_user.password = 'Admin123456'
                test_user.save()
                print("测试用户创建成功:")
                print("  用户名: admin")
                print("  邮箱: admin@example.com")
                print("  密码: Admin123456")
            
            print("数据库初始化完成！")
            
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            return False
    
    return True

if __name__ == '__main__':
    init_database() 