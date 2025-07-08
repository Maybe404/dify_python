#!/usr/bin/env python3
"""
简化的日志查看脚本
"""

import os
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
LOG_FILE = PROJECT_ROOT / 'logs' / 'app.log'

def view_logs():
    """查看日志"""
    print("📋 用户管理系统 - 日志查看器")
    print("=" * 50)
    
    if not LOG_FILE.exists():
        print(f"❌ 日志文件不存在: {LOG_FILE}")
        print("💡 提示: 启动应用后会自动创建日志文件")
        return
    
    try:
        # 获取文件大小
        file_size = LOG_FILE.stat().st_size
        if file_size > 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.2f} MB"
        elif file_size > 1024:
            size_str = f"{file_size / 1024:.2f} KB"
        else:
            size_str = f"{file_size} bytes"
            
        print(f"📁 日志文件: {LOG_FILE}")
        print(f"📄 文件大小: {size_str}")
        print()
        
        # 读取日志内容
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        print(f"📊 总行数: {total_lines}")
        print()
        
        # 显示最近的日志
        print("📋 最近的日志 (最多20行):")
        print("-" * 50)
        
        recent_lines = lines[-20:] if len(lines) > 20 else lines
        for i, line in enumerate(recent_lines, 1):
            line = line.strip()
            if line:
                # 简单的颜色标记
                if 'ERROR' in line:
                    print(f"🔴 {line}")
                elif 'WARNING' in line:
                    print(f"🟡 {line}")
                elif 'INFO' in line:
                    print(f"🔵 {line}")
                else:
                    print(f"   {line}")
        
        if len(lines) > 20:
            print(f"\n... (显示最近20行，共{total_lines}行)")
            
        # 统计信息
        print("\n" + "=" * 50)
        print("📈 统计信息:")
        
        error_count = sum(1 for line in lines if 'ERROR' in line)
        warning_count = sum(1 for line in lines if 'WARNING' in line)
        info_count = sum(1 for line in lines if 'INFO' in line)
        
        print(f"🔴 错误: {error_count}")
        print(f"🟡 警告: {warning_count}")
        print(f"🔵 信息: {info_count}")
        
    except Exception as e:
        print(f"❌ 读取日志失败: {e}")

if __name__ == '__main__':
    view_logs() 