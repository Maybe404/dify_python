#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加standard_review任务类型
使用方法: python scripts/add_standard_review_migration.py
"""

import os
import sys
from sqlalchemy import create_engine, text

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config.config import Config

def migrate_add_standard_review():
    """添加standard_review到task_type枚举"""
    
    # 创建数据库连接
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    try:
        with engine.connect() as conn:
            # 开始事务
            trans = conn.begin()
            
            try:
                print("开始添加standard_review任务类型...")
                
                # MySQL的ALTER COLUMN语法来修改枚举
                alter_sql = """
                ALTER TABLE tasks 
                MODIFY COLUMN task_type 
                ENUM('standard_interpretation', 'standard_recommendation', 'standard_comparison', 
                     'standard_international', 'standard_compliance', 'standard_review') 
                NOT NULL 
                COMMENT '任务类型'
                """
                
                conn.execute(text(alter_sql))
                
                # 提交事务
                trans.commit()
                print("✅ 成功添加standard_review任务类型到数据库")
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                print(f"❌ 迁移失败: {str(e)}")
                raise
                
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 50)
    print("数据库迁移：添加standard_review任务类型")
    print("=" * 50)
    
    # 检查环境变量
    if not Config.SQLALCHEMY_DATABASE_URI:
        print("❌ 错误：未找到数据库配置，请检查环境变量")
        sys.exit(1)
    
    print(f"数据库URI: {Config.SQLALCHEMY_DATABASE_URI[:50]}...")
    
    confirm = input("确认执行迁移? (y/N): ")
    if confirm.lower() != 'y':
        print("迁移已取消")
        sys.exit(0)
    
    migrate_add_standard_review()
    print("=" * 50)
    print("迁移完成") 