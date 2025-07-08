#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证任务状态管理改进功能
功能：
1. 测试新的uploaded状态
2. 测试多状态查询功能
3. 验证状态转换流程
"""

import os
import sys
import requests
import time
import json
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv()

# API 基础配置
BASE_URL = "http://localhost:5000/api"
TEST_USERNAME = "test@example.com"
TEST_PASSWORD = "password123"

class TaskStatusTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.access_token = None
        
    def login(self):
        """登录获取访问令牌"""
        print("正在登录...")
        login_data = {
            "email": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        
        response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                self.access_token = data['data']['access_token']
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                print("✓ 登录成功")
                return True
        
        print(f"✗ 登录失败: {response.text}")
        return False
    
    def test_status_display(self):
        """测试状态显示映射"""
        print("\n" + "="*50)
        print("测试1: 状态显示映射")
        print("="*50)
        
        # 获取任务类型列表
        response = self.session.get(f"{self.base_url}/tasks/types")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 成功获取任务类型列表")
            print(f"支持的任务类型: {[t['name'] for t in data['data']['task_types']]}")
            return True
        else:
            print(f"✗ 获取任务类型失败: {response.text}")
            return False
    
    def test_file_upload(self):
        """测试文件上传功能，验证uploaded状态"""
        print("\n" + "="*50)
        print("测试2: 文件上传与uploaded状态")
        print("="*50)
        
        # 创建测试文件
        test_content = "这是一个测试文档，用于验证文件上传功能。\n测试时间: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        test_filename = "test_upload.txt"
        
        with open(test_filename, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        try:
            # 上传文件
            files = {'file': (test_filename, open(test_filename, 'rb'), 'text/plain')}
            data = {'task_type': 'standard_interpretation'}
            
            print("正在上传文件...")
            response = self.session.post(f"{self.base_url}/tasks/upload", files=files, data=data)
            
            if response.status_code == 201:
                result = response.json()
                if result.get('success'):
                    task_data = result['data']['task']
                    file_data = result['data']['file']
                    task_id = task_data['id']
                    
                    print(f"✓ 文件上传成功")
                    print(f"  任务ID: {task_id}")
                    print(f"  任务状态: {task_data['status']} ({task_data['status_display']})")
                    print(f"  文件状态: {file_data['upload_status']}")
                    
                    # 验证状态是否为uploaded
                    if task_data['status'] == 'uploaded':
                        print("✓ 任务状态正确更新为uploaded")
                    else:
                        print(f"✗ 任务状态异常: 期望uploaded，实际为{task_data['status']}")
                    
                    return task_id
                else:
                    print(f"✗ 上传失败: {result.get('message')}")
            else:
                print(f"✗ 上传请求失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"✗ 上传过程异常: {str(e)}")
        finally:
            # 清理测试文件
            if os.path.exists(test_filename):
                os.remove(test_filename)
        
        return None
    
    def test_multi_status_query(self, task_id=None):
        """测试多状态查询功能"""
        print("\n" + "="*50)
        print("测试3: 多状态查询功能")
        print("="*50)
        
        # 测试单状态查询
        print("测试单状态查询 (uploaded)...")
        response = self.session.get(f"{self.base_url}/tasks?status=uploaded")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                tasks = data['data']['tasks']
                uploaded_count = len(tasks)
                print(f"✓ 单状态查询成功，找到 {uploaded_count} 个uploaded状态的任务")
                
                # 验证状态过滤
                if all(task['status'] == 'uploaded' for task in tasks):
                    print("✓ 状态过滤正确")
                else:
                    print("✗ 状态过滤有误")
            else:
                print(f"✗ 查询失败: {data.get('message')}")
        else:
            print(f"✗ 查询请求失败: {response.status_code}")
        
        # 测试多状态查询
        print("\n测试多状态查询 (uploaded,pending,failed)...")
        response = self.session.get(f"{self.base_url}/tasks?status=uploaded,pending,failed")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                tasks = data['data']['tasks']
                multi_count = len(tasks)
                print(f"✓ 多状态查询成功，找到 {multi_count} 个任务")
                
                # 验证状态范围
                allowed_statuses = {'uploaded', 'pending', 'failed'}
                actual_statuses = {task['status'] for task in tasks}
                
                if actual_statuses.issubset(allowed_statuses):
                    print(f"✓ 多状态过滤正确，实际状态: {actual_statuses}")
                else:
                    unexpected = actual_statuses - allowed_statuses
                    print(f"✗ 多状态过滤有误，发现意外状态: {unexpected}")
                    
                # 显示状态分布
                status_counts = {}
                for task in tasks:
                    status = task['status']
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                print(f"  状态分布: {status_counts}")
                
            else:
                print(f"✗ 多状态查询失败: {data.get('message')}")
        else:
            print(f"✗ 多状态查询请求失败: {response.status_code}")
        
        # 测试无效状态查询
        print("\n测试无效状态查询...")
        response = self.session.get(f"{self.base_url}/tasks?status=invalid_status")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                tasks = data['data']['tasks']
                print(f"✓ 无效状态查询处理正常，返回 {len(tasks)} 个任务")
            else:
                print(f"无效状态查询返回错误: {data.get('message')}")
    
    def test_status_transition(self, task_id):
        """测试状态转换流程"""
        if not task_id:
            print("\n跳过状态转换测试（没有可用的任务ID）")
            return
            
        print("\n" + "="*50)
        print("测试4: 状态转换流程")
        print("="*50)
        
        # 检查当前状态
        response = self.session.get(f"{self.base_url}/tasks/{task_id}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                task = data['data']['task']
                current_status = task['status']
                print(f"任务当前状态: {current_status} ({task['status_display']})")
                
                if current_status == 'uploaded':
                    print("✓ 任务处于uploaded状态，可以进行标准处理")
                    
                    # 模拟调用标准处理接口（这里只是演示，实际可能需要具体的处理数据）
                    print("准备调用标准处理接口...")
                    print("注意：标准处理会将状态从uploaded更新为processing，然后处理完成后更新为completed")
                    
                else:
                    print(f"任务状态为 {current_status}，不在预期的uploaded状态")
            else:
                print(f"获取任务详情失败: {data.get('message')}")
        else:
            print(f"获取任务详情请求失败: {response.status_code}")
    
    def test_dashboard_stats(self):
        """测试仪表板统计功能"""
        print("\n" + "="*50)
        print("测试5: 仪表板统计")
        print("="*50)
        
        response = self.session.get(f"{self.base_url}/tasks/dashboard")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data['data']
                print("✓ 仪表板统计获取成功")
                print(f"  总任务数: {stats.get('total_tasks', 0)}")
                print("  各状态统计:")
                
                status_stats = stats.get('status_stats', {})
                for status, count in status_stats.items():
                    print(f"    {status}: {count}")
                
                # 检查是否包含uploaded状态的统计
                if 'uploaded' in status_stats:
                    print("✓ 仪表板正确包含uploaded状态统计")
                else:
                    print("◉ 仪表板未包含uploaded状态统计（可能没有uploaded状态的任务）")
                    
            else:
                print(f"✗ 获取仪表板统计失败: {data.get('message')}")
        else:
            print(f"✗ 仪表板统计请求失败: {response.status_code}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始执行任务状态管理改进功能测试")
        print("="*60)
        
        # 登录
        if not self.login():
            print("登录失败，测试终止")
            return False
        
        # 执行各项测试
        self.test_status_display()
        task_id = self.test_file_upload()
        self.test_multi_status_query(task_id)
        self.test_status_transition(task_id)
        self.test_dashboard_stats()
        
        print("\n" + "="*60)
        print("所有测试执行完成")
        print("="*60)
        
        return True

def main():
    """主函数"""
    tester = TaskStatusTester()
    tester.run_all_tests()

if __name__ == '__main__':
    main() 