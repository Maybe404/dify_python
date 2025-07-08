#!/usr/bin/env python3
"""
数据库重建脚本 - 解决外键约束问题
使用方法: python scripts/rebuild_database.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Task, File, Conversation

def rebuild_database():
    """重建数据库表结构"""
    app = create_app()
    
    with app.app_context():
        print("🔄 开始重建数据库...")
        
        try:
            # 1. 删除所有表（逆序删除，避免外键约束问题）
            print("📋 删除现有表...")
            db.drop_all()
            print("✅ 所有表已删除")
            
            # 2. 重新创建所有表
            print("🏗️  创建新表...")
            db.create_all()
            print("✅ 所有表已创建")
            
            # 3. 验证表结构
            print("🔍 验证表结构...")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['users', 'tasks', 'files', 'conversations']
            for table in expected_tables:
                if table in tables:
                    print(f"  ✅ {table} 表已创建")
                    # 显示表结构
                    columns = inspector.get_columns(table)
                    for col in columns:
                        print(f"    - {col['name']}: {col['type']}")
                else:
                    print(f"  ❌ {table} 表创建失败")
            
            print("\n🎉 数据库重建完成！")
            print("\n📝 下一步操作：")
            print("  1. 数据库已重建，可以重新开始使用")
            print("  2. 运行 python run.py 启动应用")
            
        except Exception as e:
            print(f"❌ 数据库重建失败: {str(e)}")
            print(f"详细错误信息: {e}")
            return False
    
    return True

if __name__ == "__main__":
    success = rebuild_database()
    sys.exit(0 if success else 1) 