#!/usr/bin/env python3
"""
测试分页查询接口功能
用于验证任务结果分页查询的正确性
"""

import requests
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PaginationAPITester:
    """分页API测试类"""
    
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.token = None
        self.headers = {}
    
    def login(self, email, password):
        """登录获取Token"""
        login_data = {
            'credential': email,
            'password': password
        }
        
        response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                self.token = result['data']['access_token']
                self.headers = {
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                }
                print(f"✅ 登录成功: {result['data']['user']['email']}")
                return True
        
        print(f"❌ 登录失败: {response.text}")
        return False
    
    def test_pagination_supported_task(self, task_id):
        """测试支持分页的任务类型"""
        print(f"\n🔍 测试任务 {task_id} 的分页功能...")
        
        # 测试不同的分页参数
        test_cases = [
            {'page': 1, 'per_page': 5},
            {'page': 1, 'per_page': 10},
            {'page': 2, 'per_page': 5},
            {'page': 1, 'per_page': 20, 'sort_order': 'desc'},
        ]
        
        for case in test_cases:
            print(f"\n📄 测试参数: {case}")
            
            # 构建请求URL
            params = '&'.join([f"{k}={v}" for k, v in case.items()])
            url = f"{self.base_url}/api/tasks/{task_id}/results/paginated?{params}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    data = result['data']
                    pagination = data['pagination']
                    items = data['items']
                    task_info = data['task_info']
                    
                    print(f"✅ 请求成功")
                    print(f"   任务类型: {task_info['task_type_display']}")
                    print(f"   任务状态: {task_info['status_display']}")
                    print(f"   总条数: {pagination['total_items']}")
                    print(f"   总页数: {pagination['total_pages']}")
                    print(f"   当前页: {pagination['current_page']}")
                    print(f"   每页条数: {pagination['per_page']}")
                    print(f"   本页条数: {len(items)}")
                    print(f"   有下一页: {pagination['has_next']}")
                    print(f"   有上一页: {pagination['has_prev']}")
                    
                    # 显示前几条数据示例
                    if items:
                        print(f"   数据示例:")
                        for i, item in enumerate(items[:3]):  # 只显示前3条
                            print(f"     [{item.get('sn', 'N/A')}] {item.get('issueLocation', 'N/A')[:20]}...")
                else:
                    print(f"❌ 请求失败: {result['message']}")
            else:
                print(f"❌ HTTP错误 {response.status_code}: {response.text}")
    
    def test_unsupported_task(self, task_id):
        """测试不支持分页的任务类型"""
        print(f"\n🚫 测试不支持分页的任务 {task_id}...")
        
        url = f"{self.base_url}/api/tasks/{task_id}/results/paginated"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 400:
            result = response.json()
            print(f"✅ 正确拒绝: {result['message']}")
        else:
            print(f"❌ 预期400错误，实际: {response.status_code}")
    
    def get_user_tasks(self):
        """获取用户的任务列表"""
        url = f"{self.base_url}/api/tasks"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                return result['data']['tasks']
        
        return []
    
    def run_tests(self, email=None, password=None):
        """运行所有测试"""
        print("🚀 开始分页API测试...")
        
        # 如果没有提供登录信息，使用默认测试账号
        if not email or not password:
            email = input("请输入邮箱地址: ").strip()
            password = input("请输入密码: ").strip()
        
        # 登录
        if not self.login(email, password):
            return False
        
        # 获取用户任务列表
        tasks = self.get_user_tasks()
        if not tasks:
            print("❌ 没有找到任务，请先创建一些任务")
            return False
        
        print(f"\n📋 找到 {len(tasks)} 个任务")
        
        # 按任务类型分类
        pagination_supported = []
        other_tasks = []
        
        for task in tasks:
            task_type = task['task_type']
            if task_type in ['standard_review', 'standard_recommendation', 'standard_compliance']:
                pagination_supported.append(task)
            else:
                other_tasks.append(task)
        
        print(f"   支持分页: {len(pagination_supported)} 个")
        print(f"   其他类型: {len(other_tasks)} 个")
        
        # 测试支持分页的任务
        if pagination_supported:
            print(f"\n📊 测试支持分页的任务...")
            for task in pagination_supported[:3]:  # 最多测试3个
                if task['status'] == 'completed':
                    self.test_pagination_supported_task(task['id'])
                else:
                    print(f"⏳ 跳过未完成任务: {task['title']} ({task['status_display']})")
        
        # 测试不支持分页的任务
        if other_tasks:
            print(f"\n🚫 测试不支持分页的任务...")
            for task in other_tasks[:2]:  # 最多测试2个
                self.test_unsupported_task(task['id'])
        
        print(f"\n🎉 测试完成!")
        return True

def main():
    """主函数"""
    # 可以通过命令行参数指定测试参数
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
        base_url = sys.argv[3] if len(sys.argv) > 3 else 'http://localhost:5000'
    else:
        email = None
        password = None
        base_url = 'http://localhost:5000'
    
    tester = PaginationAPITester(base_url)
    tester.run_tests(email, password)

if __name__ == '__main__':
    main() 