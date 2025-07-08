#!/usr/bin/env python3
"""
日志查看和分析脚本
方便查看和分析应用日志
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import re

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
LOG_FILE = PROJECT_ROOT / 'logs' / 'app.log'

def print_header(title):
    """打印标题"""
    print("=" * 60)
    print(f"📋 {title}")
    print("=" * 60)

def check_log_file():
    """检查日志文件是否存在"""
    if not LOG_FILE.exists():
        print(f"❌ 日志文件不存在: {LOG_FILE}")
        print("💡 提示:")
        print("   1. 确保应用已经启动过")
        print("   2. 检查日志配置是否正确")
        print("   3. 确认日志目录权限")
        return False
    return True

def view_recent_logs(lines=50):
    """查看最近的日志"""
    print_header(f"最近 {lines} 行日志")
    
    if not check_log_file():
        return
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            for line in recent_lines:
                line = line.strip()
                if line:
                    # 根据日志级别着色
                    if 'ERROR' in line:
                        print(f"🔴 {line}")
                    elif 'WARNING' in line:
                        print(f"🟡 {line}")
                    elif 'INFO' in line:
                        print(f"🔵 {line}")
                    elif 'DEBUG' in line:
                        print(f"⚪ {line}")
                    else:
                        print(f"   {line}")
                        
    except Exception as e:
        print(f"❌ 读取日志文件失败: {e}")

def search_logs(keyword, case_sensitive=False):
    """搜索日志内容"""
    print_header(f"搜索关键词: '{keyword}'")
    
    if not check_log_file():
        return
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        matches = []
        for i, line in enumerate(lines, 1):
            if case_sensitive:
                if keyword in line:
                    matches.append((i, line.strip()))
            else:
                if keyword.lower() in line.lower():
                    matches.append((i, line.strip()))
        
        if matches:
            print(f"📊 找到 {len(matches)} 条匹配记录:")
            print()
            for line_num, line in matches:
                print(f"行 {line_num}: {line}")
        else:
            print(f"❌ 未找到包含 '{keyword}' 的日志记录")
            
    except Exception as e:
        print(f"❌ 搜索日志失败: {e}")

def analyze_logs():
    """分析日志统计信息"""
    print_header("日志分析报告")
    
    if not check_log_file():
        return
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 统计信息
        total_lines = len(lines)
        error_count = 0
        warning_count = 0
        info_count = 0
        debug_count = 0
        
        # 用户操作统计
        login_count = 0
        register_count = 0
        
        # 时间范围
        first_log_time = None
        last_log_time = None
        
        # 分析每一行
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 统计日志级别
            if 'ERROR' in line:
                error_count += 1
            elif 'WARNING' in line:
                warning_count += 1
            elif 'INFO' in line:
                info_count += 1
            elif 'DEBUG' in line:
                debug_count += 1
            
            # 统计用户操作
            if '登录' in line or 'login' in line.lower():
                login_count += 1
            if '注册' in line or 'register' in line.lower():
                register_count += 1
            
            # 提取时间戳
            time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            if time_match:
                try:
                    log_time = datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')
                    if first_log_time is None:
                        first_log_time = log_time
                    last_log_time = log_time
                except ValueError:
                    pass
        
        # 输出统计结果
        print(f"📊 总日志行数: {total_lines}")
        print()
        
        print("📈 日志级别分布:")
        print(f"   🔴 错误 (ERROR):   {error_count}")
        print(f"   🟡 警告 (WARNING): {warning_count}")
        print(f"   🔵 信息 (INFO):    {info_count}")
        print(f"   ⚪ 调试 (DEBUG):   {debug_count}")
        print()
        
        print("👥 用户操作统计:")
        print(f"   🔐 登录操作: {login_count}")
        print(f"   📝 注册操作: {register_count}")
        print()
        
        if first_log_time and last_log_time:
            duration = last_log_time - first_log_time
            print("⏰ 时间范围:")
            print(f"   📅 最早日志: {first_log_time}")
            print(f"   📅 最新日志: {last_log_time}")
            print(f"   ⏱️  时间跨度: {duration}")
        
        # 文件大小
        file_size = LOG_FILE.stat().st_size
        if file_size > 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.2f} MB"
        elif file_size > 1024:
            size_str = f"{file_size / 1024:.2f} KB"
        else:
            size_str = f"{file_size} bytes"
        
        print()
        print(f"📁 文件信息:")
        print(f"   📄 文件大小: {size_str}")
        print(f"   📂 文件路径: {LOG_FILE}")
        
    except Exception as e:
        print(f"❌ 分析日志失败: {e}")

def view_errors_only():
    """只查看错误日志"""
    print_header("错误日志")
    
    if not check_log_file():
        return
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        error_lines = []
        for i, line in enumerate(lines, 1):
            if 'ERROR' in line:
                error_lines.append((i, line.strip()))
        
        if error_lines:
            print(f"🔴 找到 {len(error_lines)} 条错误记录:")
            print()
            for line_num, line in error_lines:
                print(f"行 {line_num}: {line}")
        else:
            print("✅ 未发现错误日志")
            
    except Exception as e:
        print(f"❌ 查看错误日志失败: {e}")

def view_today_logs():
    """查看今天的日志"""
    today = datetime.now().strftime('%Y-%m-%d')
    print_header(f"今天的日志 ({today})")
    
    if not check_log_file():
        return
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        today_lines = []
        for i, line in enumerate(lines, 1):
            if today in line:
                today_lines.append((i, line.strip()))
        
        if today_lines:
            print(f"📅 今天共有 {len(today_lines)} 条日志:")
            print()
            for line_num, line in today_lines[-20:]:  # 显示最近20条
                if 'ERROR' in line:
                    print(f"🔴 行 {line_num}: {line}")
                elif 'WARNING' in line:
                    print(f"🟡 行 {line_num}: {line}")
                elif 'INFO' in line:
                    print(f"🔵 行 {line_num}: {line}")
                else:
                    print(f"   行 {line_num}: {line}")
            
            if len(today_lines) > 20:
                print(f"\n... (显示最近20条，共{len(today_lines)}条)")
        else:
            print("❌ 今天暂无日志记录")
            
    except Exception as e:
        print(f"❌ 查看今天日志失败: {e}")

def main():
    parser = argparse.ArgumentParser(description='日志查看和分析工具')
    parser.add_argument('--recent', '-r', type=int, default=50,
                       help='查看最近N行日志 (默认50行)')
    parser.add_argument('--search', '-s', type=str,
                       help='搜索关键词')
    parser.add_argument('--case-sensitive', '-c', action='store_true',
                       help='区分大小写搜索')
    parser.add_argument('--analyze', '-a', action='store_true',
                       help='分析日志统计信息')
    parser.add_argument('--errors', '-e', action='store_true',
                       help='只显示错误日志')
    parser.add_argument('--today', '-t', action='store_true',
                       help='显示今天的日志')
    
    args = parser.parse_args()
    
    print("📋 日志查看工具")
    print(f"📁 日志文件: {LOG_FILE}")
    print()
    
    if args.analyze:
        analyze_logs()
    elif args.search:
        search_logs(args.search, args.case_sensitive)
    elif args.errors:
        view_errors_only()
    elif args.today:
        view_today_logs()
    else:
        view_recent_logs(args.recent)
    
    print()
    print("💡 使用提示:")
    print("   python scripts/view_logs.py --recent 100    # 查看最近100行")
    print("   python scripts/view_logs.py --search 登录   # 搜索关键词")
    print("   python scripts/view_logs.py --analyze       # 分析统计")
    print("   python scripts/view_logs.py --errors        # 只看错误")
    print("   python scripts/view_logs.py --today         # 今天的日志")

if __name__ == '__main__':
    main() 