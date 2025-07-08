#!/usr/bin/env python3
"""
日志分析工具
用于分析应用日志，提供统计信息和问题排查功能
"""

import os
import re
import sys
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import argparse

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'app.log')

class LogAnalyzer:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.log_entries = []
        self.stats = {
            'total_entries': 0,
            'by_level': defaultdict(int),
            'by_hour': defaultdict(int),
            'by_date': defaultdict(int),
            'errors': [],
            'warnings': [],
            'security_events': [],
            'api_requests': [],
            'slow_operations': [],
            'top_ips': Counter(),
            'top_users': Counter(),
            'response_times': []
        }
    
    def parse_log_line(self, line):
        """解析单行日志"""
        # 日志格式: 2025-06-13 15:52:38,723 [INFO] app: 消息内容 [in 文件路径:行号]
        pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \[(\w+)\] (\w+): (.+?) \[in (.+?):(\d+)\]'
        match = re.match(pattern, line.strip())
        
        if match:
            timestamp_str, level, logger, message, file_path, line_no = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
            
            return {
                'timestamp': timestamp,
                'level': level,
                'logger': logger,
                'message': message,
                'file_path': file_path,
                'line_no': int(line_no),
                'raw_line': line.strip()
            }
        return None
    
    def load_logs(self):
        """加载日志文件"""
        if not os.path.exists(self.log_file_path):
            print(f"❌ 日志文件不存在: {self.log_file_path}")
            return False
        
        print(f"📂 正在加载日志文件: {self.log_file_path}")
        
        try:
            # 尝试不同的编码方式
            encodings = ['utf-8', 'gbk', 'utf-8-sig', 'latin1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(self.log_file_path, 'r', encoding=encoding) as f:
                        content = f.readlines()
                    print(f"✅ 使用编码 {encoding} 成功读取文件")
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                print("❌ 无法使用任何编码读取文件")
                return False
                
            for line_no, line in enumerate(content, 1):
                entry = self.parse_log_line(line)
                if entry:
                    self.log_entries.append(entry)
                    self.analyze_entry(entry)
                    
            self.stats['total_entries'] = len(self.log_entries)
            print(f"✅ 成功加载 {self.stats['total_entries']} 条日志记录")
            return True
            
        except Exception as e:
            print(f"❌ 加载日志文件失败: {e}")
            return False
    
    def analyze_entry(self, entry):
        """分析单条日志记录"""
        # 按级别统计
        self.stats['by_level'][entry['level']] += 1
        
        # 按时间统计
        hour_key = entry['timestamp'].strftime('%Y-%m-%d %H:00')
        date_key = entry['timestamp'].strftime('%Y-%m-%d')
        self.stats['by_hour'][hour_key] += 1
        self.stats['by_date'][date_key] += 1
        
        message = entry['message']
        
        # 收集错误和警告
        if entry['level'] == 'ERROR':
            self.stats['errors'].append(entry)
        elif entry['level'] == 'WARNING':
            self.stats['warnings'].append(entry)
        
        # 分析安全事件
        if '安全事件:' in message:
            self.stats['security_events'].append(entry)
        
        # 分析API请求
        if 'API请求' in message:
            self.stats['api_requests'].append(entry)
            
            # 提取响应时间
            time_match = re.search(r'耗时: ([\d.]+)ms', message)
            if time_match:
                response_time = float(time_match.group(1))
                self.stats['response_times'].append(response_time)
                
                # 记录慢请求（>1000ms）
                if response_time > 1000:
                    self.stats['slow_operations'].append(entry)
        
        # 提取IP地址
        ip_match = re.search(r'IP: ([\d.]+)', message)
        if ip_match:
            self.stats['top_ips'][ip_match.group(1)] += 1
        
        # 提取用户信息
        user_match = re.search(r'用户名: (\w+)', message)
        if user_match:
            self.stats['top_users'][user_match.group(1)] += 1
    
    def print_summary(self):
        """打印分析摘要"""
        print("\n" + "="*60)
        print("📊 日志分析报告")
        print("="*60)
        
        # 基本统计
        print(f"\n📈 基本统计:")
        print(f"   总日志条数: {self.stats['total_entries']}")
        
        if self.log_entries:
            start_time = min(entry['timestamp'] for entry in self.log_entries)
            end_time = max(entry['timestamp'] for entry in self.log_entries)
            print(f"   时间范围: {start_time.strftime('%Y-%m-%d %H:%M:%S')} ~ {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 按级别统计
        print(f"\n📋 按日志级别统计:")
        for level in ['INFO', 'WARNING', 'ERROR', 'DEBUG']:
            count = self.stats['by_level'][level]
            if count > 0:
                percentage = (count / self.stats['total_entries'] * 100) if self.stats['total_entries'] > 0 else 0
                print(f"   {level}: {count} ({percentage:.1f}%)")
        
        # 错误统计
        error_count = len(self.stats['errors'])
        warning_count = len(self.stats['warnings'])
        
        if error_count > 0:
            print(f"\n🔴 错误统计:")
            print(f"   错误总数: {error_count}")
            print(f"\n   最近的错误:")
            for error in self.stats['errors'][-5:]:
                print(f"   - {error['timestamp'].strftime('%H:%M:%S')}: {error['message'][:80]}...")
        
        if warning_count > 0:
            print(f"\n🟡 警告统计:")
            print(f"   警告总数: {warning_count}")
            print(f"\n   最近的警告:")
            for warning in self.stats['warnings'][-5:]:
                print(f"   - {warning['timestamp'].strftime('%H:%M:%S')}: {warning['message'][:80]}...")
        
        # 安全事件
        security_count = len(self.stats['security_events'])
        if security_count > 0:
            print(f"\n🔒 安全事件统计:")
            print(f"   安全事件总数: {security_count}")
            
            # 分析安全事件类型
            security_types = Counter()
            for event in self.stats['security_events']:
                if '登录成功' in event['message']:
                    security_types['登录成功'] += 1
                elif '登录失败' in event['message']:
                    security_types['登录失败'] += 1
                elif '注册成功' in event['message']:
                    security_types['注册成功'] += 1
                elif '注册失败' in event['message']:
                    security_types['注册失败'] += 1
                elif '登出' in event['message']:
                    security_types['用户登出'] += 1
            
            for event_type, count in security_types.most_common():
                print(f"   - {event_type}: {count}")
        
        # API请求统计
        api_count = len(self.stats['api_requests'])
        if api_count > 0:
            print(f"\n🌐 API请求统计:")
            print(f"   API请求总数: {api_count}")
            
            if self.stats['response_times']:
                avg_time = sum(self.stats['response_times']) / len(self.stats['response_times'])
                max_time = max(self.stats['response_times'])
                min_time = min(self.stats['response_times'])
                print(f"   平均响应时间: {avg_time:.2f}ms")
                print(f"   最大响应时间: {max_time:.2f}ms")
                print(f"   最小响应时间: {min_time:.2f}ms")
            
            slow_count = len(self.stats['slow_operations'])
            if slow_count > 0:
                print(f"   慢请求(>1s): {slow_count}")
        
        # 最活跃的IP
        if self.stats['top_ips']:
            print(f"\n🌍 最活跃的IP地址:")
            for ip, count in self.stats['top_ips'].most_common(5):
                print(f"   - {ip}: {count} 次请求")
        
        # 最活跃的用户
        if self.stats['top_users']:
            print(f"\n👥 最活跃的用户:")
            for user, count in self.stats['top_users'].most_common(5):
                print(f"   - {user}: {count} 次操作")
    
    def search_logs(self, keyword, level=None, start_time=None, end_time=None):
        """搜索日志"""
        results = []
        
        for entry in self.log_entries:
            # 级别过滤
            if level and entry['level'] != level.upper():
                continue
            
            # 时间过滤
            if start_time and entry['timestamp'] < start_time:
                continue
            if end_time and entry['timestamp'] > end_time:
                continue
            
            # 关键词搜索
            if keyword.lower() in entry['message'].lower():
                results.append(entry)
        
        return results
    
    def print_search_results(self, results, limit=20):
        """打印搜索结果"""
        if not results:
            print("❌ 没有找到匹配的日志记录")
            return
        
        print(f"\n🔍 找到 {len(results)} 条匹配记录 (显示最新 {min(limit, len(results))} 条):")
        print("-" * 80)
        
        for entry in results[-limit:]:
            timestamp = entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            level_color = {
                'ERROR': '🔴',
                'WARNING': '🟡', 
                'INFO': '🔵',
                'DEBUG': '⚪'
            }.get(entry['level'], '⚪')
            
            print(f"{level_color} [{timestamp}] {entry['level']}: {entry['message']}")


def main():
    parser = argparse.ArgumentParser(description='日志分析工具')
    parser.add_argument('--file', '-f', default=LOG_FILE, help='日志文件路径')
    parser.add_argument('--search', '-s', help='搜索关键词')
    parser.add_argument('--level', '-l', choices=['INFO', 'WARNING', 'ERROR', 'DEBUG'], help='过滤日志级别')
    parser.add_argument('--hours', type=int, help='查看最近N小时的日志')
    parser.add_argument('--limit', type=int, default=20, help='搜索结果显示数量限制')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = LogAnalyzer(args.file)
    
    # 加载日志
    if not analyzer.load_logs():
        return 1
    
    # 如果有搜索条件
    if args.search or args.level or args.hours:
        # 计算时间范围
        start_time = None
        if args.hours:
            start_time = datetime.now() - timedelta(hours=args.hours)
        
        # 搜索日志
        results = analyzer.search_logs(
            keyword=args.search or '',
            level=args.level,
            start_time=start_time
        )
        
        analyzer.print_search_results(results, args.limit)
    else:
        # 显示摘要
        analyzer.print_summary()
    
    return 0


if __name__ == '__main__':
    exit(main()) 