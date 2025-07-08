#!/usr/bin/env python3
"""
手动数据库清理脚本 - 解决外键约束问题
使用原生SQL语句逐步清理和重建数据库
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text

def manual_reset_database():
    """手动重置数据库"""
    app = create_app()
    
    with app.app_context():
        print("🔧 开始手动重置数据库...")
        
        try:
            # 1. 获取数据库连接
            connection = db.engine.connect()
            
            # 2. 禁用外键检查
            print("📋 禁用外键检查...")
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # 3. 删除所有相关表（如果存在）
            tables_to_drop = ['conversations', 'files', 'tasks', 'users']
            for table in tables_to_drop:
                try:
                    connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    print(f"✅ 删除表 {table}")
                except Exception as e:
                    print(f"⚠️  删除表 {table} 时出错（可能不存在）: {str(e)}")
            
            # 4. 重新启用外键检查
            print("📋 重新启用外键检查...")
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            # 5. 提交事务
            connection.commit()
            connection.close()
            
            print("✅ 数据库清理完成")
            
            # 6. 重新创建表
            print("🏗️  重新创建表...")
            db.create_all()
            print("✅ 所有表重新创建成功")
            
            # 7. 验证表结构
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
                    
                    # 显示外键
                    foreign_keys = inspector.get_foreign_keys(table)
                    for fk in foreign_keys:
                        print(f"    外键: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
                    print()
                else:
                    print(f"  ❌ {table} 表创建失败")
            
            print("\n🎉 数据库重置完成！")
            return True
            
        except Exception as e:
            print(f"❌ 数据库重置失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = manual_reset_database()
    if success:
        print("\n📝 下一步操作：")
        print("  1. 数据库已重置，可以重新开始使用")
        print("  2. 运行 python run.py 启动应用")
    else:
        print("\n❌ 数据库重置失败")
    sys.exit(0 if success else 1) 