#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
任务管理系统数据库初始化脚本
"""

import os
import sys
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.task import Task, TaskFile, TaskResult
from app.services.standard_config_service import StandardConfigService

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def init_tasks_database():
    """初始化任务管理相关数据库表"""
    logger = setup_logging()
    
    try:
        # 创建Flask应用
        app = create_app()
        
        with app.app_context():
            logger.info("开始初始化任务管理数据库...")
            
            # 检查环境配置
            logger.info("检查环境配置...")
            config_status = StandardConfigService.get_config_status()
            logger.info(f"配置状态: {config_status['configured_types']}/{config_status['total_types']} 个类型已配置")
            
            # 创建数据库表
            logger.info("创建数据库表...")
            
            # 检查表是否存在
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            tables_to_create = ['tasks', 'task_files', 'task_results']
            new_tables = [table for table in tables_to_create if table not in existing_tables]
            
            if new_tables:
                logger.info(f"将创建新表: {', '.join(new_tables)}")
                db.create_all()
                logger.info("数据库表创建成功！")
            else:
                logger.info("所有任务相关表已存在，无需创建")
            
            # 验证表结构
            logger.info("验证表结构...")
            for table_name in tables_to_create:
                if table_name in inspector.get_table_names():
                    columns = [col['name'] for col in inspector.get_columns(table_name)]
                    logger.info(f"表 {table_name} 包含字段: {', '.join(columns)}")
                else:
                    logger.error(f"表 {table_name} 不存在！")
                    return False
            
            # 显示任务类型配置
            logger.info("支持的任务类型:")
            task_types = StandardConfigService.get_all_standard_types()
            for task_type in task_types:
                logger.info(f"  - {task_type['key']}: {task_type['name']}")
            
            logger.info("任务管理数据库初始化完成！")
            return True
            
    except Exception as e:
        logger.error(f"初始化失败: {str(e)}", exc_info=True)
        return False

def check_database_status():
    """检查数据库状态"""
    logger = setup_logging()
    
    try:
        app = create_app()
        
        with app.app_context():
            logger.info("检查数据库连接...")
            
            # 检查数据库连接
            try:
                db.session.execute(db.text('SELECT 1'))
                logger.info("✓ 数据库连接正常")
            except Exception as e:
                logger.error(f"✗ 数据库连接失败: {str(e)}")
                return False
            
            # 检查表是否存在
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = ['users', 'tasks', 'task_files', 'task_results']
            
            logger.info("检查必需的表:")
            for table in required_tables:
                if table in existing_tables:
                    logger.info(f"✓ 表 {table} 存在")
                else:
                    logger.error(f"✗ 表 {table} 不存在")
            
            # 统计现有数据
            if 'tasks' in existing_tables:
                task_count = db.session.query(Task).count()
                logger.info(f"现有任务数量: {task_count}")
                
                if task_count > 0:
                    # 按状态统计
                    from sqlalchemy import func
                    status_stats = dict(
                        db.session.query(Task.status, func.count(Task.id))
                        .group_by(Task.status)
                        .all()
                    )
                    logger.info(f"任务状态统计: {status_stats}")
                    
                    # 按类型统计
                    type_stats = dict(
                        db.session.query(Task.task_type, func.count(Task.id))
                        .group_by(Task.task_type)
                        .all()
                    )
                    logger.info(f"任务类型统计: {type_stats}")
            
            return True
            
    except Exception as e:
        logger.error(f"检查失败: {str(e)}", exc_info=True)
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='任务管理系统数据库工具')
    parser.add_argument('--action', choices=['init', 'check'], default='init',
                      help='执行操作: init(初始化) 或 check(检查)')
    
    args = parser.parse_args()
    
    if args.action == 'init':
        success = init_tasks_database()
    elif args.action == 'check':
        success = check_database_status()
    else:
        print("未知操作")
        success = False
    
    if success:
        print("操作完成")
        sys.exit(0)
    else:
        print("操作失败")
        sys.exit(1)

if __name__ == '__main__':
    main() 