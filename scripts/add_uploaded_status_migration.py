#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加 'uploaded' 状态到任务表
功能：为任务状态枚举添加新的 'uploaded' 状态值，表示文件上传完成但还未开始处理
执行时间：2025-01-28
"""

import os
import sys
import logging
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv()

import pymysql
from app.config.config import Config

def setup_logger():
    """设置日志记录器"""
    logger = logging.getLogger('migration')
    logger.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    return logger

def connect_database():
    """连接到MySQL数据库"""
    try:
        connection = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USERNAME,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset='utf8mb4',
            autocommit=False
        )
        return connection
    except Exception as e:
        raise Exception(f"数据库连接失败: {str(e)}")

def check_current_status_enum(cursor):
    """检查当前任务表的状态枚举值"""
    query = """
    SELECT COLUMN_TYPE 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = %s 
    AND TABLE_NAME = 'tasks' 
    AND COLUMN_NAME = 'status'
    """
    cursor.execute(query, (Config.DB_NAME,))
    result = cursor.fetchone()
    
    if result:
        column_type = result['COLUMN_TYPE']
        logger.info(f"当前任务状态枚举: {column_type}")
        return 'uploaded' in column_type
    else:
        raise Exception("未找到任务表的status字段")

def add_uploaded_status(cursor):
    """添加uploaded状态到枚举中"""
    # 检查是否已经包含uploaded状态
    if check_current_status_enum(cursor):
        logger.info("任务状态枚举中已包含'uploaded'状态，无需迁移")
        return False
    
    logger.info("开始添加'uploaded'状态到任务枚举...")
    
    # 修改表结构，添加uploaded状态
    alter_sql = """
    ALTER TABLE tasks 
    MODIFY COLUMN status ENUM('pending', 'uploading', 'uploaded', 'processing', 'completed', 'failed') 
    DEFAULT 'pending' NOT NULL COMMENT '任务状态'
    """
    
    cursor.execute(alter_sql)
    logger.info("成功添加'uploaded'状态到任务枚举")
    return True

def verify_migration(cursor):
    """验证迁移是否成功"""
    if check_current_status_enum(cursor):
        logger.info("✓ 迁移验证成功：'uploaded'状态已成功添加")
        return True
    else:
        logger.error("✗ 迁移验证失败：'uploaded'状态未找到")
        return False

def main():
    """主函数"""
    global logger
    logger = setup_logger()
    
    logger.info("=" * 60)
    logger.info("开始执行任务状态迁移脚本")
    logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    connection = None
    try:
        # 连接数据库
        logger.info("正在连接数据库...")
        connection = connect_database()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        logger.info(f"成功连接到数据库: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
        
        # 开始事务
        connection.begin()
        
        # 执行迁移
        migration_needed = add_uploaded_status(cursor)
        
        if migration_needed:
            # 验证迁移
            if verify_migration(cursor):
                # 提交事务
                connection.commit()
                logger.info("✓ 迁移成功完成并已提交")
            else:
                # 回滚事务
                connection.rollback()
                logger.error("✗ 迁移验证失败，已回滚事务")
                return False
        else:
            connection.commit()
        
        logger.info("=" * 60)
        logger.info("任务状态迁移脚本执行完成")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        if connection:
            connection.rollback()
            logger.error(f"发生错误，已回滚事务: {str(e)}")
        else:
            logger.error(f"执行失败: {str(e)}")
        return False
        
    finally:
        if connection:
            connection.close()
            logger.info("数据库连接已关闭")

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 