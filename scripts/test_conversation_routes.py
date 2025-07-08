#!/usr/bin/env python3
"""
简单测试会话操作接口路由
"""

import requests
import json

# 测试配置
BASE_URL = "http://localhost:5000/api"

def test_routes_without_auth():
    """测试路由是否正确（不需要认证，只检查是否返回401而不是404）"""
    
    print("="*60)
    print("测试会话操作接口路由")
    print("="*60)
    
    # 测试场景
    scenarios = ['multilingual_qa', 'standard_query']
    test_conversation_id = "test-conv-123"
    
    for scenario in scenarios:
        print(f"\n🔍 测试场景: {scenario}")
        print("-" * 40)
        
        # 1. 测试重命名接口路由
        rename_url = f"{BASE_URL}/dify/v2/{scenario}/conversations/{test_conversation_id}/name"
        print(f"\n1. 重命名接口路由测试:")
        print(f"   URL: POST {rename_url}")
        
        try:
            response = requests.post(rename_url, json={"name": "test"})
            if response.status_code == 401:
                print("   ✅ 路由正确 - 返回401（需要认证）")
            elif response.status_code == 404:
                print("   ❌ 路由错误 - 返回404（路由不存在）")
            else:
                print(f"   ⚠️  路由可能正确 - 返回{response.status_code}")
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")
        
        # 2. 测试删除接口路由
        delete_url = f"{BASE_URL}/dify/v2/{scenario}/conversations/{test_conversation_id}"
        print(f"\n2. 删除接口路由测试:")
        print(f"   URL: DELETE {delete_url}")
        
        try:
            response = requests.delete(delete_url, json={"user": "test"})
            if response.status_code == 401:
                print("   ✅ 路由正确 - 返回401（需要认证）")
            elif response.status_code == 404:
                print("   ❌ 路由错误 - 返回404（路由不存在）")
            else:
                print(f"   ⚠️  路由可能正确 - 返回{response.status_code}")
        except Exception as e:
            print(f"   ❌ 请求异常: {str(e)}")

def test_config_endpoints():
    """测试配置端点是否包含新接口"""
    print(f"\n" + "="*60)
    print("测试配置端点")
    print("="*60)
    
    # 测试scenarios端点（不需要认证）
    scenarios_url = f"{BASE_URL}/dify/v2/scenarios"
    print(f"\n🔍 测试场景列表接口:")
    print(f"   URL: GET {scenarios_url}")
    
    try:
        response = requests.get(scenarios_url)
        if response.status_code == 401:
            print("   ✅ 场景列表接口存在（需要认证）")
        elif response.status_code == 404:
            print("   ❌ 场景列表接口不存在")
        else:
            print(f"   ⚠️  场景列表接口可能正常 - 状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求异常: {str(e)}")

def main():
    """主函数"""
    print("="*60)
    print("会话操作接口路由测试工具")
    print("="*60)
    print("注意: 此测试不需要登录，仅验证路由是否正确配置")
    
    # 测试路由
    test_routes_without_auth()
    
    # 测试配置端点
    test_config_endpoints()
    
    print(f"\n" + "="*60)
    print("路由测试完成")
    print("="*60)
    print("\n结果说明:")
    print("- ✅ 路由正确: 返回401表示接口存在但需要认证")
    print("- ❌ 路由错误: 返回404表示接口不存在")
    print("- ⚠️  路由可能正确: 返回其他状态码（如500等）")

if __name__ == "__main__":
    main() 