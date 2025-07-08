#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多状态查询测试脚本 - 验证正确的API调用方式
功能：演示如何正确调用多状态查询接口
"""

import requests
import json
from urllib.parse import urlencode

# API配置
BASE_URL = "http://localhost:5000/api"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MDk5NzExNSwianRpIjoiNTZmOWI2ZmQtNDU3Ny00ZWNkLTllOTktMmMxMDkxNDNkZDVkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY2OGVhNDQxLTgyZWEtNDVjZS04YmMxLWUxYmIyOWM1YTVkMiIsIm5iZiI6MTc1MDk5NzExNSwiZXhwIjoxNzUxMDQwMzE1fQ.MJBdjBAaD3TnO9b_AtS_IypXc1OkjSTOXrY9SCYMAbI"

def test_correct_multi_status_query():
    """测试正确的多状态查询方式"""
    print("="*60)
    print("测试正确的多状态查询API调用")
    print("="*60)
    
    # 设置请求头
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # 查询参数
    query_params = {
        'page': 1,
        'per_page': 20,
        'status': 'processing,completed,failed',  # 多状态查询
        'task_type': 'standard_recommendation'
    }
    
    # 构建完整URL
    url = f"{BASE_URL}/tasks?" + urlencode(query_params)
    
    print(f"✅ 正确的请求方式:")
    print(f"   方法: GET")
    print(f"   URL: {url}")
    print(f"   请求头: Authorization: Bearer {TOKEN[:20]}...")
    print()
    
    try:
        # 发送GET请求
        response = requests.get(url, headers=headers)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                tasks = data['data']['tasks']
                pagination = data['data']['pagination']
                
                print(f"✅ 查询成功!")
                print(f"   找到任务数: {len(tasks)}")
                print(f"   总任务数: {pagination['total']}")
                print()
                
                # 验证状态过滤
                allowed_statuses = {'processing', 'completed', 'failed'}
                actual_statuses = set()
                
                print("📋 任务状态统计:")
                status_counts = {}
                for task in tasks:
                    status = task['status']
                    actual_statuses.add(status)
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                for status, count in status_counts.items():
                    print(f"   {status}: {count} 个")
                
                print()
                
                # 检查是否有意外状态
                unexpected_statuses = actual_statuses - allowed_statuses
                if unexpected_statuses:
                    print(f"❌ 发现意外状态: {unexpected_statuses}")
                    print("   这表明多状态过滤功能有问题")
                    
                    # 显示意外状态的任务详情
                    print("\n意外状态的任务:")
                    for task in tasks:
                        if task['status'] in unexpected_statuses:
                            print(f"   任务ID: {task['id'][:8]}... 状态: {task['status']} 类型: {task['task_type']}")
                else:
                    print("✅ 状态过滤正确，所有任务都在指定状态范围内")
                
            else:
                print(f"❌ API返回错误: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

def test_wrong_way():
    """演示错误的调用方式"""
    print("\n" + "="*60)
    print("演示错误的API调用方式 (仅供对比)")
    print("="*60)
    
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # 错误方式：POST请求 + JSON请求体
    wrong_data = {
        "page": "1", 
        "per_page": "20", 
        "status": "processing,completed,failed",
        "task_type": "standard_recommendation" 
    }
    
    print(f"❌ 错误的请求方式:")
    print(f"   方法: POST")
    print(f"   URL: {BASE_URL}/tasks")
    print(f"   请求体: {json.dumps(wrong_data, ensure_ascii=False, indent=2)}")
    print()
    
    try:
        response = requests.post(f"{BASE_URL}/tasks", headers=headers, json=wrong_data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 405:
            print("✅ 预期结果：405 Method Not Allowed (因为/tasks只支持GET请求)")
        elif response.status_code == 200:
            print("⚠️  意外结果：请求成功了，但这不是正确的调用方式")
            
    except Exception as e:
        print(f"请求异常: {str(e)}")

def test_single_status_query():
    """测试单状态查询"""
    print("\n" + "="*60)
    print("测试单状态查询")
    print("="*60)
    
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # 单状态查询
    query_params = {
        'status': 'uploaded',  # 只查询uploaded状态
        'task_type': 'standard_recommendation'
    }
    
    url = f"{BASE_URL}/tasks?" + urlencode(query_params)
    print(f"查询URL: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                tasks = data['data']['tasks']
                print(f"✅ 单状态查询成功，找到 {len(tasks)} 个uploaded状态的任务")
                
                # 验证所有任务都是uploaded状态
                all_uploaded = all(task['status'] == 'uploaded' for task in tasks)
                if all_uploaded:
                    print("✅ 所有任务状态都正确")
                else:
                    print("❌ 发现非uploaded状态的任务")
            else:
                print(f"❌ 查询失败: {data.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

def main():
    """主函数"""
    print("多状态查询API测试")
    print("当前时间:", "2025-06-27 12:30:00")
    print()
    
    # 测试正确的调用方式
    test_correct_multi_status_query()
    
    # 测试错误的调用方式
    test_wrong_way()
    
    # 测试单状态查询
    test_single_status_query()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
    print("\n💡 总结:")
    print("1. /api/tasks 接口只支持 GET 请求")
    print("2. 查询参数必须在URL中，不能在请求体中")
    print("3. 多状态查询格式: ?status=status1,status2,status3")
    print("4. 正确的URL示例: /api/tasks?status=processing,completed,failed&task_type=standard_recommendation")

if __name__ == '__main__':
    main() 