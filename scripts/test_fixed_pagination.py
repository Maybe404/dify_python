#!/usr/bin/env python3
"""
测试修复后的分页功能
验证answer字段修复和分页接口工作状态
"""

import sys
import os
import requests
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_task_detail_api(base_url, task_id, token):
    """测试任务详情接口"""
    print(f"🔍 测试任务详情接口: {task_id}")
    
    url = f"{base_url}/api/tasks/{task_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            task_data = result['data']
            task_info = task_data['task']
            results = task_data['results']
            
            print(f"✅ 任务详情获取成功")
            print(f"   任务类型: {task_info['task_type_display']}")
            print(f"   任务状态: {task_info['status_display']}")
            print(f"   结果数量: {len(results)}")
            
            if results:
                latest_result = results[0]
                print(f"   最新结果ID: {latest_result['id']}")
                print(f"   answer字段: {'有数据' if latest_result['answer'] else '空'}")
                
                if latest_result['answer']:
                    print(f"   answer长度: {len(latest_result['answer'])} 字符")
                    
                    # 尝试解析answer内容
                    try:
                        parsed_data = json.loads(latest_result['answer'])
                        if isinstance(parsed_data, list):
                            print(f"   📊 解析成功: {len(parsed_data)} 条记录")
                            return True, len(parsed_data)
                        else:
                            print(f"   ⚠️  数据不是列表格式")
                            return False, 0
                    except json.JSONDecodeError:
                        print(f"   ❌ JSON解析失败")
                        return False, 0
                else:
                    print(f"   ❌ answer字段仍为空")
                    return False, 0
            else:
                print(f"   ❌ 没有结果数据")
                return False, 0
        else:
            print(f"❌ 请求失败: {result['message']}")
            return False, 0
    else:
        print(f"❌ HTTP错误 {response.status_code}: {response.text}")
        return False, 0

def test_pagination_api(base_url, task_id, token, total_items):
    """测试分页接口"""
    print(f"\n📄 测试分页接口: {task_id}")
    
    # 测试第一页
    url = f"{base_url}/api/tasks/{task_id}/results/paginated"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    params = {'page': 1, 'per_page': 5}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            data = result['data']
            pagination = data['pagination']
            items = data['items']
            
            print(f"✅ 分页接口测试成功")
            print(f"   当前页: {pagination['current_page']}")
            print(f"   每页条数: {pagination['per_page']}")
            print(f"   总条数: {pagination['total_items']}")
            print(f"   总页数: {pagination['total_pages']}")
            print(f"   本页条数: {len(items)}")
            print(f"   有下一页: {pagination['has_next']}")
            
            # 验证数据格式
            if items:
                first_item = items[0]
                required_fields = ['sn', 'issueLocation', 'originalText', 'issueDescription', 'recommendedModification']
                missing_fields = [field for field in required_fields if field not in first_item]
                
                if missing_fields:
                    print(f"   ⚠️  缺少字段: {missing_fields}")
                else:
                    print(f"   ✅ 数据格式验证通过")
                
                print(f"   📋 第一条数据示例:")
                print(f"      序号: {first_item.get('sn', 'N/A')}")
                print(f"      位置: {first_item.get('issueLocation', 'N/A')}")
                print(f"      问题: {first_item.get('issueDescription', 'N/A')[:50]}...")
            
            # 测试分页一致性
            if pagination['total_items'] == total_items:
                print(f"   ✅ 分页总数与详情接口一致")
            else:
                print(f"   ⚠️  分页总数({pagination['total_items']})与详情接口({total_items})不一致")
            
            return True
        else:
            print(f"❌ 分页请求失败: {result['message']}")
            return False
    else:
        print(f"❌ 分页HTTP错误 {response.status_code}: {response.text}")
        return False

def login_and_get_token(base_url, email, password):
    """登录获取token"""
    login_data = {
        'credential': email,
        'password': password
    }
    
    response = requests.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            return result['data']['access_token']
    
    return None

def main():
    """主函数"""
    base_url = 'http://localhost:5000'
    
    # 获取登录信息
    email = input("请输入邮箱地址: ").strip()
    password = input("请输入密码: ").strip()
    
    # 登录
    print(f"🔐 正在登录...")
    token = login_and_get_token(base_url, email, password)
    
    if not token:
        print(f"❌ 登录失败")
        return
    
    print(f"✅ 登录成功")
    
    # 测试特定任务（用户提供的任务ID）
    task_id = "a12840fc-2077-4dbd-b889-1f5aef2050d0"
    
    # 1. 测试任务详情接口
    detail_success, total_items = test_task_detail_api(base_url, task_id, token)
    
    if detail_success and total_items > 0:
        # 2. 测试分页接口
        pagination_success = test_pagination_api(base_url, task_id, token, total_items)
        
        if pagination_success:
            print(f"\n🎉 所有测试通过！修复成功！")
        else:
            print(f"\n❌ 分页接口测试失败")
    else:
        print(f"\n❌ 任务详情接口测试失败，无法继续测试分页功能")

if __name__ == '__main__':
    main() 